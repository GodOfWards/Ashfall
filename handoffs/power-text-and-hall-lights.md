# Ashfall Handoff — Power text fixes: load readouts, hall lights, and room text in old saves

Current shipped version: v0.9.3
Implied version-change type: PATCH. No state field is added. The new
appliance field and the new appliance are definition data. The load-time
resync rewrites existing room data and adds nothing to the save.
Issue: #278 — A save keeps the room text it was written with
Also closes: #279 — A load's readout says "Light on" / "Dark" for every
appliance; #280 — Acorn's hall lights are found on only 30% of runs;
#277 — APPLIANCES comment gives the oven glow bar as 372–432 W

## What this is

Four small fixes that surfaced around v0.9.3's power text, in one PATCH:

1. **#278.** A save from before v0.9.3 keeps its old room text, because
   `serializeGame()` writes `world` whole. On every load, room text is
   now copied again from the definitions.
2. **#279.** `loadStatusText()` says "Light on" / "Dark" for every
   switchable load, so a fan or a hood reads as if it were a light. Each
   appliance now defines its own readout words.
3. **#280.** Acorn's hall and stair lights use `led_light`, which is
   found switched on in 30% of runs. They become a new switchless
   appliance, `hall_light`, lit whenever power reaches it. The hallway's
   dark text stops saying the bulb is "dead".
4. **#277.** A comment gives the wrong wattage for the oven's glow bar.
   Comment only.

## Relevant existing state

Verified against `ashfall.html` at v0.9.3 (`main` at 89264a0).

**Room text and saves (#278).**
- `serializeGame()` (PERSISTENCE) writes `world` whole, so every room's
  `desc` travels in the save.
- A room's `desc` is a string or `{ reads:{ kind, id? }, variants:{ … } }`.
  It is read only through `roomDescText(room)` (RENDERING), with
  `DESC_READERS` (`load`, `grid`, `crossing`).
- Nothing assigns to a room's `desc` at runtime. A grep for
  `\.desc\s*=[^=]` finds no hits.
- The load path runs its backfills after validation, in this order:
  `resyncUidCounter()`, `backfillItemIds()`, `backfillSlotItemIds()`,
  `backfillRegistryTags()`, `backfillLocationIds()`,
  `backfillRenamedContainers()`, `backfillContainerFields()`,
  `backfillRoomAddresses()`, `backfillIllnessScale()`,
  `backfillInventoryCap()`, then `migrateCookingRelease()` and `render()`.
- There are two precedents:
  - `backfillRoomAddresses()` builds `makeDefaultWorld()` once and copies
    four static label fields from it, but only when `address` is missing.
  - `backfillRegistryTags()` recopies item `tags` from the registry on
    every load, unconditionally.
- The symptom, checked in the issue: a v0.9.2 save loaded into v0.9.3
  shows the 2A kitchen's old text, "The gas stove works too — no power
  needed to light it." `validateRoomSchema()` passes, because a plain
  string is still a legal `desc`.

**Load readouts (#279).**
- `loadStatusText(loadId)` (RENDERING) returns:
  - `"Light on"` when `loadPoweredNow(loadId)`;
  - otherwise `"Dark · switched on"` or `"Dark · switched off"`, from
    `switchOnIn(state.power, state.seed, loadId, APPLIANCES[l.appliance])`.
- It has three callers, all for switchable loads only:
  - `renderLoadSwitchPop()` (the device pop-up);
  - the Here strip's `worldDeviceState`, when `tabLoad` (from
    `switchableLoad()`) is set;
  - `renderCircuitTab()`, which skips it when `a.switchless`.
- `APPLIANCES` (WORLD DATA, POWER SCHEMA) has six entries. The four with
  a switch:

  | id | name | leftOnChance |
  |---|---|---|
  | `fridge_freezer` | Fridge-freezer | 0.99 |
  | `led_light` | Light | 0.3 |
  | `bath_fan` | Exhaust fan | 0.05 |
  | `range_hood` | Range hood | 0.05 |

  The two without, both `switchless:true`: `smoke_alarm` (Smoke alarm)
  and `gas_range` (Gas range).
- `validateWiring()` already checks every `APPLIANCES` entry: exactly one
  of `leftOnChance` and `switchless`, and a nameplate at or above the
  entry's `watts`.

**Hall lights (#280).**
- `ACORN_HOUSE_ROOMS = ["hallway1", "hallway2", "stairs1", "stairs2"]`.
- `WIRING.acorn.common` (the House panel) has one `house` circuit (15 A)
  with a fixture in each of those rooms:
  `ACORN_HOUSE_ROOMS.map(r=> ({ key:\`light_${r}\`, appliance:"led_light", circuit:"house", role:r }))`.
  None has a `container`, so none is a room fixture with Device Options.
- `led_light` is `{ name:"Light", watts:10, volts:120, leftOnChance:0.3,
  nameplate:{ printsWatts:true } }`. The POWER SCHEMA comment sources the
  10 W: "an LED bulb draws 8–15 W (Champion)".
- `switchOnIn()` returns `true` for a switchless appliance before it reads
  `state.power.switches`. `setSwitchIn()` and `doSwitchLoad()` refuse
  switchless ones.
- `hallway2`'s `desc` reads `{ kind:"load", id:"acorn.house.light_hallway2" }`:
  - `on`: "A dim corridor lit by one flickering bulb. Your door is one of
    two here, with a small transom window set beside it."
  - `off`: "A dark corridor, its one bulb dead. Your door is one of two
    here, with a small transom window set beside it."

**The glow-bar comment (#277).**
- The POWER SCHEMA comment's `gas_range` line ends: "…so no `startWatts`;
  the 372–432 W glow bar is the oven's igniter, and the oven isn't
  modelled (#259)."
- Reference figure (`docs/canon/reference/Electrical.md`; secondary
  sources, checked 2026-09-25: a solar-electric.com forum thread and
  Engineer Fix):
  - flat glow bars draw 3.2–3.6 A, which is **384–432 W at 120 V**;
  - round ones draw 2.5–3.0 A, which is **300–360 W**.

## Rules / mechanics

### 1. Room text is copied again on every load (#278)

- New `backfillRoomDescs()`, in PERSISTENCE, beside
  `backfillRoomAddresses()`.
- For every room id in `world` that `makeDefaultWorld()` also has, it
  sets `world[id].desc` to the defaults' `desc`. This happens on every
  load, whatever the save holds, the way `backfillRegistryTags()` works.
  It is safe because nothing mutates `desc` in play.
- A room the defaults don't have is left as it is.
- It runs in the load path's backfill block, after validation, next to
  `backfillRoomAddresses()`.
- Its comment says why the resync is unconditional. `desc` is static
  content that the save carries only because `world` is written whole. So
  every content pass that edits room text reaches existing saves without
  a migration of its own.
- The save format doesn't change, and `serializeGame()` is untouched.

### 2. Each appliance defines its readout (#279)

- Every `APPLIANCES` entry **without** `switchless` gains
  `readout:{ on, off }`, two strings. `switchless` entries carry none,
  since their readout is never shown.
- `loadStatusText(loadId)` returns:
  - `a.readout.on` when `loadPoweredNow(loadId)`;
  - otherwise `a.readout.off + " · switched on"` or
    `a.readout.off + " · switched off"`, by the same `switchOnIn()` call
    as today.
- The words are decided. Functional UI text, retunable:

  | id | `readout.on` | `readout.off` |
  |---|---|---|
  | `fridge_freezer` | Light on | Dark |
  | `led_light` | Lit | Dark |
  | `bath_fan` | Running | Silent |
  | `range_hood` | Running | Silent |

  The fridge keeps its current words, because what you observe at a
  fridge is its door light.
- `validateWiring()` reports a problem for an appliance without
  `switchless` whose `readout.on` or `readout.off` is not a non-empty
  string.
- The POWER SCHEMA comment documents `readout` in the APPLIANCES schema
  block. Its schema line becomes
  `{ name, watts, volts, leftOnChance | switchless, nameplate, readout?, startWatts?, … }`.
  It says `readout` is required exactly when `leftOnChance` is present.

### 3. The hall lights are switchless (#280)

- New `APPLIANCES` entry `hall_light`:
  `{ name:"Light", volts:120, switchless:true, nameplate:{ printsWatts:true } }`,
  with the same `watts` as `led_light` (see Design decisions below; the
  figure must not be written twice).
- `name:"Light"` keeps what the player sees unchanged: these rows already
  read "Light".
- POWER SCHEMA comment line for it: a common-area light. It is
  switchless as a design choice, not a sourced fact. A hall or stair light
  in a shared building is treated as always on, so it is lit whenever
  power reaches it. Retunable. Its draw is `led_light`'s bulb.
- `WIRING.acorn.common`'s fixtures use `appliance:"hall_light"` for all
  four `ACORN_HOUSE_ROOMS`. Nothing else in `WIRING` changes.
- `hallway2`'s `off` variant becomes: "A dark corridor. Your door is one
  of two here, with a small transom window set beside it." The `on`
  variant is unchanged.
- Consequences:
  - While the grid is up and the House breakers are on, all four hall
    lights are lit on every run, and `hallway2` reads its `on` text.
  - When the grid fails, or a breaker feeding them trips or is switched
    off, `hallway2` reads the `off` text.
  - In the Electrical view, the House circuit's rows now show no readout
    and no Switch button, as the smoke alarm's rows do. Their nameplate
    and meter Test stay.
- An older save may carry `state.power.switches` entries for
  `acorn.house.light_*`. They are left in place and ignored:
  `switchOnIn()` answers `true` for a switchless appliance before it reads
  them, and `setSwitchIn()` never writes one. Deleting them would imply a
  schema cleanup the load path deliberately doesn't do, the same reasoning
  its comment gives for the stale `invTab` / `worldTab`.

### 4. The glow-bar comment (#277)

- In the POWER SCHEMA comment's `gas_range` line, change "the 372–432 W
  glow bar" to "the 384–432 W glow bar (a flat one; a round one draws
  300–360 W)".
- Nothing reads it.

## Design decisions to make during implementation

- **How `hall_light` shares `led_light`'s 10 W.** Either a named constant
  used by both entries, with the Champion source moved to it, or
  `hall_light` built from `led_light`'s `watts` after the object literal.
  Recommended: the named constant, beside `APPLIANCES`. Record which one
  you picked.
- **One `makeDefaultWorld()` or two on load.** `backfillRoomDescs()` can
  build its own defaults, or share one build with
  `backfillRoomAddresses()`. Either is fine; record which.

Neither choice affects the tier.

## Data / schema changes

- **State fields:** none.
- **APPLIANCES:** `readout:{ on, off }` on the four switchable entries;
  the new `hall_light` entry. This is definition data for #279's readout
  rule.
- **WIRING:** Acorn's House fixtures change appliance from `led_light` to
  `hall_light`.
- **Rooms:** `hallway2`'s `off` variant text.
- **Save format:** unchanged. On load, room `desc` is overwritten from the
  definitions.

## In scope

- `backfillRoomDescs()`, and its call in the load path.
- `readout` on every switchable appliance, `loadStatusText()` reading it,
  and `validateWiring()` checking it.
- The `hall_light` appliance, Acorn's House fixtures using it, and
  `hallway2`'s `off` text.
- The POWER SCHEMA comments: the `readout` schema, `hall_light`'s line,
  and the glow-bar figure.

## Explicitly out of scope

- **#258:** removing the unwired-room fallback. It waits on #252–#257.
- **#29:** the log's size and cap. It waits on a play session.
- **How the player notices the grid failing** (#220, "Not owned by any
  pass yet"). The hall lights going dark is a side effect of this pass,
  not the answer to that question. Add no log line, sign or new room text
  for it.
- Readout words for other buildings' appliances, which don't exist yet.
- Removing `desc` from saves, or making render read it from the
  definitions. #278's second option was not chosen.
- Other rooms' text. Only `hallway2`'s `off` variant changes.

## Sections touched

- **WORLD DATA:**
  - `APPLIANCES` and the POWER SCHEMA comment;
  - `WIRING.acorn.common`;
  - `hallway2`.
- **PERSISTENCE:**
  - `backfillRoomDescs()` and the load path;
  - `validateWiring()`, for the `readout` check.
- **RENDERING:** `loadStatusText()`.
- No ACTIONS or SIMULATION code changes. `switchOnIn()`, `setSwitchIn()`,
  `doSwitchLoad()` and the resolver already handle a switchless load.

## UI changes

- **Readouts.** Exhaust fans and range hoods read "Running", or
  "Silent · switched on/off", in the device pop-up, the Here strip and
  the Electrical view. Lights read "Lit", or "Dark · …". The fridge is
  unchanged.
- **Acorn's halls and stairs.**
  - Lit on every run while powered.
  - Their Electrical view rows lose the readout and the Switch button.
  - The 2nd-floor hallway's dark text drops "its one bulb dead".
- **Old saves.** A save from v0.9.2 or earlier shows current room text
  after loading.

## Dependencies / issue linkage

- Fulfils #278, #279, #280 and #277. The pull request says `Closes #278`,
  `Closes #279`, `Closes #280` and `Closes #277`, one line each.
- Part of the power work tracked in #220.
- Expected to defer nothing. If the pass surfaces anything, file it at
  wrap time.

## Open questions for Tom

None. Every design question was answered in planning.

## After implementation

Open a pull request carrying:
- the version bump (PATCH);
- a new `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, citing this
  handoff by path and recording both implementation choices above;
- this handoff moved to `handoffs/archive/`;
- the four `Closes` lines.

Validation to show:
- a syntax check;
- `validateWiring()` reporting no problems;
- a save made on `main` before this pass, loaded into the new build,
  showing the 2A kitchen's current text;
- `hallway2`'s `on` text in a fresh run while the grid is up, and its
  `off` text after `POWER_FAILS_DAY`;
- `git diff origin/main...HEAD -- ashfall.html` limited to the sections
  named above.
