# Spoilage

ARCHITECTURE sections: SURVIVAL / TIME SIMULATION (ageing, freshness, and
the settles); INVENTORY / ITEM SYSTEM (the unit helpers that carry ages with
their units, and `mergeRows()`); FIRE / COOKING (cooked food and dishes start
new); PERSISTENCE (stamping on a new game and on load).

## Purpose

Food goes off. A perishable item turns Stale and then Rotten as it ages, a
powered fridge slows that and a powered freezer stops it, and when the grid
fails, everything in them starts ageing at room rate at once.

## Model

**Perishable.** An item is perishable when its registry entry carries
`spoils` and it is not sealed: a sealed item does not age.

**Ages.** A perishable row keeps one effective age per unit, in minutes,
oldest first (`ages`, ITEM DATA SCHEMA). A unit is Fresh below `staleAfter`,
Stale below `rottenAfter`, and Rotten from there (`freshnessOfAge()`). A
row's freshness is its units' shared state, or "mixed" while they have
drifted apart and not been split (`rowFreshness()`). What is eaten or taken
next is the oldest unit (`unitFreshness()`, `takeUnits()`).

**Worked out when read.** Nothing ages food every minute. A row's `ages` are
true at its `agedAt`, a minute since the collapse, and a list is brought to
a minute (`settleList()`) only when something is about to read or change it.
Settling a row adds the age gained since its `agedAt` to every unit, sets
`agedAt` to the minute, then splits the row where its units now differ
(`splitByFreshness()`) and folds any changed row into a matching one
(`remergeRow()`). A row read with no `agedAt` is taken as true now.

**The age gained over a span** (`ageOver()`): one a minute carried, on the
floor, or in a container that is neither a fridge nor a freezer. In a fridge
or a freezer (tagged `fridge` or `freezer`), when its load would be powered
with the grid up, as the power state stands (`coldStoreWired()`: its switch
on and its path closed, or no load wired to it at all, unless its building
is deliberately unsupplied: [Power](power.md)), its powered rate
while the grid was up over the span (`gridUpMinutes()`) and its unpowered
rate the rest of it; otherwise its unpowered rate throughout. The rates are
`spoilageRate()`'s.

**Where ages come from.** Every writer of `ages` sets `agedAt`:

- a world item is aged from the collapse as if it had sat where it is
  untouched (`stampAges()`, `effectiveAge()`, which reads the load's switch
  as it was found), on a new game, on load, and when a container's roll
  adds it; a placement or pool entry that sets `ages` itself keeps them;
- an item an action makes is new (`asNewlyMade()`): an opened can, a caught
  fish;
- food that finishes cooking, and a dish that forms, start new at the minute
  they are settled to (`cookItem()`, `formDish()`);
- a crafted item takes the age of the oldest unit it was made from;
- a migrated item is taken as true now.

**The three settle points.**

1. **Where the player can reach it** (`settleReachable()`): what is carried,
   and the current room's floor, containers and car containers, with every
   list nested in them. At the end of every advance of time, after every room
   change, and on a new game, restart and load.
2. **Before a power change reaches it** (`settleColdStores()`): before a
   resolve changes a building's switches or breakers, by an action or by a
   trip it finds, that building's wired fridges and freezers are settled
   under the power state as it stood, then the change is committed. A grid
   change needs no settle: `ageOver()` integrates the grid.
3. **Before an event changes it**: a lit room's heat containers, nested
   contents included, are settled before cooking or a forming dish touches
   them (`settleHeat()`).

Freshness changes log nothing, and a row in a list nobody reaches goes
"mixed" silently until it is next settled.

## Invariants

- **Only the grid changes power over a span.** Every other change to a
  fridge's power is a settle point (settle point 2). A new source of power
  (#245) changes `ageOver()`'s rule.
- **Rows that merge are settled to the same minute.** Anything that moves or
  merges rows acts on lists already settled (settle point 1, or 3 inside a
  lit room), so `mergeRows()` joins ages as they are.
- **Every reader of ages reads a settled list.** Eating, taking, crafting,
  the Dishes panel, the Wait button and the item labels read only what the
  player can reach, settled at the end of every advance and every move.
- **`ages` and `agedAt` travel together.** The unit helpers copy a row whole
  (`unitsOf()`, `takeUnits()`), so a unit split off keeps its row's minute.

## Entry points

- `settleReachable()`: the player's reach brought to now.
- `settleList()`, `settleListDeep()`: one list, or a list and everything in
  it, brought to a minute.
- `settleColdStores()`: a building's fridges and freezers, before its power
  changes.
- `stampAges()`, `stampMissingAges()`: world items' starting ages.
- `unitFreshness()`, `rowFreshness()`, `isPerishable()`, `isFrozenIn()`:
  what the rest of the game reads.

## Constants

- `FRIDGE_RATE_POWERED`: a powered fridge's rate, against room rate.
- `ROTTEN_RESTORES_FACTOR`, `ROTTEN_POISONING_CHANCE`: what Rotten food does
  when eaten.
- Each perishable's `staleAfter` and `rottenAfter` are its registry entry's
  `spoils`.

## Costs

- **Per game minute:** nothing.
- **Per advance of time and per move:** the lists the player can reach.
- **Per power change to a building:** that building's fridges and freezers.
- **Per cooking event:** the lit rooms' heat containers.
- **On a new game and on load:** the stamping walk.
