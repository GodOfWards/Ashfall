# Ashfall Handoff — The power foundation

Current shipped version: v0.8.2
Implied version-change type: MINOR — one bump for the whole release, one `SAVE_KEY` rotation
Issues (closed by this release's PR):
  #260 — Running water follows the grid
  #240 — Rooms need their windows (this release ships the shape, not the placements)
  #241 — Power network engine
  #243 — Electrical rules setting

## What this is

The first release of the power system designed in #220. Power stops being one
global date check and becomes a **network**. The network has:

- **sources**: the grid, for now;
- **distribution**: a complex's main board, a building's or unit's panel, and
  branch circuits, each protected by a breaker;
- **loads**: fixtures and appliances.

The rest of the game asks it one question: **is this load powered?** Spoilage is
the first reader.

It is one MINOR because Tom asked that the release's new persistent state break
saves once, not three times. It also carries the window and door **shape** the
building passes need, the **rules setting** chosen when a run starts, and
**running water following the grid**.

It is **one handoff, implemented in the order below, on one branch, shipped as
one version with one changelog entry and one pull request**, the way the cooking
release was.

**No building is wired by this release.** Acorn Apartments' wiring is the next
handoff (#251), planned to land straight after this one. Until a room is wired,
it **falls back to the grid directly**: everything behaves as today, except that
fridge and freezer coasting is removed (Phase 5). The engine is therefore
checked through the dev seam with a test network (Phase 8), not in play.

## How to work through this

- **Order is fixed.** Each phase depends on the ones before it. Don't start a
  phase until the previous phase's checks pass.
- **One commit (or more) per phase**, each message starting `Phase N:`. A
  session resuming the work finds the last `Phase N:` commit, re-runs that
  phase's checks, and continues from `N + 1`.
- **Checks** run in headless Chromium (Playwright is pre-installed; drive
  `ashfall.html` from a `file://` URL) and through the dev seam
  (`window.ashfallDev`). **The dev seam stays read-only.** Don't add a debug hook
  that mutates game state.
- **The version bump, changelog entry and archive move happen once, in Phase 8.**
- **Line numbers are approximate** (v0.8.2). Find code by identifier.

## Relevant existing state

Verified against `main` at v0.8.2 (`GAME_CONFIG.VERSION = "0.8.2"`,
`SAVE_KEY = "ashfall_save_v0.8"`).

### The collapse clock, power and water (CONFIG / CONSTANTS, WORLD INTERACTION)
- **Constants** (about line 474): `START_DAYS_AFTER_COLLAPSE = 2`,
  `POWER_FAILS_DAY = 21`, `WATER_FAILS_DAY = 21`. The comment says they're
  separate "since they will be set separately (#149)".
- **Predicates** (about line 5455), both reading `minutesSinceCollapse()`:
  - `powerOn(m)` is true before `POWER_FAILS_DAY`;
  - `waterRunning(m)` is true before `WATER_FAILS_DAY`.
- **Readers:**
  - `powerOn()` has **one** caller, `spoilageRate()`.
  - `waterRunning()` has **one** caller, `canFillAtSink()`, plus a comment in
    ROOM SCHEMA's `sink` entry.

### Spoilage (SURVIVAL / TIME SIMULATION, about lines 5750–5870)
- **Constants:** `FRIDGE_RATE_POWERED = 0.1`, `FRIDGE_RATE_COASTING = 0.25`,
  `FRIDGE_COAST_MIN` (2 days), `FREEZER_COAST_MIN` (5 days).
- **`spoilageRate(container, m)`:**
  - a `freezer` returns 0 until `FREEZER_COAST_MIN` after the failure, then 1;
  - a `fridge` returns `FRIDGE_RATE_POWERED` while `powerOn(m)`, then
    `FRIDGE_RATE_COASTING` until `FRIDGE_COAST_MIN`, then 1;
  - anything else returns 1.
- **`isFrozenIn(container)`:** a freezer whose rate is 0 now. It drives the
  "(Frozen)" label (in `itemStateLabels`, about line 8304).
- **`effectiveAge(container, fromM, toM)`:** integrates `spoilageRate()`
  analytically, cutting at the failure and at the two coast ends. Its readers:
  - `stampAges()` (a world item's starting age, over `[0, now]`);
  - `ageFood(dt)` (every one-minute tick, over `[now − dt, now]`).
- **`stampMissingAges()`** runs on a new game and on load. `doOpenContainer()`
  stamps rolled items.

### Fridges and freezers in the world
- **Containers tagged `fridge` / `freezer`**, one pair per kitchen, with ids
  `fridge`/`freezer` (2A), `fridge`/`freezer` (2B, a different room),
  `fridge1a`/`freezer1a` (1A). Found by `hasTag()`.
- **A container carries no link to any appliance.**

### Time
- **Every advance goes through steps of one minute or less.** `runAwakeStep()`,
  the sleep loop and the other waits all call `applyWorldTicking(dt)` for each
  step.
- **`applyWorldTicking(dt)` runs, in order:**
  - `ageFood(dt)`;
  - battery drain on items that are `on`;
  - `tickStoveTimers(dt)`;
  - per room, `cookInHeat()` and the fire's burn-down.

### Doors and windows (WORLD DATA, WORLD INTERACTION, RENDERING)
- **`makeDefaultDoors()`** returns five entries, `{ locked, sides:[a,b],
  building }`, where `building` is a BUILDINGS **id** (`"acorn"`). They're
  `2a`, `2b`, `1a`, `1b`, `1a-patio`: all entry doors, and only `2a` starts
  unlocked. **There's no open/closed state.**
- **`makeDefaultWindows()`** returns two entries, `{ state, rooms:[a,b],
  breakTag, label }`: `2a-transom` (hallway2 to living) and `1b-alley` (alley
  to onebee). `state` is `"closed"`, `"open"` or `"broken"`.
- **`getExitsForRoom()`:**
  - drops an exit whose `doorId` names a locked door;
  - adds a "Climb through the …" exit for every window touching the room whose
    state isn't `"closed"`.
- **`doOpenWindow` / `doCloseWindow` / `doBreakWindow`** set `windows[id].state`.
  `renderHereActionsPanel()` offers Open / Break (with the `breakTag` tool) on a
  closed window, and Close on an open one.
- **`doToggleLock(doorId)`** flips `locked`. Keys offer Lock / Unlock in their
  item pop-up (`getItemActions()`, about line 5236), for every door
  `doorsTouchingRoom()` returns. A locked door the player has no key for shows
  a `hereNote` ("The … door is locked.").
- **The helpers:** `doorsForRoom()`, `gatedExitsForRoom()`, `doorsTouchingRoom()`,
  `doorLabel()`, `findKeyForDoor()`.

### Persistence (PERSISTENCE)
- **`serializeGame()` writes `{ version, state, world, doors, windows }` whole.**
  Anything in `world`, `doors` or `windows` is frozen into every save.
- **`applyLoadedData()`:**
  1. merges `data.state` over `makeDefaultState()`, which is how a save lacking
     a state field gets its default;
  2. validates with `validateLoadedWorld()`;
  3. commits;
  4. runs the backfills and then `migrateCookingRelease()`, which is idempotent.
- **`doRestart(seed)`** rebuilds state, world, doors and windows, stamps ages
  and logs the wake-up line. **Options → Restart game** prompts for an optional
  seed, then calls `doRestart()`.
- **The dev seam** (end of file) is `window.ashfallDev = { validateItemRegistry,
  validateLocations, validateRoomSchema, validateReachability, simulateSeed,
  sampleSeeds }`. These are console helpers and run nothing automatically.

### Rolls
- **`chance(p, ...keyParts)`, `rollValue(...keyParts)` and `randInt()`** are keyed
  on `state.seed`, and pure for a given key.
- **`rollSeq`** is only for rolls with no natural key. "Nothing reachable from
  render() may advance rollSeq." **Keyed rolls are safe anywhere.**

### Devices in the Here panel (RENDERING, EVENTS / UI HELPERS)
- **Tabs:** Here tabs come from `listedContainers(room)`.
- **Strip:** a container tagged `device` shows the strip under the tabs, with
  `#worldDeviceState` and `#deviceOptionsBtn`.
- **Pop-up target:** `deviceTarget = { kind:"container", id }` (UI-only, never
  saved). `resolveDeviceTarget()` resolves only that kind.
- **Pop-up:** `renderDevicePop()` draws the stove's controls. It holds a bold
  name line, status lines, then `pop-actions` buttons.

### Rooms
- **`room.building`** is a building's **name**, absent outside buildings and on
  the three flats above the Main St shops.
- **`room.shelter`** is `"none"`, `"partial"` or `"full"`:
  - 37 rooms are `"full"`: every indoor room, the three flats included.
  - 4 are `"partial"`: the two Acorn balconies (`balcony`, `twobee_balcony`),
    and two outdoor street nodes (`mill2nd` under a conveyor bridge,
    `mid_cedar_1_2` with a bus shelter).
- **`BUILDINGS`** is keyed by id (`acorn`, `oak`, `cornerstore`, …) with `name`
  and `anchor`.

## Global rules and constants

Every value below is a **judgment call or a sourced figure**, as marked.
Retunable ones get a named constant beside the system that owns them.

**Breakers (sourced; UL 489 via ABB's white paper and Castor, *Molded Case
Circuit Breaker Basics*, EasyPower):**
- **100% of rating: never trips.**
- **135% of rating** trips within **60 min** at 50 A or less, and **120 min**
  above 50 A.
- **200% of rating** trips within:

  | Rating | Max time at 200% |
  |---|---|
  | 0–30 A | 2 min |
  | 31–50 A | 4 min |
  | 51–100 A | 6 min |
  | 101–150 A | 8 min |
  | 151–225 A | 10 min |

  Above 225 A the table wasn't read. **Use 10 min, flagged.**
- **Instant (magnetic) trip at 7.5× rating**: the typical calibration of a
  C-curve breaker, whose band is 5–10× (ABB). Applying it to US plug-in panel
  breakers is an **approximation, flagged**.

**Refrigerator (sourced range; figure picked within it, per Tom's
"measured range"):**
- **Running 150 W.** The measured range is 100–250 W; Champion's chart gives
  150–400 W.
- **Starting 3.5× running**, so **525 W total** at a start. The rule of thumb is
  3–4×.
- **Duty cycle 35%.** The measured range is 33–40% in a room at about 70 °F.

**Judgment calls, retunable:**
- **Compressor cycle period: 60 min** (on for 21 min at 35%). Not sourced.
- **Heat meter cooling: fully drains in 30 min** below the rating.
- **Switch starting state: on with chance 0.9.** Tom: "random but left on in
  almost all cases."
- **Breakers start on and untripped.**
- **Circuit voltage:** a 120 V circuit's current is watts ÷ 120. A 240 V
  circuit's (a two-pole breaker) is watts ÷ 240.
- **A panel or board treats its loads as balanced across two legs.** Current =
  total watts ÷ the panel's `volts`, which defaults to 240 and is a per-panel
  field. Real apartment buildings are often 120/208 V (#241). The field is there
  for a building pass to set, and the default is **flagged**.

## Phase 1 — Water follows the grid (#260)

- **Replace `powerOn(m)` with `gridUp(m)`**: the grid source's state, the same
  test against `POWER_FAILS_DAY`.
- **`waterRunning()` returns `gridUp()`.** Delete `WATER_FAILS_DAY`.
- **Update:** the constants comment (water no longer has its own day; #149's
  water option is moot while this holds) and ROOM SCHEMA's `sink` note.
- **The water follows the grid, not a building's power.** Nothing in this
  release can restore a building's power without the grid anyway, and the rule
  holds when generators arrive (#245).

### Checks — Phase 1
- Before day 21, a sink fills a bottle. After day 21 (advance time with Rest or
  Sleep), it doesn't.
- `spoilageRate()` gives the same results as before at every minute. The rename
  alone changes nothing: diff-check it.

## Phase 2 — Windows and doors: the shape (#240)

### Definitions split from saved state
- **Definitions** are what `makeDefaultDoors()` / `makeDefaultWindows()` author.
  They're **never saved**.
- **Saved state** is only what changes in play:
  - a door's `locked` and `open`;
  - a window's `state`.
- **Recommended implementation:** keep the runtime `doors` / `windows` objects
  in their current merged shape, so every existing reader keeps working. Change
  only the edges:
  - `serializeGame()` writes `doors` as `{ id: { locked, open } }` and
    `windows` as `{ id: { state } }`;
  - `applyLoadedData()` and `doRestart()` rebuild from the definitions, then
    apply the saved fields for ids the definitions still have.
  - A saved id the definitions no longer have is dropped. A definition the save
    lacks takes its authored default.
- **A v0.8 save's full door and window objects** already carry `locked` and
  `state`, so this loader reads them unchanged (a missing `open` is `false`).

### Windows
- **New definition field `climbable`** (default `false`). The two existing
  windows set `climbable:true` and behave exactly as today.
- **A window may have one room** (`rooms:[roomId]`): it opens to the outside.
  Or two, as today.
- **`getExitsForRoom()` only adds a climb exit for a window that is
  `climbable`, has two rooms, and isn't `"closed"`.**
- **Open / Close / Break stay offered on every window**, climbable or not. A
  broken non-climbable window is still not a route.
- **No new windows are placed.** Placement belongs to the building passes
  (#250).

### Doors
- **New saved field `open`** (default `false`). **A locked door is always
  closed.**
- **New definition field `lockable`** (default `true`). Interior doors authored
  later may set it `false`, and then no key action or locked note applies.
- **Here actions**, for every door `doorsTouchingRoom()` returns:
  - **"Open the … door"** on a closed, unlocked door;
  - **"Close the … door"** on an open one.
  - Instant, like the window actions. Log lines: "You open the … door." /
    "You pull the … door shut."
- **Locking an open door closes it too.** The key's action reads "Lock the …
  door" either way. The log says "You close the door and lock it." when it was
  open.
- **Movement is unchanged.** Only `locked` gates an exit. Passing through a
  closed unlocked door leaves it closed.
- **`open` has no reader yet besides its actions.** It is laid down ahead of its
  consumer, carbon monoxide (#248, on hold), the way ROOM SCHEMA's `shelter`
  was. Say so in the DOOR schema comment.

### Checks — Phase 2
- The 2A door opens and closes from the hallway and from the living room.
  Locking it while open closes it.
- The transom and the alley window open, close, break, and are climbable
  exactly as before.
- Save, reload, export and import: door `locked` / `open` and window `state`
  survive. The exported file's `doors` / `windows` hold only those fields.
- A v0.8.2 export imports: the doors keep their locks, the windows keep their
  state.

## Phase 3 — Power definitions and state (#241, #243)

### Definitions (WORLD DATA, never saved)
Shapes are binding. Names are the coding session's (see "Design decisions").

- **`APPLIANCES`**, keyed by id: `{ name, watts, startWatts?, volts,
  dutyCycle?, cycleMinutes? }`.
  - `startWatts` (the total draw at a start) marks a motor load.
  - `dutyCycle` + `cycleMinutes` mark a cycling one.
  - **This release defines one entry:** `fridge_freezer`: 150 W, starting
    525 W, 120 V, duty cycle 0.35, 60-minute cycle. It's the appliance behind
    every kitchen's Fridge + Freezer pair. It is definition data for the
    mechanic's first reader (spoilage), so it rides here, per `CLAUDE.md`.
- **`WIRING_TEMPLATES`**, keyed by id. A unit layout **by room role**:
  - its panel's main rating and `volts`;
  - its circuits (key, hand-written `label`, rating in A, `volts`, the roles
    it serves);
  - its fixtures (key, appliance id, circuit key, role, and optional container
    ids the fixture is).
  - **This release defines no template.** Acorn's pass (#251) defines the first.
- **`WIRING`**, keyed by BUILDINGS id. **Empty in this release.** Its shape:
  - a **board** (the room it hangs in, its main rating, `volts`, and one
    feeder breaker per panel with its label and rating);
  - **panels** (an id, the room it hangs in, and a template id with a
    role→room-id map, or an inline layout of the template's shape);
  - an optional **common panel or circuits** for halls and stairs.
  - Rooms are named by **room id**, never by `room.building`, because the flats
    above the shops have no `building`.
- **Expansion at startup.** `WIRING` expands once into a flat table of nodes with
  **stable ids** such as `acorn.2A.kitchen`, `acorn.2A.main`, `acorn.board.2A`.
  It also yields:
  - a lookup from (room id, container id) to the load that container belongs
    to;
  - the device list per room: which panels and boards hang there.

### State (PLAYER STATE, saved)
- **`state.power`:**
  - `switches: { loadId: bool }`;
  - `breakers: { breakerId: { on, tripped } }`;
  - `heat: { breakerId: number }`.
  - **Only entries that differ from their default are stored.**
    `makeDefaultState()` gives `{ switches:{}, breakers:{}, heat:{} }`.
- **A switch's default** is `chance(SWITCH_LEFT_ON_CHANCE, "power", "switch",
  loadId)`, which is keyed and pure. So a load the save has never seen (a
  building wired after the run started) gets a rolled state on first read with
  nothing written, and render stays roll-safe.
- **A breaker's default** is on and untripped, with heat 0.
- **`state.electricalRules`:** `"detailed"` or `"simplified"`, set when the run
  starts and never changed during it (#243). `makeDefaultState()` defaults it to
  `"detailed"`, which is also how a v0.8 save gets it.

### Checks — Phase 3
- A new game's `state.power` is empty and `state.electricalRules` is
  `"detailed"`.
- A test network passed through the Phase 8 dev helper expands to the expected
  ids.

## Phase 4 — The resolver (#241)

**Resolve every step.** The networks are small (tens of rooms), so there's no
need for a dirty-flag cache. The result is kept for render to read. **Make the
resolution a pure function of (definitions, `state.power`, rules, minute)** so
the dev seam can run it on a test network (Phase 8).

### Order within a step (called from `applyWorldTicking(dt)`, before `ageFood`)
1. **Sources:** the grid is live while `gridUp()`, with unlimited capacity. Its
   capacity is limited only by breakers.
2. **Live nodes:** a board is live if its source is live and its main is on and
   untripped. A panel is live if its feeder breaker on the board and its own
   main are on and untripped. A circuit is live if its panel is live and its
   breaker is on and untripped.
3. **Running loads:** a load draws if its switch is on and its circuit is live.
   A cycling load draws only during the on part of its cycle:
   `((minute + phase) mod cycleMinutes) < dutyCycle × cycleMinutes`. `phase` is
   `rollValue("power", "cycle", loadId) × cycleMinutes`, fixed per load, so the
   kitchens don't all cycle together.
4. **Starts:** a motor load **starts** in a step where it draws but didn't in
   the previous step (switched on, its cycle turned on, or its circuit came
   back). A starting load counts `startWatts` instead of `watts` for this step's
   **instant** check only.
5. **Instant check, lowest layer first:** circuit, then panel main, then board
   feeder, then board main. A breaker whose momentary current (running loads,
   plus starting loads at `startWatts`) exceeds **7.5 × rating** trips at once.
   Recompute below it before checking the next layer up.
6. **Heat check (the delayed trip):** for each live breaker, `f = current ÷
   rating`, using running watts.
   - **If `f > 1`:** `heat += dt ÷ t(f)`, with
     `t(f) = T200 ÷ (f − 1)^n` and
     `n = ln(T200 ÷ T135) ÷ ln(0.35)`,
     where T135 and T200 come from the breaker's rating (see Global rules).
     This passes exactly through the 135% and 200% points.
   - **If `f ≤ 1`:** `heat −= dt ÷ HEAT_COOL_MIN`, floored at 0.
   - **At `heat ≥ 1`:** the breaker trips. Check lowest layer first, and
     recompute after each trip.
7. **Tripped means off until reset.** Heat keeps cooling while tripped. A reset
   with the overload still present trips again quickly, as real breakers do.

### Simplified rules (`state.electricalRules === "simplified"`)
- **Circuits are ignored:** every load in a panel's rooms is on that panel.
- **Each panel is one breaker, its main.** The board is one breaker, its main.
- **Instant and heat checks apply to those** exactly as above.

### Log lines (game text; tone rules apply; wording retunable)
- **When a breaker trips and the player is in the room where its panel or board
  hangs:** "The panel on the wall snaps. A breaker has tripped."
- **When a breaker trips and the player is in a room where a load it fed was
  running:** "Everything in here goes quiet."
- **Otherwise, nothing.**
- **The grid failing logs nothing.** Noticing the grid fail is deferred (#220).
  Don't add it.

### Checks — Phase 4 (through the dev seam's test network, Phase 8)
- A 15 A, 120 V circuit carrying 1,800 W never trips. At 2,430 W (135%) it trips
  at 60 min. At 3,600 W (200%) it trips at 2 min.
- A 100 A panel main at 200% trips at 6 min.
- Two fridges starting in the same minute don't trip a 15 A circuit.
  Momentary current is 2 × 525 W ÷ 120 V ≈ 8.8 A, far under 112.5 A.
- A load switched on over a 7.5× momentary current trips its circuit at once.
- After day 21 every test load reads unpowered.
- In simplified mode, circuit breakers are never consulted.

## Phase 5 — Spoilage reads the network (#241)

- **`isPowered(loadId)`** reads the resolver's result.
- **`containerPowered(roomId, container)`:**
  - returns `isPowered(load)` when the container belongs to a load;
  - returns **`gridUp()`** otherwise. **This is the fallback for unwired
    rooms.**
  - `ageFood` and `isFrozenIn` need the container's room: pass it from
    `forEachItemList()`'s `roomId`.
- **`spoilageRate()`:**
  - powered fridge: `FRIDGE_RATE_POWERED` (0.1);
  - powered freezer: 0;
  - **anything unpowered: 1, immediately.**
  - **Delete `FRIDGE_RATE_COASTING`, `FRIDGE_COAST_MIN` and
    `FREEZER_COAST_MIN`.** Coasting returns with temperature (#217). Tom: an
    unpowered fridge spoils at room rate straight away.
- **`ageFood(dt)`** ages each step at the rate from the **current** power state.
  It no longer calls `effectiveAge()`.
- **`stampAges()` keeps an analytic starting age**, covering a container nobody
  has touched since the collapse:
  - it spoils at its powered rate until the grid's failure, then at 1;
  - **or at 1 throughout if its load's starting switch is off.**
  - `effectiveAge()` loses the two coast cuts and keeps only the failure cut.
- **`isFrozenIn()`** means a freezer that's powered now.
- **Update the CONTAINER SCHEMA's `fridge` / `freezer` notes** to say "while its
  load is powered", with coasting deferred to #217.

### Checks — Phase 5
- **Unwired world (this release):** Acorn's fridge food ages at 0.1 until
  day 21, then at 1 from that minute. The freezer reads "(Frozen)" until
  day 21 and not after.
- **With the dev test network wired to a fridge:** turning its switch off, or
  tripping its circuit, makes its contents age at 1 in the same step.

## Phase 6 — Panels and boards as devices (#241)

- **Tabs.** A room where a panel or board hangs gets a **device tab** for each,
  after its containers in the Here tab strip, labelled by the device's name
  ("Unit 2A panel", "Main board"; exact names come with the wiring).
  - These tabs are **not containers**: they come from the wiring's device list,
    not `room.containers`.
  - The strip shows the device's state (below) and **Device Options**.
- **`deviceTarget` gains a kind for them.** For example `{ kind:"panel", id }`.
  `resolveDeviceTarget()` resolves it through the wiring.
- **Detailed rules, the pop-up:**
  - the bold name line;
  - "Fed by the grid" or "No power";
  - then one row per breaker: **MAIN** first, then circuits in panel order.
    Each row shows its hand-written label, rating ("20 A") and state (On, Off,
    Tripped), and one button: **Switch off**, **Switch on**, or **Reset** when
    tripped.
  - A board lists its main, then one row per panel it feeds.
  - The strip reads "Main on" / "Main off", plus "N tripped" if any.
- **Simplified rules, the pop-up:** the name line, "Rating: 100 A", "On" or
  "Off", and one **Switch on / Switch off** button. Tom: "it only shows the
  rating and the turn ON/OFF button."
- **Switching and resetting are instant.** They log a functional line, for
  example "You switch the KITCHEN breaker off." or "You push the tripped KITCHEN
  breaker back on."
- **Watts never appear** (#242, #249).

### Checks — Phase 6
- With the test network (Phase 8), a panel's tab appears only in its room. Its
  pop-up switches and resets breakers, and the changes show in the next step's
  resolution. Simplified shows the one-switch form.
- In the unwired world no device tab appears anywhere. The stove's tab and
  pop-up behave exactly as before.

## Phase 7 — The rules setting (#243)

- **Options** gains a line for the current run, "Electrical rules: Detailed"
  (read-only), and a two-way choice for the next run: **Detailed** /
  **Simplified**. The choice is UI-only until a restart. **Restart game**
  applies it to the new run's `state.electricalRules`.
- **The current run's rules never change mid-run.** Tom: fixed once it starts;
  restarting offers the choice again.
- **The choice's default is the current run's rules.**
- **Later:** this moves to a New Game screen when #166 lands. Not in this
  release.

### Checks — Phase 7
- Choose Simplified, restart: the new run is simplified, and the choice
  survives save and load. A fresh page load starts Detailed.

## Phase 8 — Save migration, dev helpers, comments, wrap

### Loading older saves
- `SAVE_KEY` rotates, but **an imported v0.8.2 file must load:**
  - `state.power` and `state.electricalRules` come from `makeDefaultState()`'s
    spread;
  - doors and windows come through Phase 2's loader;
  - no container changes.
- **Loading twice changes nothing.**

### Dev helpers (read-only, in `window.ashfallDev`)
- **`validateWiring()`:**
  - every `WIRING` reference resolves: rooms, container ids, appliance ids,
    template ids, circuit keys, breaker ratings that are NEC 240.6 standard
    sizes;
  - lists every room with `shelter:"full"` that has no wiring. **That list is a
    warning while buildings are being wired (#250),** and becomes an error in
    #258.
  - In this release it lists all 37.
- **`simulatePower(network, minutes, options)`:** runs the resolver on a
  **supplied** test network, never the game's. It takes scripted switch or
  breaker changes by minute and returns per-minute currents, heat and trips.
  It's what Phases 4–6 are checked with.

### Comments
Keep the schema blocks whole and current:
- **CONSTANTS:** the collapse clock (no water day), the breaker and fridge
  figures with their sources.
- **ROOM SCHEMA:** `sink`.
- **CONTAINER SCHEMA:** `fridge` / `freezer`.
- **New DOOR and WINDOW schema blocks:** definitions vs saved state, `climbable`,
  `lockable`, `open` laid down ahead of #248.
- **New POWER schema blocks:** `APPLIANCES`, `WIRING_TEMPLATES`, `WIRING`, the
  expansion's ids, `state.power`.
- **ARCHITECTURE:** name where power lives. Recommended: a POWER sub-block
  inside SURVIVAL / TIME SIMULATION (the way STAMINA/FATIGUE sits there) for
  the resolver, with definitions in WORLD DATA.

### Wrap (per `CLAUDE.md`)
1. `GAME_CONFIG.VERSION` bumped as **MINOR**. With nothing else shipped in
   between, that's `0.9.0`, and `SAVE_KEY` becomes `ashfall_save_v0.9`.
2. **One** `CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, with
   `Implements: handoffs/power-foundation.md`, and every design decision
   resolved.
3. `git mv handoffs/power-foundation.md handoffs/archive/power-foundation.md`.
4. PR description: `Closes #260`, `Closes #240`, `Closes #241`, `Closes #243`
   (one per line).
5. New issues for anything cut or surfaced.
6. The tag commands in the final message.

### Checks — Phase 8
- Import a v0.8.2 export with a locked door, an open window and food in a
  fridge and a freezer. It loads, and the lock, the window and the food's ages
  survive. Import it twice: nothing changes the second time.
- All validators run. `validateWiring()` lists the 37 unwired rooms and no
  broken references.
- A full play-through of every phase's checks on the final build.

---

## Design decisions to make during implementation

Record each in the changelog's Notes / assumptions:
- **Identifier names:** `gridUp`, `isPowered`, `containerPowered`, `APPLIANCES`,
  `WIRING_TEMPLATES`, `WIRING`, `SWITCH_LEFT_ON_CHANCE`, `HEAT_COOL_MIN`,
  `INSTANT_TRIP_MULTIPLE`, the node id format. **The shapes above are binding.
  The names are not.**
- **How the door and window definitions split from saved state**, if it's done
  differently from the recommended runtime-merge approach. The save format is
  binding.
- **Where the resolver's per-step result is kept** for render, and how
  `ageFood` / `isFrozenIn` get the container's room.
- **The `deviceTarget` kind's name**, and how device tabs join the Here tab list.
- **The Options rules control's markup.** It must stay usable at phone width.
- **Where power sits in ARCHITECTURE**, if not the recommended POWER sub-block.

## Data / schema changes

**PLAYER STATE:** `power: { switches, breakers, heat }` and
`electricalRules`. **New persistent state: `SAVE_KEY` rotates.**

**WORLD DATA:**
- new: `APPLIANCES` (one entry), `WIRING_TEMPLATES` (empty), `WIRING` (empty);
- door definitions gain `lockable`;
- window definitions gain `climbable` (the two existing windows set it) and
  allow one room.

**Save format:** `doors` saves `{ locked, open }` per id, and `windows` saves
`{ state }` per id.

**Constants:**
- removed: `WATER_FAILS_DAY`, `FRIDGE_RATE_COASTING`, `FRIDGE_COAST_MIN`,
  `FREEZER_COAST_MIN`;
- new: the breaker, fridge and switch constants above.

## In scope

Everything in Phases 1–8.

## Explicitly out of scope

- **Any building's wiring:** #251 (Acorn, the next handoff), #252–#257, #258.
  `WIRING` ships empty.
- **The stove** (#259). It is untouched and still lights itself.
- **Room text that follows power** (#235).
- **The electrical view** (#242) and **meters and nameplates** (#249). No watts
  are shown anywhere.
- **Cords and plugging** (#244), **gasoline** (#239), **generators** (#245),
  **inlets** (#246), **shock** (#247), **carbon monoxide** (#248, on hold),
  **batteries** (#261).
- **Noticing the grid fail:** no log line or sign when the grid goes. Deferred
  in #220.
- **Cold-load pickup and coasting:** #217.
- **Faults building up on the grid by area, the grid's schedule, street lights
  and outdoor grid equipment.** Deferred in #220.
- **Three-phase service** (#256).
- **Placing any window or interior door** (#250's building passes).
- **Wells, the water tower, treatment and potability** (#47, #52).
- **#149** world-generation options. **#166** the New Game screen.

## Sections touched

- CONFIG / CONSTANTS: clock constants, the new breaker, fridge and switch
  constants.
- WORLD DATA: `APPLIANCES`, `WIRING_TEMPLATES`, `WIRING`, door and window
  definitions, the schema blocks.
- PLAYER STATE: `power`, `electricalRules`.
- WORLD INTERACTION: `gridUp`, `waterRunning`, windows in `getExitsForRoom`,
  door open/close, lock-closes.
- SURVIVAL / TIME SIMULATION: the resolver (POWER sub-block),
  `applyWorldTicking`, spoilage.
- PERSISTENCE: save format for doors and windows, load and restart rebuild, the
  rules applied at restart, dev helpers.
- EVENTS / UI HELPERS: `deviceTarget` for panels.
- RENDERING: device tabs and pop-ups for panels and boards, door actions,
  Options rules control.

Mechanics, plus the definition data they read (one appliance entry). No
instance data: no room, placement or description changes.

## UI changes

- **Here:** "Open the … door" / "Close the … door" on doors touching the room.
  Locking an open door closes it.
- **Here tabs:** panel and board device tabs with Device Options, in wired rooms
  only. There are none until #251.
- **Device Options (panel / board):** breaker rows with Switch on/off and Reset.
  In simplified rules, rating plus On/Off.
- **Options:** the current run's electrical rules, and a Detailed / Simplified
  choice for the next run.
- **Sinks** stop with the grid, as they already do on day 21.
- **Fridges and freezers stop protecting food the moment their power stops.**
  There's no two-day and five-day coast.

## Dependencies / issue linkage

Closes #260, #240, #241, #243.

Unblocks:
- #251, the next handoff, which wires Acorn and makes the engine visible;
- #252–#257, #258, #259, #235, #242, #249;
- the 0.10.0 portable-power bundle (#244, #239, #245, #246, #247).

Advances without closing #220 (the hub) and #250 (tracking).

Anything this pass cuts or surfaces becomes a new issue at the wrap.

## Open questions for Tom

None. Every design question was settled in the planning session at v0.8.2 and
recorded on #220, #240, #241, #243 and #260.

## After implementation

Open one pull request from the release branch carrying:
- the version bump;
- the single changelog entry, naming this handoff by path and recording every
  "Design decisions" resolution;
- the `git mv` of this file into `handoffs/archive/`;
- one `Closes #NN` line per issue listed at the top.

End the session's final message with `CLAUDE.md`'s tag commands.
