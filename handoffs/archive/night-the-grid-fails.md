# Ashfall Handoff — The night the grid fails: a false recovery, and Atucha's siren

Current shipped version: v0.10.6
Implied version-change type: PATCH (no new persistent state: every event
  derives from the collapse clock, and an interrupted sleep stores nothing)
Issues: #347 — A false recovery; #352 — The siren on the night the grid fails

## What this is

The grid failure on day 21 stops being a silent boundary at 08:00 and becomes
a night. The grid goes at 22:00, the siren of the Atucha nuclear plant sounds
once over the town, and a couple of hours later the power comes back for a
few minutes and then fails for good. With this pass comes a general rule:
an event loud enough to wake a sleeper ends the player's sleep early. The
siren is the only such event so far.

From #347: *"Some hours later the power comes back — briefly — and then fails
for good. The lights come on, the fridge starts humming, and a few minutes
later it's over. Nothing explains it."* From #352: *"Atucha's public siren
sounds once over Lima … Nothing follows it: no second siren, no loudspeaker,
no radio. The game never says what it was."*

## Relevant existing state

Verified against `ashfall.html` at v0.10.6.

**The collapse clock** (CONFIG, around line 535):
- `START_DAYS_AFTER_COLLAPSE = 2`, `POWER_FAILS_DAY = 21`.
- `minutesSinceCollapse()` is `START_DAYS_AFTER_COLLAPSE * MINUTES_PER_DAY +
  state.totalMinutes`. The run opens at `DAY_START_MIN` (08:00) on Day 1, so
  minute 0 since the collapse is 08:00 on the collapse day.
- `gridUp(m)` is `m < POWER_FAILS_DAY * MINUTES_PER_DAY`. So today the grid
  fails at **08:00 on the player's Day 20**.
- `mainsWaterUp(m)` is `gridUp(m)`.
- `DAY_START_MIN` is declared much later than the CONFIG constants (in
  the clock helpers, beside `absoluteMinute()`).

**Readers of the grid**, all through `gridUp()` except one:
- `stepPower()`, `refreshPower()` and `loadPoweredNow()` pass `gridUp()` to
  `resolvePowerStep()` / `powerSnapshot()`.
- `containerPowered()` falls back to `gridUp()` for an unwired container.
- The device pop-up (`fed = … gridUp()` for a board), the dev `grid` reader,
  and the `"grid"` entry in DESC_READERS. No room uses the `"grid"` reader
  yet.
- `simulatePower()` defaults its `grid` and `mains` options to `gridUp(m)` and
  `mainsWaterUp(m)`.
- `refillTanks()` returns early unless `mainsWaterUp()`.
- **`effectiveAge()` is the exception**: it computes
  `POWER_FAILS_DAY * MINUTES_PER_DAY` itself and splits the interval at that
  one boundary (powered rate before, rate 1 after). It duplicates the grid's
  definition.

**Time loops.** Every loop advances in steps of at most 1 minute and calls
`applyWorldTicking(dt)` after adding `dt` to `state.totalMinutes`:
`runAwakeStep()` (used by `advanceTime()`, and so by walking), `doRest()` and
`doSleep()`. Those three are the only callers of `applyWorldTicking()`. So a
window of a few minutes in `gridUp(m)` is seen by every loop with no special
handling.

**Logging on power.** `stepPower()` calls `logTrips()`, which logs "The panel
on the wall snaps. A breaker has tripped." at the panel, or "Everything in
here goes quiet." where something the tripped breaker fed was running. Its
comment says: "The grid failing logs nothing: noticing it is deferred
(#220)." Rooms have no electric lights. The player notices the grid only
through wired loads (a fridge's readout, the pump).

**Sleep** (`doSleep()`):
- It cannot be interrupted. It computes `remaining = missingEnergy /
  SLEEP_ENERGY_RATE` from a Fatigue-derived `ceiling`, then loops in
  1-minute steps adding Energy.
- Afterwards it snaps Energy to the ceiling, sets `fatigue = 0`,
  `lastWakeMinute` and `lastExertionMinute`, and logs "You get real sleep.
  You wake up feeling considerably better."
- `sleepOffCooldown()` requires `SLEEP_COOLDOWN_MIN` (8 h) since
  `lastWakeMinute`. `sleepAvailable()` also requires Energy below
  `sleepEnergyCeiling()` (`100 - fatigue`).

**The map outside the town** (`LIMA_STOPS`, line format `id u v type kind
streets [flags]`; `readLimaData()` keeps each stop's `type`):
- Stop types are `core`, `gravel`, `dirt`, `barrio`, `station`, `rural` and
  `rail`.
- The `rural` stops are the road north to the plant: `r111_767m`,
  `r111_973m`, `r111_2752m`, `r111_papermill`, `r111_7180m`, `r111_7334m`,
  and `atucha_gate` at (-2957, 7845).
- The `rail` stops are `fcm_crossing_6km`, `fcm_crossing_11km` and
  `atucha_halt`, out to the west.
- Every other stop is in the town.
- A building's rooms share a floor Location at their site stop's
  coordinates (`registerBuildingLocations()`), and each building instance
  knows its `site`.
- Grid-frame metres: `r111_7180m` and `r111_7334m` are about 976 m and 839 m
  from the gate; the paper mill stop is about 3.3 km from it.

**Canon and reference facts this depends on** (quoted, so this session needn't
read them):
- The grid fails on day 21, **at about ten at night**. It fails in seconds,
  as on 16 June 2019, and "for Lima it is one event: the whole town at
  once". A false recovery follows "hours later": the sealed crews' attempt
  to restart. (`docs/canon/Ashfall_Canon.md`, "The grid".)
- The Atucha plant's surviving crew declare a Green Alert on losing every
  outside line, and **the siren sounded once over the dead town that
  night**; no one came, and nothing followed it. (Canon, "Atucha".) In the
  real emergency plan a first siren announces the Green Alert and a second
  the Red Alarm (`reference/Atucha.md`, "The drills"). The game never names
  the siren or the plan.
- **Atucha I's site is about 8 km north of Lima's centre** (OSM, in
  `reference/Lima.md`). How long the siren sounds is unconfirmed, so the
  text gives no duration.

## Rules / mechanics

All figures are Tom's decisions from planning (2026-09-30). All are
retunable; name them as such in the source.

### The night's timeline

The failure gains a time of day. Everything below is derived from the
collapse clock; nothing is stored.

| Event | Figure | Lands at (player's clock) |
|---|---|---|
| Grid fails | day 21 since the collapse, **22:00** | Day 20, 22:00 |
| Siren sounds | **20 min** after the failure | Day 20, 22:20 |
| Power returns | **150 min** after the failure | Day 21, 00:30 |
| Power fails for good | **5 min** after it returned | Day 21, 00:35 |

- **The failure's minute since the collapse** is `POWER_FAILS_DAY *
  MINUTES_PER_DAY + (22 × 60 − DAY_START_MIN)`. That's 21 days and 14 hours
  after minute 0, and it lands at 22:00 on the player's Day 20. Write it as
  that derivation, not as `31080`. `POWER_FAILS_DAY` stays 21.
- **The grid's up-time is one definition**, read by both `gridUp(m)` and
  `effectiveAge()`: up before the failure, and up again in the half-open
  window `[failure + 150, failure + 155)`, down everywhere else. In
  particular:
  - `effectiveAge()` stops computing `POWER_FAILS_DAY * MINUTES_PER_DAY`
    itself. The powered rate applies to the part of `[fromM, toM)` that
    overlaps the up spans, and rate 1 to the rest. The five minutes change
    spoilage negligibly; the point is one source of truth.
  - `mainsWaterUp()` keeps following `gridUp()`, so the mains water comes
    back for the five minutes too. Tank refilling follows on its own.
- **Recovery once, fixed.** No seed roll, no second flicker.
- When the power returns, loads with their switches on start as they
  would at any power-up. If several starting at once trips a breaker under
  the detailed rules, that's accepted: it's what `logTrips()` already
  reports. Don't suppress it.

### Noticing the grid: only through what's wired

The grid itself logs nothing. The player notices it through wired loads
(readouts change as they do today) and through one line in the room they're
in:

- **Down** (at the failure, and again when the recovery ends): if any load
  in the current room was drawing on the step before the grid went down,
  log **"Everything in here goes quiet."** That's the same text `logTrips()`
  uses for a quiet room. Make it one shared definition, not two literals.
- **Up** (when the recovery starts): if any load in the current room is
  drawing on the step the grid comes back, log **"Something in here starts
  up again."**
- One line per transition at most. Unwired containers (`containerPowered()`'s
  fallback) don't trigger either line. These lines log whether the player is
  awake or asleep, as trips already do, and neither one wakes a sleeper.

### The siren

It fires once, in the step whose interval contains its minute: the minute
since the collapse before the step is below it, and after the step it's at
or above it. `dt` can be fractional, so test the crossing, not equality. It
fires in every time loop, since all of them run `applyWorldTicking()`.

It's heard **everywhere** the player can be. The line depends on where the
player is, and on whether they're asleep:

| Where the player is | Awake | Asleep (it wakes them) |
|---|---|---|
| **In town**: a stop whose type isn't `rural` or `rail`, or a building room whose site is one | Far to the north, a siren starts up. It sounds for a while, then stops, and nothing follows it. | A siren wakes you. It's far to the north, and after a while it stops. Nothing follows it. |
| **Outside town**: a `rural` or `rail` stop, or a building room sited on one, not near the plant | Far off, a siren starts up. It sounds for a while, then stops, and nothing follows it. | A siren wakes you. It's far off, and after a while it stops. Nothing follows it. |
| **Near the plant**: a room whose Location is within **1000 m** of `atucha_gate`'s | Close by, a siren starts up. It sounds for a while, then stops, and nothing follows it. | A siren wakes you. It's close by, and after a while it stops. Nothing follows it. |

- "Near" takes precedence over "outside". With 1000 m it covers the gate,
  `r111_7334m` (839 m) and, only just, `r111_7180m` (976 m). The 1000 m figure
  is retunable; if a retune drops `r111_7180m` out of the band, it hears the
  "far off" line.
- A room whose stop can't be resolved counts as in town.
- The text is approved by Tom. Log it as the game's other events are
  logged; choose the log style by precedent.

### Waking: a general rule, the siren first

- **An event can be marked as waking.** When a waking event fires during a
  step of `doSleep()`'s loop, the sleep ends after that step. The siren is
  the only waking event in this pass. The mark belongs to the event's
  definition, never a check of which event it is (no name or id test in
  the sleep loop).
- A waking event picks its asleep line (above) when it fires during sleep,
  and its awake line otherwise. That includes `doRest()` and walking, which
  it doesn't interrupt.
- **An interrupted sleep:**
  - **Energy** keeps what the loop added. No snap to the ceiling: the snap
    is for a completed sleep.
  - **Fatigue** drops in proportion to the sleep taken:
    `fatigue × (1 − slept / planned)`. `planned` is the sleep's length as
    computed at its start, and `slept` the minutes actually slept. A
    completed sleep is the case `slept = planned`, which gives 0, as today.
  - **`lastWakeMinute` is not updated**, so no 8 h cooldown starts. Sleep is
    offered again at once, whenever `sleepAvailable()` otherwise holds.
  - `lastExertionMinute` is set to now, as a completed sleep sets it.
  - "You get real sleep…" is **not** logged. The waking event's own line is
    the record. `checkGameOver()` and `render()` still run.
- A completed sleep behaves exactly as today.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

- **Constant names and placement.** The hour of the failure, the siren's
  offset, the recovery's delay and length, and the 1000 m radius. The
  failure minute needs `DAY_START_MIN`, which is declared after the CONFIG
  constants, so derive it where both are in scope, or move
  `DAY_START_MIN` up. Don't compute it at the top of the script against a
  constant not yet declared.
- **How the grid's up-time is represented**, e.g. a list of `[start, end)`
  spans both readers use, or a helper returning the powered minutes in an
  interval. Either way it's defined once.
- **How a waking event reaches the sleep loop**, e.g. a runtime flag set when
  the event fires and read by `doSleep()`'s loop, with a runtime "asleep"
  flag the event reads to pick its line. Runtime only, never saved.
- **Where the siren's source point is defined**: recommended as one constant
  naming the `atucha_gate` stop, since the plant itself isn't a stop. Say
  where it lives.
- **How a room resolves to its stop** for the town/outside test: a stop
  room is its own; a building room goes through its building's `site`.

## Data / schema changes

- **State fields:** none. Nothing is saved.
- **Item schema:** none.
- **Room/stop schema:** none. The town/outside split reads the existing stop
  `type`. "Near" is a distance from one existing stop.

## In scope

- The failure moves to 22:00 on day 21 since the collapse (player's Day 20).
- The false recovery: power, and with it the mains water, back from
  failure + 150 to failure + 155 min, once.
- `effectiveAge()` reads the shared up-time definition.
- The two "noticing" lines on grid transitions, with the quiet-room line
  shared with `logTrips()`.
- The siren, with its six lines.
- Waking as a general property of an event; interrupted sleep as specified.
- Comments brought up to date: the collapse clock's comment block, the
  `logTrips()` comment ("The grid failing logs nothing…"), and the `doSleep()`
  comment (Fatigue clears fully only on a completed sleep).

## Explicitly out of scope

- **Interrupting anything but sleep.** Walking, resting and waits aren't
  interrupted (#212's interruptible waits).
- **Anything else waking the player.** The grid lines, trips and the recovery
  don't wake.
- **Outdoor signs**: the horizon's glow going out, Atucha's lights staying on
  (#285, #344). Rooms have no electric lights, and this pass adds none.
- **The gate's text** (#344) and **the iodine tablets** (#353).
- **The siren's own sound duration or pattern** (unconfirmed; #350).
- **The cycling-load readout** saying "Running" while idle (#337).
- **Mains gas** (#342): unaffected by the recovery.
- **Seeded variation** of any figure (#149).

## Sections touched

- **CONFIG / CONSTANTS**: the night's figures.
- **SURVIVAL / TIME SIMULATION**: the collapse clock (`gridUp()`,
  `mainsWaterUp()`), `effectiveAge()`, the POWER sub-block's `stepPower()` /
  `logTrips()` for the transition lines, and the siren's firing inside
  `applyWorldTicking()` or beside it.
- **ACTIONS**: `doSleep()`, for the interruption.

No WORLD DATA instances change. Check the ARCHITECTURE comment for the exact
section names.

## UI changes

- The approved lines above, in the log.
- The Sleep button reappears right after an interrupted sleep, with its
  estimate for what's left. That follows from `sleepAvailable()`; there's
  nothing new to render.

## Validation to perform

`git diff origin/main...HEAD -- ashfall.html`, plus, in the browser console
on a new game, setting `state.totalMinutes` just before each boundary and
advancing:
- `gridUp()` is true at failure − 1, false at failure, true at failure + 150,
  false at failure + 155.
- `getClockText()` at the failure reads "Day 20, 22:00".
- The siren logs once as the clock passes 22:20. A save loaded from before
  22:20 hears it again as its clock passes: it's derived, not stored.
- A sleep started at 22:00 ends at 22:20. Energy is partly restored, Fatigue
  is reduced by the proportion slept, and the Sleep button is offered at
  once.
- A sleep that doesn't cross 22:20 completes exactly as before.
- In a room with a running wired load: "Everything in here goes quiet." at
  22:00 and at 00:35, and "Something in here starts up again." at 00:30.
- `ashfallDev.simulatePower()` with `start` across the window shows the loads
  powered for those 5 minutes.
- The siren's line at a town stop, at `atucha_halt` and at `atucha_gate`.

## Dependencies / issue linkage

- Fulfils **#347** and **#352**; the pull request closes both.
- Part of the power hub, **#220**.
- Unblocks nothing; #344 and #353 are independent.
- Expected deferrals, to file at the wrap if they stay open: none known.
  Anything cut or surfaced goes to new issues as usual.

## Open questions for Tom

None. All settled in planning, 2026-09-30.

## After implementation

Open a pull request carrying the version bump (PATCH) and a new `CHANGELOG.md`
entry per `CHANGELOG_GUIDE.md` naming this handoff by path
(`Implements: handoffs/night-the-grid-fails.md`), recording the design
decisions above. Move this file to `handoffs/archive/` in the same pull
request. Its description carries `Closes #347` and `Closes #352`.
