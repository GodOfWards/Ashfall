# Time

ARCHITECTURE sections: SURVIVAL / TIME SIMULATION (the clock and the
scheduler, and the batteries beside them); FIRE / COOKING (the settles of
cooking, fires and stove timers); PERSISTENCE (the rebuild on new game,
restart and load, and the replay page).

## Purpose

Time passes only when the player acts, and an action can take anything from
a fraction of a minute to a night's sleep. This system moves the clock
through that time, and makes everything in the world that changes with time
come out as it would if the world had been watched every minute, without
watching it: nothing checks the whole world every minute.

## Model

**The clock.** Every advance of time (`advanceTime()`, `doRest()`,
`doSleep()`) moves the clock in steps of at most a minute, and each step is
`clockStep()`: the minutes are added to `state.totalMinutes`, Hunger and
Thirst fall (`applyHungerThirst()`), and whatever is due by then is
processed (`processDueEvents()`). The caller adds its own vitals piece after
the step (`recoveryStep()`, or sleep's Energy gain) and keeps its own stop
condition. The steps exist for the player's own vitals, whose rules read
state at minute resolution. The world does no work in a step unless
something is due.

**Worked out when read.** A system whose state changes smoothly over time
keeps the minute its state was true at, and brings it forward only when it
is asked for:

- food: a perishable row's `agedAt` (`docs/systems/spoilage.md`);
- batteries: a device's `durability.asOf` while it is on, its charge
  `batteryCharge()`;
- everything the scheduler owns (below): `settledAt`.

**Settling.** `settledAt` is the minute the scheduled systems stand at.
`settleWorld()` brings them to a minute `m`, each by the span since
`settledAt`, and does what is due at `m`. It is only ever asked for the next
due minute or for now, so a span never runs past an event nobody has
processed; `TICK_EPSILON` absorbs the float left over. Every advance of time
ends by settling to now (`settleToNow()`), which also settles every list the
player can reach (`settleReachable()`), so between two advances the world is
settled to the present, and every reader reads current state.

**The scheduled systems**, and the event each has:

- tanks refill (`settleTanks()`); event: a tank coming full
  (`tankFullDue()`), which resolves its building so its pump stops;
- the grid; event: each bound of `GRID_UP_SPANS`, a failure or a return
  (`resolveGrid()`, `docs/systems/power.md`);
- batteries; event: a device switched on running out (`batteryDeaths`,
  `settleBatteryDeaths()`);
- stove timers (`settleTimer()`); event: a timer running down, which rings;
- cooking, in every heat container of a lit room (`cookInHeat()`,
  `settleVessel()`); event: the soonest completion (`soonestIn()`): a raw row
  cooked, a dish cooked, water boiled;
- fires (`settleHeat()`); event: a fire going out;
- `CLOCK_EVENTS` (`fireClockEvents()`); event: its own minute.

**The next due minute.** `planNextDue()` takes the least of every system's
next event, from what is lit, running or refilling. It is planned at the
start of every advance, since an action may have changed anything since the
last one, and again after every processed event. It is never saved.

**Processing.** At the end of each step, while the next due minute is at or
before now, the world is settled to it and its clock events fired, and the
next due minute planned again. Events land on their exact minute, not at
the end of the step that crosses them, and several inside one step happen in
time order. A waking clock event sets `wokenUp`, which ends a sleep or a
blackout after that step.

**Order at one minute:** grid changes, tanks coming full, battery deaths,
stove timers, cooking, fires, clock events. Timers settle in world order,
then lit rooms in world order, each room's cooking before its fire.

**A vessel over a span** (`settleVessel()`): a dish forms first if the
contents and water already make one; otherwise tainted water boils, and
water that comes clean forms the dish it now makes and stops the span there,
so the dish cooks from the next one; then whatever the vessel holds cooks by
the span.

**The runtime lists.** The rooms whose heat is on (`heatRooms`) and the
stoves whose timer runs (`timerStoves`) are sets walked in world order
through an index built once per world (`roomOrder()`). `batteryDeaths` is a
list of minutes, dropped once due; a minute left behind by a device switched
off since finds nothing, and it is not keyed by item, since moving an item
strips its `_uid`. All three, `settledAt`, `lastClock` and `lastGrid` are
runtime only: `rebuildSchedule()` rebuilds them from one walk of the world,
and sets the clock marks to now, on a new game, restart and load.

**Batteries.** A device on batteries (durability mode "time") drains only
while it is on. Turning it on (`switchDevice()`) makes its charge true from
now and schedules its running out; turning it off writes the charge down.
Fresh batteries in a device that is on do the same as turning it on. At a
death, one walk of every item list switches off each on device whose charge
is out by then, and says so where the player can hear it.

## Invariants

- **Every writer of scheduled state registers.** A writer of `heatActive`
  calls `scheduleHeat()`, a writer of `timerMinutes` calls
  `scheduleTimer()`, and a device is switched on only through
  `switchDevice()` (or fresh batteries, which schedule their own death).
  A missed registration is an event that never fires; the replay page's
  consistency check (`replayProblems()`) compares the lists against a full
  scan after every step.
- **Between two advances, `settledAt` is now** and every reachable list is
  settled to now. An action that changes scheduled state does so at
  `settledAt`, so the next advance plans from it.
- **A settle never crosses an event.** It is asked only for the next due
  minute or for now, and every completion inside a span is an event.
- **Nothing scheduled is saved.** The saved fields are the systems' own
  (`timerMinutes`, `fireMinutesLeft`, `cookMinutes`, `boilMinutes`,
  `tankDrawn`, `agedAt`, `asOf`); the lists and marks are rebuilt on load.
- **A clock event fires once**: `lastClock` marks how far they have fired,
  and a load starts it at now, so a save from before one hears it again.

## Entry points

- `advanceTime()`, `doRest()`, `doSleep()`: the only ways time passes. Each
  plans the next due minute first and settles to now last.
- `clockStep()`: one step, for those three alone.
- `settleWorld()`: the world at a minute; `settleToNow()`: at now, with the
  reachable lists.
- `rebuildSchedule()`: after anything writes the world wholesale (new game,
  restart, load, the benchmark's setup).
- `scheduleHeat()`, `scheduleTimer()`, `switchDevice()`,
  `scheduleBatteryDeath()`: what a writer of scheduled state calls.
- `batteryCharge()`: a device's charge at a minute.

## Constants

- `TICK_EPSILON`: the float a completion is allowed to fall short by.
- `SCHEDULER_MAX_EVENTS_PER_STEP`: a guard against an event that never
  clears; hitting it is a bug, reported in the console.
- `CLOCK_EVENTS`, `GRID_UP_SPANS`: the fixed events on the collapse clock.
- `BOIL_MINUTES`: how long tainted water boils before it comes clean.

## Costs

- **Per step:** the vitals, and one comparison of now with the next due
  minute.
- **Per advance of time:** planning the next due minute over the lit rooms,
  the running timers, the refilling tanks, the battery minutes, the grid's
  changes and the clock events; settling to now; settling the lists the
  player can reach.
- **Per event:** a timer, cooking or a fire settles the lit rooms and running
  timers; a tank coming full or a power action resolves one building; a grid
  change resolves the busy buildings; a battery running out walks every item
  list once.
- **On a new game, restart and load:** one walk of the world to rebuild the
  lists and the battery minutes.

What remains proportional to the world is the load-time rebuild and one walk
per battery death.
