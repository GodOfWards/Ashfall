# Ashfall Handoff — Compact Sizes and Side-by-Side Panels

Current shipped version: v0.7.0
Implied version-change type: PATCH
Issues: #190 — Buttons about 10% smaller than v0.7.0, and text evened out to one size across the play screen
        #191 — Here and Inventory as side-by-side columns — under the actions in portrait, right of a narrower text column in landscape
        #186 — One-column layout: a short room leaves a gap between the Here actions and the panels

## What this is

Three changes to the play screen, made together because they were designed and
approved together:

- **Controls about 10% smaller than v0.7.0**, never below 24px.
- **Text at 12px across the play screen.**
- **The Here and Inventory panels as two side-by-side columns** in both
  orientations.

The layout part answers #186's open question: in portrait, the panels move up
to sit directly under the actions.

Tom approved every value below after trying them at real size on his phone:
412×800 portrait and 860×320 landscape, at 100% zoom, with Android's Roboto and
Noto Serif. He used a private mock-up artifact, the "layout lab"
(https://claude.ai/artifact/3n7wihZzUvLZZSBAU5CdYd). You don't need it to
implement this handoff: every value it used is stated here.

## Relevant existing state

Verified against `ashfall.html` at v0.7.0. Line numbers are v0.7.0's.

- **Layout.**
  - `main` is `display:grid; grid-template-columns:1fr 320px` (`:111`).
  - `#left` holds the room description, log and action groups (`:112`, `:259`–`:264`).
  - `#sidebar` is `display:flex; flex-direction:column; gap:16px; padding:16px 18px; overflow-y:auto` (`:145`). It holds `#invPanel`, then `#worldPanel`, in DOM order (`:266`–`:275`).
  - `.panel` is `padding:11px 13px` (`:146`). Only those two panels use the class.
- **Portrait query** `@media (orientation: portrait), (max-width: 480px)` (`:181`–`:186`):
  - `main` becomes one column.
  - `#left` gets `padding:14px 16px`, no right border, and a bottom border.
  - `#worldPanel{order:-2}` and `#invPanel{order:-1}` put Here first.
  - Its comment (`:168`–`:180`) explains the 480px clause as a floor for the 320px sidebar grid.
- **#186.** In one column the grid's rows stretch by default, so `#left` absorbs the spare height. A gap then opens between the last action and the panels.
- **Tabs.**
  - `.tabs` is `display:flex; gap:5px; margin-bottom:9px; flex-wrap:wrap` (`:147`).
  - `renderInventoryPanel()` (`:7123`) and `renderWorldItemsPanel()` (`:7153`) rebuild `#invTabs` and `#worldTabs` from scratch on every render (`innerHTML = ""`, `:7125`, `:7156`).
- **Item rows.**
  - `ul.itemlist li` is a flex row (`:155`–`:156`): `.meta` (`flex:1`) with the name, quantity, weight and category, then `.btnrow` with Take, Store or Place.
  - `.itemname` (`:139`–`:141`) is bold, with `text-decoration:underline dotted; text-underline-offset:2px`.
- **The item pop-up.** `positionItemPop()` makes it exactly as wide as its row. In a half-width column that's about 175px in portrait and about 185px in landscape. That was checked in the mock-up, it reads fine, and it doesn't change.

## Rules / mechanics

No game rules change. This is presentation only.

### 1. Sizes (`<style>` block)

| selector (v0.7.0 line) | property | v0.7.0 | new |
|---|---|---|---|
| `header h1` (`:17`) | font-size | 15px | **13px** |
| `#menuToggle` (`:18`) | font-size; padding | 13px; 7px 11px | **12px; 6px 10px** |
| `#hubRow button` (`:32`–`:33`) | font-size; padding | 13px; 8px 6px | **12px; 7px 6px** |
| `.menu-actions button` (`:75`–`:76`) | font-size; padding | 13px; 8px 10px | **12px; 7px 9px** |
| `#locLabel` (`:102`) | font-size | 14px | **12px** |
| `#gaitBar span` (`:106`) | font-size | 12px | **11px** |
| `#gaitBar button` (`:107`–`:108`) | padding; min-height | 5px 9px; — | **4px 8px; 24px** |
| `#roomDesc` (`:113`) | font-size | 15px | **12px** |
| `#log p, .log-result p` (`:117`) | font-size | 13.5px | **12px** |
| `.actions-group h2` (`:123`–`:124`) | font-size | 12px | **11px** |
| `button.action` (`:126`–`:127`) | font-size; padding; min-height | 12.5px; 6px 10px; — | **12px; 5px 9px; 24px** |
| `.detailBox` (`:143`) | font-size | 12.5px | **12px** |
| `.tabs button` (`:148`–`:149`) | padding; min-height | 5px 9px; — | **4px 8px; 24px** |
| `.panel h2` (`:151`–`:152`) | font-size | 12px | **11px** |
| `ul.itemlist li` (`:155`–`:156`) | font-size | 12.5px | **12px** |
| `button.mini` (`:163`–`:164`) | min-height | — | **24px** |
| `.itemname` (`:139`–`:141`) | text-decoration | underline dotted, offset 2px | **none** (it stays bold) |

These are already at the target, so leave them as they are: `#clockLabel`, `.panel h2 .sub`, `ul.itemlist .cat`, the `.sys` / `.warn` / `.good` log lines (all 12px), `.cost` (11px), and the font sizes of `button.mini`, `.tabs button` and `#gaitBar button` (12px).

Line-heights don't change. Neither do the room description's and log's serif face.

**What this produces.** Measured at 412px with Roboto:

| control | v0.7.0 | new |
|---|---|---|
| menu | 31 | 28 |
| actions | 29 | 26 |
| pace buttons | 26 | 24 |
| tabs | 26 | 24 |
| item buttons | 24 | 24 |

The 24px `min-height` is the floor: WCAG 2.2's AA minimum target size. A straight 10% cut would have put three controls at 22–23px.

### 2. Two panel columns, in both orientations

- **`#sidebar`** becomes `display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:8px; padding:10px 8px`. Keep its `font-family` and `overflow-y`.
- **`.panel`** becomes `display:flex; flex-direction:column; padding:10px 9px; min-width:0`. The `min-width:0` is load-bearing. Without it, a grid item's automatic minimum width is its content's min-content width, and a tab row that doesn't wrap (§3) would widen its panel past its column.
- **`.panel h2`** adds `flex-wrap:wrap; gap:2px 6px`, so the weight readout and the Unequip or Device Options button can drop under the heading when a column is too narrow.
- **Item rows are unchanged.** The button stays beside the text, and the name, quantity, weight and category wrap inside `.meta`. Tom approved this in the mock-up.

### 3. Tabs: one row that scrolls sideways (both orientations)

- **`.tabs`**: `flex-wrap:nowrap; overflow-x:auto; scrollbar-width:none;` plus `mask-image` and `-webkit-mask-image`, both set to `linear-gradient(to right, #000 80%, transparent)`.
- **`.tabs::-webkit-scrollbar`**: `display:none`.
- **`.tabs button`**: `flex:none; white-space:nowrap`.

The fade is always on, as approved. It is the only sign that more tabs are off to the right.

**The selected tab is always fully visible.** After every render, each strip's selected tab (`#invTabs`, `#worldTabs`) must sit entirely inside the strip's visible area.
- Tapping a tab that's already visible must not move the strip.
- The adjustment scrolls the strip only, never the page.
- **This fails today in the mock-up:**
  1. Go to 2A's kitchen and scroll the Here strip to Pantry.
  2. Tap Pantry.
  3. Go to the living room.
  4. Floor is selected, but it starts 20px off the strip's left edge.

  The strip keeps its old scroll offset across the rebuild, clamped to the new, shorter row.

### 4. Portrait: Fill

Inside the existing portrait query, `main` gets `grid-template-rows:auto 1fr` alongside its one column.
- `#left` takes only the height it needs.
- The panel row takes the rest: the panels start directly under the actions and stretch to the bottom of the screen.
- A long list grows the page, and the page scrolls. This closes #186.
- The existing `order` rules stay, so portrait reads Here | Inventory, left to right.

### 5. Landscape: 50 / 25 / 25

`main`'s base rule becomes `grid-template-columns:minmax(0,1fr) minmax(0,1fr)`, replacing `1fr 320px`.
- The text column ends at the middle of the screen. The two panels share the right half.
- DOM order already puts Inventory first, so landscape reads text | Inventory | Here.
- `#left` keeps its v0.7.0 padding and right border.

### 6. The portrait query's comment

The comment at `:168`–`:180` stops being true once the 320px sidebar is gone. Rewrite it to describe what now holds:
- **The `max-width:480px` clause stays unchanged.** Its reason is now that three columns get too narrow below it, not a 476px floor.
- **Here now sits beside Inventory, not above it.**
- **The rows are `auto 1fr`,** and that is what keeps the panels directly under the actions (#186).

## Design decisions to make during implementation

- **How to keep the selected tab visible (§3).** One option is to set the strip's `scrollLeft` after each rebuild, using the selected button's offset. Another is a shared helper, called by both panel renderers, placed in EVENTS / UI HELPERS or RENDERING.
  - Don't use a plain `scrollIntoView()`. It can scroll the page vertically.
  - Record the choice in the changelog's Notes/assumptions.
- **Where the grid rules live.** The sidebar grid and the tab strip apply in both orientations, so the natural place is the base rules, with the portrait query overriding only `main`. Duplicating them in orientation queries is equivalent. Pick one and say which.

Neither choice changes the version tier.

## Data / schema changes

None. Nothing is added to `state`, and `SAVE_KEY` does not rotate.

## In scope

- Every value in §1's table, including removing the item-name underline.
- The two-column sidebar in both orientations (§2).
- The one-row, sideways-scrolling tab strips (§3), with the selected tab always visible.
- Portrait Fill (§4). This closes #186.
- Landscape 50 / 25 / 25 (§5).
- Rewriting the portrait query's comment (§6).

## Explicitly out of scope

- **Other text in the drawer and full-screen panels.** It was not mocked or approved, so it keeps its v0.7.0 size:
  - `#statsBox`, `#seedRow` and `#deviceStatus` (13px)
  - `.menu-section h3` and `.menu-placeholder` (12px)
  - the `#sideMenu` and `.full-panel` headings (14px)
  - `#hubRow .hint` (11px)
  - the map's text and `#mapZoomToggle` buttons
  - `#closeMenu` and `.panel-close`
- **Rejected in planning. Don't build these:**
  - a half-screen "dock" with independently scrolling halves
  - a 40 / 30 / 30 landscape split
  - a 1280px cap
  - wrapping tabs
  - a dropdown in place of tabs
- **#165:** adjustable layout in Options. This handoff's values become its defaults, but no preference UI or storage is built here.
- **#29:** the log's `max-height:110px` and 50-entry cap are unchanged.
- **#169:** a bag on the floor as a tab in Here. The scrolling strip will take it when it lands.
- **Item pop-up width and position.** `positionItemPop()` is unchanged.
- **#78:** the parked accessibility pass.

## Sections touched

- The `<style>` block, for §1–§6.
- RENDERING, `renderInventoryPanel()` and `renderWorldItemsPanel()`, for keeping the selected tab visible (§3). EVENTS / UI HELPERS too, if a shared helper is used.
- No WORLD DATA, PLAYER STATE, ACTIONS, SIMULATION or PERSISTENCE change.

## UI changes

- **Everything on the play screen is smaller and reads as one size.**
  - Room text, log and location drop from 13.5–15px to 12px, matching the controls.
  - Buttons are about 10% shorter.
  - Item names are bold without the dotted underline.
- **Portrait:** Here and Inventory sit side by side directly under the actions and fill the rest of the screen.
- **Landscape:** three columns, text | Inventory | Here, with the text column half the width.
- **Tabs:** each panel's tabs are a single row that scrolls sideways, fading at the right edge.

## Dependencies / issue linkage

- **Fulfils #190, #191 and #186.** The pull request should carry `Closes #190`, `Closes #191` and `Closes #186`.
- **#108** added the dotted underline as the touch hint that a name is tappable. Removing it is Tom's decision, made here. The changelog should say so, and note that the bold weight is now the only hint.
- **#159** set the sizes this retunes. Its values are superseded, not reverted.
- **Nothing is expected to be deferred.** If implementation surfaces something, file it at the wrap.

## Open questions for Tom

None.

## After implementation

Open a pull request with:
- `GAME_CONFIG.VERSION` bumped as a PATCH;
- a new `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, naming this handoff by the path it was read at;
- this file moved to `handoffs/archive/` with `git mv`;
- `Closes #190`, `Closes #191` and `Closes #186`.

The changelog's Notes/assumptions should flag these as judgment calls, and retunable:
- every size in §1
- the 24px floor
- the 80% fade stop
- the 8px gaps and the 10px/9px paddings
- the 50 / 50 landscape split of `main`

It should also record the two implementation choices above.

Before opening the pull request, check at 412×800 portrait and 860×320 landscape:
- the heights in §1's second table;
- the Kitchen → living-room tab case in §3.
