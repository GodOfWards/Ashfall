# Ashfall Handoff — Tier-0 sweep

Current shipped version: v0.7.1
Implied version-change type: PATCH. Nothing here adds persistent state. #195
normalises a field saves already carry, and #181 changes which items an
existing rule reaches.
Issues: #173, #176, #180, #181, #183, #184, #193, #195

## What this is

The open `tier-0` backlog, minus #167, shipped as one PATCH. Eight
independent small fixes. The only coupling is between #180 and #195:
#195's load-time tag resync is what makes #180's tag removal reach
walkie-talkies already in a save.

Each issue's open question was answered in planning. The answers are below
as rules, and none is left open.

## Relevant existing state

Verified against `ashfall.html` at v0.7.1. Line numbers are orientation
only. Find each by its function name.

- **`hereNote()`** (RENDERING, ~6695) sets
  `note.style.cssText = "color:var(--ink-faint); font-size:12.5px; padding:6px 0;"`.
  Its comment says the helper replaces a literal "written at five call
  sites". There are four call sites.
  `button.action` is `font-size:12px; padding:5px 9px`.
- **`.menu-placeholder`** (`<style>`, ~78) is the rule
  `{ font-size:12px; color:var(--ink-faint); font-style:italic; }`. No
  markup and no script uses the class.
- **`render()`'s game-over branch** (~7238):
  - Clears `#moveActions` and appends one button,
    `actionButton("Restart", ()=> doRestart())`.
  - Blanks `#craftingList`, under a comment that ends
    "(#183 asks whether it should say more)".
  - Calls `closeAllLayers()` once, guarded by `gameOverRendered`.
  - The live branch runs `renderCraftingPanel()`.
- **The hub row** is built once, at load, from `HUB_BUTTONS`. Crafting is
  `{ label:"Crafting", opens:"crafting" }`. Placeholders (`opens:null`) are
  `disabled`, with a `.hint` span reading `HUB_PLACEHOLDER_HINT`. There is
  already a `#hubRow button:disabled` style. Nothing touches the Crafting
  button after the row is built. `openPanel("crafting")` is reachable
  only from that button.
- **`doRestart(seed)`** (PERSISTENCE, ~5759) with no argument starts a fresh
  world. A uint32 replays that seed. Its comment requires click handlers
  to wrap it in an arrow function. `state.seed` holds the run's canonical
  uint32.
- **`doCraft()`** does not check `gameOver`.
- **`applyWorldTicking(min)`** (SIMULATION, ~4804) drains devices only across
  `invPools()`:
  - The condition is `if(it.on && it.durability)`. Durability drops by
    `it.drainRate*min`, clamped at 0.
  - At 0 it sets `it.on = false` and logs
    `` `Your ${it.name.toLowerCase()} runs out of battery and shuts off.` ``
    as `"warn"`.
  - `invPools()` is the inventory plus each `CONTAINER_SLOTS` slot's
    `.items`. It does not descend into `contents`.
  - The fire block below it logs only when `id === state.currentRoom`.
- **`forEachItemList(visit)`** (PERSISTENCE, ~5174) calls `visit(list)` for:
  - every `invPools()` list;
  - every room's `floor`, `containers[].items` and `carContainers[].items`;
  - the `contents` of any item in any of those lists, at any depth.

  It passes only the list, with no context. It does not visit the
  `CONTAINER_SLOTS` slot objects on `state` (the equipped bags
  themselves), only their `.items`.
- **`batteryActions(it)`** offers "Replace batteries" when
  `countByTag("battery") >= 1`, and spends one with
  `consumeByTag("battery", 1)`.
- **Items with the `battery` tag:** `spare_batteries`
  (`{ …, tags:["battery"] }`) and `walkie_talkie`
  (`{ name:"Walkie-talkie", category:"Electronics", unitWeight:0.3, tags:["battery"] }`).
  No other item carries the tag. `walkie_talkie` rolls from two spawn pools.
- **`itemFromRegistry()`** deep-copies the registry entry, `tags` included.
  It then applies `ref.overrides`. No placement in the file uses
  `overrides`, and no code changes an item's `tags` after creation. The
  ITEM DATA SCHEMA comment (~596) already says `overrides` is "for genuine
  per-instance state only".
- **`applyLoadedData()`** runs these backfills after validation, in order:
  1. `resyncUidCounter()`
  2. `backfillItemIds()`
  3. `backfillSlotItemIds()`
  4. `backfillLocationIds()`
  5. `backfillContainerFields()`
  6. `backfillRoomAddresses()`
  7. `backfillIllnessScale()`

  Then it calls `render()`. `backfillItemIds()` covers list items and
  `backfillSlotItemIds()` covers slot objects. That split is the precedent
  for the slot-object coverage below.
- **The comment above `validateReachability()`** (PERSISTENCE, ~5520) says:
  "Ten dead pools and twelve unreachable items are the expected output at
  v0.5.1, and driving them to zero is the balance pass's job (#66, #67)."
  Run at v0.7.1, the helper reports 10 dead pools and 11 unreachable
  items. #66 is closed.

## Rules / mechanics

### #193: Here-group notes

In `hereNote()`, change `font-size:12.5px` to `12px` and `padding:6px 0`
to `5px 0`. The colour is unchanged. Also correct the comment's "five call
sites" (there are four). Dropping the count is preferred, so it can't go
stale again.

### #184: dead CSS

Delete the `.menu-placeholder` rule. Nothing replaces it.

### #183: Crafting after game over

- The Crafting hub button is `disabled` while `gameOver` is true and
  enabled otherwise. It has **no hint line**, because "You did not survive."
  already says why. The existing `#hubRow button:disabled` style is the
  whole visual.
- The state is set on every `render()`, in both branches. That way
  Restart, Replay this seed, and loading a save after death all re-enable
  it.
- Identify the button by `opens === "crafting"`, never by its label.
- The game-over branch still blanks `#craftingList`. Rewrite its comment
  to say why the blanking stays: `doCraft()` has no `gameOver` guard, so
  live recipe buttons must never survive into the game-over screen. The
  comment must no longer cite an issue number.

### #176: Replay this seed

- In the game-over branch, add a second button after Restart:
  `actionButton("Replay this seed", ()=> doRestart(state.seed))`.
- Order: **Restart**, then **Replay this seed**.
- Restart is unchanged.

### #181: devices drain wherever they are

- `applyWorldTicking()` drains every item with `it.on && it.durability`,
  wherever `forEachItemList()` can reach it: carried, stowed inside a bag's
  `contents`, on any floor, in any container or car container, in any
  room. The drain formula and switch-off are unchanged.
- The log line when a device hits 0 depends on where it is:

| Where the device is | Log line (`"warn"`) |
|---|---|
| Carried: in an `invPools()` list, or in the `contents` of a carried item at any depth | `` `Your ${name} runs out of battery and shuts off.` `` (unchanged) |
| In the current room: `world[state.currentRoom]`'s `floor`, `containers[].items` or `carContainers[].items`, or nested `contents` at any depth | `` `The ${name} runs out of battery and shuts off.` `` |
| Anywhere else | No line. It shuts off silently. |

  `${name}` is `it.name.toLowerCase()`, as today.

### #180: the walkie-talkie is not a battery

Remove `tags:["battery"]` from `walkie_talkie`'s `ITEM_REGISTRY` entry. The
entry then has no `tags` field. It gets nothing in its place: no `device`
tag, no `on`/`hasBatteries`/`durability`.

### #195: tags resync from the registry on load

- New `backfillRegistryTags()` in PERSISTENCE, called from
  `applyLoadedData()` after `backfillItemIds()` and
  `backfillSlotItemIds()`, since it needs `itemId`.
- It covers every item `forEachItemList()` reaches, **and** each
  `CONTAINER_SLOTS` slot object on `state`.
- For each such item whose `itemId` is a key of `ITEM_REGISTRY`:
  - if the registry entry has `tags`, set `it.tags` to a fresh copy of that
    array;
  - otherwise, `delete it.tags`.
- An item with no `itemId`, or one that is not in the registry, is left
  untouched.
- It runs on load only. A new game's items already come from the registry.
- The ITEM DATA SCHEMA comment's `overrides` paragraph gains one rule: an
  item's `tags` are definition data. `overrides` never sets them, and the
  load path resyncs them from the registry.
- The backfill's own comment says why it exists: `itemFromRegistry()`
  deep-copies `tags` onto every instance, so without it a registry tag fix
  would never reach a save.

### #173: the reachability comment

Rewrite the paragraph above `validateReachability()` that ends "(#66, #67)":

- No count, no version and no issue number.
- Keep the point that the helper reports state and does not assert it is
  good.
- Say that dead pools and unreachable items are expected until the spawn
  balance is done.
- Name `ashfallDev.validateReachability()` as the live figure.
  `ashfallDev.sampleSeeds()` may be named alongside it.
- The exact wording is the coding session's.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

- **#181: how the tick knows where a device is.** `forEachItemList()`
  passes only the list. The options are:
  - (a) walk the three scopes (carried, current room, elsewhere) separately
    inside `applyWorldTicking()`;
  - (b) give the walker an optional context argument, leaving existing
    callers unaffected;
  - (c) test list membership another way.

  Recommended: (a) or (b), whichever reads cleaner. Whatever the choice,
  every list must be visited exactly once, so no device drains twice in a
  tick.
- **#183: how `render()` reaches the Crafting button.** Keep a reference
  when the hub row is built, or look it up by its `opens` value. Either is
  fine.
- **#193: inline style or class.** Keep `hereNote()`'s inline style
  (recommended; a two-value edit) or move it to a CSS class. Moving it is
  allowed but not required. #165's text-size option is the pass that
  would need a class.

## Data / schema changes

- **State fields:** none. `SAVE_KEY` does not rotate.
- **Item registry:** `walkie_talkie` loses its `tags` field (#180). This is
  a correction to a definition, not instance data. It is the only WORLD
  DATA change in this pass, and none of the mechanics here depends on it.
- **Item schema:** no new fields. The ITEM DATA SCHEMA comment gains the
  rule that `tags` are definition data, resynced on load (#195).

## In scope

- [ ] #193: `hereNote()` at 12px, `padding:5px 0`; its call-site-count comment corrected
- [ ] #184: `.menu-placeholder` rule deleted
- [ ] #183: Crafting hub button disabled while game over, with no hint; the blanking comment rewritten without the issue number
- [ ] #176: "Replay this seed" after Restart on the game-over screen
- [ ] #181: device drain over every item list; log line by location as tabled
- [ ] #180: `battery` removed from `walkie_talkie`
- [ ] #195: `backfillRegistryTags()` on load, covering list items and slot objects; the schema comment rule
- [ ] #173: the reachability comment rewritten without count, version or issue numbers

## Explicitly out of scope

- **#167** (tag-driven Disassemble). It has its own design questions: the
  tag name, full reversibility, and per-item log text. It gets its own
  pass. #195 removes its save seam once shipped, but it is not
  implemented here. `campfire_kit` gets no tag.
- The walkie-talkie as a working device (`device` tag, battery controls).
  Also a salvage action to cannibalise its batteries.
- A `gameOver` guard in `doCraft()`. The disabled button and the blanked
  catalogue keep the question moot.
- Resyncing **container** tags. Containers are world instance data, not
  registry entries.
- A log line for devices outside the current room, or any notification of
  them.
- Showing the seed on the game-over screen. It stays in Options.

## Sections touched

- **RENDERING**: `hereNote()`, `render()`'s game-over branch, the hub-row
  build / Crafting button state, `<style>`
- **SIMULATION**: `applyWorldTicking()`
- **WORLD DATA**: `walkie_talkie`'s registry entry, plus the ITEM DATA
  SCHEMA comment
- **PERSISTENCE**: `backfillRegistryTags()`, `applyLoadedData()`, and
  the comment above `validateReachability()`
- `forEachItemList()`, only if decision (b) above is taken

## UI changes

- **Here group:** the dim notes (locked door, sleep cooldown, nothing to
  light a fire) are half a pixel smaller and a pixel less padded.
- **Game-over screen:** two buttons, Restart then Replay this seed.
- **Drawer after death:** Crafting is greyed out and does nothing.
- **Log:** a device switched on in the room you're in now says "The … runs
  out of battery and shuts off." when it dies.
- **Batteries:** "Replace batteries" is no longer offered for a
  walkie-talkie. In old saves this applies once they're loaded.

## Dependencies / issue linkage

Closes #173, #176, #180, #181, #183, #184, #193, #195. #167 stays open, and
#195 unblocks its save seam. Nothing is expected to be deferred. File
anything that surfaces anyway.

## Validation the coding session should show

- `git diff origin/main...HEAD -- ashfall.html` touches only the sections
  listed above.
- `ashfallDev.validateReachability()` output is unchanged: 10 dead pools,
  11 unreachable items, and the same tool-tag lines.
- **#195 and #180 on an old save.** Take a v0.7.1 save carrying a
  walkie-talkie (tagged `battery`) and a portable radio, with no spare
  batteries. After loading it, the walkie-talkie has no `tags` and the
  radio's controls offer no "Replace batteries".
- **#181.** Switch on a radio on the current room's floor, or in a stowed
  bag, then wait. It drains and logs the right line. One in another room
  drains silently.
- **#183 and #176.** After game over, Crafting is disabled. Replay this seed
  restarts with the same `state.seed`, and Crafting is enabled again.

## Open questions for Tom

None.

## After implementation

Open one pull request carrying:

- the PATCH bump;
- a `CHANGELOG.md` entry naming `handoffs/tier-0-sweep.md` and recording
  the three implementation decisions;
- `Closes` lines for all eight issues;
- this file moved with `git mv` to `handoffs/archive/tier-0-sweep.md`.
