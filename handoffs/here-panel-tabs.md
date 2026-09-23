# Ashfall Handoff — Here panel tabs: floor bags, visible devices, and the backfill comments

Current shipped version: v0.7.2
Implied version-change type: PATCH. Nothing is added to `state`, to any saved
item or to any saved room. The floor-bag tab key lives in `worldTab`, which is
UI-only and never saved, and a bag's `contents` is a field saves already carry.
Issues: #169, #188, #197

## What this is

Three small fixes, shipped as one PATCH:

- **#169.** A bag lying on a room's floor opens as a tab in the Here panel, so
  you can take from it and store into it there.
- **#188.** A container tagged `device` is a Here tab whether or not the room
  has been searched. Today 1B's stove can't be lit until you "Search the unit",
  though the room description says it sits in the corner.
- **#197.** Comment-only drift in PERSISTENCE: a count and three ordinals that
  went stale.

#169 and #188 both edit the tab list in `renderWorldItemsPanel()`, which is why
they ship together. #197 rides along because it is comment-only.

A second handoff, `handoffs/carry-load.md`, was written in the same planning
session and must be implemented **after** this one. See "Dependencies".

## Relevant existing state

Verified against `ashfall.html` at v0.7.2. Line numbers are only a guide; find
each item by its function name.

- **`renderWorldItemsPanel()`** (RENDERING, ~7226):
  - It builds `worldTabDefs` as `[["floor","Floor"]]`.
  - Then, only when `!room.searchLabel || room.searched`, it adds
    `[c.id, c.name]` for each unlocked `room.containers` entry.
  - Then it adds each `room.carContainers` entry while `!room.carLocked`.
  - A tab's click handler looks the key up in `room.containers` or
    `room.carContainers`. On a match it calls `doOpenContainer(room, c)`.
    Otherwise it sets `worldTab = key` and renders.
  - **After** building the buttons, and after `revealActiveTab()`, it falls
    back with `if(!worldTabDefs.find(d=>d[0]===worldTab)) worldTab = "floor";`.
    So in the render where the fallback fires, no tab button carries
    `.active`.
  - The header is
    `totalWeight(currentWorld.items).toFixed(2) + " / " + currentWorld.capacityKg + " kg"`,
    with no guard for a missing capacity.
  - The Device Options button shows when
    `room.containers.find(c=> c.id === worldTab)` is tagged `device`.
- **`worldSlot(room, tab)`** (INVENTORY / ITEM SYSTEM, ~4192) resolves:
  - `"floor"` → `{ items:room.floor, capacityKg:room.floorCap }`;
  - otherwise a `room.containers` id, then a `room.carContainers` id →
    `{ items:c.items, capacityKg:c.capacityKg }`;
  - anything else → `null`.

  `doTake()`, `doStore()`, `doConsume()`, `doOpen()` and `doEquip()` all
  resolve their world side through `worldSlot(room, worldTab)`.
- **`doStore()`** refuses with "That won't fit there." when
  `dst.capacityKg && totalWeight(dst.items) + moveQty*itemUnitWeight(it) > dst.capacityKg`.
  `renderInventoryPanel()` labels the store button `worldTab === "floor" ? "Place" : "Store"`.
  `getItemActions()` makes the same choice (~4389).
- **`findItemByUid(uid)`** (~3839) searches `invPools()`, then every room's
  `floor`, `containers[].items` and `carContainers[].items`. It never looks
  inside an item's `contents`. `renderItemPop()` resolves the open item
  through it and closes the pop-up when it returns `null`.
- **Bags.** The five equippable bags are the `ITEM_REGISTRY` entries with a
  `slotType`: `worn_backpack`, `duffel_bag`, `purse`, `fanny_pack` and
  `tote_bag`. All are `category:"Container"`, and `"Container"` is not in
  `STACKABLE`, so every bag is its own row with its own `_uid`. A bag from the
  registry has **no** `contents` field. `contents` appears only when
  `doUnequip()` builds the item. `doEquip()` reads `it.contents || []`.
- **The dropped keychain.** `doUnequip()`'s fallback branch builds a bag-shaped
  item for a slot with no `itemId`, which means the keychain:
  `{ name, category:"Container", qty:1, unitWeight, slotType:slotKey, capacityKg:slot.capacityKg, contents }`.
  The keychain's `capacityKg` is `null`. The Unequip button is offered for
  every `CONTAINER_SLOTS` tab, keychain included, so a player can unequip the
  keychain and put it on a floor. `keychainAllows()` is enforced only when
  `invTab === "keychain"`.
- **`doOpenContainer(room, container)`** (~4770) sets `worldTab` and rolls loot
  once for a container with `spawnPools` and no `spawnRolled`.
- **`doSearch()`** (~4684) spends `room.searchMinutes` and sets
  `room.searched`. It logs
  `"You search the place carefully. You find: " + <every room.containers name, lower-cased, comma-joined> + "."`
  as `"good"`.
- **`renderHereActionsPanel()`** shows the search button while
  `room.searchLabel && !room.searched`. Its "Cut the lock on …" loop is
  search-gated too. This pass doesn't touch either.
- **Rooms with a search.** There are four (`searchLabel:` appears four times).
  Only `onebee` (Apartment 1B, "Search the unit") has a container tagged
  `device`. Its containers, in order, are Stove (`tags:["device","heat"]`),
  Tool Cabinet, Desk and Closet.
- **`roomStove()`, `getHeatContainer()` and the Device Options panel** all
  read `room.containers` directly and ignore the search already. The only
  gate on 1B's stove is the tab list.
- **PERSISTENCE comments (#197).** `applyLoadedData()` runs
  `resyncUidCounter()`, then seven backfills: `backfillItemIds()`,
  `backfillSlotItemIds()`, `backfillRegistryTags()`, `backfillLocationIds()`,
  `backfillContainerFields()`, `backfillRoomAddresses()` and
  `backfillIllnessScale()`.
  - The comment above `validateLoadedWorld()` says it covers the shapes that
    make "`resyncUidCounter()`, the three backfills or `render()` throw".
  - `backfillRoomAddresses()`'s comment opens "third companion to
    `backfillLocationIds()`".
  - `backfillSlotItemIds()`'s opens "fourth companion to `backfillItemIds()`".
  - `backfillIllnessScale()`'s opens "sixth companion to
    `backfillItemIds()`".
  - `backfillRegistryTags()`'s opens "companion to `backfillItemIds()`", with
    no ordinal.

## Rules / mechanics

### #169: a bag on the floor is a tab

- **Which items get a tab:** every item on the **current room's** `floor`
  that has a `slotType` **and** a numeric `capacityKg`. That is every
  registry bag.
  - A dropped keychain has `capacityKg:null`, so it gets no tab. Its keys
    stay reachable by picking it up and equipping it again. This keeps
    `keychainAllows()` from needing a second enforcement point.
  - Bags in room containers, car containers, other bags or the inventory get
    no tab. Their contents stay out of reach until the bag is dropped or
    equipped.
- **Tab order:** Floor, then floor-bag tabs in floor order, then the room's
  containers, then car containers.
- **Visibility:** floor-bag tabs show whether or not the room has been
  searched. The bag is on the floor, and Floor is never gated.
- **Label:** the bag's `name`. When two or more floor bags share a name, the
  first in floor order keeps the plain name and later ones are numbered from 2:
  "Purse", "Purse 2", "Purse 3".
- **Key:** the bag's `_uid` (via `ensureUid()`), never its floor index. It is
  prefixed so it can't collide with an authored container id. See the
  implementation decisions below.
- **Resolution:** `worldSlot(room, tab)` resolves a floor-bag key by finding
  the item with that `_uid` in `room.floor` and returning
  `{ items: bag.contents, capacityKg: bag.capacityKg }`. A bag with no
  `contents` gets `contents = []` on resolve. That field already exists on
  unequipped bags and is saved and walked by `forEachItemList()`. Because
  every transfer routes through `worldSlot()`, Take, Store, Eat/Drink, Open
  and Equip all work from a floor-bag tab with no new action code.
- **Capacity:** storing into a floor bag is checked against the bag's own
  `capacityKg` only, not against the room's `floorCap`. `giveItem()` already
  lets a floor go over its cap, and the bag's contents take no extra floor
  space.
- **Header:** the Here header on a floor-bag tab reads `<contents weight> / <capacityKg> kg`,
  the same format as a container's.
- **Store label:** "Store", like any non-floor tab. The existing
  `worldTab === "floor"` tests already give this.
- **No loot roll.** A floor-bag tab never calls `doOpenContainer()`. The click
  handler's container lookup already misses a bag key. Keep it that way.
- **The tab going away:** take the bag, equip it from the floor, or store it
  into a container, and its tab disappears. The existing fallback to Floor
  covers it, but it runs after the buttons are built. **Move the fallback
  above the button loop**, so the render that drops the tab also marks Floor
  as active. This fixes a latent quirk that any disappearing tab already
  hits.
- **`findItemByUid()`** also searches the `contents` of every floor bag in the
  **current room** (bags meeting the tab rule above), one level deep. It does
  not search bags elsewhere. Without this, opening an item's pop-up from a
  floor-bag tab closes it at once.

### #188: devices are always a tab

- In `renderWorldItemsPanel()`, an unlocked container tagged `device` is a
  tab whether or not the room has been searched. Other containers stay gated
  as today.
- Order is the containers' authored order. Before a search only the device
  tabs are in it. After a search every unlocked container is in it. 1B's
  Stove is first either way.
- **The search line lists only what the search revealed.** `doSearch()`
  leaves out containers tagged `device`. In 1B: "You search the place
  carefully. You find: tool cabinet, desk, closet."
- **If nothing is left to list:** `doSearch()` logs "You search the place
  carefully. You find nothing else." as `"good"`. No room reaches this today;
  it guards a future content pass. The wording is retunable.
- The Device Options button, `roomStove()` and cooking need no change.

### #197: comments carry no count

- `validateLoadedWorld()`'s comment: "the three backfills" becomes "the
  load-time backfills". Leave the rest of the comment as it is.
- Drop the ordinals:
  - `backfillRoomAddresses()`: "third companion to `backfillLocationIds()`"
    → "companion to `backfillLocationIds()`".
  - `backfillSlotItemIds()`: "fourth companion to `backfillItemIds()`" →
    "companion to `backfillItemIds()`".
  - `backfillIllnessScale()`: "sixth companion to `backfillItemIds()`" →
    "companion to `backfillItemIds()`".

  Re-wrap the lines as needed. Change no other words.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

1. **The floor-bag tab key's prefix.** Container ids are authored strings and
   uids are `"u" + n`. Recommended: `"bag:" + uid`. It can't be mistaken for a
   container id, and a floor-bag key is recognisable with `startsWith`.
2. **Where the floor-bag list is computed.** `renderWorldItemsPanel()`,
   `worldSlot()` and `findItemByUid()` all need the same answer to "which
   floor items are open bags". Recommended: one helper in INVENTORY / ITEM
   SYSTEM (e.g. `floorBags(room)`) that all three call. The rule is then
   written once.
3. **Where `contents = []` is created.** Either in `worldSlot()` on resolve,
   as specified above, or in `doStore()` on first store with `worldSlot()`
   returning a fresh empty array before that. Either works. Pick one and name
   it.

## Data / schema changes

None. No state field, no item or container schema field, no tag, and no
WORLD DATA edit.

## In scope

- `floorBags()` or its equivalent, used by the tab list, `worldSlot()` and
  `findItemByUid()`.
- The tab list's device rule, floor-bag tabs and moving the fallback earlier.
- `doSearch()`'s filtered list and its empty-list line.
- Four comment edits in PERSISTENCE.

## Explicitly out of scope

- **#167** (Disassemble). It was shelved in this planning session; Tom will
  make its yields depend on category.
- **Carry load** (#168, #170): `handoffs/carry-load.md`, implemented after
  this.
- Opening a bag that sits in a room container, a car container or another
  bag. Tom's model keeps those closed.
- Any "visible without search" container tag (#15). The rule keys off the
  existing `device` tag.
- Reachable crafting (#119) and container `kind` (#128). A floor bag is one
  more container "in reach" for #119. Nothing here builds toward it.

## Sections touched

- INVENTORY / ITEM SYSTEM: `worldSlot()`, `findItemByUid()` and the new
  helper.
- WORLD INTERACTION: `doSearch()`.
- RENDERING: `renderWorldItemsPanel()`.
- PERSISTENCE: comments only.

No WORLD DATA, no SIMULATION, no CRAFTING.

## UI changes

- **Here panel:** a bag on the floor has its own tab after Floor. It is named
  after the bag, and numbered when two share a name. Its header shows how full
  the bag is. Take and Store work there as in any container.
- **1B:** the Stove tab and its Device Options button show before the unit is
  searched. The search line no longer lists the stove.
- **Log:** a room whose search reveals nothing new says "You find nothing
  else." No room does this yet.

## Dependencies / issue linkage

Closes #169, #188, #197.

`handoffs/carry-load.md` depends on this one. Its hard-limit check on Take and
Equip reads from `worldSlot()`, which is how it reaches floor-bag tabs. Nothing
here depends on it.

File anything that surfaces during implementation. Nothing is expected to be
deferred.

## Validation the coding session should show

- `git diff origin/main...HEAD -- ashfall.html` touches only the sections
  listed above.
- **Floor bags:**
  1. Drop two purses in a room. The tabs read "Purse" and "Purse 2", after
     Floor.
  2. Store into "Purse 2". The header shows its fill against 5 kg.
  3. Take the first purse. Its tab goes, and the remaining one is now
     "Purse". If a tab was open, Floor is marked active in the same render.
  4. An item's pop-up opened from a floor-bag tab stays open.
- **The keychain:** unequip it and drop it. It gets no tab.
- **No roll:** a floor bag's tab never adds loot.
- **1B, new game:** the Stove tab and Device Options show before the search,
  and the stove lights. Searching logs "You find: tool cabinet, desk,
  closet."
- **Saves:** a v0.7.2 save loads unchanged. A bag already on a floor in that
  save gets its tab.

## Open questions for Tom

None.

## After implementation

Open one pull request carrying:

- the PATCH bump;
- a `CHANGELOG.md` entry naming `handoffs/here-panel-tabs.md` and recording
  the three implementation decisions;
- `Closes #169`, `Closes #188` and `Closes #197`;
- this file moved with `git mv` to `handoffs/archive/here-panel-tabs.md`.
