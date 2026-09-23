# Ashfall Handoff — Menu hub: the item pop-up, the drawer hub with Crafting, and Options

Current shipped version: v0.6.3
Implied version-change type: PATCH
Issues: #157 — The item interaction menu becomes a pop-up at the item — today it borrows the Craft panel
        #158 — The side menu becomes a hub — Crafting opens full-screen, Health and Clothing as placeholders, the Craft panel leaves the page
        #160 — Options menu — opened from the side menu; the seed and Restart move into it

## What this is

Three rendering changes that together give the game its menu structure. They
ship as one pass because they share one convention, what a hub sub-menu is, and
because #158 can't ship without #157:

1. **#157.** Item actions move out of the Craft panel into a **pop-up at the
   tapped item**.
2. **#158.** The ☰ drawer becomes a **hub**. A row of buttons at the top opens
   sub-menus. **Crafting** opens full-screen, **Health** and **Clothing** are
   disabled placeholders, and the Craft panel leaves the page.
3. **#160.** **Options** is the hub's fourth button. It holds the seed, now
   copyable, and Restart. The drawer's Run section goes.

Nothing enters `state`. `RECIPES`, `canCraft()`, `doCraft()`, `getItemActions()`,
`seedFromInput()` and `doRestart()` are not changed; they are called from new
places.

**Sibling handoffs from the same planning session:**
- `handoffs/portrait-layout.md` (#159) edits the `<style>` block's layout rules
  and the `@media` query. This pass adds new rules to the same block and removes
  the Craft panel's markup. They touch no common line, and either can ship first.
- `handoffs/device-options.md` (#161) builds on this pass and **must ship after
  it**.

## Relevant existing state

Verified against `ashfall.html` at v0.6.3. Line numbers are that file's.

**The detail view (#157's starting point).**
- `detailItem` (`:3678`) is UI-only, `{ uid, side }`, and never saved. It is set by
  the `.itemname` button's click handler in `renderItemList()` (`:6326`).
- It is cleared on movement (`:4481`), load (`applyLoadedData()`, `:5219`) and
  restart (`doRestart()`, `:5596`).
- `doOpen()` re-points it at the opened unit (`:4179`).
- `renderCraftPanel()` (`:6361`) has two branches:
  - **`detailItem` set** (`:6365`): resolves it through `findItemByUid()`, and
    clears it and re-renders if the item isn't found. Otherwise it shows:
    - the name line;
    - the `category · N kg (N kg each)` line;
    - the durability line: `N/M uses`, `No batteries installed`, or
      `N% charge — On/Off`;
    - the `Sealed` / `Opened` line;
    - then one `button.action` per `getItemActions()` entry, each followed by a
      `<br>`, and `#craftBackBtn` (← Back).
  - **Otherwise** (`:6409`): the recipe catalogue. Every recipe shows, with
    unavailable ones disabled with `(needs …)`, and the comment explains why
    this list is a catalogue, not an action list.
- **Take All moves the item and clears the view.** `addToList()` gives every new
  stack entry a fresh `_uid` (`:3938`–`:3943`), so Take All removes the source
  uid. `findItemByUid()` then misses, and the view clears itself. Take 1 / Half
  leaves the source uid in place, and the view stays on it.
- `render()`'s game-over branch (`:6664`) clears `#craftBackBtn` and
  `#craftBody` by id. Those lines go with the panel.

**The drawer (#158 and #160's starting point).**
- `#sideMenu` markup (`:142`):
  - the `Menu ✕` heading;
  - **Save / Load**: save, load, export, import, and `#restartMenuBtn`;
  - **Stats** (`#statsBox`);
  - **Run** (`#runBox`);
  - **Map**.
- `openMenu()` / `closeMenu()` (`:5658`) toggle `.open` on `#sideMenu` and `.show`
  on `#menuBackdrop`. The backdrop's click closes the drawer.
- Z-order: `#menuBackdrop` is at `z-index:15`, and `#sideMenu` at `20`.
- Nothing listens for `keydown` anywhere in the file.
- `#menuToggle` sits in `<header>`, which `render()` never touches, so the drawer
  can still be opened on the game-over screen.
- `renderRunPanel()` (`:6659`) writes `Seed: N` into `#runBox`. `render()` calls it
  **before** its game-over branch, because that branch wipes `#statsBox` and the
  seed is what a player wants after dying (comment at `:6654`).
- `#restartMenuBtn`'s handler (`:5645`) runs a `prompt()`:
  - Cancel aborts;
  - blank calls `doRestart()`;
  - anything else calls `doRestart(seedFromInput(s))`.

  The comment above it records that Cancel is the destructive-action guard.
- Save, Load, Export and Import log to `#log` and leave the drawer open.

**Crafting's output.**
- `doCraft()` (`:4829`) spends `recipe.minutes` through `advanceTime()`, then
  `giveItem()`, then `log("You craft a …", "good", "craft:<id>")`.
- **`giveItem()` can log first.** It logs a warning when the output drops to the
  floor (`:4046`–`:4052`).
- **`advanceTime()` can log, and can end the run.** It runs the simulation, which
  logs its own lines, and sets `gameOver` at `:4682`.
- **`log()` (`:3866`) doesn't always append.** A call whose `key` matches the last
  entry **updates that entry in place** (a `×N` count, or a summary) instead of
  appending. So two crafts of the same thing in a row add no new element.

## Rules / mechanics

This is a rendering pass, so the rules are about behaviour, not the simulation.

### A. Layers, Esc and focus (shared by every surface below)

- **There are three kinds of layer:** the **item pop-up**, the **drawer**, and a
  **full-screen panel** (Crafting or Options) stacked over the drawer.
  #161 will add one more full-screen panel, the device panel, using the same machinery, so
  build it generically: an ordered stack of open layers.
- **Esc closes the topmost open layer only.**
  - Pop-up open → the pop-up closes.
  - Crafting over the drawer → Crafting closes and the drawer stays.
  - Drawer alone → the drawer closes.
- **Focus moves in on open and back on close.**
  - When a layer opens, keyboard focus moves to its first focusable control.
  - When it closes, focus returns to the element that was focused when it opened.
  - If that element no longer exists because a render rebuilt it (item rows are
    rebuilt on every `render()`), focus the equivalent control if there is one:
    the `.itemname` button for the same `_uid`. Otherwise drop focus without
    error.
- **A re-render must not drop focus out of an open layer.** If focus was inside a
  layer that `render()` rebuilds, it lands back inside that layer.
- Show the focus outline for keyboard use only (`:focus-visible`), so tapping and
  clicking look as they do today.
- **Game over closes every layer** (Tom). When `render()` takes its game-over
  branch, the pop-up, any full-screen panel and the drawer all close, so "You did
  not survive." is what the player sees. The drawer and Options can still be
  opened afterwards.
- Full ARIA (roles, labels, inert backgrounds) stays parked in #78. This pass
  adds Esc and focus only.

### B. The item pop-up (#157)

- **Opening.** Tapping an item's `.itemname` sets `detailItem = { uid, side }`
  exactly as today, and opens the pop-up for that item.
- **Content.** Exactly what the detail view shows today, unchanged in wording and
  order:
  - the name line, the category/weight line and the durability line;
  - the Sealed/Opened line;
  - then `getItemActions(found.list, found.index, detailItem.side)` rendered as
    `button.action`s, **one per line**, stacked in a column (not with `<br>`).
  - Disabled entries render disabled with `.blocked`, as today. The Take family
    stays disabled rather than hidden while the keychain tab is open, per the
    comment in `getItemActions()`.
  - The pop-up adds no action of its own. `getItemActions()` stays the single
    source.
- **Position** (Tom). Anchored to the tapped item's row:
  - it opens directly **below** the row;
  - it flips **above** the row when opening below would run off the bottom of the
    viewport;
  - it stays fully on-screen horizontally in both layouts.
- **The anchor row is found by uid, never by index.** Rows are rebuilt on every
  `render()`, so the pop-up re-finds its row by the item's `_uid` after each
  render and re-anchors to it. Never keep the row index or the DOM node the
  pop-up was opened from.
- **It stays open after an action** (Tom) and updates in place: Turn on becomes
  Turn off, quantities drop. This works as it does today because every action
  already ends in `render()`.
- **It closes on:**
  - a tap or click **outside** it. This works the same way the drawer's
    `#menuBackdrop` works: a transparent layer behind the pop-up takes the tap,
    closes the pop-up, and does nothing else. A tap on another item's name
    therefore closes this pop-up; a second tap opens that item's;
  - **Esc**;
  - **`detailItem` clearing for any reason**: movement, load, restart, or
    `findItemByUid()` missing because the item left every list (for example, Take
    All). The pop-up's visibility follows `detailItem`, and nothing else
    decides it.
  - Closing it sets `detailItem = null`.
- **What survives.** `doOpen()`'s re-pointing of `detailItem` keeps working, so
  opening the last sealed unit keeps the pop-up open on the opened one.
- **Relationship to the drawer.** The pop-up belongs to the play area and sits
  **below** the drawer's backdrop. Opening the drawer does not close it; it is
  simply covered. (#161 relies on this: Device Options opens the drawer from the
  pop-up and returns to it.)

### C. The drawer hub (#158)

- **A button row at the top of the drawer** (Tom), directly under the `Menu ✕`
  heading and above Save / Load. In order:
  1. **Crafting** (enabled);
  2. **Health** (disabled placeholder);
  3. **Clothing** (disabled placeholder);
  4. **Options** (enabled).

  The order is a layout call and retunable. Define the row as data, one entry per
  button giving its label, whether it is enabled, and what it opens, so adding
  one later is a one-line change.
- **Placeholders** (Tom) are greyed and disabled, and carry the hint **"Not
  yet"**. That follows the rule that a disabled control says why, as the recipe
  list's `(needs …)` does. The hint is functional UI text and retunable. #163 and
  #164 enable the two buttons later.
- **Crafting and Options open full-screen, stacked over the drawer** (Tom).
  - Each covers the whole viewport, above the drawer, with its own heading and a
    close control.
  - Closing one returns to the **drawer**, not to play.
  - Esc behaves the same way (A).
- **The Craft panel leaves the page in both layouts.** Its `.panel` markup,
  `#craftBody`, `#craftBackBtn` and their game-over-branch lines are removed. The
  sidebar holds Inventory and Here only.
- **Save / Load, Stats and Map** are otherwise unchanged. The Run section goes
  (D).

### D. The Crafting panel

- **Content:** today's recipe catalogue, moved as-is:
  - every recipe in `RECIPES` order;
  - unavailable ones disabled with `(needs …)`;
  - the catalogue comment moves with it and stays true.
- **Rendering.** While the panel is open, `render()` re-renders it like any other
  panel, so availability updates after every action.
- **After a craft the panel stays open** (Tom), with a **result area** that shows
  **every log entry that craft wrote** (Tom):
  - the craft line;
  - any `giveItem()` "drops to the floor" warning;
  - anything the craft's `advanceTime()` logged.

  It shows those entries and nothing older, in the order and wording `#log` shows
  them.
  - **Entries that updated in place count.** `log()` can update the last entry
    instead of appending (a second identical craft adds `×2`). An entry updated
    in place counts as written by this craft and is shown in its updated form.
  - The result area is **replaced** on the next craft, and **cleared** when the
    panel closes.
  - It is a view of `#log`. It must not keep a second copy of log history, and
    must not add a line to `#log`.
  - `doCraft()` is not changed; capture what it wrote from the panel's click
    handler.
- **If the craft ends the run,** A's game-over rule closes everything.

### E. The Options panel (#160)

- **Opened** from the hub's Options button, full-screen over the drawer (C).
- **Content, in order:**
  1. **The seed**, as its canonical number (the same value `renderRunPanel()`
     prints today). It is **selectable text**, with a **Copy** button beside it
     that puts the number on the clipboard (Tom).
  2. **Restart game**, next to the seed it would replay.
- **The seed must be correct after game over.** Whatever writes it runs whether
  or not `gameOver` is set, the guarantee `renderRunPanel()` gives today. Keep
  its comment's reasoning with the new code.
- **Restart keeps today's `prompt()`** (Tom). The wording is unchanged, Cancel
  aborts, and blank and typed input go to `doRestart()` / `seedFromInput()` as
  now. The handler moves; its logic does not.
- **After a confirmed Restart, every layer closes** (Tom), so the player sees
  "You wake up in your apartment…" in the new run. Cancel closes nothing.
- **The drawer's Run section is removed:** its markup, `#runBox`, and
  `#runBox`'s share of the `#statsBox, #runBox` CSS rule. `renderRunPanel()` is
  retargeted or folded into the Options renderer.
- `#restartMenuBtn` leaves the Save / Load section.
- **The game-over screen's own Restart button** (`:6671`) is unchanged. A "Replay
  this seed" button there is #176, not this pass.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

- **Markup for the full-screen panels.** One shared panel element that Crafting
  and Options render into, or one element each. Either is fine. #161 adds a
  third occupant, so shared is slightly ahead.
- **The layer stack's shape.** An array of open layers, per-layer flags, or
  something else, as long as Esc and focus behave as in A and #161 can push one
  more layer.
- **How the result area finds what a craft wrote.** For example, snapshot
  `#log`'s children and the last entry's text before `doCraft()`, then diff after.
  Any method that meets D's rule without changing `doCraft()` or `log()`.
- **Copy's mechanism and feedback.**
  - Mechanism: `navigator.clipboard.writeText()` with a fallback (select the
    text, then `document.execCommand("copy")`), for pages opened from `file://`
    where the async clipboard may be unavailable.
  - Feedback: for example, the button reading "Copied" briefly. It must not go to
    `#log`, which the panel covers. Functional text, retunable.
- **The pop-up's width, and what happens on scroll.** Recommended: no wider than
  the row, clamped to the viewport minus a small margin, and re-anchored on
  scroll and resize so it stays attached to its row.
- **Z-order.** Suggested: pop-up and its transparent backdrop below
  `#menuBackdrop`'s 15; full-screen panel above `#sideMenu`'s 20.

## Data / schema changes

None. No state field, no item or world schema change, no registry change. New
UI-only variables, if any (the layer stack, the result-area contents), live
beside `detailItem` and stay out of `state`. `SAVE_KEY` does not rotate.

## In scope

- [ ] Item pop-up per B, replacing the detail view; `detailItem` semantics unchanged.
- [ ] Drawer button row per C, with the Health and Clothing placeholders.
- [ ] Full-screen Crafting panel per D, with the result area.
- [ ] Full-screen Options panel per E: copyable seed, Restart with its prompt.
- [ ] The Craft panel removed from the sidebar, in markup, CSS and the render
      paths including the game-over branch.
- [ ] Run section and `#restartMenuBtn` removed from the drawer.
- [ ] Esc and focus per A, for every layer.
- [ ] Game over and confirmed Restart close every layer.
- [ ] Stale comments rewritten wherever they describe the detail view living in
      the Craft panel. Grep `detail view`, `Craft panel`, `craftBody`, `runBox`
      and `renderCraftPanel`.

## Explicitly out of scope

- **#159**: layout, orientation and compact button sizes. Its own handoff.
  Button sizes in the pop-up and the panels use whatever `button.action` is when
  this ships.
- **#161**: Device Options. Build the layer stack so it can take one more layer,
  and nothing more.
- **#162**: search and filters in Crafting.
- **#163 / #164**: enabling Health and Clothing.
- **#165**: adjustable panel sizes.
- **#166**: title screen.
- **#176**: Replay this seed on the game-over screen.
- **#78**: ARIA roles and labels, and the closed drawer's tab order.
- Heat recipes joining the Crafting panel (#119, #120).
- Any change to `getItemActions()`, `doCraft()`, `doRestart()` or `log()`.

## Sections touched

- `<style>`: pop-up, full-screen panel, hub row, placeholder style, focus-visible
  outline; the Craft panel's rules go.
- Markup: `#sideMenu` (hub row added; Run and `#restartMenuBtn` removed),
  `#sidebar` (Craft panel removed), plus new elements for the pop-up and the
  full-screen panel(s).
- **EVENTS / UI HELPERS**: `openMenu()` / `closeMenu()` joined by the layer
  stack, Esc handling, focus handling, and the Restart handler's new home.
- **RENDERING**: `renderItemList()` (open the pop-up), `renderCraftPanel()` split
  into the pop-up renderer and the Crafting panel renderer, `renderRunPanel()`
  retargeted, and `render()`'s game-over branch.
- No WORLD DATA, no ACTIONS, no SIMULATION, no PERSISTENCE logic. The Restart
  handler is event wiring that calls PERSISTENCE's `doRestart()` unchanged.

## UI changes

- Tapping an item's name opens a pop-up at the item instead of changing the
  Craft panel.
- The Craft panel is gone from the page.
- The ☰ drawer opens onto a row of four buttons: Crafting, Health (Not yet),
  Clothing (Not yet), Options.
- Crafting and Options each open full-screen over the drawer.
- The seed is no longer shown every time the drawer opens. It's in Options,
  selectable, with Copy.
- Esc closes the topmost menu layer, and keyboard focus follows the layers.
- Functional text introduced: **"Crafting"**, **"Health"**, **"Clothing"**,
  **"Options"**, **"Not yet"**, **"Copy"** and any copy feedback. It's held to
  clarity, not to the game's descriptive tone, and all of it is retunable.

## Dependencies / issue linkage

- Fulfils **#157**, **#158** and **#160**. The pull request carries
  `Closes #157`, `Closes #158` and `Closes #160`.
- Unblocks **#161** (`handoffs/device-options.md`), **#162**, **#163** and
  **#164**.
- The v0.6.0 line numbers in those issues are stale. Use this handoff's.
- Anything cut or deferred during implementation is filed as a new issue at the
  wrap.

## Open questions for Tom

None. All were answered in the planning session at v0.6.3, and the answers are
recorded on #157, #158 and #160.

## After implementation

Open a pull request with:
- `GAME_CONFIG.VERSION` bumped (PATCH);
- a new `CHANGELOG.md` entry naming this handoff by path and recording the
  implementation decisions above;
- this handoff moved to `handoffs/archive/` with `git mv`;
- `Closes #157`, `Closes #158` and `Closes #160`.
