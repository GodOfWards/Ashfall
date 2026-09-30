# Ashfall Handoff — Event scheduler, power on events, and ageing worked out when read

Current shipped version: v0.10.11
Implied version-change type: MINOR (v0.11.0). #372 alone would be PATCH;
#369 and #373 change the saved shape.
Issue: #372 — Event scheduler — time jumps from event to event instead of
stepping every minute; with #369 — Electrical simulation: drop per-minute
resolving; and #373 — Food ageing and batteries worked out when read

## What this is

Every game minute, `applyWorldTicking()` walks the whole town four times,
and power is re-resolved for every building the player has touched. This
pass puts the game on principle 1 of `docs/02-code-practices.md`
(Performance): **nothing checks the whole world every minute**. The time
loop keeps stepping each minute for the player's own vitals, and does no
world work unless something is due. Everything else is either settled over
a span when needed, or fires as a scheduled event.

It lands in five phases, each its own commit (`Phase N: …`), pushed as it
is made:

1. **The replay page**: a dev page and a script that let the phases be
   compared. No behaviour change.
2. **The scheduler** (#372). No behaviour change beyond the two sub-minute
   points under Rules, Phase 2.
3. **Power on events** (#369). Intended behaviour changes.
4. **Food and batteries worked out when read** (#373). No behaviour change.
5. **Docs**: three systems docs, and the ARCHITECTURE comment.

## Relevant existing state

Verified against `ashfall.html` at v0.10.11.

**The loops.** Four loops advance time in steps of at most one minute, and
each step runs `applyHungerThirst(dt)` then `applyWorldTicking(dt)`:

- `runAwakeStep(min, untilWoken)`, then `recoveryStep(dt, "normal")`. It is
  called by `advanceTime(min)` for the action's minutes, and again for a
  collapse: the blackout (`COLLAPSE_BLACKOUT_MIN`, with `untilWoken`, as
  `asleep`) or the stumble (`COLLAPSE_STUMBLE_MIN`).
- `doRest()`, then `recoveryStep(dt, "rest")`.
- `doSleep()`, then its Energy gain. It stops after the step in which
  `wokenUp` is set.

**`applyWorldTicking(min)`**, in order: `stepPower(min)`,
`refillTanks(min)`, `ageFood(min)`, the battery drain (a
`forEachItemList()` walk), `tickStoveTimers(min)` (a walk over every
container of every room), then a walk over every room: for each room with
`heatActive`, `cookInHeat(r, min)` and then the fire burn-down
(`fireMinutesLeft -= min`; at ≤ 0 the heat goes off, with "The fire burns
down and goes out." if the player is there). Last, `fireClockEvents(min)`
(the siren, `CLOCK_EVENTS`, which may set `wokenUp`).

**Cooking.** `cookInHeat()` goes over every `heat`-tagged container in the
room. `cookItem()` adds `dt` to a raw row's `cookMinutes`, and at
`cookMinutesOf(it) − TICK_EPSILON` turns it Cooked, sets its `ages` to
zeros and remerges it. `cookVessel()` boils tainted water (`boilMinutes`,
`BOIL_MINUTES`), forms a dish if the contents now match a template
(`formDish()`, `ages = [0]`), then cooks whatever it holds. Nothing in
cooking logs. `soonestCooking(room)` already works out the soonest
completion in a room's heat container (a raw row, a dish, a dish that will
form, water boiling), but only for `getHeatContainer(room)`, not for every
heat container. `doWaitForCooking()` advances by exactly that remainder.

**Writers of the heat and timers.** `heatActive`: `doLightStove()`,
`doBuildFire()`, `doExtinguish()`, the burn-down, and the benchmark setup.
`fireMinutesLeft`: `doBuildFire()`, `doAddFuel()` (no time passes),
`doDismantleCampfire()`, and the burn-down. `timerMinutes`:
`doAddStoveTimer()`, `tickStoveTimers()`, and the benchmark. The ring logs
"You hear the ringing sound of the timer." if the player's room has the
stove's `buildingId`.

**Power.** `stepPower(dt)` runs `powerStep()` over the busy buildings
(POWER RUNS: an entry in `state.power`, a float that is not full, or
`untouchedTrippers()`), stores `state.power` and `powerNow`, then calls
`logGridChange(dt, before, after)` and `logTrips(trips)`.
`resolvePowerStep()` does an instant check (`momentary >
BREAKER_CURVES[curve].instant × rating`, breakers only, never fuses) and a
heat check (`power.heat`, rising by `dt ÷ tripMinutes()` or `dt ÷
fuseBlowMinutes()` while over the rating, draining by `dt ÷
HEAT_COOL_MIN`). `powerSnapshot()` makes a cycling load (`dutyCycle`,
`cycleMinutes`) draw only in the on part of its cycle, `((minute + phase)
mod cycleMinutes) < dutyCycle × cycleMinutes`, with `phase =
cycleRoll(seed, loadId) × cycleMinutes`. It makes a pump (`flowLph`) draw
while its float calls (below `TANK_FLOAT_START`, or latched on through
`prevDrawing` until full). `starting` is a motor load (`startWatts`)
drawing now that wasn't in `prevDrawing`. The actions `doSwitchBreaker()`,
`doSwitchLoad()`, `doResetBreaker()` and `doRewireFuse()` write
`state.power`, and the change shows from the next step. `loadLookNow()`
exists so a load's own readout shows a switch change at once.
`refreshPower()` resolves with no step and no starts (boot, restart, load).
`backfillPowerState()` shapes `state.power` as `{ switches, breakers, heat
}`. `validateWiring()` checks `tripMinutes(rating, BREAKER_F_NO_TRIP) ≥
BREAKER_NO_TRIP_MIN` and `fuseBlowMinutes(FUSE_F_NO_BLOW) ≥
FUSE_NO_BLOW_MIN`, and allows an `idle` readout word only on a load with
`dutyCycle` or `flowLph`. `ashfallDev.simulatePower()` steps a network per
minute and reports `heat` per row.

The appliances that matter here: `fridge_freezer` (100 W, `startWatts`
1300, `dutyCycle` 0.35 of 60 min, readout with no idle word);
`water_heater` (`WATER_HEATER_WATTS`, `dutyCycle` from
`WATER_HEATER_LOSS_KWH_DAY`, which works out to 0.05 of 120 min, about
100 W average, readout with idle word "Standing by"); `house_pump` (370 W,
`startWatts` 3300, `flowLph`, idle "Standing by").

**Tanks.** `state.tankDrawn[buildingId]` holds the litres drawn, with an
entry only while the tank is below full. `doFillAtSink()` adds to it.
`refillTanks(dt)` runs only while `mainsWaterUp()` (which is `gridUp()`).
A pumped tank (`TANK_PUMPS[b]`) refills at the pump's `flowLph` while
`powerNow` says the pump is drawing. An unpumped tank refills at
`HOUSE_PUMP_FLOW_LPH` while below full. Both go through
`refilledDrawn()`, rounded to the millilitre each step, and the entry is
deleted at 0.

**The grid.** `GRID_UP_SPANS` is a list of half-open spans of minutes since
the collapse. `gridUp(m)` and `gridUpMinutes(from, to)` read it.
`CLOCK_EVENTS` holds the siren at `POWER_FAILS_MIN +
SIREN_AFTER_FAIL_MIN`, which `wakes`.

**Food.** A perishable row keeps `ages`, one per unit, oldest first.
`ageFood(dt)` walks every list, grows each unit by
`spoilageRate(container, containerPowered(roomId, container)) × dt` (1 for
the floor and anything carried), and splits by freshness
(`splitByFreshness()`) and remerges changed rows. Nothing about freshness
is logged. `effectiveAge(container, roomId, from, to)` already works out
the age an untouched container gives over a span: the powered rate for
`gridUpMinutes()` when the load's untouched switch is on, 1 otherwise.
`stampAges()` / `stampMissingAges()` use it on a new game, on load, and on
a spawn roll (`doOpenContainer()`, the benchmark). The other writers of
`ages`: `asNewlyMade()` (an opened sealed unit, a caught fish),
`cookItem()`, `formDish()`, the crafted item in the crafting action, and
the 0.7 migrations (`rottenItem()`, the spoiled stew). The readers
(`unitFreshness()`, `rowFreshness()`, `sameStackState()`,
`leastLeftRow()`, `templateCandidates()`, `takeNearby()`, the crafted
item's age, the item labels) all read lists the player can reach:
`nearbyLists()` (`invPools()`, the current room's floor, its listed
containers), and render's lists for the current room and the inventory.
`unitsOf()` and `addToList()` deep-copy rows with JSON, which strips
`_uid` and copies every other field. `mergeRows()` concatenates `ages`.

**Batteries.** Only items with `durability.mode === "time"`: the
flashlight and the portable radio. The drain is `current −= drainRate ×
min` while `on`. At 0 the device turns off and logs "Your <name> runs out
of battery and shuts off." if carried, "The <name> …" if in the current
room, and nothing elsewhere. `batteryActions()` holds Turn on / Turn off
(`it.on = !it.on`, silent), Remove batteries (`on = false`) and Replace
batteries (`current = max`, leaves `on` as it was). `durabilityText()`
reads `current`. The benchmark switches radios on directly.

**The benchmark and the save refusal.** `benchMode` (`?bench`) runs
`runBenchmark()` after boot, and `doSaveLocal()` refuses to save on it.
`.github/scripts/perf_check.py` loads the page on the base and the head
commits in headless Chromium, from files written with `git show`.

## Rules / mechanics

### Phase 1 — The replay page

- **`ashfall.html?replay`** runs a fixed scenario after the boot's first
  paint, as `?bench` does, and leaves `window.ashfallReplayResult = {
  steps:[{ label, log, digest }] }`. `log` holds the lines the step added,
  in order. `digest` is a canonical JSON of the game state after the step:
  `state` plus every room's saved item lists, sorted keys. Its Save is
  refused, with the same guard as the benchmark's, extended to either page.
  Nothing is added to `ashfallDev`.
- **The scenario**, one labelled step per bullet, from a fixed seed
  (`REPLAY_SEED`), set up in code where play would be slow (giving items,
  setting the clock as the benchmark does):
  1. A new game. A walk of several street moves at Walk, so the clock
     goes fractional.
  2. At home: open the fridge and freezer (their spawn rolls), take a
     perishable, drop it on the floor.
  3. Raw fish in the stove, and a cooking pot with tainted water and a
     stew's ingredients. Light the stove, add a 10-minute timer, Wait for
     cooking until nothing is left cooking, then Rest.
  4. A campfire on a street stop, with a raw fish on it. Walk away and
     back, repeatedly, until the fire has burned out, so it goes out
     partway through a fractional move.
  5. Three radios switched on with a few minutes of charge: one carried,
     one on the current room's floor, one in another room. Advance 30
     minutes.
  6. Draw a building's tank below its float level. Set the clock to day
     `POWER_FAILS_DAY` shortly before `POWER_FAILS_HOUR`, with low
     Energy, and Sleep through the failure and the siren (which wakes).
     Then advance past the recovery and its end.
  7. A blackout: set Energy to 0 on the collapse count that blacks out,
     and advance one minute.
- **`.github/scripts/replay_compare.py`** takes two commits, loads each
  one's page in headless Chromium (written out with `git show`, as
  `perf_check.py` does), and reports every step whose `log` or `digest`
  differs, with the differing lines or keys. It exits 1 on any difference.
  It is run by hand, not in CI. Its docstring says what it is for.
- **A consistency check on the replay page only.** After each step, the
  page compares the scheduler's runtime lists (Phase 2 onward) against a
  full scan of the world, and fails the step if they disagree. That
  catches a writer that forgot to register.

### Phase 2 — The scheduler (#372)

**One clock.** A single function advances time by one step `dt` (≤ 1). It
adds `dt` to `state.totalMinutes`, runs `applyHungerThirst(dt)`, runs the
per-minute world work that is still per-minute in this phase
(`stepPower`, `refillTanks`, `ageFood`, the battery drain, in that order),
then **processes due events** (below). `runAwakeStep()`, `doRest()` and
`doSleep()` call it, and keep their own vitals piece after it
(`recoveryStep()` or the Energy gain) and their own stop conditions. At
the end of every advance (`advanceTime()` after any collapse, `doRest()`,
`doSleep()` on both its branches), the world is **settled** to now.

**Settling.** One runtime minute, `settledAt`, marks how far the
scheduled systems have been brought. Settling to minute `m` advances all
of them by `span = m − settledAt`, then sets `settledAt = m`. It is set to
now on a new game, restart and load. In this phase it covers:

- **Stove timers**, in world order: `timerMinutes −= span`. At ≤
  `TICK_EPSILON`: 0, and the ring as today.
- **Lit heat rooms**, in world order, each heat container of the room,
  each item in it:
  - a plain raw row: `cookItem(list, row, span)`, as today;
  - a vessel (`settleVessel`):
    1. If it holds no dish and a template is ready, form it (`formDish()`).
    2. If it still holds no dish and its water is tainted, add `span` to
       `boilMinutes`. If that reaches `BOIL_MINUTES − TICK_EPSILON`, the
       water turns clean; if a template is now ready, form it and stop
       here (the new dish cooks from the next span).
    3. Cook whatever it holds by `span`, as `cookVessel()` does today.
  - then the fire: `fireMinutesLeft −= span`. At ≤ `TICK_EPSILON` the heat
    goes off, `fireMinutesLeft = null`, and the line logs as today.

  All timers settle first, then all heat rooms, which is today's order.
  World order is `roomIds()` order.

A settle never runs past an unprocessed completion, because it only ever
settles to the next due minute or to now. `TICK_EPSILON` absorbs the
float left over, as it does today.

**The next due minute.** Each system reports its soonest event, in
minutes since the collapse, from what is lit or running:

- a timer: `settledAt + timerMinutes`;
- a heat room: `settledAt +` the least of its fire's `fireMinutesLeft`
  and the soonest cooking completion across **all** its heat containers.
  That is `soonestCooking()`'s rule (a raw row's `cookRemaining()`, a
  dish's, a dish that will form at its item's full `cooks.minutes`, water
  boiling at `BOIL_MINUTES − boilMinutes`), extended from
  `getHeatContainer()` to every heat container. Refactor
  `soonestCooking()` so both it and the scheduler use one function;
  `soonestCooking()` keeps its current answer;
- a `CLOCK_EVENTS` entry whose `at` hasn't been processed.

The loop caches the least of these. It is recomputed at the start of every
advance of time (an action may have changed anything since the last one)
and after every processed event. Nothing about it is saved.

**Processing due events**, at the end of each step: while the cached next
minute `m` ≤ now + `TICK_EPSILON`, settle to `m` (which performs the
completions and their lines), then fire every `CLOCK_EVENTS` entry with
`lastClock < at ≤ m`, set `lastClock = m`, and recompute. At the same
minute the order is: timers, cooking, fires, clock events. From Phase 3,
the grid and tank events come first (Phase 3 lists them). Clock events
keep their `line(roomId, asleep)` and `wakes` exactly as today.

**The runtime lists.** Rooms with `heatActive`, and stove containers with
`timerMinutes > 0`, are kept in two runtime lists in world order. They are
rebuilt by one scan on a new game, restart and load, and updated at every
writer listed under Relevant existing state, the benchmark setup
included. `tickStoveTimers()` and the heat loop leave
`applyWorldTicking()`, and `fireClockEvents()` is replaced by the clock
event processing above.

**Exact minute (decided, Tom).** Events land on their exact minute, not at
the end of the step that crosses it. Two consequences, both accepted:

- Food on a fire that goes out partway through a step cooks up to the
  minute the fire goes out, where today it gets the whole step. A dish
  that forms when its water finishes boiling starts cooking from that
  minute, where today it gets the whole step.
- Two events inside one step log in time order, not in
  `applyWorldTicking()`'s system order. The same minute keeps the order
  above.

Otherwise the same events happen at the same minutes, with the same lines.
A sleep or blackout still ends after the step whose event wakes it.

### Phase 3 — Power on events (#369)

Decided (Tom): electricity is a gameplay system, not a realistic one.

**No heat.** `state.power` becomes `{ switches, breakers }`. These go:
`power.heat`, `heatIn()`, `setHeatIn()`, the heat check,
`tripMinutes()`, `fuseBlowMinutes()`, `anchorMinutes()`, `bandMinutes()`,
`HEAT_COOL_MIN`, `BREAKER_F_LOW`, `BREAKER_F_HIGH`, `BREAKER_T_LOW_MIN`,
`BREAKER_T_HIGH_MIN`, `BREAKER_F_NO_TRIP`, `BREAKER_NO_TRIP_MIN`,
`FUSE_F_NO_BLOW`, `FUSE_NO_BLOW_MIN`, `FUSE_F_LOW`, `FUSE_T_LOW_MIN`,
`FUSE_F_HIGH`, `FUSE_T_HIGH_MIN`, and `validateWiring()`'s two
time-to-trip checks. `rewireFuseIn()` is a reset. `backfillPowerState()`
keeps `switches` and `breakers` only. `BREAKER_CURVES`,
`DEFAULT_BREAKER_CURVE`, `STANDARD_BREAKER_RATINGS`, `EDISON_FUSE_MAX_A`
and the rating checks stay.

**The resolve.** A pure `resolvePower(net, appliances, power, rules,
gridLive, minute, prevDrawing, seed, floats)` replaces `resolvePowerStep()`
and has no `dt`. Lowest layer first, looking again after every trip, as
today:

1. **Instant**: a closed breaker (not a fuse) that the rules consult, not
   an RCD or a cut-off switch, whose `momentary > instant × rating`, trips
   (cause `"instant"`).
2. **Overload**: a closed breaker or fuse that the rules consult, not an
   RCD or a cut-off switch, whose `running > rating`, trips (cause
   `"overload"`). A fuse's trip is its blowing, as today.

**Draw.** For current, and so for trips and meters:

- a cycling load (`dutyCycle`) draws `watts × dutyCycle` whenever it is
  powered;
- a pump draws `watts` while its float calls, as today;
- any other load draws `watts` while powered.

`running` sums the loads' draw. `momentary` counts a starting load at its
`startWatts`, as today.

**Starts (decided, Tom).** A motor load (`startWatts`) starts when it is
drawing in this resolve and was not in the previous resolve of its
building (`prevDrawing`). That happens when it is switched on, when its
circuit comes live (a reset, a rewire, the grid returning), or when its
float calls. With no previous resolve (`refreshPower()`: boot, restart,
load) nothing starts, as today. A cycling load no longer starts on each
cycle.

**What the player sees drawing (decided, Tom).** The readouts and the
room lines keep today's cycle. A second, presentation-only predicate
answers "is it running at minute m", worked out when read: for a cycling
load, powered and in the on part of its cycle, by today's phase formula
at `m`; for a pump, its float calling; for anything else, powered. It
serves `loadStatusText()`'s idle word and `logGridChange()`'s
`drewHere`, evaluated at the minute before the grid change and at it. It
never feeds current or trips. `dutyCycle` and `cycleMinutes` stay in
APPLIANCES for it, and the validator's idle-word rule is unchanged.

**When power resolves.** Only here. The per-minute `stepPower()` goes.

- **An action** that changes `state.power` (`doSwitchBreaker()`,
  `doSwitchLoad()`, `doResetBreaker()`, `doRewireFuse()`) resolves that
  building at once, logs its trips at once (`logTrips()`, same wording),
  and updates `powerNow`. `isPowered()` and spoilage see it at once, not
  from the next step. `loadLookNow()` may then collapse into a read of
  `powerNow` (implementation choice).
- **A water draw** (`doFillAtSink()`) that changes a pumped tank's float
  resolves that building at once.
- **Grid events**: every boundary of `GRID_UP_SPANS` is a scheduled event.
  At it, settle to that minute, then resolve the busy buildings and
  `untouchedTrippers()` with the new `gridUp()`, then `logGridChange()`
  and `logTrips()`. `untouchedTrippers()` sums draw by the rule above,
  with `max(draw, startWatts)` for its momentary superset.
- **Tank full**: see Tanks.

**Tanks.** `refillTanks()` leaves the per-minute tick and becomes part of
the settle. Over a span, a tank in `state.tankDrawn` refills if the mains
are up and it is unpumped, or its pump is drawing in `powerNow`. Neither
condition changes inside a span, because grid events and resolves are
settle points. Refill is `drawn − flowLph ÷ 60 × span`, rounded to the
millilitre once per settle, and the entry is deleted at 0. Its event,
"tank full", is at `settledAt + drawn ÷ (flowLph ÷ 60)` for each tank
refilling. At it, delete the entry, then resolve a pumped tank's building
so the pump stops and its latch clears. `tankLeft()`, `waterRunningIn()`
and `tankFloatsNow()` read `state.tankDrawn`, which is settled at every
advance's end.

**Order at one minute**, now complete: grid events, tank full, (Phase 4:
battery deaths,) stove timers, cooking, fires, clock events.

**`ashfallDev.simulatePower()`** keeps its signature, less `heat`:
options' `power` has no `heat`, and rows have no `heat`. It resolves each
minute with `resolvePower()`, refilling its tanks per minute as today. It
is a dev tool, so per-minute there is fine.

**Behaviour changes (all accepted in #369):**

- trips happen on the action or event that causes them, with unchanged
  wording;
- an overload above the rating trips at once;
- the water heater, at about 100 W average, effectively stops causing
  trips;
- the fridge no longer surges on each cycle;
- the clamp reads a cycling load's average (the fridge about 0.16 A,
  steady);
- a switch change is seen by spoilage at once.

### Phase 4 — Food and batteries worked out when read (#373)

**Food: `agedAt`.** A perishable row gains `agedAt`: the minute since the
collapse at which its `ages` are true. Every writer of `ages` sets it:
`stampAges()` (to now, and also for a row that has `ages` but no
`agedAt`), `asNewlyMade()`, `cookItem()` and `formDish()` (the settle's
minute), the crafted item, and the migrations. A row read with no
`agedAt` is treated as settled now.

**The age gained over a span**, `ageOver(container, roomId, from, to)`:

- carried, on the floor, or in a container that is neither `fridge` nor
  `freezer`: `to − from`;
- in a fridge or freezer: if its load's switch is on and its path is
  closed as the power state stands, with the grid taken as up
  (`powerSnapshot()` with `gridLive` true on its building: pure, no
  trips), or it is unwired (the grid feeds it), then
  `up = gridUpMinutes(from, to)`, and the gain is
  `spoilageRate(c, true) × up + spoilageRate(c, false) × (to − from − up)`.
  Otherwise, `spoilageRate(c, false) × (to − from)`.

`effectiveAge()` stays for stamping (it reads the untouched switch).

**Settling a list** to minute `m`: for each perishable row, `ages += ageOver(…,
row.agedAt, m)` per unit, `agedAt = m`, then split by freshness and
remerge changed rows, exactly as `ageFood()`'s body does. `ageFood()` and
its per-minute call go. A list is settled:

1. **Where the player can reach it**: at the end of every advance of time,
   after every room change (`doMove()`, so every step of Walk to…), and
   after a new game, restart or load. That covers `invPools()`, the
   current room's floor, all its containers and car containers, and all
   nested `contents`.
2. **Before a power change reaches it**: before a resolve changes a
   building's switches or breakers (an action, or a trip a resolve finds),
   settle that building's wired fridge and freezer containers to that
   minute, under the power state as it stood. The resolve is pure, so
   compute it, settle, then commit. Grid changes need no settle, since
   `ageOver()` integrates the grid.
3. **Before an event changes it**: at a cooking completion, settle the
   heat container's list (nested contents included) to that minute before
   `cookItem()` or `formDish()` touches it.

Anything that moves or merges rows acts on lists that are already settled
(rule 1), so `mergeRows()` always joins rows settled to the same minute.
Say so in its comment. No food events exist: freshness changes log
nothing, and a row in an unreached list goes "mixed" silently until it is
next settled.

**Batteries: `durability.asOf`.** It is present exactly while a
time-mode device is `on`. `batteryCharge(it)` returns `current` when off,
and `max(0, current − drainRate × (now − asOf))` when on.
`durabilityText()` reads it. The drain in `applyWorldTicking()` goes.

- **Turn on**: `asOf = now`, and schedule its death.
- **Turn off**: `current = batteryCharge(it)`, delete `asOf`.
- **Remove batteries**: as Turn off, then as today.
- **Replace batteries**: `current = max`, and if on, `asOf = now` and
  schedule its death.

**Battery deaths** are scheduled events. A runtime list of minutes
(`asOf + current ÷ drainRate`) is added to on every scheduling, and
rebuilt by one walk on a new game, restart and load. At a due minute `m`,
one `forEachItemList()` walk switches off every on time-mode device whose
`batteryCharge()` at `m` is ≤ `TICK_EPSILON`: `current = 0`, `on =
false`, delete `asOf`, with today's lines by `roomId`. Then the minutes ≤
`m` are dropped from the list. A minute left behind by a device switched
off earlier finds nothing. The list isn't keyed by `_uid`, since moving
an item strips it. A device switched on with no charge dies at the next
step, as today. The benchmark's radios go through Turn on's path.

**After Phase 4**, a step's world work is only processing due events.
`applyWorldTicking()` goes or shrinks to that.

## Design decisions to make during implementation

Record each pick in the changelog entry.

- **Names**: the clock function, the settle function, `settledAt`,
  `ageOver()`, the presentation "running" predicate, `resolvePower()`.
  Recommended: names that say what they do, in the file's style.
- **The runtime lists' shape**: arrays kept in world order, or sets
  iterated in world order through a room-index map built per world.
  Recommended: the index map, since inserting needs no sort.
- **`loadLookNow()`**: keep it, or collapse it into reads of `powerNow`
  now that actions resolve at once. Recommended: collapse it, if every
  caller's answer stays the same.
- **The replay scenario's concrete rooms and items**, within the steps
  given. Choose ones the seed makes reliable, and name them in constants
  beside `REPLAY_SEED`.

## Data / schema changes

- **PLAYER STATE**: `state.power` loses `heat` and becomes `{ switches,
  breakers }`. The schema comment is updated.
- **ITEM DATA SCHEMA**: a perishable row's instance field `agedAt`
  (minutes since the collapse; its `ages` are true then). A time-mode
  `durability` gains `asOf`, present exactly while the device is on. Both
  are documented beside `ages` and `durability`.
- **Nothing for the scheduler.** Its lists, `settledAt`, the next due
  minute and the battery minutes are runtime only, rebuilt on load.
- `GAME_CONFIG.VERSION` becomes `0.11.0`, which rotates `SAVE_KEY`
  through `versionCompat()`. No save migration is written.

## Costs

| | Today | After |
|---|---|---|
| Per game minute | 4 whole-town scans, plus power for every busy building | The vitals, and one comparison with the next due minute |
| Per advance of time (any action) | — | Settle: the lit rooms, running timers, refilling tanks, and the reachable lists. Recompute the next due minute over those, the clock events and the grid spans. |
| Per event | — | A timer, cooking or fire: that room. Grid change: resolve the busy buildings and the untouched trippers (~25–40 µs each, #369's figures). Tank full or a power action: resolve one building. Battery death: one `forEachItemList()` walk. |
| On load, restart, new game | a stamping walk | the same walk, plus rebuilding the runtime lists |

Nothing walks the whole world per minute or per action. What remains
proportional to the world is load-time rebuilding and one walk per
battery death. The benchmark's 8-hour sleep should fall from about 3.8 s
toward its 200 ms budget. Report the Performance job's numbers in the pull
request, and don't change the budgets (#376).

## In scope

- [ ] Phase 1: `?replay`, its scenario and consistency check, the save
      guard, `replay_compare.py`.
- [ ] Phase 2: one clock; settling; the next due minute; the runtime
      lists; timers, cooking, fire and clock events on the scheduler.
      `replay_compare.py` Phase 1 → Phase 2: differences only of the two
      exact-minute kinds, each one explained in the pull request.
- [ ] Phase 3: heat gone; `resolvePower()`; averaged draw; starts at start
      events; the presentation predicate; resolve on actions, water draws,
      grid events and tank full; tanks settled; `simulatePower()`
      updated; the validator's time checks gone. `replay_compare.py`
      Phase 2 → Phase 3: differences only in `state.power.heat`, and any
      trip timing, explained.
- [ ] Phase 4: `agedAt`, `ageOver()`, the three settle triggers;
      `durability.asOf`, `batteryCharge()`, battery deaths as events;
      `ageFood()` and the drain gone. `replay_compare.py` Phase 3 →
      Phase 4: identical once the digest settles every list (on the
      replay page only) and ignores `agedAt` and `asOf`, with ages
      compared to 1e-6.
- [ ] Phase 5: the systems docs and the ARCHITECTURE comment.
- [ ] The wrap, per `docs/03-workflow.md`: v0.11.0, the changelog entry,
      this handoff archived, `Closes #372`, `Closes #369`, `Closes #373`,
      and the three `replay_compare.py` results in the pull request.

## Explicitly out of scope

- Making the Performance budgets fail (#376). It follows once the timings
  are under budget.
- Over-fusing a tapón (#365). With no heat, its wiring's overheating needs
  a new, event-driven model of its own.
- Temperature, and a fridge that coasts on its cold (#217).
- Generators and other power sources (#245). The systems docs must say
  that a new source changes `ageOver()`'s rule, "only the grid changes
  power over a span".
- Anything that makes a wait interruptible (#212).
- Retuning any value. Every constant keeps its value, apart from those
  removed.

## Sections touched

- CONFIG / CONSTANTS: the heat constants go.
- WORLD DATA: the ITEM DATA and POWER SCHEMA comments, and APPLIANCES'
  comment on draw.
- PLAYER STATE: `state.power`.
- INVENTORY / ITEM SYSTEM: `batteryActions()`, and the comment on
  `mergeRows()`.
- WORLD INTERACTION: `doMove()`'s settle, the power actions,
  `doFillAtSink()`.
- SURVIVAL / TIME SIMULATION, with POWER and STAMINA / FATIGUE: the loops,
  the scheduler, the resolve, spoilage.
- FIRE / COOKING: the settle of cooking, the fire and timers;
  `soonestCooking()`.
- PERSISTENCE: `backfillPowerState()`, load and restart rebuilding the
  runtime lists, `simulatePower()`, the replay page, the benchmark setup.
- RENDERING: `durabilityText()`, `loadStatusText()`.
- The ARCHITECTURE comment: SIMULATION's paragraph (`resolvePowerStep()`
  goes; name the clock and the scheduler) and MECHANICS PASS's
  survival/time pointer.

## Systems docs

None exist yet to read. This pass writes three, per `docs/systems/README.md`'s
format, and updates that README's index (Power is no longer overdue;
Survival still is):

- **`docs/systems/time.md`** (new): the clock, settling, the next due
  minute, the runtime lists, event order at one minute, the rule that
  every writer of scheduled state registers, the settle points, and
  batteries.
- **`docs/systems/power.md`** (new): the network, the resolve, draw and
  starts, the presentation predicate, when power resolves, tanks, and
  POWER RUNS. The POWER overview comments move here, leaving one-line
  pointers.
- **`docs/systems/spoilage.md`** (new): ages, `agedAt`, `ageOver()` and
  its grid-only rule, the three settle triggers, and freshness. The
  SPOILAGE comment moves here.

## UI changes

- A trip's line appears with the action that causes it.
- The clamp meter reads a cycling load's average.
- The water heater's readout still alternates between "Running" and
  "Standing by".

No new controls or wording.

## Dependencies / issue linkage

- Closes #372, #369 and #373.
- Unblocks #376, which is left untouched.
- #365 has already been updated for the loss of heat.
- Expected deferrals: none. If the replay shows a difference none of the
  rules above predicts, stop and ask Tom rather than accept it.

## Open questions for Tom

None.
