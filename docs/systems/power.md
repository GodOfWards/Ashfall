# Power

ARCHITECTURE sections: SURVIVAL / TIME SIMULATION, its POWER sub-section (the
network's expansion, the resolve, the game's reads of it, the stop rules and
KETTLES); WORLD DATA (POWER SCHEMA: `APPLIANCES`, `WIRING_TEMPLATES`, `WIRING`,
`GAME_WIRING`, and BUILDING TYPES' `wiring` and `water`); PLAYER STATE
(`state.power`, `state.tankDrawn`); WORLD INTERACTION (the power actions, the
kettle's switch, the meters); INVENTORY / ITEM SYSTEM (the sink's draw on a
tank, `drawFromTank()`; the kettle's pop-up actions, and a running kettle
lifted); RENDERING (the device pop-up, the Electrical view and the
microwave's dial, the readouts).

## Purpose

The town's electricity: a grid that fails, boards and panels of breakers and
fuses, and the appliances behind them. It decides what has power, which is
what keeps a fridge cold, lights a stove by itself and fills a house's tank,
and it gives the player breakers to trip and reset. Electricity is a
gameplay system, not a realistic one.

## Model

**The network.** Sources (the grid, today the only one), distribution (a
building's board, each unit's panel, branch circuits, each behind a breaker
or a fuse) and loads (fixtures and appliances). Its definitions are world
data, expanded once at startup into a flat table of nodes with stable ids
(`expandWiring()`, POWER SCHEMA in the code); what changes in play is
`state.power`, only what differs from the default: a load's own switch, a
breaker's handle and whether it has tripped. The rest of the game asks it
one question, `isPowered()`.

**A look** (`powerSnapshot()`) is a pure function of a network, a power
state, the electrical rules, whether the grid is live, the previous
resolve's drawing, the seed, each tank's float (`tankFloat()`) and how many
items run through each plug load (`plugsNow()`). It works
out, lowest layer first (`BREAKER_LAYERS`), what is live, what each load's
switch and path give it (powered), what draws, what starts, and the current
through every breaker. Simplified rules skip feeders and circuits, but never
a fuse (`consultsBreaker()`, `circuitSkipped()`).

**Draw.** A cycling load (`dutyCycle`) draws its average, watts ×
`dutyCycle`, whenever it has power (`loadDrawWatts()`). A pump (`flowLph`)
draws while its tank's float calls: the tank below `TANK_FLOAT_START`, or the
pump drawing in the previous resolve and the tank not yet full; never on a
full tank. A plug load draws its watts times the items running through it,
while there are any. Any other load draws its watts while it has power. A breaker's
running current is its loads' draw over its volts; its momentary current
counts a starting load at its `startWatts`.

**Starts.** A motor load (`startWatts`) starts when it draws in a resolve and
did not in its building's previous one: switched on, its circuit come live (a
reset, a rewire, the grid returning), or its float calling. With no previous
resolve (`refreshPower()`: boot, restart, load) nothing starts. A cycling
load does not start on each cycle.

**The resolve** (`resolvePower()`) is pure and has no time in it. Lowest
layer first, looking again after every layer's trips:

1. **Instant:** a closed breaker (never a fuse) the rules consult, not an RCD
   or a cut-off switch, whose momentary current is over its curve's
   `instant` multiple of its rating (`BREAKER_CURVES`) trips.
2. **Overload:** a closed breaker or fuse the rules consult, not an RCD or a
   cut-off switch, whose running current is over its rating trips. A fuse's
   trip is its blowing.

It returns the look after its trips, the new power state and the trips, each
with the loads its breaker fed that were drawing.

**When power resolves.** Only when something changes it:

- **An action** on a building's switches or breakers (`doSwitchBreaker()`,
  `doSwitchLoad()`, `doResetBreaker()`, `doRewireFuse()`) makes its change on
  a copy, resolves that building on it, and commits the result
  (`changePower()`): its trips happen, and are heard, with the action.
- **A water draw** (`doFillAtSink()`, `doDrinkAtSink()`, through
  `drawFromTank()`) that moves a pumped tank's float resolves its building at
  once, so its pump starts or stops calling.
- **A tank coming full** is a scheduled event (`docs/systems/time.md`): its
  building resolves, so the pump stops and its latch clears.
- **An appliance's timed stop and a kettle switching on, off or cutting out**
  resolve its building, at their minute (below).
- **The grid failing or returning**, at every bound of `GRID_UP_SPANS`, is a
  scheduled event (`resolveGrid()`): the world is settled to that minute,
  then every busy building resolves at the grid's new state, then the
  player hears what changed (`logGridChange()`, `logTrips()`).

**POWER RUNS.** Buildings share nothing but the grid, so each resolves on its
own, and one nobody has touched needs no resolving at all: with no entry in
the power state, its breakers closed, its switches at their rolled defaults
(`switchOnIn()`), its tank full and nothing running through its plugs, its
look is a pure function of the seed, the rules and the grid (`stillLook()`).
A building is busy when it has an entry in the power state (a switch, a
breaker or a stop), a float that is not full, a plug with an item running
through it, or default-on loads that could overload one of its breakers
(`untouchedTrippers()`, which sums a superset of what can draw; a plug load,
having nothing running, draws nothing there). `powerNow` holds the grid's state and, per
building, the look its last resolve left; every other building is still,
and its values are worked out when read (`powerRead()`). Nothing is
approximated: a still building's look is exactly what a resolve would give
it. A result is never changed once made, so the one before a grid change
stays readable.

**What the player sees running** (`loadRunningAt()`) is presentation only,
and never feeds current or trips: a cycling load runs while it has power and
is in the on part of its cycle, its phase fixed per load by a keyed roll
(`cycleRoll()`) so the kitchens don't all cycle together; a pump while it
draws; anything else while it has power. It serves a readout's idle word
(`loadStatusText()`) and the grid's lines, taken at the minute before the
change and at it.

**Tanks.** A building with a tank (BUILDING TYPES' `water`) runs its sinks
while the tank holds water (`waterRunningIn()`); `state.tankDrawn` holds the
litres drawn, with an entry only while below full. While the mains run
(`mainsWaterUp()`), a tank refills at its pump's `flowLph` while that pump
draws, or, in a building with no pump load (the unwired fallback), at
`HOUSE_PUMP_FLOW_LPH` whenever it is below full (`tankRefillLph()`). Refilling
is settled, not ticked (`settleTanks()`), rounded to the millilitre once per
settle; neither condition changes inside a span, since grid changes and
resolves are settle points.

**The meters** read the network as it stands (`loadSupplyVolts()`,
`breakerLoadSideVolts()`, `breakerCurrent()`): a cycling load reads its
average draw.

**Stop rules.** An appliance with `stops` (POWER SCHEMA) switches itself off.
A timed one (the toaster's `TOASTER_RUN_MIN`, the microwave's dial, picked
from `MICROWAVE_MINUTE_CHOICES` in the Electrical view) records when it stops
on switching on (`doSwitchLoad()`): `state.power.stops`, `{ at }` while it
runs and `{ left }` while it waits for power. The stop is a scheduled event
(`settleApplianceStops()`): its switch goes off, its entry goes, its building
resolves, and its line is heard in its room. After every resolve of a
building (`changePower()`, `resolveGrid()`, `refreshPower()`), its stops are
set against the look the resolve left (`applyStopRules()`): one left
unpowered whose rule is "off" switches off (the toaster pops, heard in its
room), one whose rule is "pause" keeps its time left, and a paused one with
power again runs on from then. A load switched off that isn't drawing
changes nothing a look shows, so the rule needs no resolve of its own.
Switched on without power at its socket, an "off" appliance doesn't latch,
and says so; a "pause" one switches on and waits.

**Plugs and the electric kettle** (KETTLES). A socket circuit (a template
circuit's `sockets`) gives every room it serves a plug load, the first such
circuit in panel order taking it, of `PLUG_APPLIANCE`, with no switch and no
fixture: the Electrical view lists none (`expandWiring()`). An item with an
`appliance` (the electric kettle) is plugged in while it lies on the floor of
such a room (`plugFor()`), and while it runs (`on`) it draws through that
room's plug, so its circuit and every breaker upstream carry it, and it can
trip them; a trip or the grid going down is heard and noticed in its room as
any load's is. It heats its water at its appliance's watts ×
`KETTLE_EFFICIENCY` and cuts out at the boil, at once when empty, a scheduled
event ([Time](time.md)). Running means powered: a resolve that leaves its plug
unpowered switches it off, silently, and it is off when power returns
(`applyStopRules()`). Lifted off its floor, it switches off first; poured or
drunk empty, it cuts out with its line. The running kettles are a runtime
list, rebuilt from the room floors by `refreshPower()` before its resolves.

## Invariants

- **Every change to `state.power` in play goes through a resolve**:
  `changePower()` for an action or a float, `resolveGrid()` and
  `refreshPower()` for the rest. A write that skipped it would leave
  `powerNow` stale; the replay page's check (`replayProblems()`) finds a busy
  building no resolve has looked at.
- **Before a building's switches or breakers change, its fridges and freezers
  are settled** under the power state as it stood (`adoptPower()`,
  `docs/systems/spoilage.md`).
- **Only the grid changes power over a span.** Every other change happens at
  a settle point: an appliance's stop and a kettle's cut-out are scheduled
  events, each a settle point. A new source of power (#245) breaks this, and
  with it spoilage's rule for a span.
- **A running kettle has power**: every resolve applies the stop rules, which
  switch off a kettle whose plug it left unpowered.
- **Only a load with a timed stop rule, switched on, has a stop entry**, and
  one that runs has power while one that waits has none (`replayProblems()`
  checks both).
- **A still building is never stored.** Its look is always derived from its
  own nodes, so a building wired after a run started needs nothing written.
- **Starts need a previous resolve.** Nothing starts on boot, restart or
  load.

## Entry points

- `isPowered()`: whether a load has power now; spoilage, the stove and the
  room descriptions read it.
- `loadRunningNow()`: whether a load is running, for its readout.
- `changePower()`, `resolveBuilding()`: an action's or an event's resolve of
  one building, its stop rules applied after (`applyStopRules()`).
- `doSwitchLoad()`, `doSwitchKettle()`: a fixture's switch and the kettle's.
- `plugFor()`, `plugsNow()`: whether an item is plugged in, and what runs
  through the plugs.
- `resolveGrid()`: a grid change, from the scheduler.
- `refreshPower()`: the network rebuilt on boot, restart and load.
- `simulatePower()`: the dev seam's test network, resolved every minute.
- `validateWiring()`: the dev seam's check of every wiring reference.

## Constants

- `BREAKER_CURVES`, `DEFAULT_BREAKER_CURVE`: each curve's instant multiple.
- `STANDARD_BREAKER_RATINGS`, `EDISON_FUSE_MAX_A`: the ratings
  `validateWiring()` allows.
- `PANEL_DEFAULT_VOLTS`: a panel's or board's volts when it gives none.
- `OLD_BOARD_PCT`, `OLD_BOARD_FUSE_A`, `REWIRE_FUSE_MIN`: the old fuse
  boards.
- `TANK_FLOAT_START`, `HOUSE_PUMP_FLOW_LPH`, `HOUSE_TANK_L`: tanks and pumps.
- `TOASTER_RUN_MIN`, `MICROWAVE_MINUTE_CHOICES`, `MICROWAVE_DIAL_MAX_MIN`: the
  stop rules' times.
- `PLUG_APPLIANCE`, `KETTLE_EFFICIENCY`: what a plug load is, and how much of
  a kettle's draw reaches its water.
- `GRID_UP_SPANS` (from `POWER_FAILS_DAY`, `POWER_FAILS_HOUR`,
  `GRID_RECOVERY_AFTER_MIN`, `GRID_RECOVERY_MIN`): when the grid is up.
- `METER_READING_MIN`: a meter reading's time.

## Costs

- **Per game minute:** nothing.
- **Per power action or float change:** one building resolved.
- **Per tank coming full, appliance stop or kettle cut-out:** one building
  resolved. After a resolve, the stop rules walk that building's stop entries
  (none in an untouched building) and the running kettles.
- **Per grid change:** every busy building resolved; still buildings cost
  nothing until read.
- **Per read of a still building:** its look, kept per rules, seed and grid.
