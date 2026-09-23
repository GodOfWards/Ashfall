# Ashfall Handoff — A stowed bag's contents: counted at load, and counted as weight

Current shipped version: v0.6.0
Implied version-change type: PATCH
Issues: #153 — Load-time scans skip an unequipped bag's `contents` — resyncUidCounter() can hand out a uid already in use
        #156 — A stowed bag weighs only itself — its `contents` count toward no capacity anywhere

## What this is

When a bag is unequipped, what it held moves into the bag item's `contents`
array. Two parts of the file never look inside that array, and this pass fixes
both. They share one fact: **an item can hold a list of items, to any depth.**

1. **#153, load.** `resyncUidCounter()` and `backfillItemIds()` never descend into
   `contents`. After a load, `_uidCounter` can end up at or below a `_uid` still in
   use inside a stowed bag. New items then reuse it, and re-equipping the bag
   leaves two live items sharing one uid. Fix: one shared walker over every item
   list, nested contents included, used by every load-time scan.
2. **#156, weight.** `totalWeight()` counts `qty × unitWeight`, and a stowed bag's
   `unitWeight` is the empty bag's. A full 18 kg duffel sits in the 3 kg base
   inventory as 0.8 kg, and bags nest. Fix: an item weighs its own `unitWeight`
   plus the weight of its `contents`, recursively, everywhere weight is read.

Tom's decisions (planning session at v0.6.0):

- **Bags may nest inside other containers.** What a stowed bag holds stays out of
  reach until the bag is dropped or equipped. Only equipping exists today;
  dropping is #169.
- **Unequipping a loaded bag that doesn't fit the base inventory goes over the
  cap.** It is not refused and not dropped. The readout shows the true figure,
  e.g. `18.80 / 3 kg`, and nothing more fits into that pool until it is back
  under.
- **A save already over cap after this change is left over cap.** No load-time
  repair moves anything.
- **Bundle #153 and #156** into this one pass.

## Relevant existing state

Verified against `ashfall.html` at v0.6.0. Line numbers are that file's.

**Where `contents` comes from and goes to.**

- `doUnequip()` (4179) builds the item from the registry and attaches
  `contents: slot.items`. It then calls `addToList(state.inventory.items, item)`
  **with no capacity check.** That existing behaviour is what "goes over the cap"
  means, and it stays.
- `doEquip()` makes `it.contents || []` the new slot's `items`.
- `addToList()` deep-clones with `JSON.parse(JSON.stringify(item))`, so a moved
  bag carries its contents, uids and all, and no two lists ever share an array.
  **A cycle is impossible**: a bag's contents is a cloned tree, and an equipped
  bag is a slot, not an item in any list, so it can't be stored inside itself.
- Nesting is reachable today:
  1. put a stowed purse (with contents) into an equipped duffel's tab;
  2. unequip the duffel.

  The purse, with its contents, is now inside the duffel item's `contents`.

**The load-time scans.** `applyLoadedData()` runs, in order (5195–5201):
`resyncUidCounter()`, `backfillItemIds()`, `backfillSlotItemIds()`,
`backfillLocationIds()`, `backfillContainerFields()`, `backfillRoomAddresses()`,
`backfillIllnessScale()`.

Three of them walk item lists, and each builds its own walk:

| function | line | walks | descends into `contents`? |
|---|---|---|---|
| `resyncUidCounter()` | 4961 | `invPools()` + every room's `floor`, `containers[].items`, `carContainers[].items` | **no** |
| `backfillItemIds()` | 4984 | same | **no** |
| `backfillIllnessScale()` | 5140 | same | yes, via its own recursion (5146) |

`backfillSlotItemIds()` walks slot objects, not item lists, and is not affected.

`findItemByUid()` doesn't descend into `contents`, and that is correct: nothing
inside a stowed bag appears in any panel. **It is not changed here.** (#169 will
need it to search floor bags. That is recorded on #169.)

**Every place weight is read.**

- `totalWeight(list)` (3899): `list.reduce((s,it)=> s + it.qty*it.unitWeight, 0)`.
  Called by:
  - `addToDestination()` (4012)
  - `giveItem()` (4021)
  - `doStore()` (4096)
  - `renderInventoryPanel()` (6409)
  - `renderWorldItemsPanel()` (6442)
- Inline `qty × unitWeight` products that bypass `totalWeight()`:
  - `addToDestination()` 4011: `item.qty * item.unitWeight`
  - `giveItem()` 4020: `item.qty * item.unitWeight`
  - `doStore()` 4096: `moveQty*it.unitWeight`
  - `renderItemList()` 6116: the per-row `(it.qty * it.unitWeight).toFixed(2)`
  - `renderCraftPanel()` 6175: the detail view's `(it.qty*it.unitWeight).toFixed(2)`
  - `renderCraftPanel()` 6178: the detail view's `(${it.unitWeight.toFixed(2)} kg each)`

**Bags never stack.** Every bag is `category:"Container"`, which is not in
`STACKABLE`, so a bag row always has `qty:1`.

## Rules / mechanics

### A. One walker over every item list (#153)

- **One function visits every item array reachable from the current `state` and
  `world`:**
  - each list in `invPools()`;
  - each room's `floor`;
  - each room's `containers[].items` and `carContainers[].items`;
  - recursively, the `contents` of every item in any visited list, to any depth.
    Visit a `contents` only when `Array.isArray(it.contents)`, the guard
    `backfillIllnessScale()` already uses. Skip `null`/non-object entries the way
    the existing scans do.
- **It visits lists, not items**, e.g. `forEachItemList(visit)` calling
  `visit(list)`. Each caller keeps its own per-item logic.
- **`resyncUidCounter()`, `backfillItemIds()` and `backfillIllnessScale()` all use
  it** instead of their own walks. `backfillIllnessScale()`'s private recursion is
  removed; the walker's recursion replaces it.
- **It reads `state` and `world` at call time.** `applyLoadedData()` assigns both
  before any backfill runs, and that order is unchanged.
- **`applyLoadedData()`'s call order is unchanged.**

### B. Weight includes contents (#156)

- **Two helpers, defined once in INVENTORY / ITEM SYSTEM beside `totalWeight()`:**
  - an item's per-unit weight =
    `it.unitWeight + (Array.isArray(it.contents) ? totalWeight(it.contents) : 0)`
  - an item's weight = `it.qty × per-unit weight`
- **`totalWeight(list)`** sums the item weight. The recursion into nested bags
  goes through `totalWeight()` itself, so any depth is counted.
- **Every inline product in the table above** is replaced by the helpers.
  After this pass, no `qty * unitWeight` product may appear outside the helpers:
  grep for it.
- **The detail view's "kg each"** shows the per-unit helper, so a bag's line reads
  its loaded weight and `total = qty × each` holds on every row.
- **An item with no `contents` weighs exactly what it did before.** That is every
  item except a stowed bag.

### C. Capacity and over-cap, following Tom's decisions

- **`doUnequip()` is not given a capacity check.** A loaded bag always goes into
  the base inventory, even past its 3 kg. This is today's code path, and it must
  stay.
- **Over cap, the existing checks do the rest unchanged:**
  - `addToDestination()` refuses any addition, so Take shows "That won't fit — not
    enough room there.";
  - `giveItem()` falls through to the floor with its existing warning (a crafted
    item, a caught fish, removed batteries);
  - `doStore()` from the over-cap pool works, since moving weight *out* is never
    refused.
- **Floors and containers stay hard caps** at loaded weight:
  - `doStore()` of a loaded bag into a container or onto a floor is refused when
    the loaded weight doesn't fit;
  - `addToDestination()` refuses taking a loaded bag into a pool it doesn't fit.
  These are behaviour changes. The changelog must list them.
- **No load-time repair.** A save whose inventory is over cap after this change
  loads over cap and stays that way until the player lightens it.
- **Equipped slots are unchanged.** No total anywhere counts an equipped bag's own
  weight today, and that stays so. What an equipped bag weighs on the player is
  #168.

### D. Comments

- **The ITEM DATA SCHEMA's `contents` line (531)** gains: its items count toward
  the item's weight, and every load-time scan reaches them through the walker.
- **Beside the walker**, one short invariant comment: every scan over item lists
  goes through it, because a hand-rolled walk is how `contents` got missed.
  Carry intent, not history. No issue numbers or versions in comments.
- **`backfillIllnessScale()`'s comment** no longer says it is the only scan that
  descends into `contents`. Correct that sentence.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

- **Names.** Suggested: `forEachItemList()`, `itemUnitWeight()`, `itemWeight()`.
  The shapes above are the spec.
- **Where the walker lives.** Recommended: PERSISTENCE, beside
  `resyncUidCounter()`, since every caller is a load-time scan. INVENTORY / ITEM
  SYSTEM is acceptable if the implementation finds a reason, and the reason gets
  recorded.
- **Whether the walker also serves `validateReachability()`'s `placed` count.**
  Recommended **no**. That helper walks a fresh default world, which holds no
  `contents`, so its report cannot change either way. Leaving it alone keeps this
  pass off the function `handoffs/seed-report.md` edits.

None of these moves the version type.

## Data / schema changes

- No state field, no item field, no room field. `contents` is already persisted.
  `SAVE_KEY` does not move.
- The ITEM DATA SCHEMA comment for `contents` is updated (Rules D).

## In scope

- The shared walker, and the three load-time scans moved onto it (A).
- The two weight helpers, `totalWeight()` built on them, and all six inline
  products replaced (B).
- The comment updates (D).

## Explicitly out of scope

- **#168** (encumbrance and the equipped-bag carry bonus), **#170**
  (over-encumbrance penalties and a hard limit), **#169** (a floor bag as a Here
  tab, including `findItemByUid()` searching floor bags). This pass only makes
  weight true; those give it consequences.
- **Forbidding nesting.** Tom's decision is that bags may nest.
- **Any capacity number.** No bag's `capacityKg`, no `floorCap`, and not the base
  inventory's 3 kg.
- **A load-time repair for over-cap saves.**
- **`findItemByUid()`.**
- **#134** (per-unit durability in stacks). Unrelated: bags never stack.

## Sections touched

- **INVENTORY / ITEM SYSTEM**: `totalWeight()` and the two helpers;
  `addToDestination()`, `giveItem()`, `doStore()`'s weight reads.
- **PERSISTENCE**: the walker; `resyncUidCounter()`, `backfillItemIds()`,
  `backfillIllnessScale()`.
- **RENDERING**: `renderItemList()`'s row total; `renderCraftPanel()`'s detail
  weight and "each" figure. These are display of the same weight, not new state.
- **WORLD DATA**: the ITEM DATA SCHEMA comment only. No data.
- **CONFIG / CONSTANTS**: `GAME_CONFIG.VERSION` only.

## UI changes

No new string or control. Changed figures:

- **Inventory tab readout.** A stowed loaded bag now counts in full, and can read
  over cap (`18.80 / 3 kg`) after an unequip.
- **Here panel readout.** A loaded bag on the floor or in a container counts in
  full.
- **Item rows and the detail view.** A stowed bag shows its loaded weight, total
  and "each".
- **Existing warnings fire in new cases:**
  - "That won't fit — not enough room there." / "That won't fit there." when a
    loaded bag doesn't fit, or when anything is taken into an over-cap pool;
  - `giveItem()`'s floor-drop lines when the base inventory is over cap.

## Validation to perform

**The diff.** `git diff origin/main...HEAD -- ashfall.html` shows only the
functions named in Sections touched, plus `GAME_CONFIG.VERSION`.

**#153, the uid case.** Use a copy with internals exposed, not committed.
1. Equip a bag, open the detail view of two items in its tab so they get
   `_uid`s, then unequip it.
2. Export the save, reload the page, import it.
3. Assert `_uidCounter` exceeds every `_uid` anywhere, nested contents included.
4. Take new items, open their details, re-equip the bag, and confirm no two items
   share a `_uid`. Also run the issue's in-game reproduce steps.
5. Repeat with the bag nested inside a second stowed bag.

**#153, the backfills.** Build a save with a pre-registry item (no `itemId`) and a
pre-0.6 raw fish (`illnessChance:35`), each inside a stowed bag nested two deep.
After import, the item has its `itemId` and the fish reads `0.35`. Importing
again changes nothing.

**#156, weight.**
- Fill the duffel, unequip it: the inventory reads over 3 kg, Take into the
  inventory is refused, and crafting a bandage drops it to the floor with the
  existing warning.
- Store items out of the over-cap inventory: allowed.
- Try placing the loaded duffel on a `floorCap:20` mid-block floor that is
  already partly full: refused when it doesn't fit.
- Nest a loaded purse inside an equipped duffel: the duffel tab's readout counts
  the purse's contents.
- Every item row and detail view without `contents` shows the same figures as
  v0.6.0. Spot-check a stack, a durability item and an opened can.
- Grep: no `qty * unitWeight` / `qty*unitWeight` product outside the helpers.

**The validators.** `ashfallDev.validateRoomSchema()`, `validateLocations()`,
`validateItemRegistry()` and `validateReachability()` give output identical to
v0.6.0.

## Dependencies / issue linkage

**Fulfils #153 and #156.** Put both `Closes #153` and `Closes #156` in the pull
request.

**This is the prerequisite for:**
- **#169**: a floor bag's `floorCap` check needs loaded weight;
- **#168**: "full weight while stowed" needs loaded weight;
- **#170**: the over-cap state this pass makes reachable is its subject.

Nothing is expected to be deferred. If anything is, file it.

**Sibling handoffs** written in the same planning session:
`handoffs/2a-door-both-ways.md` (#145) and `handoffs/seed-report.md` (#150). All
three were checked against v0.6.0 and **touch no common line**:
- This one edits `totalWeight()` and the transfer functions, three load-time
  scans, and two RENDERING functions.
- The seed report edits the roll core, `rolledLootFor()`, `doOpenContainer()`,
  and `validateReachability()` with new helpers beside it. It shares PERSISTENCE
  with this pass but no function.
- The 2A handoff edits four WORLD DATA lines.

They can ship in any order.

## Open questions for Tom

None. Nesting, the unequip-over-cap behaviour, leaving old saves over cap, and the
bundling were all Tom's decisions.

## After implementation

Open one pull request carrying the version bump and a new `CHANGELOG.md` entry per
`CHANGELOG_GUIDE.md` that names this handoff by path, records the Design decisions
above, and lists the capacity behaviour changes under Changed / Reworked. `git mv` this file
to `handoffs/archive/` in the same pull request. The description carries
`Closes #153` and `Closes #156`.
