# Ashfall Handoff — Seed report: what a seed's world holds

Current shipped version: v0.6.0
Implied version-change type: PATCH
Issue: #150 — Seed-aware reachability — report what a seed's world actually holds, not just what it can

## What this is

Two new dev-only console helpers on the `window.ashfallDev` seam:

- **`simulateSeed(seed)`** is the manifest of one seed's world: every item stack
  in it, hand-placed or rolled, without playing the seed.
- **`sampleSeeds(n, start)`** runs many seeds and compares how often each loot roll
  actually hits against the probability `SPAWN_POOLS` says it should have. It also
  reports how often each item and tool tag appears across seeds.

In the issue's words:

> arithmetic says what they should be, simulation says what they are. Those
> agreeing is worth knowing; them disagreeing is worth knowing much more.

Tom's decisions (planning session at v0.6.0):

- **Existence only.** The helpers report what a seed's world *contains*, not what
  the player can reach past locks, windows or searches.
- **`tier-1`, PATCH.** Nothing here is persisted and nothing here is a mechanic.

To make this possible, the roll core has to accept a seed explicitly. **Every roll
the game makes must come out bit-identical to v0.6.0.**

## Relevant existing state

Verified against `ashfall.html` at v0.6.0. Line numbers are that file's.

**The roll core** (CORE UTILITIES) reads the run's seed implicitly, at one point:

```js
function hashKey(parts){ return fnv1a(parts.join(KEY_SEP), state.seed); }      // 3751
function rollValue(...parts){ let t = (hashKey(parts) + 0x6D2B79F5) | 0; … }   // 3754
function chance(p, ...keyParts){ /* legality warn-and-clamp */ return rollValue(...keyParts) < p; }  // 3769
function randInt(min, max, ...keyParts){ return min + Math.floor(rollValue(...keyParts) * (max - min + 1)); }  // 3779
```

`chance()` is the one place a probability's legality is checked. It warns and
clamps rather than throwing. That must stay true.

**The three game callers of the core:**

- `rolledLootFor(roomId, container)` (4555). It is pure (no mutation, no state
  read but `state.seed`). Keys:
  - empty gate: `"loot", roomId, container.id, poolId, "empty"`
  - entry: `"loot", roomId, container.id, poolId, entry.itemId`
  - quantity: `…, entry.itemId, "qty"`

  Its only caller is `doOpenContainer()` (4579), which passes
  `state.currentRoom`.
- `doFish()`: `chance(FISH_BITE_CHANCE, "fish", state.currentRoom, state.totalMinutes)` (4841).
- `doConsume()`: `chance(it.illnessChance, "illness", state.rollSeq)` (4126).

**Which containers roll.** A container rolls when it carries `spawnPools` and not
`spawnRolled`. `validateReachability()` (5317) computes that inline, over a
freshly built `makeDefaultWorld()`, into a `livePools` set. In the fresh world
**24 containers roll**, in five buildings:

- Acorn (5): `twobee_kitchen` fridge and pantry, `twobee_bathroom` undersink,
  `twobee_bedroom` dresser, `onebee` closet
- Oak Apartments (8)
- Auto Workshop (4)
- Police Station (3)
- Riverside Freight (4)

The other 50 containers that carry `spawnPools` ship `spawnRolled:true` with
hand-placed contents. No car container carries `spawnPools`.

**Ten pools are dead**: no rolling container draws from them. Eleven registry
items are unreachable (#133).

**A premise from the issue that turned out false, so the report must not be built
around it:**

- Every tag in `REPORTED_TOOL_TAGS` (5291) has at least one hand-placed instance.
  Checked by running `ashfallDev.validateReachability()` at v0.6.0.
- Hand-placed contents don't depend on the seed.
- So **today no seed can be missing a tool tag**, and the per-seed tag check will
  read "present" for every tag in every seed. It is still built, because it
  becomes informative the moment hand-placed tools are thinned (#133) or a start
  without them exists (#137). The value today is the manifest and the sampler's
  hit-rate check.

**The dev seam** (6501):

```js
window.ashfallDev = { validateItemRegistry, validateLocations, validateRoomSchema, validateReachability };
```

Its comment states the rule this pass must keep: "read-only reporting helpers,
nothing that writes game state".

## Rules / mechanics

### 1. The roll core takes an explicit seed

- **`hashKey` takes the seed as an argument** instead of reading `state.seed`.
- **There is one explicit-seed core**, for example `rollValueFor(seed, parts)`, and
  `rollValue(...parts)` becomes `rollValueFor(state.seed, parts)`.
- **`chance(p, ...keyParts)` keeps its signature and stays the game's API.** Its
  explicit-seed sibling (e.g. `chanceFor(seed, p, keyParts)`) holds the
  warn-and-clamp legality check, and `chance()` delegates to it. The check must
  exist in exactly one place.
- **`randInt` gets the same treatment**, e.g. `randIntFor(seed, min, max, keyParts)`
  with `randInt()` delegating.
- **`doFish()` and `doConsume()` are not edited.** They keep calling `chance()`.
- **Never read or write `state.seed` to evaluate another seed**, not even
  temporarily with a restore. The seam is read-only by rule, and a
  swap-and-restore can leave the wrong seed in place if anything between the two
  throws.

### 2. Loot evaluation is per pool, and the key shape is written once

- **Split `rolledLootFor()`'s pool loop body into a per-pool function**, e.g.
  `rolledPoolFor(seed, roomId, containerId, poolId)`. It returns
  `{ empty, items }`:
  - `empty` is the result of the pool's empty gate;
  - `items` is the list of `itemFromRegistry()` stacks that hit, in declaration
    order.
- **`rolledLootFor(seed, roomId, container)` concatenates `rolledPoolFor()`** over
  `container.spawnPools`, in their order. An unknown pool id still contributes
  nothing.
- **`doOpenContainer()` passes `state.seed` explicitly.** It is the only game
  caller.
- **The three loot key shapes live only inside `rolledPoolFor()`.** The sampler
  must get entry-level hits by calling it, never by rebuilding the keys itself. A
  key shape written twice is the "one source of truth" violation the project
  rules forbid.

### 3. One definition of "a container that still rolls"

- **Extract a helper**, e.g. `rollingContainers(world)`, returning
  `[{ roomId, container }]` for every container (including car containers) with
  `spawnPools && !spawnRolled`.
- **`validateReachability()` uses it** to build `livePools`, and its report must
  stay byte-identical to v0.6.0's.
- **`simulateSeed()` and `sampleSeeds()` use it too.**

### 4. `simulateSeed(seed)`

**Seed argument:**
- a number → `seed >>> 0`;
- a string → `seedFromInput(seed)`, so a typed word gives exactly the world
  Restart would give it;
- omitted → `state.seed`, the current run. This is the helper's only read of game
  state.

**The world it reads:**
- Builds `makeDefaultWorld()` once. It never reads the live `world`, because a
  played world has already rolled and moved things.
- For the starting inventory, uses `makeDefaultState(seed)` so no `Math.random()`
  is drawn.

**Rows it produces**, one per item stack:

| field | value |
|---|---|
| `roomId` | the room, or `"(start)"` for the starting state's inventory and slots |
| `place` | `"floor"`, a container `id`, or a slot key |
| `source` | `"hand-placed"` or `"rolled"` |
| `itemId` | the item |
| `qty` | the stack's quantity |

- **Hand-placed rows** cover every floor, every container's authored `items`,
  every car container, and the starting state's inventory and slots.
- **Rolled rows** are `rolledLootFor(seed, roomId, container)` for each rolling
  container. A rolling container's own authored `items` array is empty today; if
  it ever isn't, those items are hand-placed rows.

**Tag summary.** For each tag in `REPORTED_TOOL_TAGS`, the number of stacks
carrying it (hand-placed plus rolled). Count stacks, not units, which is the same
convention `validateReachability()`'s `placed` count uses, so the two reports
compare directly.

**Output:**
- `console.table()` the rows;
- `console.log()` one line per tag;
- return `{ seed, rows, tags }`.

### 5. `sampleSeeds(n = 1000, start = 0)`

- **Seeds** are `start … start + n − 1`, each `>>> 0`. Deterministic, so a report
  can be reproduced exactly.
- **Build the fresh world once** and reuse it for every seed. It is safe to share
  because every function evaluated is pure.

**What it reports**, over every `(rolling container, pool)` pair and every seed:

1. **Per pool entry.**
   - `trials`: the number of (container, seed) pairs whose container draws that
     pool.
   - `hits`: how many of those contained the entry's `itemId` in
     `rolledPoolFor(…).items`.
   - `observed` = `hits / trials`.
   - `expected` = `(1 − emptyChance) × chance`.
2. **Per pool empty gate.** `observed` empty rate against `emptyChance`, over the
   same trials.
3. **Per item.** The fraction of seeds in which the item appears anywhere in the
   seed's world, as `simulateSeed()` would list it. Hand-placed items read `1`.
   Unreachable items read `0`. This is the #133 instrument ("in 1000 seeds,
   X appeared in N").
4. **Per tag.** The fraction of seeds in which the tag's stack count is 0. It
   reads `0` for every tag today (see Relevant existing state).

**Flagging**, for rows 1 and 2:
- A row is flagged when
  `|observed − expected| > SAMPLE_TOLERANCE_SIGMA × sqrt(expected × (1 − expected) / trials)`.
- `SAMPLE_TOLERANCE_SIGMA = 3`. It is a named constant beside the helpers, a
  judgment call, retunable.
- At 3σ across roughly 200 comparisons, one chance flag in a clean run is
  expected. A flag is a prompt to rerun with a larger `n` or another `start`, not
  a verdict. The helper's comment must say so.

**Dead pools** have `trials: 0`. List them as not rolled, never as flagged.

**Output:**
- `console.warn()` the flagged rows if there are any;
- `console.log()` a one-line summary (`n`, `start`, rows compared, rows flagged);
- return `{ n, start, entries, pools, items, tags }`.

### 6. Seam and comments

- **Add both helpers to `window.ashfallDev`.** The seam's comment currently says
  "The four validators above". It becomes the six helpers, and the read-only rule
  stays stated.
- **Rewrite `rolledLootFor()`'s comment line** "That last property is what lets a
  seed be evaluated without playing it (#150)." Name `simulateSeed()` instead of
  an issue number. Comments carry intent, not tracker references.
- **Give the new helpers a comment block** in the style of the four validators:
  dev-only, not wired to UI, runs nothing automatically, how to call it.
- **Place them in PERSISTENCE** beside `validateReachability()`, where the other
  dev helpers live.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

- **Names** of the explicit-seed core and siblings (`rollValueFor`/`chanceFor`/
  `randIntFor`, `rolledPoolFor`, `rollingContainers`). The names above are
  suggestions; the shapes are the spec.
- **Argument order** of the explicit-seed functions. Recommended: seed first,
  matching `rolledLootFor(seed, …)`.
- **Exact row field names** in the returned report objects, as long as each
  carries the quantities listed above.

None of these moves the version type.

## Data / schema changes

None. No state field, no item or room field, no save change. `SAVE_KEY` does not
move.

## In scope

- The explicit-seed roll core (Rules 1).
- The `rolledPoolFor()` / `rolledLootFor()` split (Rules 2).
- The `rollingContainers()` extraction, with `validateReachability()` rewired
  onto it (Rules 3).
- `simulateSeed()` and `sampleSeeds()` (Rules 4, 5).
- The seam entry and the comment updates (Rules 6).

## Explicitly out of scope

- **Anything that answers "can the player get to it".** Locked doors
  (`1b`, `2b`, `1a`), locked storage units (`breakTag:"cutting"`), breakable
  windows, `searchLabel` rooms. Existence only, by Tom's decision.
- **#133**, fixing the dead pools and unreachable items. This pass only measures
  them.
- **Quantity-distribution checks** (whether `qtyMin…qtyMax` draws are uniform).
  Not asked for.
- **#15** (respawn), **#149** (run options, benched), **#10** (skill checks).
- **`validateReachability()`'s own report.** It must not change. Its comment line
  "Ten dead pools and twelve unreachable items are the expected output at v0.5.1"
  is out of date (eleven), but it is not this pass's to edit.
- **Any UI.** Console only.

## Sections touched

- **CORE UTILITIES**: the roll core's explicit seed.
- **WORLD INTERACTION**: `rolledLootFor()` split, `rolledPoolFor()`,
  `doOpenContainer()`'s call.
- **PERSISTENCE**: `rollingContainers()`, `validateReachability()` rewired,
  `simulateSeed()`, `sampleSeeds()`.
- **The dev seam** at the foot of the script.
- **CONFIG / CONSTANTS**: `GAME_CONFIG.VERSION` only.

No WORLD DATA. No ACTIONS other than `doOpenContainer()`'s argument. No
RENDERING.

## UI changes

None.

## Validation to perform

**Bit-identical rolls.** Use a copy of the file with internals exposed, not
committed, as v0.6.0's validation did. For seeds `0 … 199`, every rolling
container's yield must be identical between v0.6.0 and this build:
- compare v0.6.0's `rolledLootFor(roomId, container)` under `state.seed = s`
  against this build's `rolledLootFor(s, roomId, container)`;
- compare every `rollValue()` for the fishing and illness key shapes the same way.

**The manifest matches play.** Start a run, note its seed, and open all 24
rolling containers in-game. Their contents must equal `simulateSeed()`'s rolled
rows for that seed. Also check that `simulateSeed("some word")` equals
`simulateSeed(seedFromInput("some word"))`.

**The helpers are read-only.** Call `simulateSeed()` and `sampleSeeds()` with a
save loaded. `JSON.stringify` of `state`, `world`, `doors` and `windows` must be
identical before and after.

**`validateReachability()` is unchanged.** Its output is byte-identical to
v0.6.0's.

**The sampler agrees with the arithmetic.** `sampleSeeds()` at defaults: record
how many rows were compared and flagged. Expect zero or one chance flags. For
comparison, v0.6.0's validation measured `bottled_water` in
`kitchen_nonperishable` at 0.172 against the expected 0.174 over 20,000 seeds.
Record the runtime of `sampleSeeds(1000)`.

**The chance legality check is still in one place.** Grep for the warn-and-clamp;
it appears exactly once.

## Dependencies / issue linkage

**Fulfils #150.**

**Unblocks measurement for:**
- **#133**, which can now quote seed frequencies;
- **#149**'s loot-availability option, whenever #149 comes off the bench.

Nothing is expected to be deferred. If `sampleSeeds()` flags a pool entry that
stays flagged across a rerun with a different `start` and a larger `n`, that is
a real finding about the derived `chance` figures. File it as a new issue and do
not retune anything in this pass.

**Sibling handoffs** written in the same planning session:
`handoffs/2a-door-both-ways.md` (#145) and `handoffs/stowed-bag-contents.md`
(#153 + #156). All three were checked against v0.6.0 and **touch no common
line**:
- This one edits the roll core, `rolledLootFor()`, `doOpenContainer()`, and
  `validateReachability()` with the new helpers beside it.
- The bag handoff edits `resyncUidCounter()`, `backfillItemIds()` and
  `backfillIllnessScale()`, which are also in PERSISTENCE but are different
  functions. Its new walker sits beside `resyncUidCounter()`, not beside
  `validateReachability()`. Whichever ships second may meet a nearby hunk, but no
  shared line.

They can ship in any order.

## Open questions for Tom

None. Scope (existence only) and tier (`tier-1`, PATCH) were Tom's decisions.

## After implementation

Open a pull request carrying the version bump and a new `CHANGELOG.md` entry per
`CHANGELOG_GUIDE.md` that names this handoff by path and records the Design
decisions above. `git mv` this file to `handoffs/archive/` in the same pull
request, and put `Closes #150` in the description.
