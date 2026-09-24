# Ashfall Handoff — Vessel water guards and vessel button labels

Current shipped version: v0.8.0
Implied version-change type: PATCH
Issue: #224 — Pour into a vessel that's already full of clean water empties the bottle for nothing
Issue: #223 — Vessel actions share a label when two vessels nearby share a name

## What this is

Two small fixes to the vessel actions the cooking release (v0.8.0) added,
both in the same loop of `getItemActions()`:

- **#224:** **Pour into the <vessel>** and **Fill at the sink** are offered
  when they can change nothing. Taking them wastes the bottle's water, or
  restarts a tainted vessel's boil.
- **#223:** two vessels with the same name nearby give two identical
  **Add to the <vessel>** / **Pour into the <vessel>** buttons, and the
  player can't tell which is which.

Both are `tier-0`, with no new state.

## Relevant existing state

Verified against `ashfall.html` at v0.8.0. Line numbers are left out on
purpose. Find each piece by its identifier.

- **Water on an item.** `it.water` is `{ kind, fill }` on a bottle
  (`holdsWater` entry) and `{ kind }` on a vessel, whose water is
  all-or-nothing (`vessel.waterKg` when present). An item with no water has
  no `water` field: drinking the last of a bottle and `doPourIntoVessel()`
  both `delete` it. `waterKindOf(it)` returns `"clean"`, `"tainted"` or
  `null`.
- **`holdsWaterAtAll(it)`** is true for a bottle, and for a vessel with
  `waterKg > 0` that holds no dish. It says nothing about whether the item
  is already full.
- **`addWater(unit, kind)`** fills to full. Any tainted water already
  there keeps it tainted, and it always runs `delete unit.boilMinutes`.
- **`canFillAtSink(it)`** excludes only an item full of **clean** water:
  `!(waterKindOf(it) === "clean" && (vesselDefOf(it) || it.water.fill === 1))`.
  So a vessel of tainted water is offered Fill at the sink. That only resets
  its boil, because the water stays tainted. A bottle full of tainted water
  is offered it and nothing changes. `doFillAtSink()` re-checks
  `canFillAtSink()`.
- **Pour into.** In `getItemActions()`, for a non-vessel item, it is offered
  on every vessel from `nearbyVessels()` when
  `it.water && holdsWaterAtAll(it) && holdsWaterAtAll(v)`. So a vessel that
  already holds water gets it too. `doPourIntoVessel()` re-checks only
  `bottle.water`, `holdsWaterAtAll(vessel)` and `vesselDefOf(vessel)`.
  Pouring into a boiling tainted vessel leaves it tainted and restarts its
  `BOIL_MINUTES` boil (#224's comment).
- **Add to.** It's offered in the same loop when
  `canAddToVessel(list, it, v)`. Capacity counts `totalWeight(v.contents)`
  plus the unit's weight against `capacityKg`. Water doesn't count.
- **Labels.** Both buttons use `v.name.toLowerCase()`, with no location.
- **`nearbyVessels()`** walks `nearbyLists()`, then the room's heat
  container (`getHeatContainer()`), and keeps each vessel once, in that
  order. `nearbyLists()` is `invPools()` (the inventory, then each
  equipped bag slot), then `room.floor`, then each
  `listedContainers(room)` entry's `items`. It does **not** reach inside
  floor bags. The heat container can be outside `listedContainers()` (an
  unsearched room), and it's still reached.
- **Here tab labels.** Floor is `"Floor"`. An authored or car container is
  `c.name`. No room at v0.8.0 has two containers with the same name, and
  none is named "Floor" (checked by loading the world in a browser). Floor
  bags are numbered ("Purse", "Purse 2"), but no vessel is reached inside
  one.
- **`rebuildKeepingFocus()`** restores focus by the button's text, then by
  position. Identical labels are why focus can land on the other
  saucepan's button (#223).

## Rules / mechanics

### 1. Can this item take more water (#224)

Add one predicate, used by both Fill at the sink and Pour into. It is true
when:

- `holdsWaterAtAll(it)`, and
- the item is a **vessel** holding no water (`!it.water`), or a **bottle**
  with no water or with `it.water.fill < 1`.

So a vessel holding any water, clean or tainted, can't take more, because
vessel water is all-or-nothing until #47. Neither can a bottle that is full
of either kind.

**Fill at the sink** is offered when the room has a sink, the water is
running, and the predicate holds. It replaces `canFillAtSink()`'s current
clean-only exclusion. `doFillAtSink()` goes on re-checking it.

**Pour into the <vessel>** is offered for an item with water
(`it.water && holdsWaterAtAll(it)`) on vessel `v` when:

- the predicate holds for `v`, **or**
- `v` holds **clean** water and the bottle holds **tainted** water. Tom
  chose to keep this, even though it just taints the vessel.

`doPourIntoVessel()` re-checks the same condition before acting. Its
effect, log line and `addWater()` are unchanged.

What this means for the player:

| Action | Target | Before | After |
|---|---|---|---|
| Fill at the sink | vessel, no water | offered | offered |
| Fill at the sink | vessel, clean or tainted water | clean: not offered; tainted: offered, only resets the boil | not offered |
| Fill at the sink | bottle, below full (either kind) | offered | offered |
| Fill at the sink | bottle, full (either kind) | clean: not offered; tainted: offered, no-op | not offered |
| Pour into | vessel, no water | offered | offered |
| Pour into | vessel, clean water; bottle clean | offered, no-op | not offered |
| Pour into | vessel, clean water; bottle tainted | offered, taints it | offered, taints it |
| Pour into | vessel, tainted water (either bottle) | offered, resets the boil | not offered |

`addWater()`'s `delete unit.boilMinutes` stays as it is. After this pass
it only runs on a vessel that holds no water or holds clean water, and
neither has a boil in progress.

### 2. Labels for Add to / Pour into (#223)

These rules apply separately to each action, **Add to** and **Pour into**.
They apply only to the vessels that action is being offered on, after the
guards above.

1. **Place.** Every vessel from `nearbyVessels()` has a place, taken from
   where it was found:
   - in any `invPools()` list: `carried`
   - on `room.floor`: `Floor`
   - in a container (listed, or the heat container): that container's
     `name`, which is its Here tab label

2. **One button per name and place.** Vessels offered this action that
   share a name **and** a place get **one** button. It acts on the
   **fullest** of them, the one with the greatest
   `totalWeight(v.contents || [])`. A tie goes to the first in
   `nearbyVessels()` order. Tom's reasoning: the vessels are
   indistinguishable to the player until #47 shows what each one holds.

3. **The place is shown only on a name clash.** When the buttons left
   after step 2 include two or more for the same vessel name, each of those
   buttons gets its place in parentheses. Any other button keeps today's
   label.

   ```
   One saucepan nearby:            Add to the dented saucepan
   Saucepans on stove and floor:   Add to the dented saucepan (Stove)
                                   Add to the dented saucepan (Floor)
   One carried, one in the stove:  Add to the dented saucepan (carried)
                                   Add to the dented saucepan (Stove)
   Two on the floor, none else:    Add to the dented saucepan   → the fuller one
   ```

   The same applies to **Pour into the <vessel>**.

With these rules, no two buttons of one action carry the same label, so
`rebuildKeepingFocus()` can no longer land on the wrong vessel's button.

**Retunable wording:** `carried` in lowercase against the capitalized tab
names (`Floor`, `Stove`) is what Tom picked from the options. It's
functional UI text, so clarity is the test, not tone. Note it as retunable
in the changelog.

## Design decisions to make during implementation

Record each in the changelog's Notes/assumptions.

- **How the place travels with a vessel.** For example, `nearbyVessels()`
  returns `{ vessel, place }`, or a sibling helper maps a vessel to its
  place. Recommended: have `nearbyVessels()` return pairs, since it already
  knows which list it found each vessel in. Its only caller at v0.8.0 is
  the loop in `getItemActions()`.
- **Where grouping lives.** Either a small helper that takes one action's
  offered vessels and returns `{ vessel, label }` entries, called once for
  Add and once for Pour, or inline in the loop. Recommended: the helper,
  so both actions share one set of rules.
- **Name of the #224 predicate.** For example `canTakeWater(it)`.

## Data / schema changes

None. No state fields, no item or registry fields, no save change.

## In scope

- The shared "can take more water" predicate, and both guards (Fill at the
  sink, Pour into), with their action functions re-checking.
- Place labels only on a name clash, and one button per name and place
  acting on the fullest vessel, for both Add to and Pour into.

## Explicitly out of scope

- **#47** (fluid volumes). Vessel water stays all-or-nothing, and a pour
  still empties the bottle whatever its fill. Showing what each vessel holds
  in its button is #47's.
- **#222** (tunable values of the cooking release).
- Log lines. "You pour the water into the …" and the Add line are
  unchanged and don't gain the place.
- The vessel's own pop-up (`vesselActions()`) and the Crafting panel's
  Dishes. Neither has the duplicate-label problem.
- Floor bags' contents. `nearbyLists()` doesn't reach them, and this pass
  doesn't change that.

## Sections touched

ACTIONS, INVENTORY / ITEM SYSTEM only. `canFillAtSink()` (or the new
predicate), `nearbyVessels()` and `doPourIntoVessel()` sit in its main
block. `getItemActions()`, where the labels are built, sits in its
"item-detail action list" sub-block. No WORLD DATA, and no RENDERING
function changes.

## UI changes

- The item pop-up no longer offers **Fill at the sink** on a vessel that
  holds water, or on a bottle that's full.
- It no longer offers **Pour into the <vessel>** on a vessel that holds
  water, except a clean-water vessel when the bottle is tainted.
- Where two nearby vessels share a name, **Add to** / **Pour into** buttons
  name the place: `(Floor)`, `(carried)`, or the container's name.
  Same-named vessels in one place share one button.

## Dependencies / issue linkage

Fulfils #224 and #223. The pull request carries `Closes #224` and
`Closes #223`. Nothing is expected to be deferred. If something is, file it
at the wrap.

## Open questions for Tom

None.

## After implementation

Open a pull request with the PATCH version bump and a new `CHANGELOG.md`
entry per `CHANGELOG_GUIDE.md`. The entry should reference this handoff by
path and record the implementation decisions above and the retunable
`carried` wording. Close both issues with `Closes #224` and `Closes #223`,
and move this handoff to `handoffs/archive/` in the same pull request.
