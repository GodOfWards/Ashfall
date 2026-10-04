# Ashfall Handoff — Atucha over the run, and the water network

Current shipped version: v0.13.0
Implied version-change type: PATCH
Issue: #344 — The Atucha entrance has a guard post; #439 — Atucha over the
run; #300 — The water network

## What this is

Three PATCH issues in one pass, built in three phases:

1. **A calendar and a darkness rule** (#439): the clock gets a real date, and
   "dark" means between civil dusk and civil dawn for that date. This is the
   game's first notion of night.
2. **Atucha at the gate and on the horizon** (#344, #439): the gate shows the
   real entrance (#344), and its text then follows the plant's three phases:
   the grid, the diesels, and silence. After dark, the north end of town sees
   the plant's lights while the diesels run.
3. **The water network** (#300): the mains lag the grid when it comes back.
   A home on a paved street fills its tank from the network and has no pump.
   A home on a gravel or dirt street fills it from its own well, with its
   own pump, whether or not the mains run.

Nothing in this pass adds a save field.

## Relevant existing state

Verified against `ashfall.html` at v0.13.0. Line numbers are approximate.

**The clock** (CONFIG / CONSTANTS ~570; SURVIVAL / TIME SIMULATION ~7196):

- `minutesSinceCollapse()` = `START_DAYS_AFTER_COLLAPSE * MINUTES_PER_DAY +
  state.totalMinutes`. Minute 0 of it is `DAY_START_MIN` (08:00) on the
  collapse day, which is the same frame `POWER_FAILS_MIN` uses.
- `absoluteMinute()`, `dayNumber()`, `minutesIntoDay()` derive the player's
  Day N and the time of day from `state.totalMinutes`. Day 1 is
  `START_DAYS_AFTER_COLLAPSE` days after the collapse.
- `TIME_OF_DAY_BANDS` are the vague clock's words. Their comment says a later
  light layer "is meant to read this table". **This pass doesn't**: Tom
  decided darkness comes from the daylight table (below). Rewrite that
  comment so it no longer claims the light layer will read the bands. The
  bands remain the vague clock's words only.
- `GRID_UP_SPANS`: half-open `[from, to)` spans of minutes since the
  collapse. Up until `POWER_FAILS_MIN`, then the false recovery,
  `GRID_RECOVERY_AFTER_MIN` later for `GRID_RECOVERY_MIN`. `gridUp(m)`,
  `gridUpMinutes()`.
- `GRID_CHANGES` (~8293), the spans' finite bounds, are scheduled events:
  `planNextDue()` and `settleWorld()` call `resolveGrid()` at each.
- `CLOCK_EVENTS` (~8212): the siren. `SIREN_SOURCE_STOP = "atucha_gate"`.

**Stop text** (WORLD DATA ~3742):

- `LIMA_STOP_TEXT.atucha_gate` is "The road ends at the Atucha complex. The
  fence runs off both ways, and the gate is shut. Beyond it, the plant's
  domes."
- `buildLimaStops()` sets each stop room's `desc` from `stopDesc()` once, at
  build time.
- A room's `desc` may already be state variants (ROOM SCHEMA ~863):
  `{ reads:{ kind, … }, variants:{ state: text } }`. `DESC_READERS`
  (RENDERING ~13856) has `load` and `grid`, and `roomDescText()` picks the
  variant. The room validation (~10777) checks every reader state has a text.
  `renderLocationPanel()` writes `roomDescText(room)` plus a fire note.
- `LIMA.stops` gives each stop `{ id, x, y, type, kind, … }`, in grid-frame
  metres with +y the grid's north. Town stops are kind `c` (corner) or `m`
  (mid). The northernmost town stops are at y ≈ 1,196–1,278. `atucha_gate`
  is a `rural` stop at (−2957, 7845).

**Water** (BUILDING TYPES ~4050–4300; SURVIVAL / TIME SIMULATION ~7255–7335;
POWER ~8640):

- `row_house`, `casa` and `shop_home` have `water:{ tankL:HOUSE_TANK_L }`.
  Every sink in the game is in one of them.
- `mainsWaterUp(m)` returns `gridUp(m)`. Its comment reserves it for #300.
- `tankRefillLph(b, m)` returns 0 unless `mainsWaterUp(m)`. Then:
  - a building with a pump (`TANK_PUMPS[b]`) refills at the pump's `flowLph`
    while the pump is drawing (`powerNow`);
  - a building without one (today only `shop_home`, which is unwired)
    refills at `HOUSE_PUMP_FLOW_LPH` whenever it's below full.

  Its comment says the rate "never changes between two settles: grid events
  and resolves are settle points".
- `settleTanks()` and `tankFullDue()` settle and schedule refills. A
  drawn-down tank has an entry in `state.tankDrawn`.
- `WIRING_TEMPLATES.row_house` and `.casa` each have a
  `{ key:"pump", appliance:"house_pump", circuit:"water", … }` fixture.
  The row house's is in the laundry, the casa's on the patio.
  `casa_fuses`, the old fuse board about half the casas get through
  `oldBoardOverrides()`, copies the casa's fixtures onto its one fuse
  circuit.
- `TANK_PUMPS` (~8657) is built from `tankPumpsOf()`. It finds every load
  whose appliance has `flowLph`, by building.
- `validateWiring()` (~10896–10906) reports a wired building with a tank and
  no `flowLph` load ("a tank, but no pump load"), one with two, and a
  `flowLph` load in a building with no tank.
- `BUILDING_INFO` (~5348): `{ name, site, entry, tankL }` per building.
- `LIMA.links`: `{ a, b, code, surface }`, where `surface` is `p` paved,
  `g` gravel, `d` dirt or `r` railway. The block's comment says only `r` is
  read today.
  - At v0.13.0, of the 428 house sites (mid stops), 200 are paved, 226 are
    unpaved and 2 are mixed (`m_c24_acc_c17`, `m_sn_c111_sn`).
  - The home stop `m_c90b_c117_c119` is paved, so the home and
    `row_neighbour` are both paved. The pharmacy's site `m_c7_c10_c8` and
    the corner store's `x_c113_c50` are paved too.
- The row house's laundry `desc`: "A washing machine, a deep sink, and the
  pump that fills the house's water tank. The back door opens onto the
  garden."
- `backfillPowerState()` (PERSISTENCE ~10470) rebuilds `state.power` on
  every load. It keeps `switches` and `breakers` as they are, and keeps a
  stop only for a load with a timed stop rule.
- `simulatePower()` (dev seam ~11280) refills a pump's tank "while the pump
  draws and the mains run" (its `mains` option, default `mainsWaterUp()`).
- **The replay's step 6** ("The tank drawn, the grid failing during a
  sleep…", ~11564) does this: it draws the home's tank to
  `REPLAY_TANK_MARGIN_L` above its float level, then below it with real
  fills, so that the home's pump is refilling as the grid fails and is still
  called for when it returns.
- Comments that name #300: ~6487 (the sinks: "whatever was left in the
  pipes is #300's") and ~7258 (`mainsWaterUp()`).

**Facts the work depends on**, quoted because the coding session reads
neither the canon nor the reference folder:

- **The plant's phases** (canon, "Atucha"):
  - Day 2 to day 21 after the collapse, the plant draws its cooling power
    from the grid.
  - From day 21 to about day 50, its diesels run.
  - After that it's dark and silent.

  Days are counted from the collapse, as `POWER_FAILS_DAY` is. Day 50 is
  "plausible, not exact".
- **Day zero** (the collapse day) **is Wednesday 19 February 2025** (Tom;
  canon). The run starts on Friday 21 February, and the grid fails on
  Wednesday 12 March.
- **Local time** is UTC−3, with no daylight saving (Daylight.md, Confirmed).
  The game clock is local time.
- **The water network** (Lima.md, Water):
  - It has no town tank. It's fed by electric wells, which stop with the
    grid (ENDEZA, primary).
  - Repressurising takes "como mínimo, duplica el tiempo de parada", at
    least twice the time the wells were stopped (ENDEZA, primary).
  - The network runs under paved streets only (Tom, first-hand).
- **Civil dawn and civil dusk at Lima** (USNO, 34.0447 S 59.1961 W, UTC−3;
  Daylight.md, Confirmed). January's rows are from 2026, the rest from 2025.
  On the same calendar date, any year differs by under a minute.

  | Date | Dawn | Dusk | | Date | Dawn | Dusk |
  |---|---|---|---|---|---|---|
  | 01-01 | 05:20 | 20:41 | | 07-01 | 07:35 | 18:26 |
  | 01-08 | 05:26 | 20:41 | | 07-08 | 07:35 | 18:29 |
  | 01-15 | 05:33 | 20:39 | | 07-15 | 07:33 | 18:33 |
  | 01-22 | 05:40 | 20:36 | | 07-22 | 07:29 | 18:37 |
  | 02-01 | 05:51 | 20:29 | | 08-01 | 07:23 | 18:44 |
  | 02-08 | 05:59 | 20:23 | | 08-08 | 07:17 | 18:48 |
  | 02-15 | 06:06 | 20:15 | | 08-15 | 07:10 | 18:53 |
  | 02-22 | 06:13 | 20:07 | | 08-22 | 07:02 | 18:58 |
  | 03-01 | 06:19 | 19:58 | | 09-01 | 06:50 | 19:04 |
  | 03-08 | 06:25 | 19:49 | | 09-08 | 06:40 | 19:09 |
  | 03-15 | 06:31 | 19:39 | | 09-15 | 06:31 | 19:14 |
  | 03-22 | 06:37 | 19:30 | | 09-22 | 06:21 | 19:18 |
  | 04-01 | 06:44 | 19:16 | | 10-01 | 06:08 | 19:25 |
  | 04-08 | 06:49 | 19:07 | | 10-08 | 05:59 | 19:30 |
  | 04-15 | 06:55 | 18:58 | | 10-15 | 05:49 | 19:36 |
  | 04-22 | 07:00 | 18:50 | | 10-22 | 05:40 | 19:43 |
  | 05-01 | 07:06 | 18:41 | | 11-01 | 05:29 | 19:52 |
  | 05-08 | 07:11 | 18:35 | | 11-08 | 05:22 | 19:59 |
  | 05-15 | 07:16 | 18:30 | | 11-15 | 05:17 | 20:06 |
  | 05-22 | 07:20 | 18:26 | | 11-22 | 05:13 | 20:14 |
  | 06-01 | 07:26 | 18:23 | | 12-01 | 05:10 | 20:22 |
  | 06-08 | 07:30 | 18:22 | | 12-08 | 05:09 | 20:29 |
  | 06-15 | 07:33 | 18:22 | | 12-15 | 05:11 | 20:34 |
  | 06-22 | 07:35 | 18:23 | | 12-22 | 05:13 | 20:38 |

  The code keeps a one-line pointer to `docs/canon/reference/Daylight.md`
  beside the table.

## Rules / mechanics

### Phase 1 — The calendar and darkness (#439)

- **`DAY_ZERO_DATE`**: 19 February 2025, a named constant in CONFIG /
  CONSTANTS beside the collapse clock. The collapse clock's minute 0 is
  `DAY_START_MIN` on that date.
- **The calendar of a minute** `m` since the collapse:
  - local minutes since day zero's midnight = `m + DAY_START_MIN`;
  - the date is `DAY_ZERO_DATE` plus `floor((m + DAY_START_MIN) /
    MINUTES_PER_DAY)` days, in the real calendar, leap days included;
  - the time of day is `(m + DAY_START_MIN) mod MINUTES_PER_DAY`.

  At the current minute, the time of day equals `minutesIntoDay()`. Write it
  so they can't disagree (one derives from the other, or both from one
  helper). Day 1 08:00 must come out as Friday 21 February 2025, 08:00.
  `POWER_FAILS_MIN` must come out as 12 March 2025, 22:00.
- **The daylight table** holds the rows above, by month and day. To find
  dawn and dusk on a date:
  - find the row on or before it and the next row, wrapping from 12-22 to
    the next year's 01-01;
  - interpolate linearly between them by the real number of days between
    the two dates in that calendar year. That puts 29 February between
    02-22 and 03-01 with no special case.

  A run longer than a year reuses the table by calendar date (Tom), never
  by a count of 365 days.
- **`isDark(m)`**: true when the time of day is before that date's civil
  dawn, or at or after its civil dusk. Pure, render-safe and never stored.
  It's the game's one darkness rule. #58's day and night builds on it later.
- No player-visible change in this phase alone.

### Phase 2 — Atucha at the gate and on the horizon (#344, #439)

**The gate's base text (#344)**, exactly as written, in place of today's:

> The road ends at the entrance to the Atucha complex, with wire fences on
> both sides. A guard post stands on an island between the lanes, cones in
> front of it, and nobody is in it. Past it, cars parked off to the left, and
> beyond them a grey dome over red-brick blocks.

It's fixed and true in every phase. Nothing in it changes with the plant.

**The plant's state**, derived from the clock and never stored:

- **`DIESELS_STOP_DAY = 50`**: days since the collapse, like
  `POWER_FAILS_DAY`. Retunable ("plausible, not exact").
- **`DIESELS_STOP_HOUR`**: see Design decisions below.
- **`DIESELS_STOP_MIN`** is derived the way `POWER_FAILS_MIN` is:
  `DIESELS_STOP_DAY * MINUTES_PER_DAY + (DIESELS_STOP_HOUR * 60 -
  DAY_START_MIN)`.
- **The plant's phase at minute `m`**:
  - `grid` while `gridUp(m)`. That includes the false recovery, a
    consequence of reading `gridUp()` (Tom), not a separate decision.
  - otherwise `diesels` while `m < DIESELS_STOP_MIN`;
  - otherwise `silent`.
- **The diesels stopping is not an event.** Nothing logs it and nothing is
  scheduled. The text simply reads differently from then on.

**At the gate**, the stop's text is the base text, a space, then the line
for the phase and the darkness (Tom's text):

| Phase | Dark | Line appended |
|---|---|---|
| `grid` | no | "Behind you, the switchyard hums inside its fence." |
| `grid` | yes | "Behind you, the switchyard hums inside its fence. Past the dome, the plant's lights are on." |
| `diesels` | no | "The switchyard is silent. Somewhere past the dome, engines are running." |
| `diesels` | yes | "The switchyard is silent. Somewhere past the dome, engines are running, and lights are on in some of the buildings." |
| `silent` | either | "The switchyard is silent, and nothing sounds from the plant." |

- Build it through the existing state-variant `desc`: a new `DESC_READERS`
  entry (for example `atucha`) with five states, and `atucha_gate`'s `desc`
  as `{ reads:{ kind:"atucha" }, variants:{ … } }`. Each variant is the full
  text: base text, space, line.
- The base text is written once and composed into the five variants. It's
  never repeated.
- The text runs four or five sentences, over the guideline. Tom accepted
  that.

**The horizon line (#439)**, Tom's text:

> Far to the north, over the fields, Atucha's lights are on. There are no
> others.

- It's shown **only while all of these hold**:
  - the player's current room is one of the horizon stops (below);
  - the plant's phase is `diesels`;
  - `isDark()` is true.

  It doesn't show while the grid is up: the horizon line starts with the
  grid's failure (Tom).
- **The horizon stops are town street stops only** (Tom, 2026-10-04): stops
  of kind `c` or `m`, never `rural`, `rail` or `station` ones, and never a
  room inside a building, a patio or a garden.
  - Which of them count as "near the north end" is a named, retunable rule:
    see Design decisions.
  - The set is computed once at world build, not per render.
- The line is data, beside `LIMA_STOP_TEXT`. Its predicate is a mechanic,
  and rendering only appends what the predicate allows.
- Nothing about it is stored, and it isn't an event: one night the lights
  simply aren't there.

### Phase 3 — The water network (#300)

**The mains lag the grid** (Tom, from ENDEZA):

- **`MAINS_REPRESSURE_FACTOR = 2`**, named and retunable, with a pointer to
  Lima.md (ENDEZA's "como mínimo, duplica").
- **The mains' up spans** are derived once from `GRID_UP_SPANS`, for example
  as `MAINS_UP_SPANS`:
  - For each grid span `[a, b)` in order, the outage before it is `a −` the
    previous span's `b`. The mains span is `[a + MAINS_REPRESSURE_FACTOR ×
    outage, b)`, dropped if empty.
  - The first span, which starts at `−Infinity`, has no outage before it, so
    the mains are up for all of it.
  - Spans must stay sorted and non-overlapping.
- **`mainsWaterUp(m)`** reads the mains' spans. With today's constants the
  mains are up until `POWER_FAILS_MIN` and never again: the false recovery
  (`GRID_RECOVERY_MIN` < 2 × `GRID_RECOVERY_AFTER_MIN`) brings back lights,
  not water. Don't special-case that. It falls out of the rule.
- **The mains' changes are settle points.** Every finite bound of the mains'
  spans is a scheduled change, just as `GRID_CHANGES` is.
  - At a mains change the world settles (`settleWorld()`), so the tanks
    settle to it. Nothing needs resolving: mains water powers nothing.
  - A mains change that falls on a grid change's minute is processed once at
    that minute.
  - Keep `tankRefillLph()`'s invariant: the rate never changes between two
    settles.
- **No save field.** As with the grid, the clock is enough. The scheduler's
  `lastGrid`-style marker for the mains is runtime only, rebuilt like
  `lastGrid` on load.

**Which homes fill from the network** (Tom):

- **A building's fill** is decided at world build from its site stop's
  links in `LIMA.links`:
  - **network** if any link touching the site stop is paved (`p`), including
    a site whose links differ (Tom, 2026-10-04);
  - **well** otherwise.

  Store it in `BUILDING_INFO` (for example `tankFill: "network" | "well"`)
  for every building with a tank. It's derived and never saved. Update
  `BUILDING_INFO`'s comment and `LIMA_LINKS`' comment ("only `r` is read
  today").
- **`NETWORK_FILL_LPH = 600`** (Tom): the rate network pressure fills a
  tank. A 1,000 L tank fills from empty in 100 minutes. Unconfirmed and
  retunable; #412 is the research issue that will replace it. Comment it
  so.
- **`tankRefillLph(b, m)`**, in full:

  | Fill | Wired with a pump | Rate |
  |---|---|---|
  | network | never (no pump; see below) | `NETWORK_FILL_LPH` whenever below full, while `mainsWaterUp(m)`. A float valve: no `TANK_FLOAT_START`, no latch, no power |
  | well | yes | the pump's `flowLph` while the pump is drawing (`powerNow`), **whether or not the mains run** |
  | well | no (unwired, today none: both `shop_home`s are paved) | `HOUSE_PUMP_FLOW_LPH` whenever below full, while `gridUp(m)`: the stand-in for a pump with power |

  A well pump's drawing is unchanged: its float, its latch, its power, as
  `powerSnapshot()` already decides.
- **A network-fed building has no pump.**
  - At world build, a wired building whose fill is `network` loses every
    fixture whose appliance has `flowLph`, whatever template its panel ends
    up with after the instance's overrides (`casa`, `casa_fuses`,
    `row_house`).
  - The other fixtures, circuits, their keys and so their load ids are
    unchanged. A well-fed wired building keeps its pump exactly as today.
  - The `WATER` circuit stays on every board, holding the water heater.
- **`TANK_PUMPS`** then holds only well buildings. Nothing else reads a
  missing pump as "unwired" any more: `tankRefillLph()` reads the building's
  fill first.
- **`validateWiring()`**:
  - a wired **network** building with a tank and any `flowLph` load is a
    problem;
  - a wired **well** building with a tank and no `flowLph` load, or two, is
    a problem;
  - a `flowLph` load with no tank stays a problem.
- **The row house's laundry text** drops the pump (Tom):

  > A washing machine and a deep sink. The back door opens onto the garden.

  Both row houses are paved, so the type's text changes. No casa's text
  names its pump, so no casa text changes.

**Old saves (PATCH):**

- `backfillPowerState()` drops every `switches` entry whose load id is not
  in `POWER_NET.loads`. That's where a paved home's old pump switch goes,
  and anything else stale. It stays idempotent.
- `breakers` are untouched: no circuit is removed.
- `state.tankDrawn` is untouched. A paved home's drawn tank refills at
  `NETWORK_FILL_LPH` while the mains run, and stays as it is after.

**The dev seam and the replay:**

- **`simulatePower()`** mirrors the game. A pump's tank refills while the
  pump draws, with no mains condition. Remove the `mains` option and its doc
  lines if nothing else reads them. It models no network tanks: it simulates
  power, and a network tank draws none.
- **The replay's step 6** can no longer draw the home's pump, since the home
  has none. See Design decisions. Whichever is chosen, the step's label and
  the replay comment say what it now exercises, and
  `REPLAY_TANK_MARGIN_L` goes if nothing reads it.

## Design decisions to make during implementation

Record each pick in the changelog.

1. **`DIESELS_STOP_HOUR`.** The canon gives only "about day 50".
   Recommended: **14** (mid-afternoon, so the first night after is the first
   without the lights). Any hour keeps PATCH. Retunable.
2. **Which town stops are "near the north end"** (`ATUCHA_HORIZON_…`, a
   named rule). Options:
   - (a) a line on the map: town stops with grid `y` at or above a named
     constant;
   - (b) a distance from the northernmost town stop.

   Recommended: (a), **y ≥ 1100**. At v0.13.0 that's 31 stops, the last two
   rows of blocks (the northern edge is y ≈ 1,196–1,278), across barrio,
   core and dirt stops. Retunable.
3. **Where the horizon line goes.** Options:
   - (a) appended to the stop's text in `renderLocationPanel()`, the way the
     fire note is;
   - (b) a line of its own under the text.

   Recommended: (a). Either way, the rule is a SIMULATION predicate and the
   text is WORLD DATA.
4. **How the daylight table is held.** Options:
   - (a) the rows as `"MM-DD HH:MM HH:MM"` lines, parsed once;
   - (b) an array of objects.

   Recommended: (a), matching how Lima's data blocks are held. It must match
   the rows above to the minute.
5. **How the calendar is computed.** Options:
   - (a) UTC `Date` arithmetic from `DAY_ZERO_DATE`'s year, month and day
     (never the machine's local time zone);
   - (b) a day count against a hand-built month table.

   Recommended: (a). Leap years must come out right either way.
6. **The replay's step 6.** Options:
   - (a) keep it at the home: draw the tank down, and let the step cover the
     network fill up to the failure and no refill through the false
     recovery;
   - (b) move it to a well casa near the home, so it still drives a pump
     through the failure.

   Recommended: **(a)**. The mains' lag is the riskiest new scheduling in
   the pass, and the home is on the replay's walk. If you take (a), file a
   `code-health` issue at the wrap for replay coverage of a well pump.
   Either way, the replay's digests change. That's expected; say so in the
   pull request.

## Data / schema changes

- **PLAYER STATE:** none. Nothing new is saved. `backfillPowerState()` drops
  switch entries for loads that no longer exist.
- **ROOM SCHEMA:** `desc` variants gain a reader kind (`DESC_READERS`).
  Document it beside `load` and `grid`.
- **BUILDING TYPES `water` schema comment:** the fill (network or well) and
  what each means. Pumps only on well buildings.
- **`BUILDING_INFO`:** gains the building's fill.
- **New constants:** `DAY_ZERO_DATE`, the daylight table, `DIESELS_STOP_DAY`,
  `DIESELS_STOP_HOUR`, `DIESELS_STOP_MIN`, the horizon-stop rule's constant,
  `MAINS_REPRESSURE_FACTOR`, `NETWORK_FILL_LPH`, and the mains' spans and
  changes (derived). Each with a one-line why. Each judgment call is marked
  retunable.

## Costs

- **Darkness and the plant's phase:** worked out when read, O(1). A lookup
  in a table of 48 rows only when something asks.
  - Per render: one check of the current room against the precomputed
    horizon set; the phase and `isDark()` only on a match.
  - At the gate: the `desc` reader runs once per render, as `grid`'s does.
  - Nothing per game minute, no event.
- **The mains:** the mains' changes join the scheduled changes. With today's
  constants there's one, at the grid's failure minute. Each is one
  `settleWorld()`, with no resolve.
- **Tanks:** unchanged in shape. A network tank refills by settling, like a
  pumped one, and its coming full is the existing `tankFullDue()` event.
  Paved homes no longer resolve a building when a draw moves a float, since
  they have no pump and no float. That's slightly less work.
- **Nothing checks the whole world every minute.**
- The Performance check should show no regression beyond noise. If it does,
  the pull request says what was measured.

## In scope

- [ ] Phase 1: `DAY_ZERO_DATE`, the calendar of a minute, the daylight
  table, `isDark()`. The `TIME_OF_DAY_BANDS` comment rewritten.
- [ ] Phase 2: #344's base text. The plant's phase and its constants. The
  gate's five variants through a new `DESC_READERS` kind. The horizon stops,
  rule and line.
- [ ] Phase 3: the mains' spans and changes as settle points.
  `mainsWaterUp()` on them. Network or well per building. Network-fed
  buildings lose their pump fixtures. `NETWORK_FILL_LPH`. The new
  `tankRefillLph()`. `validateWiring()`. The laundry text.
  `backfillPowerState()` drops stale switches. `simulatePower()` and the
  replay.
- [ ] Every comment the change makes stale, including ~6487 and ~7258
  (which name #300, closed by this pass), the collapse clock's comment
  (~570, "the town's pumps run on the grid…"), `HOUSE_TANK_L`'s and
  `HOUSE_PUMP_FLOW_LPH`'s, the `casa` wiring comment ("an electric pump
  lifts its water to the roof tank"), and `LIMA_LINKS`'.
- [ ] The systems docs (below).

## Explicitly out of scope

- **The road north** (#458): what Calle 111's rural stops show of the plant.
  No horizon line there in this pass.
- **Day and night beyond the darkness rule** (#58): no light levels, no
  changed stop text elsewhere, no vague-clock change.
- **The dead along the fence** (#12).
- **Showers and toilets** (#413), **potability** (#52).
- **Generators** (#245): a well pump can now run without the mains, but
  nothing powers it after the grid fails yet.
- **The network fill rate's source** (#412). The 600 L/h stays a judgment
  call.
- **The benchmark's forced GC** (#380) ships separately.
- **Radiation** (#351), **#285's site map**.

## Sections touched

- CONFIG / CONSTANTS: `DAY_ZERO_DATE`, the diesels' constants, the collapse
  clock's comment.
- WORLD DATA: `LIMA_STOP_TEXT.atucha_gate` and its variants, the horizon
  line, `LIMA_LINKS`' comment, BUILDING TYPES (the `water` schema comment,
  the row house's laundry text), `WIRING_TEMPLATES`' comments, the build of
  a building's wiring, `BUILDING_INFO`.
- SURVIVAL / TIME SIMULATION: the calendar, the daylight table, `isDark()`,
  the plant's phase, the horizon predicate, `mainsWaterUp()` and the mains'
  spans, `tankRefillLph()`, the scheduler (`planNextDue()`,
  `settleWorld()`). POWER: `TANK_PUMPS`, `validateWiring()`.
- PERSISTENCE: `backfillPowerState()`, `simulatePower()`, the replay.
- UI / RENDERING: `DESC_READERS`, `renderLocationPanel()`.

## Systems docs

Read first: `docs/systems/time.md`, `docs/systems/power.md`,
`docs/systems/fluids.md`.

Update in the same pull request:

- **`time.md`:**
  - the calendar (`DAY_ZERO_DATE`) and `isDark()`, as a worked-out-when-read
    rule;
  - the plant's phase, derived, with no event;
  - the mains' changes in the list of scheduled systems, and in the order
    at one minute;
  - the new constants in Constants.
- **`power.md`:**
  - Tanks: network or well, the network fill, the pump only on well
    buildings, the pump no longer gated by the mains;
  - `validateWiring()`'s tank rule;
  - the constants.
- **`fluids.md`:** check the sink's sentences on tanks and the mains. They
  should still hold (a tank while it holds water, else the mains). Change
  them only if they don't.

## UI changes

- **At the gate:** the new base text, plus one line that changes with the
  phase and with darkness.
- **At the town's north end, after dark, from the grid's failure to about
  day 50:** the horizon line after the stop's text.
- **In a paved home** (the player's, the neighbours', about half the
  casas): no water pump on the board or in the Electrical view. The tank
  refills more slowly (100 minutes from empty, was 25) while the mains run,
  and never after the grid fails, the false recovery included.
- **In an unpaved casa:** no visible change yet. The pump now refills the
  tank whenever it has power, not only while the mains run. But until
  generators exist (#245), it only has power while the grid is up, which is
  when the old mains gate was open too.
- **The row house's laundry** no longer names a pump.

## Dependencies / issue linkage

- Closes #344, #439, #300.
- Unblocks #458 (the road north) and #245's "a generator restores running
  water only on an unpaved street".
- At the wrap, file a `code-health` issue for replay coverage of a well
  pump if Design decision 6 takes (a), and anything else the pass defers.

## Open questions for Tom

None.
