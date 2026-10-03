# Fluids

ARCHITECTURE sections: INVENTORY / ITEM SYSTEM (the FLUIDS, WATER
TEMPERATURE, DRINKING and POURING blocks, the sinks and timed transfers);
SURVIVAL / TIME SIMULATION (`autoDrink()`, and its check in `clockStep()`; the
electric kettle, KETTLES in POWER, is [Power](power.md)'s); FIRE / COOKING
(HEATING, and VESSELS AND DISHES: a dish's water, and boiling); PERSISTENCE
(`migrateFluidRelease()`, `migrateWaterTemperatureRelease()`); RENDERING (the
transfer submenu, the tap's Here actions, a dish's water need, the row tint);
EVENTS / UI HELPERS (`afterAction()`). The shapes are in ITEM DATA SCHEMA
(`holdsFluid`, `fluid`, a dish's `water`, `boilMinutes`, `whistleLog`) and
CONTAINER SCHEMA (`heatSource`).

## Purpose

Water is a measured fluid with a temperature. Every holder (a bottle, a
saucepan, the pot, the thermos, a canteen, a bucket, a water jug, a dispenser
jug, the two kettles) holds some millilitres of one kind of water, which the
player fills at a sink, drinks in measured amounts, pours between holders,
heats, boils clean, cooks with, and drinks on their own when thirsty.

## Model

**Holders and kinds.** A holder is an item whose registry entry carries
`holdsFluid`; its capacity is read by `capacityMlOf()`. What it holds is its
instance's `fluid`, a kind and a whole number of millilitres, absent when
empty. A holder holding a dish holds no fluid at all (`holdsFluidAtAll()`):
the dish took the water. `fluidSpaceMl()` is the room a holder has. Every
reader goes through these helpers, and every writer through `addFluid()` and
`takeFluid()`.

**Mixing.** `mixKinds()` is the one statement of what mixes: nothing with a
kind is that kind, a kind with itself is itself, and clean water with tainted
is tainted. Any other pair does not mix, and no action offers it. The kinds
are open-ended; today there are two.

**Every fluid action takes the least** of the amount asked, what the source
has, and what the target has room for. No button is greyed out for asking too
much.

**The sink and the tap.** A room with a sink runs while `waterRunningIn()`
holds ([Power](power.md): a building's tank while it holds water, else the
mains). `doFillAtSink()` fills one unit as far as it has room, clean water at
`TANK_WATER_C` off a tank or `MAINS_WATER_C` off the mains, mixed into what is
there; `doDrinkAtSink()` drinks `MEASURE_ML` from the tap. Off a tank, both draw the litres they take, to the
millilitre (`drawFromTank()`), only what the tank has left on the last of it,
and a draw that moves a pumped tank's float resolves its building. A sink on
the mains draws nothing down. A dry tank's sink says so in the fill's and the
tap's place (`tapDryFor()`, `sinkDry()`).

**Drinking.** Any holder with fluid and no dish is drunk from (`drinkable()`),
a vessel with ingredients included: the water, never the food. Every drink
takes `MEASURE_ML`, or what is left when less; there is no drink to full
Thirst. The unit is the least-left one
holding the same fluid among the rows of the same item (`drinkTarget()`), as
Eat picks. `drinkFrom()` is the one drink: Thirst at `WATER_THIRST_PER_L`, the
fluid taken (a holder drunk dry stays, empty), its line, and for tainted water
food poisoning at `TAINTED_WATER_POISONING_CHANCE` per
`TAINTED_WATER_DOSE_ML`. Eating by the part (`EAT_PARTS`) is food's alone.

**Auto-drink.** Awake and below `LOW_THIRST_THRESHOLD`, the player drinks on
their own (`autoDrink()`) from what they carry (`invPools()`), clean water
only and never from a tap: `MEASURE_ML` in all, from the holder with the
least left first, then the next if one runs dry, until the measure is drunk
or the clean water carried runs out. At the threshold, one measure lifts
Thirst clear of it, so it fires again only when Thirst next falls below. It is checked at the minute Thirst crosses the threshold, in
`clockStep()`, and at the end of every action (`afterAction()`), never while
asleep, during a sleep or a blackout. There is no switch.

**Pouring.** Any holder with fluid and no dish pours into any other within
reach (`nearbyPlaces()`: what is carried, the floor, the listed containers,
the room's heat container) that has room and whose fluid mixes
(`pourTargets()`). Rows of one item in one place that would hold the same
fluid after the pour are one target, poured into the fullest unit among them
that is not full. The source unit is split off its row first, so the rest of
its row is a target like any other (`pourFluid()`). Pour out the water empties
one unit (`doPourOut()`).

**Timed transfers.** A fill or a pour that moves no more than
`FLUID_INSTANT_MAX_ML`, judged by what it moves, is instant; a larger one
takes its litres over `TAP_FLOW_L_PER_MIN` (a fill) or `POUR_L_PER_MIN` (a
pour), a minute at least (`transferMinutes()`). The water moves first, a tank
draw resolving its building with it, and then the minutes pass
(`advanceTime()`); nothing interrupts them. The button shows the time, rounded
up, only when it would be taken. Pour out and drinking stay instant.

**Temperature.** A water's temperature is true at a minute: a fluid's `temp`
(or a dish's water's), and absent means `ROOM_TEMP_C`, at any minute, so
nothing the world spawns needs one. It is worked out when read
(`waterTempOf()`, `fluidTempC()`): Newton's law in closed form, cooling toward
the room at the holder's `holdsFluid.coolPerMin`, written from
`OPEN_PAN_COOL_PER_MIN`, `CLOSED_HOLDER_COOL_FACTOR` and the holder's size
(`holderCoolPerMin()`), or `THERMOS_COOL_PER_MIN`. Nothing ticks it and
nothing schedules it. Every writer stamps it at `settledAt` through
`setWaterTemp()`, which drops a temperature within `TEMP_MERGE_TOLERANCE_C` of
the room's.

**Mixing temperatures.** Water added to a holder (`addFluid()`: a fill or a
pour) takes the volume-weighted mean of the two temperatures, each read now,
stamped now. Two holder rows stack only when their water's temperatures, read
now, are within `TEMP_MERGE_TOLERANCE_C` (`sameStackState()`), and a merge
takes their mean by units (`mergeRows()`). Rows that differ only by
temperature gather under one header, as rows that differ by level do.

**Heating.** Only a holder whose `holdsFluid.heats` is set heats: the
saucepans, the pot and the stovetop kettle. In a lit room's heat containers
each gets its source's full power (`heatKwOf()`, by its container's
`heatSource`: `STOVE_HEAT_KW` or `CAMPFIRE_HEAT_KW`), as if on its own burner,
and its water rises linearly, at the power over its litres and
`WATER_HEAT_KJ_PER_L_K` (`heatOver()`), to `WATER_BOIL_C`, where it stays: at
the boil. Any other holder in a heat container cools as anywhere else. A
heating holder in a lit room is stamped by every settle, at its minute
(`settleVessel()`), so a span starts from the stamp when the holder has heated
throughout, and from the closed-form value when it has been off the heat in
between. The electric kettle heats on its own ([Power](power.md), KETTLES).

**The boil.** Tainted water's `boilMinutes` counts only its time at the boil,
without a break: water that starts a span below the boil (taken off the heat,
the heat out or put out, cooler water poured in) has lost its count, and water
mixed to below the boil loses it at once; water at the boil poured into water
at the boil keeps it. At `BOIL_MINUTES` it turns clean, and forms the dish it
now makes, ending the span there. A holder with a `whistleLog` (the stovetop
kettle) says it when its water reaches the boil from below, heard in its room:
once a boil, since it whistles again only from below.

**Dishes.** A dish that needs water needs at least `DISH_WATER_MIN_SHARE` of
its vessel's capacity in clean water (`dishWaterMinMl()`, `templateStatus()`).
A dish that forms takes up all the water there is (`formDish()`), and a water
dish keeps that water's volume and temperature as its `water`. It heats, holds
at the boil and cools by the same rules, at its vessel's constant and power,
with its water, at the part of the dish left, as the volume (`dishWaterL()`).
A water dish's `cookMinutes` count only while its water is at the boil: below
it they pause, and nothing is lost. A dish without water, or one from an older
save with no `water`, cooks by the span, as do raw items in a heat container
and ingredients in a vessel no template matches. The world's stew pots
(`dishFrom()`) come with their water at the room's temperature.

**The tint.** A row whose unit holds water, or whose vessel's dish has water,
is tinted in its own background by that water's temperature
(`unitWaterTempC()`, `waterTint()`): warm above `ROOM_TEMP_C`, cool below,
untinted at it, stronger the further off, the boil the strongest warm tint and
`WATER_FREEZE_C` the strongest cool one (`TINT_MAX_ALPHA`, `TINT_CURVE`). Only
the row: never the pop-up, and never a group's header. Drinking hot water does
nothing.

**Weight.** A fluid weighs a kilogram a litre (`fluidWeightOf()`), added to
its holder's weight.

**Groups and levels.** A holder's level is its millilitres over its capacity
(`unitLevel()`), drawn as a meter along its row. Holders stack only at the same
kind and millilitre, and temperatures within the tolerance
(`sameStackState()`), and rows that differ only by level or temperature
gather under one header (`groupKeyOf()`).

## Invariants

- **A holder's `fluid` is absent when empty, never zero**, and never more than
  its capacity: `takeFluid()` deletes it at zero, and every caller of
  `addFluid()` adds no more than `fluidSpaceMl()`.
- **A holder holding a dish holds no fluid**: `formDish()` deletes it, and
  `holdsFluidAtAll()` gives such a holder no room, so nothing pours or fills
  into it.
- **Kinds mix only through `mixKinds()`**, and an action whose pair it refuses
  is not offered.
- **Every change to one unit of a row goes through `changeOneUnit()`**, so a
  stack's other units keep their fluid and identical units fold back together.
- **A temperature is stamped at `settledAt`, never ahead of it**, so a read at
  any minute a settle can ask for is the closed form forward from the stamp.
- **A heating holder in a lit room is stamped by every settle**, and a running
  kettle by every settle ([Power](power.md)): the boil count's "without a
  break" rests on it.
- **A boil count is never kept below the boil**: `settleVessel()` drops it for
  water that starts a span below, and `addFluid()` for water mixed below.
- **Auto-drink drinks only clean water from carried holders**, and never while
  `asleep`.

## Entry points

- `capacityMlOf()`, `holdsFluidAtAll()`, `fluidSpaceMl()`, `fluidKindOf()`,
  `mixKinds()`: what the rest of the game reads.
- `addFluid()`, `takeFluid()`: the only writers of `fluid`.
- `waterTempOf()`, `fluidTempC()`, `unitWaterTempC()`: a temperature, read;
  `setWaterTemp()`: the one writer of `temp`.
- `settleVessel()`: a heating holder over a span; `heatOver()`,
  `minutesToBoil()`: the heating arithmetic.
- `drinkFrom()`: one drink from a holder, by hand or on your own.
- `doDrink()`, `doDrinkAtSink()`, `doFillAtSink()`, `doPour()`, `doPourOut()`:
  the actions; `transferMinutes()`, their time.
- `autoDrink()`: the drink on your own, from `clockStep()` and
  `afterAction()`.
- `migrateFluidRelease()`: an older save's `water` brought into `fluid`, on
  load; `migrateWaterTemperatureRelease()`: a saved campfire given its
  `heatSource`.

## Constants

- `MEASURE_ML`: what every drink drinks, auto-drink's included, and what Pour
  by the measure pours.
- `WATER_THIRST_PER_L`: Thirst restored per litre drunk.
- `TAINTED_WATER_POISONING_CHANCE`, `TAINTED_WATER_DOSE_ML`: tainted water's
  food-poisoning chance, and the amount it is for.
- `LOW_THIRST_THRESHOLD`: below it, the player drinks on their own.
- `DISH_WATER_MIN_SHARE`: the share of a vessel a dish needs in water.
- `BOIL_MINUTES`: how long tainted water must be at the boil, unbroken, to
  come clean.
- `FLUID_INSTANT_MAX_ML`, `TAP_FLOW_L_PER_MIN`, `POUR_L_PER_MIN`: timed
  transfers.
- `ROOM_TEMP_C`, `TANK_WATER_C`, `MAINS_WATER_C`, `WATER_BOIL_C`,
  `WATER_FREEZE_C`, `WATER_HEAT_KJ_PER_L_K`: the temperatures and the physics.
- `OPEN_PAN_COOL_PER_MIN`, `CLOSED_HOLDER_COOL_FACTOR`, `THERMOS_COOL_PER_MIN`:
  the cooling constants' sources.
- `TEMP_MERGE_TOLERANCE_C`, `TEMP_EPSILON_C`: stacking, and the boil's float.
- `STOVE_HEAT_KW`, `CAMPFIRE_HEAT_KW` (`HEAT_SOURCES`): the power a heat
  container gives each heating holder.
- `TINT_MAX_ALPHA`, `TINT_CURVE`: the row tint.
- `LEVEL_WARN_BELOW`: a meter at or below it draws in the warning colour.

## Costs

- **Per game minute:** one comparison of Thirst before and after the step.
- **Per action:** one comparison of Thirst with the threshold. Only while awake
  and below it does auto-drink walk the carried lists, never the world.
- **Per fluid action:** one or two items. Building the transfer submenu walks
  the lists in reach once. A timed transfer runs `advanceTime()` for its
  minutes, as any timed action does.
- **Per game minute:** nothing about temperature: it is worked out when read.
- **Per settle of a lit room:** the heating arithmetic per heating holder in
  its heat containers, beside its cooking ([Time](time.md)).
- **Per advance:** a lit room's next event adds the time to the boil (a
  holder that whistles, tainted water, a water dish) to its arithmetic.
- **Per render:** one temperature read (one exponential) per row with water,
  for its tint; a stack check reads two.
