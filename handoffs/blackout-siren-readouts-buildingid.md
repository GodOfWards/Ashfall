# Ashfall Handoff — Three small fixes: the siren in a blackout, idle readouts, `buildingId`

Current shipped version: v0.10.8
Implied version-change type: PATCH (no new persistent state; see "Data / schema changes")
Issues: #356 — A blacked-out player hears the siren as if awake;
#337 — A cycling load's readout says "Running" while it's idle;
#89 — `building` means a name on rooms and an id on doors and keys

## What this is

Three independent `tier-0` fixes, shipped as one PATCH:

1. **#356.** A long exhaustion blackout counts as asleep for waking events.
   The siren wakes a blacked-out player, as it wakes a sleeping one, and the
   blackout ends early.
2. **#337.** A load that can stand powered but idle (the water heater, the
   house pump) says so. "Running" is shown only while it is drawing.
3. **#89.** Every field named `building` that holds a building **id** is
   renamed `buildingId`. After the rename, `building` means the display name
   and nothing else.

Each is its own section below. They share no code.

---

## 1. The siren during a blackout (#356)

### Relevant existing state

- `advanceTime(min)` (SURVIVAL/TIME SIMULATION) runs `runAwakeStep(min)`.
  Then, if Energy is at or below 0, it increments `state.collapseCount`. Every
  `COLLAPSE_BLACKOUT_EVERY`-th (3rd) collapse is a **blackout**; the others are
  a **stumble**:
  - Blackout: `log("Your body gives out completely. You black out — hours pass before you come to, disoriented and vulnerable.", "warn")`,
    then `runAwakeStep(COLLAPSE_BLACKOUT_MIN)` (300), then
    `state.vitals.energy = clamp(COLLAPSE_BLACKOUT_ENERGY)` (90; "set to, not
    added").
  - Stumble: a log line, `runAwakeStep(COLLAPSE_STUMBLE_MIN)` (20), then Energy
    `+ COLLAPSE_STUMBLE_ENERGY`.
- `runAwakeStep(min)` loops in ≤1-minute steps: `totalMinutes`,
  `applyHungerThirst`, `applyWorldTicking`, `recoveryStep(dt, "normal")`. It
  has no early exit.
- Sleep's runtime flags, never saved: `let asleep = false, wokenUp = false;`.
  `doSleep()` sets `asleep = true` for its loop (in a `try/finally`). The loop
  condition is `while(remaining > 1e-9 && !wokenUp)`. After the loop, it
  treats `interrupted = wokenUp && remaining > 1e-9`, so **a waking event in
  the last step leaves the sleep complete**, and it resets `wokenUp`.
- `fireClockEvents(dt)` (called through `applyWorldTicking`) logs
  `ev.line(state.currentRoom, asleep)` and, for an event marked `wakes`, sets
  `wokenUp = true` if `asleep`. The one event today is Atucha's siren
  (`CLOCK_EVENTS`, `wakes: true`). Its lines are in `SIREN_LINES`. The asleep
  variants all begin "A siren wakes you." (e.g. town: "A siren wakes you.
  It's far to the north, and after a while it stops. Nothing follows it.").
- Today a blackout runs through the awake path, so the player gets the awake
  line ("Far to the north, a siren starts up…"), and the blackout isn't cut
  short.

### Rules

**Blackout (the long collapse) only.** The stumble is unchanged: it stays on
the awake path, hears the awake line, and isn't cut short. You're down, but
not unconscious.

1. **The blackout counts as asleep for clock events.** For the whole
   blackout, `fireClockEvents()` must see the player as asleep, so it picks
   the `asleep` line and a `wakes` event sets `wokenUp`. Clear the flag
   afterwards on every path (as `doSleep()` does with `finally`).
2. **A waking event ends the blackout after that step,** as it ends sleep.
   Measure the minutes actually taken, `taken`, out of
   `COLLAPSE_BLACKOUT_MIN`.
3. **Energy.**
   - Completed blackout: unchanged, `clamp(COLLAPSE_BLACKOUT_ENERGY)`.
   - Woken early: Energy is **set to**
     `clamp(COLLAPSE_BLACKOUT_ENERGY * taken / COLLAPSE_BLACKOUT_MIN)`. Woken 120
     minutes in gives 36. This is derived from the existing two constants, so
     there's no new constant. It's still a balance choice, so retunable (Tom,
     2026-09-30).
   - **A waking event in the last step leaves the blackout complete**, as it
     does for sleep: full Energy, and the completion line below.
4. **Nothing else changes.** `collapseCount` still increments once per
   collapse. Nothing else special happens after an interrupted blackout: no
   Fatigue change, no cooldown, no `lastExertionMinute` write, since the
   blackout sets none of these today. `wokenUp` is reset afterwards, so a
   later sleep doesn't start already woken.
5. **Log lines (Tom, 2026-09-30).** The existing single line is split in two:
   - At the start of the blackout, before its steps run:
     `"Your body gives out completely. You black out."`, class `"warn"`.
   - After a **completed** blackout only:
     `"Hours pass before you come to, disoriented and vulnerable."`, class
     `"warn"`.
   - When **woken early**, no second line: the siren's own asleep line ("A
     siren wakes you…"), logged during the step, is the record. This is how
     sleep handles it.

   So a woken blackout reads: "…You black out." then "A siren wakes you. …".
   A full one reads: "…You black out." then "Hours pass before you come to…".

### Design decisions to make during implementation

- **How the blackout gets an early exit.** For example, an optional stop
  condition on `runAwakeStep()`, or a blackout-specific loop in `advanceTime()`
  that performs the same four per-step calls. Either way, the per-step
  behaviour must stay identical to `runAwakeStep`'s (including
  `recoveryStep(dt, "normal")`). Record which you chose.
- **Whether the `asleep` flag is renamed** now that it covers a blackout too
  (e.g. to something meaning "not awake"). Recommended default: keep `asleep`
  and update its comment ("Sleep's runtime flags…") to say a blackout sets it
  too. Either way, `CLOCK_EVENTS`' comment, which says `line` is told
  "whether the player is asleep", must stay true. Record the choice.

---

## 2. Idle readouts for the water heater and the pump (#337)

### Relevant existing state

- `loadStatusText(loadId)` (RENDERING) returns `a.readout.on` whenever
  `loadPoweredNow(loadId)`, else `a.readout.off + " · " + "switched on" |
  "switched off"`. Its three callers (the device pop-up, the panel
  tab line, the room's load list) all go through it.
- `loadPoweredNow()` takes a fresh `powerSnapshot()` of the load's own
  building on `state.power`, with **`prevDrawing` null**, so that a hand on the
  load's own switch shows in its readout at once. It stores nothing, so it is
  render-safe.
- `powerSnapshot()` also computes `drawing`:
  - A **cycling** load (`dutyCycle`, `cycleMinutes`) draws only in the on part
    of its cycle.
  - A **pump** (`flowLph`) draws only while its float calls: its tank is below
    the start level, **or** it was drawing in `prevDrawing` and the tank isn't
    full yet. With `prevDrawing` null, only the first test applies.
- Meters read the **last step's** result (`powerNow`, via `powerRead()`). So a
  clamp on an idle heater reads 0 A while the readout says "Running".
- APPLIANCES today: `water_heater` has `dutyCycle` ≈ 0.05 and `cycleMinutes`
  120, and readout `{ on:"Running", off:"Stopped" }`. `house_pump` has
  `flowLph` and readout `{ on:"Running", off:"Stopped" }`. `fridge_freezer`
  cycles too (`dutyCycle` 0.35), but its readout `{ on:"Light on", off:"Dark" }`
  describes its **door light**, which is on whenever it has power.
- POWER SCHEMA, `readout`: "`on` while it is powered and running, `off`
  otherwise". That already claims what the code doesn't do.
- `validateWiring()` requires every non-switchless appliance to have a
  `readout` with non-empty `on` and `off`.

### Rules

1. **`readout` gains an optional third word, `idle`**: shown while the load is
   powered but not drawing. An appliance without `idle` behaves exactly as now:
   `on` whenever it is powered.
2. **Words (Tom, 2026-09-30):**
   - `water_heater`: `{ on:"Running", idle:"Standing by", off:"Stopped" }`.
   - `house_pump`: `{ on:"Running", idle:"Standing by", off:"Stopped" }`.
   - Every other appliance is unchanged, **including `fridge_freezer`**. Its
     readout is its door light, not its compressor, and it gets no `idle`.
   - Functional UI text, retunable.
3. **`loadStatusText()`:**
   - Not powered now: unchanged (`off · switched on|off`).
   - Powered now, has `idle`, and not drawing now: `idle`.
   - Otherwise: `on`.
4. **What "drawing now" means for the readout.** It must agree with what the
   resolver does:
   - The heater shows "Running" during the on part of its cycle and "Standing
     by" for the rest.
   - The pump shows "Running" while its float calls, **including the latch**:
     a pump that started below the start level keeps running until the tank
     is full.
   - It keeps the existing property that flipping the load's own switch shows
     in its readout at once.
   - It stays render-safe: nothing stored, nothing started.
   - Read the same way, a freshly switched-on heater in its off phase shows
     "Standing by" at once.
5. **POWER SCHEMA's `readout` entry** is rewritten to state the three words and
   when each shows. Its note that the words are "Functional UI text,
   retunable" stays.
6. **`validateWiring()`:** an `idle` that is present must be a non-empty
   string. Also report an `idle` on an appliance that can't be powered and
   idle (neither `dutyCycle` nor `flowLph`), since the word would never show.

### Design decisions to make during implementation

- **How the readout gets "drawing now" with the pump's latch.** Recommended:
  the same fresh look `loadPoweredNow()` takes, with the load's building's
  last-step drawing (from `powerNow`, e.g. through `priorDrawing()` or
  `powerRead(powerNow, "drawing", …)`) passed as `prevDrawing` rather than
  null. Keep it one look for both `powered` and `drawing`, not two snapshots
  per readout. Reading `powerRead(powerNow, "drawing", id)` alone isn't
  enough: it would show a just-flipped switch only from the next step. Record
  what you did.
- The helper's name, and whether `loadPoweredNow()` is generalised or a sibling
  is added.

---

## 3. Rename id-holding `building` fields to `buildingId` (#89)

### Relevant existing state (v0.10.8)

On a **room**, `building` is the display name ("Pharmacy"). The ROOM SCHEMA
comment says it "holds a building's name and nothing else, ever". It is read by
the locator bar (`[room.address, room.building, room.area]`) and
`doorNamesFor()`'s disambiguator (`b.building`). Rooms already carry
`buildingId`, the instance id.

Everywhere else, `building` holds a building **id**:

- **Doors.** The building builder sets
  `const def = { locked:!!d.locked, sides, building:inst.id };`. The
  wired-layout builder (in the wiring expander) sets
  `const def = { locked:!!d.locked, sides, building:b };`. Documented in the
  door definition comment ("`building` a building instance's id … Not
  room.building, which holds a name").
- **A masterKey item's `building`.** Documented in the ITEM DATA SCHEMA
  (`masterKey` "key unlocks every door in `building`"; `building` "building
  association for a masterKey"). Read by:
  - `findKeyForDoor()`: `if(it.masterKey && it.building === door.building) return it;`
  - the key's unlock-all loop:
    `doors[doorId].building===it.building`.

  No item in `ITEM_REGISTRY` carries `masterKey` today.
- **Power boards and panels.** `expandWiring()` sets
  `{ id:boardId, building:b, … }` and `{ id:panelId, building:b, board:boardId, … }`.
  They are documented in the comment above it (`boards { id: { id, building,
  name, … } }`, `panels { id: { id, building, board, … } }`). Read by:
  - the per-building index: `subOf(bd.building)`, `idx.of[bd.id] = bd.building`,
    and the same for `pn`;
  - the device-name disambiguator: `BUILDING_INFO[node.building]`.
- The ROOM SCHEMA's `building` entry carries a note warning that
  `doors[].building` and a master key's `building` are a different field
  holding an id.
- The stove timer already compares `buildingId`. The comment above
  `doAddStoveTimer()` still says "the player's room must have a `building`,
  and the same one", which is stale.

**Saves:** none of these is saved. Door, board and panel definitions are built
at load. A save carries only door state `{ locked, open, broken }` per door id.
The saved power state is only `switches`, `breakers` and `heat` maps
(`backfillPowerState()`). No item carries `masterKey`. So this is PATCH.

### Rules

1. Rename to `buildingId`: the door definition field (both builders), the
   masterKey item field, and the board and panel field. Update every reader
   listed above.
2. `room.building` (the name) is **not** renamed.
3. Update the comments:
   - the door definition field's entry;
   - the ITEM DATA SCHEMA's `masterKey`/`building` pair (it becomes
     `masterKey`/`buildingId`);
   - the `boards`/`panels` shape comment above `expandWiring()`.

   The ROOM SCHEMA's collision note is removed or reduced to "the name; the
   id is `buildingId`": once the rename lands, there's no collision left to
   warn about.
4. Fix the stale stove-timer comment so it says what the code does: heard when
   the player's room has the same `buildingId` as the stove's.
5. **Proof:** after the change, the only remaining `.building` reads and
   `building:` writes in `ashfall.html` are room-name ones
   (`room.building`, `building:name` in the building builder, and
   `doorNamesFor()`'s `b.building`). State the grep you used in the
   changelog's validation section.

---

## Data / schema changes

- **No new or changed PLAYER STATE fields.** The `asleep`/`wokenUp` flags are
  runtime only, never saved.
- APPLIANCES schema: `readout` gains the optional `idle` word (definition data,
  never saved).
- Door definitions, expanded boards and panels, and the masterKey item field:
  `building` → `buildingId` (definition data, never saved).
- No `SAVE_KEY` change; PATCH.

## In scope

- #356: the blackout counts as asleep for clock events, ends early when woken,
  gets prorated Energy, and uses the split log line. The stumble is unchanged.
- #337: `readout.idle`, the heater's and pump's `idle` words, and
  `loadStatusText()`'s three-way rule, with the drawing test including the
  pump's latch. Plus the POWER SCHEMA comment and the validator check.
- #89: the rename across doors, masterKey, boards and panels; the schema
  comments; the stove-timer comment.

## Explicitly out of scope

- **#344**, the Atucha gate text. It's a lore discussion, held for later.
- #333 (wiring the TV and washing machine), #258 (removing the unwired-room
  fallback), #222 (the cooking balance pass).
- Any new clock event, siren wording change, or change to sleep itself.
- Changing the fridge-freezer's readout, or giving any other appliance an
  `idle` word.
- Renaming `room.building`.

## Sections touched

- **SURVIVAL/TIME SIMULATION** (mechanics): `advanceTime()`, `runAwakeStep()`
  or a sibling, the `asleep`/`wokenUp` comment.
- **WORLD DATA** (definition data only): APPLIANCES' `readout` for
  `water_heater` and `house_pump`; the ITEM DATA SCHEMA comment; the ROOM
  SCHEMA and door-definition comments.
- **POWER** (wherever the ARCHITECTURE comment places `expandWiring()`, the
  index builder and `validateWiring()`): the `buildingId` rename, and the
  `idle` validator check.
- **ACTIONS:** `findKeyForDoor()`, the masterKey unlock loop, and the stove
  timer comment.
- **RENDERING:** `loadStatusText()`, and the device-name disambiguator's
  `node.building`.

Check each against the ARCHITECTURE comment; it is the source of truth for
where these live.

## UI changes

- The blackout's log line is split. When the siren falls inside a blackout,
  you get "A siren wakes you…" and come to early, with less Energy.
- The water heater's and pump's readouts show "Standing by" while powered and
  idle, and "Running" only while drawing.
- No visible change from #89.

## Dependencies / issue linkage

Fulfils #356, #337 and #89. The pull request closes all three
(`Closes #356`, `Closes #337`, `Closes #89`). Nothing is expected to be
deferred. If something is, file it at the wrap.

## Open questions for Tom

None. Everything above was settled with Tom on 2026-09-30.

## After implementation

Open a pull request with the version bump and a new `CHANGELOG.md` entry per
`CHANGELOG_GUIDE.md`. The entry references this handoff by path and records
the implementation choices made above (the blackout's early exit, the `asleep`
flag's name, how the readout gets "drawing now"). The pull request closes
#356, #337 and #89, and `git mv`s this file to `handoffs/archive/`.
