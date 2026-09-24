# Ashfall — Changelog

Reverse-chronological. Each entry covers one version bump. Older entries are
kept for context but should not need to be re-read for a change scoped to a
single system — see the ARCHITECTURE comment in the script for which section
owns which behavior. The file begins at v0.1.3; 0.1.0–0.1.2 predate it and are
project genesis, not missing entries. The one genuine gap, v0.2.3, is marked in
place. v0.2.0 is not a second one — it is a skipped number, and v0.2.1's own
closing line records the bump as `"0.1.3"` → `"0.2.1"`.

Eleven versions below this line are absent from the tag list, and that is
correct. v0.1.3 through v0.3.0 shipped before this repository existed: its root
commit holds only the process guides, the game file first appears at v0.4.0, and
no commit anywhere carries a pre-0.4 `GAME_CONFIG.VERSION`. Their entries were
imported as history. So tags begin at v0.4.0 by fact rather than by oversight,
and there is no commit those eleven tags could correctly point at — the
wrap-time checklist's tagging step governs versions that shipped *here*.

---

## v0.8.2 — Device pop-up and panel polish

Implements: handoffs/device-popup-and-panel-polish.md

Implements #228, #229, #230, #231 and #37 in full, per
`handoffs/device-popup-and-panel-polish.md`. A polish pass from the v0.8.1
playtest plus two backlog fixes: device controls move out of the full-screen
Device Options panel, the item panels' tabs stop moving, a pot of stew lists as
the stew, repeated save-system lines collapse, and Wide-map street names are
placed only where they land inside the view. All rendering: nothing is added to
`state`, to any saved item or to any saved room, and `SAVE_KEY` stays
`ashfall_save_v0.8`. **PATCH**, so existing browser saves keep loading.

**UI**

- **Device controls (#228).** The radio's controls (Turn on/off, Remove
  batteries, Replace batteries) now sit in its item pop-up, as the
  flashlight's always have, on both the Here and Inventory sides. The stove's
  Device Options opens a new **device pop-up**, `#devicePop` with its own
  transparent `#devicePopBackdrop`, styled as the item pop-up through a shared
  `.pop` / `.pop-backdrop` class. It holds the stove's name in bold, its
  `stoveOnText()` and `stoveTimerText()` lines, then Light the stove / Turn off
  the stove (or "Nothing you're carrying will light it."), then the `+5 / +10 /
  +30` row. Labels are unchanged. It hangs from the Here strip at the strip's
  width, stays open after a control and redraws in place on every `render()`,
  and closes on an outside tap, on Esc, and when its target stops resolving:
  leaving the room, switching the Here tab, a load or a restart. Focus returns
  to Device Options. A control's result is its line in `#log` and nothing
  else. The `.timer-steps` buttons now share their row evenly
  (`flex:1 1 0`, no side padding, centred text), because at phone width the
  pop-up is ~146px wide and `+30` spilled past its edge at natural width.
- **Tab strips that don't move (#229).** Each item panel's header holds only
  its title and weight. Below each tab row is a new `.tab-strip`: `#worldStrip`
  holds `#worldDeviceState` ("Off · Timer: 10", unchanged, stove only) and
  Device Options, shown only on a `device` container's tab; `#invStrip` holds
  Unequip, shown only while it was shown before (any slot's tab, the keychain's
  included). A hidden strip is `display:none` and takes no space. Game over
  hides both.
- **A dish shows as the dish (#230).** A vessel holding a dish lists under the
  dish's name, labels and category, with the vessel-and-dish weight:
  `Meat and vegetable stew (Cooked) (Stale) ×1 — 4.20 kg (Food)`. Its pop-up's
  name line is the dish, its stats line `Food · 4.20 kg (4.20 kg each)`, and a
  new line under it reads `In a cooking pot`. Actions, log lines,
  `vesselButtonNames()` labels and the Crafting panel are unchanged; an empty
  vessel, or one holding water or ingredients, still shows as the vessel with
  its "Holds: …" line. Poured out or eaten up, the row goes back to the
  vessel's name on the next render, and the pop-up follows by `_uid`.
- **Save-system lines collapse (#231).** The four save-system `log()` calls
  pass their own key, `"save"`, `"load"`, `"export"` and `"import"`, with no
  `LOG_SUMMARIES` entry, so a repeat reads `Progress saved to this browser. ×2`
  and a save followed by an export stays two lines.

**Fixed**

- **Wide-map street names drawn outside the view (#37).** A name sits
  `MAP_LABEL_OFFSET` to `MAP_LABEL_OFFSET + MAP_LABEL_CAP` off its street,
  above a horizontal street and right of a vertical one, but
  `mapPositionStreetLabels()` counted a street as on screen with an inclusive
  test on its line alone. A street within 17 units of the top edge
  (horizontal) or the right edge (vertical) had its names placed wholly
  outside the box. The test now asks for the new `MAP_LABEL_DEPTH`
  (`MAP_LABEL_OFFSET + MAP_LABEL_CAP`, 17) on the name's side only:
  `street.a.y >= box.y + MAP_LABEL_DEPTH` for a horizontal street,
  `street.a.x <= box.x + box.w - MAP_LABEL_DEPTH` for a vertical one. The
  other bound is unchanged. `mapLabelMetrics()`'s `clearance` reads the same
  constant in place of the sum it spelled out. Close view is untouched.

**Removed**

- The full-screen Device Options panel: the `#devicePanel` section, the
  `#deviceStatus` / `#deviceControls` rules, `openDevicePanel()` and its
  drawer-opening path, `renderDevicePanel()` (replaced by `renderDevicePop()`),
  `deviceResult`, `runDeviceControl()`, `renderDeviceResult()`, and the
  `{ kind:"item" }` shape of `deviceTarget`, whose only shape is now
  `{ kind:"container", id }`. `.log-result` and `renderLogResult()` stay for
  Crafting.
- `getItemActions()`'s `device` branch: it pushes `batteryActions(it)` for
  every item.
- `itemStateText()`, folded into the new `itemDisplay()` (below).

**Changed / Reworked**

- `itemDisplay(it, ctx)` returns `{ name, state, category, vessel }` and is the
  one statement of whether an item shows as itself or as its vessel's dish.
  `renderItemList()`, `renderItemPop()` and the pop-up's "Holds: …" line all
  read it.
- `positionItemPop()`'s placement rule is now `placePop(pop, rect)`, taking the
  anchor's client rect. `positionItemPop()` passes its row;
  `positionDevicePop()` passes `#worldStrip`. The resize and scroll listeners
  re-place both.
- `resolveDeviceTarget()` also returns null unless `worldTab` is still the
  target container's id.

**New content**

- `portable_radio` drops `tags:["device"]` and now carries no tags. This is the
  definition data for the item-controls rule above: the tag's only reader on
  items is gone. `backfillRegistryTags()` strips it from radios in existing
  saves on load.

**Documentation**

- ITEM DATA SCHEMA: `device` is out of the item tag list, which now says an
  item's controls sit in its item pop-up and `device` is a container's tag
  only. CONTAINER SCHEMA: the `device` line names the device pop-up and the
  Here strip, and `timerMinutes` is set from the device pop-up.
- Comments that named the Device Options panel were updated: `.full-panel`,
  `.log-result`, MENU LAYERS, `layerStack`, `deviceTarget`, `batteryActions()`,
  `durabilityText()`, `logWrittenBy()`, `openCraftingForVessel()`, the stove
  timer block, `stoveOnText()`, and the Here actions' stove note.
- Issues: #222's "Timer display" row now names the device pop-up and the Here
  strip. Nothing was deferred, and no new issues were filed.

**Explicitly out of scope**

- The Device Options label, the stove's control labels, and the timer's steps
  and wording.
- Log size and the 50-entry cap (#29); food subcategories (#219); carried
  timers (#214); power and appliances as devices (#220), which will follow the
  item-pop-up rule if they bring `device` items.
- Close-view building labels, and converging Wide and Close label visibility
  into one idiom (raised in #37's comments).
- Any change to what a vessel or dish does, weighs or logs.

**Open questions / decisions resolved**

The handoff left three choices to this session.

1. **Header stability: a fixed height.** Each item panel's header is always
   two 15px lines tall (`line-height:15px; height:calc(2 * 15px + 2px);
   align-content:center`), and the weight is `white-space:nowrap`. On a narrow
   panel the weight wraps whole under the title; where it fits beside it, the
   one line sits centred in the two-line band. The other option, keeping the
   weight on the title's line and shortening the title with an ellipsis, cut
   "INVENTORY" to a few letters at phone width: at 355px the title is ~79px
   and "37.95 / 13 kg" ~75px against ~146px of room, and at 320px only ~47px
   would have been left for the title. The cost is ~17px of empty header on a
   wide screen. Retunable.
2. **The device pop-up's element: a second element** sharing the item pop-up's
   styles through `.pop`, as the handoff recommended. Its open state follows
   `deviceTarget` as the item pop-up's follows `detailItem`: Device Options
   sets `deviceTarget` and calls `render()`, and `renderDevicePop()` opens the
   layer if it is closed. Closing it (`hideDevicePop()`) clears `deviceTarget`.
3. **One display helper:** `itemDisplay()`, with `itemStateText()` folded into
   it.

**Notes / assumptions**

- `In a <vessel name, lowercased>` is functional UI text, retunable. Every
  vessel name today starts with a consonant, so "a" is always the article.
- The strips are right-aligned and wrap (`gap:4px 6px`), so on a narrow Here
  panel "Off · Timer: 0" and Device Options can take two lines. That moves the
  list, not the tabs.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` is the record of what changed.
  The script passes `node --check`.
- **Tab strips** (headless Chromium; panel top to tab-strip top, in px). Here
  on Floor, Stove and Cabinets; Inventory on Inventory, Keychain and an
  equipped backpack; each with a light load and a heavy one (`37.95 / 13 kg`,
  `12.00 / 12 kg` in the bag, `105.00 / 50 kg` on the floor):

  | Viewport | Here: Floor / Cabinets | Here: Stove | Inventory: Inventory | Inventory: Keychain | Inventory: bag |
  |---|---|---|---|---|---|
  | 355×770, before | 33 | 92 | 48 | 58 | 62 |
  | 355×770, after | 51 | 51 | 51 | 51 | 51 |
  | 1440×900, before | 33 | 43 | 33 | 43 | 43 |
  | 1440×900, after | 51 | 51 | 51 | 51 | 51 |

  After the change every figure was also 51 at 320×700, 390×844 and
  1024×768.
- **Device controls**, driven through the UI at 355×770. Radio, on both
  sides: Turn on and off, Remove and Replace batteries from the pop-up, no
  Device Options line, and the `device` tag gone after a load. Stove: Light,
  each timer step (to `Timer: 45`, the strip following), Turn off, and the
  "Nothing you're carrying" note with no fire-starter. The pop-up stayed open
  and updated after each control, drew no result area, sat at the strip's
  width directly below it, and matched `#itemPop`'s background, border,
  shadow, padding and font. It closed on Esc (focus back on Device Options),
  on an outside tap, on switching the Here tab and on leaving the room.
- **Dish.** The 2A stove's pot of stew listed and popped up as above; after Eat
  1/2 it was still the stew; after Pour it out the row read `Cooking pot ×1 —
  1.20 kg (Tool)` and the open pop-up followed it. A pot of water and a
  saucepan holding meat listed and popped up as before.
- **Log.** Save twice gave `×2`; save then export gave two lines; load twice
  gave `×2`. No page errors throughout.
- **Map.** #37's sweep, re-taken: all 176 street/mid-block nodes × the four
  Wide spans, counting each shown name's rendered box against the SVG's box.

  | Span (blocks) | Shown, before | Wholly outside, before | Shown, after | Wholly outside, after |
  |---|---|---|---|---|
  | 3 | 1542 | 168 | 1374 | 0 |
  | 4 | 3171 | 430 | 2741 | 0 |
  | 5 | 3851 | 205 | 3646 | 0 |
  | 6 | 4989 | 421 | 4568 | 0 |

  No name was partly outside on either side. Every name wholly inside on
  `main` was placed identically on the branch (same street, same transform),
  at every node and span, and the branch placed none that `main` did not.

**Sections touched**

- RENDERING, including MAP: `itemDisplay()`, `renderItemList()`,
  `renderItemPop()`, `placePop()`, `positionItemPop()`, `renderDevicePop()`,
  `positionDevicePop()`, `resolveDeviceTarget()`, `renderInventoryPanel()`,
  `renderWorldItemsPanel()`, `render()`, `mapPositionStreetLabels()`,
  `mapLabelMetrics()`, `MAP_LABEL_DEPTH`.
- EVENTS / UI HELPERS: the device pop-up's layer wiring, `positionPops()` and
  the scroll listener; `openDevicePanel()` removed.
- INVENTORY / ITEM SYSTEM: `getItemActions()`'s `device` branch.
- PERSISTENCE: the four save-system `log()` keys.
- ITEM DATA / WORLD DATA: the radio's tag and the schema comments.
- PLAYER STATE: `deviceTarget`'s comment; `deviceResult` removed.
- The `<style>` block and the markup. No SIMULATION change.

**Version**: `GAME_CONFIG.VERSION` `"0.8.1"` → `"0.8.2"`

---

## v0.8.1 — Vessel water guards and vessel button labels

Implements: handoffs/vessel-water-and-labels.md

Implements #224 and #223 in full, per `handoffs/vessel-water-and-labels.md`.
**Fill at the sink** and **Pour into the <vessel>** are no longer offered when
they would change nothing or only restart a boil, and two nearby vessels with
the same name no longer give two identical **Add to** / **Pour into** buttons.
Nothing is added to `state`, to any saved item or to any saved room, and
`SAVE_KEY` stays `ashfall_save_v0.8`. **PATCH**, so existing browser saves keep
loading.

**Fixed**

- **Water went into vessels and bottles that couldn't take more (#224).**
  `canFillAtSink()` excluded only an item full of **clean** water, so a vessel
  of tainted water was offered Fill at the sink (it only reset the boil) and a
  bottle full of tainted water was offered a no-op. Pour into was offered on
  any vessel that could hold water at all, so it emptied a bottle into a
  vessel already full of clean water, or restarted a tainted vessel's boil.
  The new `canTakeWater(it)` is the one predicate both ask: `holdsWaterAtAll(it)`,
  and either a vessel with no `water` (vessel water is all-or-nothing until
  #47) or a bottle with no `water` or `water.fill < 1`.
  - `canFillAtSink()` is now sink + `waterRunning()` + `canTakeWater(it)`.
    `doFillAtSink()` goes on re-checking it.
  - The new `canPourInto(bottle, vessel)` is true when the bottle has water it
    can hold and `vessel` is a vessel that `canTakeWater()`, or one holding
    **clean** water (and no dish) when the bottle's is **tainted** — kept by
    Tom's choice, though it only taints the vessel. `getItemActions()` offers
    Pour into on it, and `doPourIntoVessel()` re-checks it in place of its
    old `bottle.water` / `holdsWaterAtAll(vessel)` / `vesselDefOf(vessel)`
    guard. The pour's effect, log line and `addWater()` are unchanged.
  - `addWater()`'s `delete unit.boilMinutes` is unchanged. It now only runs on
    a vessel with no water or with clean water, neither of which is boiling.
- **Same-named vessels gave identical buttons (#223).** Add to / Pour into
  labelled each vessel by `v.name.toLowerCase()` alone, so two dented
  saucepans nearby gave two buttons reading the same, and
  `rebuildKeepingFocus()`, which restores focus by label, could land on the
  other saucepan's. `nearbyVessels()` now returns `{ vessel, place }` entries:
  `carried` for a vessel in `invPools()`, `Floor` for `room.floor`, else the
  container's `name` (a listed container or the heat container), its Here tab
  label. The new `vesselButtonNames(offered)` takes one action's offered
  entries and, per action:
  - gives vessels sharing a name **and** a place one button, on the fullest by
    `totalWeight(v.contents || [])`, a tie to the first in `nearbyVessels()`
    order;
  - appends ` (<place>)` to every button whose vessel name is still on two or
    more buttons, and leaves every other label as it was.

  `getItemActions()` calls it once for Add to and once for Pour into, then
  walks `nearbyVessels()` in order, so the buttons keep their old order (Add
  then Pour, per vessel). No two buttons of one action now share a label.

**UI**

- The item pop-up no longer offers Fill at the sink on a vessel holding any
  water or on a full bottle of either kind, nor Pour into on a vessel holding
  water, except a clean-water vessel when the bottle's water is tainted.
- Where two nearby vessels share a name, their Add to / Pour into buttons read
  e.g. "Add to the dented saucepan (Stove)", "(Floor)" or "(carried)".
  Same-named vessels in one place share one button. A vessel whose name is
  unique nearby keeps today's label.

**Sections touched**

- ACTIONS → INVENTORY / ITEM SYSTEM only: `canFillAtSink()`, the new
  `canTakeWater()`, `nearbyVessels()`, the new `vesselButtonNames()` and
  `canPourInto()`, `doPourIntoVessel()` in its main block; `getItemActions()`
  in its item-detail action list sub-block. No WORLD DATA, no RENDERING
  function, no PERSISTENCE change.

**Explicitly out of scope**

- #47 (fluid volumes). Vessel water stays all-or-nothing, a pour still empties
  the bottle whatever its fill, and showing what each vessel holds is #47's.
- #222 (tunable values of the cooking release).
- Log lines. The Pour and Add lines don't gain the place.
- The vessel's own pop-up (`vesselActions()`) and the Crafting panel's Dishes,
  which have no duplicate-label problem.
- Floor bags' contents. `nearbyLists()` still doesn't reach them.

**Open questions / decisions resolved**

- **How the place travels with a vessel:** `nearbyVessels()` returns
  `{ vessel, place }` pairs, as the handoff recommended. It maps each list it
  walks to a place by identity (`invPools()` membership, `room.floor`, then the
  room's containers and car containers by `items`), so `nearbyLists()` is
  unchanged. Its one caller, `getItemActions()`, was updated.
- **Where grouping lives:** a helper, `vesselButtonNames()`, shared by both
  actions, returning a `Map` from each vessel given a button to the name its
  label shows. Names are compared lowercased, since that is what the label
  shows.
- **Name of the #224 predicate:** `canTakeWater()`. The pour condition is its
  own helper, `canPourInto()`, so the offer and `doPourIntoVessel()` read one
  definition.

**Notes / assumptions**

- **Retunable wording:** the place `carried`, lowercase against the capitalized
  tab names (`Floor`, `Stove`), is Tom's pick. Functional UI text, held to
  clarity.
- Checked in headless Chromium against the kitchen: every row of the handoff's
  Fill / Pour table, and its label examples (one saucepan; Stove + Floor;
  carried + Floor + Stove; two on the Floor → one button acting on the fuller
  one). No page errors.

**Documentation**

- Comments on `canFillAtSink()`, `nearbyVessels()` and `getItemActions()`'s
  vessel loop updated for the new rules. Nothing was deferred; no new issues
  filed.

**Version**: `GAME_CONFIG.VERSION` `"0.8.0"` → `"0.8.1"`

---

## v0.8.0 — The cooking release

Implements: handoffs/cooking-release.md

Implements #206, #167, #210, #218, #178, #213, #48, #121, #119, #120, #162 and
#215 in full, per `handoffs/cooking-release.md`. The release is one MINOR,
built on one branch in ten phases, one `Phase N:` commit each. Food now
changes over time. A run starts two days after the collapse, and power and
running water fail on day 21. Food spoils, slower in a fridge and not at all in
a working freezer. Cooking happens by itself in a lit stove or campfire, and
the stove has a timer. Food is eaten by the half and the quarter. Water comes in
plastic bottles you fill at a sink. Crafting reaches the room and has a
Preparation group. Pots and pans turn their contents and water into a dish.
The one illness becomes food poisoning. **MINOR**: `SAVE_KEY` rotates from
`ashfall_save_v0.7` to `ashfall_save_v0.8`, so a 0.7 browser save does not
auto-load. An imported 0.7 file loads through `migrateCookingRelease()`.

**New**

- **Collapse clock.** `START_DAYS_AFTER_COLLAPSE` = 2, `POWER_FAILS_DAY` = 21,
  `WATER_FAILS_DAY` = 21 (separate on purpose, #149). `minutesSinceCollapse()`
  = `START_DAYS_AFTER_COLLAPSE × MINUTES_PER_DAY + state.totalMinutes`, derived
  and never stored. `powerOn(m)` / `waterRunning(m)` default `m` to now. The
  Day N clock still counts from the start of the run.
- **Food poisoning.** `ILLNESSES` (SURVIVAL / TIME SIMULATION) is the one
  definition table: `food_poisoning: { durationMin:180, minutesPerHealth:20,
  onsetLog }`, today's values. `state.illnesses` counts each running illness
  down, and `applyHungerThirst()` drains Health for each one at its own rate.
  `startIllness(id)` starts a timer only if that illness isn't already running.
  Every source rolls through `rollFoodPoisoning(p)`: if `p > 0`, it rolls
  `chance(p, "food_poisoning", state.rollSeq)` and advances `rollSeq` even when
  the player is already ill, the old order. `rollSeq`'s render invariant
  stands. `combinePoisoning(a, b)` = `1 − (1 − a)(1 − b)`.
- **Item-state core.** Every item state below extends three shared pieces:
  - `sameStackState(a, b)`, the one merge predicate. It compares `itemId`,
    `category`, no durability, `!!sealed`, cook state (and a raw row's
    `cookMinutes`), freshness, `portion`, and water kind and fill.
    `mergeRows()` concatenates `ages`, oldest first.
  - Unit helpers. Every path that changes a row's `qty` goes through
    `takeUnits(row, n)` / `dropUnits(list, i, n)`, which take the oldest
    units. `unitsOf()` is the same split without removing anything, for a
    transfer that checks its destination first. `changeOneUnit()` changes one
    unit, splitting it out of a larger row. `remergeRow()` folds a row whose
    state changed in place into a matching row, and hands the folded row's
    `_uid` to the survivor when the survivor has none.
  - `itemStateLabels(it, ctx)`: Open, cook state, freshness or Frozen, water,
    in that order, shown in the row's `.state` span and the pop-up's name
    line. Log lines keep the plain name.
- **Passive cooking (#178).** A registry entry with `cooks: { minutes,
  restores, foodPoisoningChance? }` is cookable. Its own `restores` and
  `foodPoisoningChance` are the Raw state's. An instance carries `cookState`
  (absent = raw) and, while raw, `cookMinutes`. Each tick the heat is on,
  `cookInHeat()` advances every raw cookable row lying directly in a `heat`
  container, or in a vessel there. At `cooks.minutes` the row turns Cooked,
  starts Fresh (ages reset to 0) and folds into a matching cooked row. The
  counter stops at completion (#179 will extend it). Progress holds when the
  heat stops or the item is taken out. Nothing is logged. `foodEffects(it)`
  is the one reader of restores and poisoning (Eat, the Eat gate, dish maths),
  always from the registry, never the instance's copies.
- **Wait until the … is cooked** replaces the Cook buttons. It is offered
  while the heat is on and something is progressing, and targets the least
  time left (`soonestCooking()`): a raw item, a vessel's forming or raw dish,
  ingredients cooking alone, or tainted water ("Wait until the water boils").
  On a campfire it is offered only while `fireMinutesLeft` covers the wait.
  It runs `advanceTime(remaining)` and logs "You keep an eye on it." (key
  `wait`).
- **Stove timer (#213).** `timerMinutes` on the stove container. Device
  Options shows "On"/"Off" and "Timer: N" (N = `Math.ceil`), and adds
  `STOVE_TIMER_STEPS` (+5, +10, +30) minutes per press, with no clear, no
  subtract and no cap. The presses cost no time and log nothing.
  `tickStoveTimers()` counts every timer down whether or not the stove is on.
  At 0 it rings: "You hear the ringing sound of the timer." (plain), heard
  only when the player's room has a `building` equal to the stove room's.
- **Spoilage (#48).** An entry with `spoils: { staleAfter, rottenAfter }` is
  perishable once unsealed. Each row keeps `ages`, one effective age per
  unit, oldest first. A unit is Fresh, then Stale, then Rotten. Stale has no
  effect (#216). Rotten restores × `ROTTEN_RESTORES_FACTOR` (0.35), and its
  poisoning is `combinePoisoning(own, ROTTEN_POISONING_CHANCE ×
  POISONING_TRAIT_MULTIPLIER)`: a rotten raw fish is 0.5775.
  `spoilageRate(container, m)` is ×`FRIDGE_RATE_POWERED` (0.1) in a `fridge`
  while powered, ×`FRIDGE_RATE_COASTING` (0.25) for `FRIDGE_COAST_MIN` (2 d)
  after the power fails, then 1. A `freezer` is 0 while powered and for
  `FREEZER_COAST_MIN` (5 d) after, then 1. Anything else is 1.
  `effectiveAge(container, from, to)` integrates it exactly, split at the
  power boundaries. `ageFood()` ages every perishable each tick by that
  integral, splits a row whose units now differ in state (oldest first, in
  place) and refolds changed rows. `stampMissingAges()` ages world items as if
  they had sat where they are since the collapse. It runs on a new game (boot
  and `doRestart()`), on rolled loot in `doOpenContainer()`, and on load.
  Items an action makes are new (`asNewlyMade()`): a caught fish, an opened
  can, a dish. At the default start, fridge food is 288 min old, freezer food
  0, and anything else two days.
- **Rationing (#121).** A unit carries `portion` (1, 0.75, 0.5, 0.25; absent
  = 1). Eat eats what is left of one unit. Eat 1/2 and Eat 1/4 (`EAT_PARTS`)
  are offered only while the part is less than what is left. `eatTarget()`
  eats from the unit with the least left, among rows of the same item, cook
  state and freshness, and the oldest among equals, whichever row was clicked.
  Restores and the poisoning chance scale linearly with the amount. A part
  logs "You <verb> some of the <name>." under the same key.
- **Water (Phase 7).** `plastic_bottle` holds `water: { kind, fill }` per its
  `holdsWater: { kg:0.5, restores:{thirst:30} }`, drunk through the
  rationing buttons with the fill as the portion (`consumeProfile()`, the
  interim Drink rule until #47). Tainted water rolls
  `TAINTED_WATER_POISONING_CHANCE` (0.35) × the amount. A drunk-dry bottle
  stays, empty. **Fill at the sink** (rooms with `sink`, while
  `waterRunning()`) fills one unit to full, and any tainted water taints the
  whole. It is instant, and not offered on an item already full of clean
  water, nor after day 21.
- **Reachable crafting (#119).** `nearbyLists()`: the inventory pools, the
  room's floor, the containers the Here panel lists (`listedContainers()`,
  now shared with the tab strip) and the open car. Never floor-bag or vessel
  contents, and never an unrolled container. Recipe inputs may name a
  `cookState`. `takeNearby()` takes perishable units oldest first across
  everything nearby, ties to the inventory, and everything else in list
  order. The tool gate stays carried (`hasTool()`). Output always lands on
  the room's floor, with the heap line (`logHeap()`, now shared with
  `giveItem()`) when over `floorCap`.
- **Preparation (#120).** `RECIPES` carry `group` (`craft` / `prep`) and an
  optional `doneLog`. New recipe **Fillet the fish**: one raw `fish`,
  `tool:"blade"` (the tag's first consumer), 10 min → `fish_fillets`. A
  perishable output takes the age of the oldest perishable unit used, so a
  fillet is as old as its fish.
- **Vessels and dishes (#215).** A `vessel: { kind, capacityKg, waterKg }`
  holds ingredients in `contents`, or once formed, its one dish, plus
  `water: { kind }` when full. Ingredients carry `ingredient: { role, label,
  restores?, addPortion? }`. **Add to the <vessel>** moves one unit (a
  quarter for `addPortion` items), within `capacityKg`. **Take out**,
  **Pour into** (a bottle, whatever its fill), **Pour out the water** and
  **Fill at the sink** apply until a dish forms. Tainted water boils clean in
  `BOIL_MINUTES` (5) on the heat. `DISH_TEMPLATES` is checked in order the
  first tick the vessel sits in a lit heat container: boiled pasta, boiled
  rice, soup, stew, roast, stir fry. The first match turns contents and water
  into one raw dish (`formDish()` → `buildDish()`). Its restores are the
  ingredients' contributions × (1 + `DISH_RESTORES_BONUS`, 0.25). Its
  `foodPoisoning: { raw, cooked }` is the riskiest unit's chance × that unit's
  share. Its name comes from the top one or two labels ("Fish and vegetable
  stew"), and its weight is the contents plus the water. The dish then cooks
  like any cookable. It is eaten from the pot by the rationing buttons,
  poured out with **Pour it out**, and never leaves its vessel.
- **Create dish** on an empty vessel opens the Crafting panel on **Dishes**
  with that vessel as context: its templates only, each with what the vessel
  holds toward it, what is missing and whether it's ready, and **Add
  ingredients** to pull missing units from nearby (oldest first). Water is
  never pulled.
- **`migrateCookingRelease()`**, run last on every load, idempotently.
  Retired ids are rebuilt from the registry, keeping `qty` and `_uid`
  (`MIGRATED_ITEMS`). The spoiled foods come back as their fresh ids at
  exactly Rotten, the stew pot as a cooking pot of Rotten stew, and bottled
  water as full clean bottles. Instance `illnessChance` is deleted, and
  `illnessMinutesLeft` becomes `illnesses.food_poisoning`. Missing default
  containers are added after their predecessor (the freezers), default
  container `tags` are copied (the fridges), and `sink` is copied. Then
  `stampMissingAges()`.

**New content**

- Registry: `fish` (replaces `raw_fish` / `cooked_fish`; 0.3 kg, raw hunger
  10 / 0.35, cooked hunger 35, 15 min, 12 h / 1 d), `fish_fillets`, `meat`,
  `vegetables`, `milk`, `bread`, `leftovers` (now Food), `ice_cream`,
  `plastic_bottle`, `cooking_pot`, `roasting_pan`, and the six `dish_*`
  entries. Opened cans spoil in 1 d / 3 d. Shelf lives and values are the
  handoff's.
- `pasta` and `rice_bag` are grain ingredients (hunger 120 a unit, added a
  quarter at a time). Pasta is no longer edible. The frying pan and both
  saucepans are vessels, and `burnt_saucepan` is now a Tool. The cans, meat,
  fish, fillets and vegetables carry `ingredient`.
- `campfire_kit` gains the `disassemble` tag and `disassembleLog`.
- Each of the three kitchens gets a `fridge` tag on its fridge and a
  **Freezer** straight after it (`freezer` / `freezer1a`, 10 kg, draws the new
  `kitchen_frozen` pool). The three kitchens and three bathrooms get `sink`.
- `kitchen_frozen` (emptyChance 0.2: meat 0.5, vegetables 0.5, fish 0.3, ice
  cream 0.4). `kitchen_tools` gains the cooking pot (0.15) and roasting pan
  (0.10). Every one of these is chosen, not derived, and noted as such in the
  SPAWN_POOLS comment.
- `kitchen_perishable`'s spoiled entries name the fresh foods at their old
  chances. Its fish entries are `fish` and `fish` keyed `fish_cooked` with
  `state:{ cookState:"cooked" }`, and the stew entry is a `cooking_pot` keyed
  `stew_pot` holding a cooked stew. Every `bottled_water` pool entry and
  placement is a full clean `plastic_bottle`.
- The 2A stove holds a cooking pot of cooked meat and vegetable stew (hunger
  62.5, thirst 2.5). At the start it is two days old, so Stale. The 2A
  fridge's leftovers are placed at `ages:[5 d]`, already Rotten.
- Six room texts rewritten for the new start: the 2A living room, kitchen and
  bathroom, the 1A kitchen, Oak 1B, and the 2nd St rail crossing.

**Changed / Reworked**

- *Disassemble (#167).* Offered for any `disassemble`-tagged item that a
  `RECIPES` entry outputs. It returns every input of that recipe at full
  quantity, and logs the registry's `disassembleLog` with `{qty}` replaced by
  the first input's quantity, or "You take the <name> apart." if the item has
  none. The kit's line is unchanged in play.
- *Dismantle (#210).* Refunds `CAMPFIRE_DISMANTLE_BASE_WOOD` (1) plus
  `Math.floor(fireMinutesLeft / FIRE_MINUTES_PER_WOOD)`. A burnt-out fire
  gives 1, and one put out right after building from a kit gives 3.
- *Crafted items* land on the floor, not in the open inventory tab.
- *Registry-only fields.* `REGISTRY_ONLY_FIELDS` (`carryFactor`,
  `foodPoisoningChance`, `disassembleLog`, `cooks`, `spoils`, `holdsWater`,
  `vessel`, `ingredient`, `dish`) are left off instances by
  `itemFromRegistry()` and read through `registryEntryOf()`.
  `illnessChance` is renamed `foodPoisoningChance` on the registry.
- *Spawn pool entries* take an optional `key` (the roll key, and the
  duplicate check, default `itemId`) and `state` (instance fields after
  `itemFromRegistry()`). `rolledPoolFor()` returns each stack's key, and
  `sampleSeeds()` tallies by key.
- *Weight.* `itemUnitWeight()` counts a unit at its `portion` of
  `unitWeight`, plus water (a bottle's `holdsWater.kg` × fill, a vessel's
  `waterKg`).

**Fixed**

- **#206: Enter on a Here or Inventory tab dropped focus to the page.** Both
  tab strips were rebuilt with `innerHTML = ""`, and `rebuildKeepingFocus()`
  returned early for anything that wasn't an open layer. It now takes an
  `isLayer` flag (default true), and the strips pass `false`. Focus returns to
  the tab with the same label, or to the tab now at the same position.

**Removed**

- `HEAT_RECIPES`, `doCookInContainer()` and the "Cook the …" buttons.
- `ILLNESS_DURATION_MIN`, `ILLNESS_MINUTES_PER_HEALTH` (now in `ILLNESSES`),
  `state.illnessMinutesLeft` (now `state.illnesses`).
- Ids `raw_fish`, `cooked_fish`, `spoiled_milk`, `moldy_bread`,
  `rotten_produce`, `rotten_leftovers`, `pot_of_spoiled_stew`,
  `bottled_water` (see `MIGRATED_ITEMS`).
- The `it.itemId === "campfire_kit"` Disassemble branch.

**UI**

- Item names carry state: (Open), (Raw)/(Cooked), (Fresh)/(Stale)/(Rotten)/
  (Frozen), (Water)/(Tainted), and a vessel with a dish reads "Dented
  saucepan: Fish stew (Cooked) (Fresh)". A vessel's pop-up lists "Holds: …"
  and its water.
- Eat / Drink 1/2 and 1/4. New pop-up actions: Fill at the sink, Add to …,
  Take out …, Pour into …, Pour out the water, Pour it out, Create dish.
- Here: the Wait button replaces Cook. With the stove's tab selected, the
  header reads `On · Timer: 30` between the weight and Device Options, and
  the header wraps by piece on a narrow panel.
- Device Options (stove): the Timer line, then +5 / +10 / +30 after Light /
  Turn off.
- Crafting panel: a search box, **All · Crafting · Preparation · Dishes**, a
  **Can make now** toggle, "(needs Fish (Raw) ×1, a blade)" wording, the
  Dishes catalogue, and vessel context from Create dish. Search and filters
  are UI-only and reset when the panel closes.

**Documentation**

- The ITEM DATA SCHEMA now covers `cooks`, `cookState`, `cookMinutes`,
  `spoils`, `ages`, `portion`, `holdsWater`, `water`, `vessel`, `contents`
  (a vessel's too), `ingredient`, `dish` and a dish's instance fields,
  `boilMinutes`, `foodPoisoningChance` (renamed, registry-read) and
  `disassembleLog`. The tag list adds `disassemble`, and `blade` moves to
  "read by a mechanic today". The CONTAINER SCHEMA adds `fridge`, `freezer`,
  `timerMinutes` and the note that a future respawn (#15) must skip
  perishables. The ROOM SCHEMA adds `sink`. SPAWN_POOLS documents `key`,
  `state` and the chosen chances. The ARCHITECTURE word list names no Cook
  action and is unchanged.
- The `CAMPFIRE_DISMANTLE_BASE_WOOD` comment records that the build → put
  out → dismantle cycle breaks even only because the build burns fuel and
  the baseline is ≤ 1.
- Validators: `validateItemRegistry()` checks `foodPoisoningChance` and
  `cooks.foodPoisoningChance` ∈ [0, 1], `cooks.minutes` > 0, `staleAfter` <
  `rottenAfter`, `ingredient.role` ∈ `INGREDIENT_ROLES`, and that every
  `DISH_TEMPLATES` item is a dish entry with `cooks`.
  `validateReachability()` counts dish entries as reachable and duplicates by
  key. `ACTION_GRANTED_ITEM_IDS` is `firewood`, `fish` and `spare_batteries`,
  and `REPORTED_TOOL_TAGS` gains `blade`.
- Filed: #223 (vessel action labels collide when two vessels share a name)
  and #224 (Pour into a vessel already full of clean water wastes the
  bottle). Nothing in the handoff's scope was cut.

**Sections touched**

- CONFIG / CONSTANTS: the new constants, `RECIPES` (groups, fillet),
  `DISH_TEMPLATES`; `HEAT_RECIPES` removed.
- WORLD DATA: registry, pools, kitchens and bathrooms, six room texts.
- PLAYER STATE: `illnesses`.
- CORE UTILITIES: comments only.
- INVENTORY / ITEM SYSTEM: merge, units, eating, opening, sinks, vessel
  actions, actions list.
- WORLD INTERACTION: collapse clock helpers, `doOpenContainer()` stamping.
- SURVIVAL / TIME SIMULATION: illness, spoilage, world ticking.
- CRAFTING: reach, unit choice, output.
- FIRE / COOKING: cooking tick, Wait, timer, dismantle, vessels and dishes.
- PERSISTENCE: migration, stamping on restart, dev helpers.
- EVENTS / UI HELPERS and RENDERING: labels, pop-up, Here actions and
  header, Device Options, crafting panel, tab-strip focus.

**Explicitly out of scope**

- #179 burning, #214 carried and digital timers, #216 Stale effects, #217
  freezing and thawing times, #219 food subcategories, #220 power for other
  appliances, #47 fluid volumes and drinking from vessels or taps, #52
  tainted water sources, #211 disassembly by category, #96 the propane torch,
  #149 world-generation options, #137 the hospital opening, #15 respawn (the
  comment only), #134 / #116 per-unit durability, #89 building ids (the timer
  compares names), #212 the sidebar Wait. Bowls and serving out of vessels,
  #119's used-tool-to-inventory rule, the `needsHeat` gate, and the Day N
  clock are unchanged.

**Open questions / decisions resolved**

- **`rebuildKeepingFocus()`**: a third parameter, `isLayer = true`, rather
  than a sibling helper. The tab strips pass `false`.
- **Helper names**: `sameStackState`, `mergeRows`, `unitsOf` / `takeUnits` /
  `dropUnits`, `changeOneUnit`, `remergeRow`, `itemStateLabels` /
  `itemStateText`, `foodEffects` / `unitFoodEffects`, `consumeProfile`,
  `eatTarget` / `leastLeftRow`, `spoilageRate`, `effectiveAge`, `stampAges` /
  `stampMissingAges`, `ageFood`, `cookInHeat` / `cookItem` / `cookVessel`,
  `soonestCooking`, `templateStatus`, `buildDish` / `formDish` / `dishFrom`,
  `nearbyLists` / `takeNearby`, `migrateCookingRelease`.
- **Owning container**: `forEachItemList()`'s visitor gains a third argument,
  `container`. Existing callers ignore it.
- **Crafting panel markup**: `#craftFilters` above the list (a search input,
  a wrapping row of group buttons, a checkbox), and Dishes rows as `.dish-row`
  divs. Checked at 390 px.
- **Wording**: "(needs Cloth ×2, Duct tape ×1)", now with ×. Tools read "a
  blade". Dishes catalogue: "A pot or saucepan with water, and two or more
  meat or vegetables", generated from the template. In vessel context: "holds
  1 of 2 · needs one more meat or vegetable, and water", "ready to cook",
  "ready once the water boils", "holds something that doesn't belong in it".
  Drinking logs "You drink the water." (the water, not the bottle). The
  fillet logs "You fillet the fish." (`doneLog`). The vessel's pop-up reads
  "Holds: …", "Full of water" / "Full of tainted water", "Empty". All
  retunable.
- **Here header**: `On · Timer: N` sits between the weight and Device
  Options, and hides when empty.
- **Judgment calls Tom should confirm:**
  - The trash pool's `rotten_leftovers` entry, which the handoff didn't
    mention, became `leftovers` with `state:{ ages:[3 d] }`, pinned Rotten,
    so the bin still holds rotten leftovers.
  - A part-eaten unit weighs its portion. Without that, adding pasta a
    quarter at a time would put four full units' weight in the pot and trip
    its `capacityKg`.
  - A dish forms and starts cooking in the same tick, so a 30-minute stew is
    done 30 minutes after it forms.
  - `CAMPFIRE_DISMANTLE_BASE_WOOD` sits beside the other fire fuel constants
    in FIRE / COOKING, not in CONFIG / CONSTANTS.
  - Refilling a vessel restarts its boil.
  - Pour out the water and Take out are silent, like Take.
  - A row split by freshness keeps its youngest units (and its `_uid`).

**Notes / assumptions**

- Every number above is the handoff's. #222 is the register of which are
  Tom's, drafts or placeholders, and the code matches it. `DISH_RESTORES_BONUS`
  is a placeholder until the bonus is discussed.
- A 0.7 raw fish carried in an imported save has no age, so it is aged from
  the collapse like any world item and usually arrives Rotten, as the handoff
  specifies.
- Ticking a day costs about 140 ms against v0.7.5's 57 ms in headless
  Chromium, for ageing every perishable each minute.

**Validation performed**

- Headless Chromium against an instrumented scratch copy (a direct-eval hook,
  and a spy on `rollFoodPoisoning` for the chance checks), driving the UI
  and the game's own actions. The shipped file carries no hook. One suite per
  phase, all re-run on the final build: 21, 20, 27, 16, 24, 12, 24, 29, 46
  and 24 checks, every one passing. They cover every check the handoff
  lists, including:
  - the Take/Store/Open/Eat sequence, diffed against v0.7.5 for identical
    stacks;
  - a v0.7.5 export imported, then exported and imported again, byte for
    byte unchanged;
  - all four validators and both seed reports, with no page errors.
- `git diff origin/main...HEAD -- ashfall.html` is the full change. Each
  phase's commit is `Phase N: …`.

**Version**: `GAME_CONFIG.VERSION` `"0.7.5"` → `"0.8.0"`

---

## v0.7.5 — Equip load delta, pop-up tab guard

Implements: handoffs/equip-load-pop-up-tab-and-tag-commands.md

Implements #203, #201 and #205, per
`handoffs/equip-load-pop-up-tab-and-tag-commands.md`. Equip is now checked
against the hard limit by what it actually adds to the load, from either side.
The item pop-up closes when its item is no longer on its side's current tab.
The third part, the wrap-time tag block, is documentation only. No new state:
`SAVE_KEY` stays `ashfall_save_v0.7`. **PATCH**, so existing browser saves keep
loading.

**Fixed**

- **#203: equipping a bag stowed in a lower-factor worn bag could raise the
  load past `CARRY_HARD_LIMIT_KG`.** `doEquip()` checked the hard limit only
  when `sourceKind === "world"`. From the inventory side, a bag moving from a
  0.72 backpack into its own 0.81 slot adds load and was never checked. The
  check now runs on both sides, by the delta:
  `added = itemUnitWeight(it) × (carryFactorOf(it) − srcFactor)`, where
  `srcFactor` is 0 in the world and `carryFactorOf(src)` in the inventory (1
  for the loose inventory and the keychain, the worn bag's own factor
  otherwise). It refuses only when `added > 0 && playerLoad() + added >
  CARRY_HARD_LIMIT_KG`, so a player already past the limit may still equip a
  bag when doing so lowers the load or leaves it unchanged. The world side is
  unchanged: with `srcFactor` 0, `added` is the old expression. Same refusal
  line ("You can't carry any more.", `warn`), and Equip stays offered.
- **#201: the item pop-up could act on the wrong item after a keyboard switch
  of the Here tab.** The pop-up closed only when its item left every list, but
  the transfer functions (`doTake`, `doStore`, `doConsume`, `doOpen`,
  `doEquip`) resolve their list from the *current* tab, so after a tab switch
  the pop-up's index pointed into a different list. `renderItemPop()` now also
  clears `detailItem` when `found.list` is not, by identity, the list its
  side's current tab resolves to: `worldSlot(world[state.currentRoom],
  worldTab).items` for `"world"`, `invSlot(invTab).items` otherwise. A null
  slot counts as a mismatch. That one check covers a tab-strip click or
  keypress, `doOpenContainer()`, a vanished tab falling back, and
  `doEquip()` setting `invTab`. Switching the *other* side's tab leaves the
  pop-up open, since that only moves where Take/Place/Store go. `doOpen()`
  re-points `detailItem` into the same list, so it stays open.

**UI**

- Equipping a bag from inside a lower-factor worn bag near 32.5 kg can now
  fail with "You can't carry any more."
- Switching a tab on the same side as an open pop-up's item closes the pop-up.

**Documentation**

- `doEquip()`'s comment, which said equipping from the inventory side was
  never refused on load, is rewritten: refused only when it would raise the
  load past `CARRY_HARD_LIMIT_KG`, a bag counting at 0 in the world and at its
  source's factor in the inventory. The carry-limits comment above
  `CARRY_LIMIT_KG` ("nothing may add load past … only Unequip can take it
  there") was left as is: it is accurate again.
- The comment above `renderItemPop()` adds a close reason ("its side's tab no
  longer showing it") and a paragraph on why the tab check exists.
- Nothing was deferred. The one known follow-up, focus loss when a tab strip
  is rebuilt, was already filed as #206.

**Sections touched**

- INVENTORY / ITEM SYSTEM: `doEquip()` (mechanics and comment).
- RENDERING: `renderItemPop()` (the guard and its comment).
- No WORLD DATA, no SIMULATION, no PERSISTENCE.

**Open questions / decisions resolved**

- **Wording.** The two code comments are as above. `CLAUDE.md` checklist item
  6 now carries the handoff's block verbatim, and states why it resolves the
  commit rather than using `HEAD` (the `v0.4.4`/`v0.4.5` → #32 history) and
  its three safeguards: `[ -n "$C" ]`, the trailing ` from`, and a squash or
  rebase merge falling through to the `else`.
- **#205 had partly landed already.** PR #207 had rewritten item 6, the
  documentation-only "no tag commands" line and the Project Guide's pointer
  before this pass. The guide pointer and the no-tag line already said what
  the handoff asks, so they are untouched. Item 6's block was the one
  difference: #207's tagged first and checked the version after, and used
  `--first-parent` with a trailing space rather than `--merges` with
  ` from`. It is replaced by the handoff's check-before-tagging block.
- **Shell.** The block assumes a POSIX shell (bash, zsh, Git Bash), as item
  6's `grep` already did. Retunable if Tom tags from elsewhere.
- **Guard shape.** One conditional in `renderItemPop()` covers both the
  existing null-`found` close and the new tab mismatch, rather than two
  separate checks.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html`: only `GAME_CONFIG.VERSION`,
  `doEquip()`'s check and comment, and `renderItemPop()`'s guard and comment.
- Headless Chromium, against a copy of the script with a test hook appended:
  a duffel stowed in a worn backpack, with the load 0.05 kg under the hard
  limit, is refused (adds 0.072 kg) and stays in the backpack, with the
  refusal logged; a duffel in the loose inventory is equipped while the load
  is past the limit, and the load drops; a pop-up on an inventory item stays
  open after a Here tab switch and closes after an inventory tab switch. No
  page errors.

**Explicitly out of scope**

- Making the transfer functions act on `found.list` (#201's option b), and
  trapping focus in the pop-up (#201's option c, overlaps #78).
- Focus loss when a tab strip is rebuilt (#206).
- Hiding or disabling Equip when it would be refused.
- Any change to Unequip's "always allowed".
- #200 (carry limit from the character) and #152 (parallel handoffs).

**Version**: `GAME_CONFIG.VERSION` `"0.7.4"` → `"0.7.5"`

---

## v0.7.4 — Carry load

Implements: handoffs/carry-load.md

Implements #168 and #170 in full, per `handoffs/carry-load.md`. The player has
one carry limit, 13 kg. A worn bag counts for less than its weight. Over the
limit, moving is slower and costs Exertion, and from 26 kg it costs Health.
Nothing may add load past 32.5 kg, except Unequip. The loose inventory loses
its 3 kg cap. The load is derived and never stored. Each bag's factor is read
from `ITEM_REGISTRY` by `itemId`. The only save-facing change deletes a field
(`inventory.capacityKg`) on load. `SAVE_KEY` stays `ashfall_save_v0.7`.
**PATCH**, so existing browser saves keep loading.

**New**

- **`playerLoad()`** (INVENTORY / ITEM SYSTEM) is the one definition every
  carry rule reads. It is `totalWeight(state.inventory.items)`, plus, for each
  filled `CONTAINER_SLOTS` slot, `(slot.unitWeight + totalWeight(slot.items))
  × carryFactorOf(slot)`. The keychain counts at 1, its ring and its keys
  included. A bag that is not worn counts in full wherever it is.
- **`carryFactorOf(thing)`** takes a slot or an item. It returns
  `ITEM_REGISTRY[thing.itemId].carryFactor` when the entry defines one, and 1
  otherwise: the keychain, the loose inventory, an unknown or unrepaired slot.
  The factor is never copied onto a slot or an item.
- **Constants**, all retunable and each written once:
  - `CARRY_LIMIT_KG = 13` and `CARRY_HARD_LIMIT_KG = CARRY_LIMIT_KG * 2.5`
    (32.5), beside `playerLoad()`.
  - `LOOSE_INVENTORY_MAX_KG = 100` and `LOOSE_INVENTORY_MAX_ENTRIES = 1000`,
    beside them. These hidden safety caps are never shown.
  - Beside `doMove()`, on the precedent of `JOG_EXERTION_PER_MIN`:
    `OVERLOAD_HARM_START_KG = CARRY_LIMIT_KG * 2` (26),
    `OVERLOAD_MIN_SPEED_FACTOR = 0.25`,
    `OVERLOAD_MAX_EXERTION_PER_MIN = JOG_EXERTION_PER_MIN`,
    `OVERLOAD_HARM_MINUTES_PER_HEALTH_START = 10` and
    `OVERLOAD_HARM_MINUTES_PER_HEALTH_END = 5`.
- **The bands.** `overloadFraction(load)` runs from the carry limit to the
  hard limit, and `harmFraction(load)` from 26 kg to the hard limit. Both are
  clamped to [0, 1] through `loadFraction()`, so past the hard limit both stay
  at 1.
  - **Speed.** `overloadSpeedFactor(load) = 1 − over × (1 −
    OVERLOAD_MIN_SPEED_FACTOR)`. `moveMinutes()` divides by the gait's speed
    times this. The `MIN_MOVE_MIN` floor does not scale. The move buttons
    price through `exitMinutes()`, so they show the slower times with no
    RENDERING change.
  - **Exertion.** Every move adds `over × OVERLOAD_MAX_EXERTION_PER_MIN ×
    minutes`, at every gait, on top of Jog's surcharge.
  - **Health.** While the load is at or above 26 kg, a move costs `minutes ×
    overloadHealthPerMin(load)`. That rate runs linearly from 0.1 per minute
    at 26 kg to 0.2 per minute at 32.5 kg and beyond. The move logs
    "Something in your back twinges under the weight." as `warn`, with the
    log key `overload-harm`, so consecutive moves collapse to "×N". Then it
    calls `checkGameOver()`.
  - `doMove()` samples `playerLoad()` once, beside its gait sample and before
    `advanceTime()`. `minutes` includes the slowdown, so the per-minute
    Exertion and Health grow with it.
- **The hard limit.** `addToDestination()` returns `{ok:false,
  reason:"load"}` when `playerLoad() + itemWeight(item) ×
  carryFactorOf(dst)` would pass `CARRY_HARD_LIMIT_KG`. The checks run in
  this order: keychain, then room (the bag's own `capacityKg`, or for the
  loose inventory the hidden caps), then load.
  - `doTake()` logs "You can't carry any more." (`warn`) on `load`.
  - `giveItem()` drops the item to the floor on `load` through its existing
    floor lines. Its code is unchanged: every refusal but the keychain's
    already took them. This covers crafting, fishing, chopping, a dismantled
    campfire, Disassemble and removed batteries.
  - `doEquip()` from the world side (floor, container or floor-bag tab) is
    refused with the same line when `itemUnitWeight(bag) × carryFactorOf(bag)`
    would pass the hard limit. From the inventory side it is never refused on
    load. `doUnequip()` is never refused, and can take the load past the hard
    limit.

**New content**

- `carryFactor` on the five bags in `ITEM_REGISTRY`: `worn_backpack` 0.72,
  `fanny_pack` 0.76, `duffel_bag` 0.81, `tote_bag` 0.85, `purse` 0.85. Each is
  Tom's first proposal × 0.9, floored to two decimals, and all are retunable.
  This is the mechanic's own definition data, not instance data: no room,
  placement or description changed.

**Removed**

- **The loose inventory's weight cap.** `makeDefaultState()`'s `inventory` no
  longer carries `capacityKg:3`. The new `backfillInventoryCap()`
  (PERSISTENCE) deletes `state.inventory.capacityKg` on every load, after the
  other backfills, so no old save keeps its 3 kg. Nothing reads a capacity off
  the inventory any more. The only weight guards on it are the hidden caps,
  checked in `addToDestination()` alone. A refusal there is `reason:"capacity"`,
  so `doTake()` says "That won't fit — not enough room there." `doUnequip()`
  and `doOpen()` don't check the caps.

**UI**

- **Inventory tab header** shows the player's load against the limit, e.g.
  `9.15 / 13 kg`. It is the normal colour at or under 13 kg, `var(--warn)`
  over 13 kg, and `var(--danger)` from 26 kg.
- **Bag tabs** are unchanged: the bag's own fill against its own capacity,
  whatever its factor. **Keychain** is unchanged (`x kg`).
- **Log:** "You can't carry any more." when Take or a world-side Equip is
  refused at the hard limit. "Something in your back twinges under the
  weight." on each move at or above 26 kg.

**Documentation**

- ITEM DATA SCHEMA documents `carryFactor` beside `capacityKg`.
- New comments on the carry constants, `carryFactorOf()`, `playerLoad()`,
  `addToDestination()`'s check order, `giveItem()`, `doEquip()`'s world-side
  check, `doUnequip()`'s deliberate lack of one, the overload block beside
  `doMove()`, `moveMinutes()`, `backfillInventoryCap()` and the Inventory
  header. The backfill's comment carries no count or ordinal.
- `validateItemRegistry()` (dev-only) also flags any entry with a `slotType`
  whose `carryFactor` is missing or not in (0, 1].
- Filed #203. An inventory-side Equip is never refused on load, per the
  handoff. But a bag stowed inside a worn bag with a lower factor counts for
  more once equipped. A full purse in the backpack gains 0.70 kg, and a
  duffel about 1 kg. So near the hard limit, that Equip can pass it by up to
  about 1 kg. Nothing else was deferred.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` touches only the sections
  listed below, plus the version line.
- Exercised in headless Chromium. A test-only hook exposed `state`, `world`
  and the functions under test. The hook is not in the shipped file. No page
  errors, and `ashfallDev.validateItemRegistry()` returned `[]`.
  - **Load arithmetic.** A new game reads `0.08 / 13 kg`: the keychain's
    0.05 plus its 0.03 kg key. Equipping an empty backpack from the floor gave
    0.51, and filling it to 12 kg gave 9.15. The handoff's figures (0.05,
    0.48, 9.12) leave out the key. Its formula counts the keychain's
    contents, and that formula is what shipped. The backpack's own tab read
    `12.00 / 12 kg`.
  - **Speed**, on a 100 m grid move at Walk: 1.0× at 13 kg, 1.6× at 22.75 kg,
    4.0× at 32.5 kg, and 4.0× at 40 kg. Jog's 100 m stays on its 1-minute
    floor at no load.
  - **Exertion and Health on real moves.** At 0 and 13 kg the move cost
    nothing extra. At 20 and 25.9 kg the Stamina drop equalled `over × 0.5 ×
    minutes` and Health did not change. At 26 kg a 2.78-minute move cost
    0.278 Health (0.1 per minute) and 0.926 Stamina. At 32.5 kg a 5.56-minute
    move cost 1.111 Health (0.2 per minute) and 2.778 Stamina. A second move
    at 30 kg collapsed the log line to "×2".
  - **The header.** Normal at 13.00, `--warn` at 13.50 and 25.90, `--danger`
    at 26.00 and above.
  - **The hard limit.** At 32 kg, taking a 1 kg item logged "You can't carry
    any more." and moved nothing. At 31 kg it moved. At 32.43 kg, 0.09 kg
    went into the worn backpack (adding 0.065), and 0.1 kg into the loose
    inventory was refused. Taking from a floor-bag tab at 32 kg was refused
    the same way. A campfire kit crafted at 32.4 kg, from firewood held in
    the backpack, dropped to the floor with "No room for the campfire kit —
    it drops to the floor instead." Equipping a floor duffel holding 5 kg
    was refused at 28 kg and allowed at 27 kg. Unequipping a full duffel at
    30 kg took the load to 33.57 kg.
  - **Hidden caps.** With 99.5 kg loose, Take logged the room message. With
    1000 entries loose, Take logged the room message. With 99.9 kg loose,
    `giveItem()` dropped a raw fish to the floor. Neither cap appears in any
    header.
  - **An old save.** A save stamped `0.7.2` with `inventory.capacityKg:3`
    loaded, had no `capacityKg` on the inventory afterwards, and took 5 kg
    loose.
  - **Death.** A move at 32.5 kg with 0.5 Health logged the twinge, then
    "Your body finally gives out.", and drew "You did not survive."

**Sections touched**

- ITEM DATA SCHEMA / `ITEM_REGISTRY`: `carryFactor` on five bags, and the
  schema comment.
- PLAYER STATE: `makeDefaultState()`'s inventory.
- CORE UTILITIES: `moveMinutes()`. The handoff files it under WORLD
  INTERACTION, but it lives in CORE UTILITIES and was edited in place.
- INVENTORY / ITEM SYSTEM: the carry constants, `carryFactorOf()`,
  `playerLoad()`, `addToDestination()`, `giveItem()` (comment only),
  `doTake()`, `doEquip()` and `doUnequip()` (comment only).
- WORLD INTERACTION: the overload constants and helpers, and `doMove()`.
- PERSISTENCE: the new `backfillInventoryCap()`, its call in
  `applyLoadedData()`, and `validateItemRegistry()`.
- RENDERING: `renderInventoryPanel()`'s header.

STAMINA / FATIGUE is unchanged: movement declares more Exertion, and the system
handles it as it handles any other. No SIMULATION, no CRAFTING, no FIRE /
COOKING.

**Open questions / decisions resolved**

- **Where the constants live: the handoff's recommendation.** The carry
  limits and the hidden caps sit beside `playerLoad()`. The speed, Exertion
  and Health figures sit beside `doMove()`.
- **The `capacityKg` removal: a named backfill,** `backfillInventoryCap()`,
  the handoff's recommendation. It is listed with the other load-time
  repairs.
- **Helper shape.** One `carryFactorOf(thing)` serves both of the handoff's
  lookups, `slotFactor(slot)` and `carryFactor(bag)`. A worn slot and a bag
  item both carry `itemId`, so one function keeps the lookup in one place.
  `loadFraction(load, from, to)` holds the clamped fraction, and
  `overloadFraction()` and `harmFraction()` are its two uses.
  `overloadSpeedFactor()` and `overloadHealthPerMin()` each write one formula
  once.
- **The registry check: added,** the handoff's recommendation.

**Notes / assumptions**

- **Every figure above is retunable.** That covers the 13 kg limit, the 2.5×
  and 2× multiples, the 0.25 speed floor, the jog-rate Exertion cap, the
  10 and 5 minutes per Health point, the five factors, and the 100 kg and
  1000-entry hidden caps. Interpolating Health per minute rather than minutes
  per point was Tom's choice, and is flagged retunable with the rest.
- **The overload Exertion is a second `applyExertion()` call** after Jog's
  line, rather than one call with a summed figure. The result is the same:
  Stamina drains first, then Fatigue. `applyExertion()` returns early at
  zero, so a move at or under 13 kg stamps no `lastExertionMinute` it didn't
  before.
- **The hidden entry cap refuses at 1000 entries even when the item would
  merge into an existing stack,** as the handoff specifies
  (`items.length >= 1000`).
- **The header's colour is set inline** (`style.color`), the precedent of the
  item pop-up's "each" line, rather than through new CSS classes.

**Explicitly out of scope**

- Capacity retunes. The shipped bag capacities stay.
- Load affecting anything but movement. Chopping, fishing, sleep and rest are
  unchanged.
- Clothing (#56), Health (#53) and weather (#58) feeding the limit or the
  penalties, and run options (#149).
- #167 (Disassemble).
- New log wording for `giveItem()`'s load refusal.
- #203 (inventory-side Equip from inside a lower-factor bag).

**Version**: `GAME_CONFIG.VERSION` `"0.7.3"` → `"0.7.4"`

---

## v0.7.3 — Here panel tabs

Implements: handoffs/here-panel-tabs.md

Implements #169, #188 and #197 in full, per `handoffs/here-panel-tabs.md`. A
bag lying on the floor opens as its own Here tab. A container tagged `device`
is a Here tab before the room is searched. Four PERSISTENCE comments lose a
stale count and three stale ordinals. Nothing is added to `state`, to any saved
item or to any saved room, and `SAVE_KEY` stays `ashfall_save_v0.7`. **PATCH**,
so existing browser saves keep loading.

**New**

- **Floor bags open as Here tabs (#169).** The new `floorBags(room)`
  (INVENTORY / ITEM SYSTEM) is the one statement of which floor items open. It
  returns every item on `room.floor` that has a `slotType` and a numeric
  `capacityKg`, which is every registry bag. A dropped keychain has
  `capacityKg:null`, so it stays shut, and `keychainAllows()` keeps its one
  enforcement point. Bags in room containers, car containers, other bags or
  the inventory also stay shut. Three places call `floorBags()`:
  - **The Here tab list.** Each floor bag is a tab after Floor, in floor order,
    before the room's containers and car containers. The tabs show whether or
    not the room has been searched.
  - **`worldSlot()`.** A floor-bag key resolves to
    `{ items: bag.contents, capacityKg: bag.capacityKg }`. Take, Store,
    Eat/Drink, Open and Equip all route through `worldSlot()`, so they work
    from a floor-bag tab with no new action code. `doStore()`'s capacity check
    uses the bag's own `capacityKg`, not the room's `floorCap`.
  - **`findItemByUid()`.** It also searches the `contents` of the current
    room's floor bags, one level deep, and no other bag. Without this, an
    item's pop-up opened from a floor-bag tab closed at once.

  A floor-bag tab never calls `doOpenContainer()`, so it never rolls loot. The
  tab handler's container lookup misses a bag key, as before.
- **`floorBagTab(bag)`** returns a floor bag's tab key, `"bag:" +
  ensureUid(bag)`.
- **`shownWithoutSearch(container)`** (WORLD INTERACTION) is true for a
  container tagged `device`. The Here tab list and `doSearch()` both ask it.

**Fixed**

- **1B's stove needed a search first (#188).** `renderWorldItemsPanel()` added
  a room's containers only when `!room.searchLabel || room.searched`. That
  gated 1B's Stove, and with it the Device Options button, behind "Search the
  unit", though the room description names the stove. An unlocked container
  now becomes a tab when the room is searched or `shownWithoutSearch(c)` is
  true. Order is the containers' authored order. Before the search, 1B shows
  Floor and Stove. After it, 1B shows Floor, Stove, Tool Cabinet, Desk and
  Closet. `roomStove()`, `getHeatContainer()` and the Device Options panel
  never read the search, so they are unchanged.
- **`doSearch()` listed what was already in view.** Its line now leaves out
  `shownWithoutSearch()` containers. In 1B it reads "You search the place
  carefully. You find: tool cabinet, desk, closet." When nothing is left to
  list, it logs "You search the place carefully. You find nothing else." as
  `"good"`. No room reaches that line yet.
- **A vanished tab left no tab active.** `renderWorldItemsPanel()` fell back to
  Floor only after it had built the buttons and run `revealActiveTab()`. On the
  render where the open tab disappeared, no button carried `.active`. The
  fallback now runs before the buttons are built, so Floor is marked active,
  and scrolled into view, on that same render.

**UI**

- **Here panel:** each bag on the floor has its own tab after Floor, named
  after the bag. When bags share a name, the first in floor order keeps the
  plain name and later ones are numbered from 2: "Purse", "Purse 2". The
  header reads `<contents weight> / <capacityKg> kg`, the same as a
  container's. The inventory's button reads "Store" there, as on any non-floor
  tab.
- **1B:** the Stove tab and its Device Options button show before the unit is
  searched. The search line no longer names the stove.

**Documentation**

- #197: `validateLoadedWorld()`'s comment says "the load-time backfills", not
  "the three backfills". `backfillRoomAddresses()`, `backfillSlotItemIds()`
  and `backfillIllnessScale()` no longer number themselves ("third", "fourth",
  "sixth companion"). No other words changed.
- New comments on `floorBags()`, `floorBagTab()`, the floor-bag branch of
  `worldSlot()` and `findItemByUid()`, `shownWithoutSearch()`, `doSearch()`'s
  empty line, and the tab list's order and fallback.
- Filed #201. In v0.7.2 a keyboard user can switch the Here tab while an item's
  pop-up is open. The pop-up's Take, Eat, Open and Equip then act on the item
  at the same index in the new tab's list. It predates this pass, which only
  adds more tabs it can happen on. Nothing else was deferred.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` touches only the sections
  listed below, plus the version line.
- Exercised in headless Chromium. The page ran with a test-only hook added to
  expose `world`, `state` and `render()`. The hook is not in the shipped file.
  v0.7.2 (`origin/main`'s `ashfall.html`) ran alongside as the baseline. No
  page errors.
  - **Floor bags.** With two purses on the floor, the tabs read Floor, Purse,
    Purse 2, then the room's containers. Purse 2 read `0.00 / 5 kg`. Storing
    Dish soap made it `0.40 / 5 kg`, and the first purse stayed empty. Storing
    6 kg of laundry detergent logged "That won't fit there." and changed
    nothing. The soap's pop-up opened from Purse 2 stayed open, and its Take
    All took the soap back. Clicking the tab six more times added no loot.
    Taking the first purse from Floor left one tab, "Purse", still holding the
    soap. A bag in a room container got no tab.
  - **The fallback.** With the remaining purse's tab open, the hook removed the
    purse and re-rendered. Floor was the only active tab on that render. No
    player action does this today: every floor removal goes through the Floor
    tab or its pop-up.
  - **The keychain.** Unequipped and placed on the floor, it got no tab.
  - **1B, new game.** The tabs were Floor and Stove. Device Options showed on
    the Stove tab, and with a box of matches the stove lit. The search logged
    "You find: tool cabinet, desk, closet.", and the tabs became Floor, Stove,
    Tool Cabinet, Desk and Closet. With the non-device containers removed by
    the hook, the search logged "You find nothing else." as `good`.
  - **Saves.** A save written by v0.7.2 held a registry purse and an
    unequipped duffel with two Dish soap in its `contents`, both on the floor.
    It loaded in v0.7.3 with no version warning. Both bags got tabs, and the
    duffel's tab listed the soap at `0.80 / 18 kg`.

**Sections touched**

- INVENTORY / ITEM SYSTEM: the new `floorBags()` and `floorBagTab()`, and
  `worldSlot()`.
- CORE UTILITIES: `findItemByUid()`. The handoff files it under INVENTORY /
  ITEM SYSTEM, but it lives in CORE UTILITIES and was edited in place.
- WORLD INTERACTION: the new `shownWithoutSearch()`, and `doSearch()`.
- RENDERING: `renderWorldItemsPanel()`.
- PERSISTENCE: comments only.

No WORLD DATA, no SIMULATION, no CRAFTING.

**Open questions / decisions resolved**

- **The tab key's prefix: `"bag:" + _uid`,** the handoff's recommendation.
  Container ids are authored words and uids are `"u" + n`, so the key cannot
  be taken for either. It is written once, in `floorBagTab()`, and
  `worldSlot()` matches by comparing against that, not by parsing the key.
- **Where the floor-bag list is computed: one helper, `floorBags(room)`,** the
  handoff's recommendation. The tab list, `worldSlot()` and `findItemByUid()`
  all call it, so the rule is written once.
- **Where `contents = []` is created: in `worldSlot()`, on resolve.** A
  registry bag gets an empty `contents` the first time its tab resolves. From
  then on, the tab, the transfers and the save all see one real array. The
  alternative was to create it in `doStore()` on first store, with
  `worldSlot()` returning a detached empty array before that. That would put
  the same fact in two functions.
- **`shownWithoutSearch()` is a helper, not two `hasTag(c, "device")` calls.**
  The tab list and `doSearch()` must agree on what a search does not hide. A
  later "visible without search" tag (#15) then changes one line.

**Notes / assumptions**

- **"You find nothing else."** is the handoff's wording, and retunable.
- **`floorBagTab()` mints a `_uid` for each floor bag in the current room when
  the Here panel draws.** `renderItemList()` avoids minting uids for every
  row, so that saves don't fill with them. A floor bag needs one for its tab
  key, as the handoff specifies. Only bags on the current room's floor get one.
- **The first `contents = []` is written during a render**, because
  `renderWorldItemsPanel()` resolves the open tab through `worldSlot()`. It
  adds no weight, touches no roll, and is the field the bag would carry had it
  ever been equipped.
- **Storing into a floor bag ignores `floorCap`,** per the handoff: the check
  is against the bag's `capacityKg` only. The bag's contents still count in
  `totalWeight(room.floor)` through `itemUnitWeight()`, as they already did
  for a bag placed full. So the Floor header rises as the bag fills, and a
  later Place onto that floor counts them. Filling a floor bag can take a
  floor past its `floorCap`, as `giveItem()` already can.

**Explicitly out of scope**

- #167 (Disassemble).
- Carry load (#168, #170), in `handoffs/carry-load.md`, which is implemented
  after this. Its Take and Equip checks reach floor-bag tabs through
  `worldSlot()`.
- Opening a bag that sits in a room container, a car container or another bag.
- A "visible without search" container tag (#15). The rule keys off `device`.
- Reachable crafting (#119) and container `kind` (#128).
- #201 (the pop-up after a keyboard tab switch).

**Version**: `GAME_CONFIG.VERSION` `"0.7.2"` → `"0.7.3"`

---

## v0.7.2 — Tier-0 sweep

Implements: handoffs/tier-0-sweep.md

Implements #173, #176, #180, #181, #183, #184, #193 and #195 in full, per
`handoffs/tier-0-sweep.md`. These are eight independent small fixes: the open
`tier-0` backlog minus #167. Only #180 and #195 are coupled. #180 removes the
walkie-talkie's `battery` tag, and #195's load-time tag resync is what takes
that removal into saves that already hold one. Nothing is added to `state`, and
`SAVE_KEY` stays `ashfall_save_v0.7`. **PATCH**, so existing browser saves keep
loading.

**Fixed**

- **The walkie-talkie was a battery (#180).** `walkie_talkie`'s `ITEM_REGISTRY`
  entry carried `tags:["battery"]`, so `countByTag("battery")` counted it, and
  "Replace batteries" on a flashlight or radio could spend a whole
  walkie-talkie through `consumeByTag("battery", 1)`. The entry no longer has a
  `tags` field and gets nothing in its place. This is the pass's only WORLD DATA
  change. It corrects a definition and places no instance.
- **A registry tag fix never reached a save (#195).** `itemFromRegistry()`
  deep-copies `tags` onto every instance, so a save keeps whatever tags its items
  were created with. The new `backfillRegistryTags()` (PERSISTENCE) resyncs
  them on load. It covers every item `forEachItemList()` reaches, and each
  `CONTAINER_SLOTS` slot object on `state`. An item whose `itemId` is an own key
  of `ITEM_REGISTRY` takes a fresh copy of the entry's `tags`, or loses the
  field when the entry has none. An item with no `itemId`, or one the registry
  does not know, is left untouched. `applyLoadedData()` calls it straight after
  `backfillItemIds()` and `backfillSlotItemIds()`, whose `itemId` it keys off.
  It runs on load only.
- **Devices stopped draining once put down (#181).** `applyWorldTicking()`
  drained only `invPools()`. That skipped a bag's `contents`, and every floor
  and container in the world. A radio left on in a room froze at its charge
  until picked up again. The drain now runs over every list
  `forEachItemList()` reaches. The formula and the switch-off are unchanged. The
  log line depends on where the device is:
  - carried, including inside a carried bag at any depth: "Your … runs out of
    battery and shuts off." (unchanged);
  - anywhere in the current room, including nested `contents`: "The … runs out
    of battery and shuts off.";
  - anywhere else: no line. It shuts off silently, as a fire elsewhere already
    goes out.
- **Crafting opened onto an empty catalogue after death (#183).** The Crafting
  hub button is now `disabled` while `gameOver` is true, and enabled otherwise.
  It has no hint line, because "You did not survive." already says why. The
  existing `#hubRow button:disabled` style is the whole visual. `render()` sets
  the state before it branches, so it runs on every render. Restart, Replay
  this seed and loading a save after death all re-enable it. The game-over
  branch still blanks `#craftingList`. `doCraft()` has no `gameOver` guard, so
  a live recipe button must never survive into the game-over screen.

**New**

- **Replay this seed (#176).** The game-over screen has a second button after
  Restart: `actionButton("Replay this seed", ()=> doRestart(state.seed))`. It
  starts a fresh run on the dead run's seed. Restart is unchanged and still
  starts a new world.
- **`forEachItemList()` says where each list is.** `visit` is now called as
  `visit(list, roomId)`, where `roomId` is the id of the room the list is in, or
  `null` when it is carried. A bag's `contents` inherits its bag's answer.
  Existing callers ignore the argument and behave as before. This is how the
  #181 tick picks its log line.

**UI**

- **Here group notes (#193).** `hereNote()` is now `font-size:12px;
  padding:5px 0`, down from 12.5px and `6px 0`. That puts it in line with
  v0.7.1's 12px play screen. The colour is unchanged. The same helper draws
  the Device Options panel's "Nothing you're carrying will light it.", which
  changes with it.
- **Game over:** two buttons, Restart then Replay this seed. In the drawer,
  Crafting is greyed out and does nothing.
- **Log:** a device switched on in the current room says "The … runs out of
  battery and shuts off." when it dies.
- **Batteries:** "Replace batteries" is no longer offered on the strength of a
  walkie-talkie. In an old save this takes effect when the save is loaded.

**Removed**

- The `.menu-placeholder` CSS rule (#184). No markup or script used the class.
  Nothing replaces it.

**Documentation**

- ITEM DATA SCHEMA: an item's `tags` are definition data. `overrides` never
  sets them, and the load path resyncs them from the registry.
- The paragraph above `validateReachability()` (#173) no longer carries a
  count, a version or an issue number. It says dead pools and unreachable items
  are expected until the spawn balance is done, and names
  `ashfallDev.validateReachability()` as the live figure, with
  `ashfallDev.sampleSeeds()` beside it.
- `hereNote()`'s comment no longer counts its call sites. It said five and
  there are four. It now also names the stove note among its uses.
- `render()`'s blanking comment no longer cites #183. It now says why the
  blanking stays.
- New comments on `applyWorldTicking()`, `backfillRegistryTags()`, the
  `forEachItemList()` second argument, and the hub-button lookup.
- Filed #197. `validateLoadedWorld()`'s comment still says "the three
  backfills". There are now seven, plus `resyncUidCounter()`. The backfills'
  own "third / fourth / sixth companion" ordinals also disagree. Found here and
  outside this handoff's scope. Nothing was deferred.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` touches only the sections
  listed below.
- Exercised in headless Chromium, with v0.7.1 (`origin/main`'s
  `ashfall.html`) run alongside as the baseline:
  - **`validateReachability()`** returns a report identical to v0.7.1's: 10
    dead pools, 11 unreachable items, the same tool-tag lines.
    `validateItemRegistry()`, `validateLocations()` and `validateRoomSchema()`
    are clean. No page errors.
  - **#195 and #180 on an old save.** The test save was a v0.7.1 save with no
    spare batteries, carrying a walkie-talkie tagged `battery` and a portable
    radio. In v0.7.1, the radio's Device Options offered "Replace batteries".
    Loaded in v0.7.2, they offered Turn on and Remove batteries only.
    Every walkie-talkie lost its `tags` field: the carried one, one two bags
    deep in `contents`, and one on another room's floor. An equipped slot object
    lost a stray `tags` field. A frying pan saved without tags got `["blunt"]`
    back. An item with no `itemId`, and one with an unknown `itemId`, kept their
    tags. The keychain was untouched.
  - **#181.** One Rest, with four devices on at 0.5% charge. A flashlight stowed
    in a carried bag logged "Your flashlight…". A radio on the current floor
    logged "The portable radio…". A flashlight in a bag inside a current-room
    container logged "The flashlight…". A radio on another room's floor went to
    0 and shut off with no line. A full radio in another room's container
    drained by exactly `60 × drainRate`, once, not twice. A switched-off
    flashlight did not drain.
  - **#183 and #176.** Alive, Crafting is enabled. After death, the buttons
    read Restart then Replay this seed. Crafting is disabled with the label
    "Crafting" only, Options is still enabled, and the catalogue is blank.
    Replay this seed kept the seed shown in Options and started at minute 0
    with full health, and Crafting was enabled again. A load after death
    re-enabled Crafting. Restart gave a new seed and re-enabled it.
  - **#193.** The sleep-cooldown note computes to 12px with `5px 0px` padding.
    The stylesheet has no `.menu-placeholder` rule.

**Sections touched**

- RENDERING: `hereNote()`, `render()` (the Crafting button state and the
  game-over branch), and `<style>`.
- EVENTS / UI HELPERS: the hub-row build, which now keeps `hubButtonFor`.
- SURVIVAL / TIME SIMULATION: `applyWorldTicking()`.
- WORLD DATA: `walkie_talkie`'s registry entry, and the ITEM DATA SCHEMA
  comment.
- PERSISTENCE: `forEachItemList()`, the new `backfillRegistryTags()`,
  `applyLoadedData()`, and the comment above `validateReachability()`.

**Open questions / decisions resolved**

- **How the tick knows where a device is (#181): option (b).**
  `forEachItemList()` got an optional second argument. Walking the three scopes
  by hand inside `applyWorldTicking()` would have been a second item walker,
  which the walker's own comment names as how a bag's `contents` gets missed.
  Each list is still visited exactly once. The drain-once check above confirms
  it.
- **How `render()` reaches the Crafting button (#183): a kept reference.**
  `hubButtonFor` maps each enabled hub button by the `FULL_PANELS` id it opens.
  It is filled when the row is built, and read as `hubButtonFor.crafting`. It
  is keyed by `opens`, never by label.
- **`hereNote()` (#193): the inline style stays.** It is a two-value edit.
  Moving it to a class is left to #165's text-size option, which would need one.
- **`backfillRegistryTags()` tests `hasOwnProperty`.** A truthy lookup would
  count an `itemId` of `"constructor"` as a registry key. The handoff says "a
  key of `ITEM_REGISTRY`", and own keys are what that means.

**Notes / assumptions**

- **The tick now walks the whole world every game minute.** A ~570-minute
  Sleep measured about 13 ms in v0.7.1 and about 35 ms in v0.7.2 on a fresh
  world. The cost scales with how many items the world holds. It is well under
  a frame, and was accepted rather than optimised.
- **A device that dies during a move counts the room being left as the current
  room.** A move's minutes tick before `state.currentRoom` changes. The fire's
  "burns down and goes out" line already works the same way.
- **The new log line's wording** is the handoff's.

**Explicitly out of scope**

- #167 (tag-driven Disassemble). #195 removes its save seam, but it is not
  implemented here. `campfire_kit` gets no tag.
- The walkie-talkie as a working device (a `device` tag, battery controls). A
  salvage action to take its batteries.
- A `gameOver` guard in `doCraft()`.
- Resyncing container tags. Containers are world instance data, not registry
  entries.
- A log line, or any notice, for a device outside the current room.
- Showing the seed on the game-over screen. It stays in Options.

**Version**: `GAME_CONFIG.VERSION` `"0.7.1"` → `"0.7.2"`

---

## v0.7.1 — Compact sizes and side-by-side panels

Implements: handoffs/compact-sizes-and-side-by-side-panels.md

Implements #190, #191 and #186 in full, per
`handoffs/compact-sizes-and-side-by-side-panels.md`. The play screen changes in
three ways. Controls are about 10% smaller than v0.7.0, with a 24px floor. Play
screen text is 12px. The Here and Inventory panels are two side-by-side columns
in both orientations. Presentation only: no game rule changes, nothing is added
to `state`, and `SAVE_KEY` stays `ashfall_save_v0.7`. **PATCH**, so existing
browser saves keep loading.

**UI**

- **Sizes.** `<style>` only. Every value is from the handoff's §1 table:
  - Title (`header h1`) 15 → 13px.
  - `#menuToggle` 13 → 12px, padding `7px 11px` → `6px 10px`.
  - `#hubRow button` 13 → 12px, padding `8px 6px` → `7px 6px`.
  - `.menu-actions button` 13 → 12px, padding `8px 10px` → `7px 9px`.
  - `#locLabel` 14 → 12px. `#roomDesc` 15 → 12px. `#log p` and
    `.log-result p` 13.5 → 12px. `.detailBox` and `ul.itemlist li` 12.5 → 12px.
  - `#gaitBar span`, `.actions-group h2` and `.panel h2` 12 → 11px.
  - `button.action` 12.5 → 12px, padding `6px 10px` → `5px 9px`.
  - `#gaitBar button` and `.tabs button` padding `5px 9px` → `4px 8px`.
  - `min-height:24px` on `button.action`, `#gaitBar button`, `.tabs button` and
    `button.mini`.
  - Line-heights and the serif face of the room text and log are unchanged.
- **Resulting heights** at 412px with Roboto: menu 31 → 28, actions 29 → 26,
  pace 26 → 24, tabs 26 → 24, item buttons 24 → 24.
- **Item names lose the dotted underline.** #108 added it as the hint that a
  name can be tapped. Removing it is Tom's decision, made in #190. The bold
  weight is now the only hint.
- **Two panel columns in both orientations (#191).**
  - `#sidebar` is a two-column grid (`minmax(0,1fr) minmax(0,1fr)`, 8px gap,
    `10px 8px` padding).
  - `.panel` is a flex column with `10px 9px` padding and `min-width:0`.
  - `.panel h2` wraps (`gap:2px 6px`), so in a narrow column the weight and the
    Unequip or Device Options button drop under the heading.
  - Item rows are unchanged: the button stays beside the text, which wraps.
- **Tabs are one row that scrolls sideways.** `.tabs` no longer wraps. It
  scrolls on `overflow-x`, with its scrollbar hidden and a fade at the right
  edge (`mask-image`, `#000 80%` → transparent). The fade is always on. It is
  the only sign that more tabs are off to the right.
- **The selected tab is always fully visible.** After every render, each strip
  scrolls its selected tab into view.
- **Portrait: Fill (#186).** `main` gets `grid-template-rows:auto 1fr`. `#left`
  takes only the height it needs, and the panels start directly under the
  actions and stretch to the bottom of the screen. A long list grows the page,
  and the page scrolls. The portrait order rules stay, so the row reads
  Here | Inventory.
- **Landscape: 50 / 25 / 25.** `main` is `minmax(0,1fr) minmax(0,1fr)` in place
  of `1fr 320px`. The text column ends at the middle of the screen, and the two
  panels share the right half: text | Inventory | Here.

**Fixed**

- **A tab strip kept a stale scroll offset across rooms.** Found in the mock-up
  and fixed here, before it could ship. Each render rebuilds a strip's buttons
  inside the same element. The browser keeps the old `scrollLeft`, clamped to
  the new, shorter row. In 2A's kitchen, scroll the Here strip to Pantry, tap
  it, then go to the living room: Floor is selected but starts 20px off the
  strip's left edge (11px in landscape). The fix is the new `revealActiveTab()`,
  below.

**New**

- **`revealActiveTab(strip)`** (RENDERING) scrolls a strip by the least distance
  that puts its `.active` tab fully in view. A tab already in view leaves the
  strip where it is. It sets the strip's `scrollLeft` only, so the page never
  moves. `renderInventoryPanel()` and `renderWorldItemsPanel()` both call it
  once their tabs are built.

**Documentation**

- The portrait query's comment is rewritten. The `max-width:480px` clause stays;
  its reason is now that three columns get too narrow below it, where it was
  the 320px sidebar's 476px floor. The comment says Here sits beside Inventory,
  and that the `auto 1fr` rows are what keep the panels under the actions
  (#186).
- New comments on the landscape columns (`main`), the panels' load-bearing
  `min-width:0`, the tab strip and its fade, and `revealActiveTab()`.
- Filed #193. `hereNote()` sets the Here group's notes inline at 12.5px. #190
  and the handoff's §1 table both miss it, so it stays at 12.5px here. Nothing
  else was deferred.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` shows the changes above and
  nothing else.
- Exercised in headless Chromium at 412×800 and 860×320, with Roboto and Noto
  Serif substituted for `system-ui` and Georgia, to match Tom's phone:
  - **Heights.** v0.7.0 measured 31 / 29 / 26 / 26 / 24, matching the handoff.
    v0.7.1 measures 28 / 26 / 24 / 24 / 24, matching §1's second table.
  - **The tab case (§3).** With `revealActiveTab()` disabled, the bug
    reproduced: Floor 20px off in portrait, 11px in landscape. With it, Floor
    is at 0 in both. Tapping a tab that was already in view (Fridge, with the
    strip scrolled to Pantry) did not move the strip. The page's `scrollY`
    stayed 0 throughout.
  - **Portrait.** The panels start 10px under `#left` (the sidebar's padding)
    and reach the bottom of the screen. With a long floor list in the living
    room (a scratch copy), the page grew to 1480px and scrolled. The sidebar
    did not scroll inside itself.
  - **Landscape.** `#left` is 430px of 860. Inventory is at x=438 and Here at
    x=649, both 203px wide.
  - **Header wrap.** On the kitchen's Stove tab, the Here header's Device
    Options button drops under the heading and stays inside the panel.
  - No horizontal page scroll at either size, and no page errors.
    `validateItemRegistry()`, `validateLocations()` and `validateRoomSchema()`
    are clean. `validateReachability()` returns the same report as v0.7.0.

**Open questions / decisions resolved**

- **Keeping the selected tab visible.** A shared helper, `revealActiveTab()`,
  called by both panel renderers. It lives in RENDERING beside them, not in
  EVENTS / UI HELPERS, because only renderers call it and it reads nothing but
  the DOM they just built. It computes the tab's position within the strip and
  sets `scrollLeft`. It does not use `scrollIntoView()`, which can scroll the
  page vertically. `Math.floor` and `Math.ceil` round the target so a
  fractional tab edge never leaves a sub-pixel sliver out of view.
- **Where the grid rules live.** In the base rules, which apply in both
  orientations: the `#sidebar` grid, the `.panel` flex column and the tab strip.
  The portrait query overrides only `main`'s tracks, as before, plus `#left` and
  the order rules.

**Notes / assumptions**

- **Retunable judgment calls, all approved by Tom in the layout lab:**
  - every size in the §1 table;
  - the 24px floor;
  - the fade's 80% stop;
  - the sidebar's 8px gaps and the `10px 8px` / `10px 9px` paddings;
  - the 50 / 50 landscape split of `main`.
- **The selected tab can sit under the fade.** "Fully visible" means inside the
  strip's scrollport. With the fade always on, a selected last tab, scrolled to
  the end, still shows its right edge faded. That is the approved look, not a
  miss by `revealActiveTab()`.
- **A stale `worldTab` gets no reveal.** `renderWorldItemsPanel()` marks the
  active tab before it falls back to Floor for a `worldTab` that no longer
  exists, so on that render no tab is `.active`. `revealActiveTab()` then does
  nothing. That behaviour is v0.7.0's; movement already resets `worldTab` to
  `"floor"` before rendering.
- **`button.action` changes everywhere it is used:** the play screen's Move and
  Here groups, the item pop-up, the Crafting list and the Device Options panel.
  #190 names the pop-up's and the recipes' buttons as part of the cut.

**Explicitly out of scope**

- Other text in the drawer and the full-screen panels keeps its v0.7.0 size:
  `#statsBox`, `#seedRow`, `#deviceStatus`, `.menu-section h3`,
  `.menu-placeholder`, the `#sideMenu` and `.full-panel` headings,
  `#hubRow .hint`, the map's text and buttons, `#closeMenu` and `.panel-close`.
- Rejected in planning: a half-screen dock, a 40 / 30 / 30 split, a 1280px cap,
  wrapping tabs, and a dropdown in place of tabs.
- #165 (adjustable layout in Options). This pass's values become its defaults.
- #29 (the log's `max-height` and 50-entry cap). #169 (a bag as a Here tab).
- `positionItemPop()`: the pop-up's width and position are unchanged.
- #78, accessibility.

**Sections touched**

- `<style>`
- RENDERING (`revealActiveTab()`, `renderInventoryPanel()`,
  `renderWorldItemsPanel()`)

**Version**: `GAME_CONFIG.VERSION` `"0.7.0"` → `"0.7.1"`

---

## v0.7.0 — Device Options: a `device` tag, container tags, and the stove's controls in their own panel

Implements: handoffs/device-options.md

Implements #161 and #177 in full, per `handoffs/device-options.md`. This is
layer 3 of the three-layer item model. A new `device` tag marks things whose
controls go beyond take and store. The portable radio and the four stoves carry
it, and their controls move into a full-screen Device Options panel. Containers
gain `tags`, with the same field, shape and vocabulary as items. Heat containers
are now found by a `heat` tag instead of by id, which fixes #177 at the root.
`room.hasStove` is removed. This is **MINOR**: the new tags live on registry
items and authored containers, and a save carries deep copies of both, so
`SAVE_KEY` rotates from `ashfall_save_v0.6` to `ashfall_save_v0.7`.
**Existing browser saves stop auto-loading.**

**New**

- **`hasTag(thing, tag)`** (INVENTORY / ITEM SYSTEM) answers "does this item or
  container carry this tag?". `hasTool()`, `countByTag()`, `consumeByTag()`,
  `findFireStarter()` and `registryCarriesTag()` now call it. Their behaviour is
  unchanged, and no `tags.includes` remains outside it.
- **The `device` tag** means the thing has controls beyond take and store, kept
  in Device Options. For an item tagged `device`, `getItemActions()` offers one
  action, **"Device Options"**, in place of the battery controls. An item that
  runs on batteries but isn't tagged (the flashlight) keeps its controls in the
  pop-up, as before.
- **`batteryActions(it)`** is the one definition of Turn on/off, Remove
  batteries and Replace batteries. The pop-up (flashlight) and the device panel
  (radio) both call it. It returns nothing unless the item's durability mode is
  `"time"`. The availability rules and the controls' silence are unchanged.
- **Container tags** read by a mechanic:
  - `heat`: a heat source's cooking space. Stoves and campfires.
  - `device`: the container has Device Options. Stoves only.
- **`getHeatContainer(room)`** returns the room's first container tagged
  `heat`. **`roomStove(room)`** returns its container tagged both `device` and
  `heat`, or null. Every stove question now asks `roomStove()`.
- **`doLightStove()`** returns without effect if `roomStove()` finds nothing.
  Otherwise it spends a fire-starter use, sets `heatActive`, spends
  `LIGHT_STOVE_MIN` and logs "You light the stove.", as before. It no longer
  calls `ensureHeatContainer()` and never creates a container.
- **`ensureHeatContainer()`** takes a fifth parameter, `tags`, set on the
  container when it creates one. An existing container is returned unchanged.
  `doBuildFire()` passes `["heat"]`, and is now the only caller.

**New content**

- `portable_radio` gains `tags:["device"]`. No other item changes.
- The four authored stove containers gain `tags:["device","heat"]`: `kitchen`,
  `twobee_kitchen` and `onebee` at `id:"stove"`, and `onea_kitchen` at
  `id:"stove1a"`. `stove1a` is not renamed, because the tag makes it work.

**Fixed**

- **#177, 1A's kitchen.** The root cause was that heat containers were found by
  id. `doLightStove()` called `ensureHeatContainer(room, "stove", …)`, which
  found no `"stove"` beside 1A's `stove1a` and created a second, empty "Stove"
  tab. `getHeatContainer()`, looking for `"stove"` or `"campfire"`, then saw
  only that empty tab, so Cook never saw the real one. Both now read tags. 1A
  keeps one Stove tab after lighting, and Cook finds `stove1a`.

**Removed**

- `hasStove` is removed from the four rooms and the ROOM SCHEMA comment. Its
  readers in `renderHereActionsPanel()` now ask `roomStove()`.
- The Here group loses "Light the stove", its note "Nothing you're carrying
  will light it." and "Turn off the stove". All three are now in the stove's
  Device Options. "Put out the fire" now shows while `heatActive` and
  `roomStove()` finds nothing: the campfire. "Add fuel to the fire", "Cook the
  …" and every campfire control are unchanged.

**UI**

- **The Device Options panel** (`#devicePanel`) is a full-screen `.full-panel`
  over the drawer. Opening it opens the drawer, if that is not already open, and
  stacks above it. Closing it by ✕ or Esc closes the drawer it opened in the
  same step. You land back on the item's pop-up (for the radio) or on play (for
  the stove). Focus returns to the Device Options control that opened it. Game
  over, Load and Restart close it with every other layer. It closes by itself if
  its target no longer resolves.
- **Radio.** The panel shows the item's name, the pop-up's status line (`No
  batteries installed` or `N% charge — On/Off`) and `batteryActions()`. The
  radio's pop-up keeps its status line and shows "Device Options" in place of
  its three controls.
- **Stove.**
  - The panel shows the container's name ("Stove") and the status `On` or `Off`,
    from `room.heatActive`.
  - Its one control: "Light the stove (0:05)" when you have a fire-starter, the
    note "Nothing you're carrying will light it." when you don't, or "Turn off
    the stove" while lit.
  - You reach it from a **"Device Options"** `button.mini` in the Here panel's
    header, beside the weight. The button shows only while the selected Here tab
    is a container tagged `device`. It follows the Inventory header's
    `#unequipBtn` pattern.
- **The panel stays open after a control runs.** Its result area, `#deviceResult`,
  shows what that control wrote to `#log`, through the same mechanism as
  Crafting's (see Organization / Structural). The radio's controls write nothing,
  so after one the area is empty and the status line carries the change.
- **1B's stove sits behind the unit's search.** `onebee` has
  `searchLabel:"Search the unit"`, and until it is searched the Here panel lists
  no containers. Its Stove tab, and so its Device Options, appear only after the
  search. Before this pass "Light the stove" sat in the Here group and ignored
  the search. See Open questions.

**Organization / Structural**

- `craftFromPanel()`'s read of `#log` is now `logWrittenBy(action)`, and
  `renderCraftResult()`'s drawing is now `renderLogResult(box, entries)`.
  Crafting and Device Options both use them, so there is one capture mechanism.
  Crafting's behaviour is unchanged.
- The result-area CSS moved from `#craftResult` to a shared `.log-result`
  class, carried by `#craftResult` and `#deviceResult`.
- `renderItemPop()`'s durability ternary is now `durabilityText(it)`. The device
  panel's status line uses the same function.
- `restoreFocus()` takes an optional `back.find()`, tried after `el` and `uid`.
  It finds the pop-up's "Device Options" button again after a render rebuilt it
  while the device panel covered it.
- New UI-only variables, never saved: `deviceTarget` (`{ kind:"item", uid }` or
  `{ kind:"container", id }`, beside `detailItem`) and `deviceResult` (beside
  `craftResult`). `applyLoadedData()` and `doRestart()` clear `deviceTarget`
  where they clear `detailItem`.

**Documentation**

- CONTAINER SCHEMA documents `tags`, with `heat` and `device` and what reads
  each. The ITEM DATA SCHEMA tag list adds `device`. The ROOM SCHEMA drops
  `hasStove`. The layer-stack comment names the device panel, and
  `renderHereActionsPanel()`'s fire-note comment now describes `roomStove()`
  instead of the removed field. New comments on `ensureHeatContainer()`,
  `doLightStove()`, `getHeatContainer()`, `roomStove()` and the campfire's
  id lookup in `doDismantleCampfire()`.
- Filed #188: 1B's stove can't be lit until "Search the unit", though the
  description shows it. Nothing else was deferred.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` shows the changes above and
  nothing else. `hasStove` appears nowhere in the file.
- Exercised in headless Chromium against saves built from the running game:
  - **1A (#177).** One Stove tab before and after lighting. A raw fish placed in
    `stove1a` offered "Cook the raw fish" and cooked there.
  - **The header button.** Shown only on the Stove tab, hidden on Floor and on
    Kitchen Shelf.
  - **The stove's panel.** Off → Light → On, with "You light the stove." in the
    result area. Turn off replaced it with "You put it out.". The Here group
    offered no stove control and no "Put out the fire" while the stove was lit.
  - **Closing.** Esc, and separately ✕, closed the panel and the drawer, cleared
    the result area and returned focus to the header button.
  - **The radio's panel.** Turn on, Remove batteries and Replace batteries each
    updated the status line and left the result area empty. The pop-up stayed
    open beneath and followed. Esc returned to the pop-up with focus on its
    "Device Options".
  - **The flashlight.** Its pop-up still offers Turn on and Remove batteries,
    and no Device Options.
  - **No fire-starter.** The stove's note showed.
  - **Campfire.** It still offers "Put out the fire", its container is saved
    with `tags:["heat"]`, and its tab shows no Device Options.
  - **Closing paths.** A Load reached while the panel was open closed the panel
    and the drawer. So did a fatal Light at 0 hunger and thirst (game over), and
    the header button was hidden.
  - **1B.** Floor only before the search; the Stove tab and its button after.
  - **Phone width.** At 390×844 the Here header fits with no horizontal scroll.
  - No page errors. `validateItemRegistry()`, `validateLocations()` and
    `validateRoomSchema()` are clean, and `validateReachability()` reports no
    authoring problems.
- **Re-verified before implementing, against v0.6.5. All held:**
  - The hub pass had shipped. Its pop-up renders `getItemActions()` and stays
    open beneath the drawer.
  - The layer stack exists (Esc closes the top layer; focus moves in on open
    and back on close).
  - Crafting's result area captures by reading `#log` around the action.
  - The battery block was one block, gated on `durability.mode === "time"`.
  - No container carried `tags`.
  - `hasStove` appeared only in the schema comment, the four rooms and the
    here-actions code.
  - The five fire functions matched the handoff's description.
  - Every stove room carried `cannotHaveFire` and one authored container named
    "Stove".
  - Cook was still a Here-group button, since #178 has not shipped.
  - `#unequipBtn` was still the context-button pattern.
  - `SAVE_KEY` had not rotated since v0.6.3 (v0.6.4 and v0.6.5 were PATCH), so
    this pass's rotation is the first since then.
- One statement outside that checklist did not hold: the handoff says none of
  the four stove rooms has a `searchLabel`, but `onebee` does. Tom was asked
  before any code was written; see below.

**Open questions / decisions resolved**

- **1B's search (asked during implementation).** With the stove's controls moved
  out of the Here group, 1B's stove can't be lit until the unit is searched.
  Tom chose to ship that as specced and track it in #188.
- **Implementation choices the handoff left open:**
  - The tag helper is `hasTag(thing, tag)`. The existing tag readers were
    rewritten to call it.
  - The stove helper is `roomStove(room)`.
  - The device target is `{ kind:"item", uid } | { kind:"container", id }`,
    resolved again on every render by `resolveDeviceTarget()`. A container
    target must be in the current room and both kinds must still carry `device`.
  - `ensureHeatContainer()` takes tags as a fifth parameter.
  - The device panel has its own element, `#devicePanel`, and is not a
    `FULL_PANELS` entry. It opens from the play area and has to open and close
    the drawer with itself, which `openPanel()` doesn't do. It shares the
    `.full-panel` class and the `.panel-close` wiring.
- **The panel closes only the drawer it opened.** If the drawer was already
  open, which only keyboard Tab can arrange, closing the panel leaves it open.
  That is the handoff's "back to where it was opened from", applied to that case.
- **The stove's content is gated on `heat`.** A fixture tagged `device` without
  `heat` would draw only its name, never the stove's controls. None exists
  today.

**Notes / assumptions**

- Retunable functional text: "Device Options" (one constant,
  `DEVICE_OPTIONS_LABEL`, which also labels the header button) and the stove's
  status "On" / "Off".
- **Imported pre-0.7 saves** load with the existing version warning and no
  container tags. No load-time backfill runs (Tom, #161 option (b)). In such a
  save:
  - stoves have no Device Options and can't be lit;
  - a lit stove shows "Put out the fire" in the Here group;
  - a campfire container built before the import has no `heat` tag, so Cook
    doesn't find it, even after a relight, since `ensureHeatContainer()`
    returns the existing container unchanged.

**Explicitly out of scope**

- #178 (passive cooking) and #179 (burning, unattended fires). Cook is not
  touched.
- #180 (the walkie-talkie's `battery` tag) and #181 (devices draining outside
  the inventory). `applyWorldTicking()` is unchanged.
- New devices (a TV, a car radio, a walkie-talkie as a device). Those are
  content.
- #15's `movable` / `disassemblable` flags, #128's container `kind`, #96's
  `roomHasHeat()`, and the campfire as a device.
- A load-time backfill of tags into old saves.
- #78, accessibility.

**Sections touched**

- ITEM DATA / WORLD DATA (definition data and schema comments)
- INVENTORY / ITEM SYSTEM (`hasTag()`, `getItemActions()`, `batteryActions()`)
- FIRE / COOKING
- PERSISTENCE (clearing `deviceTarget` on load and restart; the dev seam's
  `registryCarriesTag()`)
- EVENTS / UI HELPERS (`openDevicePanel()`, `restoreFocus()`)
- RENDERING (the device panel, the Here header button, the Here group, the
  shared result area)
- `<style>` and the markup

**Version**: `GAME_CONFIG.VERSION` `"0.6.5"` → `"0.7.0"`

---

## v0.6.5 — Portrait layout, compact action buttons, tighter line spacing

Implements: handoffs/portrait-layout.md

Implements #159 in full, per `handoffs/portrait-layout.md`. The layout now
switches on orientation instead of width. Portrait gets one column with the Here
panel above Inventory. Action buttons are smaller and the room text is set
tighter in both layouts. The pass changes the `<style>` block and adds two ids
to the sidebar's panels. No script logic changed and `state` did not change, so
`SAVE_KEY` stays the same and this is PATCH.

**UI**

- **What switches the layout.** `@media (orientation: portrait), (max-width: 480px)`
  replaces `@media (max-width:760px)`. A portrait viewport of any width gets
  the one-column layout, and so does any viewport narrower than 480px. A
  landscape viewport 480px or wider keeps today's two columns. The 480px clause
  is a floor, not the trigger. The two-column grid needs 476px (the 320px
  sidebar plus the description's minimum). Without the floor, a landscape
  window narrower than that would scroll sideways.
- **Tall desktop windows get one column too.** A desktop window taller than it
  is wide takes the one-column layout, by design (#159).
- **One-column layout.** Everything in it sits under that one query, so there is
  one alternative layout, not two. From the top: the header and `#locBar`
  (unchanged), then `#left` (room description, log, Move group, Here actions),
  then the **Here** panel, then **Inventory**, then any other sidebar panel in
  its existing DOM order. `#left`'s padding drops from `18px 26px` to
  `14px 16px`. Its border still moves from right to bottom. The two-column
  layout keeps Inventory above Here.
- **Everywhere (both layouts):**

  | rule | was | now |
  |---|---|---|
  | `button.action` font-size | `13.5px` | `12.5px` |
  | `button.action` padding | `8px 13px` | `6px 10px` |
  | `.actions` gap | `8px` | `6px` |
  | `button.action .cost` font-size | `12px` | `11px` |
  | `button.action .cost` margin-left | `4px` | `3px` |
  | `#roomDesc` line-height | `1.6` | `1.4` |
  | `#log p` line-height (and `#craftResult p`, which shares the rule) | `1.5` | `1.35` |

  An action button is now 29px tall, down from 34px.
- **Known tradeoff: tap targets.** 29px (and the old 34px) is below the usual
  44px (iOS) and 48px (Android) minimums. Tom chose the compact size knowing
  this. Tap-target minimums generally stay with #78.

**Documentation**

- Rewrote the layout comment above the media query. It now gives the
  orientation trigger, the 480px floor and the 476px grid floor behind it, that
  tall desktop windows take one column by design, and that the numbers are
  retunable. It keeps the note about `#left`'s border moving from right to
  bottom, and drops every sentence about the 760px rule.
- Filed #186. In the one-column layout, a room with little content leaves a gap
  between the Here actions and the panels. `main`'s grid rows stretch to fill
  the viewport. This predates this pass (the 760px rule did the same), but
  portrait now shows it more often. Whether the panels should sit directly under
  the actions is Tom's call. Nothing else was deferred.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` contains only the `<style>`
  block, the `id`s on the two sidebar panels, and the `GAME_CONFIG.VERSION` bump.
- Measured in headless Chromium, comparing this branch with `origin/main`:
  - 390×844 (portrait): one column, Here above Inventory, `#left` padding
    `14px 16px`, two action buttons per line.
  - 844×390 (landscape): `524px 320px` columns, Inventory above Here.
  - 900×1100 (tall desktop): one column.
  - 470×400 (landscape below the floor): one column.
  - 1280×800: two columns, as before.
  - No viewport scrolls sideways.
- Checked every `button.action` user at the compact size, in portrait and
  landscape: the Move group on Poplar St, the Here actions, the item pop-up's
  `.pop-actions`, the Crafting panel's recipe buttons (disabled, with
  `(needs …)` costs), and the game-over Restart (reached by loading a save with
  `health: 0`). All render without clipping or overlap, and costs sit inline.
  No page errors.

**Open questions / decisions resolved**

- **How Here gets above Inventory:** CSS `order` inside the query, as the
  handoff recommended. The panels got ids, `#invPanel` and `#worldPanel`, named
  after their `#invList` and `#worldList`. The rule sets `#worldPanel{ order:-2 }`
  and `#invPanel{ order:-1 }`. Any other panel keeps the default `order:0`, so it
  follows the two in DOM order wherever it sits in the markup. The DOM order
  is unchanged, and the two-column layout is untouched. No positional selectors
  were used.

**Notes / assumptions**

- These values are judgment calls and retunable: the 480px floor, the
  `14px 16px` padding, and every value in the "Everywhere" table. They come from
  mock-ups Tom approved at 390×844 and 844×390.

**Explicitly out of scope**

- #29: the log's `max-height:110px` and its 50-entry cap are unchanged.
- #165: adjustable panel sizes. This pass's values become its defaults.
- An Options toggle for the layout.
- #78: tap-target minimums and accessibility generally.

**Sections touched**

- The `<style>` block, and the markup of the two `#sidebar` panels (`id`s only).
  No WORLD DATA, ACTIONS, SIMULATION, PERSISTENCE or RENDERING logic.

**Version**: `GAME_CONFIG.VERSION` `"0.6.4"` → `"0.6.5"`

---

## v0.6.4 — Menu hub: the item pop-up, the drawer hub with Crafting, and Options

Implements: handoffs/menu-hub.md

Implements #157, #158 and #160 in full, per `handoffs/menu-hub.md`. Item
actions move out of the sidebar's Craft panel into a pop-up at the tapped item.
The ☰ drawer becomes a hub whose buttons open full-screen Crafting and Options
panels. The Craft panel and the drawer's Run section leave the page. This is a
rendering pass. Nothing enters `state`, and `RECIPES`, `canCraft()`,
`doCraft()`, `getItemActions()`, `seedFromInput()`, `doRestart()` and `log()`
are unchanged; they are only called from new places. `SAVE_KEY` does not move,
so this is PATCH.

**Changed / Reworked**

*Item detail view (#157)*

- Tapping an item's name still sets `detailItem = { uid, side }`. It now opens
  `#itemPop`, a pop-up anchored to that item's row, instead of repainting the
  Craft panel. `renderItemPop()` replaces `renderCraftPanel()`'s detail branch
  and shows the same lines in the same wording and order. The actions from
  `getItemActions()` follow, one `button.action` per line in a flex column
  (`.pop-actions`), where the old view separated them with `<br>`.
- Whether the pop-up is open follows `detailItem` and nothing else. Movement,
  load, restart and `findItemByUid()` missing (Take All) all clear it and so
  close the pop-up. Closing the pop-up sets `detailItem = null`. It stays open
  after an action and updates in place, and `doOpen()`'s re-pointing keeps it
  on the opened unit.
- Position (`positionItemPop()`): directly below the row, flipped above when
  below would run off the bottom of the viewport. Width is the row's, clamped
  to the viewport minus `POP_MARGIN` (8 px) on each side. If neither side has
  room, it takes the roomier side and scrolls inside. It re-runs on every
  render, on resize, and on scroll (capture phase, so `#sidebar`'s own scroll
  counts). The row is re-found by uid through `itemNameButton()` every time,
  never by index or a kept node.
- An outside tap lands on `#itemPopBackdrop`, a transparent layer at z-index 10
  (pop-up at 11), which closes the pop-up and does nothing else. Both sit below
  `#menuBackdrop`'s 15, so opening the drawer covers the pop-up and does not
  close it.

*Side menu hub (#158)*

- `#hubRow` sits under the `Menu ✕` heading and is built once from
  `HUB_BUTTONS`: Crafting, Health, Clothing, Options. An entry's `opens` names
  the `FULL_PANELS` id it opens. `opens: null` makes it a placeholder, disabled
  and carrying `HUB_PLACEHOLDER_HINT` ("Not yet") on a second line.
- Crafting (`#craftingPanel`) and Options (`#optionsPanel`) are `.full-panel`s:
  fixed, the whole viewport, at z-index 30, over `#sideMenu`'s 20. Each has its
  own heading and ✕. Closing one returns to the drawer.
- The Crafting panel (`renderCraftingPanel()`) is today's catalogue, moved
  as-is with its comment: every recipe in `RECIPES` order, unavailable ones
  disabled with `(needs …)`. `render()` draws it every time, like the sidebar
  panels.
- The result area (`#craftResult`). A recipe click goes through
  `craftFromPanel()`, which snapshots `#log`'s children and the last entry's
  text, calls `doCraft()` unchanged, and then keeps every `<p>` that is new,
  plus the old last one if its text changed. That second case is how a `×2`
  in-place update counts. `craftResult` holds references to `#log`'s own
  `<p>`s, never copies of their text. `renderCraftResult()` clones the ones
  still in `#log` each time it draws, so the area shows #log's current wording
  and styling. It is replaced by the next craft and cleared when the panel
  closes. It writes nothing to `#log`.

*Options (#160)*

- The seed is its canonical number in `#seedValue` (selectable,
  `user-select:all`), with **Copy** beside it and **Restart game** below.
  `renderOptionsPanel()` (was `renderRunPanel()`) writes the seed at the top of
  `render()`, ahead of the game-over branch, as before, and keeps its comment's
  reasoning.
- Copy (`copySeed()`) uses `navigator.clipboard.writeText()`. If that is
  missing or rejects, it selects the number and runs
  `document.execCommand("copy")`. Feedback is the button's own label:
  "Copied", or "Couldn't copy", for `COPY_FEEDBACK_MS` (1500 ms). It never
  logs.
- Restart keeps its `prompt()`, wording and seed handling. A confirmed restart
  calls `closeAllLayers()` and then `doRestart()`. Cancel closes nothing.

*Layers, Esc and focus*

- `layerStack` (UI-only, beside `detailItem`) holds the open layers bottom to
  top as `{ el, hide, back }`. `openLayer()` pushes an entry and focuses the
  layer's first enabled control, or the layer's root (`tabindex="-1"`) if it
  has none. `closeLayer()` removes one entry and hands focus back through
  `restoreFocus()`: first the same element, then the rebuilt `.itemname` for
  the same `_uid`, otherwise nowhere. A `keydown` listener closes the top
  layer on Escape.
- The drawer (`openMenu()` / `closeMenu()`), both full-screen panels and the
  pop-up all go through the stack. #161's device panel is one more
  `openLayer()` call.
- `rebuildKeepingFocus()` wraps the pop-up's and Crafting's rebuilds. If focus
  was inside, it goes back to the control with the same label, else the one at
  the same position, else the layer root.
- Focus rings are drawn for keyboard use only:
  `:focus:not(:focus-visible){ outline:none }` and a 2 px accent
  `:focus-visible` outline. Layer roots never draw one.
- Game over closes every layer, on the render that first draws the game-over
  screen (`gameOverRendered`).

**UI**

- The sidebar holds Inventory and Here only.
- The drawer opens onto four buttons: Crafting, Health (Not yet), Clothing
  (Not yet), Options. Save / Load, Stats and Map are otherwise unchanged. The
  seed no longer shows every time the drawer opens.
- Functional text introduced: "Crafting", "Health", "Clothing", "Options",
  "Not yet", "Seed:", "Copy", "Copied", "Couldn't copy". It is held to clarity,
  not to the game's tone, and all of it is retunable.

**Removed**

- The sidebar's Craft panel: its `.panel` markup, `#craftBody`,
  `#craftBackBtn`, `renderCraftPanel()`, and the two game-over-branch lines
  that cleared them. The game-over branch now blanks `#craftingList` instead.
- The drawer's Run section: its markup, `#runBox`, and `#runBox` in the
  `#statsBox, #runBox` rule. `#restartMenuBtn` left Save / Load and moved into
  Options, keeping its id.

**Function relocation**

- The `#restartMenuBtn` click handler moved from the end of PERSISTENCE to
  EVENTS / UI HELPERS. It is event wiring that now also closes layers, and it
  still calls PERSISTENCE's `doRestart()` unchanged.
- `renderRunPanel()` became `renderOptionsPanel()` in RENDERING and targets
  `#seedValue`.

**Documentation**

- `getItemActions()`'s two comments that named `renderCraftPanel()` now name
  `renderItemPop()` and the Crafting panel's `renderCraftingPanel()`. The
  pop-up's comment defines "the item detail view", which older comments
  elsewhere still use for the concept. None of them place it in the Craft
  panel.
- Issues filed for what this pass surfaced: #183 (Crafting after game over
  opens onto an empty catalogue: keep it, or show something else?) and #184
  (the `.menu-placeholder` CSS rule is unused). Nothing in scope was deferred.

**Open questions / decisions resolved**

- **Full-screen panel markup**: one element each (`#craftingPanel`,
  `#optionsPanel`) sharing `.full-panel`, not one shared element. Options is
  static markup that only needs its seed written. That keeps Copy's feedback
  timer on a button that is never rebuilt, and a third panel is one more
  element plus one `FULL_PANELS` entry.
- **Layer stack shape**: an array of `{ el, hide, back }`, generic over layers.
- **Finding what a craft wrote**: the before/after `#log` snapshot above.
  Neither `doCraft()` nor `log()` changed.
- **Copy**: the async clipboard with an `execCommand` fallback. Feedback is on
  the button.
- **Pop-up width and scroll**: as the handoff recommended. It is no wider than
  the row, clamped to the viewport, and re-anchored on scroll and resize.
- **Z-order**: as suggested. Pop-up and backdrop at 11/10, below 15. Panels at
  30, above 20.
- **Hub row data**: `HUB_BUTTONS` entries carry `label` and `opens`. Whether a
  button is enabled is derived from `opens`, not stored as a second field that
  could disagree with it.

**Notes / assumptions**

- **Game over closes layers once, not on every game-over render.** The map's
  zoom toggle calls `render()` from inside the drawer. Closing on every
  game-over render would shut the drawer after death, which the handoff says
  stays usable.
- **Crafting after death is empty.** The game-over branch blanks the
  catalogue, as it blanked `#craftBody`. `doCraft()` does not check
  `gameOver`, so live buttons there would let a dead player craft. Whether
  the empty panel should say something is #183, for Tom.
- **Focus is handed back only when it was in the closing layer, or had
  nowhere to be.** Focus the player moved elsewhere is not taken back. Neither
  is focus in the drawer when the pop-up closes beneath it, as it does on a
  Load.
- **The pop-up's focus return point follows `doOpen()`'s re-pointing.** After
  the last sealed unit is opened, Esc returns focus to the opened unit's
  name, which is the item the pop-up is now about.
- **`data-uid` is written only for items that already have a `_uid`.**
  Minting one for every row drawn would add a `_uid` to every item in every
  save.
- Retunable: `POP_MARGIN` (8 px), `COPY_FEEDBACK_MS` (1500 ms), the hub order,
  the placeholder hint, the full-screen body's 560 px max width, and the result
  area sitting below the recipe list.
- While the pop-up is open, its transparent backdrop also covers the ☰ Menu
  button. A tap there closes the pop-up only, per the handoff: an outside tap
  "does nothing else".

**Explicitly out of scope**

- #159 (portrait layout and compact buttons). The pop-up and panels use
  `button.action` as it is.
- #161 (Device Options). The layer stack takes one more layer and nothing more
  was built.
- #162 (Crafting search and filters), #163 / #164 (enabling Health and
  Clothing), #165 (panel sizes), #166 (title screen), #176 (Replay this seed on
  the game-over screen).
- #78 (ARIA roles, labels, inert backgrounds, the closed drawer's tab order).
- Heat recipes in the Crafting panel (#119, #120).
- Any change to `getItemActions()`, `doCraft()`, `doRestart()` or `log()`.

**Explicitly NOT changed**

- Save format and `SAVE_KEY`: no state field. `layerStack`, `craftResult` and
  `gameOverRendered` are UI-only and outside `state`.
- WORLD DATA, ACTIONS, SIMULATION and PERSISTENCE logic.
- `detailItem`'s shape and every place that clears or re-points it.
- The game-over screen's own Restart button.
- The `#log` rules' values. They gained `#craftResult` as a second selector.

**Sections touched**

- `<style>`: the hub row, `.full-panel`, the pop-up and its backdrop,
  `.pop-actions`, the focus-visible rules, `#craftResult` added to the `#log p`
  rules, `#runBox` dropped from the stats rule.
- Markup: `#sideMenu` (hub row added; Run and `#restartMenuBtn` removed),
  `#sidebar` (Craft panel removed), new `#itemPopBackdrop`, `#itemPop`,
  `#craftingPanel` and `#optionsPanel`.
- CONFIG / CONSTANTS: `GAME_CONFIG.VERSION` only.
- PLAYER STATE: the UI-only `layerStack`, `craftResult` and
  `gameOverRendered`, beside `detailItem`.
- INVENTORY / ITEM SYSTEM: two comments in `getItemActions()`.
- PERSISTENCE: the Restart handler moved out.
- EVENTS / UI HELPERS: the layer stack (`openLayer()`, `closeLayer()`,
  `closeAllLayers()`, `restoreFocus()`, `rebuildKeepingFocus()`,
  `focusablesIn()`, `itemNameButton()`), Esc, the pop-up's show/hide and
  listeners, the drawer, `FULL_PANELS`, `HUB_BUTTONS`, the Restart handler and
  `copySeed()`.
- RENDERING: `renderItemList()` (`data-uid`), `renderItemPop()`,
  `positionItemPop()`, `renderCraftingPanel()`, `craftFromPanel()`,
  `renderCraftResult()`, `renderOptionsPanel()`, `render()`.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` touches only the sections
  above. The script parses (`new Function` over the `<script>` body).
- Headless Chromium (Playwright) at 1280×800 and 390×760. Items were seeded
  through Save, an edit to the save, then Load. No page errors.
- **Pop-up.**
  - Placement: opens below its row. Flips above near the bottom (390×700).
    Re-anchors on page scroll and on resize to 360×640. Never wider than the
    row, and on-screen at both sizes.
  - Focus: moves to the first action. The ring shows for a keyboard open and
    not for a mouse open. Keyboard Enter on Take 1 keeps focus inside after
    the re-render.
  - Closing: Esc returns focus to the item's name. An outside tap closes it,
    and a tap on another item's name only closes. Take All closes it; Take 1
    and Place 1 leave it open. Movement closes it.
  - Opening the last sealed box of cereal keeps it open on the opened unit,
    and Esc then focuses that unit's name.
  - With the drawer open over it, Esc closes the drawer first and the pop-up
    second.
- **Hub and panels.**
  - The hub row's order is right, with Health and Clothing disabled and
    reading "Not yet". The drawer focuses ✕ on open.
  - Crafting fills the viewport. Esc closes Crafting, leaves the drawer open,
    and focuses the Crafting button. A second Esc closes the drawer and
    focuses ☰ Menu.
  - Results: a craft showed "You craft a bandage." A second identical craft
    showed "You craft a bandage.×2" in place. The campfire kit then replaced
    it. `#log`'s length grew only by what the crafts wrote. Availability
    updated. The result cleared on close.
  - Load from the drawer left the drawer open.
- **Options.**
  - The seed shows as a number, and Copy put it on the clipboard and read
    "Copied", then "Copy" again.
  - Restart: Cancel left Options open. A confirmed restart with `12345` closed
    every layer, logged the wake-up line, and Options then showed `12345`.
- **Game over.**
  - A craft at 0.01 health with no food or water ended the run and closed
    every layer.
  - The drawer then stayed open through a map zoom-toggle re-render, and
    Options still showed the seed.

**Version**: `GAME_CONFIG.VERSION` `"0.6.3"` → `"0.6.4"`

---

## v0.6.3 — A stowed bag's contents: counted at load, counted as weight

Implements: handoffs/stowed-bag-contents.md

Implements #153 and #156 in full, per `handoffs/stowed-bag-contents.md`. When
a bag is unequipped, what it held moves into the bag item's `contents`. Two
parts of the file never looked inside that array. The load-time scans missed
it, so a stowed item's `_uid` could be handed out again. Weight missed it too,
so a full duffel in the base inventory weighed 0.8 kg. Both now treat an item
as something that can hold a list of items, to any depth. No state or item
field is added and `SAVE_KEY` does not move, so this is PATCH.

**Fixed**

- **#153: `_uidCounter` could land at or below a `_uid` still in use.**
  Root cause: `resyncUidCounter()` and `backfillItemIds()` each walked the
  inventory pools, floors, containers and car containers by hand, and neither
  descended into `contents`. After a load, the counter ignored every uid inside
  a stowed bag. New items reused one, and re-equipping the bag left two live
  items sharing it. Fix: a single walker, `forEachItemList(visit)`
  (PERSISTENCE), calls `visit(list)` for every item array reachable from
  `state` and `world`. That includes the `contents` of any item in any visited
  list, recursively, guarded by `Array.isArray(it.contents)`.
  `resyncUidCounter()`, `backfillItemIds()` and `backfillIllnessScale()` all
  use it now. `backfillIllnessScale()`'s private recursion is gone, because the
  walker's replaces it. `applyLoadedData()`'s call order is unchanged.
- **#156: a stowed bag weighed only itself.** Root cause: `totalWeight()` and
  six inline `qty × unitWeight` products read the empty bag's `unitWeight` and
  nothing in `contents`. Fix: two helpers beside `totalWeight()` in INVENTORY /
  ITEM SYSTEM:
  - `itemUnitWeight(it)` = `it.unitWeight + (Array.isArray(it.contents) ? totalWeight(it.contents) : 0)`;
  - `itemWeight(it)` = `it.qty × itemUnitWeight(it)`.

  `totalWeight()` now sums `itemWeight()`, and the recursion runs back through
  it, so nested bags count at any depth. Every inline product was replaced:
  `addToDestination()`, `giveItem()`, `doStore()`, `renderItemList()`'s row
  total, and `renderCraftPanel()`'s total and "each" figures. No `qty *
  unitWeight` product remains outside the helpers. An item with no `contents`
  weighs exactly what it did in v0.6.2.

**Changed / Reworked**

*Capacity at loaded weight*

- **Unequipping a loaded bag can put the base inventory over its 3 kg.**
  `doUnequip()` still has no capacity check, by Tom's decision. The bag always
  goes into the inventory, and the readout shows the true figure, e.g.
  `8.90 / 3 kg`. While over cap:
  - Take into the inventory is refused: "That won't fit — not enough room
    there.";
  - `giveItem()` drops crafted items, caught fish and removed batteries to the
    floor with its existing warnings;
  - storing items out of the inventory still works.
- **Floors and containers are hard caps at loaded weight.** `doStore()` refuses
  a loaded bag onto a floor or into a container it doesn't fit ("That won't fit
  there."). `addToDestination()` refuses taking a loaded bag into a pool it
  doesn't fit. Both are behaviour changes: before this pass, a bag's contents
  weighed nothing to these checks.
- **Saves already over cap stay over cap.** No load-time repair moves
  anything.
- **Equipped slots are unchanged.** No total counts an equipped bag's own
  weight, as before. What an equipped bag weighs on the player is #168.

**UI**

- No new string or control. Figures changed: a stowed loaded bag's row total
  and detail view (total and "each") show its loaded weight. The Inventory and
  Here readouts count loaded bags in full, and the Inventory readout can read
  over cap. Existing capacity warnings now fire in the cases above.

**Documentation**

- ITEM DATA SCHEMA, `contents`: its items count toward the item's weight
  (`itemUnitWeight()`), bags may nest to any depth, and every load-time scan
  reaches them through `forEachItemList()`.
- `forEachItemList()` carries the invariant: every scan over item lists goes
  through it, because a hand-rolled walk is how a stowed bag's contents gets
  missed.
- `backfillIllnessScale()`'s comment no longer says it is the only scan that
  descends into `contents`.
- The weight helpers carry a comment saying they are the only place an item's
  weight is computed.
- Nothing was deferred, and no new issues were filed.

**Open questions / decisions resolved**

- **Names**: `forEachItemList()`, `itemUnitWeight()`, `itemWeight()`, as the
  handoff suggested.
- **Walker location**: PERSISTENCE, directly above `resyncUidCounter()`, as the
  handoff recommended. Every caller is a load-time scan.
- **`validateReachability()`**: not moved onto the walker, as the handoff
  recommended. It walks a fresh default world, which holds no `contents`, so
  its report cannot change either way.

**Notes / assumptions**

- The walker skips any list that is not an array (`Array.isArray`), where the
  old scans used `list || []`. For `null` or missing lists the two behave the
  same. The only difference is a truthy non-array, which used to throw in
  `forEach` and is now skipped. `validateLoadedWorld()` already rejects a
  non-array floor, so this can only matter for a malformed container's
  `items`.
- `doStore()`'s check reads `moveQty × itemUnitWeight(it)` rather than
  building a copy for `itemWeight()`. Bags never stack, so `moveQty` is 1
  whenever `contents` is present.

**Explicitly out of scope**

- #168 (encumbrance and the equipped-bag carry bonus), #170 (over-encumbrance
  penalties and a hard limit), #169 (a floor bag as a Here tab, including
  `findItemByUid()` searching floor bags).
- Forbidding nesting: Tom's decision is that bags may nest.
- Any capacity number: bag `capacityKg`, `floorCap`, the base inventory's 3 kg.
- A load-time repair for over-cap saves.
- `findItemByUid()`, which still does not descend into `contents`, correctly,
  since nothing inside a stowed bag appears in any panel.
- #134 (per-unit durability in stacks).

**Explicitly NOT changed**

- Save format and `SAVE_KEY`: no new field.
- `doUnequip()`, `doEquip()`, `addToList()`, `findItemByUid()`.
- `applyLoadedData()`'s backfill order.
- All WORLD DATA except the ITEM DATA SCHEMA comment. No capacity or balance
  constant.
- Every weight figure for an item without `contents`.

**Sections touched**

- CONFIG / CONSTANTS: `GAME_CONFIG.VERSION` only.
- WORLD DATA: the ITEM DATA SCHEMA comment only.
- INVENTORY / ITEM SYSTEM: `itemUnitWeight()`, `itemWeight()`, `totalWeight()`;
  the weight reads in `addToDestination()`, `giveItem()` and `doStore()`.
- PERSISTENCE: `forEachItemList()`; `resyncUidCounter()`, `backfillItemIds()`
  and `backfillIllnessScale()` moved onto it.
- RENDERING: `renderItemList()`'s row total; `renderCraftPanel()`'s detail
  total and "each" figure.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` shows only the functions named
  in Sections touched, plus `GAME_CONFIG.VERSION`. The script passes
  `node --check`.
- All checks ran in headless Chromium against uncommitted copies of v0.6.2 and
  this build, with internals exposed.
- **#153 reproduced and fixed.** Setup: one uid'd item in an equipped duffel,
  then unequip, export, reset the counter, import. v0.6.2 left `_uidCounter` at
  1 with `u1` in use. This build set it to 2. A deeper case put a purse holding
  a uid'd knife inside a duffel with two uid'd items, then unequipped, exported
  and imported. `_uidCounter` exceeded every `_uid` in any list, nested
  included. After re-equipping and adding six new uid'd items, no two items
  shared a `_uid`.
- **Backfills two deep.** A pre-registry `Paperback novel` (no `itemId`) and a
  raw fish at `illnessChance: 35` sat inside a purse inside a tote. After
  import they read `paperback_novel` and `0.35`. A second import changed
  nothing.
- **Weight.** A duffel holding 2.95 kg (a purse with contents nested inside)
  showed `2.95` on its tab, then `3.75 / 3 kg` in the inventory after unequip.
  Its row read `3.75 kg`. With nine frying pans the inventory read
  `8.90 / 3 kg`, and the detail view read `8.90 kg (8.90 kg each)`. Take into
  the inventory returned `capacity`. Storing the loaded duffel onto a floor
  capped at 5 kg was refused. With the cap lifted, storing it out of the
  over-cap inventory succeeded. A tote › purse › two items read `1.30` kg.
- **Plain items unchanged.** Row totals and detail views for a pasta stack, a
  box of matches (durability) and a sealed/opened canned soup split were
  identical text on v0.6.2 and this build.
- **Validators.** `validateRoomSchema()`, `validateLocations()`,
  `validateItemRegistry()` and `validateReachability()`: return values and
  console output identical to v0.6.2.
- Grep: no `qty * unitWeight` / `qty*unitWeight` product outside the helpers.

**Version**: `GAME_CONFIG.VERSION` `"0.6.2"` → `"0.6.3"`

---

## v0.6.2 — Seed report: what a seed's world holds

Implements: handoffs/seed-report.md

Implements #150 in full, per `handoffs/seed-report.md`. Two dev-only console
helpers join the `window.ashfallDev` seam. `simulateSeed(seed)` lists every
item stack in one seed's world, hand-placed or rolled, without playing the
seed. `sampleSeeds(n, start)` runs many seeds and checks how often each loot
roll actually hits against what `SPAWN_POOLS` says it should. To make that
possible, the roll core now takes its seed as an argument, and every roll the
game makes comes out bit-identical to v0.6.1. The helpers report existence
only, not what the player can reach, by Tom's decision. Nothing here is
persisted and nothing is a mechanic, so this is PATCH.

**New**

- **`simulateSeed(seed)`** (PERSISTENCE). `seed` can be a number (taken
  `>>> 0`) or a string (through `seedFromInput()`, so a typed word gives the
  same world Restart would). Omitted, it uses the current run's `state.seed`,
  which is the helper's only read of game state. It builds its own
  `makeDefaultWorld()` and `makeDefaultState(seed)` and never reads the live
  world. It returns `{ seed, rows, tags }`:
  - Each row is `{ roomId, place, source, itemId, qty }`. `roomId` is
    `"(start)"` for the starting inventory and slots. `place` is `"floor"`,
    a container id, `"inventory"` or a slot key. `source` is `"hand-placed"`
    or `"rolled"`.
  - Hand-placed rows cover every floor, every container's authored `items`
    (car containers included) and the starting state. Rolled rows are
    `rolledLootFor(seed, …)` for each container that still rolls.
  - `tags` counts, for each tag in `REPORTED_TOOL_TAGS`, the stacks that carry
    it. It counts stacks, not units, which is the convention
    `validateReachability()` uses, so the two reports compare directly.
  - It prints the rows with `console.table()` and one `console.log()` line per
    tag.
- **`sampleSeeds(n = 1000, start = 0)`** (PERSISTENCE). It runs seeds `start`
  through `start + n − 1`, each `>>> 0`, over one shared fresh world. It
  returns `{ n, start, entries, pools, items, tags }`:
  - `entries`: one row per pool entry, with `trials`, `hits`, `observed` and
    `expected = (1 − emptyChance) × chance`. A trial is one seed of one rolling
    container that draws the pool.
  - `pools`: one row per pool, with the empty gate's `observed` rate against
    `emptyChance`.
  - `items`: for each registry item, the fraction of seeds whose world holds
    it anywhere.
  - `tags`: for each `REPORTED_TOOL_TAGS` tag, the fraction of seeds where no
    stack carries it.
  - A pool or entry row is flagged when
    `|observed − expected| > SAMPLE_TOLERANCE_SIGMA × sqrt(expected × (1 − expected) / trials)`.
    Flagged rows go to `console.warn()`, followed by a one-line summary. A dead
    pool has `trials: 0` and `rolled: false`, and is never flagged.
- **`SAMPLE_TOLERANCE_SIGMA = 3`**, beside the helpers. At 3σ over the
  136 rows compared today, one chance flag in a clean run is expected. The
  comment says a flag is a prompt to rerun, not a verdict.

**Changed / Reworked**

*Roll core (CORE UTILITIES)*

- `hashKey(seed, parts)` takes the seed as an argument instead of reading
  `state.seed`. `rollValueFor(seed, parts)`, `chanceFor(seed, p, keyParts)`
  and `randIntFor(seed, min, max, keyParts)` are the real functions.
  `rollValue()`, `chance()` and `randInt()` keep their signatures and remain
  the game's API, bound to `state.seed`. The warn-and-clamp legality check
  moved into `chanceFor()` and is still written exactly once. Its warning text
  is unchanged. `doFish()` and `doConsume()` were not edited.

*Loot (WORLD INTERACTION)*

- `rolledPoolFor(seed, roomId, containerId, poolId)` is one pool's roll. It
  returns `{ empty, items }`, or `null` for an unknown pool id. It is now the
  only place the three loot key shapes are written. `rolledLootFor(seed,
  roomId, container)` concatenates it over `container.spawnPools` in order.
  `doOpenContainer()`, the only game caller, passes `state.seed`.

*Dev helpers (PERSISTENCE)*

- `rollingContainers(world)` returns `[{ roomId, container }]` for every
  container, car containers included, that carries `spawnPools` without
  `spawnRolled`. This is now the one definition of a container that still
  rolls. `validateReachability()` builds `livePools` from it, and both new
  helpers use it.
- `registryCarriesTag(id, tag)` was extracted from `validateReachability()`'s
  inline `carries` so the tag test is written once for all three helpers.

**Documentation**

- The roll core's comment now describes the explicit-seed form and why a
  swap-and-restore of `state.seed` is never used.
- `rolledLootFor()`'s comment names `simulateSeed()` instead of an issue
  number, and describes `rolledPoolFor()`.
- The dev seam's comment covers "the four validators and the two seed
  reports". The read-only rule stays stated.
- Filed #173: `validateReachability()`'s comment still says twelve
  unreachable items at v0.5.1, but there are eleven. The handoff put the fix
  out of scope, because that helper's report and code had to stay unchanged
  this pass. Nothing else was deferred. The one entry the sampler flagged did
  not survive a rerun (see Validation), so no finding about the `chance`
  figures was filed.

**Open questions / decisions resolved**

The handoff left these to implementation. None of them moves the version
type.

- **Names:** the handoff's suggestions were kept: `rollValueFor`,
  `chanceFor`, `randIntFor`, `rolledPoolFor`, `rollingContainers`.
- **Argument order:** seed first everywhere, matching `rolledLootFor(seed, …)`.
  The explicit-seed siblings take their key as one array, not rest
  parameters, so the seed and the key can't be confused.
- **An unknown pool id:** `rolledPoolFor()` returns `null`, not
  `{ empty, items }`, since no gate was rolled. `rolledLootFor()` skips it, as
  before.
- **Row fields:**
  - The starting inventory's `place` is `"inventory"`, which is not a slot
    key.
  - Rows list hand-placed stacks first, then rolled ones.
  - Sampler rows carry `rolled` so dead pools read as not rolled.
  - Dead pools' entries are listed too, with `observed: null`.
  - With `n = 0`, fractions are `null` rather than `NaN`.

**Notes / assumptions**

- `SAMPLE_TOLERANCE_SIGMA = 3` is the handoff's figure, a judgment call and
  retunable. The handoff estimated about 200 comparisons. The real count is
  136 (18 live pools' gates plus their 118 entries), so the comment says
  "hundred-odd".
- `sampleSeeds()` takes its per-seed item and tag tallies from the same
  `rolledPoolFor()` results that feed the entry tallies. It does not call
  `rolledLootFor()` a second time. The yield is the same by construction,
  since `rolledLootFor()` is exactly that concatenation.
- `items` reads `0` for 12 items: the 11 `validateReachability()` calls
  unreachable, plus `campfire_kit`, which can be crafted but never sits in the
  world.

**Explicitly out of scope**

- Whether the player can *reach* anything: locked doors, locked storage
  units, breakable windows and `searchLabel` rooms.
- #133 (dead pools and unreachable items). This pass only measures them.
- Checks on the quantity distribution. #15, #149 and #10.
- `validateReachability()`'s own report, which is unchanged, and its stale
  comment (#173).
- Any UI.

**Explicitly NOT changed**

- Every roll's outcome. The fishing and illness call sites. `SPAWN_POOLS`,
  `ITEM_REGISTRY` and every other WORLD DATA table.
- The save format and `SAVE_KEY`. No state field was added.
- Rendering.

**Sections touched**

- CONFIG / CONSTANTS: `GAME_CONFIG.VERSION` only.
- CORE UTILITIES: the roll core.
- WORLD INTERACTION: `rolledPoolFor()`, `rolledLootFor()`, and
  `doOpenContainer()`'s call.
- PERSISTENCE: `registryCarriesTag()`, `rollingContainers()`,
  `validateReachability()` rewired, `SAMPLE_TOLERANCE_SIGMA`,
  `simulateSeed()`, `sampleSeeds()` and their private helpers
  `seedReportRow()`, `handPlacedRows()` and `tagStackCounts()`.
- The dev seam.
- No WORLD DATA, no other ACTIONS, no SIMULATION, no RENDERING.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` shows the changes above and
  nothing else. The script passes `node --check`.
- All checks ran in headless Chromium against uncommitted copies of v0.6.1
  and this build, with internals exposed.
- **Rolls are bit-identical.** Seeds 0–199 were compared: each of the 24
  rolling containers' `rolledLootFor()` yield, plus `rollValue()` for 20
  rooms × 8 minutes of fishing keys and 30 illness keys. That is 42,800
  values, all identical. 3,802 of the loot yields were non-empty.
- **The manifest matches play.** A run on seed 987654321 opened all 24 rolling
  containers through `doOpenContainer()`. Their contents, summed per
  container and item, equalled `simulateSeed()`'s rolled rows (45 stacks).
  `simulateSeed("some word")` equals
  `simulateSeed(seedFromInput("some word"))`.
- **The helpers are read-only.** With a save loaded through
  `applyLoadedData()`, `JSON.stringify` of `state`, `world`, `doors` and
  `windows` was identical before and after `simulateSeed()` (three forms) and
  `sampleSeeds(200, 3)`.
- **`validateReachability()` is unchanged.** Its 30 lines are byte-identical
  to v0.6.1's.
- **The sampler agrees with the arithmetic.**
  - `sampleSeeds()` at defaults compared 136 rows and flagged 1:
    `valuables`/`jewelry_piece` at 0.075 against 0.052 over 1,000 trials.
  - `sampleSeeds(20000)` flagged 0. `bottled_water` in
    `kitchen_nonperishable` came out at 0.1731 against 0.1744, over 100,000
    trials.
  - `sampleSeeds(5000, 100000)` flagged a different single row
    (`clothing`/`winter_jacket`).
  - No flag persisted across a rerun, so all three are chance flags.
  - The 10 dead pools were none of them flagged.
  - Every tag's missing fraction reads 0.
  - Runtime: 235 ms for `sampleSeeds(1000)` and 4.7 s for
    `sampleSeeds(20000)`.
- **The legality check is written once.** `chance: p … clamped` occurs once
  in the file. No page errors and no clamp warnings occurred.

**Version**: `GAME_CONFIG.VERSION` `"0.6.1"` → `"0.6.2"`

---

## v0.6.1 — 2A's front door, gated both ways

Implements: handoffs/2a-door-both-ways.md

Implements #145 in full, per `handoffs/2a-door-both-ways.md`, using Tom's
option 2. Every exit *into* apartment 2A already passed through door `"2a"`,
but none of the four exits *out* of it did. With the door locked, the player
could still leave 2A from any room and only couldn't get back in. 2B and 1A
were already gated both ways from every room, and now 2A is too. This is a
content-only pass: four exits in WORLD DATA, plus one comment that described
the old data.

**Fixed**

- Door `"2a"` blocked only one way. Root cause: the four `hallway2` exits in
  `buildAcornApartments()`, from `living`, `kitchen`, `bathroom` and
  `bedroom`, were authored without a `doorId`, so `getExitsForRoom()` had
  nothing to drop when the door was locked. Each one now carries
  `doorId:"2a"`. `to`, `label` and `distanceM` are unchanged. These are the
  only exits in the file from a 2A room to `hallway2`, since `balcony` has
  none.

**UI**

No new string or control. The existing door UI, which reads the exits
directly since v0.5.6, picks up the four rooms on its own:

- With `"2a"` locked, `Leave the apartment` no longer appears in `living`,
  `kitchen`, `bathroom` or `bedroom`. In its place `renderHereActionsPanel()`
  prints `Unlock the 2nd Floor door` if a key is carried, or
  `The 2nd Floor door is locked.` if none is.
- In `kitchen`, `bathroom` and `bedroom`, the 2A key's and the master key's
  detail views now offer `Lock the 2nd Floor door` / `Unlock the 2nd Floor
  door`, through `doorsTouchingRoom()`. `living` already offered these,
  because it is one of the door's `sides`, and is unchanged.
- `doorLabel()` names the door "2nd Floor" from all four rooms, because the
  far side of each gated exit is `hallway2`, whose area differs from 2A's.

**Save compatibility**

- **An existing save keeps 2A ungated.** `applyLoadedData()` restores `world`
  from the save as a whole, and no backfill adds an exit field. Only a new
  game or a Restart gets the fix. No `SAVE_KEY` change: PATCH, as the handoff
  specified.

**Documentation**

- The comment above `doorsTouchingRoom()` justified the `sides` half of the
  union by saying 2A's exits "carry no doorId", which is no longer true.
  After this pass, every room in a door's `sides` also has an exit through
  that door, so today the `sides` half only guards against an exit authored
  without its `doorId`, which is how 2A's four were. The comment now says
  that. Changing it went beyond the handoff's "change nothing else", and Tom
  approved it during the session. It is a comment only, with no code
  change.
- Nothing was deferred.

**Explicitly out of scope**

- Whether `"2a"` should ship locked. `makeDefaultDoors()` is untouched and it
  stays `locked:false`, the only door that ships unlocked.
- The `2a-transom` window and the fire escape are unchanged. They are why
  gating is safe: both still get the player out with the door locked and no
  key.
- #89 (`room.building` duplicating `BUILDINGS[].name`), and every other door,
  key and window.

**Sections touched**

- WORLD DATA: four exits in `buildAcornApartments()`.
- WORLD INTERACTION: the comment on `doorsTouchingRoom()` only. No ACTIONS,
  SIMULATION or RENDERING code changed.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` shows the four exit lines,
  `GAME_CONFIG.VERSION`, and the `doorsTouchingRoom()` comment, and nothing
  else.
- In headless Chromium, `ashfallDev.validateItemRegistry()`,
  `validateLocations()`, `validateRoomSchema()` and
  `validateReachability()` return output identical to v0.6.0.
- Walked all four rooms with the door unlocked, then locked with the 2A key
  on the keychain, then locked with the key dropped. Every state matched the
  handoff's UI table. Unlocking from inside `kitchen`, `bathroom` and
  `bedroom` brought `Leave the apartment` back. The master key, added to a
  save, offered `Unlock the 2nd Floor door` in `kitchen`. With the door locked
  and no key, the transom (open, then climb through) reached `hallway2`, and
  the fire escape reached `alley`. No page errors.

**Version**: `GAME_CONFIG.VERSION` `"0.6.0"` → `"0.6.1"`

---

## v0.6.0 — Roll core and the seeded world

Implements: handoffs/roll-core-and-seeded-world.md

Implements #51 in full, per `handoffs/roll-core-and-seeded-world.md`. The file
had one helper and four bare `Math.random()` comparisons using three different
conventions (percent-hit, fraction-hit, fraction-miss). They are replaced by
one operation, `chance(p, ...key)`. It is backed by a stateless source seeded
per run: a roll is a pure function of the run's seed and a key naming what is
being decided. It has no cursor, so draw order never matters. The seed does
two things the old source could not. Reloading and repeating an action
reproduces its outcome, which blocks save-scumming. And container loot becomes
a property of the world rather than of the order the player explores it in.
This is the character-independent core only. #10's skill checks will be a
layer calling `chance()`.

**New**

- The roll core, in CORE UTILITIES:
  - `fnv1a(str, basis)` is a 32-bit FNV-1a hash.
  - `hashKey(parts)` joins the key parts with `KEY_SEP` and hashes them from
    `state.seed`.
  - `rollValue(...key)` returns a value in `[0,1)`: mulberry32's avalanche
    step applied to the hash, without any stepping.
  - `chance(p, ...key)` returns `rollValue(...key) < p`. `p` is a fraction in
    `[0,1]`, and this is the one place a probability is checked for legality:
    an out-of-range or non-finite `p` gets a `console.warn` and is clamped
    (NaN becomes 0) instead of throwing. `p === 0` is always false and
    `p === 1` always true. It returns a plain boolean.
  - `randInt(min, max, ...key)` is widened to take a key and uses the same
    source.
- Constants, in CONFIG / CONSTANTS: `FNV_OFFSET_BASIS` (`2166136261`),
  `FNV_PRIME` (`16777619`), and `KEY_SEP` (`"\u001F"`, the unit separator,
  which cannot occur in any id). Because of the separator, `("a","bc")` and
  `("ab","c")` never produce the same key.
- The three key shapes:
  - Pool empty gate: `"loot", roomId, containerId, poolId, "empty"`.
  - Pool entry: `"loot", roomId, containerId, poolId, itemId`.
  - Entry quantity: the entry's key plus `"qty"`.
  - Fishing bite: `"fish", state.currentRoom, state.totalMinutes`, read after
    `advanceTime()`.
  - Illness on eating: `"illness", state.rollSeq`.
  - Loot keys name pools and items by id, never by array index, so reordering
    a container's `spawnPools` or a pool's `entries` does not reshuffle the
    world.
- `rolledLootFor(roomId, container)` in WORLD INTERACTION returns a
  container's pool yield as a pure function of the seed and the container's
  identity, and mutates nothing. `doOpenContainer()` now only appends that
  yield. `spawnRolled` still guards against a second append, and
  `lastRolledMinute` is still written and still unread.
- PLAYER STATE gains two fields:
  - `seed`: a uint32, the run's identity, set once and never changed.
  - `rollSeq`: starts at `0` and tells apart rolls with no natural key.
  - `makeDefaultState(seed)` takes an optional seed. Without one it draws a
    fresh seed with `Math.random()`, now the only call to it in the file, on
    purpose.
  - `doRestart(seed)` passes the seed on.
- `seedFromInput(str)` in CORE UTILITIES turns typed text into a seed. A plain
  decimal inside the uint32 range is used as the seed itself, so the displayed
  number can be typed back in. Anything else (a word, or an out-of-range
  number) is hashed with `fnv1a` from the standard offset basis.
  `"4294967296"` is hashed rather than wrapping around to seed 0.
- `backfillIllnessScale()` in PERSISTENCE is the sixth load-time backfill,
  wired into `applyLoadedData()` after `backfillRoomAddresses()`. It divides
  any instance's `illnessChance` above 1 by 100. A legal fraction can never
  exceed 1, so the test is unambiguous and the division is exact. Running it
  on a v0.6 save changes nothing.

**Changed / Reworked**

*The four randomness sites*

- `doOpenContainer()`: the empty gate, entry and quantity rolls moved into
  `rolledLootFor()` with the keys above. The entry test is now a hit test
  (`chance(entry.chance, …)`), where it used to be the miss form
  `>= entry.chance`. Behaviour is the same, under one convention.
- `doFish()`: `chance(FISH_BITE_CHANCE, "fish", state.currentRoom,
  state.totalMinutes)`. Keying on game time is what enforces the save-scum
  rule: repeating the same cast gives the same result, while spending any
  time first changes the roll.
- `doConsume()`: the illness branch is restructured so it rolls and advances
  `rollSeq` whenever `it.illnessChance` is set, even if the player is already
  ill and the result is thrown away. That matches the order the old
  short-circuit used up draws in. The already-ill test stays inside the
  branch. Moving it into the outer guard would get `rollSeq` out of step with
  a save taken before the meal.

*`illnessChance` unit*

- `ITEM_REGISTRY.raw_fish.illnessChance` changed from `35` to `0.35`, and the
  ITEM DATA SCHEMA comment now describes it as a fraction in `[0,1]`. The
  probability is 35% before and after, so this is not a balance change. This
  is definition data for the mechanic, since the field's unit is part of the
  convention being set up, so it ships with this pass rather than as a
  separate content pass.

*Player-visible behaviour — none of it a balance change*

1. **Reloading no longer rerolls.** Repeating an action from a reloaded save
   gives the same outcome. Doing anything that costs game time first gives a
   genuinely different roll.
2. **Container loot is set by the seed and the container's location.** It is
   the same whatever order the world is explored in. A loaded save's
   containers that were already rolled keep what they were saved with.
   Containers not yet opened roll from the save's seed; a pre-0.6 save gets a
   fresh one.
3. **Illness probability is unchanged** at 35%. Only the field's unit changed.

**UI**

- A new **Run** section in the side menu, below Stats, shows `Seed: <n>` as
  the canonical uint32. `renderRunPanel()` draws it at the top of `render()`,
  before the game-over branch, so the seed stays visible after death. The
  game-over branch clears `#statsBox`; the seed has its own `#runBox`, which
  shares `#statsBox`'s style rule.
- **Restart game** now uses a `prompt()` instead of a `confirm()`, with the
  same warning plus "Leave blank for a new world, or enter a seed to replay a
  specific one." Cancel does nothing, so it still guards the destructive
  action the way the confirm did. Blank restarts with a fresh world, which is
  the old behaviour. Anything else goes through `seedFromInput()`.
- No other control, panel or string changed.

**Hardened**

- Four authoring guards were added to the validators:
  - `validateReachability()` now reports an `emptyChance` outside `[0,1]`.
  - It reports a pool that lists the same `itemId` twice.
  - It reports a container (in the fresh default world) that lists the same
    pool id twice. Both duplicates would share a roll key and always roll
    alike.
  - `validateItemRegistry()` reports any `illnessChance` outside `[0,1]`.
  - `validateReachability()`'s warning block is now labelled "pool authoring
    problems" and covers all of its checks, not only the old entry-chance
    one.
  - None of the guards fire on the current data, and the rest of
    `validateReachability()`'s report is identical to v0.5.6's.

**Documentation**

- Comments updated: the ITEM DATA SCHEMA `illnessChance` line; the
  SPAWN_POOLS header (loot is keyed and rolled through `rolledLootFor()`, and
  duplicate pool or item ids are forbidden); `doOpenContainer()`'s header;
  both validators' headers; and `applyLoadedData()` (how an older save gets
  `seed`).
- The ordering rule is written beside `rollSeq` in `makeDefaultState()`:
  nothing reachable from `render()` may advance `rollSeq`.
- Filed #153: `resyncUidCounter()` and `backfillItemIds()` never look inside
  an unequipped bag's `contents`, so after a load a stowed item's `_uid` can
  be handed out again. This predates the pass; see Notes for why
  `backfillIllnessScale()` recurses anyway. Nothing from the handoff's In
  scope list was deferred.

**Explicitly out of scope**

- #10: degrees of success, opposed rolls, modifiers, and anything that
  depends on the character. `chance()` returning a plain boolean is what
  keeps those layers apart.
- #150: `simulateSeed()` and seed sampling. `rolledLootFor()` is built to
  make it possible, and none of it is built here.
- #149: run configuration beyond the seed.
- Any general stream registry or key-namespacing scheme. There are three
  domains and three key shapes.
- `SPAWN_POOLS` values: all 178 entry `chance`s and 29 `emptyChance`s are
  untouched.
- Eating taking zero game time (#120/#121).
- #15: `lastRolledMinute` stays reserved.
- #133: dead pools and unreachable items.
- #48, #50, #52, #23: the consumers the core exists for.
- #134/#116: durability and tool wear.

**Sections touched**

- CONFIG / CONSTANTS
- WORLD DATA: the `raw_fish.illnessChance` value, the ITEM DATA SCHEMA and
  SPAWN_POOLS comments, and nothing else.
- PLAYER STATE
- CORE UTILITIES
- INVENTORY / ITEM SYSTEM: `doConsume()`
- WORLD INTERACTION: `rolledLootFor()` and `doOpenContainer()`
- FIRE / COOKING: `doFish()`
- PERSISTENCE: the backfill, `doRestart(seed)`, and the validators
- EVENTS / UI HELPERS: the restart prompt
- RENDERING: `renderRunPanel()` and the game-over Restart button
- The side-menu markup and CSS (`#runBox`)

This is neither a content-only nor a mechanics-only pass. The one WORLD DATA
value is part of the mechanic's own definition.

**Open questions / decisions resolved**

- **Seed readout placement**: the handoff's recommended default, a new
  **Run** section below Stats, chosen over a line inside Stats. It survives
  the game-over wipe, and #149 will need a home for run configuration.
- **`rolledLootFor()` extraction**: extracted as specified, so #150 can
  evaluate a seed without mutating a world.
- **`KEY_SEP`**: `"\u001F"`, as recommended.
- **Prompt wording**: the handoff's default text, unchanged.

**Notes / assumptions**

- `backfillIllnessScale()` also descends into an item's `contents`, which
  the handoff's version did not. An unequipped bag keeps its items there,
  where `invPools()` and the world walk don't reach. A pre-0.6 raw fish
  stowed in one would otherwise come back unrepaired when the bag is
  equipped again and cause illness every time it is eaten (`chance()` would
  clamp 35 to 1, with a warning). This is a technical choice, noted here
  instead of made silently. The same gap in the older scans is #153.
- The game-over **Restart** button now calls `()=> doRestart()` instead of
  passing `doRestart` directly. Once `doRestart` took a `seed` parameter, the
  bare handler would have received the click event as its seed, and
  `event >>> 0` is `0`. So every restart from the death screen would have
  replayed seed 0. This is a hazard the pass created and closed before it
  shipped, not a bug that reached players. That button still starts a fresh
  random world with no prompt, since the handoff limits UI changes to the
  menu's Restart. Replaying a seed after death goes through the menu, where
  the Run section still shows the seed.
- `FISH_BITE_CHANCE` (0.55) and the illness figure (0.35) are unchanged
  balance values, still retunable.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` is the diff. The only
  `Math.random()` left is the seed draw in `makeDefaultState()`.
- Headless Chromium, run against a copy of the file with its internals
  exposed for testing (the copy was not committed):
  - **`SAVE_KEY` rotation and the backfill.** A save made with the v0.5.6
    build (raw fish in the inventory, on the floor, and inside an unequipped
    backpack) was saved under `ashfall_save_v0.5`, which "Load from this
    browser" in v0.6.0 does not see ("No saved game found in this
    browser."). The exported file imported through the real file input with
    the v0.5.6 → v0.6.0 version warning. All three fish came back with
    `illnessChance` `0.35`. The state inherited a uint32 `seed` and
    `rollSeq` `0`, and the Run box updated. Importing the result again left
    `0.35` unchanged.
  - **The save-scum rule.** Tested across 200 seeds at the riverbank.
    Reload and repeat `doFish()`: the same outcome 200 of 200 times. Reload,
    Rest, then fish: the same outcome 104 of 200 times (chance agreement).
    Bite rate was 0.575 against 0.55.
  - **Loot.** With the same seed, opening all 24 still-rolling containers
    in reverse order after an hour's Rest gave identical contents. A
    different seed changed 23 of the 24. `rolledLootFor()` is pure and
    returns the same result on repeat calls. Opening a container twice does
    not add its loot twice. Over 20,000 seeds, `bottled_water` in
    `kitchen_nonperishable` appeared at 0.172 against the expected 0.174,
    with quantities 1, 2 and 3 about equally often.
  - **Illness.** Over 2,000 seeds the illness rate was 0.340 against 0.35.
    `rollSeq` does not move for food without `illnessChance`, and does
    advance when the player is already ill. Three raw fish eaten in the same
    minute roll independently and give the same results from a reloaded
    save.
  - **`chance()` and `rollValue()`.** `chance(0)` never fired and
    `chance(1)` always fired over 5,000 keys. `rollValue()` stayed below 1.
    `p` of `35` and `NaN` warned and clamped.
  - **`seedFromInput()` and the prompt.** Cancel left the run untouched.
    Blank gave a new seed. `" 98765 "` gave seed `98765`, and a word gave
    its hash, with both shown in the Run box. After death the seed stays
    visible, and the Restart button gave five different non-zero seeds.
  - **Validators.** A copy with a duplicated pool, a duplicated entry,
    `emptyChance:1.5` and `illnessChance:35` triggered all four new guards,
    and the real file triggers none. There were no page errors.

**Version**: `GAME_CONFIG.VERSION` `"0.5.6"` → `"0.6.0"`

---

## v0.5.6 — The locked-door note, driven by gated exits

Implements: handoffs/locked-door-note-from-exits.md

Implements #142 in full, per `handoffs/locked-door-note-from-exits.md`. In six
rooms a locked door removed the only exit and the Here panel printed nothing in
its place; in a seventh it printed a note about a door that blocks nothing. Both
came from one cause: the door UI read `doors[].sides` — which two rooms a door
physically separates — while movement is gated by `doorId` on an exit, which
says which exits that door actually blocks. The two disagree, and this pass
moves the UI onto the exits. Rendering-side only: no WORLD DATA, no schema
field, no state field, no change to which doors are lockable or which exits a
locked door removes.

**New**

- `gatedExitsForRoom(roomId)` in WORLD INTERACTION: one `{ doorId, to }` per
  exit of the room's raw `room.exits` that carries a `doorId` resolving in
  `doors`, in the room's own exit order, deduped by `doorId`. Reads raw
  `room.exits` rather than `getExitsForRoom()` — the latter is what drops a
  locked exit, which is precisely what has to be reported. An exit whose
  `doorId` does not resolve is skipped, matching how `doorLabel()` already
  fails safe.
- `doorsTouchingRoom(roomId)` beside it: the union of `doorsForRoom(roomId)`
  and the `doorId`s of that room's gated exits, `doorsForRoom()` entries first
  in their existing order. The union is load-bearing — a narrower rule would
  withdraw the master key's existing `Lock the 2nd Floor door` from inside
  `living`, which is a `sides`-only door.

**Fixed**

- The Here panel's door block (`renderHereActionsPanel()`) is now driven by the
  room's locked gated exits instead of `doorsForRoom()`. The six rooms that lose
  their only exit to a locked door now explain it: `twobee_kitchen`,
  `twobee_bathroom` and `twobee_bedroom` print the `2nd Floor` door;
  `onea_kitchen`, `onea_bathroom` and `onea_bedroom` print the `1st Floor` door
  — the same labels `twobee` and `onea` already print one room away.
- `living` no longer prints `The 2nd Floor door is locked.` The exit out of 2A
  carries no `doorId` and is walkable whatever `"2a"`'s state is, so the note was
  false. Removing it is the fix, not a side effect; the master key still offers
  Lock/Unlock there via `doorsTouchingRoom()`.
- `doorLabel(doorId, fromRoomId)` widened in place — same name, signature and
  `doorId` fallback. The far side is still the other `sides` entry when the near
  room adjoins the door; otherwise it is the `to` of that room's gated exit
  through the door. Its first guard previously returned the bare `doorId` for a
  non-`sides` room, which would have rendered `The 2b door is locked.` in the
  six rooms above. The naming rules below it are untouched.
- `getItemActions()`'s master-key branch reads `doorsTouchingRoom()` in place of
  `doorsForRoom()`, so the master key's panel — blank in those same six rooms —
  now offers Lock/Unlock there. Its `building` filter and label are unchanged.
- The single-key branch's guard is membership of `doorsTouchingRoom()` in place
  of `doors[it.doorId].sides.includes(state.currentRoom)`. This changes nothing
  today — the only single key is `acorn_apt_2a_key` (`doorId:"2a"`), and the one
  room with a `2a`-gated exit is `hallway2`, already a `sides` member — and is
  specified so a future single key behaves like the master one rather than
  inheriting the bug this pass removes.

**UI**

- No new string and no new control. The same two sentences —
  `Unlock the ${label} door` and `The ${label} door is locked.` — appear in six
  rooms where nothing appeared, and stop appearing in one room where they were
  wrong.
- `onea`'s two notes swap order (`patio` now before `1st Floor`), because the
  block follows exit order rather than `Object.keys(doors)` order. Exit order is
  also the order the exits themselves appear in the panel immediately above.
  Key-panel label order is unchanged everywhere, which is what
  `doorsTouchingRoom()`'s `doorsForRoom()`-first ordering buys.

**Explicitly NOT changed**

- WORLD DATA: no room, exit, container, item or `doors` entry moved. No
  `doorId` was added anywhere.
- `findKeyForDoor()`, `doorsForRoom()`, `doToggleLock()`, `getExitsForRoom()`
  and `makeDefaultDoors()` are untouched. Which doors are lockable, by whom, and
  which exits a locked door removes is exactly as it was.
- Save format: no state field added, read or changed. `versionCompat()` does not
  move and a PATCH bump keeps `ashfall_save_v0.5`, so v0.5.5 saves load with no
  version warning.
- `hereNote()` and `actionButton()` are used exactly as before.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` read hunk by hunk: five hunks,
  touching only `GAME_CONFIG.VERSION`, `getItemActions()`'s two key branches,
  the two new queries, `doorLabel()` and `renderHereActionsPanel()`'s door
  block. No WORLD DATA line appears in the diff.
- `node --check` on the extracted script body.
- `ashfallDev.validateRoomSchema()`, `validateLocations()`,
  `validateItemRegistry()` and `validateReachability()` run against a v0.5.5
  build and this one and diffed: identical output, as required since no world
  data moved.
- All thirteen rooms that touch a door walked through the real
  `renderHereActionsPanel()` and `getItemActions()` path in three lock states
  (default, all locked, all unlocked), against both builds. The delta is exactly
  the seven rows the handoff predicted: six rooms gain a note/button, `living`
  loses its false one, `onea`'s two notes swap order, and the other six rooms
  are byte-identical.
- The day-one route from #142 replayed: master key in hand, `onea_patio` →
  unlock `1a-patio` → `onea` → `onea_kitchen`. Before: no exit and no note.
  After: `Unlock the 1st Floor door`, and unlocking restores `Leave 1A`.
- The master key in `living` confirmed to still offer `Lock the 2nd Floor door`.

**Open questions / decisions resolved**

- **Names and return shape of the two new queries.** `gatedExitsForRoom(roomId)`
  returns `[{ doorId, to }]` as the handoff recommended. The union query is
  named `doorsTouchingRoom(roomId)` rather than the recommended `doorsAtRoom` —
  `doorsAtRoom` and `doorsForRoom` are too close to tell apart at a call site,
  and the handoff's own instruction was to rename the new one rather than the
  old one, which is described in existing comments. It keeps
  `doorsForRoom(roomId)`'s argument shape and `doorId[]` return type so the two
  still read as siblings.
- **Where the dedup lives.** Inside `gatedExitsForRoom()`, per the recommended
  default, so neither caller repeats it and the guarantee belongs to the query.
  No room needs it today; it is insurance against a future room with two exits
  through one door printing the note twice.
- **Whether `doorLabel()` is widened or gains a sibling.** Widened in place, per
  the recommended default — one function, three call sites, and no caller edited
  for the label at all. A sibling would mean choosing at each call site which to
  use.

**Explicitly out of scope**

- **#145** — 2A's four outbound exits carrying no `doorId`. Split out of #142
  during planning precisely so this pass stays rendering-side; left open and
  untouched.
- **#89** (`room.building` duplicating `BUILDINGS[].name`) — the label reads
  `area` and `room`, never `building`.
- **#29** (log size and entry cap) and **#78** (the accessibility pass).
- No new door, no new key, no new window, no world data of any kind.

**Sections touched**

- **WORLD INTERACTION** — `gatedExitsForRoom()` and `doorsTouchingRoom()` added
  beside `doorsForRoom()`; `doorLabel()`'s far-room resolution widened and its
  invariant comment extended.
- **INVENTORY / ITEM SYSTEM** — `getItemActions()`, both key branches.
- **RENDERING** — `renderHereActionsPanel()`, the door block only.
- **CONFIG / CONSTANTS** — `GAME_CONFIG.VERSION`.

**Documentation**

- The comment above `doorLabel()` now states that the far side comes from the
  room's gated exit when the near room is not a `sides` member. The two new
  queries carry comments recording why the UI is driven by exits rather than by
  `sides`.
- Nothing was deferred. No new issues were filed — the pass surfaced nothing
  beyond #145, which planning had already split out.

**Version**: `GAME_CONFIG.VERSION` `"0.5.5"` → `"0.5.6"`

---

## v0.5.5 — `shelter` corrected on five rooms, and `partial` put to use

Implements: handoffs/shelter-partial-and-none.md

Implements #141 in full, per `handoffs/shelter-partial-and-none.md`. `shelter`
records whether a room is under cover, and five rooms recorded the wrong thing:
three outdoor rooms were marked `"full"`, and two street nodes with described
overhead cover were marked `"none"`. Nothing reads the field yet, so nothing was
visibly broken — the point is that #58 (weather) and #6 (rooftops) inherit the
data rather than the error. The pass also puts `"partial"` into service for the
first time; `validateRoomSchema()` has always accepted it. Content-only: five
one-token WORLD DATA edits and the ROOM SCHEMA comment, with no mechanic, no
rendering and no state.

**New content**

- `balcony` (2A) and `twobee_balcony` (2B): `shelter:"full"` → `"partial"`. A
  top-floor balcony sits under the building's roof overhang, and a narrow ledge
  recessed into a facade is enclosed on three sides — cover without enclosure.
  The two are described as mirroring each other and take the same value.
- `onea_patio` (1A): `shelter:"full"` → `"none"`. "Out back, low fence, a gate
  leading to the alley" describes nothing overhead.
- `mill2nd`: `shelter:"none"` → `"partial"`. The description puts the room
  explicitly under a conveyor bridge.
- `mid_cedar_1_2`: `shelter:"none"` → `"partial"`. A bus shelter is a partial
  shelter by construction; at room granularity, standing at the node means
  being able to stand in it.
- Counts after the pass: `shelter:"full"` 37, `"partial"` 4, `"none"` 177 —
  218 rooms, unchanged. `cannotHaveFire` is still on 40 rooms; no room gained
  or lost it.

**Documentation**

- The `shelter` entry in the ROOM SCHEMA comment (WORLD DATA). Its type line
  now reads `"none" | "partial" | "full"`, the paragraph describing `"partial"`
  as reserved for a later pass is replaced by what `"partial"` means, and the
  claim that `shelter` and `cannotHaveFire` "happen to be coextensive" is
  replaced by the divergence this pass creates, stated in both directions: the
  two balconies and the 1A patio carry `cannotHaveFire` without being fully
  under cover, and the two partial street nodes are covered and can still host
  a fire. The "laid down ahead of its consumers" paragraph and the
  `backfillRoomAddresses()` sentence are both still true and are kept.
- Nothing was deferred, and no sixth mis-classified room turned up, so no
  issues were filed by this pass.

**Explicitly NOT changed**

- Every other room's `shelter` value. The remaining 213 are read as correct;
  a full re-read of all 218 descriptions is a content session of its own.
- Room `desc` strings. The five classifications are read *from* the
  descriptions as authored — rewriting one to justify a value would be
  reasoning backwards.
- `cannotHaveFire` on any room. The correlation breaking is the point of the
  pass, not a thing to repair.
- `validateRoomSchema()`, which already accepted `"partial"` and would not have
  caught any of these five: it checks that a value is legal, not that it is
  right.
- Save format and `versionCompat()`. No state field is added or read, and
  `backfillRoomAddresses()` still deliberately does not restore `shelter` — a
  loaded save keeps whatever value it was written with, which is acceptable
  precisely because nothing consumes it.

**Explicitly out of scope**

- #58 (weather) and #6 (rooftops), the eventual consumers. This pass gives them
  correct data to inherit and builds nothing on top of it.
- #142, the locked-door note (`handoffs/locked-door-note-from-exits.md`) —
  sibling handoff from the same planning session, touching no common line.
- #89 (`room.building` duplicating `BUILDINGS[].name`) — a different field.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` shows exactly six hunks: five
  one-token `shelter` edits, the ROOM SCHEMA comment, and `GAME_CONFIG.VERSION`.
- `node --check` on the extracted script body: clean.
- Counts by grep: `"full"` 40 → 37, `"partial"` 0 → 4, `"none"` 178 → 177,
  totalling 218; `cannotHaveFire` 40 → 40, no longer equal to the `"full"`
  count.
- `ashfallDev.validateRoomSchema()` reports no problems. `validateLocations()`,
  `validateItemRegistry()` and `validateReachability()` run against a v0.5.4
  build and this one in Chromium produce identical output, as none of them
  reads `shelter`.
- A save written by the v0.5.4 build loads in this build under
  `ashfall_save_v0.5` with no version warning.

**Open questions / decisions resolved**

- The handoff left only the schema comment's wrapping and phrasing open. Every
  statement in its replacement text is kept; the one departure is its closing
  sentence, "They are different facts, a fire rule against being under cover",
  rendered as "They are different facts (a fire rule vs. being under cover)" —
  the wording the comment already used, which the surrounding sentences read
  against more cleanly.

**Sections touched**

- **WORLD DATA** — five `shelter` values in `buildAcornApartments()` (three),
  `buildMillSt()` (one) and `buildCedarSt()` (one), and the ROOM SCHEMA
  comment.
- **CONFIG / CONSTANTS** — `GAME_CONFIG.VERSION`.

**UI**

- None. Nothing reads `shelter`, so the player sees no difference of any kind.

**Version**: `GAME_CONFIG.VERSION` `"0.5.4"` → `"0.5.5"`

---

## v0.5.4 — Door labels named by the far side

Implements: handoffs/door-label-by-far-side.md

Implements #136 in full, per `handoffs/door-label-by-far-side.md`, taking the
issue's option 1: a door is named by the side the player is *not* standing on,
derived from the world rather than tabulated. `DOOR_LABELS` gave each door one
name and both readers rendered it as *where the door leads*, so it was only ever
correct from one side — standing inside 2A with the door locked, the Here panel
read `The door to 2A is locked.` Content is untouched; this is a mechanics and
UI pass over four strings.

**Removed**

- `DOOR_LABELS` (WORLD DATA) and its comment. Nothing replaces the table — the
  name is now derived at render time by `doorLabel()`. Its `"the patio"` entry
  was a hand-written workaround for the `onea` duplicate described under
  **Fixed**, and goes with it.

**New**

- `doorLabel(doorId, fromRoomId)` in WORLD INTERACTION, beside `doorsForRoom()`
  and `findKeyForDoor()` — a world query with readers in two other ARCHITECTURE
  sections, so it belongs to neither of them. It takes the entry of
  `doors[doorId].sides` that is not `fromRoomId` and names it: the far room's
  `area` when that differs from the near room's, else its `room` lowercased,
  else its `area`, else the door id. Every caller is inside a `doorsForRoom()`
  loop or guarded by `sides.includes(state.currentRoom)`, so the near room is
  always one of the two sides.
- The composition is `area`-then-`room` because neither field alone survives the
  current world, and both failures are one door apart: `"1a-patio"` joins `onea`
  and `onea_patio`, which share the area `"1A"`, so naming by `area` reproduces
  the original bug on the patio door; `hallway2` carries `"2a"` and `"2b"`, whose
  far sides are both a `"Living Room"`, so naming by `room` gives that hallway
  two identically-labelled doors. The helper carries a comment saying so — it is
  the invariant the function body cannot state.
- Case is asymmetric on purpose: an `area` is a proper name and keeps its
  capitals (`"2A"`, `"2nd Floor"`), a `room` is a common noun and is lowercased
  (`"patio"`, `"living room"`). The template supplies the article, so neither
  form needs to carry one.

**Fixed**

- A locked door read as its own room's name from inside it. Root cause:
  `DOOR_LABELS` keyed one name per door id while both readers phrased it as a
  destination. Standing in 1A now reads `The 1st Floor door is locked.` where it
  read `The door to 1A is locked.`
- The master key offered two identically-labelled buttons in `onea`, where
  `doorsForRoom()` returns both `"1a"` and `"1a-patio"`. Reachable since v0.5.2
  opened the alley gate and made the patio a day-one route in. The two now read
  `Unlock the 1st Floor door` and `Unlock the patio door`.

**UI**

- Four strings, all functional UI text and all retunable:

  | | before | after |
  |---|---|---|
  | locked note (Here) | `The door to 2A is locked.` | `The 2A door is locked.` |
  | unlock button (Here) | `Unlock the door to 2A` | `Unlock the 2A door` |
  | master key (item detail) | `Unlock 2A` / `Lock 2A` | `Unlock the 2A door` / `Lock the 2A door` |
  | single key (item detail) | `Unlock` / `Lock` | `Unlock the 2A door` / `Lock the 2A door` |

- The name moves in front of "door" because the derivation demands it: the old
  template cannot take `"2nd Floor"` or `"patio"` without an article, and which
  strings need one is not a fact the data carries. Moving the name removes the
  article from the sentence entirely.
- `renderHereActionsPanel()`'s unlock button and the master key's now produce the
  **same** string, where they differed before (`Unlock the door to 2A` against
  `Unlock 2A`). Intended — one action offered in two panels should read alike.
- The single-key branch of `getItemActions()` named no door at all, rendering a
  bare `Unlock` / `Lock`. It now carries the same label as the other three. This
  is beyond #136's literal text and was specified deliberately by the handoff: it
  is the same sentence in the same panel.

**Changed / Reworked**

- The four inside-an-apartment cases now read `"2nd Floor"` / `"1st Floor"` where
  a hand-written table would have said `"the hallway"`. Accurate — from inside 2A
  the door does lead to the 2nd floor — and the price of deriving rather than
  tabulating. **Retunable.** If it reads wrong in play, the fix is a room-first
  variant with per-room collision detection, which needs a different helper shape
  (`doorLabels(roomId)` returning a map); the handoff names that a new planning
  question rather than an implementation choice, so it was not built here.

**Open questions / decisions resolved**

The handoff left two implementation choices open and no questions for Tom.

- **Helper name and signature.** Took the recommended default,
  `doorLabel(doorId, fromRoomId)` — argument order matching `doorsForRoom(roomId)`
  nearby, door-first at both call-site shapes.
- **Where the `|| doorId` fallback lives.** Absorbed into the helper, as
  recommended, so no caller repeats it. All four call sites now pass the result
  through unguarded. The helper returns the door id when the door is absent, when
  the near room is not one of its sides, when the far side does not resolve in
  `world`, or when the far room carries neither `area` nor `room`. No current door
  reaches any of the four.

**Explicitly out of scope**

Restated from the handoff so it needn't be reopened: **#142** (`doors[].sides`
disagreeing with the exits that carry `doorId`) — that issue is about whether the
note appears, this pass only about what it says; no `doorId` and no `sides` entry
changed. **#141** (three outdoor rooms marked `shelter:"full"`) — no `shelter`
value changed. **#89** (`room.building` duplicating `BUILDINGS[].name`) — the
helper reads `area` and `room`, never `building`. **#29** (log size and entry
cap). **#78** (the accessibility pass) — `hereNote()` and `actionButton()` are
used exactly as they were. No new door, no new key, no change to
`makeDefaultDoors()`, no exit label changed.

**Explicitly NOT changed**

- No WORLD DATA content. No room, container, exit, item or door *definition* was
  touched; `doors[].sides`, `doors[].building` and `doors[].locked` are byte-for-
  byte as they were, and `makeDefaultDoors()` is unchanged. The only WORLD DATA
  edit is the deletion of `DOOR_LABELS`, a lookup table, not a definition.
- No save format change. No state field added, read or changed. `SAVE_KEY` stays
  `ashfall_save_v0.5` — this is a PATCH bump, `versionCompat()` does not move, and
  existing browser saves keep loading.
- `findKeyForDoor()`, `doorsForRoom()` and `doToggleLock()` are unchanged. Which
  doors are lockable, by whom, and from where is exactly as it was; only the name
  on the button changed.

**Validation performed**

- `grep -c DOOR_LABELS ashfall.html` → `0`.
- `git diff origin/main...HEAD -- ashfall.html` read hunk by hunk and mapped to
  the five sections below; five hunks, nothing else in the file.
- `node --check` on the extracted script body.
- `ashfallDev.validateRoomSchema()`, `validateLocations()`, `validateItemRegistry()`
  and `validateReachability()` run against both the v0.5.3 build and this one in a
  DOM, and diffed: **identical output**, as required by a pass that changes no
  world data.
- All ten sides of all five doors exercised through the real render path — the
  locked note and, with the master key, the unlock button. Every row matches the
  handoff's table: `2A` / `2nd Floor`, `2B` / `2nd Floor`, `1A` / `1st Floor`,
  `1B` / `1st Floor`, `patio` / `living room`.
- Both `getItemActions()` key branches checked in both lock states: the master key
  in `onea` yields two buttons with **different** labels, and the single key reads
  `Unlock the 2A door` from `hallway2` and `Unlock the 2nd Floor door` from
  `living`.
- A save written by the v0.5.3 build loads under `ashfall_save_v0.5` with no
  version warning and labels its doors correctly. A v0.5.1-shaped save, whose
  `doors` blob has no `"1a-patio"` entry, loads and renders with no error; the
  loader merges the default door set, so the absent-door path is not reached in
  practice, and `doorLabel()` returns the door id if it ever is.

**Sections touched**

- **CONFIG / CONSTANTS** — `GAME_CONFIG.VERSION` only.
- **WORLD DATA** — `DOOR_LABELS` and its comment deleted. Nothing else.
- **WORLD INTERACTION** — the new `doorLabel()` helper.
- **INVENTORY / ITEM SYSTEM** — `getItemActions()`, both key branches.
- **RENDERING** — `renderHereActionsPanel()`, the unlock button and the locked note.

Untouched: PLAYER STATE, CORE UTILITIES, SURVIVAL / TIME SIMULATION, STAMINA /
FATIGUE, CRAFTING, FIRE / COOKING, PERSISTENCE, EVENTS, RENDERING / MAP, and the
document `<style>` and `<body>` blocks.

**Documentation**

- The `doorLabel()` comment is the only prose added to the script; the
  ARCHITECTURE comment and the schema comments are unchanged.
- **Nothing was deferred.** Everything this pass cut is already an open issue and
  is named under **Explicitly out of scope**, and no new issue was filed — the
  pass surfaced nothing beyond its spec.

**Version**: `GAME_CONFIG.VERSION` `"0.5.3"` → `"0.5.4"`

---

## v0.5.3 — Presentation & signal pass

Implements: handoffs/presentation-and-signal-pass.md

Implements #124, #108, #110, #113, #126 and #131 in full, per
`handoffs/presentation-and-signal-pass.md`. Everything the player reads, plus
the one mechanics fix that gives the reading something to say, plus the dev
seam that makes the project's own checks runnable. The sibling handoff
`handoffs/reachable-tools-and-content-corrections.md` shipped as v0.5.2 and
carried the same planning session's instance content; this pass is the
rendering, markup and rules half, and touches **nothing in WORLD DATA** — no
room, item, container, exit, description or pool changed.

PATCH: no field was added to anything serialized, so `versionCompat()` does not
move and `SAVE_KEY` stays `ashfall_save_v0.5`. Existing browser saves keep
loading.

**New**

*A tool that reaches zero is gone (#126)*

- `consumeMatchUse()` spent a fire-starter's use and left the item in the list
  forever. It now removes the whole entry when `durability.current` reaches
  zero or below, logs `The box of matches is spent.` as a `warn` line, and
  still returns `true` — the use it just spent was real, so the caller's action
  succeeds and only the *next* one finds nothing to light with.
- `findFireStarter()` returns `{ list, index, item }` rather than the bare
  item, the shape `findItemByUid()` already uses, because nothing could splice
  what the old return gave it. `hasMatchUses()` is unchanged.
- This is the precedent for **#116** (tool wear), not a special case for
  matches: the rule is "a tool that reaches zero is gone", and any future
  durability spender inherits it. Nothing else about fire changed —
  `findFireStarter()`'s `current > 0` predicate, `canBuildFire()`,
  `FIRE_BUILD_WOOD`, `FIRE_MINUTES_PER_WOOD` and `FIRE_MAX_MIN` are all
  untouched.
- The whole entry is spliced rather than its `qty` decremented, because
  `addToList()` never merges a durability-bearing item and every fire-starter
  placement in the world is `qty:1`, so the entry is exactly one unit. A
  placement giving `qty > 1` would mean two matchboxes sharing one
  `durability` object; that is already wrong wherever it came from and belongs
  to **#134**/#116, so it is noted rather than defended against.

**UI**

*The fire subsystem stops vanishing silently (#126)*

- Where "Light the stove" or the campfire button used to disappear once the
  last fire-starter was spent, a dim note now says why: `Nothing you're
  carrying will light it.` and `Nothing you're carrying will light a fire.`
  The campfire note is gated on `canBuildFire(room)` on purpose — a player
  with no kit and no firewood is not being denied a fire by a missing match.
  Both are functional UI text, held to clarity rather than to the game's
  descriptive tone, and both are retunable.
- `hereNote(text)` is a new helper beside `actionButton()` in RENDERING. The
  three existing inline-styled notes (locked door, sleep cooldown, not tired
  enough) and these two now share one definition instead of writing the same
  style literal five times.

*Item state in the list (#124)*

- An opened unit reads `Canned soup (Open) ×1 — 0.40 kg (Food)`; a sealed one
  is unchanged. The test is `it.sealed === false` strictly: `undefined` means
  the item was never a packaged thing and `true` means sealed, and only the
  opened state is marked. The suffix is a sibling `<span class="state">`
  outside the name element, so the clickable control's text stays exactly the
  item's name.
- The detail box keeps `Sealed` / `Opened`. The two sit in different
  grammatical positions — an adjective on a noun against a status line — and
  both read correctly; aligning them was not required and was not done.

*Markup and readability (#108)*

- `#mapZoomToggle` is a `<div>` and was a child of `<h3 class="map-heading">`,
  which is not legal — flow content inside a heading. The flex row is now a
  `.map-heading` wrapper around an `<h3>` and the toggle, with the heading's
  `margin:0 0 8px` moved onto the wrapper so the gap above the map is
  unchanged (measured at 8px before and after). `<h2>Menu <button…></h2>` is
  left alone: a button inside a heading is legal.
- `--ink-faint` `#666b72` → `#888e97` and `--danger` `#b3503f` → `#c76552`.
  Contrast ratios, recomputed from the shipped stylesheet:

  | foreground | on `--bg` | on `--panel` | on `--panel-2` |
  |---|---|---|---|
  | `--ink-faint` old `#666b72` | 3.47 | 3.12 | 2.90 |
  | `--ink-faint` new `#888e97` | 5.64 | 5.07 | 4.72 |
  | `--danger` old `#b3503f` | 3.67 | 3.29 | 3.07 |
  | `--danger` new `#c76552` | 4.80 | 4.31 | 4.02 |

  `#888e97` clears 4.5:1 on all three surfaces, which matters because
  `button.action .cost` puts `--ink-faint` on `--panel-2`. Both values are
  **retunable**, and the cost is real: `--ink-faint`'s relative luminance moves
  from 0.146 to 0.268 against `--ink-dim`'s 0.344, so the panel headings now
  sit noticeably closer to body text. The hierarchy, not the ratio alone, is
  what to judge a retune against.
- `opacity:.45` is gone from `button.action.blocked` and `button.mini.blocked`.
  Composited against the page it put a blocked label at **1.53:1** at the old
  `--danger` and **1.76:1** at the new one — effectively invisible either way,
  which is why nudging the token alone would not have fixed it. The disabled
  state is now colour and border only, landing the label at **4.02:1** on
  `--panel-2`. Blocked buttons read distinctly louder than they did.
- A 12px floor on every text token: `ul.itemlist .cat` and
  `#mapZoomToggle button` 10.5px → 12px; `.panel h2`, `.panel h2 .sub`,
  `.actions-group h2`, `.menu-section h3`, `button.mini` and `#gaitBar span`
  11px → 12px; `.tabs button` and `.logcount` 11.5px → 12px. All retunable.
  `.panel h2 .sub` is not in the handoff's table and is an addition — it
  re-declares 11px precisely so it does *not* inherit, so leaving it would have
  made it smaller than the heading containing it.
- `.itemname` is a real `<button>`, the last control in the game that wasn't.
  `ul.itemlist .meta b{ color:var(--ink); font-weight:600; }` no longer matched
  anything and was removed rather than left as a dead rule; `.itemname` carries
  that weight and colour itself, along with a button reset, a
  `padding:6px 2px` / `margin:-6px -2px` tap target and an accent-coloured
  `:active`. The padded box overlaps the row's own padding instead of adding to
  it — the item row measures 43px tall before and after.
- `viewBox="0 0 260 260"` is gone from `<svg id="mapSvg">`. It restated
  `MAP_ZOOM_RANGE.close.base` × `MAP_SPACING` in HTML where nothing would catch
  it drifting. `renderMap()` sets the attribute on first render, before
  anything is interactive; the map measured 423×423 with a correct viewBox on
  the first paint of an already-open side menu, so there is no flash of an
  unsized SVG.

**Changed / Reworked**

*Per-street map label widths (#113)*

- One label width — `"POPLAR ST"`'s — was reserved for all sixteen street
  names, over-reserving `"1ST ST"` by 63%. `mapSetLabelWidth(w)` is replaced by
  `mapLabelMetrics(w)`, a pure function returning `{ w, inset, tiers,
  clearance }` and `null` on a measurement it cannot trust. The four
  module-level `let`s (`mapLabelW`, `mapLabelInset`, `mapLabelTiers`,
  `mapLabelClearance`) are gone; `mapBindStreetLabels()` measures each street
  and stores its own metrics on the street, falling back to
  `MAP_LABEL_METRICS_FALLBACK` when its own measurement fails. The four readers
  — `mapLabelPositions()`, `mapClearCrossings()`, `mapLabelBox()` and
  `mapLabelHitsPlayer()` — take the metrics rather than closing over module
  state.
- **This is a visible densification, not a refactor.** Measured across all 176
  map nodes × 16 streets × 4 Wide spans = 11,264 street-views:

  | span | labels drawn before → after | views where the count rose | fell |
  |---|---|---|---|
  | 390 | 1,240 → 1,542 | 230 | 0 |
  | 520 | 2,468 → 3,171 | 677 | 0 |
  | 650 | 3,380 → 3,851 | 506 | 45 |
  | 780 | 4,340 → 4,989 | 657 | 44 |

  19.2% of street-views change label count (2,159 of 11,264), against #113's
  predicted 19%. Nine streets go from two names to three at span 390 and twelve
  do at span 520, exactly as #113 predicted.
- The 89 street-views that go 3 → 2 at the two widest spans are the converging
  case `mapClearCrossings()` already documents: a narrower name has a smaller
  inset, so an end position lands closer to a crossing, slides to the mid-block
  beside it, and two names converge on one mid-block — the one nearer the
  centre of the stretch keeps it. That is the existing rule applied to new
  inputs, not a new behaviour.
- The `mapLabelClearance` comment's `"POPLAR ST"` caveat is rewritten rather
  than carried over. Under per-street widths the limit is
  `MAP_SPACING - 2 * (MAP_LABEL_OFFSET + MAP_LABEL_CAP)` = 96 units and the
  widest north–south name is `"2ND ST"` at ~65, clear by ~31 units *by
  construction* rather than by the coincidence that the one over-wide name
  happens to run east–west.
- **#37's table is invalidated by this.** It counts labels drawn outside the
  viewBox per span, and its "Labels shown" column (1,240 / 2,468 / 3,380 /
  4,340) is this pass's *before* column. Its measurements need re-taking; a
  comment on #37 says so.

**Documentation**

- `MIN_DISPLAY_MIN`'s comment now carries the **decision** behind the display
  floor rather than a description of the gap (#110). **No code change.** The
  floor stays and the difference between the printed and the charged time is
  accepted rounding: a 50 m half-move costs 0.694 min at Walk and 0.500 at Jog
  and prints `(0:01)` for both, so two half-moves through a mid-block display 2
  minutes against ~1.39 spent. The comment names the three callers that can go
  sub-minute — the exit buttons via `exitMinutes()`, `estimateSleepMinutes()`,
  and `fmtDuration(room.fireMinutesLeft)` in `renderLocationPanel()` — and why
  the constant stays separate from `MIN_MOVE_MIN`.
- The four `validate*()` helpers' comments said "Call manually from the browser
  console", which the IIFE made impossible (#131). All four now name the real
  call — `ashfallDev.validateItemRegistry()`, `ashfallDev.validateLocations()`,
  `ashfallDev.validateRoomSchema()`, `ashfallDev.validateReachability()` — and
  one statement before the IIFE's closing `})();` puts them on
  `window.ashfallDev`, with a comment saying it is a read-only seam and nothing
  else belongs on it. No game behaviour changes: nothing reads
  `window.ashfallDev`, it is never serialized, and the four helpers are
  unchanged inside.
- The `MAP_LABEL_W_FALLBACK` comment no longer describes itself as "the width
  of the widest name on the map" — it is what one street falls back to when its
  own measurement fails.
- **Nothing was deferred.** Everything this pass cut was already an open issue
  and is listed under **Explicitly out of scope** below; no new issue was
  filed. One comment was added to #37, recording that this pass invalidated its
  table.

**Explicitly out of scope**

- **#134** — stacks whose units carry durability. A flashlight at 8% and one at
  100% still render identically; the `(Open)` suffix solves `sealed` and
  nothing else, by design. This is what #124 leaves behind.
- **#136** — `DOOR_LABELS` naming a door by its destination.
- **#78** — the accessibility pass. No ARIA, no roles, no live region on
  `#log`, no dialog semantics or focus trapping on `#sideMenu`, no `inert`, no
  `prefers-reduced-motion` guard. #108 was carved out of #78 precisely so none
  of that was needed here.
- **#29** — the log's 110px height and 50-entry cap; needs a play session first.
- **#37** — labels drawn outside the viewBox. Invalidated and noted, not fixed.
- **#116** — tool wear. #126 sets the precedent for what a spent tool does; it
  adds durability to nothing and no tool or weapon starts spending it.
- **#121, #111, #96, #15, #51** — untouched.

**Sections touched**

- The document `<style>` block and `<body>` markup (#108a, b, c, d). Neither is
  an ARCHITECTURE section.
- **CONFIG / CONSTANTS** — `MIN_DISPLAY_MIN`'s comment (#110), and the version
  string.
- **INVENTORY / ITEM SYSTEM** — `findFireStarter()` and `consumeMatchUse()`
  (#126). The only mechanics change in the pass.
- **RENDERING** — `renderItemList()` (#124, #108c), `renderHereActionsPanel()`
  (#126), the new `hereNote()` helper.
- **RENDERING / MAP** — the label metrics and their four readers (#113).
- **PERSISTENCE** — the four validator comments (#131).
- The IIFE's closing line — `window.ashfallDev` (#131).

Nothing in WORLD DATA, PLAYER STATE, WORLD INTERACTION, SURVIVAL / TIME
SIMULATION, STAMINA / FATIGUE, CRAFTING or EVENTS. FIRE / COOKING was read but
not edited: `doLightStove()` and `doBuildFire()` call `consumeMatchUse()` and
are unchanged.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html`, with every hunk mapped back to
  the section it falls in: 14 in the `<style>`/`<body>` block, 2 in CONFIG /
  CONSTANTS, 5 in INVENTORY / ITEM SYSTEM, 4 in PERSISTENCE, 31 in RENDERING
  (MAP included). Nothing in WORLD DATA. Syntax check via `node --check` on the
  extracted script.
- **#126**, in a browser: with a matchbox at 2 uses, lighting the stove twice
  removed it from the inventory on the second light, logged `The box of matches
  is spent.` and replaced the button with the note. Outdoors with a campfire kit
  and no fire-starter the campfire note appears; outdoors with neither kit nor
  firewood it correctly does not.
- **#124**: a stack of three sealed cans opened one unit and rendered
  `Canned soup ×2 — 0.80 kg (Food)` beside `Canned soup (Open) ×1 — 0.40 kg
  (Food)`; the detail box still read `Sealed` then `Opened`.
- **#108**: side-menu screenshots before and after — the map heading renders
  identically, and the heading-to-map gap measured 8px in both. The item row
  measured 43px tall in both, and the name control resolves to `BUTTON` and
  still opens the detail view. The map's first paint carried
  `viewBox="250 185 260 260"` at 423×423 — set by `renderMap()`, no flash. The
  contrast figures above were recomputed from the shipped stylesheet, and the
  two "old" values against `--bg` reproduce #108's stated 3.47 and 3.67.
- **#113**: the 11,264-street-view sweep above, driven by loading a save per
  map node at each Wide span. Its *before* column reproduces #37's own sweep
  (1,240 / 2,468 / 3,380 / 4,340) exactly, which is the check that it was
  measured the same way. A second sweep over the same 704 views (176 nodes × 4
  spans) took every visible name's rotated bounding box and found **0**
  name-on-name overlaps and **0** names touching the player marker.
- **#131**: `ashfallDev.validateItemRegistry()`, `validateLocations()`,
  `validateRoomSchema()` and `validateReachability()` all called from a real
  console against the shipped file — no temporary copy. The three pre-existing
  helpers report clean (0 problems each) and `validateReachability()` reports
  its 30 lines.
- **Save compatibility**: a save tagged `0.5.0` loaded against this build with
  `Progress loaded from this browser.` and no version-mismatch warning;
  `SAVE_KEY` resolved to `ashfall_save_v0.5`.
- No page errors and no console errors across every browser run.

**Notes / assumptions**

- The fencing comment on `window.ashfallDev` ships, per the handoff's
  recommendation: it is the only thing standing between a deliberate seam and
  the drawer every future helper gets hung on.
- `.state` is scoped as `ul.itemlist .state` rather than a bare `.state`, to
  match its neighbours `ul.itemlist .cat` and `ul.itemlist .meta` and to keep a
  very generic class name from applying page-wide. It is coloured
  `--ink-dim` — dimmer than the name, brighter than `.cat`.
- `.itemname`'s `6px 2px` padding with matching negative margin, and the
  accent-coloured `:active`, are judgment calls and retunable. Anything that
  changes the row height would be wrong; it does not.
- `mapSetLabelWidth` was renamed to `mapLabelMetrics`, per the handoff's
  recommendation — it no longer sets anything.
- `hereNote()` lives beside `actionButton()` in RENDERING, which is the same
  kind of helper.
- The two log/UI strings this pass adds — `The <fire-starter> is spent.` and
  the two `Nothing you're carrying will light …` notes — are retunable.

**Version**: `GAME_CONFIG.VERSION` `"0.5.2"` → `"0.5.3"`

---

## v0.5.2 — Reachable tools & content corrections

Implements: handoffs/reachable-tools-and-content-corrections.md

Implements #67, #77, #123 and #135 in full, per
`handoffs/reachable-tools-and-content-corrections.md`. A **pure WORLD DATA
pass** — no rule was added, changed, or read from a new field. Four findings
share one property, which is why they ship together: every one of them is
instance content. The sibling handoff
`handoffs/presentation-and-signal-pass.md` carries the same planning session's
mechanics half and is deliberately a separate pass, because `CLAUDE.md`'s bound
is that instance data never rides along with a mechanics change.

PATCH: no field was added to anything serialized, so `versionCompat()` does not
move and `SAVE_KEY` stays `ashfall_save_v0.5`. Existing browser saves keep
loading.

**New content**

*Second copies of the load-bearing tools (#67)*
- Five of the six tool tags that gate an action had exactly **one** reachable
  copy — the whole game's fire was one `box_of_matches` in the room the player
  wakes up in, and `fishing_rod` and `tackle_box`, which
  `renderHereActionsPanel()` requires **together**, sat in the same container.
  Each now has a second copy, hand-placed somewhere the first is not:
  `lighter` in the Corner Store `register`, `hand_axe` on `poplar6th`'s floor
  under the FIREWOOD sign, `bolt_cutters` in `onebee/toolcabinet`,
  `fishing_rod` on `mid_water_7_9`'s floor, `tackle_box` on `water9th`'s. The
  fishing pair is split across two rooms so no single loss removes fishing.
- Every placement went into an already-frozen container (`spawnRolled:true`), a
  `carContainer` (which has no pools), or a room floor. **No `spawnRolled` value
  changed anywhere in this pass**, so no live pool draw was killed — 24 of 80
  containers still roll, exactly as before.

*The screwdriver (#123)*
- `screwdriver` added to `ITEM_REGISTRY` — `Tool`, `0.15 kg`,
  `tags:["can-opening"]` and nothing else: a screwdriver is not a blade and not
  blunt. Placed beside `box_cutter`, which it is nearest in kind and weight.
- Hand-placed in the `cab` carContainer of the parked work truck on
  `mid_main_1_3`, beside the work gloves and thermos.
- Added to two pools: `tools_workshop` (after `box_cutter`) and `hardware_store`
  (after `plank`). **`hardware_store` is a dead pool (#133)** — no container
  that still rolls draws from it — so that entry spawns nothing today. It is
  written anyway so the pool is correct when #133 unfreezes it; it is not a live
  placement.

**Changed**

*`outside`'s description (#77)*
- The clause claiming the block to the west "feels like it goes on longer than
  the one to the east" is gone. `poplar2nd` is at `x:100` and `poplar3rd` at
  `x:300` with `outside` between them — both blocks are 100 m and cost the same
  at every gait, so the room was describing an asymmetry the grid does not have.
  236 characters to 153. The stoop sentence is verified correct against
  `mid_poplar_1_2`/`acorn_f0` and survives verbatim.

*The patio gate and the patio door (#77)*
- `onea_patio -> alley` was the world's only unexplained one-way exit. `alley`
  gains the return exit `{ to:"onea_patio", label:"Go through the gate",
  distanceM:6 }` — same-Location (both are `acorn_f0`), so `distanceM` is
  hand-authored and matches the reverse exit; no compass word, so
  `applyComputedDirections()` leaves it alone; not grid travel, so it renders in
  the **Here** panel.
- 1A's interior stays gated. A fifth door,
  `"1a-patio": { locked:true, sides:["onea_patio","onea"], building:"acorn" }`,
  is added to `makeDefaultDoors()`, and both existing exits between `onea` and
  `onea_patio` carry its `doorId`. `building:"acorn"` means `master_key` opens
  it, the same as `"1a"`; `acorn_apt_2a_key` does not.
- `DOOR_LABELS` gains `"1a-patio":"the patio"` — **not** `"1A"`.
  `doorsForRoom("onea")` now returns both doors and `getItemActions()`'s
  master-key branch pushes one action per door, so two doors sharing a label
  would render two identical `Unlock 1A` buttons. With "the patio" they read
  `Unlock the door to 1A` and `Unlock the door to the patio`.
- **The patio's storage bin becomes reachable on day one.** `storagebin1a` holds
  firewood ×3 and nails ×1 and was behind 1A's locked front door; it is now
  reachable through the alley — which is open from turn one — with no key and no
  tool. That is the point of opening the gate, but it is an early-game supply
  change and is recorded here rather than left to be discovered.
- **The patio is not a trap.** While `"1a-patio"` is locked, `getExitsForRoom()`
  drops the `onea` exit and leaves the alley gate, so a player who walks in
  through the gate can always walk back out.
- **1A's interior is no better protected and no worse.** Reaching it still needs
  `master_key` in `onebee/desk`, behind either door `"1b"` or the breakable
  `1b-alley` window.

*Movement labels (#135)*
- Every mid-block node has exactly two exits, and they were worded
  asymmetrically: `Head <dir> toward <Street>` one way, `Continue <dir> toward
  <Street>` the other. "Continue" encodes a direction of travel the room does
  not know — it reads as a lie to a player who just arrived from the other end.
  112 labels change `Continue` to `Head`; both exits of every mid-block now
  differ only in direction and destination. Nothing else in any label changed —
  not `to`, not `distanceM`, not `doorId`, not the compass word. Intersections,
  which use `Head <dir> on <Street>` and `Step into the block (<dir>)`, are
  untouched.

**Documentation**
- The `SPAWN_POOLS` block comment said "Every `chance` below is derived, not
  chosen [...] An ugly number here is the signal that nobody has picked it yet."
  That is now false, so it is rewritten: every `chance` **except the two
  `screwdriver` entries** is derived, those two are chosen and retunable, and an
  ugly six-decimal number still marks a derived one. The derivation note is kept
  in full — it is what makes the other 175 entries re-checkable.
- `DOOR_LABELS` gains a comment recording that it is read from **both** sides of
  a door, which is why the new door is labelled by its own name rather than its
  destination, and pointing at #136.
- **Nothing was deferred and no new issue was filed.** Everything this pass cut
  was already an open issue and is named under **Explicitly out of scope**
  below. Nothing new surfaced during implementation.

**UI**
- 112 mid-block movement buttons read "Head ..." instead of "Continue ...".
- `outside`'s description is two sentences instead of three.
- A "Go through the gate" button in the alley.
- On the patio: "The door to the patio is locked." without the master key, or an
  "Unlock the door to the patio" button with it.
- Six more items exist to be found.
- No panel, button or layout code changed.

**Notes / assumptions**
- `screwdriver`'s `unitWeight:0.15` is a judgment call, retunable: `can_opener`
  and `box_cutter` are 0.1, `kitchen_knife` 0.15.
- The two screwdriver `chance` values — `0.20` in `tools_workshop`, `0.23` in
  `hardware_store` — are **chosen, retunable balance values**, and the first
  chosen numbers in `SPAWN_POOLS`. `0.20` matches that pool's
  `box_cutter`/`metal_pipe`/`motor_oil` band; `0.23` matches `hardware_store`'s
  `plank`. The screwdriver postdates the v0.5.1 conversion and has no lottery
  weight to carry across, so there was nothing to derive them from.
- **Save compatibility.** `applyLoadedData()` assigns `world = data.world` and
  `doors = data.doors` wholesale and no backfill adds an exit or a door, so a
  v0.5.1 save gets neither the gate exit nor the `"1a-patio"` door. It stays
  internally consistent: no `doors["1a-patio"]` lookup can fire, because no exit
  in that save carries the id. New games and restarts get both. Verified, not
  assumed — see **Validation performed**.
- `onea`'s exit label to the patio was left as "Go to the patio". The door is
  signalled by the Here panel, not by the label.

**Explicitly out of scope**
- **#133** — the ten dead pools and the eleven remaining unreachable items. No
  `spawnRolled` value changed, `hardware_store` stays dead, and the screwdriver
  entry in it stays inert. Unfreezing containers is that issue's decision.
- **#126** — the spent fire-starter and the missing fire signal, in the sibling
  handoff. This pass adds a second fire-starter; it does not change what happens
  when one runs out.
- **#136** — `DOOR_LABELS` naming a door by its destination. The new door works
  around it with a label that reads acceptably from both sides; the fix is
  #136's. "The door to the patio is locked." read from the patio is a
  pre-existing wart, reproducible today by locking 2A from inside it.
- **#111** — gating vehicle forcing on `prying`. `prying` stays at 2
  hand-placed and gates nothing.
- Rebalancing any existing pool. No `chance`, `emptyChance`, `qtyMin` or
  `qtyMax` already in the file changed.
- New registry items beyond `screwdriver`; #7 lore, #8 map expansion, #6
  rooftops; #121, #116, #15, #51.

**Sections touched**
- **WORLD DATA only** — `ITEM_REGISTRY` (one entry), `SPAWN_POOLS` (two entries
  and the block comment), `makeDefaultDoors()` and `DOOR_LABELS` (one entry
  each), `buildAcornApartments()`, `buildPoplarSt()`, `buildCornerStore()`,
  `buildWaterSt()`, `buildMainSt()`, and every street builder for the 112
  labels. Plus `GAME_CONFIG.VERSION` in CONFIG / CONSTANTS.
- Untouched: PLAYER STATE, CORE UTILITIES, INVENTORY / ITEM SYSTEM, WORLD
  INTERACTION, SURVIVAL / TIME SIMULATION, STAMINA / FATIGUE, CRAFTING,
  FIRE / COOKING, PERSISTENCE, EVENTS, RENDERING.

**Validation performed**
- `git diff origin/main...HEAD -- ashfall.html` — 152 insertions, 132 deletions,
  of which 112 `+`/`-` pairs are the label rewrite and the rest are the changes
  listed above. Nothing outside WORLD DATA and the version string.
- `grep -c 'label:"Continue ' ashfall.html` → **0**;
  `grep -c 'label:"Head ' ashfall.html` → **451** (339 + 112), as the handoff's
  acceptance test specifies.
- Syntax check of the extracted script body with `node --check`.
- `validateReachability()` on a fresh world, run in headless Chromium, against
  the handoff's acceptance table — every row matches: dead pools **10**
  (unchanged), unreachable items **12 → 11** (`lighter` is placed),
  `fire-starter`/`fishing`/`tackle`/`chopping`/`cutting` **1 → 2** hand-placed
  each, `can-opening` **5 → 7**, `blunt` **10 → 11**, `prying` **2** and `heat`
  **1** unchanged. `validateItemRegistry()`, `validateLocations()` and
  `validateRoomSchema()` all still report clean, and the page loads with no
  console error.
- In-browser walkthrough: alley → gate → patio and back out; the patio door
  reads "The door to the patio is locked." without the master key and unlocks
  with it; `storagebin1a` opens from the alley with no key (firewood ×3, nails
  ×1); inside `onea` with the master key and both doors locked, the Here panel
  shows two distinct buttons — `Unlock the door to 1A` and `Unlock the door to
  the patio`.
- Save compatibility exercised, not asserted: a save written by the v0.5.1 build
  loads into this one under the same `ashfall_save_v0.5` key, logs "Progress
  loaded from this browser." with **no** version warning, and its `alley` has no
  gate exit, its `onea_patio` exits carry no `doorId`, and its `doors` holds the
  original four.

**Version**: `GAME_CONFIG.VERSION` `"0.5.1"` → `"0.5.2"`

---

## v0.5.1 — Spawn probability model

Implements: handoffs/spawn-probability-model.md

Implements #127 in full, per `handoffs/spawn-probability-model.md`. `SPAWN_POOLS`
was a weighted lottery: `emptyChance` skipped the roll, `rollCount` decided how
many picks to make, and each pick was an independent weighted draw over
`entries`. A `weight` is only meaningful beside its neighbours, so no entry
stated how likely that item was to be in a container, adding one entry silently
re-priced every other entry in every container drawing that pool, and two items'
likelihoods could not be set independently at any weights.

This pass replaces the lottery with an **independent per-entry chance**. Each
entry is rolled once, on its own, against its own `chance`. `emptyChance`
survives as its own gate ahead of the entries — a settled planning decision, and
the reason `chance` is conditional rather than absolute.

**This is not a no-behaviour-change pass.** P(appears) is preserved exactly for
every entry; quantity distribution is deliberately changed. See **Changed /
Reworked** below.

PATCH, despite #127's `tier-2` label mapping to MINOR. `SPAWN_POOLS` is a code
constant and no field was added to anything that is serialized — containers
still carry only `spawnPools`, `spawnRolled` and `lastRolledMinute` — so
`versionCompat()` does not move, `SAVE_KEY` stays `ashfall_save_v0.5`, and
existing browser saves keep loading. The mismatch is deliberate, not an error.

**Changed / Reworked**

*The roll (`doOpenContainer()`, WORLD INTERACTION)*
- `emptyChance` gates the pool as before; then every entry is walked once in
  declaration order and spawns if `Math.random() < entry.chance`. An entry can
  contribute **at most one stack per roll**, where the old model's
  with-replacement picks could select the same entry repeatedly and let
  `addToList()` merge them — the "three can openers in one drawer" case is gone.
- Items land in the container in the order the pool lists them.

*The intended behaviour change*
- Probability of appearance is preserved exactly, entry for entry. Quantity is
  not, and cannot be: the old model's duplicate picks have no counterpart in a
  model that rolls each entry once. `retail_stock_food` made 1.800 picks per
  roll but yielded 1.633 distinct items; that 0.167 of duplicate mass is what
  disappears.
- Expected item **units** fall **6.6%** across all 28 pools (32.831 → 30.657).
  The five largest drops: `retail_stock_food` 2.739 → 2.481, `hardware_store`
  2.363 → 2.163, `fuel_fire` 1.761 → 1.575, `kitchen_nonperishable` 2.513 →
  2.377, `warehouse_goods` 1.513 → 1.385. Across the 24 containers that actually
  roll, a whole run loses ~3.3 expected item units.
- The drop is **not compensated**, deliberately. Scaling the chances would break
  the P(appears) the conversion exists to preserve; raising `qtyMax` would
  hand-tune ~30 entries by feel. Both would destroy the re-derivability that
  makes this diff checkable, to protect numbers the balance pass overwrites.
- Large lucky stacks get shorter. That is the whole of the player-visible
  consequence, and it is statistical — no button, panel, label or log line
  changed.

*`SPAWN_POOLS` schema (WORLD DATA)*
- **Added** `chance` per entry — a number in `(0,1]`, the probability the entry
  appears *given the pool did not come up empty*, so
  `P(appears) = (1 - emptyChance) * chance`. Stated in the block comment,
  because `chance:0.55` in a pool with `emptyChance:0.25` is 41% of containers,
  not 55%.
- **Removed** `weight` (per entry) and `rollCount` (per pool). `emptyChance`,
  `qtyMin` and `qtyMax` keep their meanings exactly.
- All 28 pools converted; 175 entries. `chance` is the new rule's own schema
  field, so data and mechanic ship together under `CLAUDE.md`'s
  "definition data rides along with its mechanic" bound — the
  `restores`/`verb` + `doConsume()` precedent. No room, placement, description
  or map coordinate changed, which is the bound holding.

*The conversion*
- Every `chance` is **derived, not chosen**, generated programmatically from the
  pre-change pool definitions and written to six decimal places. For an entry of
  weight `w` in a pool whose weights sum to `W` and whose `rollCount` was
  `[a, b]`:

  ```
  chance = mean over k in {a, a+1, …, b} of [ 1 - (1 - w/W)^k ]
  ```

  the probability the entry is picked at least once in `k` with-replacement
  draws, averaged over the uniform `rollCount`. Multiplying by
  `(1 - emptyChance)` recovers the old unconditional probability exactly, which
  is why `emptyChance` was carried across rather than folded in. Where `a` is 0
  the `k = 0` term contributes 0 and is included in the mean, so the "rolled
  zero times" case is absorbed into `chance` and `emptyChance` stays as
  authored.
- The numbers read `0.245069`, not `0.25`, on purpose. An ugly derived number is
  the signal to the balance pass that nobody has chosen it yet. **No number in
  this diff is a balance decision** — that is what makes it checkable by
  re-derivation, and it is why rounding them to something tidier was not done.

**New**
- `validateReachability()` — a fourth dev-only console helper at the end of
  PERSISTENCE, sibling to `validateItemRegistry()`, `validateLocations()` and
  `validateRoomSchema()` and following their shape (returns an array, logs a
  summary, wired to nothing, runs nothing automatically). It walks a freshly
  built default world — never the live one, whose `spawnRolled` flags a save has
  already mutated — and reports three things plus one guard:
  1. **Dead pools** — a `SPAWN_POOLS` id no container with
     `spawnPools && !spawnRolled` draws from. Ten at v0.5.1: `medical_otc`,
     `medical_pharmacy`, `recreation`, `tools_general`, `retail_stock_food`,
     `retail_stock_general`, `hardware_store`, `outdoor_camping`, `trash`,
     `fuel_fire`.
  2. **Unreachable items** — an `ITEM_REGISTRY` id not hand-placed in the
     default world, not an entry in a live pool, not a `RECIPES`/`HEAT_RECIPES`
     output and not in `ACTION_GRANTED_ITEM_IDS`. Twelve at v0.5.1: `lighter`,
     `water_purification_tablets`, `compass`, `antibiotics`, `antiseptic_wipes`,
     `cough_syrup`, `vitamins`, `candy_bar`, `chewing_gum`, `paint_can`,
     `playing_cards`, `comic_book`.
  3. **Reachable tool count per tag in `REPORTED_TOOL_TAGS`** — how many
     hand-placed instances carry it and which live pools can yield one, so a
     content pass can see when a verb is down to one item. At v0.5.1:
     `fire-starter` 1, `fishing` 1, `tackle` 1 and `prying` 2, none of the four
     obtainable from any live pool; `chopping`, `cutting` and `heat` 1
     hand-placed each plus `tools_workshop`; `blunt` 10; `can-opening` 5.
  - It also flags any entry whose `chance` is not a finite number in `(0,1]` — an
    authoring guard the old integer `weight` could not have, since any positive
    integer was legal there.
  - The helper **reports** the current state; it does not assert the state is
    good. Ten dead pools and twelve unreachable items are the expected output at
    this version, and driving them to zero is the balance pass's job.
- `ACTION_GRANTED_ITEM_IDS` — `firewood`, `raw_fish`, `spare_batteries`. Items an
  action produces rather than a container holding them, written down beside the
  helper because each grant lives inside an action's body, not in any table the
  helper could walk.
- `REPORTED_TOOL_TAGS` — `fire-starter`, `fishing`, `tackle`, `chopping`,
  `cutting`, `blunt`, `can-opening`, `heat`, `prying`. Written down for the same
  reason. Both are named constants rather than inline literals so they stay
  visible and maintainable.

**Removed**
- `weightedPick()` (CORE UTILITIES). The new roll was its only caller, and a
  helper with no callers is vestigial surface — the call v0.4.14 already made.
  `randInt()` stays: the quantity draw still uses it.
- The comment above `pet_supplies` describing the per-entry weight convention
  ("commoner items 5-8, rarer or bulkier ones 1-3"). It documented a field that
  no longer exists, and the block comment now states that every `chance` is
  derived and retunable, which is what it was there to say.

**Documentation**
- The `SPAWN_POOLS` block comment rewritten: `weight`/`rollCount` replaced by
  `chance`, with the `P(appears) = (1 - emptyChance) * chance` relationship and
  the independence of entries stated. Its pointer to the v0.4.0 entry for "the
  full design" now points at this entry — v0.4.0's design is no longer the model
  in the file.
- The CONTAINER SCHEMA's `spawnRolled` paragraph corrected. It claimed the flag
  exists "so `doOpenContainer()` never overwrites" hand-placed contents, which is
  wrong about the mechanism: the roll calls `addToList()`, which appends. What
  the flag actually prevents is hand-placed contents being *topped up* with
  rolled loot.
- `randInt()`'s comment no longer names `weightedPick()`, and `doOpenContainer()`
  gained a paragraph stating the per-entry independence and the declaration-order
  guarantee.
- Filed #131 — the four dev-only validators all say "call manually from the
  browser console", and the script's IIFE makes that impossible; reaching them
  needs a devtools breakpoint inside the closure. Surfaced while verifying
  `validateReachability()` in a real browser, which had to be done against a
  temporary copy of the page with the four names hoisted onto `window`. Nothing
  else was deferred: no scope was cut, and the conversion turned up no pool with
  an empty `entries` array or an entry of weight 0.

**Open questions / decisions resolved**

The handoff left four narrow implementation calls and no design questions.

- **`weightedPick()` is deleted**, per the handoff's recommendation. See
  **Removed**.
- **The conversion script does not enter the repository.** It is scaffolding
  that runs once against the pre-change file. The formula above is the
  reproduction method: re-deriving all 175 numbers from the v0.5.0
  `SPAWN_POOLS` is how a reviewer checks this diff without trusting it.
- **The helper is named `validateReachability()`** — the `validate*` family the
  three existing helpers established, naming what it validates.
- **The three reports are one helper**, per the handoff's recommendation. They
  share the walk of the default world that works out which pools still roll;
  splitting them would do it three times.

**Notes / assumptions**
- **`prying` is counted although it gates nothing.** The handoff's constant
  description lists the tags `hasTool()`/`hasMatchUses()` are actually called
  with, which excludes `prying`; its acceptance figures include `prying` at 2.
  `prying` is counted, which is what makes the two agree. The reason is on its
  own merits: `renderHereActionsPanel()` records that forcing a vehicle was
  deliberately *not* gated on `prying` because one item carries it, and #111 is
  the standing question of whether to gate on it once that stops being true.
  Scarcity is exactly what this report measures, so the tag it already cost a
  decision belongs in it. The constant is named `REPORTED_TOOL_TAGS` rather than
  "gated tags" so the name does not claim more than is true.
- **The per-tag figure counts hand-placed instances, not distinct registry ids.**
  A crowbar placed in two rooms counts twice. That is what the handoff's
  acceptance numbers are (`blunt` 10 against 8 distinct ids), and it is the more
  useful figure: what a content pass wants to know is how many of the thing are
  out there, not how many kinds.
- The PATCH-against-`tier-2` call is the handoff's, restated in the prose above
  so the mismatch reads as deliberate.

**Explicitly out of scope**

Restated from the handoff so this needn't be opened to know what isn't here:

- **Re-authoring any pool's numbers for realism.** Every `chance` here is
  derived. The balance pass replaces them with chosen ones, and it is what
  closes #66 and #67.
- **Pool membership.** No container gained or lost a `spawnPools` entry and no
  pool gained or lost an item — matches did not enter `kitchen_tools`, however
  obviously they belong there.
- **Unfreezing containers (#66).** No `spawnRolled` value changed. The ten dead
  pools stay dead and the helper reports them; that is the intended output.
- **Second copies of single-source tools (#67).** A content decision for the
  balance pass.
- **Container kinds (#128)**, **respawn (#15)** — `lastRolledMinute` stays
  written-but-unread — **a shared roll core (#51)**, which this pass leaves as
  direct `Math.random()` calls the way the rest of the file does, and **new
  registry items**.
- **#116, #124, #126.** Adjacent to the reachability findings, none touched.

**Validation performed**
- `git diff origin/main...HEAD -- ashfall.html` — the whole of what changed, and
  it is confined to the four sections named below.
- **Syntax**: the `<script>` body extracted and passed through `node --check`.
- **The table re-derived.** All 175 entries recomputed from the pre-change
  `SPAWN_POOLS` with the formula above and compared against what shipped:
  every one matches to six decimal places, `emptyChance`/`qtyMin`/`qtyMax` are
  unchanged on every entry, entry order is unchanged in every pool, and no
  `weight` or `rollCount` survives anywhere. This is the proof that no balance
  decision entered.
- **Reference vectors**: `kitchen_tools`, `fuel_fire` and `police_evidence` (the
  degenerate `rollCount:[0,1]` case, where `chance` is just `w/W`) match the
  handoff's tables exactly, in both `chance` and `P(appears)`.
- **Both models simulated.** The roll body was lifted verbatim out of
  `ashfall.html` — the file's own text, not a transcription — and Monte-Carloed
  against the old arithmetic at 200,000 trials per pool: maximum P(appears)
  deviation 0.00382, consistent with sampling noise at that count. Re-run on the
  widest-deviating pool at 3,000,000 trials it falls to 0.00050 and keeps
  shrinking, confirming exact equivalence. Analytically, the only gap between
  the old and new P(appears) is the six-decimal rounding of `chance`, whose
  largest effect anywhere is 4.5 × 10⁻⁷.
- **The unit drop lands where predicted** — the five pools named above, and
  −6.6% overall, analytically and in simulation.
- **The helper run in a real browser** (headless Chromium, the shipped file) on a
  fresh world: ten dead pools, twelve unreachable items and the per-tag counts
  listed above, matching the handoff's acceptance figures exactly, with no
  illegal `chance`. `validateItemRegistry()`, `validateLocations()` and
  `validateRoomSchema()` still report clean.
- **All 24 rolling containers opened** in the browser: the roll produces items,
  no container came back with two stacks of the same item, and the page logged
  no errors.
- **Save compatibility**: a save written by the v0.5.0 build (`version: "0.5.0"`,
  key `ashfall_save_v0.5`) loads in the v0.5.1 build from the same origin,
  reporting "Progress loaded from this browser." with no version-mismatch
  warning. `localStorage` still carries `ashfall_save_v0.5`.

**Sections touched**
- **WORLD DATA** — `SPAWN_POOLS` (all 28 pools and its block comment) and the
  CONTAINER SCHEMA comment's `spawnRolled` paragraph.
- **WORLD INTERACTION** — `doOpenContainer()`.
- **CORE UTILITIES** — `weightedPick()` removed, `randInt()`'s comment rewritten.
- **PERSISTENCE** — the dev-helper block at the end.

Nothing in CONFIG/CONSTANTS beyond the version string, and nothing in PLAYER
STATE, INVENTORY / ITEM SYSTEM, SURVIVAL / TIME SIMULATION, STAMINA / FATIGUE,
CRAFTING, FIRE / COOKING, EVENTS, RENDERING or MAP.

**Version**: `GAME_CONFIG.VERSION` `"0.5.0"` → `"0.5.1"`

---

## v0.5.0 — Sealed food

Implements: handoffs/sealed-food.md

Implements #95 in full, per `handoffs/sealed-food.md`. The game shipped canned
food, a can opener, and no relationship between them — `can-opening` was a tag
nothing read, while five items were eaten straight out of `doConsume()` with no
tool required.

#95 frames the gap as a tool gate on eating: you may not eat a can without an
opener. Planning settled on a different shape, and that reframing is the whole
pass: opening is **an action that transforms the item**. A sealed can is not
food you cannot eat yet — it is not food. Open it and it becomes food. That
covers packaged food generally rather than cans specifically, and it leaves a
`sealed` flag behind that spoilage (#48) and rationing (#121) both want.

MINOR, and a real seam: `sealed` lands on item instances, which are serialized,
so `versionCompat()` goes `0.4` → `0.5` and `SAVE_KEY` rotates. Existing browser
saves stop auto-loading. No backfill is needed or wanted — every item's sealed
state comes from `ITEM_REGISTRY` on a fresh world.

**New**
- `doOpen(sourceKind, index)` — splits one unit off a sealed stack and opens it.
  `Canned soup ×3` becomes `×2` sealed plus `×1` opened, in the same list. Bails
  silently if the item is not sealed or if `opensWith` names a tag `hasTool()`
  cannot find. No capacity check, deliberately: the opened unit returns to the
  list the sealed one came from at the same `unitWeight`, so the list's total is
  unchanged. Points `detailItem` at the opened unit, so opening the *last* sealed
  unit doesn't close the detail view when the source stack is spliced out.
- The `can-opening` tag gets its first consumer. It is read through `hasTool()`,
  inventory-only — `hasTool()` was deliberately **not** widened to reach room
  containers, since reachability is #119's to define.

**New content**
- `sealed` / `opensWith` on nine items — `canned_soup`, `canned_beans`,
  `canned_corn`, `canned_tuna`, `canned_pet_food` and `baby_formula` open with
  `can-opening`; `cereal_box`, `peanut_butter` and `dry_pet_food` open by hand.
- `can-opening` added as a second tag to `kitchen_knife`, `box_cutter`,
  `combat_knife` and `hand_axe`, joining `can_opener`. Per `CLAUDE.md`'s rule
  that an item which should behave like an existing one gets the same tag, so
  the gate is one `hasTool()` call with no lookup table.
- `restores` on three items that were `category:"Food"` and inedible:
  `canned_pet_food` `{hunger:15}`, `baby_formula` `{hunger:18}`,
  `dry_pet_food` `{hunger:25}`, all `verb:"Eat"`. No `illnessChance` on any of
  them — they are sealed and safe, grim rather than spoiled.

This section and **New** appearing together is the both-buckets case the Project
Guide bounds: `sealed` and `opensWith` are the new mechanic's own definition, not
instance content. No room, container, exit, placement or description changed.

**Changed / Reworked**

*`addToList()`*
- The merge predicate gained `!!i.sealed === !!item.sealed`, so opened stacks
  merge with opened and sealed with sealed, and the two never merge. `!!` on both
  sides makes `undefined` and `false` the same state. Without this an opened can
  merges straight back into the stack it was split out of, which either opens all
  of them or loses the unit.
- The function now returns the entry the item ended up in — the stack it merged
  into, or the new one pushed. `doOpen()` is the only reader; no existing caller
  reads a return value, so this is additive.

*Actions on an inspected item*
- New rule, applied across `getItemActions()`: **an action offered on an item you
  are inspecting appears only if you can perform it.** Eat is absent while sealed,
  Open is absent when the required tool is not carried, and `Replace batteries` is
  now conditional on `countByTag("battery") >= 1` rather than pushed with
  `disabled: true`.
- Two sites that look like the same case are deliberately excluded, and now carry
  comments saying why: the keychain-blocked Take (both the detail view's family
  and the world panel's row button) stays disabled, because hiding it would read
  as "this item cannot be taken" when the truth is it cannot go *there*; and
  `renderCraftPanel()`'s recipe list stays a catalogue, because filtering it to
  what is craftable now would make crafting undiscoverable.

**Hardened**
- `doConsume()`'s guard is now `if(!it || !it.restores || it.sealed) return;` —
  defensive, matching the transfer block's convention that a function validates
  independently of whatever gate its caller applied. The Eat button is already
  withheld on a sealed item; this makes eating one unreachable rather than merely
  unoffered.

**UI**
- Sealed food shows an `Open` button and no Eat button; once opened, the reverse.
- `Open` is absent entirely when the required tool is not held, not greyed out.
- The detail box gained a `Sealed` / `Opened` line for packaged items, beside the
  existing `durability` line. Tested with `!== undefined` so an opened item reads
  "Opened" and an item that was never packaged reads nothing.
- `Replace batteries` disappears when no `battery`-tagged item is carried.
- Two new log lines, both collapsing on a repeat key of `"open:" + itemId`:
  `You work the lid off the <item>.` when `opensWith` is present, and
  `You break the seal on the <item>.` when it is not. Neither takes a CSS class —
  opening is neutral, so the line takes `fresh` in `log()`. "Break the seal"
  rather than "tear open" because the no-tool group spans a box, a bag and a jar,
  and only one of them tears.

**Documentation**
- ITEM DATA SCHEMA: `sealed` and `opensWith` documented; `can-opening` moved out
  of "Declared, with no consumer yet" into the list of tags read by a mechanic,
  with a note that it means "can get a can open", not "is a can opener". `prying`
  stays in the no-consumer list — a crowbar does not open a can, and #111 has
  already designated prying's future consumer.
- Issues filed for deferred work: #123 (a screwdriver, as a content-only addition
  that gets `can-opening` and changes nothing else) and #124 (the item list has
  nowhere to show item state, so a sealed and an opened can read identically —
  confirmed in play, and it will bite #121 too).

**Open questions / decisions resolved**

The handoff left two implementational choices open and no design questions.

- **Where `doOpen()` lives** — INVENTORY / ITEM SYSTEM, in the quantity-changing
  transfers sub-block beside `doConsume()`, taking the handoff's recommendation.
  It is a stack-splitting mutation, so it inherits that block's six safety rules;
  putting it in WORLD INTERACTION with the other `do*` actions would separate it
  from the rules it must follow.
- **How `doOpen()` finds the opened entry** — `addToList()` returns it, rather
  than `doOpen()` re-scanning `src.items`. The return is correct in both branches
  (the merged stack or the pushed copy), no existing caller reads one, and the
  alternative would have to re-derive a fact the function already knew.

**Notes / assumptions**
- The three new `restores` figures (15 / 18 / 25) have no prior convention behind
  them and are retunable. `canned_pet_food` is pegged just under `canned_tuna`'s
  20 at the same can size; `baby_formula` is dry powder and gets no thirst value,
  since fluids are #47/#52's ground; `dry_pet_food` is set on the assumption that
  one unit is the whole 1.5 kg bag — substantial, and far worse per kg than
  anything else.
- `dry_pet_food` carries a known awkwardness: without rationing, eating a whole
  bag is one click. That is #121's to fix, not this pass's.
- `hand_axe` carrying `can-opening` is a judgment call — an axe opens a can
  brutally, but it opens it. Retunable.
- Opening a can with a blade costs nothing: no reduced yield, no time, no injury
  risk. Settled during planning. The blade path gets its cost from #116 when tool
  wear ships.

**Explicitly out of scope**
- A screwdriver item (now #123) — a new registry entry plus pool placements is
  instance content, which may not ride along with a mechanics change.
- Tool wear (#116). Nothing here decrements anything.
- `rice_bag` and `coffee_grounds` are deliberately not sealed: neither has
  `restores`, so sealing them would yield an Open button producing something still
  inedible. They get sealed by #120.
- Individually-wrapped snacks are deliberately not sealed — `granola_bars`,
  `candy_bar`, `crackers`, `potato_chips`, `chewing_gum`. The wrapper is part of
  eating, and an Open click there buys a second click and no decision.
- The three spoiled Food items stay inedible. That is #48's ground.
- Rationing (#121) — Eat is still one whole unit. Spoilage (#48) — `sealed` is
  laid down here, but nothing decays. Reachable crafting (#119), two-stage
  cooking (#120), the propane torch (#96).

**Validation performed**
- `git diff origin/main...HEAD -- ashfall.html` reviewed in full: the diff is the
  version bump, the schema comment, 13 `ITEM_REGISTRY` lines, `addToList()`,
  `doConsume()`'s guard, the new `doOpen()`, four hunks in `getItemActions()`, and
  two in RENDERING. Nothing else.
- Syntax check: the inline script extracted and passed through `node --check`.
- Played headless in Chromium via Playwright, from a fresh world, asserting:
  Eat withheld and `Sealed` shown on `canned_soup` with no opener carried; `Open`
  absent until a `can-opening` item is picked up, then offered; opening splits
  `×3` into `×2` sealed and `×1` opened in the same container; the detail view
  follows the opened unit and offers Eat; the two stacks stay separate when both
  are taken into inventory; eating consumes the opened unit whole. Separately, on
  a scratch copy with a hand-placed `cereal_box ×1`: `Open` offered with no tool,
  the no-tool log line, and the detail view surviving the splice when the last
  sealed unit is opened. A save/load round-trip preserves `sealed:false`, and
  `localStorage` carries `ashfall_save_v0.5`. No page or console errors in either
  run.

**Sections touched**
- **WORLD DATA** — `ITEM_REGISTRY` and the ITEM DATA SCHEMA comment.
- **INVENTORY / ITEM SYSTEM** — `addToList()`; the quantity-changing transfers
  sub-block (`doConsume()`, new `doOpen()`); the item-detail action list
  sub-block (`getItemActions()`).
- **RENDERING** — `renderCraftPanel()`'s detail box and its recipe-list comment;
  `renderWorldItemsPanel()`'s row-button comment.

Nothing in PLAYER STATE, CORE UTILITIES, WORLD INTERACTION, SURVIVAL / TIME
SIMULATION, STAMINA / FATIGUE, CRAFTING, FIRE / COOKING, PERSISTENCE or MAP.

**Version**: `GAME_CONFIG.VERSION` `"0.4.18"` → `"0.5.0"`

---

## v0.4.18 — Map labels measured, not tabulated

Implements: handoffs/map-label-measurement.md

Implements #43 and #87 in full, per `handoffs/map-label-measurement.md`. Two
`tier-1` items that are one move: two hand-kept facts about rendered text, both
replaced by a measurement taken at bind time against the font the browser
actually resolved. The precedent is already in the file — v0.4.10 chose
`getComputedTextLength()` over a width table for Close's building labels, and
this applies that to the two places that still tabulated.

RENDERING only, MAP sub-block. No WORLD DATA, no mechanic, no new state: no
room, item, container, exit or description changed, `ITEM_REGISTRY` and
`BUILDINGS` were not edited, and `SAVE_KEY` does not rotate — `versionCompat()`
stays at `0.4` under a PATCH bump, so existing browser saves keep loading.

**New**
- `mapTextWidth(el, from, count)` — the one way this file measures rendered
  text. Wraps `getComputedTextLength()`, or `getSubStringLength()` when `from`
  is given, and returns `0` rather than throwing, so a measurement failure can
  never throw out of a bind and leave the map half-placed. Both label pools now
  read through it.
- `mapSetLabelWidth(w)` — recomputes `mapLabelW` and the three values derived
  from it from a single width. Rejects anything not finite or not `> 0` and
  leaves the previous width in place: a zero would collapse every tier to
  `hi - lo >= 0`, which is always true, and every street would silently jump to
  three names.
- `mapSplitName(el, name)` — chooses which space in a building name is the line
  break.
- `MAP_LABEL_W_FALLBACK` (`99.1`) — the last known good Chromium measurement of
  `"POPLAR ST"`, kept as the value the game starts with and the value it keeps
  if a measurement fails. It is no longer the live width.

**Removed**
- `MAP_LABEL_W`, `MAP_LABEL_INSET`, `MAP_LABEL_TIERS` and `MAP_LABEL_CLEARANCE`
  as module-level `const`s. Replaced by `mapLabelW`, `mapLabelInset`,
  `mapLabelTiers` and `mapLabelClearance`, all `let`s recomputed by
  `mapSetLabelWidth()`. They could not stay `const`s: they were evaluated at
  script-parse time, before any DOM node existed to measure.

**Changed / Reworked**

*Street-name width (#43)*
- `mapBindStreetLabels()` now measures each of the sixteen names once after
  setting `textContent` and calls `mapSetLabelWidth()` with the largest. One
  reading per street, not per pooled node — a street's three nodes carry the
  same string.
- Wide's pool ships `display:none` and a hidden SVG text node measures zero
  (re-probed on this build: `0` hidden, `98.163` shown). The node being read is
  shown before the reading and left shown; the snap that follows every bind sets
  `display` on every pooled node anyway. The pool is deliberately *not* shipped
  visible instead — that would paint sixteen names at the origin before the
  first position pass, which is the flash Close's build-order comment exists to
  avoid.
- All six derivation sites read the new binding. Every multiplier is unchanged:
  `6 *`, `3 *`, `1 *` for the tiers, `/ 2` for the inset and the clearance,
  `MAP_LABEL_EDGE_GAP` and `MAP_LABEL_OFFSET` as they were. Only the width they
  multiply changed source.
- `MAP_LABEL_CAP` stays the literal `12`. It is deliberately not measured:
  `getComputedTextLength()` gives width only, and `getBBox().height` reports the
  em box — `17.83` at this face, against a cap band nearer 11 — so there is no
  cheap correct reading to take. Its comment now says so.

**Fixed**
- **#87** — `renderMapClose()` broke a building name on its **first space**, so
  a three-word name rendered `["Main", "St Pharmacy"]` rather than the
  `["Main St", "Pharmacy"]` a reader expects. Root cause: the break was chosen
  at markup time, where the only thing available to choose it by is character
  position, and the layout reads width. The markup now ships the whole name in
  the first `<text>` node with the second empty, and `mapBindBuildingLabels()`
  chooses the break — the space that leaves the two sides closest in rendered
  width, measured with `getSubStringLength()` against the node that already
  carries the name, earliest space on an exact tie. `half` is computed after the
  split, since it reads the nodes.
- Line count stays decided at markup time — two nodes when the name contains a
  space, one when it does not — so nothing about the markup became
  measurement-dependent. If measurement fails every score is zero, the earliest
  space wins, and the split degrades to exactly the first-space rule it replaced.

**UI**
- **On the measuring machine, none — and that is proved below rather than
  asserted.** On other machines street-label placement may differ, correctly.
  `system-ui` is not one font: it resolves to Segoe UI, SF Pro, Roboto or
  Cantarell depending on where the page is opened, and those differ by more than
  the 3.66-unit band inside which placement is invariant. The trade this pass
  makes is deliberate and worth stating plainly: *before*, placement was
  identical on every machine and correct only on the one where `99.1` was
  measured; *after*, it is correct on every machine and identical on none. The
  literal had already drifted — `"POPLAR ST"` measures `98.163` here, a
  0.94-unit error sitting in the source.
- Building labels: all eleven current names split identically under the old and
  the new rule, so no marker changed.

**Validation performed**
- **Street-label sweep (#43).** Drove the shipped `mapLabelPositions()` /
  `mapClearCrossings()` / `mapLabelBox()` / `mapLabelHitsPlayer()` arithmetic —
  lifted verbatim out of `ashfall.html`, not reimplemented — over every view a
  player can occupy: 176 street/mid-block nodes × 4 Wide spans × 16 streets =
  **11,264 street-views**, under the old literal `99.1` and under this machine's
  measured maximum `98.16267395019531`. Result: **0 street-views with a
  different label count, 0 labels that moved**, 11,428 labels placed under each.
- **Neutrality band.** Re-derived on this build by bisecting the placement
  arithmetic: any single width in **[97.5000, 101.1572]** produces identical
  placement everywhere. Both `99.1` and the measured `98.163` fall inside it, so
  this machine is placement-neutral. (Planning found `[97.55, 101.15]`; the
  edges agree to the precision each scan resolved.)
- **The measurement is live, not incidental.** Since both widths place
  identically, a passing sweep alone would not prove the measured value reached
  the placement. Enlarging `.map-street-name` to 30px before the Wide bind makes
  the widest name measure `191.802`; the build then rendered **3** labels,
  matching the arithmetic at the measured width and not the **10** the `99.1`
  fallback predicts.
- **Building names (#87).** Ran the shipped `mapSplitName()` in-page against a
  real `.map-bldg-label` node: all **11** current `BUILDINGS` names split
  identically under the old and new rules. On three-word names the fix does what
  it claims — `"Main St Pharmacy"` goes `["Main", "St Pharmacy"]` →
  `["Main St", "Pharmacy"]` (widest line 71.13 → 55.68) and
  `"St Anne Medical Center"` goes `["St", "Anne Medical Center"]` →
  `["St Anne", "Medical Center"]` (116.75 → 84.54). `"Sunoco Gas Station"` and
  `"Riverside Freight Depot"` are unchanged by it.
- **Fallback guard (A5).** `mapSetLabelWidth()` called with `0`, `NaN`,
  `Infinity`, `-1`, `undefined` and `null` leaves the width where it was.
- **End to end.** Loaded the file in Chromium, opened the map in both modes and
  panned: no page errors, and Wide's rendered label transforms match the shipped
  arithmetic at the measured width exactly.
- Diff: `git diff origin/main...HEAD -- ashfall.html`.

**Open questions / decisions resolved**

The handoff left four narrow calls to implementation. All four took the
recommended option:
- **How the measured width reaches its six consumers** — option (a): module-level
  `let`s beside `mapZoomMode` / `mapZoomStep`, recomputed by one function at the
  end of `mapBindStreetLabels()`. Threading the width through
  `mapLabelPositions()` / `mapClearCrossings()` / `mapLabelBox()` would widen
  three signatures that run on every animation frame of a pan, for a value that
  is constant between binds. The factory form was left to #113 if it wants it.
- **Where the measurement lives inside bind** — folded into the existing loop,
  accumulating the maximum as it goes, rather than a separate first pass.
- **`getSubStringLength()` vs. re-reading each candidate** — `getSubStringLength()`:
  one layout per name rather than one per candidate split, and no text thrash.
- **Whether the fallback keeps the name `MAP_LABEL_W`** — it does not.
  `MAP_LABEL_W_FALLBACK` costs a rename at six sites and stops a reader taking
  the literal for the live width.

**Documentation**
- Comment rewrites at the three sites the handoff named: the label-size block
  (what is measured, what is not, and why `system-ui` makes a literal wrong),
  the crossing-clearance derivation (now inside `mapSetLabelWidth()` with the
  values it explains), and Close's build-order comment (line *count* is decided
  at markup time, the line *break* is not). `mapLabelBox()` gained a line saying
  its width is the widest name's and not this street's own — the crowding rule
  the tiers state, applied to one box.
- **Nothing was deferred by this pass, and no new issues were filed.** No
  seventh consumer of the width and no second measurement hazard turned up.
  #113 (per-street widths) was filed during the planning session, not by this
  pass, and this pass deliberately leaves it: its measured street table was
  re-derived here and matches to the hundredth of a unit.

**Explicitly out of scope**
- **#113 — per-street measured widths.** The deliberate remainder of #43. It
  moves 2,159 of 11,264 street-views and is a visible densification of the two
  lower Wide spans; this pass takes the **maximum** precisely so it can prove
  zero change. This pass unblocks it.
- **#37 — labels drawn outside the viewBox.** Same functions, different fault.
  Its measured table survives this pass intact, since placement does not change.
- **#108 — the duplicated `viewBox` literal** in the markup. Map-adjacent, but
  it belongs to that issue's pass.
- **Three-line building labels.** `MAP_BLDG_LINE_H` and the `first` / `lines`
  maths generalise, but a third line makes the block taller against
  `MAP_BLDG_LABEL_PAD` at the narrowest Close span. Two lines stay the maximum.
- Measuring `MAP_LABEL_CAP` — settled as "stays a literal", not deferred.
- Renaming any street or building, and any change to `MAP_STREETS`, `BUILDINGS`
  or `MAP_BUILDING_OFFSETS`.

**Notes / assumptions**
- The neutrality band is a property of this font and these sixteen names, not a
  guarantee. A future street name wider than the current maximum, or a face
  change, moves it — which is the point of measuring rather than tabulating.
- `MAP_LABEL_W_FALLBACK` is only reachable if a measurement fails or before the
  first Wide bind runs. The game opens in Close (`mapZoomMode = "close"`), so
  every session runs on the fallback until the player first switches to Wide —
  which is also the moment the first placement is computed, so nothing is
  displayed under it.
- `MAP_LABEL_CAP`'s `12` remains a chosen number against a measured cap band
  nearer 11, and stays retunable.

**Sections touched**
- RENDERING → MAP (In-Game Viewing Map) only. Nothing in WORLD DATA, PLAYER
  STATE, CORE UTILITIES, INVENTORY / ITEM SYSTEM, WORLD INTERACTION, SURVIVAL /
  TIME SIMULATION, CRAFTING, FIRE / COOKING or PERSISTENCE.

**Version**: `GAME_CONFIG.VERSION` `"0.4.17"` → `"0.4.18"`

---

## v0.4.17 — The mid-block toll, and three unstated facts

Implements: handoffs/mid-block-toll-and-three-unstated-facts.md

Implements #92, #97, #98 and #99 in full, per
`handoffs/mid-block-toll-and-three-unstated-facts.md`. Four `tier-1` items that
are one complaint applied four times: a fact the game acts on that the source
never states. A movement cost nobody chose, a log line promising a tool the gate
does not require, a save carrying UI state under a convention the file had
already decided the other way three times, and an exact arithmetic relationship
between three constants declared in two sections.

Mechanics and plumbing only. **No WORLD DATA was touched** — no room, item,
container, exit or description changed, and `ITEM_REGISTRY` was not edited.
#92 is the one player-facing balance change in the pass.

**New**
- `BLOCK_M` (`100`), in CONFIG / CONSTANTS beside `MIN_MOVE_MIN`. The grid pitch
  in metres — the same figure the `LOCATIONS` comment gives as "Block size
  100m" and that every street coordinate embodies, named where movement now
  reads it. It earns a name because a formula, not a table, depends on it.

**Changed / Reworked**

*Movement floor (#92)*
- `moveMinutes(distanceM, gridTravel)` takes a second argument and floors grid
  travel in proportion to distance — `MIN_MOVE_MIN * distanceM / BLOCK_M` —
  while everything else keeps the flat `MIN_MOVE_MIN`. `exitMinutes()`, its only
  caller, passes `isGridTravel(state.currentRoom, exit.to)`.
- The flat branch is load-bearing and is deliberately not collapsed into the
  proportional one: the 22 building entrances have `locationDistance() === 0`,
  so a proportional floor would floor them at zero and make them free. They are
  non-grid exits, so `isGridTravel()` already routes them to the flat branch;
  the rewritten `MIN_MOVE_MIN` comment now says so, because the two branches
  otherwise read as a redundancy waiting to be tidied away.
- Effect: a full block's two routes — one 100 m move, or two 50 m moves through
  the mid-block node — now cost exactly the same at every gait. Before, stopping
  mid-block cost +44% at Walk and +100% at Jog, and the mid-block nodes are
  where the trees, the parked cars, the building entrances and the loose floor
  items hang, so the toll fell on looking around. Nothing got more expensive:
  the only values that changed are the 448 fifty-metre grid exits, at Walk
  (1.000 → 0.694) and Jog (1.000 → 0.500). The 224 hundred-metre grid exits,
  all 102 non-grid exits, and all of Sneak are unchanged.

*Exertion constants (#99)*
- `CHOP_TREE_EXERTION` and `FISH_EXERTION` moved from the STAMINA / FATIGUE
  block to FIRE / COOKING, each immediately after its own duration.
  `CHOP_TREE_EXERTION` is now written as `CHOP_TREE_MIN * BASELINE_STAMINA_RATE`
  rather than the literal `30`, so the relationship survives a retune of either
  input — chopping is deliberately break-even on Stamina at full Energy, and the
  relationship is the rule, not the number. `FISH_EXERTION` stays a literal `8`:
  fishing's margin (20 minutes recovered against 8 spent, net +12) is the point,
  and the number is a balance value retunable on its own.
- Values are unchanged and the behaviour is bit-identical — `30 × 1 = 30`. The
  diff is the proof; see Validation.

**Removed**
- `invTab` and `worldTab` are gone from `makeDefaultState()` and therefore from
  the serialised save (#98). They are now module-level bindings beside
  `gameOver` and `detailItem`, the same call already made for `mapZoomMode` /
  `mapZoomStep`. All 33 references across INVENTORY / ITEM SYSTEM, WORLD
  INTERACTION and RENDERING dropped the `state.` prefix; the two that also read
  a slot out of `state` keep that lookup
  (`if(invTab !== "inventory" && !state[invTab])`). Both reset to their defaults
  in `doRestart()` and `applyLoadedData()`.
- The three task Exertion constants left the STAMINA / FATIGUE block — see
  **Function relocation** and **Changed / Reworked** above. Nothing replaced
  them there; the block's header comment now states that it owns only what
  Exertion *does*.

**Function relocation**
- `JOG_EXERTION_PER_MIN` moved from CONFIG / CONSTANTS to WORLD INTERACTION,
  immediately above `doMove()`, its only reader. With that move no task's
  Exertion is left orphaned in the STAMINA / FATIGUE block and the
  "declared beside the task" rule holds without exception. No function body
  moved between sections in this pass.

**UI**
- Mid-block travel is cheaper at Walk and Jog. The Move buttons' printed costs
  do not visibly change: `fmtDuration()` floors display at `MIN_DISPLAY_MIN`, so
  a sub-minute half-move still reads `(0:01)` — see **Explicitly out of scope**.
- Forcing a vehicle logs "You force the door. The lock gives with a crack."
  instead of "You pry the door open. …" (#97). The old line promised a crowbar
  the gate never required; "force" matches the button's own label. The second
  sentence is unchanged, and the gate stays `hasTool("blunt")`.
- The Inventory and Here panels open on Inventory and Floor after a load or a
  restart, rather than on whichever tab was showing when the game was saved.
  That is what "the save carries no record of the panels" means in practice, and
  it is what `mapZoomMode` already does.

**Documentation**
- `MIN_MOVE_MIN`'s comment rewritten: the two branches and why they differ, that
  the flat branch is what stops the 22 zero-distance entrances being free, and
  that the per-move flat floor is what produced the +44% / +100% toll — so the
  next reader sees the proportional form as chosen rather than stumbled into.
  The "over a 50 m block the two are identical" clause is deleted; this pass
  makes it false. The pace paragraph stays: a 100 m block at Jog still costs
  1.00 against Walk's 1.39.
- A comment above the vehicle gate in `renderHereActionsPanel()` records that
  any `blunt` item qualifies and that gating on `prying` was declined, since the
  crowbar alone carries it and early vehicle access would depend on one item.
  `prying` remains in `ITEM_REGISTRY` and remains in the ITEM DATA SCHEMA
  comment's "declared, with no consumer yet" group.
- Comments on `invTab` / `worldTab`, on both new FIRE / COOKING constants, on
  `JOG_EXERTION_PER_MIN`'s new home, and on the inert keys an old save leaves in
  `state`.
- Two issues filed for work this pass deferred: the sub-minute display gap in
  `fmtDuration()` / `MIN_DISPLAY_MIN` that #92 made worth an opinion (`tier-1`),
  and revisiting the `prying` gate once #66 makes the crowbar reachable outside
  `onebee/toolcabinet` and `hardware/toolwall` (`tier-2`, blocked on #66). Both
  were judged worth filing. The ARCHITECTURE comment needs no change: no section
  gains or loses a responsibility.

**Open questions / decisions resolved**
The handoff left three narrow implementation calls open. All three took the
recommended option:
- **`JOG_EXERTION_PER_MIN`'s home** — moved to WORLD INTERACTION above
  `doMove()`, rather than left in place with the block comment naming movement
  as an exception. Consistency won: after this pass the block holds no task
  constant at all.
- **Inert `invTab` / `worldTab` keys in loaded saves** — left in `state` rather
  than `delete`d in `applyLoadedData()`. They arrive through the
  `{ ...base, ...data.state }` spread, nothing reads them, and deleting two
  named keys would imply a schema check this load path deliberately does not
  perform: `validateLoadedWorld()` validates only the shapes that would throw.
  No behavioural difference either way.
- **`moveMinutes()`'s floor** — the ternary is inlined rather than extracted
  into a `moveFloorMinutes()` helper. There is exactly one caller, and the
  two-line body reads as well inline.

**Notes / assumptions**
- #92 is the pass's only balance change and is retunable. The proportional floor
  asserts that one 50 m half-move should cost half a block, which is a design
  position, not arithmetic; `MIN_MOVE_MIN` and `BLOCK_M` are both knobs on it.
  No `GAITS` speed, `MIN_MOVE_MIN`, `FISH_EXERTION`, `CHOP_TREE_MIN` or
  `BASELINE_STAMINA_RATE` value changed.
- #99's half is bit-identical: only where two constants live, and how one is
  written, changed.

**Explicitly out of scope**
- **The sub-minute display gap.** `fmtDuration()` floors display at
  `MIN_DISPLAY_MIN`, so a 50 m half-move at Jog now costs 0.500 and still reads
  `(0:01)` — the button claims twice what it charges. That is the display
  floor's own question; `MIN_DISPLAY_MIN` was split out from `MIN_MOVE_MIN`
  precisely so the two could move independently. Filed, not fixed.
- **Gating anything on `prying`.** #97 is settled as a prose fix; the tag stays
  unconsumed.
- **#66 / #67** — spawn reachability and the single-matchbox fire problem. #97's
  decision leans on them being open; neither is touched here.
- **#8** — map expansion. It adds roughly 300 rooms reached through mid-block
  nodes, which is why #92 was worth settling first, but no map work happens
  here.
- **#43, #87** — map label measurement and splitting. Unrelated.

**Explicitly NOT changed**
- No room, item, container, exit or description. No `LOCATIONS` entry, no
  `build*()` function, no `ITEM_REGISTRY` edit. No item-schema field, tag or
  category.
- No new state field anywhere — #98 *removes* two and adds none. `SAVE_KEY` does
  not rotate: a PATCH bump keeps `versionCompat()` at `0.4`, so existing browser
  saves keep loading, and an old save's `invTab` / `worldTab` survive the spread
  as inert keys nothing reads.
- `MIN_DISPLAY_MIN`, `fmtDuration()`, `GAITS`, `effectiveGait()`,
  `gaitLocked()`, `isGridTravel()` and `locationDistance()` are all untouched.
- `applyExertion()`, `recoveryStep()` and `runAwakeStep()` are untouched: this
  pass moved two Exertion figures and rewrote one as a product, and changed
  nothing about what Exertion does.
- Sneak, 100 m grid moves and every non-grid exit cost exactly what they cost
  before.

**Validation performed**
- **The exit census is unchanged**, re-run through `isGridTravel()` /
  `locationDistance()` under a Node harness that loads the script body behind a
  DOM stub: **448** grid exits at 50 m, **224** at 100 m, **102** non-grid, of
  which **22** are zero-distance, **774** total.
- `2 × moveMinutes(50, true) === moveMinutes(100, true)` holds exactly at all
  three gaits (Sneak 2.778, Walk 1.389, Jog 1.000), and
  `moveMinutes(0, false) === MIN_MOVE_MIN`. A real `doMove()` across a 50 m grid
  exit at Walk charges 0.694 — exactly what `exitMinutes()` priced it at — and a
  zero-distance building entrance still costs `MIN_MOVE_MIN`.
- `grep -c "state\.invTab\|state\.worldTab" ashfall.html` reports **0**, and a
  fresh `serializeGame()` contains neither key. A save carrying both keys and a
  non-default tab loads successfully, the two bindings reset to `"inventory"` /
  `"floor"`, and the inert keys are left in `state` untouched. `doRestart()`
  resets both.
- `CHOP_TREE_EXERTION` still evaluates to **30** and `FISH_EXERTION` to **8**. A
  chop at full Energy leaves Stamina exactly where it started; a fish leaves it
  **+12**. The "no behaviour change" claim for #99 is proven by
  `git diff origin/main...HEAD -- ashfall.html`, which shows the two constants
  moved and one rewritten as a product, and nothing else in the chop or fish
  paths.
- `validateItemRegistry()`, `validateLocations()` and `validateRoomSchema()` all
  report clean, and a fresh `makeDefaultWorld()` emits no
  `applyComputedDirections` warnings.

**Sections touched**
- **CONFIG / CONSTANTS** — `BLOCK_M` added; `MIN_MOVE_MIN` comment rewritten;
  `JOG_EXERTION_PER_MIN`, `CHOP_TREE_EXERTION` and `FISH_EXERTION` removed from
  the STAMINA / FATIGUE block, whose header comment narrows.
- **CORE UTILITIES** — `moveMinutes()`, `exitMinutes()`.
- **PLAYER STATE** — `makeDefaultState()` loses two fields; two module-level
  bindings added.
- **INVENTORY / ITEM SYSTEM** — `addToDestination()`, `doTake()`, `doStore()`,
  `doConsume()`, `doEquip()`, `doUnequip()`, `getItemActions()`: tab references
  only.
- **WORLD INTERACTION** — `doMove()`, `doOpenContainer()`, `doBreakCar()`;
  `JOG_EXERTION_PER_MIN`'s new home.
- **FIRE / COOKING** — `FISH_EXERTION` and `CHOP_TREE_EXERTION` arrive.
- **PERSISTENCE** — `applyLoadedData()` resets the two bindings.
- **RENDERING** — `renderInventoryPanel()`, `renderWorldItemsPanel()`,
  `renderHereActionsPanel()` (the gate comment only).

**Version**: `GAME_CONFIG.VERSION` `"0.4.16"` → `"0.4.17"`

---

## v0.4.16 — computeDirection()'s zero vector, and a build-time guard

Implements: handoffs/direction-zero-vector-guard.md

Implements #68 in full, per `handoffs/direction-zero-vector-guard.md`.
`computeDirection()` treated "no movement" as "pure vertical movement" and
answered `"down"` for it. Every building entrance in the game is such a pair —
a building floor's Location shares its street node's `(x,y)` *and* its `z`, by
design, because that sharing is what makes an entrance cost `MIN_MOVE_MIN`.
Nothing was visibly wrong only because none of those 22 exit labels happens to
contain a compass word: `applyComputedDirections()` rewrites a label only when
one is present, so it rewrote none of them. The next content pass to add
buildings with hand-written entrance labels would have had the perfectly
natural `"Head east into the pharmacy"` silently rewritten to `"Head down into
the pharmacy"` at world-build time, with no error and no warning.

WORLD DATA only, and no world data was edited — two functions changed, no room
definition.

**Fixed**
- `computeDirection()` returns `null` when `dx`, `dy` and `dz` are all zero,
  ahead of the vertical branch. Root cause: the vertical branch
  (`if(dx === 0 && dy === 0) return dz > 0 ? "up" : "down";`) was reached by the
  zero vector, where `dz > 0` is false, so "the same point" and "directly below"
  gave the same answer. The two are now distinct cases and are deliberately not
  collapsed — two Locations differing only in `z` still answer `"up"` /
  `"down"`, which #6 (rooftops) depends on.
- `applyComputedDirections()` skips substitution when `computeDirection()`
  returns `null`, leaving `exit.label` exactly as authored rather than splicing
  the string `"null"` into it. The `slice`/`slice` substitution is unchanged for
  every non-null direction.

**Hardened**
- `applyComputedDirections()` emits one `console.warn` when a label matches
  `COMPASS_WORD_RE` **and** its two Locations are the same point, naming the
  room, the destination, the authored label, both Location ids, and the fact
  that the label was left alone. The conjunction is the whole condition: a
  same-point exit with no compass word is the ordinary building entrance, all 22
  of them, and stays silent. A wrong compass word reads as plausible English, so
  the moment it is produced is the only moment it can be caught —
  `applyComputedDirections()` already walks every exit at build time and is the
  one place where both the same-point pair and the compass word are in hand.
  `validateLoadedWorld()` is the precedent for a check earning a real code path
  rather than sitting in the dev-helper block like `validateLocations()`.

**Open questions / decisions resolved**
- **`null` rather than a sentinel string** for the zero vector. `"here"` would
  also have worked and would have let `MOVE_DIRECTION_RANK` name it explicitly,
  but `moveDirectionRank()`'s existing `rank == null ? 4 : rank` already handles
  `null` with no edit, and a sentinel string invites a caller to print it.
- **The warning carries both the room ids and the Location ids.** The room ids
  say which exit to go and fix; the Location ids are what a reader needs to
  check `LOCATIONS` and confirm the two really do share a point.

**Documentation**
- The comment above `computeDirection()` now states the zero-vector case and why
  it is not the vertical case — a building floor shares its street node's `z`,
  while a rooftop or upper floor differs in it.
- The comment above `applyComputedDirections()` states the same-point skip and
  why only the compass-word case warns.
- Nothing was deferred, and no new issues were filed. The ARCHITECTURE comment
  needs no change: no section gains or loses a responsibility.

**Explicitly out of scope**
- **#87** — the building-name line split in `renderMapClose()`. Raised in #68's
  body as a second trap in the same area, split out during planning; it is
  RENDERING, not WORLD DATA, already filed, and carries its own before/after
  obligation.
- **Changing any exit label.** None was rewritten, and proving that is a
  validation step below.
- **Changing `LOCATIONS` so building floors stop sharing their street node's
  point.** The sharing is deliberate.
- **#75** (`MIN_MOVE_MIN` flattening the gait ladder) and **#8** itself, which
  this pass unblocks without implementing.

**Explicitly NOT changed**
- No exit label, no room definition, no `LOCATIONS` entry, no `build*()`
  function. No PLAYER STATE, ITEM DATA SCHEMA, room, container or exit schema
  field. `SAVE_KEY` does not rotate — a PATCH bump keeps `versionCompat()` at
  `0.4`, so existing browser saves keep loading.
- `moveDirectionRank()` and `MOVE_DIRECTION_RANK` are untouched. The existing
  `rank == null ? 4 : rank` is what absorbs the new `null`; it is unreached by a
  zero vector today, since grid travel requires both rooms to use their own id
  as their `locationId` and no two street nodes share a point.
- Genuine vertical movement, the four compass cases, and the `|dx| === |dy|`
  diagonal tie all answer exactly as before.

**Validation performed**
- **Every exit label in the built world is byte-identical before and after.**
  `makeDefaultWorld()` was built from `origin/main` and from this branch under a
  Node harness that loads the script body behind a DOM stub, and
  `{roomId, exit.to, exit.label}` was collected for all **774** exits across all
  **218** rooms and diffed. Zero differences — that is the proof of "no
  player-visible change", not an assertion of it.
- The before-state the handoff measured still holds: **22** cross-Location exits
  connect two Locations at the same point, and **zero** of them carry a compass
  word.
- `computeDirection()` truth table, 11 cases: zero vector → `null`; same
  `(x,y)` with greater `z` → `"up"`, with lesser `z` → `"down"`; the four
  compass cases; both diagonal ties; and `|dx| > |dy|`. All pass.
- `moveDirectionRank()` ranks a zero-vector pair **4** and still ranks north
  **0**.
- A fresh `makeDefaultWorld()` prints **zero** warnings.
- Injecting a test exit carrying a compass word between two Locations at the
  same point (`mid_poplar_1_2` → `hallway1`, labelled
  `"Head east into Acorn Apartments"`) prints **exactly one** warning and leaves
  the label unchanged, while the real same-point entrance beside it
  (`"Enter Acorn Apartments"`) stays silent and unedited. Done in a test-only
  shim; the shipped file was not edited for it.
- 17 assertions, 17 passing. No page errors on load.
- `git diff origin/main...HEAD -- ashfall.html` is the version bump plus four
  hunks spanning lines 1619–1661 — the two functions and their comments. No
  `build*()` function and no room definition appears in the diff.

**Sections touched**
- **WORLD DATA** only — `computeDirection()` and `applyComputedDirections()`,
  which live there per the ARCHITECTURE comment. Nothing in ACTIONS, SIMULATION,
  PERSISTENCE, CORE UTILITIES or RENDERING.

**Version**: `GAME_CONFIG.VERSION` `"0.4.15"` → `"0.4.16"`

---

## v0.4.15 — Rules written twice: the gait lock and the equipment round trip

Implements: handoffs/rules-written-twice.md

Implements #69 and #71 in full, per `handoffs/rules-written-twice.md`. Two
`tier-1` items that are one complaint: a fact the file already owns, restated at
a call site. #69 is a game rule — Fatigue 100 deciding what the player may do,
written as a bare `100` in two sections, neither of which owns Fatigue, and
enforced by a write to PLAYER STATE from inside RENDERING. #71 is an item
definition — `ITEM_REGISTRY` owns what a bag is, and `doUnequip()` rebuilt one by
hand. Both resolve the same way: name the fact once, give it a predicate or a
constructor, and have the call sites ask rather than restate.

One player-visible behavior change, in the gait lock. Everything else in this
pass is behavior-neutral.

**New**

- `FATIGUE_GAIT_LOCK` (`100`) in the STAMINA / FATIGUE SYSTEM CONSTANTS block:
  the Fatigue at which the pace bar locks to Sneak, previously a bare literal at
  two call sites. Value unchanged from v0.4.14.
- `gaitLocked()` and `effectiveGait()` in the STAMINA / FATIGUE SYSTEM section,
  beside `fatigueRecoveryAllowed()` — the predicate pattern that section already
  uses. `gaitLocked()` is `state.vitals.fatigue >= FATIGUE_GAIT_LOCK`;
  `effectiveGait()` returns `"sneak"` while locked and `state.gait` otherwise.
- `backfillSlotItemIds()` in PERSISTENCE, wired into `applyLoadedData()` beside
  the four existing backfills. Gives a loaded equipment slot its `itemId` by
  reverse name match against `ITEM_REGISTRY` — sound for the same reason
  `backfillItemIds()` is, registry names being unique. Skips slots that already
  carry one, and slots that match nothing: `state.keychain` is not a found item
  and has no registry entry, so it is correctly left alone.

**Changed / Reworked**

*The gait lock*

- `state.gait` is now the player's *preference* and is written in exactly one
  place: the pace-bar click handler, from the player's click. The lock no longer
  overwrites it. Previously, reaching Fatigue 100 coerced `state.gait` to
  `"sneak"` and the chosen pace was destroyed — the player had to re-pick it
  after recovering. Now the lock supplies an effective gait while it holds, and
  the preference lights up again by itself once Fatigue falls below
  `FATIGUE_GAIT_LOCK`. This is the pass's one player-visible change.
- `moveMinutes()` prices movement through `GAITS[effectiveGait()].speed` rather
  than `GAITS[state.gait].speed`. This is what removes a load-bearing call order
  nothing in the file documented: pricing and charging previously agreed only
  because `render()` happened to call `renderStatsPanel()` (which coerced the
  gait) before `renderMoveActionsPanel()` (which priced the exits). Both now
  derive from the same predicate whenever they run.
- `doMove()` charges the Jog surcharge on the effective gait, not the
  preference, so a locked player is not billed `JOG_EXERTION_PER_MIN` for a
  distance covered at Sneak speed. It is sampled *before* `advanceTime()`: that
  call runs recovery, which can drop Fatigue below the lock part-way through the
  move, and reading the gait afterwards would charge Jog exertion for a move
  already priced at Sneak. Net effect is identical to v0.4.14, which got the
  same answer only because the coercion had already run.

*The equipment round trip*

- `doEquip()` carries `itemId` onto the slot object it builds. `doUnequip()`
  reconstructs the item through `itemFromRegistry({ id: slot.itemId, qty:1 })`
  and attaches `contents`, deleting the hand-written
  `category`/`slotType`/`capacityKg` triple for all five equippable bags. The
  hand-built object survives as a commented fallback reached by exactly two
  things — `state.keychain`, which has no registry entry by design, and a slot
  from a save written before this pass and not yet repaired by
  `backfillSlotItemIds()`.

**Fixed**

- Round-tripping an equipped bag through `doUnequip()` dropped its `itemId`,
  because the item was hand-built rather than taken from the registry. Observable
  effect: `countInPools("worn_backpack")` returned 0 while the bag sat in
  inventory. Latent rather than live — nothing reads a bag's id today, and
  `backfillItemIds()` restored it on the next save/load — but the gap is now
  closed at the source rather than repaired after the fact.
- `addToList()` copied with `{ ...item }`, a shallow spread, so a new stack entry
  shared its source's `tags` array and `durability` object. Behavior-neutral
  today: `getItemActions()`'s `splittable` gate is
  `STACKABLE.has(it.category) && !it.durability`, so a durability-bearing stack
  never splits and the source is always spliced out whole — the two stackable
  items that carry durability (`box_of_matches`, `lighter`) are excluded by that
  guard. The guard lives in a different function from the copy, which is why the
  copy is now `JSON.parse(JSON.stringify(item))` — matching
  `itemFromRegistry()`, so both item-creating paths agree — rather than relying
  on it. The `delete copy._uid` comment is extended, not replaced: it documents
  a different hazard and is still the only thing that does.

**UI**

- The pace bar. While Fatigue is at `FATIGUE_GAIT_LOCK` it disables everything
  but Sneak and shows Sneak lit, exactly as before. The difference is
  afterwards: the player's previously chosen pace becomes active again on its
  own instead of the bar being left on Sneak with the choice discarded.
- The click handler no longer toggles `active` by hand before calling
  `render()`. `renderStatsPanel()` sets it from `effectiveGait()`, so one place
  decides which button is lit instead of two.
- Nothing else moves: the Move panel's durations, the equipment tabs and the
  inventory rows render as before.

**Documentation**

- `renderStatsPanel()` no longer writes to PLAYER STATE during a render,
  restoring the ARCHITECTURE comment's "UI/RENDERING ... should never contain
  rules" for the gait lock. Two more such writes remain — `state.invTab` in
  `renderInventoryPanel()` and `state.worldTab` in `renderWorldItemsPanel()` —
  and are deliberately untouched here; they are UI-state normalisation rather
  than game rules, and are #98's subject.
- Nothing further was deferred. Both items this pass sets aside were filed
  during the planning session that wrote the handoff — **#98** (`invTab` /
  `worldTab` as PLAYER STATE) and **#99** (the chop break-even knife-edge) — and
  no new issues surfaced during implementation.

**Open questions / decisions resolved**

- *Where `gaitLocked()` and `effectiveGait()` live.* Placed in the STAMINA /
  FATIGUE SYSTEM section beside `fatigueRecoveryAllowed()`, the handoff's
  recommendation, over CORE UTILITIES beside `moveMinutes()`: the rule is about
  Fatigue, so it belongs where a reader retuning `FATIGUE_GAIT_LOCK` will look.
- *One function or two.* Kept as two, the handoff's recommendation. They answer
  different questions — `gaitLocked()` is what the click guard and the
  button-disabling want, `effectiveGait()` is what pricing wants — and
  collapsing them would make one call site derive the other's answer.
- *Sampling the gait in `doMove()`.* Not a question the handoff raised; it
  surfaced under test. The handoff specified `if(effectiveGait() === "fast")` in
  place of the old check, which left the read after `advanceTime()` and so
  charged Jog exertion whenever recovery lifted the lock mid-move — the exact
  bug the handoff's rule 1 warned the fix could introduce, reached by a
  different route. Resolved by sampling `effectiveGait()` into a local before
  `advanceTime()`, which also matches v0.4.14's behavior exactly.

**Data / schema changes**

- No new PLAYER STATE field. `state[slotType]` gains an `itemId` property on the
  existing slot object, written by `doEquip()` and backfilled on load. The ITEM
  DATA SCHEMA is unchanged and WORLD DATA is untouched.
- Save format is additive and backward-compatible: old saves load,
  `backfillSlotItemIds()` and `doUnequip()`'s fallback both handle a slot
  without `itemId`, and `SAVE_KEY` stays `ashfall_save_v0.4`. Hence PATCH.
- `state.gait` keeps its shape and meaning. A v0.4.14 save written while locked
  holds `"sneak"` — the coercion had already destroyed the preference before the
  save — so it loads as a Sneak preference rather than the pace the player
  originally chose. There is nothing to recover; noted so the difference is not
  silent.

**Explicitly out of scope**

- #71's option 3, the un-projected slot (`state[slotType]` holding the item
  object rather than a projection). It changes the persisted shape of every
  slot, making it MINOR.
- Giving `state.keychain` an `ITEM_REGISTRY` entry to avoid the fallback branch.
  The comment at `CONTAINER_SLOTS` records a deliberate decision that the
  keychain is not a found item, and an entry would make it placeable and
  spawnable.
- `state.invTab` / `state.worldTab` as PLAYER STATE — #98. Both render-time
  writes are left exactly as they are.
- The chop break-even knife-edge — #99.
- Showing Fatigue anywhere in the UI. It remains invisible, which is why the
  lock still arrives without warning; that is #49's job.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` reviewed in full: 83 insertions,
  17 deletions, all within the eight sections listed below and no others.
- Syntax check on the extracted script (`node --check`), clean.
- Driven in headless Chromium against an instrumented copy of the build (the
  instrumentation is scratch, not shipped). The gait lock: at Fatigue 100,
  `gaitLocked()` holds, `effectiveGait()` returns `"sneak"`, `state.gait`
  retains the player's `"fast"`, `moveMinutes()` prices at Sneak speed, the bar
  shows Sneak lit with Walk and Jog disabled, a click on a disabled pace is
  refused, and `doMove()` spends no Stamina; below 100 the `"fast"` preference
  is lit again with nothing disabled and no re-pick, and the Jog surcharge is
  charged as before. `renderStatsPanel()` leaves `state.gait` untouched.
- **Call-order fix proved, not asserted.** Exit durations were priced before
  `renderStatsPanel()`, after it, and with the lock toggled between — identical
  to six decimal places across all three, on a room whose exits price above
  `MIN_MOVE_MIN` so the floor could not mask a difference.
  `renderStatsPanel()` and `renderMoveActionsPanel()` may now run in either
  order with the same result.
- All five equippable bags (`worn_backpack`, `duffel_bag`, `purse`,
  `fanny_pack`, `tote_bag`) round-tripped with contents through equip → store →
  unequip → re-equip: each came back carrying its `itemId`, with `category`,
  `slotType`, `capacityKg`, `unitWeight` and `name` matching its registry entry,
  contents byte-identical, no stale `_uid`, and `countInPools(id)` returning 1
  while stowed.
- `state.keychain` round-tripped through the fallback branch: unequips as a
  `Container` with `slotType:"keychain"` and no `itemId`, contents intact, tab
  reset, and re-equips.
- A genuine v0.4.13 save — generated by running the v0.4.13 build and confirming
  its slot object carried only `name`/`unitWeight`/`capacityKg`/`items` — loaded
  into this build: `backfillSlotItemIds()` assigned `worn_backpack`, the
  keychain was left without one, bag contents and the gait preference survived,
  and the repaired slot then took the registry branch on unequip.
- `addToList()`: a stackable durability-bearing item (`box_of_matches`) copied
  through it no longer shares its source's `durability` object or `tags` array,
  mutating the copy leaves the source unchanged, `_uid` is still stripped, and
  stackables still merge. A `_uid` uniqueness sweep across every inventory pool,
  floor and container after a partial `doTake()` found no duplicates.
- Current-version save/load round trip, a full `render()` under both lock
  states, and a click-through of every enabled button on screen — no page errors
  and no console errors in any run.

**Sections touched**

CONFIG / CONSTANTS (`FATIGUE_GAIT_LOCK`), CORE UTILITIES (`moveMinutes`),
INVENTORY / ITEM SYSTEM (`addToList`, `doEquip`, `doUnequip`), WORLD INTERACTION
(`doMove`), SURVIVAL / TIME SIMULATION → STAMINA / FATIGUE (`gaitLocked`,
`effectiveGait`), PERSISTENCE (`backfillSlotItemIds`, `applyLoadedData`), EVENTS
/ UI HELPERS (the pace-bar click handler), RENDERING (`renderStatsPanel`). No
WORLD DATA — this is a mechanics-and-rendering pass.

**Notes / assumptions**

- `FATIGUE_GAIT_LOCK` is named, not retuned: `100` is v0.4.14's value and the
  top of the Fatigue scale. It is now a single knob should a future pass want
  the lock to bite earlier.
- The lock's *effect* is unchanged — Sneak only, at Fatigue 100. Only the
  preference's survival is new. A player who never reaches Fatigue 100 sees no
  difference at all.

**Version**: `GAME_CONFIG.VERSION` `"0.4.14"` → `"0.4.15"`

---

## v0.4.14 — Vestigial surface, and the rope duplicate

Implements: handoffs/vestigial-surface-and-the-rope-duplicate.md

Implements #70 and #76 in full, per
`handoffs/vestigial-surface-and-the-rope-duplicate.md`. Two `tier-1` items that
are one complaint applied to two layers: surface that reads as live and is not.
#70 is code and constants — an unreachable action path, a `STACKABLE` member
matching no item, capability tags nothing consumes. #76 is content — one object
under two registry ids, which the stacking rule then refuses to merge. A
deletion pass throughout: no mechanic changes, no new state, `SAVE_KEY` stays
`ashfall_save_v0.4` and existing browser saves keep loading.

Some of this is deliberately *kept* and annotated rather than deleted. Keeping
a thing is a decision this pass made, not an omission — the comment is what
stops it being re-filed.

**Removed**

- **`doTryDoor()` and the `room.lockedDoors` block in
  `renderHereActionsPanel()`** — an unreachable path. `room.lockedDoors` was
  read in exactly one place and set in none: no room in any of the 26
  `build*()` functions defines it, and it is absent from the ROOM SCHEMA
  comment. `doTryDoor()` was reachable only from that block, and its
  `label.replace("Try the door", …)` expected a label shape no data produces.
  The surviving locked-door implementation — the `doors` table plus
  `findKeyForDoor()`, rendered a few lines below — is the replacement, and was
  already doing the whole job.
- **`"Ammunition"` from `STACKABLE`**, leaving
  `new Set(["Food","Medical","Materials"])`. Zero registry entries carry
  `category:"Ammunition"`; the ten categories actually present are Clothing,
  Container, Electronics, Food, Key, Literature, Materials, Medical, Misc and
  Tool. A set member matching no item's category can never be consulted, so
  this changes no behavior. The hint it carried — that ammunition was once
  considered — is redundant with the registry's own
  `// Self-defense (firearms deliberately excluded)` comment, which says it
  more clearly.
- **The `length_of_rope` registry entry** — see **Changed / Reworked** below.

**Changed / Reworked**

*The rope merge (content)*

- `length_of_rope` (`"Length of rope"`) and `rope` (`"Rope"`) were one object
  under two ids — identical `category:"Materials"` and `unitWeight:1.5`,
  differing only in display string, with no mechanic referencing either id: no
  recipe input, no tag, no world check. Because `Materials` is in `STACKABLE`
  and `addToList()` merges on `itemId`, a player holding both carried two
  inventory rows for one object, and a container drawing `tools_general` twice
  could roll one of each.
- `rope` is the survivor — three placements to `length_of_rope`'s one, two
  spawn pools to its one. Three edits: the registry entry deleted, the
  `balcony`/`storagebin` placement repointed from `{ id:"length_of_rope" }` to
  `{ id:"rope" }`, and `tools_general`'s two entries collapsed into one at
  weight `11`. `hardware_store`'s `rope` at weight `7` and `hardware`/`bins`'
  hand placement of `qty:2` are untouched.

**Documentation**

- **The ITEM DATA SCHEMA `tags` entry rewritten.** It listed ten tags and the
  registry carries eleven — `can-opening`, on `can_opener`, was never listed.
  An incomplete specification of the tag system is exactly what that omission
  cost, so the list is now complete and split by state: read by a mechanic
  today (`blunt`, `cutting`, `chopping`, `fishing`, `tackle`, `fire-starter`,
  `battery`), and declared with no consumer yet (`blade`, `prying`,
  `can-opening`, `heat`). The tag *set* is unchanged — no tag was added or
  removed from any item. All four unconsumed tags stay in `ITEM_REGISTRY`:
  they are content-facing, they are how a future item says "I behave like a
  knife", and deleting then re-adding them is churn paid in registry edits.
- `heat` is documented into the second group with its reason stated:
  `roomHasHeat()` exists and reads it, but `roomHasHeat()`'s only caller is
  `canCraft()`'s `needsHeat` branch, which no recipe sets. It is reachable code
  on an unreachable path.
- **`canCraft()`'s two unset gates annotated.** `recipe.tool` and
  `recipe.needsHeat` are gated and printed by `renderCraftPanel()`'s "needs …"
  string, and neither `RECIPES` entry (`bandage`, `campfire_kit`) sets either;
  `HEAT_RECIPES` does not route through `canCraft()` at all. Both branches stay
  — `canCraft()` reads as a small complete crafting gate *because* they are
  there, and deleting them means the next recipe needing a tool re-adds them.
  The comment says that, so the next reader does not re-file #70.
- **`backfillContainerFields()`'s second `scan()` annotated.** `scan()` returns
  early unless the *default* container has `spawnPools`; three rooms carry
  `carContainers` (`poplar2nd`, `mid_poplar_1_2`, `mid_main_1_3`) and none of
  their containers has `spawnPools`, so the call can copy nothing today. It
  stays — it costs one line and covers a car container gaining `spawnPools`
  later — and the comment records that, so the next audit does not re-derive it.
- Per the handoff's comment-wording constraint, none of the three new comments
  names an issue number, a version or a handoff path: each explains itself as a
  rule.
- **Nothing further was deferred.** The three items this pass defers — #95, #96
  and #97 — were filed by the planning session that wrote the handoff, and
  implementation surfaced nothing new to file.

**Open questions / decisions resolved**

- **No `validateRegistryDuplicates()` dev helper was added**, and the
  measurement behind that is recorded so it is not re-proposed. Signature =
  the registry entry with `name` removed: across 154 entries that yields 28
  colliding groups covering 82 entries, 53% of the registry, with
  `rope`/`length_of_rope` landing in a six-member group beside `plank`,
  `spare_parts_box`, `spare_machine_parts` and `paint_can`, none of which is a
  duplicate of anything. Narrowing to "same signature *and* both in one spawn
  pool" still returns 13 groups, including every medical item that weighs
  0.05 kg. `canned_corn` and `canned_tuna` are identical in every modelled
  property and are *not* a duplicate — corn and tuna are two foods a later
  spoilage or nutrition layer would separate. What made the rope pair a
  duplicate is that the two names denote the same object, which is semantic and
  invisible to any signature comparison.
- The handoff left nothing else open; every keep/delete call was settled in
  planning and taken as written.

**Notes / assumptions**

- **`tools_general`'s rope weight of `11` is retunable**, and was chosen to be
  provably rate-neutral rather than balanced. The pool's entry weights totalled
  8+6+6+5+5+2 = 32, of which rope in either form was 6+5 = 11. After the merge
  the total is 8+6+11+5+2 = 32 and rope is 11. Any rope, before or after, is
  11/32 of a pick. The status quo it preserves was itself an accident of two
  ids existing, so 11 is a starting point, not a considered balance number.
- **Save compatibility, stated rather than left to be discovered:** an existing
  save holding a `length_of_rope` item keeps working. Items carry their own
  `name`, `category` and `unitWeight` in the save, and `backfillItemIds()` only
  *adds* a missing `itemId` — it never rewrites one. The orphaned item simply
  stops stacking with `rope`, which is exactly the status quo. No backfill was
  added and none is wanted.
- This pass touches both WORLD DATA and non-content sections, which is not the
  both-buckets case the Project Guide bounds — nothing here is a new mechanic
  shipping with its defining data. It is a deletion pass that happens to delete
  in two places, so there is no **New content** section to pair with a **New**
  one.

**UI**

- The one visible change: the `balcony` storage bin's rope now displays as
  "Rope" rather than "Length of rope", and a second inventory row that could
  previously appear for the same object no longer can. Everything else is
  invisible by construction — `room.lockedDoors` was never set so its button
  never rendered, `Ammunition` matched no item's category, and the tag and
  recipe-gate changes are comments.

**Explicitly out of scope**

- **Wiring `can-opening` to a consumer — #95.** The one dead tag whose absence
  is player-visible. A genuine new mechanic, `tier-2`. This pass keeps the tag
  in place precisely so #95 has something to consume.
- **Making `heat` live — #96.** Gating the Cook action on `roomHasHeat()`
  rather than `room.heatActive` would make `propane_torch` functional. A new
  mechanic, not cleanup.
- **Retagging `doBreakCar()` — #97.** It is gated on `hasTool("blunt")` while
  its log line reads "You pry the door open", and `prying` sits unconsumed on
  the crowbar. Retagging narrows the tool set from eight items to one, which is
  a balance change and does not belong in a deletion pass.
- **Deleting `recipe.tool` / `needsHeat`** — considered and rejected above.
- **The `canned_corn`/`canned_tuna` signature collision** — not a duplicate, no
  action.

**Explicitly NOT changed**

- No balance constant, threshold or formula, other than the `tools_general`
  rope weight documented above as rate-neutral.
- No save format change. `SAVE_KEY` still derives to `ashfall_save_v0.4`; no
  persistent state field was added, removed or renamed, and no backfill was
  added.
- No mechanic. `hasTool()`, `countByTag()`, `consumeByTag()`,
  `findFireStarter()` and `roomHasHeat()` are untouched, as are every
  `breakTag` call site and the `doors`/`findKeyForDoor()` locked-door path that
  survives the `doTryDoor()` deletion.
- No room, exit, container, door, window or description. The only WORLD DATA
  touched is one registry entry deleted, one placement repointed and one spawn
  pool edited.
- No tag added to or removed from any item; no function moved between sections.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` reviewed in full: seven hunks,
  and nothing outside the six scoped edits plus the version bump. The two
  deletions remove only the lines named above; the three annotations add
  comment lines and no statements.
- Residue check — `grep -n "length_of_rope\|lockedDoors\|doTryDoor\|Ammunition" ashfall.html`
  returns nothing, confirming no dangling reference to either deleted path or
  the removed registry id.
- Tag audit — every `tags:[…]` value in `ITEM_REGISTRY` enumerated and counted:
  eleven distinct tags, matching the rewritten schema comment exactly.
- `tools_general` weight arithmetic checked against the pool as it now stands:
  8+6+11+5+2 = 32, rope 11/32, identical to the pre-merge rate.
- Syntax check — the `<script>` body extracted and run through `node --check`,
  clean.

**Sections touched**

CONFIG / CONSTANTS (`STACKABLE`, `GAME_CONFIG.VERSION`), WORLD DATA
(`ITEM_REGISTRY`, `SPAWN_POOLS`, one `balcony` placement, the ITEM DATA SCHEMA
comment), WORLD INTERACTION (`doTryDoor()` deleted), CRAFTING (`canCraft()`
comment), PERSISTENCE (`backfillContainerFields()` comment), UI/RENDERING
(`renderHereActionsPanel()`).

**Version**: `GAME_CONFIG.VERSION` `"0.4.13"` → `"0.4.14"`

---

## v0.4.13 — Partial stacks, a vague clock, and a display floor

Implements: handoffs/partial-stacks-vague-clock-and-display-floor.md

Implements #81, #59 and #75 in full, per
`handoffs/partial-stacks-vague-clock-and-display-floor.md`. Three independent
`tier-1` items bundled into one pass, each giving an existing system a surface
it was missing: a quantity `doTake()`/`doStore()` already accepted, a time the
clock already derived, and a floor already being applied to every duration
label. No new mechanic, no new content, no new persistent state — `SAVE_KEY`
does not rotate and existing browser saves keep loading.

**New**

- **`MIN_DISPLAY_MIN`** — the floor `fmtDuration()` applies to any duration the
  UI prints, in game minutes. It is `1`, the same value `MIN_MOVE_MIN` has, so
  the split changes no pixel; the point is that retuning the movement floor no
  longer silently re-rounds Rest, Sleep, Search, fishing, every craft recipe and
  the fire's fuel readout along with it. `moveMinutes()` keeps reading
  `MIN_MOVE_MIN`.
- **`MINUTES_PER_DAY`** — `1440`, now the single definition of a game day's
  length. Replaces both literals in `getClockText()` and both in `DECAY`; the
  file contains exactly one `1440` after this pass.
- **`TIME_OF_DAY_BANDS`** — a seven-entry table mapping a minute of the day to a
  band label: `late night` (00:00), `dawn` (05:00), `morning` (07:00), `midday`
  (12:00), `afternoon` (14:00), `evening` (18:00), `night` (21:00). Entries are
  sorted ascending by `from`, the first is `from: 0`, and each band runs until
  the next one's `from` — stated as invariants in the comment. It is the single
  place in the game that says what part of the day a minute falls in, laid down
  deliberately ahead of #58's light layer so that layer reads this table instead
  of forming a second opinion about when evening starts.
- **`absoluteMinute()`, `dayNumber()`, `minutesIntoDay()`** — the clock's
  arithmetic, extracted so there is one of it. `getClockText()` is now composed
  from them and `getVagueClockText()` reuses `dayNumber()` rather than
  re-deriving it; #60's playthrough stats can call `dayNumber()` directly.
- **`timeOfDayBand()`** and **`getVagueClockText()`** — the band lookup and the
  watchless reading, `"Day 3, evening"`.

**UI**

- **`#clockLabel` is never empty during play.** Without a watch it reads
  `"Day 3, evening"` where it previously rendered the empty string: the day
  number always shows, and precision is what the watch buys rather than all
  sense of time. With a watch the reading is unchanged (`"Day 3, 14:22"`), and
  `render()`'s game-over branch still blanks the label without routing through
  either function. Band labels are lowercase so both forms compose identically
  after `"Day N, "`. This is functional UI text held to clarity, not to the
  prose tone.
- **The item detail view offers `Take All` / `Take Half` / `Take 1`**, and the
  mirror on the inventory side: `Place All`/`Store All`, `Place Half`/`Store
  Half`, `Place 1`/`Store 1`, on the existing destination-dependent label.
  `Take Half` (and its mirror) appears for a stackable of 3 or more and moves
  `Math.ceil(it.qty/2)` — half of 7 takes 4 and leaves 3. Moving 7 of 12 is
  still inexpressible; All / Half / 1 is the settled set.
- **"Take" and "Place"/"Store" in the detail view are renamed to "… All"**,
  because "Take" beside "Take Half" no longer says which it is. The inline list
  rows in `renderItemList()` are unchanged and keep the bare
  `Take`/`Place`/`Store` label — one button in the row, nothing to distinguish
  it from.

**Changed / Reworked**

- `getItemActions()` computes the split gate once as `splittable`
  (`STACKABLE.has(it.category) && !it.durability`, the gate the single-unit
  button already used) and the keychain predicate once as `keychainBlocked`,
  which now applies to all three world-side buttons unchanged. `doTake()`,
  `doStore()` and `normalizeQty()` are untouched — they already accepted and
  validated any quantity, including the capacity check that makes a too-heavy
  Half fail without moving anything.
- `DECAY` is expressed in terms of `MINUTES_PER_DAY`
  (`hunger:100/(3*MINUTES_PER_DAY)`, `thirst`/`energy` `100/MINUTES_PER_DAY`).
  The three rates are bit-identical to v0.4.12's; the comment above them now
  reads in days rather than hours to match.

**Removed**

- **The dead `button.mini.step` CSS rule.** No revision in the repository's
  history ever set a `.step` class on a button — `git log -S` over every commit
  finds none — so it has been inert since v0.4.0. This pass settles that the
  quantity picker is a button set in the detail view, so nothing will apply it;
  removing it stops it implying a stepper control that was decided against.

**Documentation**

- `MIN_MOVE_MIN` gains a comment recording two things the constant could not
  show: that it is load-bearing (22 of the 774 exits are building entrances
  whose two Locations share coordinates, so their distance is 0 and this floor
  is all that stops them being free), and the pace decision #75 settles — **pace
  is a journey-scale choice, not a per-block one.** With the floor at 1 minute,
  one 100 m block costs 1.00 minute at Jog against Walk's 1.39 — a 28% saving,
  not the 40% that Jog's 67%-higher speed implies — and over a 50 m block the
  two gaits are identical, both floored to 1 minute. That is intended, not a
  defect.
- **Nothing was deferred and no new issues were filed.** The one finding this
  area has produced that is not fixed here, #92 (a mid-block stop costing more
  than the block it sits inside), was filed during the planning session that
  wrote the handoff and is explicitly out of scope below.

**Open questions / decisions resolved**

The handoff left five choices to implementation; all five took the recommended
option.

- **Comments name no issue numbers.** Both the band table and `MIN_MOVE_MIN`
  explain themselves as rules ("a later light-and-darkness layer reads these
  bands") rather than by ticket, since a roadmap number goes stale on its own
  schedule. v0.4.12's `shelter` comment does cite issue numbers; this pass
  deliberately does not follow that precedent.
- **The inline row button keeps its bare label.** `Take`/`Place`/`Store`
  unchanged in `renderItemList()`; "All" is only meaningful where there is an
  alternative to distinguish it from. It reads consistently beside the detail
  view on screen.
- **Half rounds up** — `Math.ceil`, which keeps the gate at qty 3 rather than 4
  and lets repeated halving converge downward without stranding a 1.
- **`MINUTES_PER_DAY` and `MIN_DISPLAY_MIN` both sit in CONFIG / CONSTANTS**
  with the other top-level constants, not beside `DAY_START_MIN`.
- **The band boundaries are the handoff's recommended table**, unchanged after
  seeing them on screen.

**Notes / assumptions**

- **The seven band boundaries are a judgment call with no prior convention and
  are retunable.** They are set to be plausible as *light* boundaries because
  #58's layer is meant to read them. The number of bands is fixed at seven by
  #59; the boundaries are not.
- **Half rounding up, and the `qty >= 3` gate on Half, are both retunable.** The
  gate is written inline with a comment rather than as a named constant: at qty
  2 half is 1 and the button would duplicate "… 1", which is a rule, not a magic
  number — a constant there would only restate the digit.
- **The watch stays worth carrying.** Bands are 2–5 hours wide, and the two
  readouts a player plans against — `room.fireMinutesLeft` and
  `estimateSleepMinutes()` — print minutes either way. Confirmed on screen: a
  watchless run reads `"Day 1, morning"` beside `Rest (1:00)` and
  `Sleep (1:30)`.
- **`MIN_DISPLAY_MIN` is deliberately equal to `MIN_MOVE_MIN`.** The two
  sub-minute readouts that can reach the floor (`"Sleep (0:01)"` and the fire's
  `"roughly 0:01 of fuel left"`) read exactly as they did at v0.4.12.

**Explicitly NOT changed**

- No gait speed, no floor value, and no arithmetic in `moveMinutes()` or
  `exitMinutes()`. Every movement cost in the game is unchanged.
- No balance constant, no `DECAY` rate, no `ITEM_REGISTRY` entry, no WORLD DATA.
- No PLAYER STATE field, no ITEM DATA SCHEMA or ROOM SCHEMA change, no save
  format change and no backfill. `SAVE_KEY` is unchanged at `ashfall_save_v0.4`.
- `doTake()`, `doStore()`, `normalizeQty()`, `addToDestination()` and
  `renderItemList()` keep their bodies. The detail view's behaviour after a
  partial take is unchanged and intentional: the source stack keeps its `_uid`
  and the panel stays open on it, while `Take All` splices it and the panel
  falls back to the recipe list.
- `hasWatch()` and `isWatch` are untouched, and `shelter` stays unread — a
  reading gated on being able to see outside needs a flag that does not exist
  yet, and `shelter` is not it.

**Validation performed**

- `git diff origin/main...HEAD -- ashfall.html` is the proof of the "no other
  visible change" claim: the `MIN_DISPLAY_MIN` split shows as the new constant
  plus one word changed in `fmtDuration()`, and nothing else in the diff touches
  a duration.
- Both builds (v0.4.12 from `origin/main` and this one) were loaded into a Node
  harness against a stub DOM and compared directly, 65 checks, all passing:
  `getClockText()` byte-identical over 65,001 consecutive minutes plus
  fractional and negative inputs; `fmtDuration()` identical over −10 to 2000
  minutes in 0.1 steps; all three `DECAY` rates identical; **all 774 exits × 3
  gaits identical in both minutes and rendered label**, with the minimum still
  exactly `1`; `timeOfDayBand()` matching the table for all 1440 minutes of the
  day with all seven bands reachable; both clock readings agreeing on the day
  number over 14 game days; and the button sets for stack sizes 1, 2, 3 and 12,
  for a non-stackable, for a durability-bearing item, and under the keychain
  gate.
- Driven in Chromium: `"Day 1, morning"` without a watch, `"Day 1, 08:00"` after
  picking one up, `Take All | Take Half | Take 1` on a stack of 7, the
  `Place`/`Store` mirror on both world tabs, half of 7 leaving 3 with the detail
  view still open on the shrinking stack, and an over-capacity `Take Half`
  failing without moving anything. No console errors. The longest label,
  `"Day 1, late night"`, introduces no horizontal overflow at 375px, 760px or
  1280px — relevant to #49, which is not otherwise touched.

**Sections touched**

- **CONFIG / CONSTANTS** — `MIN_DISPLAY_MIN`, `MINUTES_PER_DAY`, the comments on
  `MIN_MOVE_MIN` and `DECAY`.
- **CORE UTILITIES** — `fmtDuration()`.
- **WORLD INTERACTION** — the `DAY_START_MIN` neighbourhood: `absoluteMinute()`,
  `dayNumber()`, `minutesIntoDay()`, `TIME_OF_DAY_BANDS`, `timeOfDayBand()`,
  `getClockText()`, `getVagueClockText()`.
- **INVENTORY / ITEM SYSTEM** — `getItemActions()` only.
- **RENDERING** — `renderLocationPanel()`.
- The `<style>` block — one deleted rule.

Neither a content pass nor a mechanics pass: WORLD DATA is untouched and no rule
in ACTIONS or SIMULATION changed. All three items are new surfaces onto state
and behaviour that already existed.

**Explicitly out of scope**

- **#92** — that a mid-block stop costs more than the block it sits inside. It
  is the same constant seen from the route side and is a real balance change;
  #75's pace question is settled here, that one is not.
- **#75's options 2, 3 and 4** — lowering or removing the movement floor,
  retuning gait speeds, rescaling the grid. Option 1 only.
- **Sub-minute duration display**, which would follow from dropping the floor.
- **Any arbitrary quantity** — no stepper, no free-text field, no prompt. #47
  (fluid transfer) will need more than this if it ever lands.
- **The inline list rows** — no new control there.
- **#58's weather and light model**, beyond laying the band table down as its
  seam and reading it for one label. No darkness, no temperature.
- **Reading `shelter`** — the see-outside refinement needs a flag that does not
  exist yet.
- **#70** (the empty `Ammunition` STACKABLE category), **#49** (`#rightBar`
  crowding), **#60** (playthrough stats), **#47**. None is a prerequisite and
  none is touched.

**Version**: `GAME_CONFIG.VERSION` `"0.4.12"` → `"0.4.13"`

---

## v0.4.12 — A room's address, its building, and whether it is under cover

Implements: handoffs/room-address-and-shelter.md

Implements #42 and #82 in full, per `handoffs/room-address-and-shelter.md`, and
discharges #88 by bannering the handoff both changes invalidate. Two ROOM SCHEMA
changes settled in one pass because both require editing all 218 room
definitions: `building` is split into `address` (where the room is) and
`building` (what building it is inside), and a new `shelter` field is laid down
on every room with no consumer, ahead of #58 and #6. Content and one utility
function only — no new mechanic. `SAVE_KEY` does not rotate; existing browser
saves keep loading and are repaired by a new backfill.

**Changed / Reworked**

*Room identity fields*
- **`address` is new and mandatory on all 218 rooms** — the street or
  intersection the room is at, as a display string, never empty. The rule, now
  in the ROOM SCHEMA comment: *a room's address is the street it is on, and a
  building fronts a street, never a corner.* A street or mid-block node's
  address is its own location, intersection nodes included (`"Dock St & 6th
  St"`); a room inside a building takes the named street that building fronts,
  so the Police Station is entered from `maple3rd` but addresses as
  `"Maple St"`. Four of the six single-room buildings were already authored this
  way — the pass extends the convention rather than inventing it.
- **`building` narrows to a building's name, or absent.** It held a building
  name on 33 rooms, a street or intersection on 184, and `""` on one. It now
  holds a name and nothing else, ever. The six rooms that carried their
  building's name in `room` (`cornerstore`, `pharmacy`, `hardware`, `storage`,
  `riverbank`) moved it into `building` and set `room: null`.
- **`shelter` is new and mandatory on all 218 rooms** — `"none"` or `"full"`,
  178 and 40 respectively. `"partial"` is documented as a reserved third value
  and used by no room: classifying covered porches and open garages is content
  for the pass that gives `shelter` a consumer. **Nothing reads `shelter`
  today.** It ships unread on purpose, the way LOCATIONS' `z` does, so #58
  (weather) and #6 (rooftops) need no retrofit across every room — and, more to
  the point, so #8's ~300 new rooms author it from the start.
- **`shelter` is not `cannotHaveFire`, and is not derived from it.** The two are
  coextensive across all 218 rooms today; that is a measured coincidence of the
  current content, not an invariant, and the implementation does not exploit it.
  They are different facts, and content that breaks the correlation is already
  specced (`handoffs/building-placement-and-elm-st.md`'s unfinished house is
  outdoors and fire-capable). Deriving from `locationId === roomId` was likewise
  rejected — it is wrong for exactly the two interesting rooms, `alley` and
  `riverbank`, both of which are `"none"` while carrying no `cannotHaveFire`.
- Field order in a room literal is now `locationId, address, building, area,
  room, shelter, desc, …`. `shelter` sits with the identity block rather than
  with the optional environmental flags below `desc`, because like `locationId`
  it is mandatory and those flags are not.
- `doors[id].building` and `master_key.building` are a **different field**
  holding a building *id* (`"acorn"`), read by `getItemActions()` and
  `findKeyForDoor()`. Untouched, and now called out as distinct in the schema
  comment.

*`roomLabel()`*
- The four-branch function is replaced by an outward-in composition:
  `[address, building, area].filter(Boolean).join(", ")`, then `room` joined
  with `" - "` when there is an `area` and `", "` otherwise. Every room has an
  address; the other three are optional. The old four branches could not tell
  `"Oak Apartments, Stairwell"` from `"Main St, Corner Store"` — identical field
  shapes, opposite meanings — which is the two-facts-in-one-field problem #42
  was filed for.

**UI**
- **34 of 218 location-bar labels change**, all by gaining the street they are
  on as a prefix, plus `riverbank` losing the leading `", "` it rendered from
  `building: ""`. `#locLabel` is the only thing on screen that differs; no new
  element, no button, no rewritten wording. The alternative composition (drop
  the address when a building name is present) was considered and rejected:
  it would have lost the address for the six single-room buildings that carry
  one today.

| room | before | after |
|---|---|---|
| `living` | `"Acorn Apartments, 2A - Living Room"` | `"Poplar St, Acorn Apartments, 2A - Living Room"` |
| `kitchen` | `"Acorn Apartments, 2A - Kitchen"` | `"Poplar St, Acorn Apartments, 2A - Kitchen"` |
| `bathroom` | `"Acorn Apartments, 2A - Bathroom"` | `"Poplar St, Acorn Apartments, 2A - Bathroom"` |
| `bedroom` | `"Acorn Apartments, 2A - Bedroom"` | `"Poplar St, Acorn Apartments, 2A - Bedroom"` |
| `balcony` | `"Acorn Apartments, 2A - Balcony"` | `"Poplar St, Acorn Apartments, 2A - Balcony"` |
| `hallway2` | `"Acorn Apartments, 2nd Floor - Hallway"` | `"Poplar St, Acorn Apartments, 2nd Floor - Hallway"` |
| `twobee` | `"Acorn Apartments, 2B - Living Room"` | `"Poplar St, Acorn Apartments, 2B - Living Room"` |
| `twobee_kitchen` | `"Acorn Apartments, 2B - Kitchen"` | `"Poplar St, Acorn Apartments, 2B - Kitchen"` |
| `twobee_bathroom` | `"Acorn Apartments, 2B - Bathroom"` | `"Poplar St, Acorn Apartments, 2B - Bathroom"` |
| `twobee_bedroom` | `"Acorn Apartments, 2B - Bedroom"` | `"Poplar St, Acorn Apartments, 2B - Bedroom"` |
| `twobee_balcony` | `"Acorn Apartments, 2B - Balcony"` | `"Poplar St, Acorn Apartments, 2B - Balcony"` |
| `stairs2` | `"Acorn Apartments, 2nd Floor - Stairs"` | `"Poplar St, Acorn Apartments, 2nd Floor - Stairs"` |
| `stairs1` | `"Acorn Apartments, 1st Floor - Stairs"` | `"Poplar St, Acorn Apartments, 1st Floor - Stairs"` |
| `hallway1` | `"Acorn Apartments, 1st Floor - Hallway"` | `"Poplar St, Acorn Apartments, 1st Floor - Hallway"` |
| `onea` | `"Acorn Apartments, 1A - Living Room"` | `"Poplar St, Acorn Apartments, 1A - Living Room"` |
| `onea_kitchen` | `"Acorn Apartments, 1A - Kitchen"` | `"Poplar St, Acorn Apartments, 1A - Kitchen"` |
| `onea_bathroom` | `"Acorn Apartments, 1A - Bathroom"` | `"Poplar St, Acorn Apartments, 1A - Bathroom"` |
| `onea_bedroom` | `"Acorn Apartments, 1A - Bedroom"` | `"Poplar St, Acorn Apartments, 1A - Bedroom"` |
| `onea_patio` | `"Acorn Apartments, 1A - Patio"` | `"Poplar St, Acorn Apartments, 1A - Patio"` |
| `onebee` | `"Acorn Apartments, 1B"` | `"Poplar St, Acorn Apartments, 1B"` |
| `oak_hallway1` | `"Oak Apartments, 1st Floor - Hallway"` | `"Poplar St, Oak Apartments, 1st Floor - Hallway"` |
| `oak_stairs` | `"Oak Apartments, Stairwell"` | `"Poplar St, Oak Apartments, Stairwell"` |
| `oak_hallway2` | `"Oak Apartments, 2nd Floor - Hallway"` | `"Poplar St, Oak Apartments, 2nd Floor - Hallway"` |
| `oak_1a` | `"Oak Apartments, 1A"` | `"Poplar St, Oak Apartments, 1A"` |
| `oak_1b` | `"Oak Apartments, 1B"` | `"Poplar St, Oak Apartments, 1B"` |
| `oak_2a` | `"Oak Apartments, 2A"` | `"Poplar St, Oak Apartments, 2A"` |
| `oak_2b` | `"Oak Apartments, 2B"` | `"Poplar St, Oak Apartments, 2B"` |
| `auto_shop` | `"Auto Workshop, Main Bay"` | `"Main St, Auto Workshop, Main Bay"` |
| `auto_shop_back` | `"Auto Workshop, Back Office"` | `"Main St, Auto Workshop, Back Office"` |
| `police_lobby` | `"Police Station, Lobby"` | `"Maple St, Police Station, Lobby"` |
| `police_evidence` | `"Police Station, Evidence & Holding"` | `"Maple St, Police Station, Evidence & Holding"` |
| `industrial_floor` | `"Riverside Freight, Warehouse Floor"` | `"Maple St, Riverside Freight, Warehouse Floor"` |
| `industrial_office` | `"Riverside Freight, Office"` | `"Maple St, Riverside Freight, Office"` |
| `riverbank` | `", Riverbank"` | `"Water St, Riverbank"` |

  The other 184 labels are byte-identical — including all 64 intersection
  nodes, all 117 street and mid-block nodes, `alley`, and the three flats above
  the Main St shops.

**New**
- **`backfillRoomAddresses()`** (PERSISTENCE), the fourth backfill beside
  `backfillItemIds()` / `backfillLocationIds()` / `backfillContainerFields()`,
  called from `applyLoadedData()` after the other three. `applyLoadedData()`
  takes the incoming world wholesale, so a save made before this ships carries
  rooms with the old `building` and no `address` — every one of its 218 labels
  would render `"undefined, …"`. It keys off `address === undefined`, not
  falsiness, and copies all four label fields rather than just `address`:
  `building`'s meaning changed and `room` moved for six rooms, so restoring
  `address` alone would leave `cornerstore` reading
  `"Main St, Corner Store, Corner Store"`. All four are static content with
  `roomLabel()` as their only reader, which is what makes taking them wholesale
  from the defaults safe. **`shelter` gets no backfill** — nothing reads it, so
  an old save's rooms lacking it changes nothing; the pass that adds the first
  consumer inherits that backfill, and the schema comment says so.
- **`validateRoomSchema()`** (PERSISTENCE), a dev-only console helper beside
  `validateLocations()`, wired to nothing. Reports a room with no `address`, a
  missing `shelter`, or a `shelter` outside `"none"`/`"partial"`/`"full"`.
  A helper rather than a build-time warning because both failures are loud: a
  missing `address` renders `"undefined"` in the location bar of the room you
  are standing in, on the first frame.

**Open questions / decisions resolved**
- **`building: null` is omitted, not written, on the 176 street nodes** (and on
  `alley` and the three flats). `address` is what those rooms have, and
  `filter(Boolean)` treats absent and `null` identically; the schema comment
  states that `building` is absent when the room is not inside a named building.
- **`shelter` is a bare string**, not a `SHELTER` frozen constant set. The three
  legal values are named in the ROOM SCHEMA comment and in
  `validateRoomSchema()`. The file's other enumerated room fields (`sleepSpot`,
  `searchLabel`) are bare strings too, and a constant set read by one validator
  is not yet earning its name.
- **`backfillRoomAddresses()` runs last** in `applyLoadedData()`'s backfill
  block. It is independent of the other three; the position is for reading
  order only.

**Notes / assumptions**
- **The three flats above the Main St shops get `building: null`, not the
  shop's name** — a flat over the Corner Store is not inside the Corner Store;
  the shop is downstairs and the residence is reached by its own stair. This is
  a judgment call with no prior convention, and it is **retunable**: it also
  happens to preserve those three labels exactly, which is convenient but is not
  the argument for it.
- The 40 `"full"` rooms are **exactly** the 40 carrying `cannotHaveFire`. Stated
  here as a measured fact about today's content, not as an invariant anything
  may rely on.

**Explicitly out of scope**
- **The remaining `BUILDINGS[].name` ↔ `room.building` duplication.** This pass
  removed the `room.room` half of it — all eleven `BUILDINGS` names now live in
  some room's `building` field — but not the rest. Deriving from
  `BUILDINGS[id].name` needs a stable `buildingId` on rooms to join on, since
  matching by name string is what the project avoids. Filed as **#89**.
- **`cannotHaveFire`** — not replaced, not derived, not removed.
- **Giving `shelter` a consumer** (#58, #6), and **#8 itself**: no room was
  added.
- **#68** (`computeDirection()`'s zero vector), specced separately in
  `handoffs/direction-zero-vector-guard.md`; **#87** and **#37**, both
  RENDERING.
- The 64 intersection nodes' `"<Street> St & <N>th St"` strings, which read
  correctly and stay as authored.

**Documentation**
- The ROOM SCHEMA comment documents `address` (with the address rule),
  `building`'s narrowed meaning and its distinctness from `doors[].building`,
  and `shelter` (legal values, the reserved `"partial"`, the LOCATIONS-`z`
  precedent for shipping a field unread, the not-`cannotHaveFire` rule, and the
  inherited backfill).
- **`handoffs/building-placement-and-elm-st.md` carries a supersession banner**
  as of this PR — it authors `building:"214 Elm St"`, a meaning the field no
  longer has, and specs no `shelter` at all. Body untouched; the banner names
  what changed, notes that its label *output* is unaffected, and points at #88.
  This closes #88.
- **Deferred and filed: #89** (the `buildingId` question above). Nothing else
  was deferred.

**Sections touched**
- **WORLD DATA** — the ROOM SCHEMA comment and all 218 room definitions, across
  the ten building builders and the sixteen street builders.
- **CORE UTILITIES** — `roomLabel()`.
- **PERSISTENCE** — `applyLoadedData()`'s backfill block, new
  `backfillRoomAddresses()`, new `validateRoomSchema()` in the dev-helper block.
- Nothing in ACTIONS, SIMULATION or the STAMINA/FATIGUE sub-block. RENDERING is
  reached only through `renderLocationPanel()`'s existing, unedited call to
  `roomLabel()`. The ARCHITECTURE comment needs no change — no section gains or
  loses a responsibility.

**Validation performed**
- **Full before/after label table for all 218 rooms**, built on `origin/main`
  and on the branch and diffed: **exactly 34 rows differ**, each exactly as the
  handoff's table specifies. The 184 unchanged labels are proven, not asserted.
- **No label starts or ends with `", "`, is empty, or contains `undefined`.**
- `validateRoomSchema()` returns `[]`. Counts: **178 `"none"`, 40 `"full"`, 0
  `"partial"`**, 0 rooms without an address. `validateLocations()` still returns
  `[]`.
- **`shelter` vs. `cannotHaveFire`:** the two sets are identical (40 = 40) and
  `alley` / `riverbank` are `"none"` with no `cannotHaveFire`, as expected.
- **Old-save round trip:** a `serializeGame()` output produced on `origin/main`
  at v0.4.11, loaded into the branch build, renders all 218 labels identically
  to a fresh world — and leaves `shelter` undefined on all 218, which is the
  specified behavior. A well-formed new save still round-trips byte-identically
  through `serializeGame()`.
- **Master key regression:** `findKeyForDoor()` resolves the Acorn master key
  for all four Acorn doors (`1a`, `1b`, `2a`, `2b`) — the guard on
  `doors[].building` / `master_key.building` not having been caught by the
  field sweep.
- **Page load in Chromium: zero console errors or warnings**, `#locLabel` reads
  `"Poplar St, Acorn Apartments, 2A - Living Room"`.
- **Diff discipline:** `git diff origin/main...HEAD -- ashfall.html` — the
  version bump, the ROOM SCHEMA comment, 218 single-line room definitions,
  `roomLabel()`, and two additions in PERSISTENCE. Nothing in ACTIONS,
  SIMULATION or RENDERING.

**Version**: `GAME_CONFIG.VERSION` `"0.4.11"` → `"0.4.12"`

---

## v0.4.11 — Reproduced defect sweep: Sleep, fire spend, load atomicity, log freshness

Implements: handoffs/reproduced-defect-sweep.md

Implements #61, #62, #63, #64 and #65 in full, per
`handoffs/reproduced-defect-sweep.md`. Five independent defects, each with a
deterministic reproduction, bundled into one correctness pass because each is
small and none needs new state. No new mechanic, no content, no save field.
`SAVE_KEY` does not rotate — existing browser saves keep loading.

**Fixed**
- **Sleep could lower Energy (#61).** `doSleep()` ended with
  `state.vitals.energy = clamp(ceiling)`, an unconditional assignment to the
  Fatigue-derived ceiling. At `E=70 Fa=40` the ceiling is 60, so a
  zero-duration Sleep dropped Energy by 10 and still cleared Fatigue; at
  `E=16.1 Fa=100` the ceiling is 0 and Sleep emptied Energy outright. The
  assignment is now `Math.max(state.vitals.energy, sleepEnergyCeiling())` — it
  still snaps the loop's approximate landing exact, but can only raise.
- **The first campfire cost no firewood, or three too many (#62).**
  `canBuildFire()` gated a first build on a `campfire_kit` alone, while
  `doBuildFire()` then called `consumeFromPools("firewood", FIRE_BUILD_WOOD)`
  unconditionally. `consumeFromPools()` takes what it can and reports nothing,
  so with no firewood the fire lit free, and with firewood in a pocket it
  silently ate three pieces the gate never asked for. `doBuildFire()`'s spend is
  now a three-way branch: a first build consumes the kit only and banks
  `CAMPFIRE_KIT_COST * FIRE_MINUTES_PER_WOOD`; a rebuild in an existing
  campfire consumes `FIRE_BUILD_WOOD`; a banked relight consumes nothing.
- **"Add fuel" at the burn cap wasted a firewood (#64).** The render gate
  offered the button at any `fireMinutesLeft < FIRE_MAX_MIN`, so at 350 minutes
  one piece of wood bought 10 minutes and `doAddFuel()`'s `Math.min` discarded
  the other 50. The gate is now
  `room.fireMinutesLeft <= FIRE_MAX_MIN - FIRE_MINUTES_PER_WOOD`, so the button
  is offered only while a piece buys its full value. `doAddFuel()` itself is
  unchanged; its `Math.min` is simply no longer the binding constraint from the
  UI path.
- **A collapsed log summary changed brightness with its last line's class
  (#65).** `log()` decided `fresh` from the caller's `cls` argument, but a
  `LOG_SUMMARIES` line renders unclassed regardless of what the call passed.
  A fishing run ending on a bite (`"good"`) therefore rendered dim while the
  same run ending on a miss (`null`) rendered bright. A `summarised` local now
  records that the summary branch ran, and `if(summarised || !cls)` marks the
  line fresh — freshness follows what was rendered, not what was asked for.

**Hardened**
- **A rejected load no longer leaves a broken world on screen (#63).**
  `applyLoadedData()` assigned `world` before running `resyncUidCounter()`, the
  three backfills and `render()`, any of which throws on a malformed save. Both
  callers caught the throw and reported "nothing was loaded" — untrue, since the
  bad world was already committed and the session was unplayable with `doRestart()`
  the only way out, and nothing surfaced it. The load is now atomic: `nextState`,
  `nextWorld`, `nextDoors` and `nextWindows` are built as locals, a new
  `validateLoadedWorld()` checks them, and the four module bindings are assigned
  only on success. The backfills run after validation, not before — they repair
  old-but-well-formed saves and are not what makes a malformed one safe.
- **New `validateLoadedWorld(nextWorld, nextState)` in PERSISTENCE**, returning
  an array of problem strings the way `validateItemRegistry()` and
  `validateLocations()` do. It covers exactly the five shapes that throw today —
  a room's `floor`, `exits` or `containers` not being an array,
  `state.inventory.items` not being an array, and any populated `CONTAINER_SLOTS`
  bag whose `items` is not an array — and no more. This is a shape check, not a
  schema validator. `carContainers` is optional on a room and is checked only
  when present. It sits in PERSISTENCE beside the backfills rather than in the
  dev-helper block, because unlike its two siblings it is wired into a real code
  path and runs on every load.

**Changed / Reworked**

*Sleep availability*
- **A Sleep that would restore no Energy is no longer offered.**
  `sleepAvailable()` was purely a cooldown test and is now the conjunction of
  two named halves: `sleepOffCooldown()` (the old `SLEEP_COOLDOWN_MIN` test,
  unchanged) and `sleepRestoresEnergy()` (`state.vitals.energy <
  sleepEnergyCeiling()`). `doSleep()`'s existing `if(!sleepAvailable()) return;`
  guard now blocks the zero-duration case at the action level, not only in the UI.
- **At Fatigue 100 the ceiling is 0, so Sleep is never offered.** `energy < 0`
  is never true. The Sneak lock must be worked off through `recoveryStep()`
  instead. This is the intended price of the decision, not a side effect — see
  **Open questions / decisions resolved**.

**New**
- `sleepEnergyCeiling()` in the STAMINA / FATIGUE sub-block, returning
  `clamp(100 - state.vitals.fatigue)`. The ceiling was derived independently in
  `doSleep()` and `estimateSleepMinutes()`; this pass added a third consumer, so
  it is now defined once and read by all three.

**Removed**
- `doSleep()`'s `fatigueAtSleep` local. Extracting `sleepEnergyCeiling()` left
  it with no reader — its only use was the ceiling derivation it no longer
  performs. The snapshot semantics it carried are unchanged and now belong to
  `const ceiling`, which is still read once before the loop; the comment above
  it says so explicitly. See **Notes / assumptions**.

**UI**
- **The Sleep note names which of the two reasons applies.** The existing
  string `"You're not tired enough to sleep yet."` moves to the case it was
  always describing — no Energy deficit — and the cooldown gets
  `"You've slept too recently to manage it again."` Both are functional UI text,
  held to clarity rather than the game's prose tone.
- **The spurious `"Sleep (0:01)"` label is gone**, as a consequence of the gate
  rather than a change to `fmtDuration()`. The button renders only when the
  Sleep will really run, so `estimateSleepMinutes()` is never 0 at that point.
- **"Add fuel to the fire" now disappears from 300 minutes rather than 360.**
  No new text; `renderLocationPanel()` already prints the fire's remaining fuel,
  so the button's absence is explicable on screen.
- **A collapsed `fish` / `rest` / `chop` / `fuel` summary is now consistently
  the bright (`fresh`) line.** No wording changed.
- **A rejected save shows the same message as before.** The difference is that
  the session is still playable afterwards.

**Open questions / decisions resolved**
The handoff carried two balance calls, both answered by Tom during planning and
specced as settled. Neither was re-opened during implementation.
- **A — a Sleep that would restore no Energy is refused.** Sleep exists to
  recover Energy; when there is none to recover it is not offered, and the free
  Fatigue wipe goes with it. **The first-proposed predicate was wrong and is not
  what shipped.** It was `energy < ceiling || fatigue > 0`, and the `|| fatigue > 0`
  clause is true in exactly the cases the defect lives in — it would have
  permitted all six tested states, including `E=70 Fa=40` and `E=16.1 Fa=100`,
  closing nothing. The shipped test is `energy < ceiling` alone, which is true
  only when the Sleep would actually run.
- **A's consequence, verified not a trap.** From the state a chop-and-fish grind
  actually reaches (`E=16.1 St=0.0 Fa=100.0 Hu=51 Th=3`), standing still and
  doing nothing, Fatigue reaches 0 without plateauing — driving `recoveryStep()`
  directly it clears at 436 game minutes, and through the real awake path
  (`advanceTime()`, where collapses fire and each grants Energy) at 733 with
  three collapses. Recovery never stalls; there is no softlock. The cost of
  reaching Fatigue 100 is roughly one wasted day, which is the point.
- **B — a campfire kit contains its own first load of wood.** A first fire costs
  the kit and nothing else: 3 firewood total, not 6. `canBuildFire()` was already
  right, so `doBuildFire()` is what changed. This also makes the economy
  internally consistent — a kit is `CAMPFIRE_KIT_COST` firewood and yields
  `CAMPFIRE_KIT_COST * FIRE_MINUTES_PER_WOOD` = 180 minutes, and a rebuild is
  `FIRE_BUILD_WOOD` firewood for `FIRE_BUILD_WOOD * FIRE_MINUTES_PER_WOOD` = 180.
  Same wood, same burn. What the kit buys over loose wood is the 15 crafting
  minutes and the permanent `campfireBuilt` structure in that room.

**Notes / assumptions**
The handoff left four narrow calls to implementation. All four took its
recommendation, and a fifth arose from the work itself.
- **`validateLoadedWorld()` returns strings, not booleans**, matching the two
  existing validators, and `applyLoadedData()` `console.warn`s them on rejection
  the way `validateLocations()` does. A failed import leaves something
  diagnosable in the console while the player-facing message stays generic.
- **The two `catch` messages are unchanged.** Now that the load is atomic,
  `"Couldn't read a save from this browser."` and `"That file couldn't be read
  as a save."` are no longer untrue, and the validator's `console.warn` carries
  the detail. No third message was added for a shape failure.
- **The `summarised` flag is a local in `log()`**, not a second
  `LOG_SUMMARIES[key]` test at the bottom of the function. The second test would
  be a second source of truth for one condition.
- **The cooldown note reads `"You've slept too recently to manage it again."`** —
  the handoff's proposed string, taken as-is. Retunable: anything equally plain
  would do.
- **`doSleep()`'s `fatigueAtSleep` local was removed rather than kept.** The
  handoff asked for it to be kept, on the grounds that its snapshot semantics
  are load-bearing. Extracting `sleepEnergyCeiling()` left it with no reader at
  all, and the semantics the handoff was protecting are carried by `const
  ceiling` — read once, before the loop, with the loop measuring against it. An
  unused local would have been dead code standing in for a comment, so the
  comment now states the snapshot directly. This is the one place the pass
  departs from the handoff's letter.
- **Decision A raises the value of #49** (player condition UI). Fatigue is
  displayed nowhere, which is why #61 arrived without warning, and A makes the
  Fatigue-100 state more costly without making it more legible. Not this pass's
  job; worth stating.

**Explicitly out of scope**
Restated from the handoff so this needn't be opened to know what isn't here.
- **`consumeFromPools()` gaining a return value.** It is the root hazard behind
  both #62 and #64 — five call sites can all silently under-pay the same way —
  and it is a different pass, because it touches `doCraft()` and
  `doDismantleCampfire()`, which are otherwise untouched here. Nothing in this
  pass forced it.
- **`fmtDuration()`'s `MIN_MOVE_MIN` floor (#75).** The Sleep gate removed the
  symptom that made it visible; the floor itself is untouched.
- **Whether "Add fuel", "Put out the fire" and Eat/Drink should cost game time.**
  All three are free while every other action charges. A balance question
  spanning three subsystems; #64 notes it and this pass does not answer it.
- **#66** (ten spawn pools never roll) and **#67** (single-copy tool gates).
  Both bear on the firewood economy and neither is touched.
- **#29** (the log's size and 50-entry cap). This pass edits `log()` and leaves
  `LOG_MAX_ENTRIES` and `#log`'s `max-height` alone.
- **#78** (accessibility). The new cooldown note inherits `var(--ink-faint)` at
  12.5px, matching the existing note's styling and its WCAG AA failure. #78
  fixes both together or neither.
- **The `", Riverbank"` location label.** Real and reproduced, but it belongs to
  #42's decision about what the `building` field means.

**Explicitly NOT changed**
- **WORLD DATA.** No room, item, container, exit, door, window or description.
  `ITEM_REGISTRY`, `LOCATIONS`, `BUILDINGS` and every `build*()` function show
  zero diff.
- **The save format.** No new or changed PLAYER STATE field, ITEM DATA SCHEMA
  field, tag or category, and no room/container/exit schema change. `SAVE_KEY`
  does not rotate. Fix #63 does make some previously-loadable saves refuse to
  load — the malformed ones that currently load halfway and break the session.
  That is the point, and it is not a format change.
- **Balance constants.** `CAMPFIRE_KIT_COST`, `FIRE_BUILD_WOOD`,
  `FIRE_MINUTES_PER_WOOD`, `FIRE_MAX_MIN`, `SLEEP_ENERGY_RATE`,
  `SLEEP_COOLDOWN_MIN` and every recovery rate are untouched — only the
  comment above `FIRE_BUILD_WOOD` changed, to stop reading as though every
  fresh burn costs it.
- **`doAddFuel()`, `canBuildFire()` and `consumeFromPools()` bodies.**
  `canBuildFire()` gained a comment and nothing else; it was already correct
  under decision B.
- **`recoveryStep()` and the Stamina/Fatigue recovery rules.** The no-softlock
  result above is a measurement of existing behavior, not a change to it.

**Validation performed**
- **The handoff's acceptance tests were run as written**, against the real file
  in headless Chromium, on `origin/main` and on this branch, with the internals
  exposed by a test-only shim rather than by editing the shipped file.
- **#61:** all five table rows match. `E=70 Fa=40` and `E=16.1 Fa=100` — button
  absent, note "not tired enough", vitals untouched (was: `"Sleep (0:01)"`,
  Energy → 60 and → 0 respectively). `E=50 Fa=40` still runs 60 minutes to
  Energy 60; `E=85 Fa=0` still runs 90 minutes to Energy 100. Cooldown-not-elapsed
  now reads "slept too recently". No-softlock measured as recorded above.
- **#62:** a first build carrying 5 firewood leaves all 5 (was: 2), banks 170
  minutes after `BUILD_FIRE_MIN`, and consumes the kit. With 0 firewood,
  `canBuildFire()` is still true and the fire still lights. Relight with
  `campfireBuilt`, `fireMinutesLeft = 0` and 0 firewood is still refused; with 3
  firewood it builds, firewood → 0, `fireMinutesLeft = 170`. A banked relight
  spends nothing. All three log strings still reach their cases.
- **#64:** at 350 the button is absent (was: shown, one wood for 10 minutes); at
  301 absent; at 300 shown, and one wood takes it to 360.
- **#63:** eight save shapes. The four that previously threw — missing `floor`,
  missing `containers`, missing `exits`, non-array `inventory.items` — now
  return `false` cleanly with `state`, `world` and `totalMinutes` provably
  unchanged. The three already rejected (empty object, missing `world`, unknown
  `currentRoom`) still return `false`. A well-formed save still round-trips
  byte-identically through `serializeGame()`.
- **#65:** three casts ending on a bite and three ending on a miss both render
  `[fresh]` (was: `[(none)]` and `[fresh]` for the same text). Regression guards
  hold — a `warn` line still breaks a tally run into separate lines, a `craft:`
  run still keeps its `good` class and its `×3` counter and is still not fresh,
  and the 50-entry cap still trims from the front.
- **No page errors** on load or during any test run.
- **Diff discipline:** `git diff origin/main...HEAD -- ashfall.html` is 14 hunks
  and 127 changed lines, the lowest at line 256 (the version bump) and the next
  at 3576 — past the whole of WORLD DATA. No `build*()` function appears in the
  diff.

**Sections touched**
- **SURVIVAL / TIME SIMULATION**, STAMINA / FATIGUE sub-block — `doSleep()`,
  `sleepAvailable()` and its two new halves, `sleepEnergyCeiling()`,
  `estimateSleepMinutes()`.
- **FIRE / COOKING** — `doBuildFire()`, `canBuildFire()`'s comment, the
  `FIRE_BUILD_WOOD` constants comment.
- **PERSISTENCE** — `applyLoadedData()`, new `validateLoadedWorld()`.
- **CORE UTILITIES** — `log()`.
- **RENDERING** — the sleep gate and the "Add fuel" gate in
  `renderHereActionsPanel()`.

**Documentation**
- Comments added or rewritten at each changed site: the `FIRE_BUILD_WOOD` block
  (a first fire comes from the kit, a rebuild costs `FIRE_BUILD_WOOD`),
  `canBuildFire()`'s first-build branch, `doBuildFire()`'s hoisted `banked` and
  its kit-burn derivation, `doSleep()`'s ceiling snapshot and its `Math.max`
  rationale, the Sleep-gate halves including the Fatigue-100 consequence,
  `log()`'s summary branch (unclassed *and therefore* fresh), the "Add fuel"
  gate, and `validateLoadedWorld()`/`applyLoadedData()`'s atomicity contract.
  The ARCHITECTURE comment needed no change — no section gained or lost a
  responsibility.
- **Nothing was deferred and no new issues were filed.** The pass surfaced
  nothing beyond what the handoff already listed as out of scope; every item in
  that list has an existing issue or is named there.

**Version**: `GAME_CONFIG.VERSION` `"0.4.10"` → `"0.4.11"`

---

## v0.4.10 — Building identity in WORLD DATA, and Close-map labels that fit

Implements: handoffs/map-building-identity-and-label-fit.md

Implements #39 and #16 in full, per
`handoffs/map-building-identity-and-label-fit.md`. Three parts: a building's
name and anchor move out of RENDERING into WORLD DATA, Close-map building
labels stop being cut off by the edge of the view, and the two-column layout
collapses to one column on a phone. No mechanic, no content, no save field and
no player-facing text changed.

**Organization / Structural**
- **`MAP_BUILDINGS` is split in two along the line between what a building is
  and how it is drawn.** `BUILDINGS` (WORLD DATA, immediately after
  `LOCATIONS`) holds `name` and `anchor` keyed by a stable building id;
  `MAP_BUILDING_OFFSETS` (RENDERING/MAP) holds the `dx`/`dy` label offset under
  the same keys. `renderMapClose()` and `mapBindBuildingLabels()` read both.
  `MAP_BUILDINGS` is gone. A building's name and the Location it sits on are
  reference data, the same category as `LOCATIONS` itself — the label offset is
  the only part of the old table that was genuinely about rendering.
- **Membership of `MAP_BUILDING_OFFSETS` is now what decides which buildings
  the map names.** A `BUILDINGS` entry with no offsets entry is never reached by
  `renderMapClose()`. Every building has one today, so exactly the same eleven
  markers are drawn; the seam exists for #8, where two buildings can sit close
  enough that only one can carry a label. Both tables carry a comment saying so,
  since a table whose every key is present cannot show it.
- The `LOCATIONS` comment on Pharmacy/Hardware Store sharing an anchor now names
  `MAP_BUILDING_OFFSETS` and says which section it lives in, rather than naming
  a table that no longer exists.

**Fixed**
- **Close-map building labels are no longer cut off by the edge of the view.**
  Root cause: `renderMap()` rebuilds the SVG only when the zoom *mode* changes —
  a move or a `+`/`−` step animates the viewBox underneath the existing markup
  instead — so `renderMapClose()` wrote each label's `x`/`y` once, at build
  time, and the box then slid out from under it. There was no point in the Close
  path where a label and its live viewBox were both in hand. Fixed by mirroring
  the split Wide has used since v0.4.5: `mapBindBuildingLabels()` caches the
  pool once per rebuild, and `mapPositionBuildingLabels(box)` places it from both
  sites that set the viewBox — the snap branch and every animation frame of
  `mapUpdateViewBox()`.
- Measured over all 191 Locations at all three Close steps: **41 / 62 / 117
  clipped label lines before, 0 / 0 / 0 after**. The original v0.4.0 repro —
  `Pharmacy` rendering as `Pharm` from the starting location at the default
  zoom — no longer reproduces.
- **The page no longer scrolls sideways below 480px.** `main` was
  `grid-template-columns:1fr 320px` with no `@media` rule anywhere in the
  stylesheet, giving the document a hard 476px floor: `scrollWidth` was 476 at
  320, 360, 375 and 414. One breakpoint at 760px collapses it to a single
  column. `scrollWidth === clientWidth` at 320/360/375/414/480/760, and the
  grid is unchanged from 761 up.

**New**
- `mapBindBuildingLabels()` (RENDERING/MAP) caches each marked building's dot
  position, its one or two `<text>` nodes, half the width of its widest line,
  and the block's vertical extent. Widths come from `getComputedTextLength()` on
  the bound node rather than a hand-kept table — a table would need re-measuring
  on every rename and would not survive #8 adding buildings. Bind runs only on a
  zoom-mode change, the moment that already rebuilds the SVG, so a pan does no
  layout reads. It returns early outside Close, which is what keeps Wide
  untouched.
- `mapPositionBuildingLabels(box)` (RENDERING/MAP) applies three rules per
  label. **Suppress** — if the marker circle does not intersect the box at all,
  every line is hidden. **Clamp horizontally on a shared centre** — `cx` is
  `dot.x` clamped into `[box.x + PAD + half, box.x + box.w - PAD - half]`, the
  same `cx` for both lines, so a two-line name stays centred as a block instead
  of staggering. **Clamp vertically as a unit** — the block's extent is shifted
  inside `[box.y + PAD, box.y + box.h - PAD]` and that one shift applies to both
  lines' `y`.
- Suppression rather than a bigger clamp is what keeps a name near the thing it
  names. A clamp alone removes all the clipping but can drag a name most of a
  view away to sit pinned against an edge pointing at a dot that isn't drawn.
  Every such case is a building whose own marker is off screen, so those are
  hidden instead — the same call `mapLabelHitsPlayer()` already makes for street
  names under the player marker, for the same reason: a slide can cascade.
  Measured max distance from a drawn label's centre to its own dot: **32.7 user
  units**, against `MAP_BLDG_LABEL_PAD + half` as the bound.
- `MAP_BLDG_DOT_R` (6), `MAP_BLDG_LINE_H` (11) and `MAP_BLDG_LABEL_PAD` (6) are
  named in the MAP sub-block. The first two were literals inside
  `renderMapClose()`'s loop and are now each read from two places — the marker
  circle and the visibility test, the line spacing and the positioner.

**UI**
- Close map: no building label is drawn outside the view, and a label whose
  building marker is off screen is not drawn at all. The set of markers, their
  coordinates and their offsets are unchanged.
- Below 760px the sidebar sits under the main column instead of beside it, and
  `#left`'s `border-right` becomes a `border-bottom` — at full width it would
  otherwise read as a stray rule down the right edge of the page. Above 760px
  nothing changes.
- No label, button, log line or description was reworded.

**Open questions / decisions resolved**
- **Where the label text is written** — the handoff left this between
  `renderMapClose()` emitting each `<text>` with its content already set, and
  the nodes shipping empty for `mapBindBuildingLabels()` to fill the way
  `mapBindStreetLabels()` does. Took the handoff's recommendation and emit the
  text in `renderMapClose()`: Wide's pool is generic across streets, whereas
  each building node belongs to one building, so filling it at bind time buys
  nothing.
- **The nodes ship visible, not hidden.** Wide's pool ships
  `style="display:none"` and this one deliberately does not: a hidden node has
  no layout, so `getComputedTextLength()` measures every name as zero wide and
  the clamp silently does nothing — caught in the browser during validation,
  where every label sat unmoved on its dot. `renderMap()` sets the markup,
  binds and snaps in one synchronous pass, so nothing is painted at the origin
  in between.

**Notes / assumptions**
- **`MAP_BLDG_LABEL_PAD = 6` is a judgment call with no prior convention and is
  retunable**, flagged as such in the source. Anything from about 4 to 10
  behaves the same; the bound on how far a name can sit from its dot moves with
  it.
- **The 760px breakpoint is retunable.** The measured overflow cliff is between
  414 and 480, so any value from 480 up removes the overflow. 760 is chosen
  because the layout stops being *usable* well before it starts overflowing — at
  375px the room description renders about three words wide — and because it is
  the value the superseded `handoffs/map-view-ui-fixes.md` proposed, so it has
  the most thought behind it. Nothing depends on the exact number.
- **The label block's vertical extent is taken from the line box, not a measured
  ink band.** `MAP_BLDG_LINE_H` (11) is taller than the 10px face's cap height,
  so the top edge is conservative, and `MAP_BLDG_LABEL_PAD` covers what a
  descender reaches past the bottom baseline. Retunable with the face, like
  `MAP_LABEL_CAP` for street names.
- **The gaps between a dot and its label (10 above, 16 below) stay literals**
  and keep their v0.4.9 values, so no unclamped label moved. They are not
  symmetric because a baseline below the dot has to clear the circle while one
  above it only has to clear the cap height.

**Explicitly out of scope**
- **#8** — no building is added, moved or renamed. This pass builds the
  `MAP_BUILDING_OFFSETS` seam #8 needs; filling it is that pass's job, specced
  in `handoffs/building-placement-and-elm-st.md`.
- **#42** — the `building` field meaning a building name on multi-room buildings
  and a street on single-room ones. Routed around with a separate table; no room
  definition was edited and `roomLabel()` was not touched.
- **#43** — `MAP_LABEL_W` as a hand-measured font width. This pass is what
  establishes whether bind-time measurement reads well.
- **#37** — Wide-map street names drawn outside the box. Same family of bug in
  the other mode; its fix is in `mapPositionStreetLabels()`, untouched here.
- **Label-vs-label overlap between buildings.** No two building label lines
  overlap at any position today, which is a property of there being eleven
  buildings rather than of the placement logic, which has no overlap test at
  all. Left as is.
- Retuning any `dx`/`dy`; the zoom ladder and `MAP_ZOOM_RANGE`; anything in Wide
  mode; a mobile-first redesign, touch or gesture support, and `#sideMenu`,
  which is `position:fixed` with `max-width:92vw` and already behaves at phone
  widths.

**Explicitly NOT changed**
- **No room, item, container, exit, door or window definition.** `BUILDINGS` is
  a new reference table; `makeDefaultWorld()` is untouched.
- **No balance constant, threshold or duration.**
- **The save format.** PATCH, so `versionCompat("0.4.10")` still yields `0.4`
  and `SAVE_KEY` is unchanged — existing browser saves keep loading. `BUILDINGS`
  is not persisted; saves restore `world`, `doors` and `windows`, and it is none
  of those. No new `state` field: `mapBuildingLabels` is module-level beside
  `mapStreetLabels`, deliberately outside `state`, as `mapZoomMode` and
  `mapZoomStep` already are.
- **Wide mode.** It draws no building markers, `mapBindBuildingLabels()` returns
  early outside Close, and `mapPositionStreetLabels()` was not edited.
- **Marker positions.** All eleven dots are at byte-identical coordinates before
  and after, and every `name`, `anchor`, `dx` and `dy` survived the table split
  unchanged.
- ACTIONS, SIMULATION, PLAYER STATE and PERSISTENCE.

**Validation performed**
- `git diff origin/main...HEAD -- ashfall.html` is the diff of record.
- Syntax check on the extracted `<script>` body (`node --check`), clean.
- **Table split proven entry by entry**, not asserted: both versions loaded in
  Chromium side by side and all eleven entries compared by name — `anchor`,
  `dx` and `dy` identical across the split, no `BUILDINGS` entry without an
  offset and no offset without a `BUILDINGS` entry.
- **Clipping replayed in Chromium over all 191 Locations at all three Close
  steps**, on both `origin/main` and this branch, by placing the labels for each
  Location's target viewBox and reading each visible node's `getBBox()`. Lines
  crossing a box edge: **41 / 62 / 117 before, 0 / 0 / 0 after**. Every drawn
  label is fully inside its box, and the set of drawn labels is exactly the set
  whose own marker circle intersects the box.
- **No marker moved**: the eleven `circle.map-bldg-dot` coordinates are
  identical between `origin/main` and this branch.
- **The real game run in Chromium**, not just the placement replayed: load, open
  the map, toggle Close → Wide → Close, step the zoom through its range in both
  directions, and walk to another room. No page errors, no console errors. Wide
  emits 48 street-name nodes and zero building labels; Close rebinds after the
  round trip and places its labels with zero clipped.
- **Widths measured in Chromium at 320/360/375/414/480/760/761/900/1200.**
  `scrollWidth === clientWidth` at every one; `main` is one column through 760
  and `1fr 320px` from 761 up. The same measurement on `origin/main` gives
  `scrollWidth` 476 at 320/360/375/414, which is the overflow being fixed.

**Sections touched**
- **WORLD DATA** — the new `BUILDINGS` table and one comment retarget on
  `LOCATIONS`. No room, item, container or exit definition.
- **RENDERING / MAP** — `MAP_BUILDING_OFFSETS`, `MAP_BLDG_DOT_R`,
  `MAP_BLDG_LINE_H`, `MAP_BLDG_LABEL_PAD`, `renderMapClose()`,
  `mapBindBuildingLabels()`, `mapPositionBuildingLabels()`, the two call sites
  in `mapUpdateViewBox()` and the bind call in `renderMap()`.
- **The document `<style>` block** — one `@media` rule.

**Documentation**
- Nothing was deferred and no scope was cut, so this pass files no new issues.
  #42, #43 and #37 were already open before it started and none was touched.
- `handoffs/building-placement-and-elm-st.md` is unblocked by this pass: it
  assumes the `BUILDINGS` / `MAP_BUILDING_OFFSETS` seam has shipped.

**Version**: `GAME_CONFIG.VERSION` `"0.4.9"` → `"0.4.10"`

## v0.4.9 — Self-documenting source: named game rules, comments without history

Implements: handoffs/source-self-documenting.md

Implements #33 in full, per `handoffs/source-self-documenting.md`. One pass over
`ashfall.html` with a single goal: the source should say what is true now,
without prose propping it up. No mechanic, value, string or save field changed.

**Organization / Structural**
- **Five action durations that were written twice now have one home.**
  `FISH_DURATION_MIN` (20), `LIGHT_STOVE_MIN` (5), `BUILD_FIRE_MIN` (10),
  `DISMANTLE_CAMPFIRE_MIN` (10) and `CHOP_TREE_MIN` (30) are declared once in
  FIRE/COOKING; `advanceTime()` in ACTIONS and `fmtDuration()` in RENDERING both
  read them. A button and the action it launches can no longer disagree about
  what something costs — that was six literals across a section boundary, and is
  now five constants. `BUILD_FIRE_MIN` and `DISMANTLE_CAMPFIRE_MIN` share a value
  and are deliberately kept as two constants: they are different facts, and
  merging them would mean retuning one silently retunes the other.
- **The fire derivation is written out.** `FIRE_BUILD_WOOD` (3) and
  `FIRE_MINUTES_PER_WOOD` (60) replace the bare `3` in `canBuildFire()` /
  `doBuildFire()` and the bare `60` in `doAddFuel()`, and `doBuildFire()` now
  sets `room.fireMinutesLeft = FIRE_BUILD_WOOD * FIRE_MINUTES_PER_WOOD` instead
  of a literal `180`. The 3 x 60 = 180 relationship previously existed only as a
  coincidence between two functions thirteen lines apart; it now holds by
  construction. `CAMPFIRE_KIT_COST` (also 3) is untouched and deliberately not
  merged — it is what the kit contains, not the fuel a burn costs.
- Also named in FIRE/COOKING: `HEAT_CONTAINER_CAPACITY_KG` (8, the stove and the
  campfire alike, previously two literals), `CHOP_TREE_FIREWOOD` (6) and
  `FISH_BITE_CHANCE` (0.55). `FIRE_MAX_MIN` (360) moved up from its inline
  declaration into the same block so FIRE/COOKING's constants have one home.
- `LOG_MAX_ENTRIES` (50) names the log cap in `log()`. This is the number #29
  exists to re-judge; naming it is the precondition for that issue, not its
  fulfilment, and the value is unchanged.
- SURVIVAL / TIME SIMULATION gained the health-drain rates as named divisors:
  `STARVATION_MINUTES_PER_HEALTH` (30), `DEHYDRATION_MINUTES_PER_HEALTH` (15),
  `ILLNESS_MINUTES_PER_HEALTH` (20), plus `ILLNESS_DURATION_MIN` (180), which
  `doConsume()` sets and `applyHungerThirst()` spends. The divisor form
  (`min/30`, not `(1/30)*min`) was kept deliberately — see **Validation
  performed**.
- `advanceTime()`'s collapse branch had five anonymous numbers in six lines and
  now has `COLLAPSE_BLACKOUT_EVERY` (3), `COLLAPSE_BLACKOUT_MIN` (300),
  `COLLAPSE_BLACKOUT_ENERGY` (90), `COLLAPSE_STUMBLE_MIN` (20) and
  `COLLAPSE_STUMBLE_ENERGY` (30).
- `DAY_START_MIN` (`8*60`) names the start-of-day offset in `getClockText()`.
  It shares a value with `SLEEP_COOLDOWN_MIN` and is deliberately separate.

**Documentation**
- **Version tails stripped, sentences kept** across some 60 comment sites. Where a
  version was the whole comment it went entirely: `// Current version: 0.4.6.`
  inside the ARCHITECTURE block (two versions stale, and duplicating
  `GAME_CONFIG.VERSION` twenty-odd lines below), and the six-line RENDERING
  preamble whose "Unchanged in this revision" had no referent at `main`. The
  seven `Silent:` notes in INVENTORY/ITEM SYSTEM kept their sentences — each
  explains why a `log()` call is *absent*, which is the one thing no reader can
  see in the code.
- **A version naming save-data vintage is a live predicate and stayed.**
  `backfillLocationIds()`'s "Older saves (pre-v0.2.9) predate the locationId
  field" and `backfillContainerFields()`'s "(pre-v0.4.0)" describe the shape of
  data still sitting in people's browsers, not when code arrived. Strip the
  version and the comment stops meaning anything. Both kept verbatim.
- **All 18 `sec. N` citations stripped, sentences kept.** They cited numbered
  sections of a Stamina & Fatigue handoff that is not in the repository, and the
  v0.2.1 changelog entry that carries those rules has no numbered sections to
  resolve them against. Every sentence stands without the citation.
- **Dead handoff pointers stripped.** None of the cited names
  (*"Ashfall v0.2.1 — Stamina & Fatigue System"*, *"Container Spawn Pools &
  Population System"*, *"Ashfall v0.2.9.md"*, *"Ashfall v0.2.5.md"*, the v0.3.0
  handoff) resolves to anything in `handoffs/`. Where a pointer carried a
  provenance clause and nothing else, both went; where it sat beside a live
  judgment-call flag, the flag stayed — ITEM_REGISTRY keeps *"weights are
  estimates … retunable"* and SPAWN_POOLS keeps the *"commoner items 5-8, rarer
  or bulkier ones 1-3"* convention.
- **Stale references retargeted.** `lastRolledMinute`'s "roadmap item 15" →
  `#15`; the RENDERING/MAP banner dropped "Tier 1 item 3" (tier is a GitHub
  label now); the PERSISTENCE comment's "Save format is unchanged in 0.1.3
  (still {…})" became a plain statement of the format, which is the only place
  it is written down.
- **One correction to the handoff.** It directed the documents/lore comment's
  "roadmap item 13" to `#13`, reasoning from the `#15` coincidence. It does not
  hold: `#13` is *Hunting with traps*; roadmap item 13 migrated to **`#7` — Lore
  development**, which its issue body states outright. Retargeted to `#7`.
- **One dead pointer the handoff's audit did not catch.** The STAMINA/FATIGUE
  module header said "(see CORE ACTIONS below)". No CORE ACTIONS section exists —
  ACTIONS is grouped as INVENTORY/ITEM SYSTEM, WORLD INTERACTION, CRAFTING and
  FIRE/COOKING — and the sections it meant are *above* that line, not below.
  Pointer stripped; the sentence stands on its own. Every remaining `see X` in
  the file now resolves to something in the file.
- **Two whole-comment pointers were repointed rather than deleted**, per the
  handoff's first design decision — see **Open questions / decisions resolved**.
- Nothing was deferred that needs a new issue. The Part B4 literals left alone
  are recorded below as judgment calls, not cut scope.

**Explicitly NOT changed**
- **No value changed.** Every constant introduced equals the literal it
  replaced, checkable one by one against the handoff's tables.
- **No player-visible string changed.** The five duration buttons render the
  same text; they just read the constant the action spends.
- Balance constants, `RECIPES`/`HEAT_RECIPES`, the stamina/fatigue rules, and
  both recovery ladders are untouched.
- **Save format and `SAVE_KEY` unchanged.** No new or changed state fields, item
  schema fields, tags, categories, or room/container/exit fields. This is a
  PATCH, so `versionCompat()` still yields `0.4` and existing browser saves load.
- **No WORLD DATA content changed** — no room, item, container, exit or
  description. The pass reached into WORLD DATA's *comments* only.
- Rendering logic and every function body outside the literal-to-constant
  substitutions are byte-identical.
- The ARCHITECTURE block's section list, the ROOM/CONTAINER/EXIT/ITEM schema
  blocks, and the LOCATIONS coordinate convention all keep their content.

**Validation performed**
- `git diff origin/main...HEAD -- ashfall.html` is the diff of record.
- **Part A proof:** with every full-line `//` comment stripped from both sides,
  the before and after files are identical apart from one trailing comment on a
  code line (`mapStreetLabels`). No comment edit ran into code.
- **Part B proof:** every non-comment line in the diff is a literal replaced by a
  constant of the same value, or the version bump — the full list is short enough
  to read in one screen of `git diff`. For the five duration pairs, both halves
  now read the same constant, so button and action cannot disagree by
  construction.
- The health-drain constants are divisors (`min/STARVATION_MINUTES_PER_HEALTH`),
  not per-minute rates (`STARVATION_HEALTH_PER_MIN*min`), specifically so the
  floating-point arithmetic is bit-identical to what it replaced. The rate form
  reads marginally better and can differ by an ulp; on a pass whose whole claim
  is "no behaviour change", the divisor form was the honest choice.
- Syntax check: the `<script>` body extracted and run through `node --check`.
- Runtime check: the same body evaluated under a minimal DOM stub, which
  completes module init and a full first render pass. This catches the one real
  hazard in Part B — a temporal-dead-zone error from a `const` referenced before
  its declaration (`ILLNESS_DURATION_MIN` is declared in SURVIVAL and read by
  `doConsume()` above it; safe because the read happens inside a function body).
- Section-banner audit: all 19 ARCHITECTURE section and sub-block banners present
  and well-formed. Deleting the RENDERING preamble briefly collapsed the
  RENDERING and MAP banners into one; caught and fixed.

**Sections touched**
CONFIG / CONSTANTS, WORLD DATA (comments only), PLAYER STATE (comments only),
SURVIVAL / TIME SIMULATION including STAMINA/FATIGUE, ACTIONS — chiefly
FIRE/COOKING — PERSISTENCE (comments only), and UI / RENDERING including MAP.
Wide but shallow: outside Part B's constant introductions, no executable line
changed.

**Open questions / decisions resolved**
- **Repointing whole-comment pointers: taken, twice.** Where a dead pointer was
  the comment's entire content *and* the target changelog entry genuinely carries
  the rules, it was repointed rather than deleted — the STAMINA/FATIGUE header
  now reads "See the v0.2.1 entry in CHANGELOG.md for the full rules", and
  SPAWN_POOLS points at the v0.4.0 entry. A reader following either comment wants
  the rules, and unlike a `sec. N` citation this resolves. The SPAWN_POOLS one
  was reworded rather than repointed verbatim: the v0.4.0 entry describes the
  design but has no per-container assignment table, so that half of the sentence
  now says the assignments live on the containers' own `spawnPools` fields, which
  is both true and closer to hand.
- **`FIRE_MAX_MIN` left as 360, not derived.** It is `6 * FIRE_MINUTES_PER_WOOD`,
  but writing it that way invents a `FIRE_MAX_WOOD` nothing else uses. The cap
  reads as its own fact — six hours of banked burn, however you got there.
- **Both recovery ladders left as `if`-chains.** `energyRecoveryMultiplier()`
  (80/60/40/20 → 1.00/.90/.75/.50/.25) and `staminaMaxForEnergy()`
  (40/20 → 100/80/50) read perfectly well today; a table of named thresholds
  would be more machinery for no gain at the call site.
- **Left literal, read at the call site and judged clearer as numbers:** the
  sleep-vs-rest energy multipliers (`applyEnergyBaseline(dt, mode === "rest" ? 1
  : 2)`) — the parameter already names itself; the starting vitals
  (75/75/85/100/100/0) and starting inventory capacity — per-instance data in an
  object literal whose keys name each number; and the `-9999` "never happened"
  sentinels, which the comment directly above them explains better than a name
  would.
- **The LOCATIONS coordinate-convention block** is on the handoff's "stays
  untouched" list, but its stale `"Ashfall v0.2.9.md"` pointer is named in the
  handoff's own dead-pointer enumeration. It was read as structural protection —
  don't rewrite the convention — so the block keeps every word of its content and
  received only the line-level version/pointer strips, on the precedent the
  handoff itself set for `// Current version: 0.4.6.` inside ARCHITECTURE.
- **Naming judgment calls, all retunable:** `STARVATION_MINUTES_PER_HEALTH` and
  its siblings use a `_MINUTES_PER_HEALTH` suffix rather than the file's `_MIN`
  suffix, because `_MIN` reads as "a duration" everywhere else and these are
  rates. `COLLAPSE_BLACKOUT_ENERGY` is set-to while `COLLAPSE_STUMBLE_ENERGY` is
  added-to; the asymmetry is pre-existing behaviour and is flagged in a trailing
  comment on each rather than hidden behind matching names.

**Explicitly out of scope**
- **#29** — the log cap's *value*. The 50 is named, not changed.
- **#23** — the illness system. `ILLNESS_DURATION_MIN` names the existing timer
  and nothing is built on it.
- **#39** — `MAP_BUILDINGS` as world data living in RENDERING.
- **#37, #16** — open map/UI issues, adjacent but not prerequisites.
- **#32** — the v0.4.4 / v0.4.5 tag correction, which is run locally.

**Version**: `GAME_CONFIG.VERSION` `"0.4.8"` → `"0.4.9"`

---

## v0.4.8 — Map zoom ladder, and street names clear of intersections

Implements: handoffs/map-zoom-and-label-collisions.md

Implements #27 and #28 in full, per `handoffs/map-zoom-and-label-collisions.md`.
Two changes taken as one pass because they land in the same code: the `+`/`−`
buttons shipped inert in v0.4.5 get a working zoom ladder, and the street-name
placement that ladder retunes gets its intersection-collision fix.

RENDERING only, and within it the MAP sub-block. No new state fields — the zoom
step joins `mapZoomMode` as a module-level `let`, deliberately outside `state` —
so `SAVE_KEY` still derives from `0.4` and existing browser saves keep loading.
No WORLD DATA, no mechanics, no stylesheet change.

**Changed / Reworked**

*Zoom ladder*

- A view's span is now a whole number of blocks: `span = mapZoomStep *
  MAP_SPACING`. `MAP_ZOOM_RANGE` gives each mode the steps it allows and the
  step it opens at — Close `1..3`, base `2` (130 / 260 / 390 units across);
  Wide `3..6`, base `6` (390 / 520 / 650 / 780). `mapTargetViewBox()` reads the
  step instead of picking a span from `mapZoomMode`, which now only bounds the
  range.
- `+` zooms in, which is a *smaller* span: the step counts blocks across, so
  `mapZoomIn` decrements it.
- The step is clamped in `mapSetZoomStep()`, at the two places it changes — a
  `+`/`−` click, and the mode toggle moving the range under it — and nowhere
  else. Both buttons take their `disabled` state from the same range in the
  same call, so a button never offers a step that would do nothing, and
  `mapTargetViewBox()` does no per-frame clamping of a value that changes only
  on a click.
- Switching mode clamps to the nearest step the new mode allows rather than
  resetting to its base. Where the ranges overlap this keeps the box: Close@3 →
  Wide@3 is the same 390-unit view with only the content changing.
- A zoom step re-aims the existing viewBox and does not rebuild the SVG —
  content stays keyed on the mode via `mapRenderedZoom`. The existing 350ms
  animation already interpolates `w`/`h`, and `mapPositionStreetLabels()`
  already runs per frame, so the names re-place themselves as the span changes.
  A **mode** switch still rebuilds, as before.

*Street-name placement (Wide)*

- `mapLabelPositions()` now passes its tier positions through
  `mapClearCrossings()`: a position within `MAP_LABEL_CLEARANCE` of an
  intersection slides to the mid-block beside it. Intersections fall on the grid
  pitch along both axes, so this is arithmetic on the position rather than a
  walk through the street's chain.
- `mapPositionStreetLabels()` takes the player's map node and drops any name
  whose box would fall under the player marker, which nothing in the placement
  previously knew about. `mapLabelBox()` is the one description of what a name
  occupies, used by that test and derived from the same constants as the
  clearance.

**Fixed** — #28, street names colliding at intersections

A name is placed against the *clipped visible* stretch of its street, so an
inset position frequently landed within a name's own width of a crossing, where
a horizontal name's band and a vertical name's band overlap. v0.4.7 put 213
overlapping pairs on screen across the 176 map nodes at its single span. Sliding
those positions to a mid-block — `MAP_SPACING / 2` from either crossing — is
what removes them; the count is now 0 at every span on the ladder (see
**Validation performed**).

**Removed**

- `MAP_CLOSE_VIEW` (260) and `MAP_WIDE_VIEW` (800). Both are now the `base`
  entries of `MAP_ZOOM_RANGE`, expressed in blocks, and the span is derived
  where it is read. Keeping either as a named derivation would have left a
  constant with no remaining use.

**New constants**

- `MAP_LABEL_W` (99.1) and `MAP_LABEL_CAP` (12) — the rendered width of the
  widest name on the map (`"POPLAR ST"`) and the cap height, in user units at
  the 15px `.map-street-name` face. Measured against the font, not chosen, and
  commented as such: every name is upper case with no descender, so the cap
  height is the whole ink band.
- `MAP_LABEL_CLEARANCE` = `MAP_LABEL_W / 2 + MAP_LABEL_OFFSET + MAP_LABEL_CAP`
  (66.55) — how far past an intersection a name's box can still reach the
  crossing street's name.
- `MAP_LABEL_EDGE_GAP` (5), the breathing room in the inset below.

**Derivations named** (previously bare literals, same or near-same values)

| Was | Now | Value |
|---|---|---|
| `MAP_CLOSE_VIEW = 260` | `MAP_ZOOM_RANGE.close.base * MAP_SPACING` | 260 |
| `MAP_WIDE_VIEW = 800` | `MAP_ZOOM_RANGE.wide.base * MAP_SPACING` | **780** |
| `MAP_LABEL_INSET = 55` | `MAP_LABEL_W / 2 + MAP_LABEL_EDGE_GAP` | 54.55 |
| `MAP_LABEL_TIERS` 600 / 300 / 110 | `6 / 3 / 1 * MAP_LABEL_W` | 594.6 / 297.3 / 99.1 |

Wide's default view is **780 rather than 800** — a deliberate 2.5% tightening
of shipped v0.4.5 behaviour, approved during planning, so that every view on the
ladder sits on the block pitch. The tier thresholds move by under 2% except the
smallest, where 110 → 99.1 makes "one name wide" the literal condition for
getting one name. The tiers are a crowding rule, not a legibility one: a name's
width in user units is the same at every span, so what they measure still means
the same thing, and the ladder's ranges are what keep names readable. As
predicted in #27, the 1-label tier is reachable now — unreachable at span 800,
it fires at every span on the ladder.

**UI**

- `+` and `−` are live, each disabling itself at its end of the current mode's
  range; the static `disabled` attributes are gone from the markup and the
  initial state is set from the range at boot. Neither button gained a
  `data-zoom` attribute, which would have captured it into the Close/Wide
  handler.
- Close gains one step in and one step out of its previous view; Wide gains
  three steps in, and its default view is very slightly tighter.
- Wide street names no longer collide at intersections and no longer sit under
  the player marker. A street that loses one of its two or three names to either
  rule keeps the others; where it was the only one, `#locBar` still names the
  player's location.

**Open questions / decisions resolved**

The handoff left four implementation choices open. The first three took its
recommended default; the fourth did too, as `mapSetZoomStep()`.

1. *Nudge direction* — toward the centre of the visible stretch. The mid-block
   on the far side is the fallback, and a name with neither left inside the
   stretch is dropped rather than slid again.
2. *Two names converging on one mid-block* — the one nearer the centre of the
   stretch keeps it. Generalised slightly: any two names on a street that end
   up closer than one name's width apart resolve the same way, which covers the
   near-miss as well as the exact tie.
3. *Shape of the clearance constant* — computed from the width and geometry
   constants at use, so retuning the face or the widest name carries through.
4. *How `disabled` is refreshed* — one helper, called from both handlers.

A fifth decision the handoff did not anticipate: **the clearance formula
itself**. The handoff derived `(width + height) / 2 ≈ 57.05` by treating a name
as a box centred on its anchor. It is not centred — it sits `MAP_LABEL_OFFSET`
off its own street line and its ink runs one cap height further, so the distance
at which a crossing name can still be touched is `MAP_LABEL_W / 2 +
MAP_LABEL_OFFSET + MAP_LABEL_CAP` = 66.55, and under the handoff's number a name
could sit 9.5 units inside that reach without being nudged. The implemented
constant uses the measured geometry.

**Notes / assumptions**

- Every number introduced here is retunable and none has a prior convention
  behind it: the two step ranges and their bases, the tier multipliers, and
  `MAP_LABEL_EDGE_GAP`. Close's ceiling was picked as the step where its 10-unit
  building labels stay near 10 CSS px (the map renders ~420px wide); Wide's base
  is the widest step that still leaves the town's 910 units something to pan
  within.
- `MAP_LABEL_W` keeps the handoff's measured 99.1. The same string measures
  98.2 in the browser this pass was validated in — fonts resolve differently per
  system — and the larger value is the conservative one for a clearance.
- **The clearance a mid-block gives is not symmetric, and one side of it is
  thin.** A mid-block sits 65 units from either crossing, which clears the 66.55
  reach on the side a name is slid away from but comes ~1.5 units short of it at
  the crossing beyond. Closing that gap needs the two names meeting there to
  *both* be within ~3 units of the widest: only `"POPLAR ST"` is, and it runs
  east-west, so it never meets another name that wide. The sweep confirms it —
  zero overlaps, and the closest two crossing names come is 12.6 units. A
  north-south street named wider than `MAP_SPACING - 2 * (MAP_LABEL_OFFSET +
  MAP_LABEL_CAP)` would reintroduce the collisions, and that constraint is
  recorded beside the constant. It is a tighter bound than the handoff's
  estimate of ~115 units, which came from the centred-box model above.

**Documentation**

- Filed #37: in Wide, a street lying exactly on the viewBox edge is still
  treated as on screen and given its names, which then render entirely outside
  the box. Pre-existing — v0.4.7 emitted the same 370 such labels at span 800,
  where they were sliced by the edge rather than missed by it — and out of this
  pass's scope. Surfaced by this pass's sweep.
- Nothing else was deferred. No ARCHITECTURE comment or schema comment changed:
  no section moved and no schema shape changed.

**Explicitly out of scope** (deferred by the handoff, still open)

- #16's close-map building-label clipping, and its mobile breakpoint.
- Neighbourhood / district labels, and any content that varies by span — that
  needs a spatial grouping layer the file does not have.
- Zoom or mode persistence, and any preferences store.
- Viewport culling in `renderMapClose()`, which still emits all 176 node dots
  per rebuild.
- Clamping `mapTargetViewBox()` to the town's bounds, deliberately left
  unclamped in v0.4.5.
- Any change to `LOCATIONS`, `MAP_STREETS` or `MAP_BUILDINGS`.
- #33's comment and literal pass, apart from the `MAP_*` derivations above,
  which this pass owned by agreement.

**Validation performed**

Headless sweep in Chromium against the real renderer, driving an instrumented
copy of `ashfall.html` (the shipped file plus one line exporting the map
internals). Every label box is read from the element's own `getBBox()` and
transform, so the geometry checked is what the browser drew, not the model the
code places from.

- **Wide — 176 nodes × 4 spans (390/520/650/780) = 704 positions, 11,428
  labels.** Zero overlapping pairs. Zero names outside their street's visible
  stretch. Zero clipped along the street's axis. No street over its tier's
  count. Zero names intersecting the player marker. Closest approach between two
  crossing names: 12.6 units.
- **The same sweep against v0.4.7** (176 nodes at span 800, 4,696 labels):
  **213 overlapping pairs**. This is the #28 regression test.
- **Close — 176 nodes × 3 spans (130/260/390) = 528 positions.** The viewBox is
  exactly the expected player-centred box at every one, and zero street names
  are emitted in any of them.
- **Controls**, clicked through the real UI: opens at Close step 2 with both
  buttons enabled; `+` reaches 130 and disables itself; `−` reaches 390 and
  disables itself; a forced click on a disabled button changes nothing; a zoom
  step leaves the SVG's children untouched (a marker attribute on the first
  child survives every step) while a mode switch replaces them (224 ↔ 66
  children); Close@3 → Wide holds the 390 box; Wide@6 → Close clamps to 3, not
  to base 2; Close@1 → Wide clamps to 3. Neither `+` nor `−` carries
  `data-zoom`.
- `node --check` on the extracted script, and a play-through (move six times,
  switch modes, zoom) with no page or console errors.
- Diff: `git diff origin/main...HEAD -- ashfall.html`.

**Sections touched**

RENDERING, MAP sub-block only — `MAP_ZOOM_RANGE` and the `MAP_LABEL_*`
constants, `mapSetZoomStep()`, `mapTargetViewBox()`, `mapUpdateViewBox()`,
`mapLabelPositions()`, `mapClearCrossings()`, `mapLabelBox()`,
`mapLabelHitsPlayer()`, `mapPositionStreetLabels()`, and the `#mapZoomToggle`
handlers. Plus the two `<button>` elements in the document body, and one line in
the boot sequence.

**Version**: `GAME_CONFIG.VERSION` `"0.4.7"` → `"0.4.8"`

---

## v0.4.7 — WORLD DATA cleanup: street/building split, vestigial exit fields, registry duplicate

Implements: handoffs/world-data-cleanup.md

Implements #3, #4 and #5 in full, per `handoffs/world-data-cleanup.md`. Three
`tier-0` cleanups taken as one pass because they all land in WORLD DATA. No
mechanics, no rendering, no new state fields, no save-format change —
`SAVE_KEY` still derives from `0.4`, so existing browser saves keep loading.

Parts 1 and 2 below are content edits; Part 3 is pure code motion. The only
player-visible change in the whole pass is the item name in Part 2.

**Removed** — WORLD DATA, 26 vestigial `distanceM` fields

`exitMinutes()` reads `exit.distanceM` only when both rooms share a
`locationId`; for a cross-Location exit it calls `locationDistance()` on the
two `LOCATIONS` entries instead and the field is never consulted. 26
cross-Location exits still carried one. All 26 are gone, leaving `{ to, label }`
(plus `doorId` where present), which is the shape the EXIT SCHEMA comment
already documented — this makes the code match a comment that was already
right, so the comment itself needed no edit.

- The 68 same-Location exits are untouched; every one still carries its
  hand-authored `distanceM`.
- `getExitsForRoom()`'s synthesized window-climb exit keeps its `distanceM:4`.
  Both windows (`2a-transom`, `1b-alley`) join rooms inside one Location, so
  that value *is* read; stripping it would have made a climb cost `NaN`
  minutes. It is also built at render time in WORLD INTERACTION, not WORLD
  DATA.

**Removed** — WORLD DATA, the `bandages` registry entry

`ITEM_REGISTRY` carried `bandages` ("Bandages") and `bandage` ("Bandage") as
byte-identical `Medical` / `0.05 kg` entries differing only in display name.
The singular survives; the plural is deleted and its seven references
repointed, every quantity preserved exactly:

- One `SPAWN_POOLS` entry (`{ itemId:"bandage", weight:8, qtyMin:1, qtyMax:3 }`)
  and six world placements (qty 4, 2, 2, 3, 5, 2 — 18 in total).
- The singular wins because it is the `RECIPES` output, so "Craft a bandage"
  no longer produces **Bandages ×1**; and because `Medical` is in `STACKABLE`
  and the detail view appends `×N`, where **Bandage ×4** is unambiguous and
  **Bandages ×4** is not. The registry's other Medical plurals (`Painkillers`,
  `Gauze rolls`) are mass or packaged nouns where `×N` counts containers; a
  bandage is not one of those.

**Organization / Structural** — WORLD DATA, one builder per street and per building

`buildStreetsAndOutdoor()` (60 rooms) and `buildOuterStreets()` (125 rooms) are
deleted and their 185 rooms redistributed across 21 new builders. The old seam
was "original core vs. the v0.4.1 outer ring", which cut through ten of the
sixteen streets — Maple, Main, Water and Poplar each had nodes in both
functions, as did 4th, 2nd, 1st, 3rd and 5th. A room now belongs to the street
its id names, so each street is defined in exactly one place.

- **Five building builders**, matching the existing `buildOakApartments()`
  pattern and placed beside the other building builders: `buildCornerStore()`,
  `buildPharmacy()`, `buildHardwareStore()`, `buildStorageFacility()`,
  `buildRiverbank()`. The v0.2.8 modularity pass extracted one function per
  building but left these four buildings and the riverbank set-piece inside
  the street function.
- **Sixteen street builders**, each merging that street's core and outer
  nodes: `buildDockSt()`, `buildMillSt()`, `buildCedarSt()`, `buildElmSt()`,
  `buildMapleSt()`, `buildPoplarSt()`, `buildMainSt()`, `buildWaterSt()` (15
  rooms each — 8 intersections plus 7 mid-blocks), and `buildSixthSt()`,
  `buildFourthSt()`, `buildSecondSt()`, `buildFirstSt()`, `buildThirdSt()`,
  `buildFifthSt()`, `buildSeventhSt()`, `buildNinthSt()` (7 mid-blocks each).
  They are emitted west to east, the order the grid itself runs in.
- `makeDefaultWorld()` now lists all 26 builders. Its `Object.assign` shape and
  its `applyComputedDirections(world)` return are unchanged.
- `buildOuterStreets()`'s sixteen `// DOCK ST` … `// 9TH ST` group comments are
  deleted rather than moved: the function names now carry what they carried.
  Its header comment describing the core/outer seam went with it, that seam no
  longer existing.
- Every room definition moved verbatim — same id, `locationId`, `desc`, flags,
  containers, floor items and exit list, in the same order within each room.

**Open questions / decisions resolved**

Both placement calls the handoff left open, resolved as it recommended:

- **`outside` goes in `buildPoplarSt()`.** It is the Poplar St / 1st St
  intersection under an id predating the grid, so the id-names-the-street rule
  doesn't reach it. The counts settle it: with `outside` in Poplar, all eight
  named streets own 15 rooms and all eight numbered streets own 7. It is
  **not** renamed to `poplar1st` — `applyLoadedData()` restores a save's world
  wholesale rather than rebuilding it from `makeDefaultWorld()`, so the id
  every existing save already holds has to keep resolving. A comment at the
  definition says so.
- **`alley` goes in `buildPoplarSt()`** too, keeping `buildAcornApartments()`
  strictly interior. The room's own `building:"Poplar St"` field is the
  tiebreak against its `locationId:"acorn_f0"`; it is the one room in the pass
  that neither the naming rule nor the room counts decide, which is why Poplar
  holds 16 rooms where the other named streets hold 15.

**Explicitly NOT changed**

- **No room id, container id or item id renamed**, the `bandages` deletion
  aside. See the `outside` note above for why.
- **No travel time re-tuned.** The 26 stripped values were already unread; see
  Validation below.
- **No new `distanceM` added anywhere**, and no same-Location exit lost one.
- **`SAVE_KEY`, the save format, and `applyLoadedData()`** — untouched. A PATCH
  bump keeps `ashfall_save_v0.4`.
- **No ACTIONS, SIMULATION, PERSISTENCE, or UI/RENDERING code.** `exitMinutes()`
  was read to confirm Part 1's premise and not edited.
- **No balance constant, threshold, or spawn weight.** `bandage` inherits the
  plural's `weight:8, qtyMin:1, qtyMax:3` exactly.
- **The outer nodes keep their empty `containers:[]`.** Placing buildings in
  the 44 new intersections and 81 new mid-blocks is #8, not this pass.
- **`bandage` gains no mechanical behavior.** It still has no `restores`,
  `verb`, `durability` or tags, and "Craft a bandage" is still a dead end;
  that belongs to #23.

**Validation performed**

`git diff origin/main...HEAD -- ashfall.html` is the diff of record (973
insertions, 880 deletions — the net +93 lines is the 21 function headers and
returns replacing 2, plus the `outside` comment). Beyond reading it, the world
was built out of the file before and after and compared:

- **Room set identical.** `Object.keys(makeDefaultWorld())` sorted matches
  exactly, 218 ids before and after.
- **Exit census.** Cross-Location exits carrying `distanceM` went 26 → 0; the
  26 that lost the field are exactly the 26 the handoff named. Same-Location
  exits missing one stayed 0. Totals held at 706 cross and 68 same.
- **Travel times unchanged.** `exitMinutes()` was evaluated for all 774 exits
  at all three gaits — 2,322 probes — with zero differences. This is the real
  test of Part 1: the field being unread was the premise, and this is what
  checks it.
- **Every room otherwise byte-identical.** With the stripped distances and the
  `Bandages`/`bandages` → `Bandage`/`bandage` rename normalized away, all 218
  room objects compare equal, exit order included. Nothing else moved.
- **Window climbs still finite.** Both windows, both directions, all three
  gaits: same-Location and 0:01, not `NaN`. Confirmed again in the browser —
  "Climb through the transom window (0:01)".
- **Syntax and runtime.** The script block parses, and the file was loaded in
  Chromium and driven through the DOM: a route out of the apartment across
  `mid_poplar_1_2`, `alley`, `outside`, `main1st` and `main3rd` (four different
  new builders) reported correct durations at every step, both map views
  rendered (188 node dots, 16 street runs, and the street names inside the
  player-centred window), and the medicine cabinet read
  `Bandage ×4 — 0.20 kg (Medical)`. Zero page errors throughout.

**UI**

- Six world placements and one loot pool now read **"Bandage ×N"** instead of
  **"Bandages ×N"**. Same weight, category, stacking and spawn odds.
- Nothing else the player sees changes: same rooms, same exits, same labels,
  same travel times, same map.

**Sections touched**

**WORLD DATA only** — the room builder functions, `makeDefaultWorld()`,
`ITEM_REGISTRY` and `SPAWN_POOLS`. Content-only in the Project Guide's sense.

**Documentation**

- The EXIT SCHEMA comment needed no edit: it already described the
  post-#4 bimodal shape.
- A comment at `outside`'s definition records that its id is historical and
  why renaming it would strand saves.
- **Nothing was deferred.** The pass surfaced no new work, so no issues were
  filed. #33 (the comment and magic-number pass) was already blocked on this
  one — its audit is expressed in line numbers that Part 3 invalidates — and is
  now unblocked.

**Version**: `GAME_CONFIG.VERSION` `"0.4.6"` → `"0.4.7"`

---

## v0.4.6 — Log: routine lines removed, repeated lines collapsed

Implements: handoffs/log-noise-and-collapse.md

Implements #21 and #22 in full, per `handoffs/log-noise-and-collapse.md`. The
log stops confirming what a panel already shows, and a run of the same action
reports once instead of once per repetition. Rendering behavior — how existing
state changes are surfaced. No mechanics, no world data, no vitals math, no new
state fields, no save-format change.

**Removed** — INVENTORY / ITEM SYSTEM, seven routine `log()` calls

Each failed the same test: does the line tell the player something the screen
doesn't already show?

- `doTake()` and `doStore()` — the item visibly moves between the Here and
  Inventory panels. `doStore()`'s `verb` local went with its line.
- `doEquip()` and `doUnequip()` — a new inventory tab appears, or disappears.
- The battery controls in `getItemActions()`: on/off (the detail view already
  reads "— On" / "— Off"), removal (the batteries appear in inventory and the
  view reads "No batteries installed") and replacement (the charge readout
  jumps to 100%).
- Every failure and redirect still speaks: "That won't fit", "No room for the
  … — it drops to the floor instead", "Your keychain can't hold that", "You're
  already carrying something in that slot", and every consequence line with no
  visible counterpart.
- `doConsume()` keeps its line. Eating is the one case where the panels don't
  tell the story: the item count drops, but the effect lands on Hunger and
  Thirst, which live behind the ☰ menu and are invisible during normal play.

**New** — EVENTS / UI HELPERS, collapsing consecutive runs

- `log(text, cls)` becomes `log(text, cls, key, outcome)`. Both new parameters
  are optional and every existing unkeyed call site behaves exactly as before:
  it never collapses, and nothing collapses into it.
- With a `key`, the line collapses into `#log`'s last child if that child
  carries the same `dataset.logKey`; otherwise it appends a new element
  carrying it. **Only consecutive runs collapse.** Any intervening line breaks
  a run — including a `warn`, on purpose: a string of ten "That won't fit"
  failures is worth seeing in full, and hiding repeated failures would hide a
  stuck player from themselves. `fish, fish, chop, eat, eat, drink, fish, eat`
  logs as `fish, chop, eat, drink, fish, eat`.
- **Tally actions** (fixed text) key on the action and re-render as prose from
  the second occurrence: `doFish()` as `fish` with `bite`/`miss` outcomes,
  `doRest()` as `rest`, `doChopTree()` as `chop`, `doAddFuel()` as `fuel`. The
  four sentences live in one `LOG_SUMMARIES` table beside `log()`: "You fish
  seven times. Three bites." / "Nothing bites." / "One bite." for the
  degenerate counts, "You rest for three hours.", "You chop down three
  trees.", "You feed three more pieces of wood into the fire."
- **Counted actions** (the text names an object) keep their sentence and class
  and gain a dim trailing `<span class="logcount">×3</span>`. Their keys carry
  the object — `consume:` + item id, `craft:` + output id, `cook:` + recipe id
  — so eating three different things can never render as one line naming the
  first. New style: `.logcount{ color:var(--ink-faint); font-size:11.5px;
  margin-left:5px; }`, so the count reads as functional UI rather than as part
  of the prose.
- `numberWord()` in UTILITIES, beside `fmtDuration()`: spelled out through
  ten, digits from eleven up, matching the game's prose.
- On collapsing a tally run the element's outcome class is cleared — a fishing
  run mixes a `good` bite with an unclassed miss, and the summary is a neutral
  report of both. Counted runs keep their class.
- `.fresh` follows its existing rule unchanged — stripped from every line,
  then applied to the line just written when `cls` is falsy — so the newest
  line stays highlighted whether it was appended or rewritten in place.
- Runs may span movement: `doMove()` logs nothing, so chopping a tree in three
  rooms in a row still collapses to one line. Intended.
- `doSearch()` is deliberately unkeyed: a room can only be searched once and
  different rooms would key differently, so it could never collapse.
- The 50-entry cap and the scroll-to-bottom behavior are unchanged.

**UI**

- Taking, storing, equipping, unequipping and servicing batteries are silent.
  Their failure warnings are not.
- Eating and drinking still report.
- A repeated action reads as one line: "You fish seven times. Three bites." /
  "You rest for three hours." / "You chop down three trees." / "You eat the
  canned soup. ×3".
- Failures never collapse.

**Sections touched**

- EVENTS / UI HELPERS — `log()`, the new `LOG_SUMMARIES` table.
- UTILITIES — the new `numberWord()` and `NUMBER_WORDS`.
- INVENTORY / ITEM SYSTEM — five removed `log()` calls across `doTake()`,
  `doStore()`, `doEquip()`, `doUnequip()` and the battery actions in
  `getItemActions()`; one key added in `doConsume()`.
- FIRE / COOKING — keys in `doFish()`, `doAddFuel()`, `doChopTree()`,
  `doCookInContainer()`.
- CRAFTING — key in `doCraft()`.
- WORLD INTERACTION — key in `doRest()`.
- The document `<style>` block for `.logcount`.

Only the `log()` calls inside those action functions changed; no ACTIONS
logic, no simulation rule and no vitals math was touched.

**Open questions / decisions resolved**

The handoff left four implementation calls open; all four took its recommended
default.

- **Where the summary text lives**: one `LOG_SUMMARIES` table next to `log()`,
  keyed by action id and taking the tally object — not sentences built at the
  four call sites. A future content pass edits all four strings in one place.
- **How a call site passes its outcome**: a fourth optional parameter
  defaulting to the key itself, so only `doFish()` names an outcome
  (`bite`/`miss`) and the three single-outcome actions pass nothing extra.
- **`numberWord()` placement**: UTILITIES, beside `fmtDuration()`.
- **When a tally run starts tallying**: from the first occurrence, so the
  transition at n = 2 is a re-render rather than a reconstruction.

**Notes / assumptions**

- The two battery-servicing removals ("You pull the batteries out of the …",
  "You put fresh batteries in the …") are an **explicit extension of #21's
  original table by two call sites**, made because they fail the same test and
  leaving them would have made the battery controls inconsistent — silent when
  toggled, chatty when serviced.
- Collapse state lives on the `<p>` element: `dataset.logKey` for matching and
  a `_logTally` expando for the counts, since `dataset` values are strings.
  Nothing about the log is in `state`, so nothing about it is serialized.
- `doConsume()`'s key is `"consume:" + (it.itemId || it.name)`. The handoff
  specified `it.itemId`; the name fallback is a guard for the runtime-literal
  items the remaining `giveItem()` call sites still build (the `tier-0`
  registry cleanup), which would otherwise all key as `consume:undefined` and
  collapse different foods into one line.
- The summary wording is the handoff's, including "You fish two times." for a
  run of exactly two — retunable prose, not a settled style rule.

**Explicitly NOT changed**

- `#log`'s 110px cap, its 50-entry trim, its gap and its line styles.
- `serializeGame()`, `applyLoadedData()`, `doRestart()`'s `innerHTML = ""`.
  `SAVE_KEY` is unchanged: `versionCompat()` reads `MAJOR.MINOR`, and this
  pass adds no state.
- Illness, vitals, `doConsume()`'s mechanics — only its `log()` call's key.
- `doSearch()`, `doSleep()`, `doLightStove()`, `doBuildFire()`,
  `doExtinguish()`, `doDismantleCampfire()`, the door/window lines, the save
  and load `sys` lines, and every `warn` in the file: all unkeyed, all
  unchanged.
- No vitals readout was added outside the ☰ menu, per the handoff.

**Validation performed**

Driven in headless Chromium against an instrumented copy, with `Math.random`
scripted where an outcome had to be forced:

- Seven fishing attempts, three bites: one line, "You fish seven times. Three
  bites." Two attempts with one bite: "You fish two times. One bite." Three
  attempts, no bites: "You fish three times. Nothing bites." A single attempt
  keeps its ordinary sentence with no summary.
- A fishing run broken by an intervening `warn` produces two fish lines with
  the warning between them, not a run of two.
- Rest ×3 → "You rest for three hours."; ×12 → "You rest for 12 hours."
  (digits above ten). Fuel ×3 → "You feed three more pieces of wood into the
  fire." Chop ×3 across three different rooms → "You chop down three trees.",
  confirming a run spans movement.
- Eating the same item three times then a different one: two lines, "You eat
  the canned soup. ×3" and "You eat the granola bars." Alternating two items
  four times: four separate lines, never collapsed. Three raw fish where the
  second triggers the illness warning: "×2", the warning, then a fresh line.
- Crafting the same recipe twice: one line with "×2".
- Equipping, unequipping, storing and taking, all four verified to have
  actually moved the item: **zero** log lines. The following "That won't fit
  there." warning still appears. Battery on/off, removal and replacement write
  nothing.
- `.fresh` lands on the rewritten line when the collapsing call is unclassed,
  and exactly one line carries it.
- The cap holds: 60 filler lines plus a collapsed rest run leaves exactly 50
  children with the summary last.
- `node --check` on the extracted script; no page or console errors in any
  scenario.
- Re-ran v0.4.4's and v0.4.5's own validations against this build: 672/102
  exit split intact with all 224 head/block pairs ordered, 42 rooms hiding
  Move, and the Wide map still exactly player-centred with label counts
  matching their tiers.

**Explicitly out of scope**

Per the handoff: no resizing or restyling of `#log`, no vitals readout outside
the ☰ menu, no change to illness or vitals, no summarising across
non-consecutive occurrences (rejected during planning — it deletes the events
between survivors and implies an order that didn't happen), and no collapsing
of `warn` lines. #23 (illness system) is the recorded home of the
hidden-vitals finding and is untouched.

**Documentation**

- The ARCHITECTURE comment's "Current version" line is bumped to 0.4.6.
- Filed #29: re-judge `#log`'s 110px cap and 50-entry limit against the
  quieter feed. The handoff deferred this explicitly on the grounds that it
  has to be judged in play rather than guessed at; the issue records the
  current values and says so.
- Nothing else was deferred out of this pass.

**Version**: `GAME_CONFIG.VERSION` `"0.4.5"` → `"0.4.6"` (third of three
passes in this pull request: `"0.4.3"` → `"0.4.4"` → `"0.4.5"` → `"0.4.6"`)

---

## v0.4.5 — Wide map: panning, zoom placeholders, viewport-relative labels

Implements: handoffs/wide-map-panning.md

Implements #19 and #20 in full, per `handoffs/wide-map-panning.md`. The Wide
map now centres on the player and slides as they move; street names are placed
against the part of each street on screen; two inert `+` / `−` buttons reserve
the layout slot for a later zoom pass. Rendering-only, MAP sub-block. No
mechanics, no world data, no new state fields, no save-format change.

**Changed / Reworked** — RENDERING / MAP, Wide is a span, not a box

- `MAP_WIDE_VIEWBOX = { x:20, y:20, w:1000, h:1000 }` is replaced by
  `MAP_WIDE_VIEW = 800`, a span mirroring `MAP_CLOSE_VIEW = 260`.
  `mapTargetViewBox()` collapses to one code path for both modes: a
  player-centred box of the active span. Wide never panned before because its
  target was a constant; nothing in `renderMap()` or `mapUpdateViewBox()`
  needed changing to make it pan, and the existing 350ms ease-out animation
  now runs for Wide moves too.
- The span had to shrink for panning to mean anything. Node extents run 55 →
  965 on both axes — 910 units — so a 1000-unit box has almost nothing to pan
  within. At span 800 the box ranges over x ∈ [−345, 565] as the player
  crosses town, which is the full width of the grid.
- The box is **not clamped** to content bounds. At the western edge a
  player-centred Wide box is 47% empty canvas; Close at the same spot is
  already 40% empty. Clamping was rejected: the ask was for Wide to pan the
  way Close does, and clamping would also stop Wide panning at all for any
  span ≥ 960.
- The player marker is untouched: `r="5"` in Close, `MAP_PLAYER_R_WIDE = 12`
  in Wide.

**Changed / Reworked** — RENDERING / MAP, street names placed against the viewport

- `mapBlockLabels()` is gone. It emitted one `<text>` per block at build time
  — 7 blocks × 16 streets = 112 labels — which stops meaning anything once the
  view moves.
- `renderMapWide()` now emits a fixed pool of `MAP_LABELS_PER_STREET` (3)
  empty, hidden `<text class="map-street-name" data-street="N">` nodes per
  street: 48 in total, created once per Wide render and thereafter only moved,
  shown or hidden. Nothing is created or destroyed during a pan.
- `mapBindStreetLabels()` caches that pool as element references, plus each
  street's endpoints and heading angle, in the module-level `mapStreetLabels`.
  It runs from `renderMap()` right after the SVG content is rebuilt, and
  clears the pool for Close, which emits no street names at all.
- `mapPositionStreetLabels(box)` places them. Every street run is
  axis-aligned, so visibility is a 1-D clamp: a horizontal street is on screen
  only if its single `y` lies inside the box, and its visible stretch is
  `[max(min(ax,bx), box.x), min(max(ax,bx), box.x + box.w)]`; vertical streets
  are the same with the axes swapped. Label count follows `MAP_LABEL_TIERS` on
  that stretch's length — 3 at ≥ 600, 2 at ≥ 300, 1 at ≥ 110, none below —
  positioned at `lo + MAP_LABEL_INSET`, the midpoint, and `hi −
  MAP_LABEL_INSET` (one label sits at the midpoint alone). Unused pool nodes
  get `display:none`.
- Rotation and offset are v0.4.3's logic unchanged: the label rides its
  street's heading folded into `(-90, 90]`, so vertical streets still read
  bottom-to-top, offset off the line by `MAP_LABEL_OFFSET = 5`. This pass
  changes where labels sit, never which way they read.
- Labels are repositioned wherever the viewBox is set — the snap branch of
  `mapUpdateViewBox()` and every `requestAnimationFrame` step — since the
  placement is relative to the window, not to the street.

**UI**

- Wide shows about 80% of the town at a time, centred on the player, sliding
  as they move, instead of the whole town fixed in place.
- On-screen street names drop from 112 to at most 42, averaging 26.7 across
  all 176 street positions.
- Two greyed-out `+` / `−` buttons sit to the right of Wide, in that order,
  using `&minus;` so they read as a matched pair. They are `disabled`, carry no
  handler, and deliberately carry **no `data-zoom` attribute** — the mode
  toggle binds `#mapZoomToggle button[data-zoom]`, and giving the placeholders
  that attribute would have broken the Close/Wide switch. They get the
  existing disabled treatment, `#mapZoomToggle button:disabled{ opacity:.4;
  cursor:not-allowed; }`, matching `#gaitBar`.
- Near the town's edges Wide shows empty canvas past the player, as Close
  already does.

**Removed**

- `mapBlockLabels()` and `MAP_WIDE_VIEWBOX`. Replaced by the label pool and
  `MAP_WIDE_VIEW` respectively.

**Sections touched**

UI/RENDERING, the MAP sub-block only — `mapTargetViewBox()`,
`mapUpdateViewBox()`, `renderMapWide()`, `renderMap()`, the new
`mapBindStreetLabels()` / `mapPositionStreetLabels()` / `mapLabelPositions()`,
the `#mapZoomToggle` markup, and one rule in the document `<style>` block.

**Open questions / decisions resolved**

The handoff left four implementation calls open; all four took its recommended
default.

- **Per-frame vs. on-settle label repositioning**: per frame, inside
  `step()`. At most 48 nodes exist and only `transform` and `display` change,
  so no element is created or destroyed mid-animation. Verified mid-pan:
  labels track the intermediate box, not the target.
- **Where the pool lives**: a module-level array of element references,
  `mapStreetLabels`, populated once per rebuild — the DOM is not re-queried
  per frame. Mirrors how `mapPositionPlayer()` resolves `#mapPlayer`.
- **Button order and glyphs**: `+` then `−`, using `&minus;`.
- **Four named constants or one table**: one table, `MAP_LABEL_TIERS`, read by
  `mapLabelPositions()` via a `find()` on the longest matching tier. No inline
  magic numbers.

**Notes / assumptions**

- `MAP_WIDE_VIEW = 800`, `MAP_LABEL_INSET = 55`, and all three
  `MAP_LABEL_TIERS` thresholds (600 / 300 / 110) are **retunable** and have no
  prior convention behind them. 800 is the smallest span that both zooms in
  noticeably and leaves room to pan; 55 is half the widest street name
  (`POPLAR ST`, 99.1 units at 15px), which is what keeps a full-width label
  inside the visible span instead of clipped at its edge.
- The 1-label tier is currently unreachable: sweeping all 176 street nodes at
  span 800 produced only 0-, 2- and 3-label streets. It is kept because the
  spans a working zoom introduces (#27) will reach it.
- Zoom mode stays a module-level `let`, not a field on `state`, so
  `versionCompat()` still yields `"0.4"` and `SAVE_KEY` is unchanged.
  Persisting a zoom level would have made this MINOR.

**Explicitly NOT changed**

- Close view: `renderMapClose()` is untouched, its span stays 260, its marker
  stays `r="5"`, and it still emits zero `text.map-street-name` nodes.
  Re-checked after a Wide round trip.
- `LOCATIONS`, `MAP_STREETS`, `MAP_BUILDINGS`, `MAP_STREET_NODE_IDS`,
  `MAP_SPACING`, `MAP_MARGIN`, `mapToSvg()`, `mapPathD()`,
  `mapPositionPlayer()` — no node moves.
- The viewBox is not clamped in either mode; Close's own edge behavior is
  unchanged.
- `serializeGame()`, `SAVE_KEY`, and every balance constant outside the MAP
  sub-block.

**Validation performed**

Driven in headless Chromium against an instrumented copy of the new file:

- The Wide viewBox is exactly player-centred at every one of 14 sampled
  positions across two full-width walks (POPLAR ST west → east, 1ST ST south →
  north, plus the four grid corners): `box.x === px − 400` and
  `box.y === py − 400` with no exception.
- Sampled mid-animation as well as settled: the box is intermediate and the
  labels are placed against that intermediate box, confirming per-frame
  repositioning.
- Swept **all 176 street/mid-block nodes**. At every position, each street's
  label count matches `MAP_LABEL_TIERS` applied to its own visible stretch
  (992 two-label streets, 904 three-label, 920 with none, zero mismatches); no
  label falls outside its street's visible span; and no label — measured with
  its real rendered width — is clipped at a span edge. Peak 42 labels on
  screen, mean 26.7.
- Close view after load and after a Wide round trip: `viewBox` back to the
  260-span player-centred box, player `r="5"`, 11 building dots, 19 building
  labels, 176 node dots, 0 street-name nodes, empty label pool.
- The `+` / `−` buttons are present, `disabled`, rendered at `opacity:.4` with
  `cursor:not-allowed`; clicking both changes neither the zoom mode, the
  active-button class, nor the viewBox.
- No page or console errors on load, on toggling modes, or across the walks.
- `node --check` on the extracted script; `git diff main -- ashfall.html`
  confirms the MAP sub-block, the markup and the one CSS rule are all that
  moved.
- One property the handoff asked for did **not** hold: labels can collide at
  an intersection. 116 of the 176 positions show at least one overlapping
  pair, worst case `ELM ST` over `3RD ST` at 17 × 17 units. It is inherent to
  the placement rule as specced — an inset position often lands near a
  crossing, where two 15-unit-tall name bands can cross — so this pass shipped
  the rule as written and filed #28 rather than inventing a placement rule the
  handoff didn't specify.

**Explicitly out of scope**

Per the handoff: no working zoom (the buttons ship inert), no persisted zoom
level, no viewBox clamping, no change to Close view or to any map geometry
constant. Close-map building-label clipping and phone-viewport overflow (both
findings under #16) live in nearby code and are untouched; #16 stays open.
Building placement in the outer ring (#8) is unrelated.

**Documentation**

- The ARCHITECTURE comment's "Current version" line is bumped to 0.4.5.
- Filed #27: make the `+` / `−` controls work, carrying the handoff's
  recommendation that the zoom variable be scoped per mode so Close and Wide
  each scale from their own base span, plus the note that
  `MAP_LABEL_TIERS` needs re-checking at any new span.
- Filed #28: Wide-map street names can collide at an intersection, with the
  measured sweep above and three candidate fixes.

**Version**: `GAME_CONFIG.VERSION` `"0.4.4"` → `"0.4.5"`

---

## v0.4.4 — Exit split: grid travel vs. Here

Implements: handoffs/exit-move-split.md

Implements #18 in full, per `handoffs/exit-move-split.md`. Rendering-only:
the Move panel now holds street travel alone, ordered by compass, and every
other exit renders at the top of Here. No WORLD DATA, no PLAYER STATE, no
mechanics, no save-format change.

**Changed / Reworked** — UI/RENDERING, exit panels

Every exit used to render as a Move button in `exits`-array authoring order,
so "Climb the stairs", "Enter the pharmacy" and "Climb through the window" all
sat under a heading that means travel, and a street's four directions came out
in whatever order the world data happened to list them.

- New `isGridTravel(fromId, toId)` in WORLD INTERACTION, beside
  `getExitsForRoom()`: an exit is grid travel if and only if both endpoints are
  street/mid-block nodes, which the ROOM SCHEMA marks by giving such a room its
  own id as its `locationId`. This is deliberately *not* the cross-Location
  test (`fromRoom.locationId !== toRoom.locationId`), which sends 706 of the
  world's 774 exits to Move — 34 too many, among them the stairwells, the
  apartment-over-shop doors, the `balcony → alley` fire escape and every
  "Enter the …" building door.
- `renderMoveActionsPanel()` filters `getExitsForRoom()` to grid travel and
  sorts it by `MOVE_DIRECTION_RANK` — `north:0, east:1, west:2, south:3` —
  keyed on `computeDirection()` of the two rooms' `locationId`s. No label
  parsing and no new exit field: `computeDirection()` already reproduces the
  compass word in every grid exit's own label.
- The sort has no secondary key on purpose. `Array.prototype.sort` is stable,
  which is what keeps each intersection's "Head …" exit ahead of its
  "Step into the block …" exit — the relationship is authoring order, not
  something re-derived from label text.
- `renderHereActionsPanel()` renders the non-grid exits first, above the
  locked-door notices, in unmodified authoring order, with their existing
  `fmtDuration(exitMinutes(exit))` cost suffix and `actionButton` styling.
  Window-climb exits are among them: `getExitsForRoom()` still generates them
  and they still track window state; only their parent panel changed.
- `getExitsForRoom()` is untouched — same signature, same one list, same
  window handling. Each panel filters it.

**UI**

- Indoors the Move group disappears entirely: the static markup's Move
  `.actions-group` gained `id="moveGroup"`, and the panel hides it when it
  holds no buttons, mirroring `hereGroup`. 42 of the game's 218 rooms are
  non-street rooms, so an empty "MOVE" heading was the common case indoors.
- The game-over branch of `render()` returns before
  `renderMoveActionsPanel()` runs and puts its "Restart" button in
  `moveActions`, so it now sets `moveGroup` back to visible — otherwise dying
  indoors would have left Restart behind a hidden group.
- On a street, Move holds only travel, ordered North, East, West, South.
  Nine street rooms with building entrances gain a Here section; the other
  167 still show none.
- No button label, cost, or styling changed.

**Sections touched**

- UI/RENDERING — `renderMoveActionsPanel()`, `renderHereActionsPanel()`,
  `render()`'s game-over branch, and the static Move `.actions-group` markup.
- WORLD INTERACTION — one added helper, `isGridTravel()`.

**Open questions / decisions resolved**

The handoff left three narrow implementation calls open; all three took its
recommended default.

- **Where the classification helper lives**: WORLD INTERACTION, beside
  `getExitsForRoom()`, which already owns "which exits does this room offer".
  It reads WORLD DATA and is consumed by RENDERING, so RENDERING was the other
  candidate.
- **One list or two**: one. `getExitsForRoom()` keeps its signature and each
  render function filters, which keeps window-exit generation in a single
  place and makes the change provably additive.
- **A visual separator for the relocated exits in Here**: none. They are
  ordinary action buttons and the panel already mixes kinds. If they read as
  crowded in play, that is a follow-up.

**Notes / assumptions**

- The compass order North/East/West/South comes from the handoff, not from a
  prior convention in the code — it is the retunable part of this pass.
- An unknown direction ranks 4, after `south`, rather than resolving to
  `undefined` and poisoning the comparator. No street node can currently
  produce `up`/`down` (every one is `z:0`), but the sort no longer depends on
  that staying true.

**Explicitly NOT changed**

- No `exits` array is reordered, renamed, or given a new field; no exit label,
  `distanceM`, or duration changed.
- `getExitsForRoom()`'s body, `doMove()`, `exitMinutes()` and
  `computeDirection()` are untouched.
- The Here panel's existing actions (locked doors, Rest, Sleep, Search,
  windows, vehicle, fishing, stove, fire, tree, container locks) keep their
  order; the relocated exits are inserted ahead of them.
- `SAVE_KEY` is unchanged — `versionCompat()` reads `MAJOR.MINOR`, so a PATCH
  bump keeps existing browser saves loading.

**Validation performed**

Driven in headless Chromium against an instrumented copy of the new file,
walking all 218 rooms and all 774 exits:

- The split classifies 672 exits as grid travel and 102 as everything else,
  matching the handoff's verified counts exactly. 176 rooms satisfy
  `locationId === id`.
- Every street room's Move buttons match the expected filtered-and-sorted
  list, label for label; direction ranks are monotonic in all 176 street
  rooms; the compass word in every grid label agrees with the computed
  direction. Move-button counts per street room: 2 buttons in 112 rooms, 4 in
  4, 6 in 24, 8 in 36.
- All 224 two-exit direction buckets render "Head …"/"Continue …" before
  "Step into the block …", with no secondary sort key.
- All 42 non-street rooms hide the Move group; no street room hides it.
- In the nine street rooms with non-grid exits, the relocated exits render
  first in Here and in authoring order.
- Both windows, driven through `closed` and `open` in both of their rooms:
  the climb exit appears in Here and never in Move when open, and is absent
  from both when closed.
- No page errors or console errors during the walk.
- The diff is the proof of the data claim: `git diff main -- ashfall.html`
  (equivalently `git diff v0.4.3:ashfall_0_4_3.html`, since the release tags
  predate the filename-normalization pass) touches only the five sites listed
  under **Sections touched** and the version constants.

**Explicitly out of scope**

Per the handoff: no reordering of the Here panel's existing actions, no
compass-rose or spatial button layout (a rose degrades badly in the many rooms
with no directional exits), no change to `exits` data or labels, no renaming
of the "Move" and "Here" headings. #4 (vestigial `distanceM` on cross-Location
exits) is adjacent but not a prerequisite. Phone-viewport layout (#16) and map
rendering (#19, #20) are untouched.

**Documentation**

- The ARCHITECTURE comment's "Current version" line is bumped to 0.4.4.
- Filed #26: the `git diff vX.Y.Z -- ashfall.html` recipe in the Project Guide
  and the changelog guide no longer resolves, because every existing release
  tag predates the rename to `ashfall.html` and carries a versioned filename
  instead.
- Nothing else was deferred out of this pass.

**Version**: `GAME_CONFIG.VERSION` `"0.4.3"` → `"0.4.4"`

---

## v0.4.3 — Wide-view map readability

No handoff file — a direct request to make the side-menu map's Wide view
legible. Scoped to the MAP sub-block of RENDERING plus the document
`<style>` block. No mechanics, no world data, no new state fields, no
save-format change.

**Changed** — RENDERING / MAP, one street name per block

Wide view drew each street as a single continuous `<textPath>` carrying
`mapRepeatedLabel()`'s three copies of the name spaced by bullets, so a
street read `1ST ST • 1ST ST • 1ST ST` with the copies falling wherever
the path put them rather than on anything meaningful.

- `mapRepeatedLabel()` is gone, replaced by `mapBlockLabels(name, chain)`.
  Every chain in `MAP_STREETS` alternates intersection, mid-block,
  intersection, so its even indices are the intersections; the function
  walks them in steps of two and emits one `<text>` per block, centred
  between the two intersections that bound it. That is exactly one name
  per block, each one centred on its own block.
- Each label is rotated onto its block's heading, folded into `(-90, 90]`
  so vertical streets read bottom-to-top instead of upside down, and
  offset off the line by `MAP_LABEL_OFFSET` (5 units) so the name sits
  beside the street rather than on it.
- `renderMapWide()` no longer emits the `<defs>` block of
  `mapstreetpath-N` paths, since nothing references them now; it draws
  every street line first and every label after, so no run is painted
  over its own names.
- Labels are `<text transform="translate(...) rotate(...)">` rather than
  `<textPath>`. The grid is axis-aligned, so a block's heading is always
  0 or ±90 and the flat transform is enough — no path-following needed.

**Changed** — RENDERING / MAP, player marker

- New `MAP_PLAYER_R_WIDE` (12), used for `#mapPlayer` in
  `renderMapWide()` only. Wide's viewBox is 1000 units against Close's
  `MAP_CLOSE_VIEW` of 260, so the shared radius of 5 rendered at roughly
  4px across and read as another node dot. `renderMapClose()` still
  emits `r="5"`.

**UI**

- `#sideMenu` width 360px → 460px, with `max-width:92vw` added so the
  panel still fits a phone-width viewport. Wide's viewBox is fixed, so
  the whole map scales up with the panel.
- `.map-street-name` font-size 11px → 15px, letter-spacing 2px → .5px.
  The looser tracking was there to stretch names along a whole street
  run; with one name per block the size is what matters and the tracking
  only costs width.

**Explicitly NOT changed**

- Close view: `renderMapClose()` is untouched — same street paths, node
  dots, building dots and labels, same `r="5"` player marker.
- `LOCATIONS`, `MAP_STREETS`, `MAP_SPACING`, `MAP_MARGIN`,
  `MAP_WIDE_VIEWBOX`, `mapToSvg()` and `mapPathD()` — the grid geometry
  and every street run are identical, so no node moved.
- `mapPositionPlayer()`, `mapTargetViewBox()`, `mapUpdateViewBox()` and
  `renderMap()` — marker tracking and the Close-view viewBox animation
  are unchanged.
- Movement, exits, compass wording, world data and the save format.
  `versionCompat()` truncates to `"0.4"`, so `SAVE_KEY` is unchanged and
  a v0.4.0–v0.4.2 save still loads with no version warning.

**Validation performed**

Driven in headless Chromium against the real file, Wide view open:

- 112 labels rendered — 16 streets × 7 blocks — one per block, with each
  of the 16 names appearing exactly 7 times.
- Widest label (`POPLAR ST`) measures 99.1 units against a block length
  of 130 (`MAP_SPACING`), and no label exceeds its block, so nothing
  overflows into a neighbouring block or an intersection.
- No page or console errors on load, on the Close↔Wide toggle, or while
  moving.
- Close view re-checked after the change: player `r="5"`, 11 building
  dots, and zero `text.map-street-name` nodes, matching v0.4.2.
- Player marker in Wide: `r="12"`, 10.2px across on screen against ~4px
  before, and it tracks movement — walking Poplar St west from between
  1st & 2nd stepped the marker 380 → 315 → 185 → 55 in SVG units, with
  the viewBox correctly staying fixed at `20 20 1000 1000`.
- Panel measured at 460px with the map SVG at 423px.

**Notes / assumptions**

- The 460px panel width, 15px type, `MAP_PLAYER_R_WIDE` of 12 and the
  5-unit `MAP_LABEL_OFFSET` are tuned by eye against the current 130-unit
  block, with no prior convention behind them — all four are retunable.
- 15px leaves 31 units of slack on the longest street name. A future
  street name longer than about 11 characters, or a smaller
  `MAP_SPACING`, would need the size dropped or the name abbreviated;
  nothing in the code enforces the fit.

**Version**: `GAME_CONFIG.VERSION` `"0.4.2"` → `"0.4.3"`

---

## v0.4.2 — Missing Item Category Population

Implements the "Ashfall Handoff — Missing Item Category Population"
handoff in full. Continuation of the v0.4.0 `SPAWN_POOLS`/`ITEM_REGISTRY`
work, closing the category gaps a post-v0.4.0 audit found. Content pass
(WORLD DATA) plus the small RENDERING generalization the new equippable
bags needed — no new mechanics, no new state fields, no save-format
change.

**New content** — WORLD DATA, `ITEM_REGISTRY`

36 new entries, 119 → 155. Weights are estimates consistent with existing
entries for similar real-world items; retunable.

- **Pet supplies** (none existed): `dry_pet_food`, `canned_pet_food`,
  `pet_leash`, `pet_collar`, `pet_toy`, `cat_litter`, `pet_carrier`.
- **Baby/child** (2 existed): `diapers`, `baby_formula`, `pacifier`,
  `childrens_book`, `toy_action_figure`, `baby_blanket`. `baby_formula`
  deliberately carries no `restores` — it is flavor, not player food.
- **Self-defense** (police-only items existed): `baseball_bat` and
  `riot_baton` (`blunt`), `combat_knife` (`blade`), `pepper_spray`,
  `stun_gun`.
- **Cleaning supplies**: `dish_soap`, `laundry_detergent`,
  `rubber_gloves`, `trash_bags`.
- **Documents/lore**: `dated_newspaper`, `personal_journal`,
  `unsent_letter`, `utility_bill`, `missing_person_flyer` — generic item
  types only, per Design decision 2.
- **Electronics**: `walkie_talkie` (`battery`), `dead_cellphone`,
  `disposable_camera`.
- **Money/valuables**: `gift_card`, `checkbook`.
- **Equippable bags**, `category:"Container"`, following `worn_backpack`
  exactly: `duffel_bag` (`duffel`, 18 kg), `tote_bag` (`tote`, 8 kg),
  `purse` (`purse`, 5 kg), `fanny_pack` (`fannypack`, 3 kg).

**New content** — WORLD DATA, `SPAWN_POOLS`

- 5 new pools, 23 → 28: `pet_supplies` (`rollCount:[1,2]`,
  `emptyChance:0.2`), `baby_items` (`[0,2]`, `0.3`), `self_defense`
  (`[0,1]`, `0.35`), `cleaning_supplies` (`[1,2]`, `0.15`) and
  `electronics` (`[0,1]`, `0.3`). Roll counts and empty chances are the
  handoff's; per-entry weights follow the existing convention (commoner
  items 5-8, rarer or bulkier ones 1-3) and are flagged retunable in the
  code comment.
- 6 existing pools extended: `hygiene` (+ the four cleaning items, at
  lower weights than its bathroom staples), `valuables` (+ `gift_card`,
  `checkbook`), `police_gear` (+ `riot_baton`), `office_supplies` and
  `residential_personal` (+ the electronics), and `documents_lore` (+ the
  five document types).
- `spawnPools` added on **20 existing containers**, alongside their
  current pools rather than replacing them: `pet_supplies` on four
  residential closets/dressers, `baby_items` on two bedroom containers,
  `self_defense` on the two nightstands, one Oak dresser and the hardware
  store's Tool Wall, `cleaning_supplies` on both under-sink cabinets, the
  superintendent's tool cabinet and closet and the corner store's back
  room, and `electronics` on the five `office_supplies` containers and
  both nightstands. Each new pool lands on at least one container that
  still has its roll pending, so every one of them can actually appear in
  play rather than only mattering to a future respawn cycle.
- 4 hand-placed (not pool-rolled) bags, one per building, following the
  `worn_backpack` precedent: `duffel_bag` in Acorn 2B's closet, `purse`
  in Acorn 1A's open suitcase, `tote_bag` in the flat above the corner
  store, `fanny_pack` in the flat above the hardware store. All four
  containers already carried authored contents and `spawnRolled:true`, so
  placing a bag there costs no container its spawn roll.

**Changed** — RENDERING and PLAYER STATE, slot generalization

The equip mechanism was already generic (`state[it.slotType]`), but four
places named `"keychain"`/`"backpack"` by hand, so a new `slotType` would
have silently had no tab and no Unequip button. Design decision 3 resolved
to option **(b)**, the fuller generalization, so the next bag type needs
no RENDERING edit at all:

- New `CONTAINER_SLOTS` and `SLOT_LABELS` (WORLD DATA, beside
  `itemsFromRegistry`), derived from `ITEM_REGISTRY` rather than listed.
  `keychain` is named explicitly in both, since it is the one slot that
  isn't a found item.
- New optional `slotLabel` registry property for slots whose key doesn't
  capitalize into a good tab name — `"Fanny Pack"`, `"Duffel Bag"`,
  `"Tote Bag"`. `worn_backpack` needs none, so its tab still reads
  "Backpack" exactly as before.
- `invTabDefs` and the unequip-button condition (`renderInventoryPanel`),
  `invSlot()` and `invPools()` now all read `CONTAINER_SLOTS` instead of
  naming slots. Tab order is unchanged for existing saves: Inventory,
  Keychain, Backpack, then any new bag in registry order.
- `makeDefaultState()` derives its empty slots from `CONTAINER_SLOTS`
  instead of the literal `backpack:null`, so a new bag type needs no edit
  there either.
- `keychainAllows()` is untouched and still restricts the keychain to
  `Key` items. That restriction is deliberately not inherited by the new
  bag slots.

**UI**

- Equipping a duffel bag, purse, fanny pack or tote bag adds an inventory
  tab named for it, with a working Unequip button, matching the existing
  Backpack tab's behavior exactly.

**Explicitly out of scope** (per the handoff)

- **Firearms and any combat/ammo mechanics** — Design decision 1,
  resolved to the recommended default of excluding them entirely. A
  working firearm needs ammo tracking, reload and a combat system that
  doesn't exist; inert loot would mislead the player. Deferred to roadmap
  item 6 (Zombies/Threats) so the item and its mechanics ship together.
  `stun_gun` and `pepper_spray` are in, being non-firearm deterrents with
  no ammo model implied.
- **Deep, personalized lore content** for the new document items —
  Design decision 2, resolved to the recommended default. The item
  *types* ship with plain generic names; writing dated, location-specific
  content for them is roadmap item 13's job and this pass does not
  fulfill it.
- Container property tags, the no-respawn flag and fauna (roadmap item
  15); new buildings to house these categories properly — a pet store,
  nursery or sporting-goods store (roadmap item 14's remaining half);
  map expansion, which shipped separately in v0.4.1.

**Validation performed**

Audited with a harness that evaluates the real `<script>` body under a
DOM stub and drives the assembled game, plus a real-browser check:

- All 36 new items resolve with the exact category and weight the handoff
  specced, checked entry by entry against a transcription of its tables.
  `baby_formula` confirmed to carry no `restores`.
- No firearm- or ammunition-shaped id exists in `ITEM_REGISTRY`.
- `CONTAINER_SLOTS` covers every `slotType` in the registry; every slot
  resolves a label; the Backpack tab label and the tab ordering are
  unchanged from v0.4.1.
- Equip → stash an item → unequip round-trips for all five equippable
  bags: the slot populates, `invSlot()` resolves it with the right
  capacity, its contents appear in `invPools()`, and the stored contents
  survive being unequipped back into a stowable item.
- `keychainAllows()` still accepts `Key` and rejects everything else.
- Every pool is attached to at least one container, and each of the five
  new pools reaches at least one container whose roll is still pending.
- 120,000 weighted rolls across all 28 pools — every result resolves to a
  real registry item with qty ≥ 1, and every entry has a positive weight
  and `qtyMin <= qtyMax`.
- All four new bag types confirmed findable in the default world, each in
  a `spawnRolled` container so no container lost its pool roll. (This
  check first ran too loosely — it counted the pre-existing
  `worn_backpack` toward the total and so passed while `fanny_pack` had
  silently failed to place. Tightened to exclude `worn_backpack` and to
  assert each of the four bag ids individually, which caught it.)
- A v0.4.1-shaped save, with none of the new slot keys, still loads and
  picks up every slot from `makeDefaultState()`.
- The v0.4.1 world audit re-run unchanged: 218 rooms, 774 exits, exit
  reciprocity, grid adjacency, compass wording, map coverage and
  reachability all still pass.
- Loaded in a real browser: the game boots at v0.4.2 and renders, and
  with all four bags equipped the panel shows Inventory / Keychain /
  Duffel Bag / Purse / Fanny Pack / Tote Bag with Unequip on the active
  slot.
- Diffed against `ashfall_0_4_1.html`: every removed line is an intended
  edit (version strings, the registry/pool lines being extended, the 20
  container lines gaining pools, the 4 gaining a bag, and the slot
  generalization). No room, container, item or exit was removed.

**Notes / assumptions**

- Per-entry spawn weights for the five new pools, and for the additions
  to the six existing ones, had no prior convention beyond "commoner
  higher, rarer lower" — retunable, not designed.
- **Category mismatch worth a look:** `dish_soap`, `laundry_detergent`,
  `rubber_gloves` and `trash_bags` are `Misc`, exactly as the handoff
  specifies, but their closest existing siblings (`bar_soap`, `bleach`,
  `toilet_paper`) are `Materials`. `Materials` is in `STACKABLE` and
  `Misc` is not, so as shipped these four do not stack while the older
  cleaning items do. Implemented as specced rather than silently
  deviating; it's a one-word change per entry if the stacking behavior is
  wanted.
- Which specific containers got which pool is this session's call within
  the handoff's stated pattern — in particular, pet supplies are on some
  residential units and not others, and baby items on only two, so not
  every apartment reads as having had a pet or a baby.
- `combat_knife`'s `blade` tag is currently decorative: no mechanic reads
  `blade` yet (`blunt` breaks cars and windows, `cutting` cuts locks,
  `chopping` fells trees). It is tagged for consistency with
  `kitchen_knife` and `box_cutter`, not because it does anything new.
- `baseball_bat` and `riot_baton` carry `blunt`, so they are immediately
  usable for forcing car doors and breaking windows. That is a real
  increase in how many tools can do those jobs, and worth a look if
  forced entry starts feeling too easy.
- The handoff listed four existing pools to extend; six were extended.
  `documents_lore` and `residential_personal` are the extra two, both
  named in the handoff's own per-category text (the document types and
  "extend `office_supplies`/`residential_personal`" for electronics) but
  omitted from its summary list.

**Version**: `GAME_CONFIG.VERSION` `"0.4.1"` → `"0.4.2"`

---

## v0.4.1 — Map Expansion to 8×8 Street Grid

Implements the "Ashfall Handoff — Map Expansion to 8×8 Grid" handoff for
its street-grid component. Fulfills roadmap Tier 1 item 14 (Expand the
Map) **in part only** — the building-placement half of that item is
untouched by this pass and item 14 stays open. Content pass: WORLD DATA
additions plus the mechanical `MAP` updates the larger grid required. No
new mechanics, no new state fields, no save-format change.

**Open questions resolved** (the handoff shipped with three unresolved;
Tom answered all three before this session)

- **Street names/direction.** Cedar, Elm, Mill and Dock confirmed, but all
  four placed **south** of Maple St rather than Mill/Dock north of Water.
  The handoff's table put Mill at y=400 and Dock at y=500, north of Water
  St — which would have put both streets in the river. Water St is the
  riverfront on every existing node (`fishable:true`, "just a drop to the
  mud", `riverbank`'s "Climb down to the riverbank"), so the town grows
  *away* from the water instead: Elm and Cedar continue the residential
  tree-name ring, Mill and Dock are the industrial and rail-freight edge
  beyond it. Water St remains the river / north hard limit and no existing
  description needed rewriting.
- **Numbered-street asymmetry.** Resolved symmetric the other way round:
  8th St dropped, 9th St added east, giving 3 streets west of center
  (6th, 4th, 2nd) and 4 east (3rd, 5th, 7th, 9th).
- **Pass size/phasing.** Built as a single pass, not split.

**New content** — WORLD DATA, `LOCATIONS` and the new `buildOuterStreets()`

- Street grid grown from 5 numbered × 4 named to **8 × 8**. New numbered
  streets (x, west→east): 6th `-100`, [4th `0`, 2nd `100`, 1st `200`,
  3rd `300`, 5th `400`], 7th `500`, 9th `600`. New named streets (y,
  south→north): Dock `-400`, Mill `-300`, Cedar `-200`, Elm `-100`,
  [Maple `0`, Poplar `100`, Main `200`, Water `300`]. Every existing
  coordinate is unchanged — origin stays `maple4th`, and the new grid is
  what introduces negative x and y.
- **125 new rooms**, each with a `LOCATIONS` entry at the same fixed
  100m spacing: 44 intersections (`dock6th` … `water9th`, `building`
  `"<Named> St & <Numbered> St"`, `floorCap:100`), 40 mid-blocks along the
  named streets (`mid_<name>_<lo>_<hi>`) and 41 along the numbered streets
  (`mid_<number>_<a>_<b>`), all `floorCap:20`. Mid-block coordinates are
  the midpoint of their two endpoints; adjacency is spatial order, not
  numeric, exactly as in the original grid. Room total 93 → 218.
- All 125 descriptions hand-written per the Project Guide's tone
  checklist — one to two sentences, matching the existing mid-block and
  intersection density rather than building-interior depth. New areas
  carry their own character: Elm and Cedar are the outer residential
  ring thinning into fields, Mill is the fenced industrial belt, Dock is
  the rail-freight edge where the town stops.
- New nodes ship with empty `containers:[]` — no loot placed in this
  pass. Eight mid-blocks get incidental `floor` items for texture, each
  tied to what the description already shows: `mid_cedar_5_7` (firewood,
  the dumped yard waste), `mid_dock_1_2` (planks, the broken pallet),
  `mid_dock_2_4` (tow chain), `mid_elm_2_4` (stuffed toy), `mid_main_5_7`
  (tire iron, the used-car lot), `mid_mill_7_9` (scrap metal),
  `mid_7th_mp_p` (metal pipe, the collapsed trampoline's leg) and
  `mid_water_7_9` (firewood, driftwood off the bend).
- The three new Water St nodes and their three mid-blocks carry
  `fishable:true`, matching every existing Water St node.
  `mid_elm_1_3`, `mid_maple_7_9` and `mid_9th_c_e` carry `hasTree:true`,
  the only three new descriptions that name a tree.

**Changed** — WORLD DATA, `buildStreetsAndOutdoor()`

- The 11 rooms that were the old grid's outer edge gained 26 exits
  connecting them outward: `maple4th`…`water4th` west toward 6th St,
  `maple5th`…`water5th` east toward 7th St, and all five Maple St nodes
  south toward Elm St (`maple4th` and `maple5th` were corners and gained
  two directions each). Each direction adds the established pair — one
  exit to the next intersection, one "Step into the block" exit to the
  new mid-block between them. All are cross-`Location` exits carrying
  only `{ to, label }`; `exitMinutes()` and `computeDirection()` derive
  travel time and compass wording from coordinates, as since v0.3.0.
- Water St gained no new exits north: it is still the river and the
  town's north hard limit.

**Fixed**

- `poplar2nd` was missing both of its southbound exits. `maple2nd` and
  `mid_2nd_mp_p` each point north to it, but it had no exit back, so
  Poplar & 2nd was a one-way trip from the south — a pre-existing v0.4.0
  content bug, not something this pass introduced (confirmed by running
  the reciprocity audit below against the unmodified v0.4.0 file). Added
  `{ to:"maple2nd" }` and `{ to:"mid_2nd_mp_p" }`, matching the
  intersection pattern every other node follows.

**Function relocation / new function**

- New `buildOuterStreets()` (WORLD DATA), merged in `makeDefaultWorld()`
  directly after `buildStreetsAndOutdoor()`. The handoff left placement
  of the 125 rooms to this session; they went in a sibling function
  rather than into `buildStreetsAndOutdoor()`, which would otherwise have
  roughly tripled in length. The split is along the obvious seam — the
  original 5×4 core versus the outer ring added here — and moved no
  existing line, so it is not roadmap item 9 (a by-town/by-location split
  of the existing function), which stays open and is now more pressing.

**UI** — RENDERING, `MAP` sub-block

- `MAP_STREETS` rebuilt: 16 chains (8 named + 8 numbered) of 15 nodes
  each, replacing the previous 9 chains of 9 and 7. The new nodes are
  inserted at their correct spatial position within each existing chain,
  not appended.
- `MAP_MAX_COL` `4` → `6` and `MAP_WIDE_VIEWBOX` `{20,20,610,480}` →
  `{20,20,1000,1000}`, both scaled from the 5×4 values by the same
  margin/spacing logic. New `MAP_MIN_COL` (`-1`) and `MAP_MIN_ROW` (`-4`)
  constants, because the grid now carries negative coordinates:
  `mapToSvg()` offsets by `MAP_MIN_COL` so column −1 still lands on the
  left margin. `MAP_MAX_ROW` is deliberately unchanged at `3` — Water St
  is still the northernmost row, so the river line and every pre-existing
  node keep their exact old SVG positions.
- The river path in `renderMapClose()`/`renderMapWide()` now spans
  `mapToSvg(MAP_MIN_COL, …)` → `mapToSvg(MAP_MAX_COL, …)` instead of
  starting at column 0, so it runs the full width of the wider grid.
- `MAP_BUILDINGS` untouched — no buildings were placed by this pass.
  Wide view shows the larger grid; Close view is structurally unaffected
  (it already pans per-node) and was spot-checked against the new nodes.

**Documentation**

- `LOCATIONS`' coordinate-convention comment rewritten for the 8×8 grid:
  the new col/row ranges and street orders, why the four new named
  streets sit south of Maple, and that the origin did not move.
- `MAP`'s grid-extents comment updated, including why `MAP_MIN_COL`/
  `MAP_MIN_ROW` exist and why `MAP_MAX_ROW` didn't change.
- ARCHITECTURE comment's "Current version" line bumped.
- Roadmap updated and renamed to `Ashfall_Development_Roadmap_v0.4.1.md`.
  Item 14 kept open with its scope narrowed to the building-placement
  half that this pass did not build. Item 9's room count corrected
  (60 → 185 street/outdoor rooms across two functions) and its "no
  urgency yet" note revised, since this pass is exactly the growth that
  note was waiting on. Nothing was removed.

**Explicitly out of scope** (per the handoff)

- Any new buildings in the new blocks, and any new outdoor set-pieces
  like the Storage Facility or Riverbank. This pass is the street
  skeleton only; what gets placed out there is a separate planning pass
  and the remaining half of roadmap item 14.
- No loot in the new blocks beyond the eight incidental floor items above.
- Splitting `buildStreetsAndOutdoor()` itself (roadmap item 9).
- The missing item-category population pass (separate handoff).
- Container property tags / item respawn (roadmap item 15).

**Validation performed**

Audited with a harness that evaluates the real `<script>` body under a DOM
stub and inspects the assembled `world`, run against both this file and
the unmodified v0.4.0 file for comparison:

- 218/218 rooms resolve a `locationId` in `LOCATIONS`; 774 exits, every
  target resolving to a real room.
- Every street↔street exit is reciprocal (this is the check that caught
  the `poplar2nd` bug, and it fails identically on unmodified v0.4.0).
- Every street exit spans exactly one grid step — 50m to a mid-block or
  100m to the next intersection — so no exit accidentally skips a node.
- Every compass word in every cross-`Location` exit label matches the
  direction `computeDirection()` derives from the coordinates.
- All 176 expected grid nodes present (64 intersections + 56 + 56
  mid-blocks) against an independently enumerated 8×8 grid.
- All 16 `MAP_STREETS` chains are 15 nodes, every id resolving; every
  grid node appears in some chain; all 176 render inside
  `MAP_WIDE_VIEWBOX`.
- Every room reachable from the player's start room by exit-graph search.
- Wide map rendered to SVG and rasterized — 8×8 grid draws correctly with
  the river along Water St at the north edge.
- Diffed against `ashfall_0_4_0.html`: 23 lines removed, all of them the
  intended `MAP`/comment/version edits. No existing room, container, item
  or exit was removed or rewritten — every world-data change is an
  addition.

**Notes / assumptions**

- Street names, the north/south flip, the symmetric numbered-street
  scheme and the one-pass phasing are Tom's answers to the handoff's
  three open questions, not this session's picks.
- Which four new named streets are residential (Elm, Cedar) versus
  industrial (Mill, Dock), and the specific character given to each — the
  mill and its yards, the rail spur and loading docks along Dock St — is
  this session's invention, extrapolated from the existing Riverside
  Freight warehouse and the "INDUSTRIAL-something" sign already on
  Maple St's south side. Retunable; nothing mechanical depends on it.
- The eight incidental floor items, the three `hasTree` nodes and the
  `fishable` flags on the new Water St nodes are judgment calls within the
  handoff's "sprinkle a handful for texture" guidance. Item choices are
  flavor, but `hasTree` feeds `doChopTree` and `fishable` feeds `doFish`,
  so they are live gameplay affordances and worth re-balancing if the
  outer grid ends up too generous a firewood/food source.
- `MAP_MIN_ROW` is defined and documented but not yet read by any code,
  since `MAP_MAX_ROW` alone still anchors the y axis. It is there as the
  matching half of `MAP_MIN_COL` so the extents read as a pair.
- The handoff described the 14 edge rooms as gaining "a new exit" each.
  Following the file's own convention, each new direction gains a *pair*
  (next intersection + mid-block), which is why the count here is 26
  exits across 11 rooms rather than 14.

**Version**: `GAME_CONFIG.VERSION` `"0.4.0"` → `"0.4.1"`

---

## v0.4.0 — Container Spawn Pools & Population System

Implements the "Ashfall Handoff — Container Spawn Pools & Population
System" handoff, item-spawn-pool portion in full (Tier 3 item 15, partial
fulfillment — see Explicitly NOT in this pass below).

**New**

- `SPAWN_POOLS` registry (WORLD DATA, sibling to `ITEM_REGISTRY`) — 23
  weighted loot pools (`kitchen_perishable`, `kitchen_nonperishable`,
  `kitchen_tools`, `hygiene`, `medical_otc`, `medical_pharmacy`,
  `residential_personal`, `clothing`, `documents_lore`, `recreation`,
  `tools_general`, `tools_workshop`, `office_supplies`,
  `retail_stock_food`, `retail_stock_general`, `hardware_store`,
  `outdoor_camping`, `valuables`, `police_evidence`, `police_gear`,
  `warehouse_goods`, `trash`, `fuel_fire`). Each pool entry carries
  `weight`/`qtyMin`/`qtyMax`; each pool has its own `rollCount` range and
  `emptyChance`.
- `doOpenContainer(room, container)` (WORLD INTERACTION) — rolls a
  container's `spawnPools` independently the first time it's opened
  (gated by the new `spawnRolled` container field), then stamps
  `lastRolledMinute`. Wired in by having the container-tab click handler
  in `renderWorldItemsPanel()` (RENDERING) call it instead of setting
  `state.worldTab` directly.
- `weightedPick()` / `randInt()` (CORE UTILITIES) — small RNG helpers
  backing the roll.
- `backfillContainerFields()` (PERSISTENCE), wired into
  `applyLoadedData()` alongside the existing three backfills.
- 37 new `ITEM_REGISTRY` entries (Food, Medical, Clothing, Recreation,
  Tools/Workshop, Retail, Outdoor, and Police categories) needed for pool
  depth — see the handoff's Appendix B for the full list.

**Content**

- `spawnPools` tagging retrofit across all 74 containers (69 existing +
  5 new) per the handoff's Appendix C assignment table — every building:
  Acorn Apartments, Auto Workshop, Main St (Corner Store, Pharmacy,
  Hardware Store, and the apartments above each), Oak Apartments, Police
  Station, Riverside Freight, the Poplar St alley dumpster, and the Water
  St storage units.
- The 19 previously-empty containers (Oak Apartments ×8, Auto Workshop
  ×4, Police Station ×3, Riverside Freight ×4) now populate via their
  assigned pools on first open instead of sitting permanently empty.
- Acorn Apartments 2B parity fix: added Fridge (`kitchen_perishable`),
  Pantry (`kitchen_nonperishable`), and Under-sink cabinet (`hygiene`) to
  `twobee_kitchen`/`twobee_bathroom`, and a Dresser (`clothing`,
  `residential_personal`) to `twobee_bedroom` — 2B was missing fixtures
  its 2A twin has. All four ship empty and roll on first open.
- Superintendent's unit (`onebee`) gets a new Closet (`clothing`), same
  treatment.
- All 50 pre-existing hand-placed containers reviewed against their new
  pool tags and retagged `spawnRolled:true` at authoring time so
  `doOpenContainer()` never overwrites their authored contents; their
  pools exist only so a future respawn cycle (roadmap item 15's
  remaining scope) has something to draw from.

**Content review adjustments** (existing hand-placed contents swapped
for pool consistency, per the Project Guide's "judgment calls get
flagged" principle):

- Acorn Apartments 2B, `twobee_bedroom` nightstand: swapped 2×
  `bandages` for 1× `loose_change`. The nightstand is tagged
  `residential_personal`/`documents_lore`, not a medical pool — a
  medical item sitting there was a category mismatch; `loose_change` is
  a direct `residential_personal` entry.
- Pharmacy `shelves`: swapped `vitamins` for `cold_medicine`. `shelves`
  is tagged `medical_otc` only, but `vitamins` is a `medical_pharmacy`
  pool entry per the handoff's own tables (pharmacy-grade, not OTC);
  `cold_medicine` is a `medical_otc` entry — this is the exact kind of
  swap the handoff's "In scope" item 4 calls for.

**Hardened**

- `backfillContainerFields()` was implemented slightly beyond the
  handoff's literal wording. The handoff describes it as backfilling
  only `spawnRolled`, but a genuinely old (pre-v0.4.0) save's containers
  don't carry a `spawnPools` field at all — so `doOpenContainer()`'s
  `container.spawnPools && !container.spawnRolled` guard could never
  fire for anything loaded from such a save, silently defeating the
  "still-empty containers get a chance to roll on next open" behavior
  the function exists for. Found by simulating `applyLoadedData()`
  against a save stripped of both fields. Fixed by having the backfill
  copy `spawnPools` itself from the default world (mirroring how
  `backfillLocationIds()` already copies a missing `locationId`), then
  `spawnRolled`, keyed off the same "does the default container have
  `spawnPools`" check.

**Documentation**

- Updated the CONTAINER SCHEMA comment (WORLD DATA) to document the
  three new optional container fields: `spawnPools`, `spawnRolled`,
  `lastRolledMinute`.
- Roadmap reconciled against this pass, per `Ashfall_Development_Roadmap_v0.3.0.md`'s
  own Purpose note that its accompanying planning session had already
  narrowed item 15's scope and added item 16 in advance of this
  implementation. Item 15's "Current status" note is updated from
  "specced and shipped as its own handoff" (pre-implementation wording)
  to confirm the item-spawn-pool mechanism is now actually implemented,
  in this version — the remaining scope (container property tags,
  no-respawn flag, the respawn trigger, region/town data model, vehicle
  spawn pools, fauna) was already correctly described as still open and
  needed no further edit. Item 16 (`bandage`/`bandages` naming
  duplicate) is untouched by this pass, exactly as the roadmap already
  expected — not removed. File renamed to
  `Ashfall_Development_Roadmap_v0.4.0.md` per the tracker-naming
  convention.

**Notes / assumptions**

- Duplicate-`itemId`-within-one-roll (the handoff's one open design
  decision): resolved via the existing `addToList()`/`STACKABLE`
  mechanism rather than new special-casing. Two picks of the same
  `Food`/`Medical`/`Materials` item in one roll merge into a single
  stack (the handoff's recommended default). Picks in non-`STACKABLE`
  categories (`Tool`, `Misc`, `Clothing`, etc.) remain separate stack
  entries — not a special case, just the same rule every other duplicate
  item in the game already follows.
- Helper names: `weightedPick`/`randInt`, matching the handoff's own
  suggested names.

**Explicitly NOT in this pass** (per the handoff's own scope — restated
here so a future session doesn't have to reopen the handoff to know
what's still open):

- `carContainers` (vehicle trunk/glovebox) spawn pools.
- The respawn trigger itself (time-based reroll after leaving/returning
  to town) — `lastRolledMinute` is stamped now but nothing reads it yet.
- Region/town data model.
- Container property tags (`equippable`/`movable`/`disassemblable`) and
  the no-respawn flag.
- Fauna alive/dead spawning.
- `master_key` remains purely hand-placed on `onebee`'s Desk — not a
  pool entry, and permanently lost if the player loses it (deliberate).
- The `bandage`/`bandages` naming duplicate (new roadmap Tier 0 item 16,
  not fixed here).

**Validation performed**

- `node --check` on the extracted script: no syntax errors.
- Standalone simulation of `makeDefaultWorld()` + every `SPAWN_POOLS`
  entry: all 23 pools referenced by at least one container, zero unknown
  `itemId` references from any pool into `ITEM_REGISTRY`, zero unknown
  pool ids referenced from any container, all 74 containers accounted
  for with exactly 50 `spawnRolled:true` / 24 roll-eligible (matches the
  handoff's stated counts exactly).
- 1,200-trial stochastic run of `doOpenContainer()` across every
  roll-eligible container: zero errors, ~2.2 items/roll average, ~15%
  fully-empty rolls (consistent with the authored `emptyChance` values).
- Simulated loading a save stripped of `spawnPools`/`spawnRolled`
  (representing a genuine pre-v0.4.0 save) through `applyLoadedData()`:
  confirmed all 74 containers regain correct `spawnPools`/`spawnRolled`
  and a previously-empty container successfully rolls loot on first
  open afterward.
- Headless-browser smoke test (Playwright + the pre-installed Chromium):
  loaded the file with zero console/page errors, confirmed the title
  bar reads v0.4.0, opened a `spawnRolled:true` container (Fridge) and
  confirmed it shows only its original hand-placed contents (no
  unwanted roll), then opened a previously-empty container (Oak
  Apartments 1A Dresser) and confirmed it rolled real loot on first open
  and returned identical contents on a second open (no re-roll).

**Version**: `GAME_CONFIG.VERSION` `"0.3.0"` → `"0.4.0"`

---

## v0.3.0 — Auto-Distance & Direction Wiring

Implements the `Ashfall v0.3.0.md` handoff in full — Part 2 of 2 of the
coordinate-system initiative (roadmap item 11). Part 1 (item 10,
`LOCATIONS`/`locationId`) shipped in v0.2.9. Genuine mechanics pass:
the exit-time-cost rule changes for cross-Location movement, not just
content or rendering.

**Changed — ACTIONS/WORLD INTERACTION (movement)**
- `exitMinutes(exit)` rewritten: compares `world[state.currentRoom]
  .locationId` against `world[exit.to].locationId`. Same-Location
  (`fromLoc === toLoc`) still uses hand-authored `exit.distanceM`,
  unchanged. Cross-Location (`fromLoc !== toLoc`) now calls the new
  `locationDistance(fromLoc, toLoc)` instead of a flat per-gait constant.
  `moveMinutes()`'s existing `MIN_MOVE_MIN` floor (1 minute) is unchanged
  and already covered the "minimum move stays 0:01" requirement — no
  edit needed there.
- `locationDistance(a, b)`: new helper, 3D Euclidean distance between two
  `LOCATIONS` entries, `Math.round`ed to the nearest whole meter.
  Computed on demand every call — never cached or stored on the exit, so
  `LOCATIONS` stays the single source of truth for cross-Location
  distance, per the "no duplicated source of truth" principle.
- `computeDirection(a, b)`: new helper. Pure vertical movement (`dx===0
  && dy===0`) resolves to `"up"`/`"down"` by sign of `dz`. Otherwise the
  larger of `|dx|`/`|dy|` wins the axis, with sign giving the
  cardinal direction. A genuine diagonal tie (`|dx| === |dy|`, both
  nonzero) defaults to the north/south axis, per the handoff — none was
  found in the current rectilinear grid (see Validation).
- `applyComputedDirections(world)`: new helper, called once from
  `makeDefaultWorld()` right after the six `build*()` functions are
  merged. Walks every room/exit; for any exit whose target Location
  differs from the room's own and whose label already contains an
  explicit compass word (matched via `COMPASS_WORD_RE`), replaces that
  word in place with the one `computeDirection()` derives from real
  coordinates. Chosen over a render-time approach per the handoff's
  recommended default — runs once at world-build time rather than on
  every render, keeping `exitMinutes()`/label logic simple. Labels with
  no compass word (building entrances, floor transitions, "Leave the
  apartment", etc.) are never touched, cross-Location or not.

**Removed**
- `exit.block` / `exit.blockHalf` fields, stripped from all 192 exit
  literals across the six `build*()` functions (61 `block:true` + 131
  `blockHalf:true`, confirmed by direct count against the shipped
  v0.2.9 file).
- `BLOCK_MIN`, `HALF_BLOCK_MIN` constants (CONFIG/CONSTANTS) — fully
  superseded by the computed path above.

**Data / schema changes**
- EXIT SCHEMA simplifies: cross-Location exits are now just `{ to,
  label }` (optionally `doorId`) — no `distanceM`, `block`, or
  `blockHalf`. Same-Location exits are unchanged: `{ to, label,
  distanceM }`. ARCHITECTURE's EXIT SCHEMA comment updated to describe
  the two shapes and point at `exitMinutes()`/`locationDistance()`
  instead of the old flat-constant table.
- No PLAYER STATE changes.
- **MINOR bump — `SAVE_KEY` rotates** from `ashfall_save_v0.2` to
  `ashfall_save_v0.3` (`versionCompat()` derives the key from
  `MAJOR.MINOR`). Existing browser-slot saves won't auto-load under the
  new key; still recoverable via Export/Import. This is the intended
  "real seam" for a MINOR bump, not a bug — no exit-specific save
  backfill is needed, since `world` is embedded verbatim in saves and
  the new `exitMinutes()` never reads the retired `block`/`blockHalf`
  fields even if a stale save's `world` still carries them.

**Sections touched**
- ACTIONS/WORLD INTERACTION (movement): `exitMinutes()`. `doMove()`'s
  call site is unchanged; both call sites (`doMove()` and
  `renderMoveActionsPanel()`) already read `state.currentRoom` as the
  FROM room before it's updated to `exit.to`, so no change was needed
  there.
- WORLD DATA: every `build*()` function's exit definitions lose
  `block`/`blockHalf`; `makeDefaultWorld()` now pipes its merged result
  through `applyComputedDirections()` before returning it.
- CONFIG/CONSTANTS: `BLOCK_MIN`/`HALF_BLOCK_MIN` removed.
- Documentation: ARCHITECTURE's LOCATIONS note and EXIT SCHEMA comment
  updated (see Documentation below); this is a mechanics pass, not
  content-only.

**UI**
- Exit button labels: the compass word in cross-Location labels is now
  computed rather than authored. Confirmed unchanged text in every
  case that has one today (see Validation) — this is a substitution
  mechanism going forward, not a wording change now.
- Displayed travel times shift for street-grid movement at the current
  100m-block / 3m-floor scale (e.g. a full block on foot: 2 min → ~1
  min; see the handoff's balance table). Intentional consequence of
  moving to real coordinates, not a rebalance.

**Explicitly out of scope** (per the handoff)
- Any change to same-Location exits, distance or label.
- Floor-transition/building-entrance label phrasing (no compass word
  today, none added).
- New content (rooms, basements, roofs).
- Re-deriving or adjusting the v0.2.9 `LOCATIONS` data or building/floor
  coordinates.

**Validation performed**
- `node --check` syntax pass on the extracted script: clean.
- Full diff against v0.2.9: every changed line traces to
  `CONFIG/CONSTANTS`, the EXIT SCHEMA/LOCATIONS ARCHITECTURE comments,
  the 192 `block`/`blockHalf` exit literals (field removed, label text
  untouched), `makeDefaultWorld()`, or `exitMinutes()` — no stray
  content or unrelated-mechanics edits.
- Standalone Node harness (full script through `makeDefaultWorld()`,
  executed in isolation) built the real `world` and walked all 93
  rooms / 286 exits: every exit resolves a target room and a
  `LOCATIONS` entry on both ends; 68 same-Location exits all still
  carry `distanceM`; 218 cross-Location exits correctly carry none;
  zero diagonal ties.
- Label-substitution check: 184 cross-Location exits carry a compass
  word. Diffed every one's label, old build vs. new, matched by exit
  target — **zero actual text changes**. The computed directions match
  the hand-authored ones in every existing case, confirming the
  handoff's "should read the same in virtually all cases" prediction
  rather than merely assuming it.
- `SAVE_KEY` rotation confirmed directly: `versionCompat("0.3.0")` →
  `"0.3"`, so `SAVE_KEY` = `ashfall_save_v0.3` (was `ashfall_save_v0.2`
  under v0.2.9).

**Documentation**
- ARCHITECTURE's LOCATIONS note updated: was "read only by MAP
  rendering as of v0.2.9," now describes both MAP rendering and
  movement (`exitMinutes()`/`locationDistance()`/
  `applyComputedDirections()`/`computeDirection()`) as readers. Current
  version line bumped to 0.3.0.
- EXIT SCHEMA comment rewritten to describe the same-Location vs.
  cross-Location shapes above, replacing the old three-variant
  (`distanceM`/`block`/`blockHalf`) description.
- Closes the two-part "Coordinate System" roadmap item opened in
  v0.2.9: item 11 removed from the roadmap in this same update,
  alongside the rename to `Ashfall_Development_Roadmap_v0_3_0.md`.

**Notes / assumptions**
- Audit finding, not a scope change: beyond the 192 `block`/`blockHalf`
  exits, 26 pre-existing plain-`distanceM` exits are *also*
  cross-Location — building entrances/exits and floor transitions
  (e.g. `cornerstore ↔ main2nd`, `stairs2 ↔ stairs1`, `pharmacy_apt ↔
  pharmacy`). The handoff's existing-state audit only enumerated the
  `block`/`blockHalf` population; it didn't separately flag these. The
  new `exitMinutes()` rule ("cross-Location → computed") applies to
  them the same as any other cross-Location exit, so their
  `exit.distanceM` field is now unread/vestigial rather than acted on.
  Checked, not assumed: for all 26, the old hand-authored distance and
  the newly-computed distance both fall well under the one-minute floor
  at every gait, so the *displayed* travel time (`fmtDuration`, which
  itself rounds) is identical in every case — confirmed by direct
  computation, not inferred from the small numbers involved. Left the
  vestigial `distanceM` fields in place rather than expanding this
  pass's scope to strip them; added as a new Tier 0 roadmap item
  (below) instead, per "unplanned gaps get documented as new roadmap
  items rather than silently expanded."
- No diagonal-tie case was found in the current grid (checked
  programmatically across all 218 cross-Location exit pairs) — the
  tie-break default (north/south axis) is implemented per the handoff
  but currently unexercised.

**Version**: `GAME_CONFIG.VERSION` `"0.2.9"` → `"0.3.0"`

---


## v0.2.9 — Coordinate Data Model & Map Rendering Migration

Implements the `Ashfall v0.2.9.md` handoff in full — Part 1 of 2 of the
coordinate-system initiative (roadmap item 10). Part 2 (item 11,
auto-distance & direction wiring) is specced separately in
`Ashfall v0.3.0.md` and depends on this pass. Content/rendering/
persistence only — no movement mechanic touched yet.

**New**
- `LOCATIONS`: new WORLD DATA table giving every street/mid-block node
  and building floor a real integer `(x, y, z)` position in meters.
  Origin `(0,0,0)` = `maple4th` (town SW corner), street level; +X east,
  +Y north, +Z up. Block size 100m, floor height 3m. 66 entries total:
  51 street/mid-block Locations (id = the room id itself, `z:0`,
  `(x,y)` = the old `MAP_NODES {col,row} * 100`) + 15 building-floor
  Locations (one per floor, shared by every room on that floor; `(x,y)`
  = the building's old `MAP_ANCHORS` node; `z:0`/`z:3` for ground/
  upper floor). Replaces `MAP_NODES`/`MAP_ANCHORS` entirely.
- `locationId`: new required ROOM SCHEMA field, added to every one of
  the 93 rooms across all six `build*()` functions, resolving into
  `LOCATIONS`.
- `backfillLocationIds()` (PERSISTENCE, beside `backfillItemIds()`):
  assigns `locationId` to any loaded room missing it, by direct room-id
  lookup against a freshly-built `makeDefaultWorld()` — room ids are
  stable, so (unlike `backfillItemIds()`'s name-matching) this is an
  unambiguous key lookup. Wired into `applyLoadedData()` alongside
  `resyncUidCounter()`/`backfillItemIds()`.
- `validateLocations()` (dev-only console helper, beside
  `validateItemRegistry()`): walks every room, confirms `locationId` is
  set and resolves in `LOCATIONS`; logs any that don't. Not wired to
  any button.

**Changed — MAP rendering**
- `mapToSvg`, `mapPathD`, `renderMapClose`, `renderMapWide`,
  `mapPositionPlayer`, `mapTargetViewBox` now read
  `LOCATIONS[id].x / 100` / `.y / 100` in place of the old
  `MAP_NODES[id].col` / `.row` — dividing by 100 recovers the exact same
  grid-unit spacing the SVG layout constants (`MAP_SPACING`,
  `MAP_MARGIN`) already assume, so rendered output is unchanged.
- `renderMap()` resolves the player's current map position via
  `world[state.currentRoom].locationId` instead of the removed
  `mapNodeForRoom()`.
- `MAP_BUILDINGS[i].anchor` now names a building's ground-floor
  `LOCATIONS` id (e.g. `acorn_f0`) instead of a `MAP_NODES` key. Same
  field, same usage — Pharmacy/Hardware Store still correctly share one
  anchor (`mid_main_1_3` → both resolve to `x:250,y:200`), kept visually
  distinct by their existing `dx`/`dy` cosmetic offset, which is
  untouched.
- Added `MAP_STREET_NODE_IDS` (derived once via
  `Array.from(new Set(MAP_STREETS.flatMap(s => s.chain)))`) for the
  Close-map node-dot loop in `renderMapClose()`, replacing
  `Object.keys(MAP_NODES)`. Deriving it from `MAP_STREETS` — which
  already lists every street node across its nine chains — avoids
  hand-duplicating the 51-id list a second time, per the "no duplicated
  source of truth" principle.

**Removed**
- `MAP_NODES`, `MAP_ANCHORS`, `mapNodeForRoom()` — fully superseded by
  `LOCATIONS`/`locationId`.

**Sections touched**
- WORLD DATA: new `LOCATIONS` table; `locationId` added to every room
  across all six `build*()` functions.
- UI/RENDERING → MAP sub-block: `mapToSvg`, `mapPathD`,
  `renderMapClose`, `renderMapWide`, `mapPositionPlayer`,
  `mapTargetViewBox`, `renderMap`.
- PERSISTENCE: `backfillLocationIds()`, `applyLoadedData()`.
- ACTIONS/SIMULATION untouched — no movement mechanic changed. That's
  `Ashfall v0.3.0.md` (Part 2).

**Explicitly out of scope** (per the handoff)
- `distanceM` auto-computation, `block`/`blockHalf` removal, and
  exit-label direction templating — all `Ashfall v0.3.0.md`, Part 2.
- Any new player-facing content (no new rooms, no roof/basement
  content).
- `Z` is laid down for every Location but not consumed by anything yet
  (the map is top-down) — intentional, so Part 2 and future systems
  don't have to retrofit it.

**Design decision resolved**
- `oak_stairs` floor assignment: resolved to `oak_f0` (the lower of the
  two floors it connects), per the handoff's recommended default. Acorn's
  stairwell needed no such call — it's already split into
  `stairs1`/`stairs2`, one per floor.

**Explicitly NOT changed**
- Room/item/container/exit data and values, all `distanceM`/`block`/
  `blockHalf` exit fields, `GAITS`/`BLOCK_MIN`/`HALF_BLOCK_MIN`, UI
  layout/styling, and every mechanics function outside the MAP
  rendering sub-block listed above.
- Rendered map output: pixel-identical by construction (see Validation).

**Validation performed**
- `node --check` syntax pass on the extracted script: clean.
- Full diff against v0.2.8: confirmed every changed/removed line traces
  to the `LOCATIONS`/`locationId` migration, the MAP rendering sub-block,
  `backfillLocationIds()`/`validateLocations()`, or the version-bump
  comment updates — no stray content edits.
- Standalone Node harness (`ITEM_REGISTRY`, `LOCATIONS`, all six
  `build*()` functions, and `makeDefaultWorld()` extracted and executed
  in isolation) confirmed all 93/93 rooms resolve a `locationId` that
  exists in `LOCATIONS` (mirrors `validateLocations()`'s own check).
- Confirmed mathematically, for all 51 street/mid-block ids, that
  `LOCATIONS[id].x / 100` and `.y / 100` exactly equal the old
  `MAP_NODES[id].col` and `.row` — the map's rendered coordinates are
  unchanged, not just visually similar.
- `SAVE_KEY` unaffected: confirmed `versionCompat()` still derives
  `"0.2"` from `"0.2.9"` (PATCH bump, no `SAVE_KEY` rotation).

**Documentation**
- Fixed the stale "Current version: 0.2.7" line in the ARCHITECTURE
  comment (had drifted two versions behind) and added a brief
  `LOCATIONS`/`locationId` note there and in the ROOM SCHEMA comment
  block.
- Roadmap item 10 ("Coordinate System — Part 1") is complete as of this
  entry; removed from the roadmap in the same update that renames it to
  `Ashfall_Development_Roadmap_v0_2_9.md`. Item 11 ("Part 2") is now
  unblocked and stays on the roadmap.

**Notes / assumptions**
- Count discrepancy in the handoff, resolved by following the
  authoritative table over the prose: the handoff's "Rules / mechanics"
  section states 16 building-floor Locations ("5 two-floor buildings ×
  2 + 6 one-floor buildings × 1"), but its own "Building → Location
  membership" table — marked "authoritative — apply exactly" — lists
  only 5 one-floor buildings (Storage Facility, Riverbank, Auto
  Workshop, Police Station, Riverside Freight), for 15 building-floor
  Locations, not 16. The likely source: the handoff's "Relevant existing
  state" section separately notes `MAP_BUILDINGS` has 11 entries (5
  two-floor + "the other 6"), but that 11 includes a purely cosmetic
  "Alley" marker sharing Acorn's anchor for map-label purposes only —
  not a real building with its own floor. `alley` (the room) is already
  a member of `acorn_f0` in the membership table, consistent with its
  pre-existing `MAP_ANCHORS` entry (`alley:"mid_poplar_1_2"`, the same
  anchor as every other Acorn Apartments room). Implemented as 15
  building-floor Locations (66 total, not 67) — internally consistent
  with the table, `MAP_ANCHORS`, and the live v0.2.8 room count; flagging
  here rather than silently resolving, per the "judgment calls get
  flagged" convention.

**Version**: `GAME_CONFIG.VERSION` `"0.2.8"` → `"0.2.9"`

---

## v0.2.8 — WORLD DATA / RENDERING Modularity Pass

Pure code-organization pass, per the `Ashfall v0.2.8.md` handoff. No
roadmap item — a standalone maintainability pass done at Tom's request.
No gameplay, content, or DOM-output change.

**Organization / Structural**
- Split `makeDefaultWorld()` (previously one ~1,025-line object literal,
  93 rooms) into six per-building functions —
  `buildAcornApartments()`, `buildStreetsAndOutdoor()`,
  `buildOakApartments()`, `buildAutoWorkshop()`, `buildPoliceStation()`,
  `buildRiversideFreight()` — merged back via `Object.assign()` in a now
  thin `makeDefaultWorld()`. Grouping follows the handoff's recommended
  default: one function per named building on `MAP_BUILDINGS`, plus
  `buildStreetsAndOutdoor()` for street/outdoor rooms (`building:""` or a
  street name). No room id, key, or value changed; no duplicate-key
  collisions found.
- Extracted the remaining inline sections of `render()` into six named
  panel functions, matching the existing `renderCraftPanel()` /
  `renderMap()` pattern: `renderLocationPanel()`, `renderStatsPanel()`,
  `renderMoveActionsPanel()`, `renderHereActionsPanel()`,
  `renderInventoryPanel()`, `renderWorldItemsPanel()`. `render()` is now
  a short orchestrator; the `gameOver` early-return branch stays inline
  per the handoff. Panel functions each resolve `world[state.currentRoom]`
  independently where needed, rather than threading it as a parameter —
  matching the self-contained style of the existing extracted panels.

**Sections touched**: WORLD DATA (`makeDefaultWorld()` restructure only —
no room data changed), RENDERING (`render()` and the six new panel
functions).

**Explicitly out of scope**: any content/value/DOM-output change; any
build tooling or multi-file split; the Tier 0 `giveItem()` registry
cleanup item; any roadmap edit, per Tom's explicit instruction for this
handoff.

**Explicitly NOT changed**: room/item/container/exit data and values;
UI layout, styling, or displayed text; save format (`SAVE_KEY` unaffected
— PATCH bump); any mechanics function outside `render()`'s panel
extraction.

**Validation performed**
- `node --check` syntax pass on the extracted script: clean.
- Full diff against v0.2.7: confirmed the only changes are the
  `GAME_CONFIG.VERSION` bump and the two structural relocations described
  above (no stray content edits).
- Programmatic deep-equality check of the merged `world` object against
  v0.2.7's `makeDefaultWorld()` output: 93/93 room keys present,
  order-independent structural match confirmed via a Node harness
  requiring both versions' pre-render script and comparing sorted JSON.
- Multiset comparison of every `document.getElementById(...)` call
  across both files: identical (48/48), confirming no panel dropped or
  duplicated a DOM reference during extraction.
- Functional simulation: both v0.2.7 and v0.2.8 scripts executed in a
  sandboxed DOM stub (Node `vm`, stubbed `document`/`localStorage`),
  triggering the game's initial `render()` call. Resulting DOM state
  (text/HTML/children/style/disabled) compared element-by-element across
  every panel — identical, apart from the expected version-string
  difference in `pageTitle`.

**Documentation**
- The roadmap was updated separately from this handoff, at Tom's
  explicit follow-up request (overriding the handoff's "no roadmap
  edits" instruction for that one instruction only) — not part of this
  coding pass's own scope. `Ashfall_Development_Roadmap_v0_2_7.md` was
  renamed to `Ashfall_Development_Roadmap_v0_2_8.md` and a new Tier 0
  item (#9, "Split `buildStreetsAndOutdoor()` by town/location") was
  added, noting that the v0.2.8 building-level split left all
  street/outdoor rooms in one combined function and flagging a future
  further split by town/location as a low-priority, deferrable cleanup
  item.

**Notes / assumptions**
- Building/grouping boundaries and function names follow the handoff's
  recommended defaults exactly (see "Design decisions" in
  `Ashfall v0.2.8.md`), so no deviation to record.

**Version**: `GAME_CONFIG.VERSION` `"0.2.7"` → `"0.2.8"`

---

## v0.2.7 — Item Identity & Reference Consistency

Implements `Ashfall v0.2.7.md` in full (Tier 0, item 0.1). Gives every
runtime item a stable `itemId` (registry-definition identity, alongside
the existing `_uid` instance identity) and converts the remaining
mechanics that keyed off display name to `itemId` lookups instead. This
is a cross-cutting identity-consistency pass — no content or mechanic
changes, no new persistent state.

**New — WORLD DATA**
- Four `ITEM_REGISTRY` entries added, matching properties previously
  only inline in `RECIPES`/`HEAT_RECIPES` output and `doFish()`
  (no balance changes): `bandage`, `campfire_kit`, `cooked_fish`,
  `raw_fish`.
- `RECIPES[].inputs[]` schema changed from `{name, qty}` to `{id, qty}`
  (`cloth`, `duct_tape`, `firewood`). `RECIPES[].output` /
  `HEAT_RECIPES[].output` changed from a literal item object to `{id}`.
  `HEAT_RECIPES[].input` changed from a name string (`"Raw fish"`) to an
  id string (`"raw_fish"`).

**Changed — ITEM SYSTEM**
- `itemFromRegistry()` now stamps `item.itemId = ref.id` on every item it
  produces, in addition to existing `qty`/`overrides` behavior.
- `addToList()`'s stacking match changed from
  `i.name===item.name && i.category===item.category` to
  `i.itemId===item.itemId && i.category===item.category`.
- `countInPools()` / `consumeFromPools()` now take an `itemId` first
  argument and match `it.itemId === itemId`, instead of matching on
  `name`. All nine call sites updated (`canCraft`/`doCraft`, and the
  fire/cooking `"firewood"`/`"campfire_kit"` id literals in
  `canBuildFire`/`doBuildFire`/`doAddFuel`/render's add-fuel check).
- `it.name === "Campfire Kit"` (gating the Campfire Kit "Disassemble"
  action) replaced with `it.itemId === "campfire_kit"`.

**Changed — CRAFTING, FIRE/COOKING**
- `doCraft()` and `doCookInContainer()` now resolve their output through
  `itemFromRegistry({ id: recipe.output.id, qty:1 })` instead of
  spreading a literal `recipe.output` object.
- `doFish()`'s raw-fish grant now goes through
  `itemFromRegistry({ id:"raw_fish", qty:1 })`.
- `doCookInContainer()`'s input match changed from
  `it.name===recipe.input` to `it.itemId===recipe.input`.
- Display text that previously read `.name` directly off `recipe.output`
  / `recipe.input` / a recipe input entry now looks the name up via
  `ITEM_REGISTRY[id].name` instead, since those fields are now id
  references rather than full item objects: the craft-success log line,
  the cook-finishes log line, the crafting-menu ingredient list
  (`needs Cloth x2, Duct tape x1`), and the "Cook the X" action label +
  its container-has-ingredient visibility check. Player-facing text is
  unchanged; only how it's produced changed.

**New — PERSISTENCE**
- `backfillItemIds()`, a sibling function called alongside
  `resyncUidCounter()` from `applyLoadedData()` on every load. For any
  loaded item missing `itemId`, it looks up the id by reverse name match
  against `ITEM_REGISTRY` (current registry names are unique) and
  assigns it if found. Items with no registry match are left without
  `itemId` and continue working via `_uid`/list position, same as
  before this pass. No save-format migration — additive only, no
  `SAVE_KEY` change.

**New — dev tooling**
- `validateItemRegistry()`, a console-only helper (not wired to any
  button or UI) that walks `RECIPES`/`HEAT_RECIPES` inputs/outputs and
  logs any `id` that doesn't resolve in `ITEM_REGISTRY`.

**Documentation**
- Fixed the ARCHITECTURE comment's stale `Current version: 0.2.3.` note
  to `0.2.7` (already stale independent of this pass; fixed while in the
  area).
- Roadmap: removed Tier 0, item 0.1 (Item Identity & Reference
  Consistency) — closed by this pass. No other roadmap changes; nothing
  else audited as drifted.

**Explicitly NOT changed**
- No balance values, no item weights/restores/tags changed on any
  existing or new registry entry.
- `hasTool()` and the tag system — already fully capability-based, not
  touched.
- Equipment/`doEquip()`/`doUnequip()` instance-identity reconstruction —
  out of scope per the handoff, not touched.
- No new player-state fields, no `SAVE_KEY` change.

**Validation performed**
- `node --check` on the extracted script: passes.
- Full diff against `ashfall_0_2_6.html`: confirmed every changed line
  maps to an item in the handoff's Rules/In-scope sections or a
  necessary display-text follow-through (see above); no unrelated line
  changed.
- Sandboxed functional run of the actual updated script (DOM stubbed):
  verified `validateItemRegistry()` reports no unresolved ids; crafting
  a bandage consumes `cloth`×2 + `duct_tape`×1 and yields a `bandage`
  item with `itemId` set; `doFish()` yields a `raw_fish` item with
  `itemId` set; `itemId`-based stacking in `addToList()` correctly
  merges same-id gives within one list and correctly does *not* merge
  across list/floor-overflow boundaries; `consumeFromPools()` correctly
  depletes by `itemId`; `backfillItemIds()` correctly assigns `itemId`
  to a synthetic legacy item (no `itemId`, name-only) by reverse name
  match.

**Notes / assumptions**
- The backfill scan was implemented as a sibling function
  (`backfillItemIds()`) rather than folded into `resyncUidCounter()`,
  per the handoff's "Design decisions" section leaving that shape
  choice open.

**Version**: `GAME_CONFIG.VERSION` `"0.2.6"` → `"0.2.7"`

---

## v0.2.6 — giveItem() Registry Cleanup + Street Grid Expansion & Rename

Implements `Ashfall v0.2.6.md` in full — two independent pieces of work
bundled into one pass: the last `giveItem()` registry cleanup (Tier 0,
item 0.1), and a 3×3→5×4 street grid expansion with a full north-south
street renumbering and 4 new buildings. Content-only in the WORLD DATA
sense (no new mechanic anywhere), plus the RENDERING changes the bigger
grid requires.

**Fixed**
- `giveItem()` call sites that hand-authored a literal item object instead
  of resolving through `ITEM_REGISTRY` now use `itemFromRegistry()`: the
  "Remove batteries" action (Spare batteries), the Campfire Kit
  "Disassemble" action, the campfire-dismantle refund, and the tree-chop
  yield (all three Firewood). Closes Tier 0 item 0.1 — no `giveItem()`
  call site anywhere in the script hand-authors a registry-covered item
  anymore.

**New — WORLD DATA**
- Street grid grown from 3 north-south × 3 east-west streets (9
  intersections, 12 mid-blocks) to 5×4 (20 intersections, 31 mid-blocks).
  Added Maple St (new southernmost east-west street) and 4th/5th St (new
  outer-ring north-south streets, west and east of the existing three).
  Water St remains the fixed north edge.
- 11 new intersections and 19 new mid-blocks, all outer-ring content per
  the low-density design principle (shorter descriptions, fewer parked
  cars/props than downtown).
- 4 new buildings, containers only, no items in any of them, no locks on
  any door:
  - **Oak Apartments** (4 units, no superintendent's unit) at
    `mid_poplar_2_4` — each unit is a single combined room rather than a
    full Acorn-style suite.
  - **Auto Workshop** (`auto_shop`, `auto_shop_back`) at `mid_main_3_5`.
  - **Police Station** (`police_lobby`, `police_evidence`) at `maple3rd`.
  - **Riverside Freight**, an industrial/warehouse building
    (`industrial_floor`, `industrial_office`) at `maple2nd`.

**Changed — Street renumbering**
- North-south streets renumbered west→east as 4th·2nd·1st(center)·3rd·5th
  (west of center gets evens, east gets odds). The 9 existing
  intersections were renamed accordingly (`poplar1st`→`poplar2nd`,
  `main1st`→`main2nd`, `main2nd`→`main1st`, `water1st`→`water2nd`,
  `water2nd`→`water1st`; `outside`, `poplar3rd`, `main3rd`, `water3rd`
  keep their ids). `building` display strings and every exit/label
  touching these rooms were updated to match.
- The 12 existing mid-block rooms were **also** renamed to keep ids
  internally consistent with the new numbering (e.g. `mid_poplar_1_o` →
  `mid_poplar_1_2`, `mid_main_2_3` → `mid_main_1_3`, `mid_1st_p_m` →
  `mid_2nd_p_m`). The handoff's explicit rename list only covered the two
  mid-blocks with building anchors on them; the rest were renamed to
  match for consistency, since leaving some ids on the old numbering
  scheme and others on the new would read as an authoring error rather
  than a deliberate choice. Flagged here per the "no duplicated source of
  truth" / judgment-call convention.
- Descriptions rewritten for `outside`, `main1st` (was `main2nd`), and
  `water3rd` per the handoff; `poplar3rd`'s description was left as-is
  (still geographically accurate).

**New — exits at the grid's old boundary**
- The handoff explicitly called out `main3rd` and `water3rd` gaining new
  east exits (to the new 5th St column). Working through the full grid
  geometry, the same logic applies to every other room that sat on the
  old grid's edge: `poplar3rd` also gains an east exit (to `poplar5th`),
  and `outside`/`poplar2nd`/`main2nd`/`water2nd` gain new south/west
  exits (to the new Maple row and 4th St column respectively) — all
  wired via the new mid-blocks the handoff already specifies
  (`mid_poplar_3_5`, `mid_1st_mp_p`, `mid_poplar_2_4`, `mid_main_2_4`,
  `mid_water_2_4`). The handoff's "existing renamed intersections keep
  the same number of exits" note doesn't hold once the grid grows on
  both edges; resolved using the grid data itself (Part C's node table
  and the full new-mid-block list) as ground truth, since that data is
  exact and this generalization follows directly from it.

**RENDERING**
- `mapToSvg`'s row-flip generalized from a hardcoded `(2 - row)` to
  `(MAP_MAX_ROW - row)`, with new `MAP_MAX_COL = 4` / `MAP_MAX_ROW = 3`
  constants.
- River-line coordinates in `renderMapClose` and `renderMapWide`
  generalized from `mapToSvg(0,2)`–`mapToSvg(2,2)` to
  `mapToSvg(0, MAP_MAX_ROW)`–`mapToSvg(MAP_MAX_COL, MAP_MAX_ROW)`.
- `MAP_WIDE_VIEWBOX` grown from `{x:20,y:20,w:360,h:360}` to
  `{x:20,y:20,w:610,h:480}` to fit the larger grid extent.
- `MAP_STREETS` rebuilt as 9 chains (4 horizontal + 5 vertical, up from
  6). `MAP_BUILDINGS` updated: 7 existing entries retargeted to their
  renamed anchors, 4 new entries added for the new buildings.

**Documentation**
- Roadmap reconciled: Tier 0 item 0.1 (giveItem() registry cleanup)
  removed — closed in full. Tier 1 item 2 (Adams/Washington outer-ring
  expansion) removed rather than edited in place, per the handoff's
  recommendation — this pass substantially fulfills its intent but with
  materially larger scope and different street names (4th/5th/Maple, not
  "Adams/Washington") than the item's original wording described.

**Notes / assumptions**
- Industrial building's name: "Riverside Freight" (handoff left this
  open, coding session's call).
- New container capacities followed existing precedent (e.g. Auto
  Workshop's Workbench at 30kg ≈ Hardware Store's Tool Wall).
- Industrial office's safe left unlocked (recommended default in the
  handoff) rather than seeded as a locked dead end.
- Police Station's evidence room: only `evidencelocker` was implemented
  as an actual container. The handoff also listed a `cell` container id,
  but its own parenthetical ("the cell itself isn't a container, just
  flavor") reads as the room description doing that work instead — the
  cell is mentioned in the room's `desc` text only.

**Explicitly NOT changed**
- No PLAYER STATE, ACTIONS/SIMULATION, WORLD INTERACTION,
  STAMINA/FATIGUE, CRAFTING, or PERSISTENCE code touched anywhere in this
  pass. Acorn Apartments' interior (rooms, containers, items) is
  untouched — only its map anchor id changed. No items were added to any
  of the 4 new buildings. No locks were added anywhere new; the existing
  Acorn master-key mechanic is untouched. No rooftops (Tier 1 item 1) —
  not touched.

**Validation performed**
- `node --check` on the extracted script: passes.
- Full reachability check: all 93 rooms in `makeDefaultWorld()` resolve
  through `MAP_NODES`/`MAP_ANCHORS`, and all 93 are reachable from the
  starting room (`living`) via a BFS over `exits`. Every `MAP_NODES` id
  has a corresponding room; every `MAP_STREETS` chain and `MAP_BUILDINGS`
  anchor resolves to a valid node.
- Diff against `ashfall_0_2_5.html`: every changed hunk falls within
  `CONFIG/CONSTANTS` (version bump), `WORLD DATA`, the two
  `INVENTORY/ITEM SYSTEM` and `FIRE/COOKING` `giveItem()` call sites, and
  `RENDERING`/`MAP`. No hunk touches PLAYER STATE, CORE UTILITIES, WORLD
  INTERACTION, SURVIVAL/TIME SIMULATION, STAMINA/FATIGUE, CRAFTING, or
  PERSISTENCE.

**Version**: `GAME_CONFIG.VERSION` `"0.2.5"` → `"0.2.6"`

---

## v0.2.5 — In-Game Viewing Map

Implements roadmap Tier 1, item 3 in full, per the "Ashfall v0.2.5.md"
handoff. Ported directly from `map_demo.html`, the standalone prototype
built and iterated on during the planning session.

**New**
- The side-menu `Map` section's placeholder is replaced with a working
  static orientation map: a Close/Wide zoom toggle in the section header
  (styled like the existing `#gaitBar` pace buttons) and an SVG map below
  it.
- **Close view** (default): centers on the player's current location,
  draws every street-grid node, and labels each of the 7 buildings with a
  small marker (two-line label for multi-word names, e.g. "Hardware" /
  "Store"). Re-centering on a location change is animated — a ~350ms
  cubic-ease-out `viewBox` tween via `requestAnimationFrame` (`viewBox`
  isn't CSS-animatable).
- **Wide view**: a fixed `viewBox` showing the whole grid. No building
  markers — streets only, each identified by its own name running along
  the line itself via `<textPath>` (repeated three times with a bullet
  separator), with a thin low-opacity guide stroke underneath.
- Switching between Close and Wide re-renders the SVG content and snaps
  the `viewBox` to the new view (no animation); only in-Close location
  changes animate.
- A single player-position dot repositions to the resolved map node in
  both views whenever the map re-renders.
- `#sideMenu` widened from 270px to 360px (the width the demo's two-line
  building labels and the Wide view were tuned against).

**Explicitly out of scope** (per the handoff, not implemented here)
- Fog of war / reveal-as-explored — the full grid always renders.
- Room/floor-level detail — the map resolves to *building*, never a
  specific room or floor within one.
- Click-to-travel or any interaction beyond viewing and switching zoom.
- Rooftops and the Adams/Washington outer-ring expansion — neither exists
  in world data yet; the coordinate scheme is deliberately extensible
  (plain integer/half-integer grid, no hardcoded bounds) for when they do.

**Sections touched**
- **WORLD DATA** — additive only, placed after `itemFromRegistry`/
  `itemsFromRegistry` and before `makeDefaultDoors()`: `MAP_NODES` (21
  street-grid node coordinates) and `MAP_ANCHORS` (id -> map node for
  every non-street room), plus `mapNodeForRoom()`. No existing room,
  item, container, exit, door, or window definition changed.
- **RENDERING** — new self-contained MAP sub-section (`MAP_STREETS`,
  `MAP_BUILDINGS`, `mapToSvg`, `mapPathD`, `mapRepeatedLabel`,
  `renderMapClose`, `renderMapWide`, `mapPositionPlayer`,
  `mapTargetViewBox`, `mapUpdateViewBox`, `renderMap`). `renderMap()` is
  called once, at the end of the existing top-level `render()`, alongside
  the other per-frame render calls — no new render loop or hook point was
  needed since `render()` already runs on every location change.
- **EVENTS/UI HELPERS** — click handlers for the two zoom-toggle buttons,
  added next to the existing `#gaitBar` handler.
- Menu markup/CSS: the `Map` `menu-section`'s placeholder div replaced
  with the toggle + `<svg id="mapSvg">`; new `.map-*`-prefixed CSS rules
  (no existing class names touched).

**Explicitly NOT changed**
- No PLAYER STATE, movement/WORLD INTERACTION, SURVIVAL/TIME SIMULATION,
  CRAFTING, FIRE/COOKING, or PERSISTENCE code — this is a RENDERING
  addition plus two small pieces of new static WORLD DATA, no new
  mechanic.
- No existing room, item, exit, or content definitions were altered.

**Validation performed**
- Extracted script passes `node --check` with no syntax errors.
- Confirmed via script that every room id returned by `makeDefaultWorld()`
  (50 rooms) resolves through `MAP_NODES` or `MAP_ANCHORS` — exact set
  match, none missing, none extra.
- Full diff against v0.2.4 confirms the only changes are the map feature
  (CSS, menu markup, `MAP_NODES`/`MAP_ANCHORS`/`mapNodeForRoom`, the new
  MAP rendering sub-section, the zoom-toggle event handlers, the
  `renderMap()` call, and the sideMenu width) plus the version string —
  no mechanics code touched.
- Manually traced the starting room (`living` → `mid_poplar_1_o`) through
  `mapToSvg`/`mapTargetViewBox` to confirm the default Close-view
  `viewBox` centers correctly on game start.

**Documentation**
- `Ashfall_Development_Roadmap.md` reconciled against the actual v0.2.5
  code (it had drifted — two Tier 0/1 items it still listed as pending
  were already implemented):
  - Tier 1 item 3 (this feature, In-Game Viewing Map) removed.
  - Tier 0 item 0.1 ("Remove the Phone placeholder") removed — the code
    has no Phone-related menu section, item, comment, or state field
    remaining; already fully implemented.
  - Tier 1 item 4 ("Item Registry / ID-Based Item Definitions") removed
    — `ITEM_REGISTRY` and `itemsFromRegistry()` are already in place and
    used throughout `makeDefaultWorld()`; already fully implemented.
  - New Tier 0 item 0.1 added in its place: four `giveItem()` call sites
    (Firewood ×3 in INVENTORY/ITEM SYSTEM and FIRE/COOKING, Spare
    batteries ×1 in INVENTORY/ITEM SYSTEM) still construct a literal item
    object instead of reading `ITEM_REGISTRY` via `itemFromRegistry()` —
    confirmed present via `grep` against the v0.2.5 script.
  - All subsequent Tier 1/2/3 items renumbered accordingly.

**Version**: `GAME_CONFIG.VERSION` `"0.2.4"` → `"0.2.5"`

---

## v0.2.4 — Fix missing mid-block movement directions

**Fixed**
- Every mid-block `mid_*` WORLD DATA location (12 total) has two through
  exits — one back the way you came, one continuing onward. The v0.2.3
  pass that added compass-direction wording to movement labels only
  applied it to the "back" exit (`"Head [direction] toward X"`); the
  "onward" exit kept its pre-existing `"Continue toward X"` label with no
  direction word at all. Depending on the street segment, the missing
  direction was east or north in each case (never west/south, since those
  always landed on the "back" exit of the pair).
- Fixed by adding the correct compass word to each affected `"Continue
  toward X"` label, derived as the opposite of that mid-block's paired
  `"Head [direction]"` exit and cross-checked against the adjacent
  intersection locations' own exit lists for consistency (e.g.
  `mid_main_1_2`'s "toward 2nd St" exit must be east, since `main2nd`'s
  exit back to `main1st` is labeled west).
- Affected locations: `mid_poplar_1_o`, `mid_poplar_o_3`, `mid_1st_p_m`,
  `mid_2nd_o_m`, `mid_3rd_p_m`, `mid_main_1_2`, `mid_main_2_3`,
  `mid_1st_m_w`, `mid_2nd_m_w`, `mid_3rd_m_w`, `mid_water_1_2`,
  `mid_water_2_3`.

**Scope**
- WORLD DATA only (content) — exit `label` strings exclusively. No exit
  `to` targets, no other fields, no mechanics code touched.

**Validation performed**
- Extracted script passes `node --check` with no syntax errors.
- Confirmed via `grep` that no `"Continue toward"` label (missing a
  direction word) remains in the file — all 12 now read `"Continue
  [direction] toward X"`.
- Each derived direction was cross-checked against the corresponding
  full-intersection location's exit list to confirm the two ends of each
  street segment agree on direction (e.g. a "west" exit on one side
  implies an "east" exit on the other).

**Version**: `GAME_CONFIG.VERSION` `"0.2.3"` → `"0.2.4"`

---

## v0.2.3 — no entry was written

This version shipped and no entry was written for it. `v0.2.4`'s closing line
records the bump as `"0.2.3"` → `"0.2.4"`, and two later entries name v0.2.3
directly, so the gap is an omission rather than a skipped number. Nothing has
been reconstructed: `git log` is the only surviving record of what it changed,
and a reconstruction written this long after the fact would not be the record
this file exists to keep. There is no `v0.2.3` tag either — tagging begins at
v0.4.0.

This placeholder exists so the gap reads as known rather than as an oversight
waiting to be found again.

**Version**: `GAME_CONFIG.VERSION` `"0.2.2"` → `"0.2.3"`

---

## v0.2.2 — Structural reorganization pass

Pure layout/reorg pass. No gameplay, balance, or rendering behavior changed.

**Summary**
The file's ARCHITECTURE comment documents an intended section order and
grouping rule ("ACTIONS grouped by system, as contiguous blocks"), but the
actual code had drifted from it — three sections were fragmented into
separate chunks scattered across the file. This pass makes the physical
layout match the documented architecture.

**Sections merged into single contiguous blocks**
- **INVENTORY / ITEM SYSTEM** — previously split into 3 chunks (pool/lookup
  helpers, quantity-transfer actions, item-detail action list) with WORLD
  INTERACTION, SURVIVAL/TIME SIMULATION, CRAFTING, and FIRE/COOKING sitting
  between them. Now one contiguous section, internal order preserved:
  1. pool/lookup helpers (`totalWeight` … `hasWatch`)
  2. quantity-transfer actions (`normalizeQty`, `doTake`, `doStore`,
     `doConsume`, `doEquip`, `doUnequip`)
  3. `getItemActions`
- **WORLD INTERACTION** — previously split into 2 chunks (lookup helpers,
  actions) with SURVIVAL/TIME SIMULATION and STAMINA/FATIGUE sitting between
  them. Now one contiguous section:
  1. lookup helpers (`doorsForRoom` … `getExitsForRoom`)
  2. actions (`doMove` … `doUnlockContainer`)
- **SURVIVAL / TIME SIMULATION** — previously split into 2 chunks with the
  entire STAMINA/FATIGUE SYSTEM sandwiched between them. Now one contiguous
  section, with STAMINA/FATIGUE folded in as an explicit sub-block (its own
  subheader comment retained):
  1. `applyHungerThirst`, `applyWorldTicking`, `applyEnergyBaseline`,
     `checkGameOver`
  2. STAMINA/FATIGUE SYSTEM sub-block (`applyExertion`,
     `isExertionDelayActive`, `energyRecoveryMultiplier`,
     `staminaMaxForEnergy`, `hungerThirstRecoveryPenalty`,
     `fatigueRecoveryAllowed`, `recoveryStep`, `sleepAvailable`,
     `estimateSleepMinutes`)
  3. `runAwakeStep`, `advanceTime`
  - The duplicate "SURVIVAL / TIME SIMULATION" banner that previously
    re-introduced the second fragment was removed, since the section is now
    a single contiguous block (each top-level header now appears exactly
    once, per the file's own contiguity rule).

**Function relocation**
- `doRestart` moved out of SURVIVAL/TIME SIMULATION (where it sat next to
  `advanceTime`) and into **PERSISTENCE**, placed directly after
  `applyLoadedData`. Rationale: it resets/reinitializes game state — the
  same kind of whole-state replacement `applyLoadedData` does on load —
  rather than a time-driven update. Implementation unchanged.

**Sections left untouched** (already contiguous, correct order)
CONFIG/CONSTANTS, WORLD DATA, PLAYER STATE, CORE UTILITIES, CRAFTING,
FIRE/COOKING, PERSISTENCE (aside from the `doRestart` insertion above),
EVENTS/UI HELPERS, RENDERING.

**Documentation**
- ARCHITECTURE comment updated:
  - Version reference bumped from 0.2.1 to 0.2.2.
  - Added a note that STAMINA/FATIGUE is a sub-section living inside
    SURVIVAL/TIME SIMULATION, not a separate top-level section (to prevent
    future passes from re-splitting it out).
  - Added a note that `doRestart` lives in PERSISTENCE, not SIMULATION,
    since it performs a full state reset rather than a time-driven update.
  - The "_uid is the stable identity" paragraph and the CONTENT vs
    MECHANICS guidance were left as-is (still accurate).

**Explicitly NOT changed**
- No function implementation, name, or variable was changed.
- No rendering logic changed.
- No functions were reordered *within* a section beyond what was needed to
  merge fragments together.
- No save format / version-compat logic changed beyond the version string.
- No new mechanics, tags, items, rooms, or content were added.
- No new abstractions, helper layers, or data refactors were introduced.
- No balance constants (`GAITS`, `DECAY`, etc.) were changed.

**Validation performed**
- Extracted script passes `node --check` with no syntax errors.
- Full non-blank-line multiset diff against 0.2.1 confirms the only content
  differences are: the version string, the three ARCHITECTURE comment
  additions listed above, and removal of the one duplicate section banner —
  everything else is a pure line-level move, no changed lines within any
  moved function body.
- Confirmed each of the twelve top-level section headers appears exactly
  once, in the documented order, with no other top-level header nested
  inside a section's span.

**Version**: `GAME_CONFIG.VERSION` `"0.2.1"` → `"0.2.2"`

---

## v0.2.1 — Stamina & Fatigue System

**New**
- Two new persistent vitals: **Stamina** (0–100, visible) and **Fatigue**
  (0–100, hidden).
- Strenuous actions now declare an **Exertion** amount; Stamina absorbs it
  first, and any excess spills into Fatigue. Exertion is not a stat itself —
  it's resolved once, right after a task completes.
- New dedicated Stamina/Fatigue module owns all the rules below. Tasks still
  just declare Exertion; they don't contain Stamina logic themselves.

**Exertion costs**
- Tree chopping: 30 Exertion.
- Fishing: 8 Exertion.
- Jogging: 0.5 Exertion/minute while moving at the "fast" gait. Walking
  costs nothing.
- Exertion is applied only after a task successfully completes — never at
  task start, never mid-task, and never on failure.

**Stamina recovery**
- Baseline recovery: 1 Stamina/minute while awake.
- Recovery only begins after 1 full game minute with no exertion; any
  completed exertive action resets that delay.
- Recovery speed scales with Energy (100% at Energy 80–100, down to 25% at
  Energy 0–19).
- Low Energy also caps the *maximum* Stamina you can currently recover to
  (100 above Energy 40, 80 at Energy 20–39, 50 below Energy 20). This cap is
  temporary and never forcibly reduces Stamina you already have.
- Low Hunger and low Thirst each cut recovery speed by 15%, stacking
  additively (up to -30% when both are low).

**Fatigue recovery**
- Fatigue recovers continuously at 0.5/minute, but only once Stamina has
  reached its current (Energy-capped) maximum.
- Fatigue recovery is impossible while Energy is below 20.
- Fatigue never directly damages Health. At Fatigue 100, movement is
  restricted to Sneaking until it drops.

**Energy changes**
- Awake baseline Energy depletion is now 100 → 0 over 24 game hours
  (previously ~16 hours).
- Active Stamina recovery now costs Energy at 2× the awake baseline; active
  Fatigue recovery costs 4×. This is on top of normal baseline drain, not a
  replacement for it.

**Rest (reworked)**
- Rest still lasts exactly 1 game hour.
- Rest now recovers Stamina/Fatigue at a flat 0.5 Stamina/minute *without*
  the extra recovery-related Energy cost.
- Rest no longer restores Energy directly — only Sleep does. Baseline
  Energy drain still applies during Rest.

**Sleep (reworked)**
- Sleep is now a fully separate simulation state: normal awake Energy
  depletion, Stamina recovery, and Fatigue recovery are all suspended while
  asleep.
- Sleep duration is no longer fixed at 8 hours — it's derived from how much
  Energy is missing, at a rate of 10 Energy/hour.
- If Fatigue is present when Sleep begins, it's snapshotted and temporarily
  caps how high Energy can recover that night
  (`ceiling = 100 − Fatigue at sleep start`).
- Fatigue always fully resets to 0 by the time you wake, regardless of the
  snapshot.
- After waking, Sleep is unavailable again for 8 game hours.

**UI**
- Stamina is now shown in the stats panel as a whole number, alongside
  Hunger/Thirst/Energy/Health.
- Fatigue remains hidden from normal gameplay UI (no debug panel exists in
  this build to expose it through).
- The Sleep button now shows its actual estimated duration instead of a
  fixed time, and is replaced with a note when Sleep isn't available yet
  (still on cooldown).
- Gait switching is locked to Sneak whenever Fatigue is at 100.

**Notes / assumptions**
- No "low Hunger/Thirst" threshold existed anywhere in the prior build to
  inherit, so this pass introduces one explicit value (30) used for both —
  easy to retune later if needed.
- All existing v0.1.3 systems (tasks, inventory, movement, crafting, fire,
  save/load) are unchanged apart from the specific hooks listed above.

**Version**: `GAME_CONFIG.VERSION` `"0.1.3"` → `"0.2.1"`

---

## v0.1.3

**Fixed**
- **"Take 1" disappearing bug** (root cause of the reported
  `Cannot read properties of undefined (reading 'qty')` class of errors):
  splitting a stack copied `_uid` onto the new stack via `{ ...item }`, so
  the moved portion and the remainder briefly shared one uid. The detail
  panel would then resolve to the wrong copy and show a stale quantity.
  Fixed by stripping `_uid` whenever `addToList()` creates a new stack
  entry, so every split stack gets its own fresh id on demand.

**Hardened**
- Added `getItemAt(list, index)` — safe list lookup that returns `null`
  instead of throwing when an index is stale or out of range.
- Added `normalizeQty(requested, available)` — explicit quantity
  resolution (`qty == null ? available : qty`) replacing the ambiguous
  `qty || it.qty` pattern; rejects 0, negative, NaN, non-integer, and
  over-limit values.
- `doTake`, `doStore`, `doConsume`, and `doEquip` now resolve their source
  item defensively via `getItemAt` and bail out safely if it's gone,
  instead of assuming the array index is still valid.
- `getItemActions()` now resolves its item via `getItemAt` as well, so it
  can no longer throw on a stale `list[index]`.
- Transfers remain atomic: capacity/destination checks still happen before
  any mutation, so a failed transfer changes nothing.

**Organization** (no behavior change)
- Added clear section headers throughout the script: CONFIG/CONSTANTS,
  WORLD DATA, PLAYER STATE, CORE UTILITIES, INVENTORY/ITEM SYSTEM, WORLD
  INTERACTION, SURVIVAL/TIME SIMULATION, CRAFTING, FIRE/COOKING,
  PERSISTENCE, EVENTS/UI HELPERS, RENDERING.
- Added an architecture comment near the top of the script explaining the
  data-driven design, the content-vs-mechanics split, and the uid-vs-index
  identity rule.
- Documented the ROOM, CONTAINER, EXIT, and ITEM data schemas inline as
  comments above `makeDefaultWorld()`.
- No changes to rendering logic, save file format, or world/item content.

**Version**: `GAME_CONFIG.VERSION` `0.1.2` → `0.1.3`
