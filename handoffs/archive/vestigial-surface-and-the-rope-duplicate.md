# Ashfall Handoff — Vestigial surface, and the rope duplicate

Current shipped version: v0.4.13
Implied version-change type: PATCH
Issues: #70 — Vestigial mechanics surface; #76 — `rope` and `length_of_rope`
  are one object under two registry ids

## What this is

Two `tier-1` issues that are the same complaint applied to two layers: surface
that reads as live and is not. #70 is code and constants — an unreachable
action path, a `STACKABLE` category with no members, tags nothing consumes.
#76 is content — one object under two registry ids, which the stacking rule
then refuses to merge.

Both are deletions and comment corrections. No mechanic changes, no new state,
no `SAVE_KEY` rotation. The planning session settled every keep/delete call
below; none of them is left open.

The governing constraint is the Project Guide's rule on deleting things:

> Before removing one, say what a reader loses; if the answer is anything, it
> stays.

That question has a different answer per item, which is why some of this is
deleted and some is deliberately kept and annotated instead. **Keeping a thing
is a decision this pass makes, not an omission** — the annotation is what stops
it being re-filed.

## Relevant existing state

Verified against `ashfall.html` at v0.4.13. Line numbers are that revision's and
will have moved; find by identifier.

**Unreachable path.** `room.lockedDoors` is read at `:5511` in
`renderHereActionsPanel()` and set nowhere — one hit in the whole file. No room
in any of the 26 `build*()` functions defines it, and it is absent from the ROOM
SCHEMA comment. `doTryDoor()` (`:4061`) is reachable only from that block, and
its `label.replace("Try the door", …)` expects a label shape no data produces.
The surviving locked-door implementation is the `doors` table plus
`findKeyForDoor()`, handled a few lines below at `:5514`.

**`STACKABLE`.** `:260` — `new Set(["Food","Medical","Ammunition","Materials"])`.
Measured: zero registry entries carry `category:"Ammunition"`; the ten categories
actually present are Clothing, Container, Electronics, Food, Key, Literature,
Materials, Medical, Misc, Tool. The registry comment at `:591` already records
that firearms are deliberately excluded.

**The recipe extension point.** `canCraft()` (`:4353`–`:4354`) gates on
`recipe.tool` and `recipe.needsHeat`; `renderCraftPanel()` (`:5432`) prints both
in the "needs …" string. Neither `RECIPES` entry (`bandage`, `campfire_kit`)
sets either. `HEAT_RECIPES` does not route through `canCraft()` at all —
`doCookInContainer()` has its own path.

**Tags.** Measured against every consumer — `hasTool()`, `countByTag()`,
`consumeByTag()`, and the dynamic `hasTool(w.breakTag)` / `hasTool(c.breakTag)`
call sites at `:5546` and `:5592`:

| tag | consumer |
|---|---|
| `blunt` | `doBreakCar()` gate `:5551`, both window `breakTag`s |
| `cutting` | Storage Unit 1 and 2 `breakTag` |
| `chopping` | `doChopTree()` `:4494`, its button `:5587` |
| `fishing` / `tackle` | fishing button `:5554` |
| `battery` | `countByTag`/`consumeByTag` in the battery actions `:3952` |
| `fire-starter` | `findFireStarter()` `:3735` |
| `blade` | **none** |
| `prying` | **none** |
| `can-opening` | **none** |
| `heat` | **none in practice** — `roomHasHeat()` (`:3747`) is its only reader, and `roomHasHeat()`'s only caller is the dead `needsHeat` branch |

**The schema comment is already wrong**, independently of anything above. `:429`
lists the current tags as "blunt, blade, prying, cutting, chopping, fishing,
tackle, heat, fire-starter, battery" — ten. The registry carries eleven;
`can-opening` (on `can_opener`, `:465`) is missing from the list. This was not
noted in #70 and is a finding of this planning session.

**The backfill's second scan.** `backfillContainerFields()` calls
`scan(room.carContainers, defaultRoom.carContainers)`. `scan()` returns early
unless the *default* container has `spawnPools`. Measured: three rooms carry
`carContainers` (`poplar2nd`, `mid_poplar_1_2`, `mid_main_1_3`) and zero of
their containers have `spawnPools`. The call can never do anything today.

**The rope pair.** `:484` `length_of_rope` = `{ name:"Length of rope",
category:"Materials", unitWeight:1.5 }`; `:492` `rope` = `{ name:"Rope",
category:"Materials", unitWeight:1.5 }`. Identical but for the display string.
No mechanic references either id — no recipe input, no tag, no world check.

Placements and pools:

```
length_of_rope   balcony/storagebin        (:1246)
                 tools_general weight 5    (:772)
rope             twobee_balcony/storagebin (:1333)
                 hardware/bins qty 2       (:1724)
                 tools_general weight 6    (:771)
                 hardware_store weight 7   (:810)
```

`Materials` is in `STACKABLE` and `addToList()` merges on `itemId`, so a player
holding both carries two rows for one object. A container drawing `tools_general`
twice can roll one of each.

## Rules / mechanics

### 1. Delete the unreachable locked-door path

Remove the `room.lockedDoors` block from `renderHereActionsPanel()` and the
`doTryDoor()` function entirely. A reader loses nothing: it is superseded, and
the replacement is better. No schema comment mentions `lockedDoors`, so nothing
else needs editing.

### 2. Delete `"Ammunition"` from `STACKABLE`

`STACKABLE` becomes `new Set(["Food","Medical","Materials"])`. A reader loses a
hint that ammunition was once considered; the registry comment at `:591` already
states that firearms are deliberately excluded, so the hint is redundant with a
statement that is clearer.

No behaviour change: a set member that matches no item's category can never be
consulted.

### 3. Keep the recipe extension point — and say that it is one

`recipe.tool`, `recipe.needsHeat`, `roomHasHeat()` and the `renderCraftPanel()`
"needs …" string all stay. `canCraft()` reads as a small complete crafting gate
*because* those branches are there, and deleting them means the next recipe that
needs a tool re-adds them.

Add a comment above the two branches in `canCraft()` saying what they are: gates
no current recipe sets, kept as the declared shape for recipes that will. Per
the Project Guide, this is the "why, where the what is already obvious" case —
without it the next reader re-files #70. The comment must **not** name an issue
number or a version; it explains itself as a rule.

### 4. Keep the four unconsumed tags — and mark them reserved in the schema

`blade`, `prying`, `can-opening` and `heat` all stay in `ITEM_REGISTRY`. They are
content-facing: they are how a future item says "I behave like a knife". Deleting
and re-adding them is churn, and each re-add is a registry edit.

Rewrite the ITEM DATA SCHEMA `tags` entry so it lists all eleven and separates
the two states. The required content, not the required wording:

- **Read by a mechanic today:** `blunt`, `cutting`, `chopping`, `fishing`,
  `tackle`, `fire-starter`, `battery`.
- **Declared, with no consumer yet:** `blade`, `prying`, `can-opening`, `heat`.
  An item tagged with one of these is making a claim nothing currently acts on —
  correct to write, and not yet load-bearing.

`heat` belongs in the second group and the comment should be precise about why:
its reader `roomHasHeat()` exists, but the only caller of `roomHasHeat()` is
`canCraft()`'s `needsHeat` branch, which no recipe sets. It is reachable code on
an unreachable path.

The list must be complete after this pass — an incomplete specification of the
tag system is what `can-opening` going unlisted already cost.

### 5. Keep the `carContainers` backfill scan — and mark it speculative

Keep the second `scan()` call. It costs one line and covers a car container
gaining `spawnPools` later, which is plausible content. Add a comment saying it
is future-proofing with no current effect, so the next audit does not have to
re-derive that.

### 6. Merge the rope pair onto `rope`

Delete the `length_of_rope` registry entry. `rope` (display name "Rope") is the
survivor — it has three placements to `length_of_rope`'s one and appears in two
pools to its one, so it is the cheaper repoint and the more common name.

Four edits:

1. Delete `length_of_rope` from `ITEM_REGISTRY`.
2. `balcony`/`storagebin` (`:1246`): `{ id:"length_of_rope", qty:1 }` becomes
   `{ id:"rope", qty:1 }`.
3. `tools_general` (`:771`–`:772`): delete the `length_of_rope` entry and set
   `rope`'s weight to **11**.
4. Leave `hardware_store`'s `rope` at weight 7, and `hardware/bins`' hand
   placement of `qty:2`, untouched.

**Weight 11 is chosen to be provably rate-neutral, not to be balanced.**
`tools_general`'s entry weights today total 8+6+6+5+5+2 = 32, of which rope in
either form is 6+5 = 11. After the merge the total is 8+6+11+5+2 = 32 and rope
is 11. Any rope, before or after, is 11/32 of a pick. **Flag 11 as retunable in
the changelog** — it preserves the status quo deliberately, and the status quo
was itself an accident of two ids existing.

**Save compatibility, to be stated in the changelog rather than discovered:** an
existing save holding `length_of_rope` keeps working. Items carry their own
`name`/`category`/`unitWeight` in the save, and `backfillItemIds()` only *adds*
a missing `itemId` — it never rewrites one. The orphaned item simply stops
stacking with `rope`, which is exactly the status quo. No backfill is added and
none is wanted.

### 7. Do not add a duplicate-detection dev helper

#76 suggests a third dev-only console helper, beside `validateItemRegistry()`
and `validateLocations()`, reporting registry entries that share a mechanical
signature. **This planning session built it and measured it, and it does not
work.** Recording the measurement here so it is not re-proposed:

Signature = the registry entry with `name` removed. Across the 154 entries that
yields **28 colliding groups covering 82 entries — 53% of the registry.**
`rope`/`length_of_rope` lands inside a six-member group alongside `plank`,
`spare_parts_box`, `spare_machine_parts` and `paint_can`, none of which is a
duplicate of anything.

Narrowing to "same signature *and* both in one spawn pool" still returns 13
groups, including `bandage`/`aspirin`/`gauze_rolls`/`antiseptic_wipes`
(everything medical that weighs 0.05 kg) and `canned_corn`/`canned_tuna`.

`canned_corn` and `canned_tuna` are in fact identical in every modelled property
— 0.4 kg, `restores:{hunger:20}`, `verb:"Eat"` — and are **not** a duplicate:
corn and tuna are two different foods that a later spoilage or nutrition layer
would separate. That is the proof the check cannot work. What makes
`rope`/`length_of_rope` a duplicate is that the two *names denote the same
object*, which is semantic and invisible to any signature comparison.

Add no helper. The changelog's Documentation section records the measurement and
the conclusion.

## Design decisions to make during implementation

None of substance. Every keep/delete call is settled above.

The only latitude is **comment wording** for items 3, 4 and 5. Requirements: no
issue numbers, no version numbers, no handoff path (`CLAUDE.md`'s "comments carry
intent, not history"), and the tag list in item 4 must be complete and must
distinguish the two states. Beyond that, match the surrounding voice.

## Data / schema changes

- **PLAYER STATE:** none.
- **ITEM DATA SCHEMA:** no field added or removed. One registry entry deleted
  (`length_of_rope`). The `tags` documentation is rewritten; the tag *set* is
  unchanged.
- **WORLD DATA:** one placement repointed, one `SPAWN_POOLS` entry removed and
  one weight changed. No room, exit, container or description touched.
- **Save format:** unchanged. `SAVE_KEY` stays `ashfall_save_v0.4`.

## In scope

- [ ] Delete `doTryDoor()` and the `room.lockedDoors` block.
- [ ] Delete `"Ammunition"` from `STACKABLE`.
- [ ] Comment on `canCraft()`'s two unset gates.
- [ ] Rewrite the ITEM DATA SCHEMA `tags` entry: eleven tags, live vs. reserved.
- [ ] Comment on `backfillContainerFields()`'s `carContainers` scan.
- [ ] Merge rope: registry delete, placement repoint, pool weight to 11.
- [ ] `GAME_CONFIG.VERSION` PATCH bump, changelog entry, `Closes #70` and
      `Closes #76`.

## Explicitly out of scope

- **Wiring `can-opening` to a consumer — #95.** The one dead tag whose absence is
  player-visible. A genuine new mechanic, `tier-2` MINOR. This pass keeps the tag
  in place precisely so #95 has something to consume.
- **Making `heat` live — #96.** Gating the Cook action on `roomHasHeat()` rather
  than `room.heatActive` would make `propane_torch` functional. A new mechanic,
  not cleanup. This pass keeps `roomHasHeat()` and the tag alive for it.
- **Retagging `doBreakCar()` — #97.** It is gated on `hasTool("blunt")` while its
  log line reads "You pry the door open", and `prying` sits unconsumed on the
  crowbar. Retagging narrows the tool set from eight items to one, which is a
  balance change and does not belong in a deletion pass.
- **`recipe.tool` / `needsHeat` deletion.** Considered and rejected above.
- **Any `validateRegistryDuplicates()` helper.** Measured and rejected above.
- **The `canned_corn` / `canned_tuna` signature collision.** Not a duplicate;
  no action.

## Sections touched

CONFIG / CONSTANTS (`STACKABLE`), WORLD DATA (`ITEM_REGISTRY`, `SPAWN_POOLS`, one
placement, the ITEM DATA SCHEMA comment), WORLD INTERACTION (`doTryDoor`),
CRAFTING (`canCraft`), PERSISTENCE (`backfillContainerFields`), RENDERING
(`renderHereActionsPanel`).

Note for the changelog: this pass touches both WORLD DATA and non-content
sections. That is not the both-buckets case the Project Guide bounds — nothing
here is a new mechanic with its defining data. It is a deletion pass that happens
to delete in two places.

## UI changes

None intended, and this is checkable. `room.lockedDoors` is never set, so its
button never rendered. `Ammunition` matches no item's category. The tag and
recipe-gate changes are comments only. The rope merge changes one item's display
name from "Length of rope" to "Rope" in the one container that held it, and
removes a second inventory row that could previously appear.

## Dependencies / issue linkage

- Fulfils **#70** and **#76** in full.
- Independent of every other open issue. Blocks nothing.
- **Nothing is left to file.** The three items this pass defers were filed during
  the planning session that wrote this handoff — **#95**, **#96** and **#97** —
  so the changelog's Documentation section should say that nothing further was
  deferred rather than repeating them. If implementation turns up something new,
  file that.

## Open questions for Tom

None. This handoff is ready to build from.

## After implementation

Open a pull request carrying the PATCH version bump and a new `CHANGELOG.md`
entry per `CHANGELOG_GUIDE.md`, naming this handoff by path, recording the
comment-wording choices and the "11 is rate-neutral and retunable" note, and
closing with `Closes #70` and `Closes #76`. Prove the no-behaviour-change claim
with `git diff origin/main...HEAD -- ashfall.html` rather than asserting it.
