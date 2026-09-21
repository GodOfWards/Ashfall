# Ashfall Handoff — Spawn probability model

Current shipped version: v0.5.0
Implied version-change type: PATCH
Issue: #127 — Spawn pools express relative weight, not likelihood — the model
doesn't compose as the world grows

## What this is

`SPAWN_POOLS` is a weighted lottery. A pool entry's `weight` is, per the
existing comment, a "plain relative integer, no sum constraint" — so no entry
states how likely that item is to be in a container, and no author can set two
items' likelihoods independently.

This pass replaces the lottery with an **independent per-entry chance**, and
converts the existing pools at measured equivalence so that no balance decision
hides inside a mechanics change. It does not re-author any pool for realism —
that is the balance pass that follows, and it is what closes #66 and #67.

The tier mapping in the Handoff Guide, Part 1 would make a `tier-2` issue a
MINOR. **This is a PATCH**, deliberately: `SPAWN_POOLS` is a code constant and
this pass adds no field to anything that is serialized, so `versionCompat()`
does not move and existing browser saves keep loading. Say so in the changelog's
Notes/assumptions rather than letting the mismatch read as an error.

## Relevant existing state

Verified by reading `ashfall.html` at `main`, v0.5.0 — not recalled.

**The roll**, in `doOpenContainer()` (WORLD INTERACTION):

```js
if(container.spawnPools && !container.spawnRolled){
  container.spawnPools.forEach(poolId=>{
    const pool = SPAWN_POOLS[poolId];
    if(!pool) return;
    if(Math.random() < pool.emptyChance) return;
    const rollCount = randInt(pool.rollCount[0], pool.rollCount[1]);
    for(let i=0; i<rollCount; i++){
      const entry = weightedPick(pool.entries);
      const qty = randInt(entry.qtyMin, entry.qtyMax);
      addToList(container.items, itemFromRegistry({ id:entry.itemId, qty }));
    }
  });
  container.spawnRolled = true;
  container.lastRolledMinute = state.totalMinutes;
}
```

Facts this pass depends on:

- **28 pools**, 24 containers with `spawnPools && !spawnRolled` (which roll), 50
  with `spawnRolled:true` at authoring (which never do), 6 car containers with
  no `spawnPools` at all. 218 rooms, 153 registry items.
- **`weightedPick()`** (CORE UTILITIES) is used by nothing else. After this pass
  it has no callers.
- **`randInt()`** (CORE UTILITIES) stays — the quantity draw still uses it.
- **Picks are made with replacement**, so one roll can select the same entry
  more than once; `addToList()` then merges the results into one stack.
- **`addToList()` appends.** The roll never clears `container.items`, so
  `spawnRolled:true` at authoring prevents hand-placed contents being *topped
  up*, not overwritten. The CONTAINER SCHEMA comment's stated rationale ("so
  `doOpenContainer()` never overwrites them") is wrong about the mechanism and
  should be corrected while this pass is in the file.
- **`backfillContainerFields()`** (PERSISTENCE) copies `spawnPools` and
  `spawnRolled` from a freshly-built default world onto loaded containers. It
  reads neither `weight` nor `rollCount`, so it needs **no change**.
- **`lastRolledMinute`** is written and read by nothing. It stays as-is,
  reserved for #15.
- **Dev-only console helpers** live at the end of PERSISTENCE:
  `validateItemRegistry()`, `validateLocations()`, `validateRoomSchema()`. All
  three return an array of problem strings, empty on success, and
  `console.warn`/`console.log` a summary. The new helper is a fourth sibling and
  follows that shape exactly.

## Rules / mechanics

### The new roll

Each entry in each of the container's pools is rolled **once, independently**.
`emptyChance` is retained as a per-pool gate ahead of the entries.

```
for each poolId in container.spawnPools:
    pool = SPAWN_POOLS[poolId]
    if pool is undefined: skip            (unchanged defensive guard)
    if random() < pool.emptyChance: skip  (unchanged)
    for each entry in pool.entries:
        if random() < entry.chance:
            qty = randInt(entry.qtyMin, entry.qtyMax)
            addToList(container.items, itemFromRegistry({ id:entry.itemId, qty }))
```

Entries are rolled in declaration order, so items land in the container in the
order the pool lists them. `rollCount` and `weight` are removed from the schema;
`emptyChance`, `qtyMin` and `qtyMax` keep their current meanings exactly.

An entry can now contribute **at most one stack per roll**. This is the one
intended behaviour change — see below.

### `chance` is conditional

Because `emptyChance` survives as its own gate, `entry.chance` is the
probability that the entry appears **given the pool did not come up empty**.
The unconditional probability of an item appearing in a container is therefore:

```
P(appears) = (1 - pool.emptyChance) * entry.chance
```

State this in the SPAWN_POOLS comment. An author reading `chance: 0.55` in a
pool with `emptyChance: 0.25` must not mistake it for 55% of containers.

### The conversion

Every existing entry's `chance` is **derived, not chosen**, from the pool it is
currently in. For an entry of weight `w` in a pool whose entry weights sum to
`W` and whose `rollCount` is `[a, b]`:

```
chance = mean over k in {a, a+1, …, b} of [ 1 - (1 - w/W)^k ]
```

That is the probability the entry is picked at least once in `k`
with-replacement draws, averaged over the uniform `rollCount`. Multiplying by
`(1 - emptyChance)` recovers today's unconditional probability exactly, which is
why `emptyChance` is carried across unchanged rather than folded in.

Where `a` is 0, the `k = 0` term contributes 0 and is included in the mean —
the "rolled zero times" case is correctly absorbed into `chance`, and
`emptyChance` stays exactly as authored.

**Generate the table programmatically from the pre-change `SPAWN_POOLS`.** Do
not transcribe ~200 numbers by hand and do not round them to something
tidier-looking: a tidy number is a balance decision, and this pass must not
contain one. Six decimal places.

The numbers will look arbitrary — `0.245069`, not `0.25`. That is the point.
An ugly derived number is the signal to the balance pass that nobody has chosen
it yet.

#### Reference vectors

Verify the implementation against these before converting the rest. All values
computed from the shipped v0.5.0 pool definitions.

`kitchen_tools` — `rollCount:[0,2]`, `emptyChance:0.25`:

| entry | weight | `chance` | P(appears) |
|---|---|---|---|
| `can_opener` | 7 | 0.245069 | 0.183802 |
| `frying_pan` | 6 | 0.213018 | 0.159763 |
| `kitchen_knife` | 6 | 0.213018 | 0.159763 |
| `dented_saucepan` | 4 | 0.145957 | 0.109467 |
| `burnt_saucepan` | 3 | 0.110947 | 0.083210 |

`fuel_fire` — `rollCount:[1,2]`, `emptyChance:0.15`:

| entry | weight | `chance` | P(appears) |
|---|---|---|---|
| `firewood` | 8 | 0.498866 | 0.424036 |
| `box_of_matches` | 6 | 0.387755 | 0.329592 |
| `lighter` | 5 | 0.328798 | 0.279478 |
| `campfire_kit` | 2 | 0.138322 | 0.117574 |

`police_evidence` — `rollCount:[0,1]`, `emptyChance:0.4` (the degenerate case,
where `chance` is just `w/W`):

| entry | weight | `chance` | P(appears) |
|---|---|---|---|
| `evidence_bag` | 6 | 0.333333 | 0.200000 |
| `sealed_evidence_box` | 3 | 0.166667 | 0.100000 |

### The intended behaviour change

P(appears) is preserved exactly for every entry. **Quantity is not, and cannot
be.** The old model's duplicate picks have no counterpart in a model that rolls
each entry once.

- `retail_stock_food` makes 1.800 picks per roll but yields only 1.633 distinct
  items; the 0.167 gap is duplicate mass, and it is what disappears.
- Expected item *units* fall **6.6%** across all 28 pools. The five largest
  drops: `retail_stock_food` 2.74 → 2.48, `hardware_store` 2.36 → 2.16,
  `fuel_fire` 1.76 → 1.57, `kitchen_nonperishable` 2.51 → 2.38,
  `warehouse_goods` 1.51 → 1.39.
- Across the 24 containers that actually roll today, a whole run loses **3.3
  expected item units** (59.0 → 55.7).

This was weighed and accepted during planning. Do **not** compensate for it —
not by scaling the chances (which would break the P(appears) the conversion
exists to preserve) and not by raising `qtyMax` (which would hand-tune ~30
entries by feel). Both would destroy the re-derivability that makes this diff
checkable, to protect numbers the balance pass will overwrite.

The changelog must state this plainly: **this is not a no-behaviour-change
pass.** Probability of appearance preserved exactly; quantity distribution
deliberately changed; large lucky stacks get shorter and the "three can openers
in one drawer" case is gone.

### The reachability helper

A fourth dev-only console helper, sibling to the three named above, in the same
block at the end of PERSISTENCE. Not wired to any button and nothing calls it
automatically. Returns an array of problem strings, empty on success.

It reports three things, against a **freshly-built default world** (a live save
has mutated `spawnRolled`, so the running `world` would give the wrong answer):

1. **Dead pools** — every `SPAWN_POOLS` id that no container with
   `spawnPools && !spawnRolled` draws from. At v0.5.0 this is ten:
   `medical_otc`, `medical_pharmacy`, `recreation`, `tools_general`,
   `retail_stock_food`, `retail_stock_general`, `hardware_store`,
   `outdoor_camping`, `trash`, `fuel_fire`.
2. **Unreachable items** — every `ITEM_REGISTRY` id that is not hand-placed in
   the default world (room floors, containers, car containers, the starting
   keychain), not an entry in a live pool, not a `RECIPES`/`HEAT_RECIPES`
   output, and not granted by an action. At v0.5.0 this is twelve: `lighter`,
   `water_purification_tablets`, `compass`, `antibiotics`, `antiseptic_wipes`,
   `cough_syrup`, `vitamins`, `candy_bar`, `chewing_gum`, `paint_can`,
   `playing_cards`, `comic_book`.
3. **Reachable tool count per gated tag** — for each tag the game gates an
   action on, how many reachable instances carry it, so a content pass can see
   when a verb is down to one item. At v0.5.0: `fire-starter` 1, `fishing` 1,
   `tackle` 1 (none of the three obtainable from any live pool), `prying` 2
   (also no live pool), `chopping` and `cutting` 1 hand-placed each plus
   `tools_workshop`, `blunt` 10, `can-opening` 5.

Two lists have to be written down because they cannot be derived at runtime,
and both should be named constants beside the helper rather than inline
literals, so they are visible and maintainable:

- **Action-granted items** — items an action produces rather than a container
  holding them: `firewood` (`doChopTree()`, `doDismantleCampfire()`, campfire
  kit Disassemble), `raw_fish` (`doFish()`), `spare_batteries` (Remove
  batteries).
- **Gated tags** — the tags `hasTool()` / `hasMatchUses()` are called with:
  `fire-starter`, `fishing`, `tackle`, `chopping`, `cutting`, `blunt`,
  `can-opening`, plus `heat` (whose only reader is `canCraft()`'s `needsHeat`
  branch, which no recipe sets) and the `breakTag` values carried by windows and
  locked containers.

It should also flag any entry whose `chance` is not a finite number in `(0, 1]`
— a cheap authoring guard the old `weight` could not have, since any positive
integer was legal.

The helper reports the current state; it does not assert that the state is
good. Ten dead pools and twelve unreachable items are expected output at the
moment this ships, and the balance pass is what drives them to zero.

## Design decisions to make during implementation

Narrow calls. Record which was taken in the changelog's Notes/assumptions.

1. **Whether `weightedPick()` is deleted or kept.** It has no other caller once
   the roll changes. Recommended: **delete it**, and say so in the changelog's
   Removed section — a helper with no callers is vestigial surface, which
   v0.4.14 already established as worth removing rather than carrying. Keeping
   it would need a reason stated in a comment.
2. **Where the conversion script lives.** It is scaffolding, not shipped code —
   it runs once against the pre-change file to generate the table. Recommended:
   it does not enter the repository at all, and the changelog records the
   formula (which is in this handoff) as the reproduction method. Do not leave
   it in `ashfall.html`.
3. **The helper's name.** `validateItemRegistry()`, `validateLocations()` and
   `validateRoomSchema()` are the existing pattern. Something in that family —
   the thing it validates is reachability, not a schema.
4. **Whether the three reports are one helper or three.** Recommended: **one**,
   returning one combined problem list. They share the "walk the default world
   and work out what rolls" computation, and splitting them would do it three
   times. Three separate reports inside one function is fine.

## Data / schema changes

**`SPAWN_POOLS` entry schema** (WORLD DATA):

- **Removed:** `weight` (per entry), `rollCount` (per pool).
- **Added:** `chance` (per entry) — a number in `(0, 1]`, the probability this
  entry appears given the pool did not come up empty.
- **Unchanged:** `emptyChance` (per pool), `qtyMin`/`qtyMax` (per entry).

No PLAYER STATE fields. No ITEM DATA SCHEMA fields. No ROOM/CONTAINER/EXIT
schema fields — `spawnPools`, `spawnRolled` and `lastRolledMinute` are all
untouched, which is what keeps this a PATCH.

**Comments to rewrite** (both in WORLD DATA):

- The `SPAWN_POOLS` block comment — `weight` and `rollCount` descriptions
  replaced by `chance`, with the `P(appears) = (1 - emptyChance) * chance`
  relationship stated, and the note that entries are independent. Its pointer
  to "the v0.4.0 entry in CHANGELOG.md for the full design" should point at this
  pass's entry instead, or be dropped — the v0.4.0 design is no longer the
  model in the file.
- The CONTAINER SCHEMA's `spawnRolled` description — correct the "never
  overwrites them" rationale to what actually happens (the roll appends; the
  flag prevents hand-placed contents being topped up).

## In scope

- Rewrite the roll in `doOpenContainer()` per **The new roll** above.
- Convert all 28 pools to `chance` at measured equivalence, generated
  programmatically, verified against the reference vectors.
- Remove `weight` and `rollCount` from every pool; keep `emptyChance`,
  `qtyMin`, `qtyMax`.
- Resolve design decision 1 (`weightedPick()`).
- Add the reachability helper.
- Rewrite the two comments named above.
- `GAME_CONFIG.VERSION` PATCH bump.

## Explicitly out of scope

- **Re-authoring any pool's numbers for realism.** Every `chance` this pass
  writes is derived. The balance pass is what replaces them with chosen ones,
  and it is what closes #66 and #67. Changing even one number here would mean
  the diff can no longer be verified by re-derivation.
- **Pool membership.** No container gains or loses a `spawnPools` entry, and no
  pool gains or loses an item. Matches do not enter `kitchen_tools` in this
  pass, however obviously they belong there.
- **Unfreezing containers (#66).** No `spawnRolled` value changes. The ten dead
  pools stay dead and the helper reports them; that is the intended output.
- **Second copies of single-source tools (#67).** Single-sourcing has been
  settled as *not* the intent, but the fix is a content decision for the
  balance pass.
- **Container kinds (#128).** Container definitions are not touched at all.
- **Respawn (#15).** `lastRolledMinute` stays unread. A per-entry chance makes
  respawn easier to express later; nothing here acts on that.
- **A shared roll core (#51).** This pass keeps using `Math.random()` directly,
  as the rest of the file does. Folding spawn rolls into a common core is #51's
  ground, and doing it here would widen a mechanics change into a second one.
- **New registry items.** The household objects a realistic kitchen wants
  (sponge, plates, cutlery, mugs, candles) do not exist in `ITEM_REGISTRY`.
  That is instance content and cannot ride a mechanics change.
- **#116 tool wear, #124 item state in the list, #126 spent fire-starters.**
  Adjacent to the reachability findings, none of them touched here.

## Sections touched

- **WORLD DATA** — `SPAWN_POOLS` (every pool), its block comment, and the
  CONTAINER SCHEMA comment's `spawnRolled` paragraph.
- **WORLD INTERACTION** — `doOpenContainer()`.
- **CORE UTILITIES** — `weightedPick()`, per design decision 1.
- **PERSISTENCE** — the dev-helper block at the end, for the new helper.

Nothing in PLAYER STATE, INVENTORY / ITEM SYSTEM, SURVIVAL / TIME SIMULATION,
STAMINA / FATIGUE, CRAFTING, FIRE / COOKING, EVENTS, RENDERING or MAP.

This is the "definition data rides along with its mechanic" case the Project
Guide bounds: `chance` is the new rule's own schema field, the same shape as
`restores`/`verb` shipping with `doConsume()`. No room, placement, description
or map coordinate changes, which is the bound holding.

## UI changes

None. No button, panel, label or log line changes. The only player-visible
consequence is statistical: slightly fewer items overall, and no more
same-item duplicate picks within one container's roll.

## Dependencies / issue linkage

- **Fulfils #127.** The pull request carries `Closes #127`.
- **Unblocks #66 and #67** — both become answerable once a pool can state a
  likelihood. Neither is closed by this pass; the balance pass that re-authors
  the pools closes them.
- **#128** (container kinds) is sequenced after this, so it rewrites container
  definitions once against a settled model.
- **#51** (a roll core) should be checked against this before it hardens — this
  is a second system choosing its own RNG shape.
- **Expected to leave deferred:** nothing new beyond what is already filed. If
  the conversion turns up a pool whose numbers cannot be derived cleanly (an
  entry with weight 0, a pool with an empty `entries` array — neither exists at
  v0.5.0), file it rather than choosing a number.

## Open questions for Tom

None. Four decisions were settled during planning and are recorded above as
spec rather than as questions: independent per-entry chance over weights;
`emptyChance` retained as its own gate; conversion at measured equivalence with
the 6.6% unit drop accepted and explicitly not compensated; the reachability
helper rides along with this pass rather than the balance pass.

## After implementation

Open a pull request carrying the PATCH version bump and a new `CHANGELOG.md`
entry per `docs/CHANGELOG_GUIDE.md`, naming this handoff by the path it was read
at, recording the design decisions resolved above, and closing #127 with
`Closes #127`. Move this file to `handoffs/archive/` in the same pull request
(`git mv`, filename unchanged). Tag the merge commit, naming it explicitly.

**Validation this pass specifically needs**, beyond the usual diff and syntax
check:

- **Re-derive the table.** Recompute every `chance` from the pre-change pool
  definitions with the formula above and confirm it matches what shipped, to
  six decimal places. This is the proof that no balance decision entered.
- **Simulate both models.** For each pool, Monte-Carlo the old roll and the new
  one and confirm P(appears) agrees per entry within sampling error. Planning
  ran this at 200,000 trials per pool against the shipped v0.5.0 arithmetic and
  saw a maximum deviation of 0.00209.
- **Confirm the unit drop lands where predicted** — the five pools named above,
  and −6.6% overall.
- **Run the new helper** on a fresh world and confirm it reports the ten pools,
  the twelve items and the per-tag counts listed above. Those numbers were
  verified against v0.5.0 during planning and are the helper's acceptance test.
- **Save compatibility.** A save written before this pass loads afterwards, and
  `localStorage` still carries `ashfall_save_v0.5`.
