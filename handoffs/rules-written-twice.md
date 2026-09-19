# Ashfall Handoff — Rules written twice: the gait lock and the equipment round trip

Current shipped version: v0.4.13
Implied version-change type: PATCH
Issues: #69 — The Fatigue-100 Sneak lock is a game rule living in RENDERING, and
  it is written twice; #71 — `doEquip()`/`doUnequip()` hand-build item objects
  and drop `itemId`

## What this is

Two `tier-1` issues that are one complaint: a fact the file already owns, stated
again at a call site. #69 is a game rule — `fatigue >= 100` decides what the
player may do, and is written in two sections, neither of which owns the
Stamina/Fatigue system. #71 is an item definition — `ITEM_REGISTRY` owns what a
backpack is, and `doUnequip()` rebuilds one by hand.

Both resolve the same way: name the fact once, give it a predicate or a
constructor, and have the call sites ask rather than restate.

**#69 carries a deliberate behaviour change** — see rule 1. Everything else in
this pass is behaviour-neutral.

## Relevant existing state

Verified against `ashfall.html` at v0.4.13. Line numbers are that revision's;
find by identifier.

### The gait lock

Three sites, two sections, one unnamed threshold:

```js
// EVENTS / UI HELPERS, the gait click handler  :4816
if(state.vitals.fatigue >= 100 && btn.dataset.gait !== "sneak") return;

// RENDERING, renderStatsPanel()  :5464
const fatigueLocked = state.vitals.fatigue >= 100;
if(fatigueLocked) state.gait = "sneak";              // <-- a write to PLAYER STATE, during a render
document.querySelectorAll("#gaitBar button[data-gait]").forEach(btn=>{
  btn.classList.toggle("active", state.gait === btn.dataset.gait);
  btn.disabled = fatigueLocked && btn.dataset.gait !== "sneak";
});
```

Every other threshold in the STAMINA / FATIGUE block is a named constant
(`LOW_HUNGER_THRESHOLD`, `STAMINA_RECOVERY_DELAY_MIN`, `REST_STAMINA_RATE`). This
one is a bare `100` in two places, in neither of which the system lives.

**The state write during render is the sharper half.** The ARCHITECTURE comment
says RENDERING "should never contain rules"; this one both contains a rule and
changes the game to enforce it. It is correct today only by call order:
`render()` runs `renderStatsPanel()` (which forces the gait) before
`renderMoveActionsPanel()` (which prices exits through `exitMinutes()` →
`moveMinutes()` → `GAITS[state.gait].speed`), so buttons show Sneak-priced
durations and the following `doMove()` charges Sneak. Reorder those two calls and
the panel prices at the old gait while movement charges the new one. Nothing in
the file says the order is load-bearing.

The click handler also toggles `active` by hand before calling `render()`, which
then sets `active` again from `state.gait` — two places deciding which button is
lit.

**The rule is reachable.** `applyExertion()` runs after `advanceTime()` at every
call site, so an action's own duration recovers Stamina before its Exertion
lands. At full Energy, chopping is exactly break-even (`CHOP_TREE_EXERTION` 30 vs
`CHOP_TREE_MIN` 30 × `BASELINE_STAMINA_RATE` 1) and fishing is net positive.
Fatigue only builds once `energyRecoveryMultiplier()` and
`hungerThirstRecoveryPenalty()` bite — which a real run reaches; a chop-and-fish
loop from a fresh start hits Fatigue 100 around game minute 1040.

### The equipment round trip

```js
// doEquip()  :3870
state[it.slotType] = { name:it.name, unitWeight:it.unitWeight, capacityKg:it.capacityKg, items: it.contents || [] };

// doUnequip()  :3879
const item = { name:slot.name, category:"Container", qty:1, unitWeight:slot.unitWeight,
  slotType:slotKey, capacityKg:slot.capacityKg, contents:slot.items };
```

Neither goes near `itemFromRegistry()`. `category:"Container"` is a hard-coded
literal of a property the registry already owns. The round trip is lossless for
gameplay — contents, weight, capacity and the tab all survive — and loses exactly
one thing: `itemId`. Observable effect: `countInPools("worn_backpack")` returns 0
while the bag is in inventory. Nothing reads it for a bag today, and
`backfillItemIds()` restores it on the next save/load, so this is a latent gap
rather than a live bug.

**The keychain is the constraint.** `CONTAINER_SLOTS` is
`["keychain"].concat(…registry slotTypes…)` — measured, the registry contributes
five: `worn_backpack:backpack`, `duffel_bag:duffel`, `purse:purse`,
`fanny_pack:fannypack`, `tote_bag:tote`. `state.keychain` is built by
`makeDefaultState()` in the same projected shape and is **not** a found item; it
has no registry entry and therefore no `itemId` to carry.

And it is unequippable today. `renderInventoryPanel()` shows the Unequip button
whenever `CONTAINER_SLOTS.indexOf(state.invTab) >= 0`, and `"keychain"` is index
0. So `doUnequip("keychain")` is reachable from the UI and must keep working.
**#71's option 2 as written does not account for this** — a bare
`itemFromRegistry({ id: slot.itemId })` throws on the keychain. The spec below
adds the fallback branch that option 2 needs.

Registry names are unique — measured, 154 entries, 154 distinct names — so a
name-keyed backfill is unambiguous, exactly as `backfillItemIds()` already
assumes.

### The shallow-copy aliasing trap

`itemFromRegistry()` deep-clones on purpose so no two placements share mutable
state. But `addToList()` stores `const copy = { ...item }` — shallow — so a moved
stack's `durability` and `tags` are the *same objects* as the source's.

Dormant, not live: a stack only splits through the Half/1 buttons, whose
`splittable` gate in `getItemActions()` is `STACKABLE.has(it.category) &&
!it.durability`, so a durability-bearing item is never split — the source is
spliced out whole and no aliased pair survives. The two stackable items that
carry durability (`box_of_matches`, `lighter`) are excluded by that guard.

The guard that keeps it dormant lives in a different function from the copy, so
nothing local warns a future edit to `splittable`.

## Rules / mechanics

### 1. The gait lock becomes a named rule with one home — and the pace preference survives it

**The behaviour change, stated plainly:** today, hitting Fatigue 100 overwrites
`state.gait` with `"sneak"` and the player's chosen pace is gone — when Fatigue
drops they must re-pick it. After this pass, `state.gait` is the player's
*preference* and is never written by the lock; the lock supplies an *effective*
gait while it holds, and the preference lights up again by itself when Fatigue
falls below 100. This must be called out in the changelog as player-visible.

Add to the STAMINA / FATIGUE SYSTEM CONSTANTS block, beside `LOW_HUNGER_THRESHOLD`:

```js
const FATIGUE_GAIT_LOCK = 100;
```

Add to the STAMINA / FATIGUE SYSTEM section, beside `sleepAvailable()` and
`fatigueRecoveryAllowed()` — the predicate pattern the file already uses:

```js
function gaitLocked(){ return state.vitals.fatigue >= FATIGUE_GAIT_LOCK; }
function effectiveGait(){ return gaitLocked() ? "sneak" : state.gait; }
```

Then, in order of how easy each is to get wrong:

- **`moveMinutes()`** reads `GAITS[effectiveGait()].speed` in place of
  `GAITS[state.gait].speed`. This is what makes the call-order fragility
  disappear: pricing and charging both derive from the same predicate, whenever
  they run.
- **`doMove()`'s jog surcharge** becomes `if(effectiveGait() === "fast")`, not
  `if(state.gait === "fast")`. **This is the one place the change is not
  mechanical.** Under the old model the coercion had already rewritten
  `state.gait` to `"sneak"`, so the check read Sneak and no exertion applied.
  Under the new model `state.gait` stays `"fast"`, and leaving this line alone
  would charge a locked player Jog exertion while moving at Sneak speed —
  a new bug introduced by the fix. It must change.
- **`renderStatsPanel()`** drops the `state.gait = "sneak"` write entirely, and
  becomes:

  ```js
  const locked = gaitLocked();
  document.querySelectorAll("#gaitBar button[data-gait]").forEach(btn=>{
    btn.classList.toggle("active", effectiveGait() === btn.dataset.gait);
    btn.disabled = locked && btn.dataset.gait !== "sneak";
  });
  ```

  RENDERING now reads two predicates and writes no state. The bar shows Sneak lit
  while locked — which is true, it is what movement costs — and returns to the
  player's pace when the lock lifts.
- **The click handler** reads the predicate: `if(gaitLocked() && btn.dataset.gait
  !== "sneak") return;`. Delete its manual `classList` toggling — `render()` runs
  on the next line and `renderStatsPanel()` sets `active` from `effectiveGait()`,
  so the handler's version is a second opinion about the same thing. After this,
  one place decides which button is lit.

`state.gait` is still written in exactly one place: the click handler, from the
player's click. That is the point.

**Save compatibility:** `state.gait` keeps its shape and meaning (a gait key), so
no backfill. A v0.4.13 save written while locked holds `"sneak"` — the coercion
already destroyed the preference before the save — so it loads as a Sneak
preference. Correct, and worth one changelog sentence rather than a silent
difference.

### 2. The equipment slot carries `itemId`, and unequip rebuilds through the registry

**`doEquip()`** adds `itemId` to the slot object it builds:

```js
state[it.slotType] = { itemId: it.itemId, name:it.name, unitWeight:it.unitWeight,
  capacityKg:it.capacityKg, items: it.contents || [] };
```

**`doUnequip()`** reconstructs through the registry when it can, and keeps the
hand-built object only for the case that genuinely has no registry entry:

```js
const item = slot.itemId
  ? Object.assign(itemFromRegistry({ id: slot.itemId, qty:1 }), { contents: slot.items })
  : { name:slot.name, category:"Container", qty:1, unitWeight:slot.unitWeight,
      slotType:slotKey, capacityKg:slot.capacityKg, contents:slot.items };
```

Every found bag takes the first branch, which deletes the hand-written
`category`/`slotType`/`capacityKg` triple for all five of them. The second branch
is reached by exactly two things, and a comment must say so: the keychain, which
has no registry entry by design, and a slot loaded from a save written before
this pass. Without that comment the branch reads as dead code and gets deleted by
the next audit.

**Add `backfillSlotItemIds()`** to PERSISTENCE, called from `applyLoadedData()`
alongside the existing backfills. It gives a loaded slot its `itemId` by reverse
name match against `ITEM_REGISTRY`, the way `backfillItemIds()` does for items —
sound because registry names are unique. The keychain matches nothing and is
left alone, which is correct. Skip any slot that already has an `itemId`, and any
that is `null`.

Its comment should say what it is for, in the voice of the four backfills already
there: an old save's equipped bag has no `itemId`, so `countInPools()` cannot see
it and unequipping it would take the fallback branch.

**Ordering:** it must run after `state` is committed and may run anywhere among
the other backfills — it reads only `state[slot]` and `ITEM_REGISTRY`, and no
other backfill touches equipment slots.

### 3. `addToList()` deep-clones

Replace the shallow copy with a deep one:

```js
const copy = JSON.parse(JSON.stringify(item));
delete copy._uid;
```

This closes the aliasing class rather than documenting it. `itemFromRegistry()`
already deep-clones for the same reason, so this makes the two item-creating
paths agree.

**It is behaviour-neutral today, and the proof belongs in the changelog:** the
`splittable` gate means no aliased pair is currently observable. Verify by diff
plus the reasoning, not by assertion.

Check the callers before changing it — all six are safe, and the handoff states
why so the coding session does not have to re-derive it. `doTake()`/`doStore()`
pass a spread of an item they are about to shrink or splice; `giveItem()` and
`doOpenContainer()`/`doCookInContainer()` pass freshly-built registry items;
`doDismantleCampfire()` moves a container's items to the floor and then discards
the container; `doUnequip()` passes an item whose `contents` come from a slot
that is nulled on the next line. None needs the copy to alias its source.

The existing comment above `delete copy._uid` stays — it explains a different
hazard (two array entries sharing a uid) and is still the only thing that does.
Extend it with a sentence on why the clone is deep; do not replace it.

## Design decisions to make during implementation

**Where `gaitLocked()` and `effectiveGait()` live.** Recommended: the STAMINA /
FATIGUE SYSTEM section, beside `fatigueRecoveryAllowed()`. Alternative: CORE
UTILITIES beside `moveMinutes()`. The first is recommended because the rule is
about Fatigue, and the section that owns Fatigue is where a reader retuning
`FATIGUE_GAIT_LOCK` will look. Record which was used.

**Whether `effectiveGait()` is one function or two.** Recommended: two, as
specced — `gaitLocked()` is what the button-disabling and the click guard want,
and `effectiveGait()` is what pricing wants. Collapsing to one would make one of
the two call sites derive the other's answer. Record if collapsed.

Explicitly **not** open, and not to be relitigated: giving the keychain an
`ITEM_REGISTRY` entry so it needs no fallback branch. It would make
`CONTAINER_SLOTS`' explicit `["keychain"]` redundant and is tempting for that
reason, but the comment at `CONTAINER_SLOTS` records a deliberate decision that
the keychain is not a found item, and a registry entry makes it placeable and
spawnable in a way nothing wants. The fallback branch is the right shape.

Also not open: #71's option 3 (`state[slotType]` holds the item object rather
than a projection). It changes the persisted shape of every slot, which makes it
MINOR, and it buys little over option 2. Out of scope below.

## Data / schema changes

- **PLAYER STATE:** no new field. `state[slotType]` gains an `itemId` property on
  the existing slot object — a new key on an existing structure, written by
  `doEquip()` and backfilled on load. This does **not** rotate `SAVE_KEY`: old
  saves load, and `backfillSlotItemIds()` plus the `doUnequip()` fallback both
  handle a slot without it. The pass stays PATCH.
- **ITEM DATA SCHEMA:** unchanged.
- **WORLD DATA:** untouched.
- **Save format:** additive and backward-compatible. `SAVE_KEY` stays
  `ashfall_save_v0.4`.

## In scope

- [ ] `FATIGUE_GAIT_LOCK`, `gaitLocked()`, `effectiveGait()`.
- [ ] `moveMinutes()` and `doMove()`'s jog check read `effectiveGait()`.
- [ ] `renderStatsPanel()` stops writing `state.gait`; the click handler reads
      the predicate and stops toggling `active` by hand.
- [ ] `doEquip()` carries `itemId`; `doUnequip()` rebuilds through the registry
      with a commented fallback.
- [ ] `backfillSlotItemIds()`, wired into `applyLoadedData()`.
- [ ] `addToList()` deep-clones; the `_uid` comment gains a sentence.
- [ ] `GAME_CONFIG.VERSION` PATCH bump, changelog entry, `Closes #69` and
      `Closes #71`.

## Explicitly out of scope

- **#71 option 3**, the un-projected slot. MINOR; see above.
- **`invTab` / `worldTab` as PLAYER STATE — #98.** #69 flags two more state writes
  during render — `renderInventoryPanel()`'s `state.invTab = "inventory"` and
  `renderWorldItemsPanel()`'s `state.worldTab = "floor"`. Both are UI-state
  normalisation rather than game rules, both are load-bearing (the next line
  would throw on a stale tab), and both raise a separate question: `invTab` and
  `worldTab` are the only pure-UI fields in `state` and are therefore serialised,
  while `mapZoomMode`/`mapZoomStep` were deliberately kept out with a comment
  saying so. That is its own decision. **Leave both lines exactly as they are.**
- **The chop break-even knife-edge — #99.** `CHOP_TREE_EXERTION` (30) is exactly
  `CHOP_TREE_MIN` (30) × `BASELINE_STAMINA_RATE` (1), so chopping is precisely
  free at full Energy and retuning any one of the three flips it. Nothing in the
  source records that the three are in this relationship. A balance observation,
  not this pass's work.
- **Showing Fatigue anywhere.** It remains invisible, which is why the lock
  arrives without warning. That is #49's job.

## Sections touched

CONFIG / CONSTANTS (`FATIGUE_GAIT_LOCK`), CORE UTILITIES (`moveMinutes`),
INVENTORY / ITEM SYSTEM (`addToList`, `doEquip`, `doUnequip`), WORLD INTERACTION
(`doMove`), SURVIVAL / TIME SIMULATION → STAMINA / FATIGUE (`gaitLocked`,
`effectiveGait`), PERSISTENCE (`backfillSlotItemIds`, `applyLoadedData`), EVENTS
/ UI HELPERS (the gait click handler), RENDERING (`renderStatsPanel`).

No WORLD DATA. This is a mechanics-and-rendering pass.

## UI changes

One, and it is the behaviour change in rule 1. While Fatigue is at 100 the pace
bar disables everything but Sneak and shows Sneak lit — unchanged from today. The
difference is afterwards: when Fatigue drops below 100 the player's previously
chosen pace becomes active again on its own, instead of the bar being left on
Sneak with the old choice discarded.

Nothing else moves. The Move panel's durations, the equipment tabs and the
inventory rows all render exactly as before.

## Dependencies / issue linkage

- Fulfils **#69** and **#71** in full.
- Independent. Blocks nothing, blocked by nothing.
- **Nothing is left to file.** Both items this pass defers were filed during the
  planning session that wrote this handoff — **#98** and **#99** — so the
  changelog's Documentation section should say that nothing further was deferred
  rather than repeating them. If implementation turns up something new, file that.

## Open questions for Tom

None. This handoff is ready to build from.

## After implementation

Open a pull request carrying the PATCH version bump and a new `CHANGELOG.md`
entry per `CHANGELOG_GUIDE.md`, naming this handoff by path, recording the two
"Design decisions" resolutions, and closing with `Closes #69` and `Closes #71`.

Validation this pass specifically needs, beyond the diff:

- **Drive the lock.** Reach Fatigue 100, confirm the bar disables, confirm
  movement is priced *and charged* at Sneak, confirm Jog exertion is not applied
  while locked, then recover below 100 and confirm the previously chosen pace
  comes back by itself.
- **Prove the call-order fix.** `renderStatsPanel()` and
  `renderMoveActionsPanel()` may now be called in either order with identical
  results. Say so, having checked it.
- **Round-trip every bag.** All five equippable bags, with contents, through
  equip → store something → unequip → re-equip, confirming `countInPools()` sees
  the stowed bag by id.
- **Round-trip the keychain**, which takes the fallback branch.
- **Load a v0.4.13 save** holding an equipped bag and confirm
  `backfillSlotItemIds()` gives it its `itemId`.
