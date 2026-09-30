# Power

ARCHITECTURE sections: SURVIVAL / TIME SIMULATION, its POWER sub-section (the
network's expansion, the resolve, and the game's reads of it); WORLD DATA
(POWER SCHEMA: `APPLIANCES`, `WIRING_TEMPLATES`, `WIRING`, `GAME_WIRING`, and
BUILDING TYPES' `wiring` and `water`); PLAYER STATE (`state.power`,
`state.tankDrawn`); WORLD INTERACTION (the power actions, the meters,
`doFillAtSink()`); RENDERING (the device pop-up, the Electrical view, the
readouts).

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
resolve's drawing, the seed and each tank's float (`tankFloat()`). It works
out, lowest layer first (`BREAKER_LAYERS`), what is live, what each load's
switch and path give it (powered), what draws, what starts, and the current
through every breaker. Simplified rules skip feeders and circuits, but never
a fuse (`consultsBreaker()`, `circuitSkipped()`).

**Draw.** A cycling load (`dutyCycle`) draws its average, watts ×
`dutyCycle`, whenever it has power (`loadDrawWatts()`). A pump (`flowLph`)
draws while its tank's float calls: the tank below `TANK_FLOAT_START`, or the
pump drawing in the previous resolve and the tank not yet full; never on a
full tank. Any other load draws its watts while it has power. A breaker's
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
- **A water draw** (`doFillAtSink()`) that moves a pumped tank's float
  resolves its building at once, so its pump starts or stops calling.
- **A tank coming full** is a scheduled event (`docs/systems/time.md`): its
  building resolves, so the pump stops and its latch clears.
- **The grid failing or returning**, at every bound of `GRID_UP_SPANS`, is a
  scheduled event (`resolveGrid()`): the world is settled to that minute,
  then every busy building resolves at the grid's new state, then the
  player hears what changed (`logGridChange()`, `logTrips()`).

**POWER RUNS.** Buildings share nothing but the grid, so each resolves on its
own, and one nobody has touched needs no resolving at all: with no entry in
the power state, its breakers closed, its switches at their rolled defaults
(`switchOnIn()`) and its tank full, its look is a pure function of the seed,
the rules and the grid (`stillLook()`). A building is busy when it has an
entry in the power state, a float that is not full, or default-on loads that
could overload one of its breakers (`untouchedTrippers()`, which sums a
superset of what can draw). `powerNow` holds the grid's state and, per
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
  a settle point. A new source of power (#245) breaks this, and with it
  spoilage's rule for a span.
- **A still building is never stored.** Its look is always derived from its
  own nodes, so a building wired after a run started needs nothing written.
- **Starts need a previous resolve.** Nothing starts on boot, restart or
  load.

## Entry points

- `isPowered()`: whether a load has power now; spoilage, the stove and the
  room descriptions read it.
- `loadRunningNow()`: whether a load is running, for its readout.
- `changePower()`, `resolveBuilding()`: an action's or an event's resolve of
  one building.
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
- `GRID_UP_SPANS` (from `POWER_FAILS_DAY`, `POWER_FAILS_HOUR`,
  `GRID_RECOVERY_AFTER_MIN`, `GRID_RECOVERY_MIN`): when the grid is up.
- `METER_READING_MIN`: a meter reading's time.

## Costs

- **Per game minute:** nothing.
- **Per power action or float change:** one building resolved.
- **Per tank coming full:** one building resolved.
- **Per grid change:** every busy building resolved; still buildings cost
  nothing until read.
- **Per read of a still building:** its look, kept per rules, seed and grid.
