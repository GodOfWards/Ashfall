# Ashfall Handoff — The mid-block toll, and three unstated facts

Current shipped version: v0.4.16
Implied version-change type: PATCH
Issues: #92 — the move floor makes a mid-block stop cost more than the block it
sits inside; #97 — `doBreakCar()` is gated on `blunt` while its log line says
"You pry the door open"; #98 — `invTab` and `worldTab` are the only pure-UI
fields in `state`; #99 — chopping is exactly break-even at full Energy, and
nothing says the three constants are in that relationship

## What this is

Four `tier-1` items that are one complaint applied four times: **a fact the
game acts on that the source never states.** A movement cost nobody chose, a
log line that promises a tool the gate doesn't require, a save that carries UI
state under a convention the file elsewhere decided the other way, and an exact
arithmetic relationship between three constants declared in two sections.

None of the four is a new mechanic. Three are behaviour-neutral or
near-neutral; one (#92) is a deliberate balance change, and is the only part of
this pass a player will feel.

## Relevant existing state

All of this was verified by reading `ashfall.html` at v0.4.16 and by
enumerating the live world, not recalled.

### Movement (#92)

`moveMinutes()` is the only place a duration is floored, and `exitMinutes()` is
its only caller:

```js
const MIN_MOVE_MIN = 1;
function moveMinutes(distanceM){ return Math.max(MIN_MOVE_MIN, distanceM / GAITS[effectiveGait()].speed / 60); }
function exitMinutes(exit){
  const fromLoc = world[state.currentRoom].locationId;
  const toLoc = world[exit.to].locationId;
  const d = (fromLoc === toLoc) ? exit.distanceM : locationDistance(fromLoc, toLoc);
  return moveMinutes(d);
}
```

`exitMinutes()` has three callers: `doMove()`, `renderMoveActionsPanel()` and
`renderHereActionsPanel()`.

The live exit census, computed by walking every room's `exits` through
`isGridTravel()` / `locationDistance()`:

| | count |
|---|---|
| grid-travel exits at 50 m | **448** |
| grid-travel exits at 100 m | **224** |
| non-grid exits | **102** |
| …of which zero-distance (building entrances) | **22** |
| total | **774** |

Exactly two grid distances exist. Every full block has two routes with the same
endpoints — one 100 m move, or two 50 m moves through the mid-block node — and
the flat per-move floor prices them differently:

| gait | 1 × 100 m | 2 × 50 m | penalty for stopping |
|---|---|---|---|
| sneak (0.6 m/s) | 2.778 | 2.778 | none |
| walk (1.2 m/s) | 1.389 | 2.000 | +44% |
| fast (2.0 m/s) | 1.000 | 2.000 | +100% |

The mid-block nodes are where the world's content hangs: the five `hasTree`
rooms, the parked cars at `mid_poplar_1_2` and `mid_main_1_3`, the entrances to
Acorn, Oak, the alley, the pharmacy, the hardware store and the auto shop, and
loose floor items at `mid_dock_2_4`, `mid_dock_1_2`, `mid_mill_7_9`,
`mid_main_5_7`. The toll falls on looking around.

`MIN_MOVE_MIN`'s existing comment explains the pace question and the 22
zero-distance entrances, and ends with a clause this pass makes false: "over a
50 m block the two are identical, both floored to 1 minute."

### Vehicle forcing (#97)

```js
// renderHereActionsPanel()
if(room.carContainers && room.carLocked && hasTool("blunt")){
  hereBox.appendChild(actionButton("Force the vehicle open", doBreakCar, "locked"));
}

function doBreakCar(){
  const room = world[state.currentRoom];
  room.carLocked = false;
  log("You pry the door open. The lock gives with a crack.", "warn");
  render();
}
```

Eight items carry `blunt` (`frying_pan`, `metal_pipe`, `crowbar`, `wrench`,
`hand_axe`, `tire_iron`, `baseball_bat`, `riot_baton`). One carries `prying`:
the crowbar. `prying` is listed in the ITEM DATA SCHEMA comment's
"declared, with no consumer yet" group, and stays there.

### UI fields in `state` (#98)

```js
currentRoom:"living", gait:"walk", invTab:"inventory", worldTab:"floor",
```

`serializeGame()` writes `state` wholesale, so both fields land in every save
and every export. The file has already decided this question the other way,
three times, for fields of exactly this kind — `mapZoomMode` / `mapZoomStep`
("deliberately outside `state`"), `gameOver` ("UI-only: never saved") and
`detailItem` ("UI-only").

25 references, all in `ashfall.html`:

- `addToDestination()` :3783, :3785
- `doTake()` :3846 · `doStore()` :3865, :3866
- `doConsume()` :3884 · `doEquip()` :3900, :3911 · `doUnequip()` :3929
- `getItemActions()` :3955, :3962
- `doMove()` :4111 · `doOpenContainer()` :4204
- `renderInventoryPanel()` :5695, :5699, :5700, :5703, :5707, :5709, :5712
- `renderWorldItemsPanel()` :5727, :5731, :5735, :5736, :5740

Two of those are writes from inside `render()`, which is otherwise a pure
projection. Both are load-bearing — the line after each would throw on a stale
tab — and both stay; the point of the move is that they stop being writes to
saved data.

### The chop relationship (#99)

Three constants, two sections, ~4,100 lines apart:

```js
const BASELINE_STAMINA_RATE = 1;    // :295, STAMINA / FATIGUE SYSTEM CONSTANTS
const CHOP_TREE_EXERTION = 30;      // :312, STAMINA / FATIGUE SYSTEM CONSTANTS
const FISH_EXERTION = 8;            // :313, STAMINA / FATIGUE SYSTEM CONSTANTS
const FISH_DURATION_MIN = 20;       // :4438, FIRE / COOKING
const CHOP_TREE_MIN = 30;           // :4442, FIRE / COOKING
```

`applyExertion()` is called *after* `advanceTime()` at every call site
(`doFish()` :4456-4457, `doChopTree()` :4562-4563, `doMove()` :4098-4106), so
an action's own duration recovers Stamina before its Exertion lands. The
recovery delay does not eat into that: `runAwakeStep()` increments
`state.totalMinutes` before calling `recoveryStep()`, so on the first minute
`totalMinutes - lastExertionMinute` is already 1 and
`isExertionDelayActive()`'s `< STAMINA_RECOVERY_DELAY_MIN` is false. The full
duration recovers.

At full Energy with no hunger/thirst penalty:

```
chop : 30 min × 1/min recovered = 30   spent 30   net  0.0
fish : 20 min × 1/min recovered = 20   spent  8   net +12.0
```

Chopping sits exactly on the line. Retune `CHOP_TREE_MIN`, `CHOP_TREE_EXERTION`
or `BASELINE_STAMINA_RATE` — the last for reasons having nothing to do with
chopping — and it flips either way. Nothing records that they are in this
relationship.

`const` is not hoisted, so the derivation cannot simply be written where
`CHOP_TREE_EXERTION` currently sits: `CHOP_TREE_MIN` is declared ~4,100 lines
later and the reference would throw at load. A constant has to move.

## Rules / mechanics

### 1. Grid travel is floored per block, not per move (#92)

Add a named constant for the grid pitch, beside `MIN_MOVE_MIN` in
CONFIG / CONSTANTS:

```js
const BLOCK_M = 100;
```

It is the same figure the `LOCATIONS` comment states as "Block size 100m" and
that every street coordinate embodies; this is that figure named where
movement reads it. Say so in its comment — it is a second statement of a fact
the coordinates already carry, and the reason it earns a name is that a
formula, not a table, now depends on it.

Apply the floor in proportion to distance for grid travel, flat for everything
else:

```js
function moveMinutes(distanceM, gridTravel){
  const floor = gridTravel ? MIN_MOVE_MIN * distanceM / BLOCK_M : MIN_MOVE_MIN;
  return Math.max(floor, distanceM / GAITS[effectiveGait()].speed / 60);
}
function exitMinutes(exit){
  const fromLoc = world[state.currentRoom].locationId;
  const toLoc = world[exit.to].locationId;
  const d = (fromLoc === toLoc) ? exit.distanceM : locationDistance(fromLoc, toLoc);
  return moveMinutes(d, isGridTravel(state.currentRoom, exit.to));
}
```

`isGridTravel()` is a function declaration in the same IIFE scope and is
therefore hoisted; calling it from `exitMinutes()` needs no reordering.

**The flat branch is load-bearing and must not be collapsed into the
proportional one.** The 22 building entrances have `locationDistance() === 0`;
a proportional floor would floor them at zero and make them free. They are
non-grid exits, so `isGridTravel()` already routes them to the flat floor —
but the reason has to be written down, because the two branches otherwise look
like a redundancy waiting to be tidied away.

Resulting costs — and this is the whole behavioural change:

| gait | 100 m | 2 × 50 m before | 2 × 50 m after |
|---|---|---|---|
| sneak | 2.778 | 2.778 | 2.778 |
| walk | 1.389 | 2.000 | **1.389** |
| fast | 1.000 | 2.000 | **1.000** |

Both routes now cost exactly the same at every gait. Nothing gets more
expensive: the only values that change are the 448 fifty-metre grid exits, at
Walk (1.000 → 0.694) and Jog (1.000 → 0.500). 100 m moves, every non-grid
exit, and all of Sneak are untouched.

Rewrite `MIN_MOVE_MIN`'s comment. It must state: the two branches and why they
differ; that the flat branch is what stops the 22 zero-distance entrances being
free; and that the per-move flat floor is what produced the +44% / +100% toll,
so the next reader knows the proportional form was chosen rather than
stumbled into. Delete the "over a 50 m block the two are identical" clause —
this pass makes it false. Keep the pace paragraph; it is still correct, since a
100 m block at Jog still costs 1.00 against Walk's 1.39.

### 2. The vehicle log line stops promising a crowbar (#97)

In `doBreakCar()`:

```js
log("You force the door. The lock gives with a crack.", "warn");
```

"Force" matches the button's own label. The second sentence is unchanged — it
was never the problem.

The gate stays `hasTool("blunt")`. Add a comment above it saying so and why,
so the next audit reads a decision rather than an oversight — naming no issue
number, version or handoff path, per the convention the v0.4.14 annotations
follow:

```js
// Forcing a vehicle asks for leverage, not one specific tool: any `blunt`
// item qualifies, and the log line is worded to match. Deliberately not
// gated on `prying`, which is carried by the crowbar alone and would make
// early vehicle access depend on a single item.
```

`prying` remains in `ITEM_REGISTRY` and remains in the schema comment's
"declared, with no consumer yet" list. Neither changes.

### 3. `invTab` and `worldTab` leave `state` (#98)

Remove both from `makeDefaultState()`, leaving
`currentRoom:"living", gait:"walk",`.

Declare them as module-level bindings immediately after `detailItem`, carrying
a comment in the same register as `mapZoomMode`'s:

```js
let invTab = "inventory";
let worldTab = "floor";
```

The comment must say that they are UI-only and deliberately outside `state`,
that this is the same call already made for `mapZoomMode`/`mapZoomStep`,
`gameOver` and `detailItem`, and that the consequence is a save carrying no
record of what the panels looked like.

Rewrite all 25 references to drop the `state.` prefix. Two need care, because
only the prefix on the tab goes — the slot lookup still reads `state`:

```js
if(invTab !== "inventory" && !state[invTab]) invTab = "inventory";   // :5695
if(CONTAINER_SLOTS.indexOf(invTab) >= 0){                            // :5707
```

Reset both to their defaults wherever a session's UI restarts:

- `doRestart()`, beside `detailItem = null; _uidCounter = 1;`
- `applyLoadedData()`, beside `detailItem = null; gameOver = false;`

Both panels therefore open on Inventory and Floor after a load or a restart.
That is the intended behaviour, not a side effect: it is what "the save carries
no record of the panels" means in practice, and it is the same thing
`mapZoomMode` already does.

**Save compatibility.** `SAVE_KEY` does not rotate — this removes fields rather
than adding them, and the version change is PATCH. An existing save's
`invTab`/`worldTab` survive `applyLoadedData()`'s
`{ ...base, ...data.state }` spread as inert keys that nothing reads; see the
design decision below for what to do about that.

### 4. The chop relationship is written as a derivation (#99)

Move each task's Exertion constant to sit beside its duration, then derive
the one that is derivable.

Remove from CONFIG / CONSTANTS (STAMINA / FATIGUE block): `CHOP_TREE_EXERTION`
and `FISH_EXERTION`, and — per the design decision below —
`JOG_EXERTION_PER_MIN`.

Add to FIRE / COOKING, each immediately after its own duration:

```js
const FISH_DURATION_MIN = 20;
// Fishing is deliberately net positive on Stamina at full Energy: 20 minutes
// of baseline recovery against 8 spent. Not derived from its duration the way
// chopping is — the margin is the point, and the number is a balance value
// retunable on its own.
const FISH_EXERTION = 8;
…
const CHOP_TREE_MIN = 30;
// Chopping is deliberately break-even on Stamina at full Energy: a chop spends
// exactly what its own duration recovers at the awake baseline rate, so it is
// sustainable while rested and bites only once low Energy or low Hunger/Thirst
// pull the recovery multiplier down. Written as the product rather than as a
// literal so the relationship survives a retune of either input — the
// relationship is the rule, not the number.
const CHOP_TREE_EXERTION = CHOP_TREE_MIN * BASELINE_STAMINA_RATE;
```

`BASELINE_STAMINA_RATE` is declared at :295, long before FIRE / COOKING, so the
derivation evaluates cleanly. `30 × 1 = 30`: the value is unchanged and the
behaviour is bit-identical, which the diff proves.

Add one line to the STAMINA / FATIGUE constants block's header comment saying
that each task's Exertion is now declared beside the task, and that this block
owns only what Exertion *does*. Without it the emptied block reads as having
lost something rather than having been narrowed on purpose.

## Design decisions to make during implementation

Each of these is a narrow call. Record which was taken in the changelog's
Notes/assumptions or Documentation section — don't choose silently.

1. **`JOG_EXERTION_PER_MIN`'s home.** Its only reader is `doMove()`.
   *Recommended:* move it to WORLD INTERACTION immediately above `doMove()`,
   so that after this pass no task's Exertion is left orphaned in the
   STAMINA / FATIGUE block and the "declared beside the task" rule holds
   without exception. *Alternative:* leave it where it is, and say in the
   block comment that movement is the exception because it has no single
   duration to sit beside. Either is defensible; the first is more consistent.

2. **Inert `invTab`/`worldTab` keys in loaded saves.** After #98 these arrive
   from an old save, are read by nothing, and are re-emitted by the next
   `serializeGame()`. *Recommended:* leave them, and say why in a sentence —
   the load path deliberately validates only the shapes that would throw
   (`validateLoadedWorld()`), so deleting two named keys would imply a schema
   check the file does not perform, for fields that cost nothing. *Alternative:*
   `delete` both in `applyLoadedData()` after the spread. No behavioural
   difference either way.

3. **`moveMinutes()`'s floor, inline or named.** The spec above inlines the
   ternary. Extracting a `moveFloorMinutes(distanceM, gridTravel)` is equally
   acceptable if the call site reads better for it; there is exactly one
   caller, so this is a readability call and nothing else.

## Data / schema changes

None. No new or changed state fields, item-schema fields, tags, categories, or
room/container/exit schema fields. #98 *removes* two fields from PLAYER STATE
and from the serialised save; nothing is added anywhere.

## In scope

- `BLOCK_M`; the proportional grid-travel floor in `moveMinutes()`; the
  `gridTravel` argument threaded from `exitMinutes()`; the rewritten
  `MIN_MOVE_MIN` comment.
- `doBreakCar()`'s log line; the comment on the `blunt` gate.
- `invTab`/`worldTab` moved out of `state`, all 25 references rewritten, both
  reset in `doRestart()` and `applyLoadedData()`.
- `CHOP_TREE_EXERTION` and `FISH_EXERTION` moved to FIRE / COOKING;
  `CHOP_TREE_EXERTION` written as `CHOP_TREE_MIN * BASELINE_STAMINA_RATE`;
  the STAMINA / FATIGUE block comment narrowed to match.

## Explicitly out of scope

- **The sub-minute display gap.** `fmtDuration()` floors display at
  `MIN_DISPLAY_MIN` (1 minute), so after #92 a 50 m half-move at Jog costs
  0.500 and still reads `(0:01)` — the button claims twice what it charges,
  and two half-moves display 2 minutes against 1 charged. This is the display
  floor's own question, and `MIN_DISPLAY_MIN` was split out from
  `MIN_MOVE_MIN` precisely so the two could move independently. Do not touch
  it here; file it (see below).
- **Gating anything on `prying`.** #97 is settled as a prose fix. The tag stays
  unconsumed.
- **#66 / #67** — the unreachable spawn pools and the single-matchbox fire
  problem. #97's decision leans on them being open, but this pass does not
  touch either.
- **#8** — map expansion. It adds roughly 300 rooms reached through mid-block
  nodes, which is why #92 is worth settling before it, but no map work happens
  here.
- **#43, #87** — map label measurement and splitting. Unrelated.
- Any retune of `MIN_MOVE_MIN`, `GAITS` speeds, `FISH_EXERTION`,
  `CHOP_TREE_MIN` or `BASELINE_STAMINA_RATE`. Their *values* are unchanged;
  only where two of them live, and how one is written, changes.

## Sections touched

- **CONFIG / CONSTANTS** — `BLOCK_M` added; `MIN_MOVE_MIN` comment rewritten;
  `CHOP_TREE_EXERTION`, `FISH_EXERTION` (and `JOG_EXERTION_PER_MIN`, per
  decision 1) removed from the STAMINA / FATIGUE block, whose header comment
  narrows.
- **CORE UTILITIES** — `moveMinutes()`, `exitMinutes()`.
- **PLAYER STATE** — `makeDefaultState()` loses two fields; two module-level
  bindings added beside `gameOver` / `detailItem`.
- **INVENTORY / ITEM SYSTEM** — `addToDestination()`, `doTake()`, `doStore()`,
  `doConsume()`, `doEquip()`, `doUnequip()`, `getItemActions()`: tab references
  only.
- **WORLD INTERACTION** — `doMove()`, `doOpenContainer()`, `doBreakCar()`;
  `JOG_EXERTION_PER_MIN` if decision 1 takes the recommendation.
- **FIRE / COOKING** — the two Exertion constants arrive here.
- **PERSISTENCE** — `applyLoadedData()` resets the two bindings.
- **RENDERING** — `renderInventoryPanel()`, `renderWorldItemsPanel()`,
  `renderHereActionsPanel()` (the gate comment only).

This is a mechanics-and-plumbing pass. **No WORLD DATA changes at all** — no
room, item, container, exit or description is touched, and `ITEM_REGISTRY` is
not edited.

## UI changes

- Mid-block travel gets cheaper at Walk and Jog. The Move buttons' printed
  costs do not visibly change, because `fmtDuration()` already rounds a
  sub-minute half-move up to `(0:01)` — see "out of scope".
- Forcing a vehicle logs "You force the door. The lock gives with a crack."
  instead of "You pry the door open. …".
- The Inventory and Here panels open on their first tab after a load or a
  restart, rather than on the tab that was showing when the game was saved.

Nothing else. No new buttons, no removed buttons, no layout change.

## Validation

- **`#92`** — re-run the exit census through `isGridTravel()` /
  `locationDistance()` and confirm it is unchanged: 448 grid exits at 50 m,
  224 at 100 m, 102 non-grid of which 22 zero-distance, 774 total. Then
  confirm `2 × moveMinutes(50, true) === moveMinutes(100, true)` at all three
  gaits, and that `moveMinutes(0, false) === MIN_MOVE_MIN`.
- **`#98`** — `grep -c "state\.invTab\|state\.worldTab" ashfall.html` must
  report `0`, and a fresh `serializeGame()` must contain neither key. Equip a
  bag, switch to its tab, save, reload: the game loads and the Inventory panel
  opens on Inventory.
- **`#99`** — `CHOP_TREE_EXERTION` must still evaluate to `30`. The behaviour
  claim is "no change", so prove it by diff per the Project Guide:
  `git diff origin/main...HEAD -- ashfall.html` should show the two constants
  moved and one rewritten as a product, and nothing else in the chop or fish
  paths.
- The whole pass: `validateItemRegistry()`, `validateLocations()` and
  `validateRoomSchema()` from the console should all still report clean, and
  the load should produce no `applyComputedDirections` warnings.

## Dependencies / issue linkage

Fulfils **#92**, **#97**, **#98** and **#99** — `Closes #92`, `Closes #97`,
`Closes #98`, `Closes #99` in the pull request description.

Expected to be filed at wrap-time:

1. **The sub-minute display gap** described under "out of scope" — a half-move
   that costs 0.500 and prints `(0:01)`. Name `fmtDuration()` and
   `MIN_DISPLAY_MIN`, and note that #92 is what made the gap worth having an
   opinion about. `tier-1`.
2. **Revisit gating vehicle forcing on `prying`** once #66 makes the crowbar
   reachable outside `onebee/toolcabinet` and `hardware/toolwall`. #97's
   decision is explicitly conditional on the current reachability, and closing
   it leaves nothing else recording that. `tier-2`, blocked on #66.

If either turns out not to be worth filing, say so in the changelog's
Documentation section rather than dropping it silently.

Related but not prerequisites: **#66/#67** (spawn reachability), **#8** (map
expansion), **#75** (settled the pace question this pass leaves standing),
**#53** (health multipliers will land on #99's arithmetic, which is easier to
reason about once the relationship is written down).

## Open questions for Tom

None. All four design calls were settled during the planning session:
proportional floor for #92, prose-not-gate for #97, both fields out of `state`
for #98, derive-and-move-the-Exertion-constants for #99.

## After implementation

Open one pull request carrying `GAME_CONFIG.VERSION` bumped (PATCH), a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md` naming this handoff by the
path it was read at, `Closes #92`, `Closes #97`, `Closes #98`, `Closes #99`,
the two new issues above referenced, and this file moved to
`handoffs/archive/` by `git mv` with its filename unchanged.

Record in the entry: which option each of the three implementation decisions
took, that #92 is the pass's only player-facing balance change and is
retunable, and that #99's half is bit-identical and proven by diff.
