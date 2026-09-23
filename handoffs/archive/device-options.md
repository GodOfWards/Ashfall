# Ashfall Handoff — Device Options: a `device` tag, container tags, and the stove's controls in their own panel

Current shipped version: v0.6.3
Implied version-change type: MINOR
Issues: #161 — Device Options — a third menu layer for tagged items and fixtures, opened in the side menu
        #177 — Apartment 1A's stove is `stove1a`, so lighting it adds a second "Stove" tab and Cook only sees the new one

## Before you start: this handoff depends on another

**`handoffs/menu-hub.md` (#157, #158, #160) must have shipped first.** This
handoff was written at v0.6.3, before that pass existed. It builds on three
things that pass adds:
- the item pop-up;
- the layer stack with Esc and focus;
- the Crafting panel's result area.

If `handoffs/menu-hub.md` is still at the top level of `handoffs/`, it has not
shipped. **Stop.**

If it has shipped, re-check every premise in **"Re-verify before implementing"**
against the file you have open before writing any code. Line numbers below are
v0.6.3's and will have moved. What matters is whether each *statement* is still
true. If one is false in a way that changes the design, stop and ask Tom rather
than adapting silently. (This is #152's staleness risk, handled by hand.)

## What this is

**Layer 3 of the three-layer item model** adopted from Project Zomboid:
1. the item lists;
2. the interaction pop-up (#157);
3. **Device Options**, a panel for things whose controls go beyond picking them
   up.

From #161:

> A tag decides what is a device. Items and room fixtures that get it gain a
> "Device Options" entry.

This pass:
1. **Adds a `device` tag.** The portable radio and the four stoves carry it.
2. **Gives containers tags,** with the same field, shape and vocabulary items
   already use. That fixes **#177** at the root: heat containers are found by a
   `heat` tag, not by their ids.
3. **Moves the radio's controls and the stove's Light / Turn off** into a
   full-screen Device Options panel.
4. **Removes `room.hasStove`,** which would otherwise say what the tagged stove
   container already says.

**Why MINOR.** Tom chose MINOR over a load-time backfill (#161, persistence
option (b)):
- saved items are deep copies of their registry entry, tags included;
- `serializeGame()` writes `world` whole;
- so new tags on registry items and authored containers never reach an existing
  save.

Instead of patching old saves, `SAVE_KEY` rotates.

## Relevant existing state

Verified against `ashfall.html` at v0.6.3. Line numbers are that file's.

**Item devices.**
- `flashlight` (`:576`) and `portable_radio` (`:605`) are the only items with
  `durability.mode:"time"`. Both carry `on`, `hasBatteries` and `drainRate`, and
  neither has tags.
- `getItemActions()` (`:4229`) offers their controls in one block (`:4283`), gated
  on the **property** `it.durability && it.durability.mode === "time"`:
  - `Turn on` / `Turn off` and `Remove batteries`, while `hasBatteries !== false`;
  - `Replace batteries`, while `countByTag("battery") >= 1`.
- All three controls are silent: they flip state and call `render()`, and the
  comments say the detail view's status line shows the result.
- The block is **not gated by side**, so the controls work on world items too.
- The detail view's status line for these items (in `renderCraftPanel()` at
  v0.6.3; in the hub pass's pop-up after it) reads `No batteries installed` or
  `N% charge — On/Off`.

**Tags today.**
- Items carry `tags` (an array of capability strings). They are read through
  `hasTool(tag)` (`:4064`), `countByTag()` (`:3980`) and `consumeByTag()`
  (`:3983`), all over `invPools()`.
- **No container carries a `tags` field anywhere.** The CONTAINER SCHEMA comment
  (`:460`) lists `id, name, capacityKg, items`, `locked`, `breakTag` and the spawn
  fields.
- The item tag `heat` exists on `propane_torch` (`:627`) only, and is read by
  `roomHasHeat()` (`:4029`) through `hasTool("heat")`.

**Fixture devices: the stove.**
- **The room flag.** `hasStove:true` is on four rooms: `kitchen` (`:1302`),
  `twobee_kitchen` (`:1403`), `onea_kitchen` (`:1504`) and `onebee` (`:1563`). All
  four also carry `cannotHaveFire:true`, and none has a `searchLabel`.
- **The authored containers.** Each of those rooms authors a stove container
  named `"Stove"`: `id:"stove"` at `:1304`, `:1405` and `:1565`, and
  **`id:"stove1a"` at `:1506`**. None is locked.
- **Lighting it.** `doLightStove()` (`:4893`):
  1. spends a match use;
  2. calls `ensureHeatContainer(room, "stove", "Stove", HEAT_CONTAINER_CAPACITY_KG)`,
     which creates a container with id `"stove"` if the room has none;
  3. sets `room.heatActive`, spends `LIGHT_STOVE_MIN`, and logs "You light the
     stove."
- **Turning it off.** `doExtinguish()` (`:4941`) clears `heatActive` and logs "You
  put it out." The campfire shares it.
- **Finding the heat container.** `getHeatContainer()` (`:4963`) is
  `room.containers.find(c=> c.id==="stove" || c.id==="campfire")`.
- **#177's bug.** In `onea_kitchen`, lighting the stove creates a second, empty
  "Stove" tab, and Cook only sees that one.
- **The Here group** (`render()`'s here-actions code, `:6545`–`:6581`):
  - `hasStove && !heatActive && hasMatchUses()` → "Light the stove (5 min)";
  - `hasStove && !heatActive` otherwise → the note "Nothing you're carrying will
    light it.";
  - `heatActive` → `hasStove ? "Turn off the stove" : "Put out the fire"`;
  - "Add fuel", when the fire has `fireMinutesLeft` and room under the cap;
  - "Cook the …" per `HEAT_RECIPES`, against `getHeatContainer()`.

  The comment at `:6545` says every `hasStove` room also carries
  `cannotHaveFire`.

**Fixture devices: the campfire** (not a device; context only).
- `doBuildFire()` (`:4907`) creates its container with
  `ensureHeatContainer(room, "campfire", "Campfire", HEAT_CONTAINER_CAPACITY_KG)`.
- `doDismantleCampfire()` (`:4947`) finds and removes that container by the id
  `"campfire"`. That id is assigned by code, not authored.

**The Here panel.**
- The markup is `<h2>Here <span class="sub" id="worldWeight"></span></h2>`
  (`:196`).
- `renderWorldItemsPanel()` (`:6623`):
  - builds tabs from Floor plus unlocked containers;
  - falls back to Floor when `worldTab` no longer resolves;
  - resolves the current tab through `worldSlot(room, worldTab)`.
- **The precedent for a context button.** The Inventory header carries
  `#unequipBtn`, a `button.mini` shown only while the selected inventory tab is
  an equipped bag (`renderInventoryPanel()`, `:6614`).

**Loading.** `applyLoadedData()` (`:5192`) loads a save from another `MAJOR.MINOR`
with only a logged warning ("…it may not load correctly."). An Import of a
pre-change save will therefore load without container tags. That is the
consequence of option (b), accepted, and not repaired.

## Re-verify before implementing

Each line is a premise this design rests on. Check each against the file you
have open.
- [ ] The hub pass has shipped. Its item pop-up renders `getItemActions()`, and
      it stays open **beneath** the drawer when the drawer opens.
- [ ] The hub pass's layer stack exists: Esc closes the topmost layer, focus
      moves in on open and back on close, and one more full-screen layer can be
      pushed.
- [ ] The hub pass's Crafting result area exists. Note how it captures "the log
      entries an action wrote", because D reuses it.
- [ ] `getItemActions()`'s battery block is still one block gated on
      `durability.mode === "time"`, with the three controls above and nothing
      new.
- [ ] Still no container anywhere carries `tags`.
- [ ] `hasStove` still appears only in the ROOM schema comment, the four rooms
      and `render()`'s here-actions stove code.
- [ ] `getHeatContainer()`, `ensureHeatContainer()`, `doLightStove()`,
      `doExtinguish()` and `doDismantleCampfire()` are as described above.
- [ ] Every `hasStove` room still carries `cannotHaveFire` and one authored
      container named "Stove".
- [ ] "Cook the …" is still a Here-group button. If **#178 (passive cooking)**
      has shipped, Cook has changed shape. This pass still doesn't touch it, but
      check that #178's heat-container lookup follows C.
- [ ] `#unequipBtn` in the Inventory header is still the context-button
      pattern.
- [ ] No pass since v0.6.3 has already rotated `SAVE_KEY` for an unrelated
      reason. The bump is MINOR either way; this is only so the changelog tells
      the truth about why.

## Rules / mechanics

### A. The `device` tag

- **`device` means "has controls beyond take and store, kept in Device
  Options."** It describes the thing, as `blunt` and `fishing` do.
- **Carried by:**
  - `portable_radio`, in `ITEM_REGISTRY`: `tags:["device"]`;
  - the four authored stove containers, as `tags:["device","heat"]` (B).
- **Not carried by `flashlight`** (Tom). Like Zomboid's, it has no panel. Its
  Turn on/off and battery controls stay in the pop-up.
- **How `getItemActions()` changes:**
  - For an item **tagged `device`**, the battery block is not offered. One action
    is offered in its place: **"Device Options"**, which opens the device panel
    for that item (D).
  - For an item **not tagged `device`** that meets the existing
    `durability.mode === "time"` gate (the flashlight), nothing changes.
  - The battery controls' logic is defined **once** and used by both the
    pop-up's flashlight path and the device panel. Moving the closures out of
    `getItemActions()` into one shared function is the obvious shape. There must
    not be two copies of Turn on / Remove / Replace.
- This is the "one case that touches both" (CLAUDE.md): the tag is the
  mechanic's own definition data. Adding new devices to the world (a car radio, a
  TV, a walkie-talkie) is content and is **not** part of this pass.

### B. Container tags

- **Containers gain an optional `tags` field.** It has the same shape as items'
  (an array of capability strings) and the **same vocabulary**. A tag means the
  same thing on a container as on an item.
- **One shared helper** answers "does this thing carry this tag?" for items and
  containers alike, for example `hasTag(thing, tag)`.
  - New code reads container tags only through it.
  - `hasTool()`, `countByTag()` and `consumeByTag()` may use it internally, as
    long as their behaviour is unchanged.
- **Tags used on containers in this pass:**
  - `heat`: the container is a heat source's cooking space. Stoves and
    campfires.
  - `device`: the container has Device Options. Stoves only.
- **The CONTAINER SCHEMA comment documents `tags`,** with those two values and
  what reads them.
- **Authored data.** The four stove containers get `tags:["device","heat"]`:
  `kitchen`, `twobee_kitchen` and `onebee` at `id:"stove"`, and `onea_kitchen` at
  `id:"stove1a"`.
- **Code-created data.**
  - `ensureHeatContainer()` gains a way to set tags on the container it creates.
  - `doBuildFire()` creates the campfire container with `tags:["heat"]`.
  - `doLightStove()` no longer calls `ensureHeatContainer()` at all (C).
- **#15's planned property flags** (`movable`, `disassemblable`) would be more
  tags in this same array. This pass adds none of them.

### C. Heat lookup by tag, and `hasStove` removed (#177)

- **`getHeatContainer(room)`** returns the room's first container tagged `heat`.
  The id comparison is gone.
- **"The room's stove"** is the room's container tagged both `device` and `heat`.
  One helper returns it, or nothing. Every stove question asks that helper.
- **`room.hasStove` is removed** (Tom):
  - from the ROOM schema comment (`:448`);
  - from the four rooms;
  - from every reader, which asks the stove helper instead.
- **`doLightStove()`** acts on the room's stove:
  - it returns without effect if the room has none;
  - otherwise it spends a match use, sets `heatActive`, spends `LIGHT_STOVE_MIN`
    and logs "You light the stove." as today;
  - it **never creates a container.** In `onea_kitchen` that is exactly #177's
    fix: no second "Stove" tab, and Cook finds `stove1a` by its tag.
- **`doExtinguish()`** is unchanged.
- **`doDismantleCampfire()`** still finds the campfire container by its id
  `"campfire"`. That id is assigned by code in `doBuildFire()`, not authored, so
  it is not a name check. Leave it.
- **Rewrite the comment at `:6545`** ("every hasStove room also carries
  cannotHaveFire") so it describes the stove helper, not the removed field.

### D. The Device Options panel

- **It is a full-screen panel over the drawer,** following the hub convention.
  Opening it opens the drawer, if it is not already open, and pushes the device
  panel above it.
- **Its target is identified explicitly,** never by position:
  - **item target:** its `_uid`, resolved through `findItemByUid()` on every
    render;
  - **container target:** its `id`, resolved against the **current room's**
    `containers` on every render.
- **If the target no longer resolves, the panel closes.**
- **Closing returns to where it was opened from** (Tom):
  - opened from the item pop-up → back to the pop-up;
  - opened from the Here header → back to play.

  In both cases the device panel **and the drawer** close together, as one step.
  Esc does the same in one press. Focus returns to the Device Options control
  that opened it.
- **Game over, load and restart close it,** with every other layer (the hub
  pass's rules).
- **Content for an item target:**
  - a heading with the item's name;
  - the **status line**, with exactly the text the pop-up shows: `No batteries
    installed` or `N% charge — On/Off`. Take it from one shared function, not a
    second copy of the ternary;
  - the controls from A's shared battery function, with today's availability
    rules unchanged.
- **Content for the stove:**
  - a heading with the container's `name` ("Stove");
  - a status line, **`On`** while `room.heatActive`, **`Off`** otherwise;
  - the controls:
    - not lit and `hasMatchUses()` → **"Light the stove (5 min)"**, the same label
      and `fmtDuration(LIGHT_STOVE_MIN)` as today, calling `doLightStove()`;
    - not lit and no fire-starter → the note **"Nothing you're carrying will
      light it."**, as today;
    - lit → **"Turn off the stove"**, calling `doExtinguish()`.
- **After a control runs, the panel stays open** (Tom). The status line updates,
  and the panel shows **Crafting's result area**: every log entry that control
  wrote, including entries updated in place, replaced on the next control and
  cleared when the panel closes.
  - Reuse the hub pass's mechanism. Don't build a second one.
  - The radio's controls write nothing, so their result area stays empty and the
    status line carries the change, as today.

### E. How Device Options is reached

- **An item:** the **"Device Options"** entry in its pop-up (A). It works the
  same whether the item is in the Inventory or the Here panel. Item controls
  aren't gated by side today, and that stays true.
- **A fixture** (Tom): **the selected Here tab is the focus.** While the selected
  tab resolves to a container tagged `device`, a **"Device Options"**
  `button.mini` shows in the **Here panel header**, beside `#worldWeight`. It
  follows the Inventory header's `#unequipBtn` pattern, and is hidden on every
  other tab. Tapping it opens the device panel for that container.
- **The Here group loses the stove's controls:** Light, the "Nothing you're
  carrying will light it." note, and "Turn off the stove". What remains:
  - **"Put out the fire"**, shown while `heatActive` and the room has no stove.
    That is the campfire; its label logic now reads the stove helper instead of
    `hasStove`;
  - **"Add fuel to the fire"**, unchanged;
  - **"Cook the …"**, unchanged, and still in the Here group (Tom). It will be
    replaced by #178, not by this pass;
  - every campfire control, unchanged. The campfire is not a device (Tom).

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

- **The shared tag helper's name and signature** (`hasTag(thing, tag)` is a
  suggestion), and whether `hasTool()` / `countByTag()` / `consumeByTag()` are
  rewritten to use it. Either is fine if their behaviour is unchanged.
- **The stove helper's name** (for example `roomStove(room)`).
- **The device-target variable's shape**, for example
  `{ kind:"item", uid } | { kind:"container", id }`. It is UI-only, lives beside
  `detailItem`, and is never saved.
- **How `ensureHeatContainer()` takes tags:** an extra parameter, or the caller
  sets them on the returned container.
- **Whether the device panel shares the hub pass's full-screen panel element** or
  has its own. Follow whatever that pass chose if it made sharing easy.

## Data / schema changes

- **ITEM_REGISTRY:** `portable_radio` gains `tags:["device"]`. No other item
  changes.
- **ITEM DATA SCHEMA comment:** `device` joins the list of tags read by a
  mechanic.
- **CONTAINER SCHEMA:** new optional `tags` field, documented with the `heat` and
  `device` values and their readers.
- **WORLD DATA:**
  - the four stove containers gain `tags:["device","heat"]`;
  - `hasStove:true` is removed from the four rooms;
  - no room, placement, description or container is added. The `stove1a` id is
    **not** renamed, because the tag makes it work.
- **ROOM schema comment:** `hasStove` removed.
- **PLAYER STATE:** nothing. The device-target variable is UI-only.
- **Persistence:** **MINOR**, and `SAVE_KEY` rotates. There is no load-time
  backfill (Tom). An Import of a pre-change save loads with the existing version
  warning and without container tags. Stoves in such a save have no Device
  Options, and the changelog says so.

## In scope

- [ ] The `device` tag on `portable_radio`; the pop-up's "Device Options" entry
      replaces its battery controls.
- [ ] The flashlight unchanged in the pop-up.
- [ ] One shared definition of the battery controls, and one of the status line.
- [ ] Container `tags` per B, with the shared helper and the schema comment.
- [ ] `getHeatContainer()` by `heat` tag; the stove helper; `doLightStove()`
      without `ensureHeatContainer()`.
- [ ] `hasStove` removed everywhere.
- [ ] The Device Options panel per D, for item and container targets.
- [ ] The Here-header "Device Options" button per E.
- [ ] Stove controls removed from the Here group; campfire and Cook unchanged.
- [ ] Onea kitchen (#177) checked by hand: one "Stove" tab before and after
      lighting, and Cook offered for a raw fish placed in it.
- [ ] Stale comments rewritten (`:6545`, and any that describe the battery block
      or the stove buttons as living in the Here group or the pop-up).

## Explicitly out of scope

- **#178** (passive cooking) and **#179** (burning, unattended fires). Cook is
  not touched.
- **#180**: the walkie-talkie's `battery` tag. Replace batteries' consumption
  rule is unchanged.
- **#181**: devices draining outside the inventory. `applyWorldTicking()` is
  unchanged.
- **New devices** (a TV, a car radio, a walkie-talkie as a device). Those are
  content.
- **#15**'s `movable` / `disassemblable` flags and the respawn trigger.
- **#128**: container `kind`.
- **#96**: the propane torch and what counts as heat. `roomHasHeat()` is
  unchanged.
- The campfire as a device.
- A load-time backfill of tags into old saves (Tom: option (b)).
- **#78**: ARIA.

## Sections touched

- **ITEM DATA / WORLD DATA:** definition data only. The radio's tag, the stove
  containers' tags, `hasStove` removed, and the schema comments.
- **INVENTORY / ITEM SYSTEM:** `getItemActions()` (Device Options entry; the
  battery block moved to one shared definition) and the shared tag helper.
- **FIRE / COOKING:** `getHeatContainer()`, `ensureHeatContainer()`,
  `doLightStove()`, and the stove helper.
- **EVENTS / UI HELPERS:** opening and closing the device layer, using the hub
  pass's layer stack.
- **RENDERING:** the device panel; the Here header's button in
  `renderWorldItemsPanel()`; the stove controls removed from the here-actions
  code.
- **`<style>`:** whatever the device panel needs beyond the hub pass's panel
  styles.
- **PERSISTENCE:** no code change. `SAVE_KEY` rotates through the version bump.

## UI changes

- **The radio.** Its pop-up shows its status line and **"Device Options"**
  instead of Turn on/off and the battery buttons. Those live in the Device
  Options panel.
- **The flashlight.** Unchanged.
- **In a kitchen.** Selecting the **Stove** tab in the Here panel shows a
  **"Device Options"** button in the panel's header. The panel shows `On`/`Off`
  and Light the stove / Turn off the stove.
- **The Here group.** It no longer shows "Light the stove", its note, or "Turn
  off the stove".
- **Apartment 1A's kitchen.** It keeps one Stove tab after lighting, and cooking
  works there (#177).
- **Functional text introduced:** **"Device Options"**, and the stove's status
  **"On"** / **"Off"**. It's held to clarity and retunable.

## Dependencies / issue linkage

- Fulfils **#161** and **#177**. The pull request carries `Closes #161` and
  `Closes #177`.
- Depends on **`handoffs/menu-hub.md`** (#157, #158, #160), which must ship
  first.
- #14 (vehicles) will add a car radio as a future fixture device. Nothing is
  needed now.
- Anything deferred during implementation is filed as a new issue at the wrap.

## Open questions for Tom

None. All were answered in the planning session at v0.6.3, and the answers are
recorded on #161 and #177. If a premise in "Re-verify before implementing" turns
out false, that becomes a new question. Ask it; don't resolve it.

## After implementation

Open a pull request with:
- `GAME_CONFIG.VERSION` bumped (**MINOR**, starting PATCH at 0);
- a new `CHANGELOG.md` entry naming this handoff by path. It states that
  `SAVE_KEY` rotates and existing browser saves stop auto-loading, that Import of
  an older save loads without stove Device Options, which premises were
  re-verified, and the implementation decisions above;
- this handoff moved to `handoffs/archive/` with `git mv`;
- `Closes #161` and `Closes #177`.
