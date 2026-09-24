# Ashfall Handoff — Device pop-up and panel polish

Current shipped version: v0.8.1
Implied version-change type: PATCH
Issue: #228 — Device Options as a pop-up menu
Issue: #229 — The Here panel's tabs jump down when a device tab is selected
Issue: #230 — A dish lists under its own name, not its vessel's
Issue: #231 — Saving twice writes "Progress saved to this browser." twice
Issue: #37 — Wide map: a street on the viewBox edge is given names that render outside the box

## What this is

A polish pass from the v0.8.1 playtest, plus two small fixes from the
backlog. Five changes, all rendering, none adding state:

1. **#228.** Device controls move out of the full-screen Device Options
   panel. The radio's controls go straight into its item pop-up. The
   stove's go into a pop-up styled like the item pop-up. The full-screen
   panel is retired.
2. **#229.** Neither item panel's tab strip moves when its tab changes.
   Everything that comes and goes with a tab moves to a strip below the
   tabs.
3. **#230.** A vessel holding a dish lists as the dish. The vessel is
   named only in the pop-up.
4. **#231.** Repeated save/load/export/import lines collapse into one
   line with a `×N` count, as other repeated lines do.
5. **#37.** Wide-map street names are placed only where they land inside
   the view.

## Relevant existing state

Verified against `ashfall.html` at v0.8.1. Find each piece by its
identifier. Line numbers are left out on purpose.

**Devices today.** Two things carry `device`. The **portable radio** is an
item: `tags:["device"]` in `ITEM_REGISTRY`. The **stove** is a room fixture:
the `stove` / `stove1a` containers, `tags:["device","heat"]`, found by
`roomStove()`. The flashlight runs on batteries but is not a device, so its
controls already sit in its item pop-up.

**The full-screen panel.** The markup is `<section id="devicePanel"
class="full-panel">`: `#deviceTitle`, `#deviceStatus`, `#deviceControls`
and `#deviceResult`. The code:
- `openDevicePanel(target)` opens the drawer first, then stacks the panel
  over it with `openLayer()`.
- `renderDevicePanel()` is called from every `render()`.
- `resolveDeviceTarget()` looks the target up again on each render.
- `runDeviceControl()` feeds the result area through `logWrittenBy()`.
- `renderDeviceResult()` draws that area.

The UI-only state is `deviceTarget` (`{ kind:"item", uid }` or
`{ kind:"container", id }`) and `deviceResult`. Load and restart both
clear `deviceTarget`. `DEVICE_OPTIONS_LABEL = "Device Options"`.

For an item, the panel shows `durabilityText(it)` and `batteryActions(it)`.
For the stove, the panel shows, in order:
- the status lines `stoveOnText(room)` and `stoveTimerText(stove)`;
- "Turn off the stove" (`doExtinguish`) when `room.heatActive`, or
  "Light the stove " + `fmtDuration(LIGHT_STOVE_MIN)` (`doLightStove`) when
  `hasMatchUses()`, or otherwise `hereNote("Nothing you're carrying will
  light it.")`;
- a `.timer-steps` row, one `"+" + m` button per `STOVE_TIMER_STEPS` entry
  (`doAddStoveTimer(m)`).

A fixture carrying `device` without `heat` draws only its title.

**The item pop-up.** `#itemPop` and `#itemPopBackdrop` are drawn by
`renderItemPop()` and placed by `positionItemPop()`:
- It hangs from its row, found by uid, at the row's width.
- It sits below the row and flips above when it doesn't fit. Otherwise it
  takes the roomier side and scrolls.
- It re-runs on every render, scroll and resize.
- It stays open after an action and updates in place. An outside tap
  (the backdrop) or Esc closes it.

`getItemActions()` builds its buttons. For an item with `device`, it pushes
a `DEVICE_OPTIONS_LABEL` action that opens the panel. For any other item
it pushes `batteryActions(it)`. The layer system is `openLayer()`,
`closeLayer()`, `layerStack`, `restoreFocus()` and
`rebuildKeepingFocus()`.

**The headers.** Here's header is `<h2>Here <span class="sub">`, holding
`#worldWeight`, then `#worldDeviceState` ("Off · Timer: 10", shown only on
the stove's tab), then `#deviceOptionsBtn` (shown on any `device` tab). All
three are set in `renderWorldItemsPanel()`. Inventory's header is
`<h2>Inventory <span class="sub">`, holding `#invWeight` and `#unequipBtn`
(shown on an equipped bag slot's tab). `#worldPanel h2 .sub` has
`flex-wrap:wrap`.

Measured in headless Chromium at a 355×770 viewport (each item panel
166px wide), from the top of the panel to the top of its tab strip:

| Panel | Tab | Tabs start at |
|---|---|---|
| Here | Floor | 33px |
| Here | Stove | 92px |
| Inventory | Inventory | 48px |
| Inventory | a tab showing Unequip | 62px |

Inventory's header already wraps at that width without Unequip. So its
height can also change with the weight's text.

**Dish display.** `itemStateText(it, ctx)` returns the text after an item's
name. For a vessel holding a dish (`vesselDefOf(it) && dishIn(it)`), that is
`: <dish name><dish's labels>`. Both callers use it:
- **The list row** (`renderItemList()`): the name button (`.itemname`,
  `data-uid`) holds `it.name`, then the state text, then
  `×qty — kg (category)`.
- **The pop-up**: the name line is `it.name` plus the state text. The
  stats line is `it.category · weight (each)`. For a vessel *without* a
  dish, it also draws a "Holds: …" line.

Dish entries (`dish_*`) have `category:"Food"`. The vessel names are
Frying pan, Burnt saucepan, Dented saucepan, Cooking pot and Roasting pan.

**The log.** `log(text, cls, key, outcome)` collapses a line into the one
before it only when both carry the same `key` (`dataset.logKey`). The four
save-system lines pass no key:
- "Progress saved to this browser."
- "Progress loaded from this browser."
- "Save file exported."
- "Save file imported."

All four are `"sys"`, in the Save / Load / Export / Import handlers.

**Wide map labels.** `mapPositionStreetLabels(box, node)` counts a street as
on screen with an inclusive bounds test on its line:
- horizontal: `street.a.y >= box.y && street.a.y <= box.y + box.h`;
- vertical: `street.a.x >= box.x && street.a.x <= box.x + box.w`.

`mapLabelBox()` puts the name on one side of the line: above a horizontal
street, right of a vertical one. Its ink runs from `MAP_LABEL_OFFSET` (5) to
`MAP_LABEL_OFFSET + MAP_LABEL_CAP` (17) off the line. So a street within 17
units of the top edge (horizontal) or of the right edge (vertical) gets
names drawn entirely outside the box. #37's counts date from v0.5.2 and
predate v0.5.3's per-street widths, so they need re-taking.

## Rules / mechanics

### 1. Device controls (#228)

**Item devices.** The radio loses its `device` tag. `getItemActions()` drops
its `device` branch and pushes `batteryActions(it)` for every item, as it
already does for the flashlight. The radio's pop-up then shows its status
line (`durabilityText()`, already drawn) and Turn on/off, Remove batteries
and Replace batteries inline. `device` becomes a container-only tag. Update
the ITEM DATA SCHEMA tag list to drop it, and the CONTAINER schema's
`device` line to name the pop-up instead of the panel.

**Fixture devices: the device pop-up.**
- **Opening.** The Device Options button, now in the Here panel's strip
  (below, in 2), opens a pop-up.
- **Look.** Visually the same as the item pop-up: same panel, border,
  shadow, padding and font. A bold title line with the fixture's name, the
  status lines, then the controls in `.pop-actions`.
- **Stove contents, in order:**
  - `stoveOnText(room)` and `stoveTimerText(stove)`, as two lines, as the
    panel has them;
  - Light the stove / Turn off the stove, or the "Nothing you're carrying
    will light it." note, exactly as `renderDevicePanel()` chooses today,
    labels unchanged;
  - the `+5 / +10 / +30` timer buttons in one row (`.timer-steps`), as
    today.
- **Other fixtures.** One with `device` but not `heat` draws only its
  title, as today.
- **Placement.** It hangs from the strip the button sits in, at that
  strip's width, with `positionItemPop()`'s placement rule: below, flip
  above, else the roomier side and scroll. `POP_MARGIN` applies. It re-runs
  on render, scroll and resize.
- **Behaviour.** It stays open after a control runs and redraws in place
  on every `render()`. It closes on an outside tap, on Esc, or when its
  target no longer resolves: `deviceTarget` is `{ kind:"container", id }`,
  looked up again on every render as now, and the pop-up also closes when
  the Here tab is no longer that container's. Focus returns to the Device
  Options button.
- **Results.** A control's result is the main log's line and nothing else.
  There is no result area.

**Retired.** Remove all of the following:
- the `#devicePanel` section;
- the `#deviceStatus` / `#deviceControls` CSS rules;
- `openDevicePanel()`'s drawer-opening path;
- `deviceResult`, `runDeviceControl()` and `renderDeviceResult()`;
- the `{ kind:"item" }` target shape.

`.log-result` and `renderLogResult()` stay, because Crafting still uses
them. Update every comment that names the Device Options panel: the CSS
comments on `.full-panel` and `.log-result`, the MENU LAYERS comment, the
Here actions comment on the stove, and the two schema lines above.

### 2. Tab strips that don't move (#229)

**The rule:** in both item panels, at every viewport width, the top of the
tab strip is the same distance from the top of its panel on every tab.

- **Headers.** They carry only the panel title and the weight. The weight
  (`#worldWeight`, `#invWeight`) must never push the tabs: either the
  header is a fixed height that fits its widest weight at the narrowest
  layout, or the weight fits on the title's line. That choice is left to
  the coding session (see "Design decisions" below).
- **The Here strip.** It sits directly below `#worldTabs`, above
  `#worldList`, and is shown only while the selected tab is a `device`
  container. It holds `#worldDeviceState` ("Off · Timer: 10", unchanged
  text, still shown only for the stove) and the Device Options button.
- **The Inventory strip.** It sits directly below `#invTabs`, above
  `#invList`, and is shown only while `#unequipBtn` would be. It holds
  Unequip, whose behaviour is unchanged.
- **Hidden strips.** A hidden strip takes no space, so a tab without one
  looks as it does today below the tabs.
- **Game over** hides both strips, as it hides their contents today.

The list moving down by one strip's height on a device or bag tab is
accepted. What must not move is the tab strip.

### 3. A dish shows as the dish (#230)

This applies when `vesselDefOf(it) && dishIn(it)`. The item is the vessel,
the dish is the one it holds, and every action is unchanged.

- **List row.** The name button's text is the **dish's** name, then the
  dish's state labels, then `×qty — <weight> kg (<dish's category>)`. For
  example, `Meat and vegetable stew (Cooked) (Stale) ×1 — 4.20 kg (Food)`.
  The weight stays `itemWeight(it)`, the vessel and dish together. The
  vessel's name does not appear.
- **Pop-up.**
  - The name line is the dish's name in bold, then its labels.
  - The stats line is the dish's category, then the same weights as now,
    with and without the pot: `Food · 4.20 kg (4.20 kg each)`.
  - A new line directly under the stats line reads
    `In a <vessel name, lowercased>`, e.g. "In a cooking pot" or "In a
    dented saucepan". Functional UI text, retunable.
  - The actions are unchanged: Take All, Eat, Eat 1/2, Eat 1/4, Pour it
    out.
- **Everything else is unchanged:**
  - a vessel that is empty, or holds water or ingredients, still lists as
    the vessel, with its "Holds: …" line;
  - log lines;
  - `vesselButtonNames()` labels;
  - the Crafting panel.

When the dish is poured out or eaten up, the row goes back to the vessel's
name on the next render. Rows resolve by `data-uid`, so focus follows.

### 4. Save-system lines collapse (#231)

Give each of the four save-system `log()` calls its own key: `"save"`,
`"load"`, `"export"` and `"import"`. Class and text stay unchanged, with no
`LOG_SUMMARIES` entry, so a repeat reads e.g.
`Progress saved to this browser. ×2`. Distinct keys mean a save followed by
an export stays two lines. `applyLoadedData()` leaves `#log` alone (only
`doRestart()` clears it), so repeated loads and imports collapse the same
way.

### 5. Wide-map street names land inside the view (#37)

In `mapPositionStreetLabels()`, the on-screen test asks for room for the
label on its own side only:

- horizontal: `street.a.y >= box.y + MAP_LABEL_OFFSET + MAP_LABEL_CAP && street.a.y <= box.y + box.h`
- vertical: `street.a.x >= box.x && street.a.x <= box.x + box.w - (MAP_LABEL_OFFSET + MAP_LABEL_CAP)`

The side away from the label keeps today's bound: the line itself must be
inside the box. That keeps every label drawn correctly today, including
those of streets near the bottom or left edge, whose bands run into the
view. It doesn't add names for streets whose line is off screen. Write the
depth once, as a named derivation or a shared constant beside
`MAP_LABEL_CAP`, not as `17`. Close view is untouched.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

1. **Header stability (2).** Either a fixed header height that fits the
   widest weight at the narrowest layout, or a layout that keeps the weight
   on the title's line (e.g. no-wrap with the title shortened by CSS
   ellipsis before the weight is). Recommended: whichever passes the
   measurement in Validation with less CSS. Neither may crop the weight.
2. **The device pop-up's element.** Either a second element (e.g.
   `#devicePop` plus its own transparent backdrop) sharing the item
   pop-up's styles through a common class, or `#itemPop` reused with a
   mode. Recommended: a second element with a shared class. Its open state
   then follows `deviceTarget`, as the item pop-up's follows `detailItem`,
   and the two never fight over one element. Generalise
   `positionItemPop()`'s rule to take an anchor rect, rather than copying
   it.
3. **Where the "dish or vessel" display decision lives (3).** One helper
   answering "what name, labels and category does this item show?", read
   by both the row and the pop-up. `itemStateText()` can be folded into it
   or kept beside it. Either way it is one statement, not two.

## Data / schema changes

- **ITEM_REGISTRY:** `portable_radio` drops `"device"` from `tags`. This is
  definition data for the pop-up rule in 1, since the tag's only reader on
  items goes away in this pass.
- **Schema comments:** the item tag list drops `device`, and the container
  `device` line names the pop-up.
- **No new state fields.** `deviceTarget` stays UI-only and never saved.
  `deviceResult` is removed. `SAVE_KEY` is unchanged.

## In scope

- 1: radio controls inline, stove pop-up, panel retired, comments updated.
- 2: both headers stabilised, the Here and Inventory strips.
- 3: the dish row and pop-up display.
- 4: the four keys.
- 5: the on-screen test, with #37's counts re-taken before and after.

## Explicitly out of scope

- The Device Options label text, the stove's control labels, and the
  timer's steps and wording: unchanged.
- Log size and the 50-entry cap: #29, which needs its own playtest.
- Food subcategories: #219.
- Carried timers: #214. Power and appliances as devices: #220. Either may
  bring new `device` items later. If one does, it follows 1's rule: controls
  inline in its item pop-up.
- Close-view building labels, and converging Wide and Close label
  visibility into one idiom (raised in #37's comments): not this pass.
- Any change to what a vessel or dish does, weighs or logs.

## Sections touched

- **RENDERING**, including MAP: the item pop-up, the new device pop-up,
  both item panels, and the Wide street labels.
- **EVENTS / UI HELPERS:** the layer wiring for the device pop-up, and the
  removal of `openDevicePanel()`'s panel path.
- **ACTIONS:** `getItemActions()`'s `device` branch only, and the four
  `log()` keys. No rule changes.
- **ITEM DATA / WORLD DATA:** the radio's tag, and the schema comments.
- The `<style>` block and the markup: the `#devicePanel` section removed,
  both strips added.

No SIMULATION change.

## UI changes

- **The radio's pop-up** shows Turn on/off and the battery controls
  directly. There is no Device Options line.
- **The stove's tab** shows a strip under the tabs, holding
  "Off · Timer: 10" and Device Options. Device Options opens a small
  pop-up: the stove's name, its two status lines, Light / Turn off (or the
  note), then +5 / +10 / +30.
- **No full-screen Device Options panel.**
- **A worn bag's tab** shows Unequip in a strip under the tabs, not in the
  header.
- **Tabs stay put** when you switch tabs, in both panels.
- **A pot of stew** lists as `Meat and vegetable stew (Cooked) (Stale) ×1 —
  4.20 kg (Food)`. Its pop-up adds "In a cooking pot".
- **Repeated saves** read `Progress saved to this browser. ×2`.
- **Wide map:** no visible change. Names that were drawn outside the view
  are no longer placed.

## Validation

- **Tab strips.** Headless Chromium at 355×770, and again at a wide
  desktop viewport. Measure each item panel's tab-strip top against its
  panel top on:
  - Here: Floor, Stove, and a non-device container;
  - Inventory: Inventory, Keychain, and an equipped bag's tab, with the
    weight at its widest (e.g. `12.50 / 13 kg`).

  Every figure for a panel must be equal. Record the before and after
  table in the changelog.
- **Device controls.** Radio: toggle on and off, remove and replace
  batteries from the pop-up, on both the Here and Inventory sides. Stove:
  light, turn off, add each timer step, and see the "Nothing you're
  carrying" note with no fire-starter. Check the pop-up stays open and
  updates after each control, and that it closes on an outside tap, on
  Esc, on leaving the room, and on switching the Here tab. Check focus
  returns to Device Options.
- **Dish.** A pot of stew in the list and in its pop-up. Eat some, then
  pour it out and see the row go back to "Cooking pot". Check that empty
  pots, pots with water and pots with ingredients are unchanged.
- **Log.** Save twice for `×2`. Save then export for two lines.
- **Map.** Re-run #37's sweep over all 176 nodes × the four Wide spans, on
  `main` and on the branch: labels shown, and labels wholly outside the
  box. After the fix, wholly-outside is 0 at every span, and no label that
  was wholly inside before is lost.
- `git diff origin/main...HEAD -- ashfall.html` is the record of what
  changed.

## Dependencies / issue linkage

Fulfils #228, #229, #230, #231 and #37: one `Closes` line each in the PR.
#222 (the cooking release's tunable register) lists "Timer display … Device
Options, Here header". After this pass that place is the device pop-up and
the Here strip. Edit that row of #222 at the wrap. Nothing is expected to be
deferred. If something is, file it.

## Open questions for Tom

None. The planning session settled all of them.

## After implementation

Open one pull request carrying:
- the version bump (PATCH);
- a `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, citing
  `Implements: handoffs/device-popup-and-panel-polish.md` and recording the
  three design decisions above and the before/after measurements;
- this handoff `git mv`'d to `handoffs/archive/`;
- `Closes #228`, `Closes #229`, `Closes #230`, `Closes #231` and
  `Closes #37`.
