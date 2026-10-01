# Fluids

ARCHITECTURE sections: INVENTORY / ITEM SYSTEM (the FLUIDS, DRINKING and
POURING blocks, and the sinks); SURVIVAL / TIME SIMULATION (`autoDrink()`, and
its check in `clockStep()`); FIRE / COOKING (VESSELS AND DISHES: a dish's
water, and boiling); PERSISTENCE (`migrateFluidRelease()`); RENDERING (the
transfer submenu, the tap's Here actions, a dish's water need); EVENTS / UI
HELPERS (`afterAction()`). The shapes are in ITEM DATA SCHEMA (`holdsFluid`,
`fluid`).

## Purpose

Water is a measured fluid. Every holder (a bottle, a saucepan, the pot, the
thermos) holds some millilitres of one kind of water, which the player fills
at a sink, drinks in measured amounts, pours between holders, cooks with,
and drinks on their own when thirsty.

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
mains). `doFillAtSink()` fills one unit as far as it has room, clean water
mixed into what is there; `doDrinkAtSink()` drinks Drink's or Drink all's
amount from the tap. Off a tank, both draw the litres they take, to the
millilitre (`drawFromTank()`), only what the tank has left on the last of it,
and a draw that moves a pumped tank's float resolves its building. A sink on
the mains draws nothing down. A dry tank's sink says so in the fill's and the
tap's place (`tapDryFor()`, `sinkDry()`).

**Drinking.** Any holder with fluid and no dish is drunk from (`drinkable()`),
a vessel with ingredients included: the water, never the food. Drink takes
`MEASURE_ML`, Drink all what brings Thirst to `VITAL_MAX`
(`drinkAllMl()`), each or what is left. The unit is the least-left one
holding the same fluid among the rows of the same item (`drinkTarget()`), as
Eat picks. `drinkFrom()` is the one drink: Thirst at `WATER_THIRST_PER_L`, the
fluid taken (a holder drunk dry stays, empty), its line, and for tainted water
food poisoning at `TAINTED_WATER_POISONING_CHANCE` per
`TAINTED_WATER_DOSE_ML`. Eating by the part (`EAT_PARTS`) is food's alone.

**Auto-drink.** Awake and below `LOW_THIRST_THRESHOLD`, the player drinks on
their own (`autoDrink()`) from what they carry (`invPools()`), clean water
only and never from a tap: the holder with the least left first, each as
Drink all, the next as one empties, until Thirst is full or the clean water
carried runs out. It is checked at the minute Thirst crosses the threshold, in
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

**Dishes.** A dish that needs water needs at least `DISH_WATER_MIN_SHARE` of
its vessel's capacity in clean water (`dishWaterMinMl()`, `templateStatus()`);
enough tainted water boils clean after `BOIL_MINUTES`, whatever its volume
(`settleVessel()`), and water added to a vessel starts its boil over. A dish
that forms takes up all the water there is (`formDish()`).

**Weight.** A fluid weighs a kilogram a litre (`fluidWeightOf()`), added to
its holder's weight.

**Groups and levels.** A holder's level is its millilitres over its capacity
(`unitLevel()`), drawn as a meter along its row. Holders stack only at the same
kind and millilitre (`sameStackState()`), and rows that differ only by level
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
- **Auto-drink drinks only clean water from carried holders**, and never while
  `asleep`.

## Entry points

- `capacityMlOf()`, `holdsFluidAtAll()`, `fluidSpaceMl()`, `fluidKindOf()`,
  `mixKinds()`: what the rest of the game reads.
- `addFluid()`, `takeFluid()`: the only writers of `fluid`.
- `drinkFrom()`: one drink from a holder, by hand or on your own.
- `doDrink()`, `doDrinkAtSink()`, `doFillAtSink()`, `doPour()`, `doPourOut()`:
  the actions.
- `autoDrink()`: the drink on your own, from `clockStep()` and
  `afterAction()`.
- `migrateFluidRelease()`: an older save's `water` brought into `fluid`, on
  load.

## Constants

- `MEASURE_ML`: what Drink drinks and Pour by the measure pours.
- `WATER_THIRST_PER_L`: Thirst restored per litre drunk.
- `TAINTED_WATER_POISONING_CHANCE`, `TAINTED_WATER_DOSE_ML`: tainted water's
  food-poisoning chance, and the amount it is for.
- `VITAL_MAX`: the top of Thirst's scale, what Drink all drinks to.
- `LOW_THIRST_THRESHOLD`: below it, the player drinks on their own.
- `DISH_WATER_MIN_SHARE`: the share of a vessel a dish needs in water.
- `BOIL_MINUTES`: how long tainted water boils before it comes clean.
- `LEVEL_WARN_BELOW`: a meter at or below it draws in the warning colour.

## Costs

- **Per game minute:** one comparison of Thirst before and after the step.
- **Per action:** one comparison of Thirst with the threshold. Only while awake
  and below it does auto-drink walk the carried lists, never the world.
- **Per fluid action:** one or two items. Building the transfer submenu walks
  the lists in reach once.
- Nothing is scheduled, and nothing about fluid is settled over time.
