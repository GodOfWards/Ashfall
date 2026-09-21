# Ashfall Handoff — Presentation & Signal Pass

Current shipped version: v0.5.1
Implied version-change type: PATCH
Issues: #124 — the item list cannot show item state; #108 — markup and
readability fixes that stand on their own; #110 — move buttons print a duration
the move doesn't charge; #113 — every street name is spaced as if it were
POPLAR ST; #126 — a spent fire-starter never leaves the inventory, and fire ends
with no signal; #131 — the four dev validators say "call from the browser
console", and the IIFE makes that impossible

> **There is a sibling handoff at the top level.**
> `handoffs/reachable-tools-and-content-corrections.md` is the other half of the
> same planning session. The two are independent — neither reads the other's
> code — but **do that one first**, so the version numbers fall in the order the
> changelog entries describe. Implement one handoff per pull request; do not
> merge the two.

## What this is

Everything the player reads, plus the one mechanics fix that gives the reading
something to say, plus the dev seam that makes the project's own checks
runnable.

The split against the sibling handoff is `CLAUDE.md`'s: instance data never
rides along with a mechanics change. #126 is a mechanics change
(INVENTORY / ITEM SYSTEM), so all the instance content went to the other pass
and everything here is rendering, markup, a comment, and one rule.

The six:

- **#126** — `consumeMatchUse()` decrements a fire-starter's durability and
  never removes it. Worse, once the last one is spent, "Light the stove" and
  "Set up the campfire kit" simply stop being rendered, with no log line and no
  visible cause: an entire subsystem disappears and the player is left to infer
  it. Tom's decision: **consume at zero, and add the dim note** — the shape
  `renderHereActionsPanel()` already uses for a locked door with no key and for
  sleep on cooldown.
- **#124** — a sealed and an opened can render identically in the item list.
  Tom's decision: **an `(Open)` suffix on the name**, opened only. The
  durability half of #124 is not solved by a suffix and is now **#134**.
- **#108** — four independent markup and readability defects, all plain HTML
  and CSS plus one `renderItemList()` change.
- **#113** — one label width (`"POPLAR ST"`) is reserved for all sixteen street
  names, so `"1ST ST"` is over-reserved by 63%.
- **#110** — the display floor hides a sub-minute move cost. Tom's decision:
  **keep the floor, write down why.** Comment only.
- **#131** — the four `validate*()` helpers are local bindings inside the IIFE
  and cannot be called from the console, which all four comments claim they can.

## Relevant existing state

Verified by reading `ashfall.html` at v0.5.1, not recalled.

### #126 — the fire-starter

```js
function findFireStarter(){
  for(const list of invPools()){
    const m = list.find(it=> it.tags && it.tags.includes("fire-starter") && it.durability && it.durability.current>0);
    if(m) return m;
  }
  return null;
}
function hasMatchUses(){ return !!findFireStarter(); }
function consumeMatchUse(){
  const m = findFireStarter();
  if(!m) return false;
  m.durability.current -= 1;
  return true;
}
```

`findFireStarter()` returns the **item**, not its list — which is why nothing
can splice it. `consumeMatchUse()` has exactly two callers: `doLightStove()` and
`doBuildFire()`, both of which `return` early when it returns false.

The two render gates that vanish:

```js
if(room.hasStove && !room.heatActive && hasMatchUses()){
  hereBox.appendChild(actionButton("Light the stove " + fmtDuration(LIGHT_STOVE_MIN), doLightStove));
}
if(!room.cannotHaveFire && !room.heatActive && hasMatchUses() && canBuildFire(room)){
  …
}
```

Every room with `hasStove:true` also carries `cannotHaveFire:true` (`kitchen`,
`twobee_kitchen`, `onea_kitchen`, `onebee`), so the two notes below can never
both appear in one room today. That is a fact about the current content, not a
rule — write the code so both firing would be harmless.

The dim-note pattern to match, which already appears three times:

```js
const note = document.createElement("div");
note.style.cssText = "color:var(--ink-faint); font-size:12.5px; padding:6px 0;";
note.textContent = `The door to ${label} is locked.`;
hereBox.appendChild(note);
```

Four items carry `durability`: `box_of_matches` and `lighter` (`mode:"uses"`),
`flashlight` and `portable_radio` (`mode:"time"`). Only the first two carry
`fire-starter`.

### #124 — the item row

```js
meta.appendChild(nameEl);
meta.appendChild(document.createTextNode(` ×${it.qty} — ${total} kg `));
const catSpan = document.createElement("span");
catSpan.className = "cat";
catSpan.textContent = `(${it.category})`;
```

`addToList()` keeps sealed and opened stacks apart:

```js
&& !i.durability && !!i.sealed === !!item.sealed);
```

so `sealed` is genuinely three-valued on an item — `undefined` (never a packaged
thing), `true`, `false` — and all three are meaningful. The detail box already
reads it:

```js
if(it.sealed !== undefined){ … it.sealed ? "Sealed" : "Opened" … }
```

### #108 — the four defects

1. `<h3 class="map-heading">Map <div id="mapZoomToggle">` — a `<div>` is flow
   content and is not legal inside a heading. (`<h2>Menu <button…>` on the line
   above **is** legal; a button is phrasing content.)
2. `--ink-faint:#666b72` and `--danger:#b3503f`, both carrying small text.
   `button.action.blocked` and `button.mini.blocked` additionally carry
   `opacity:.45`.
3. `.itemname` is a `<b>` with a click handler — the control that opens item
   detail, and the only control in the game that is not a `<button>`. Its
   weight and colour come from `ul.itemlist .meta b{ color:var(--ink);
   font-weight:600; }`, a selector that will stop matching.
4. `<svg id="mapSvg" viewBox="0 0 260 260">` — 260 is
   `MAP_ZOOM_RANGE.close.base` (2) × `MAP_SPACING` (130), restated in HTML where
   nothing catches it drifting.

### #113 — the label metrics

```js
let mapLabelW, mapLabelInset, mapLabelTiers, mapLabelClearance;
function mapSetLabelWidth(w){
  if(!Number.isFinite(w) || w <= 0) return;
  mapLabelW = w;
  mapLabelInset = w / 2 + MAP_LABEL_EDGE_GAP;
  mapLabelTiers = [ { minVisible: 6*w, count:3 }, { minVisible: 3*w, count:2 }, { minVisible: 1*w, count:1 } ];
  mapLabelClearance = w / 2 + MAP_LABEL_OFFSET + MAP_LABEL_CAP;
}
mapSetLabelWidth(MAP_LABEL_W_FALLBACK);
```

`mapBindStreetLabels()` already measures per street and throws the detail away:

```js
if(els.length){ els[0].style.display = ""; widest = Math.max(widest, mapTextWidth(els[0])); }
mapStreetLabels.push({ a, b, angle, horizontal: a.y === b.y, els });
…
mapSetLabelWidth(widest);
```

The four values have four readers: `mapLabelPositions()` (tiers, inset),
`mapClearCrossings()` (`mapLabelW` twice — the `room` guard and the `kept`
separation filter — plus clearance), `mapLabelBox()` (`mapLabelW`), and
`mapLabelHitsPlayer()` (clearance).

The hidden-node hazard #113 flags is **already handled**: Wide's pool ships
`display:none`, and the bind shows `els[0]` before measuring precisely because a
hidden SVG text node measures zero.

### #110 — the display floor

```js
const MIN_MOVE_MIN = 1;
const MIN_DISPLAY_MIN = 1;
function moveMinutes(distanceM, gridTravel){
  const floor = gridTravel ? MIN_MOVE_MIN * distanceM / BLOCK_M : MIN_MOVE_MIN;
  return Math.max(floor, distanceM / GAITS[effectiveGait()].speed / 60);
}
function fmtDuration(min){ min = Math.max(MIN_DISPLAY_MIN, Math.round(min)); … }
```

A 50 m half-move costs `50/1.2/60 = 0.694` at Walk and `max(0.5, 0.417) = 0.500`
at Jog, and prints `(0:01)` for both.

Three `fmtDuration()` callers can go sub-minute; every other caller is fed a
fixed constant of 5 minutes or more:

- the Move and Here exit buttons, via `exitMinutes()`;
- `estimateSleepMinutes()` — `sleepAvailable()` only requires energy *below* the
  ceiling, so the gap can be arbitrarily small;
- `fmtDuration(room.fireMinutesLeft)` in `renderLocationPanel()`, which
  decrements continuously toward zero.

### #131 — the closure

The script is `(function(){ "use strict"; … })();`. All four helpers —
`validateItemRegistry()`, `validateLocations()`, `validateRoomSchema()`,
`validateReachability()` — are local bindings inside it. Each carries a comment
saying "Call manually from the browser console"; none can be. The v0.5.1 pass
verified `validateReachability()` against a temporary copy of the page with the
four names hoisted onto `window`.

## Rules / mechanics

One rule changes, and only one: **a fire-starter is destroyed when its last use
is spent.**

```
WHEN consumeMatchUse() takes the last use of a fire-starter
  (durability.current reaches 0 or below)
THEN that item is removed from the list it was in,
AND  a log line says so,
AND  consumeMatchUse() still returns true — the use it just spent was real,
     and the caller's action succeeds.
```

This is the precedent for **#116** (tool wear), which will add durability
spenders beyond this one, and for any future worn-out tool. Say so in the
changelog: the rule is "a tool that reaches zero is gone", not "matches are
special".

Nothing else about fire changes — `findFireStarter()`'s `current > 0` predicate,
`hasMatchUses()`, `canBuildFire()`, `FIRE_BUILD_WOOD`, `FIRE_MINUTES_PER_WOOD`
and `FIRE_MAX_MIN` are all untouched.

## Data / schema changes

**None.** No new state field, no new item property, no new room or container
field, no new save field. `versionCompat()` does not move and `SAVE_KEY` stays
`ashfall_save_v0.5`.

`it.sealed`, `it.durability` and `it.tags` are all read exactly as they are
today. `window.ashfallDev` is a browser global, not game state, and is never
serialized.

## In scope

### 1 — #126: consume the spent fire-starter, and say so

**a.** `findFireStarter()` returns the list and index alongside the item, so the
item can be spliced:

```js
function findFireStarter(){
  for(const list of invPools()){
    const index = list.findIndex(it=> it.tags && it.tags.includes("fire-starter")
                                   && it.durability && it.durability.current>0);
    if(index>=0) return { list, index, item:list[index] };
  }
  return null;
}
```

`hasMatchUses()` stays `return !!findFireStarter();` and needs no edit. This is
the shape `findItemByUid()` already uses, so it is the file's own idiom.

**b.** `consumeMatchUse()` spends the use and removes the item at zero:

```js
function consumeMatchUse(){
  const found = findFireStarter();
  if(!found) return false;
  const m = found.item;
  m.durability.current -= 1;
  if(m.durability.current <= 0){
    found.list.splice(found.index, 1);
    log(`The ${m.name.toLowerCase()} is spent.`, "warn");
  }
  return true;
}
```

The whole entry is spliced rather than `qty` being decremented, because
`addToList()` never merges a durability-bearing item and every fire-starter
placement in the world is `qty:1` — so the entry is exactly one unit. A pool or
placement giving `qty > 1` would mean two matchboxes sharing one durability
object, which is already wrong and belongs to **#134**/#116, not here. Note this
in the changelog rather than defending against it.

`"The box of matches is spent."` / `"The lighter is spent."` — understatement,
present tense, the tone the file already uses. Retunable.

**c.** The dim note, in `renderHereActionsPanel()`. Each of the two existing
gates gains an `else if` for the case where everything holds *except* a usable
fire-starter:

```js
if(room.hasStove && !room.heatActive && hasMatchUses()){
  hereBox.appendChild(actionButton("Light the stove " + fmtDuration(LIGHT_STOVE_MIN), doLightStove));
} else if(room.hasStove && !room.heatActive){
  hereBox.appendChild(hereNote("Nothing you're carrying will light it."));
}

if(!room.cannotHaveFire && !room.heatActive && hasMatchUses() && canBuildFire(room)){
  …
} else if(!room.cannotHaveFire && !room.heatActive && canBuildFire(room)){
  hereBox.appendChild(hereNote("Nothing you're carrying will light a fire."));
}
```

Both notes are *functional UI text*, held to clarity rather than to the game's
descriptive tone. Both are retunable.

The campfire note is gated on `canBuildFire(room)` on purpose: a player with no
campfire kit and no firewood is not being denied a fire by the missing
match, and telling them otherwise would be wrong.

**d.** `hereNote(text)` — extract the three existing inline-styled notes and
these two into one helper beside `actionButton()`, since the style literal would
otherwise be written five times:

```js
function hereNote(text){
  const note = document.createElement("div");
  note.style.cssText = "color:var(--ink-faint); font-size:12.5px; padding:6px 0;";
  note.textContent = text;
  return note;
}
```

The three existing call sites (locked door, sleep cooldown, not tired enough)
move to it. That is the "same fact in two places belongs in a shared definition"
rule applied to a style string; it is a refactor with no behaviour change and
must be provable by diff.

### 2 — #124: the `(Open)` suffix

In `renderItemList()`, between the name element and the ` ×qty` text node:

```js
meta.appendChild(nameEl);
if(it.sealed === false){
  const stateEl = document.createElement("span");
  stateEl.className = "state";
  stateEl.textContent = " (Open)";
  meta.appendChild(stateEl);
}
meta.appendChild(document.createTextNode(` ×${it.qty} — ${total} kg `));
```

Giving:

```
Canned soup ×2 — 0.80 kg (Food)
Canned soup (Open) ×1 — 0.40 kg (Food)
```

**`it.sealed === false` strictly.** `undefined` means the item was never a
packaged thing and shows nothing; `true` means sealed and also shows nothing.
Only the opened state is marked — a sealed can reads as the plain name, which is
Tom's decision and is why there is no `(Sealed)` counterpart.

The suffix sits **outside** the name element, so the clickable control's text
stays exactly the item's name.

CSS: `.state{ color:var(--ink-dim); }` beside the existing `ul.itemlist .cat`
rule. It must not inherit the name's `font-weight:600` — see item 3 below, which
moves that weight onto `.itemname` itself.

The detail box keeps `"Sealed"` / `"Opened"`. The two are in different
grammatical positions — an adjective on a noun versus a status line — and both
read correctly; aligning them is not required. Record the choice.

**Durability is not covered.** A flashlight at 8% and one at 100% still render
identically. That is **#134**, which this pass files nothing new for — it
already exists — and must be named in the changelog as what #124 leaves behind.

### 3 — #108: the four defects

**a. The invalid nesting.** Make `#mapZoomToggle` a sibling of the heading
rather than a child of it:

```html
<div class="map-heading">
  <h3>Map</h3>
  <div id="mapZoomToggle">…</div>
</div>
<svg id="mapSvg" …></svg>
```

`.map-heading`'s `display:flex; justify-content:space-between; align-items:center`
moves from the `<h3>` onto the wrapper. `.menu-section h3` carries
`margin:0 0 8px`, which now sits inside a flex row — move that spacing to the
wrapper so the gap above the map is unchanged. Prove it with a before/after
screenshot of the open side menu, not by assertion.

Leave `<h2>Menu <button id="closeMenu">✕</button></h2>` **as it is**. A button
inside a heading is legal, and changing it is churn with no defect behind it.

**b. The colour tokens and the smallest sizes.** Tom's decision: **both** —
nudge the tokens and raise the sizes.

Tokens:

```css
--ink-faint:#888e97;   /* was #666b72 */
--danger:#c76552;      /* was #b3503f */
```

Measured contrast ratios (computed from the sRGB values, not quoted):

| foreground | on `--bg` #111315 | on `--panel` #1b1e22 | on `--panel-2` #20242a |
|---|---|---|---|
| `--ink-faint` **old** #666b72 | 3.47 | 3.12 | 2.90 |
| `--ink-faint` **new** #888e97 | 5.64 | 5.07 | 4.72 |
| `--danger` **old** #b3503f | 3.67 | 3.29 | 3.07 |
| `--danger` **new** #c76552 | 4.80 | 4.31 | 4.02 |

(The two "old" figures against `--bg` reproduce #108's stated 3.47 and 3.67
exactly, which is the check that this table is computed the same way the issue's
was.)

`#888e97` clears 4.5:1 on all three surfaces, which matters because
`button.action .cost` puts `--ink-faint` on `--panel-2`. #108's suggested
`#7d838b` clears `--bg` (4.87) but not `--panel-2` (4.08), which is why it is not
the value here. The cost is real and must be flagged: `--ink-faint`'s relative
luminance moves from 0.146 to 0.268 against `--ink-dim`'s 0.344, so the panel
headings sit noticeably closer to body text than they do today. The value is
retunable and the hierarchy is the thing to judge it against.

**The `opacity:.45` on blocked buttons is the real defect, and nudging
`--danger` barely touches it.** Composited against the page, a blocked button's
label reads **1.53:1** at the old `--danger` and **1.76:1** at the new one —
effectively invisible either way. Remove the opacity from `button.action.blocked` and
`button.mini.blocked` and express the disabled state through colour and border
directly, so the contrast is a number someone chose rather than a by-product:

```css
button.action.blocked{ border-color:var(--danger); color:var(--danger); cursor:not-allowed; }
button.mini.blocked{ border-color:var(--danger); color:var(--danger); cursor:not-allowed; }
```

which lands the label at 4.02:1 on `--panel-2`. Blocked buttons will read
*louder* than they do today; that is the point, and it is worth a screenshot
before the changelog claims it is better.

Sizes — a **12px floor on every text token**. The starting set, all retunable:

| selector | now | to |
|---|---|---|
| `ul.itemlist .cat` | 10.5px | 12px |
| `#mapZoomToggle button` | 10.5px | 12px |
| `.panel h2`, `.actions-group h2`, `.menu-section h3` | 11px | 12px |
| `button.mini` | 11px | 12px |
| `#gaitBar span` | 11px | 12px |
| `.tabs button`, `.logcount` | 11.5px | 12px |

`button.action .cost`, `.menu-placeholder` and the `#log` variant classes are
already 12px and need no change. The 12.5px sizes (`.detailBox`,
`ul.itemlist li`, `hereNote()`) are already above the floor.

Raising `.panel h2` and `.actions-group h2` to 12px narrows their size
difference from body text at the same time as the colour nudge does. Check the
two together rather than one at a time.

**c. The item name becomes a real button.**

```js
const nameEl = document.createElement("button");
nameEl.className = "itemname";
nameEl.textContent = it.name;
nameEl.addEventListener("click", ()=>{ detailItem = { uid: ensureUid(it), side }; render(); });
```

`ul.itemlist .meta b{ color:var(--ink); font-weight:600; }` will no longer match,
so `.itemname` must carry that weight and colour itself, along with a reset and
a tap target:

```css
.itemname{ background:none; border:none; font:inherit; color:var(--ink); font-weight:600;
  padding:6px 2px; margin:-6px -2px; cursor:pointer; text-align:left;
  text-decoration:underline dotted; text-underline-offset:2px; }
.itemname:active{ color:var(--accent); }
```

The negative margin is what grows the tap target without growing the row — the
padded box overlaps the row's own padding rather than adding to it. Both the
padding and the `:active` treatment are judgment calls and retunable; verify the
row height is unchanged against a before screenshot.

Keep the `<b>` selector in the stylesheet only if something else still uses it;
if nothing does, remove it rather than leaving a rule that matches nothing.

**d. The duplicated viewBox.** Drop `viewBox="0 0 260 260"` from
`<svg id="mapSvg">` entirely. `renderMap()` sets it on the first render —
`mapRenderedZoom` starts `null`, so `zoomChanged` is true and
`mapUpdateViewBox(node, true)` runs — and `render()` is called at the bottom of
the IIFE before anything is interactive.

**Verify there is no flash of an unsized SVG.** An SVG with no `viewBox` and no
width/height attributes has a 300×150 default intrinsic size, so `height:auto`
would resolve to something until the attribute lands. It is inside the closed
side menu (`transform:translateX(-100%)`), so in practice nothing is visible —
but confirm it by opening the menu on first paint rather than reasoning about
it. If a flash does appear, the fallback is to set the attribute from JS at
module scope, derived from `MAP_ZOOM_RANGE.close.base * MAP_SPACING`, which
still removes the duplicated literal.

### 4 — #113: per-street label widths

Replace the four module-level `let`s with one metrics object per street.

**a.** `mapSetLabelWidth(w)` becomes a pure function returning metrics instead
of writing module state:

```js
function mapLabelMetrics(w){
  if(!Number.isFinite(w) || w <= 0) return null;
  return {
    w,
    inset: w / 2 + MAP_LABEL_EDGE_GAP,
    tiers: [ { minVisible: 6*w, count:3 }, { minVisible: 3*w, count:2 }, { minVisible: 1*w, count:1 } ],
    clearance: w / 2 + MAP_LABEL_OFFSET + MAP_LABEL_CAP
  };
}
const MAP_LABEL_METRICS_FALLBACK = mapLabelMetrics(MAP_LABEL_W_FALLBACK);
```

Returning `null` on a bad measurement preserves the existing guard's intent —
the caller falls back rather than taking a zero, which would collapse every tier
to `hi - lo >= 0` and give every street three names.

**b.** `mapBindStreetLabels()` stores each street's own metrics instead of
maxing:

```js
const metrics = els.length ? mapLabelMetrics(mapTextWidth(els[0])) : null;
mapStreetLabels.push({ a, b, angle, horizontal: a.y === b.y, els,
                       metrics: metrics || MAP_LABEL_METRICS_FALLBACK });
```

and the trailing `mapSetLabelWidth(widest)` and the `widest` accumulator go
away. The `els[0].style.display = ""` line stays exactly where it is — it is
what makes the measurement non-zero.

**c.** The four readers take the metrics rather than closing over module state:

- `mapLabelPositions(lo, hi, m)` — reads `m.tiers`, `m.inset`, passes `m` on.
- `mapClearCrossings(positions, lo, hi, m)` — `m.w` for the `room` guard and
  the `kept` separation filter, `m.clearance` for the crossing test.
- `mapLabelBox(street, p)` — reads `street.metrics.w`.
- `mapLabelHitsPlayer(street, p, player)` — reads `street.metrics.clearance`.

`mapPositionStreetLabels()` already has `street` in hand at both call sites, so
nothing new is threaded through it.

**d.** The `mapLabelClearance` comment's `"POPLAR ST"` caveat **dissolves and
must be rewritten**, not carried over. Under per-street widths the limit is
`MAP_SPACING - 2 * (MAP_LABEL_OFFSET + MAP_LABEL_CAP)` = 96, and the widest
north–south name is `"2ND ST"` at ~64.7 — clear by ~31 units, by construction
rather than by the coincidence that the one over-wide name happens to run
east–west. #113 calls this the strongest argument for the change; the comment
getting shorter and truer is part of the deliverable.

**This is a visible densification, not a refactor.** #113's sweep of 11,264
street-views predicts, for a street crossing the whole view:

- span 390 (step 3): **nine** streets go from 2 names to 3
- span 520 (step 4): **twelve** streets go from 2 to 3
- spans 650 and 780: no change

19% of street-views change label count and 439 more keep their count but move,
by up to a full block. Capture before/after screenshots at all four Wide spans
and report the counts; that comparison *is* the validation, since there is no
zero-diff proof to offer here.

**#37's table is invalidated by this.** #37 counts labels drawn outside the
viewBox per span, and this pass changes how many labels are placed. Note that in
the changelog and add a line to #37 saying its measurements need re-taking.

### 5 — #110: write down why the floor stays

**No code change.** `MIN_DISPLAY_MIN`'s comment gains the decision and the
evidence:

- the floor is deliberate, and the gap between printed and charged time is
  accepted rounding rather than an oversight;
- it became visible when #92 made grid travel's floor proportional — a 50 m
  half-move costs 0.694 min at Walk and 0.500 at Jog and prints `(0:01)`, so two
  half-moves through a mid-block display 2 minutes against ~1.39 spent at Walk;
- the three callers that can go sub-minute are the exit buttons via
  `exitMinutes()`, `estimateSleepMinutes()`, and `fmtDuration(room.fireMinutesLeft)`
  in `renderLocationPanel()`; every other caller is fed a constant of 5 minutes
  or more;
- the constant stays separate from `MIN_MOVE_MIN` for the reason already stated
  there — retuning the movement floor must not silently re-round Rest, Sleep,
  Search, fishing, craft times and the fire's fuel readout.

The comment must carry the *decision*, not a description of the bug. A reader
should close #110 from it rather than re-open the question.

### 6 — #131: make the dev helpers reachable

One statement immediately before the IIFE's closing `})();`:

```js
  // Dev seam. The four validators above are local bindings inside this IIFE, so
  // `validateReachability()` typed into devtools is a ReferenceError. This is the
  // one deliberate hole in the closure: read-only reporting helpers, nothing that
  // writes game state, and nothing else belongs on it.
  window.ashfallDev = { validateItemRegistry, validateLocations, validateRoomSchema, validateReachability };
```

And the four helpers' own comments change from *"Call manually from the browser
console when auditing"* to name the real call:
`ashfallDev.validateReachability()`, and so on. A comment that describes an
impossible action is the whole of what #131 is about, so leaving any of the four
unedited misses the point.

No game behaviour changes: nothing reads `window.ashfallDev`, and the four
helpers are unchanged inside.

## Design decisions to make during implementation

Narrow calls. Record whichever is picked in the changelog's Notes/assumptions.

1. **Whether the fencing comment on `window.ashfallDev` ships.** Tom chose
   "make them reachable"; the comment saying it is a read-only seam and nothing
   else may be added was the variant he did not pick. **Recommended: include
   it** — it costs one comment and is the only thing standing between a
   deliberate seam and the drawer every future helper gets hung on.
2. **`.state`'s exact styling.** `--ink-dim` is the recommendation — dimmer than
   the name, brighter than `.cat`. `--ink-faint` is the alternative and would
   make it read as a category-level aside rather than a property of the item.
3. **`.itemname`'s tap-target padding and `:active` treatment.** `6px 2px` with
   a matching negative margin, and an accent-coloured `:active`, are the
   recommendations. Anything that changes the row height is wrong.
4. **Whether `mapSetLabelWidth` keeps its name.** Recommended: rename to
   `mapLabelMetrics` — it no longer sets anything.
5. **Where `hereNote()` lives.** Recommended: beside `actionButton()` in
   RENDERING, which is the same kind of helper.

## Explicitly out of scope

- **#134 — stacks whose units carry durability.** A flashlight at 8% and one at
  100% still render identically after this pass. The `(Open)` suffix solves
  `sealed` and nothing else, by design.
- **#136 — `DOOR_LABELS` naming a door by its destination.** The sibling handoff
  adds a door that works around it; neither pass fixes it.
- **#78 — the accessibility pass.** No ARIA, no roles, no live region on `#log`,
  no dialog semantics or focus trapping on `#sideMenu`, no `inert`, no
  `prefers-reduced-motion` guard. #108 was carved out of #78 precisely so none
  of that is needed here, and #78 stays parked.
- **#29 — the log's 110px height and 50-entry cap.** Explicitly needs a play
  session first; nothing here touches `#log`'s sizing or `LOG_MAX_ENTRIES`.
- **#37 — labels drawn outside the viewBox.** Invalidated by item 4 and noted,
  not fixed.
- **#116 — tool wear.** #126 sets the precedent for what a spent tool does;
  it does not add durability to anything, and no tool or weapon starts spending
  it.
- **#133, #67, #123, #77, #135.** The sibling handoff's, or a later pass's.
- **#121, #111, #96, #15, #51.** Untouched.

## Sections touched

Not a content pass and not purely a mechanics one — the split is the point.

- **The document `<style>` block and `<body>` markup** — #108 items a, b and d.
  Neither is an ARCHITECTURE section.
- **CONFIG / CONSTANTS** — `MIN_DISPLAY_MIN`'s comment (#110), and the version
  string.
- **INVENTORY / ITEM SYSTEM** — `findFireStarter()` and `consumeMatchUse()`
  (#126). The only mechanics change in the pass.
- **RENDERING** — `renderItemList()` (#124, #108c), `renderHereActionsPanel()`
  (#126c), the new `hereNote()` helper.
- **RENDERING / MAP** — the label metrics and their four readers (#113).
- **PERSISTENCE** — the four validator comments (#131).
- **The IIFE's closing line** — `window.ashfallDev` (#131).

Nothing in WORLD DATA — no room, item, container, exit, description or pool
changes. Nothing in PLAYER STATE, WORLD INTERACTION, SURVIVAL / TIME SIMULATION,
STAMINA / FATIGUE, CRAFTING or EVENTS. `FIRE / COOKING` is read but not edited:
`doLightStove()` and `doBuildFire()` call `consumeMatchUse()` and are unchanged.

## UI changes

- An opened unit reads `Canned soup (Open) ×1 — 0.40 kg (Food)`; a sealed one is
  unchanged.
- Item names are real buttons with a larger tap target and press feedback.
- The smallest text in the game goes from 10.5px to 12px; `--ink-faint` and
  `--danger` are lighter; blocked buttons lose their `opacity:.45` and read
  distinctly louder.
- A log line when a fire-starter is spent, and a dim note where "Light the
  stove" or the campfire button used to be when nothing can light it.
- More street names on the Wide map at the two lower spans.
- The side-menu map heading is restructured; it should look identical.
- `ashfallDev.validateReachability()` works in the console.

## Dependencies / issue linkage

Fulfils **#124**, **#108**, **#110**, **#113**, **#126** and **#131** in full.
The pull request carries `Closes #124`, `Closes #108`, `Closes #110`,
`Closes #113`, `Closes #126`, `Closes #131`.

Expected to leave deferred: **nothing new**. Everything cut is already an open
issue — #134, #136, #78, #29, #37, #116 — and named above. #37 additionally
needs a note that its table was invalidated. If the pass surfaces something
else, file it and reference it in the pull request; if it surfaces nothing, say
so in the changelog's Documentation section.

## Open questions for Tom

**None.** Every design call this pass needed was settled in the planning
session: the `(Open)` suffix and that only the opened state is marked (#124),
nudging the tokens *and* raising the sizes (#108 item 2), keeping the display
floor and writing down why (#110), doing #113 knowing it is a visible
densification, consuming the fire-starter at zero *and* adding the dim note
(#126), and opening the closure for the four validators (#131).

## After implementation

Open a pull request carrying:

1. `ashfall.html` with `GAME_CONFIG.VERSION` bumped — **PATCH**, so
   `versionCompat()` does not move and `SAVE_KEY` stays `ashfall_save_v0.5`.
2. A new `CHANGELOG.md` entry at the top per `docs/CHANGELOG_GUIDE.md`, with
   `Implements: handoffs/presentation-and-signal-pass.md`. It must record: that
   #126's rule is the precedent for #116; the before/after contrast table and
   that the colour values are retunable; the before/after label counts per Wide
   span; that #37's measurements are invalidated; that #124's durability half is
   #134's; and the `qty > 1` caveat on the fire-starter splice.
3. `Closes #124`, `Closes #108`, `Closes #110`, `Closes #113`, `Closes #126`,
   `Closes #131` in the description.
4. This file moved: `git mv handoffs/presentation-and-signal-pass.md
   handoffs/archive/presentation-and-signal-pass.md`.
5. New issues for anything deferred, or a line saying nothing was.

After the merge, tag it — `git tag vX.Y.Z <commit>`, naming the commit
explicitly, then verify with
`git show vX.Y.Z:ashfall.html | grep VERSION`.

**Validation to perform**, beyond the syntax check:

- `git diff origin/main...HEAD -- ashfall.html` — confined to the sections named
  above, with nothing in WORLD DATA.
- **#126** in a browser: light the stove until the matchbox is spent; confirm
  the item leaves the inventory, the log line appears, and the note replaces the
  button. Confirm the note does **not** appear where a fire is impossible for a
  different reason — no campfire kit and no firewood.
- **#124**: open one can from a stack of three; confirm the row reads
  `(Open)` on the opened unit and nothing on the other two, and that the
  detail box still reads Sealed/Opened.
- **#108**: the restructured map heading renders identically (screenshot);
  the item-name button has the same row height and opens the detail view; the
  map draws with no flash on first open of the side menu; the contrast figures
  above re-measured against the shipped stylesheet.
- **#113**: before/after label counts for all sixteen streets at each of the
  four Wide spans, against #113's prediction of nine streets at span 390 and
  twelve at span 520. Pan the map and confirm no name overlaps another, the
  player marker, or a crossing.
- **#131**: `ashfallDev.validateReachability()` in a real devtools console on
  the shipped file — no temporary copy. All four helpers report, and the three
  pre-existing ones report clean.
- **Save compatibility**: a v0.5.x save still loads and reports "Progress loaded
  from this browser." with no version-mismatch warning.
