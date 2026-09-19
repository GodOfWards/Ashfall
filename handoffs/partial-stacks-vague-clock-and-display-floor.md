# Ashfall Handoff — Partial stacks, a vague clock, and a display floor of its own

Current shipped version: v0.4.12
Implied version-change type: PATCH
Issues: #81 — Moving part of a stack takes one click per unit; #59 — Without a
watch, show the approximate time of day instead of nothing; #75 — MIN_MOVE_MIN
flattens the gait ladder at the map's actual scale

## What this is

Three independent `tier-1` items that each give an existing system a surface it
is missing, bundled into one pass the way `handoffs/reproduced-defect-sweep.md`
bundled five defects. None of the three adds a mechanic, adds content, or adds
persistent state.

- **#81** — `doTake()`/`doStore()` already accept any quantity and already
  validate it. The UI offers two: the whole stack, or one. Moving 7 of 12 means
  clicking "Take 1" seven times. Per the issue: *"a live mechanic with no
  surface."*
- **#59** — no watch means `#clockLabel` renders the empty string and the player
  is told nothing at all about when it is. Per the issue: *"A person without a
  wristwatch still knows whether it is morning or getting dark; what they lose
  is precision, not all sense of time."*
- **#75** — `MIN_MOVE_MIN` is a movement rule that `fmtDuration()` also applies
  to Rest, Sleep, Search, fishing, every craft recipe and the fire's fuel
  readout. Per the issue: *"one constant serves both purposes."*

## Relevant existing state

Verified against `ashfall.html` at v0.4.12 by reading the file and by loading it
into a Node harness and enumerating the world. Line numbers are v0.4.12.

**Quantity transfer (#81)**

- `normalizeQty(requested, available)` (`:3784`) floors the request, rejects
  anything below 1 or above the stack, returns `null` on garbage.
- `doTake(index, qty)` (`:3791`) and `doStore(index, qty)` (`:3810`) both take
  `qty`, both check destination capacity before mutating the source, both
  re-render. The INVENTORY/ITEM SYSTEM section header (`:3772`) documents these
  guarantees as deliberate. **None of these three functions needs any change.**
- `getItemActions()` (`:3876`) is the only place the two quantities are offered.
  Its stackable gate is `STACKABLE.has(it.category) && it.qty>1 && !it.durability`,
  and the world-side buttons carry
  `disabled: state.invTab==="keychain" && !keychainAllows(it)`.
- The inventory-side label already switches on destination:
  `state.worldTab==="floor" ? "Place" : "Store"`.
- `STACKABLE` is `Food / Medical / Ammunition / Materials`. **59 of 154 registry
  items** are eligible (22 Food, 12 Medical, 25 Materials, 0 Ammunition — the
  empty category is #70's, not this pass's).
- Stacks accumulate: `addToList()` merges by `itemId`. Individual placements top
  out at 5, but `firewood` alone has 4 on the riverbank floor, 5 in the alley
  dumpster, 3 in the 1A patio bin, 6 per `doChopTree()` and 3 per campfire-kit
  disassembly — and `FIRE_BUILD_WOOD` is 3, so firewood is the item where
  partial transfer actually bites.
- **`button.mini.step` (`:105`) is CSS that nothing applies.** `git log -S` over
  every commit in the repository finds no revision in which any JS ever set that
  class; it has been dead since it arrived in v0.4.0. It is `.mini`, so it was
  sized for the inline list rows.

**Clock (#59)**

- `renderLocationPanel()` (`:5389`) is the whole of it:
  `document.getElementById("clockLabel").textContent = hasWatch() ? getClockText() : "";`
- `hasWatch()` (`:3766`) has **exactly one consumer**, that line. `isWatch` is on
  **exactly one item**, `wristwatch` (`:459`). Confirmed by grep at v0.4.12.
- `DAY_START_MIN` (`:3955`) and `getClockText()` (`:3956`) live in **WORLD
  INTERACTION**, not CORE UTILITIES — #59's scope note says CORE UTILITIES and is
  wrong about that. Don't go hunting, and don't move them.
- `getClockText()` already derives both halves of what a vague reading needs:
  `day` from `Math.floor(abs/1440)` and `tod` from `((abs%1440)+1440)%1440`.
- `render()`'s game-over branch (`:5597`) separately blanks `#clockLabel`.
- **`shelter` is not the flag this wants.** v0.4.12 shipped `shelter:
  "none"|"full"` on all 218 rooms, and it is still unread. It is tempting to
  read it as the `outdoor` flag #59 says is missing — do not. `shelter` means
  *under cover*, and your own living room is `"full"` while having windows and
  blinds; gating the reading on it would say you cannot tell morning from night
  in your own apartment. The see-outside refinement stays out of scope, exactly
  as #59 says.

**Duration floor (#75)**

- `MIN_MOVE_MIN = 1` (`:263`) has exactly two readers: `fmtDuration()` (`:3564`)
  and `moveMinutes()` (`:3572`). Confirmed by grep.
- `GAITS` (`:264`) — sneak 0.6, walk 1.2, fast 2.0 m/s.
- Across all 774 exits, grid travel has **exactly two distances, 50 m and 100 m**
  (448 and 224 exits). Three of the six gait×distance cells clamp: walk@50,
  fast@50, fast@100. #75's table reproduces exactly at v0.4.12.
- **`fmtDuration()`'s own clamp can never bind on a movement label.**
  `moveMinutes()` already floors at `MIN_MOVE_MIN`, so the minimum `exitMinutes()`
  across every exit × every gait is exactly 1. Verified by enumeration.
- Of `fmtDuration()`'s 13 call sites, eleven pass a named constant ≥ 5
  (`REST_DURATION_MIN` 60, `searchMinutes` 20/25, `FISH_DURATION_MIN` 20,
  `LIGHT_STOVE_MIN` 5, `BUILD_FIRE_MIN` 10, `DISMANTLE_CAMPFIRE_MIN` 10,
  `CHOP_TREE_MIN` 30, `recipe.minutes` 5/15) or a movement time. **Only two can
  ever pass a value below 1**: `room.fireMinutesLeft` (`:5385`, burns down
  continuously) and `estimateSleepMinutes()` (`:5467`, when Energy sits just
  under the ceiling).
- 22 exits are building entrances whose two Locations sit at identical
  coordinates, so `locationDistance()` returns 0 and `MIN_MOVE_MIN` is the only
  thing stopping them costing zero minutes. They are non-grid exits. **The floor
  on movement is load-bearing and stays.**

## Rules / mechanics

### 1. Split the duration floor from the movement floor (#75)

Add a second constant beside `MIN_MOVE_MIN` in CONFIG / CONSTANTS:

```js
const MIN_MOVE_MIN = 1;
const MIN_DISPLAY_MIN = 1;
```

`fmtDuration()` reads `MIN_DISPLAY_MIN`. `moveMinutes()` keeps `MIN_MOVE_MIN`.
Nothing else changes.

**The two values are deliberately equal, so this changes no pixel.** That is the
point: the diff is provably inert, and `git diff origin/main...HEAD --
ashfall.html` is the proof. What it buys is that retuning the movement floor —
which #92 may well do — no longer silently re-rounds every duration label in the
game.

`MIN_MOVE_MIN` also gains a comment recording the decision this pass settles:
**pace is a journey-scale choice, not a per-block one.** Jog buying 28% over
Walk on a full block rather than the 67% its speed implies is the intended
behaviour, not a defect. Write the rule; do not write an issue number (see
Design decisions).

Do **not** change any gait speed, do not lower either floor, and do not touch
`moveMinutes()`' arithmetic.

### 2. A vague clock without a watch (#59)

**Name the day length.** `1440` appears twice in `getClockText()` today and would
appear three or four times after the split below. Add `MINUTES_PER_DAY = 1440`
to CONFIG / CONSTANTS and use it at every occurrence.

**Split the derivation, so there is one of it.** Beside `DAY_START_MIN` in WORLD
INTERACTION:

```js
function absoluteMinute(){ return Math.round(DAY_START_MIN + state.totalMinutes); }
function dayNumber(){ return 1 + Math.floor(absoluteMinute()/MINUTES_PER_DAY); }
function minutesIntoDay(){ const a = absoluteMinute(); return ((a % MINUTES_PER_DAY) + MINUTES_PER_DAY) % MINUTES_PER_DAY; }
```

`getClockText()` is rewritten to compose from these three and must produce a
byte-identical string to today's for every input — `"Day 3, 14:22"`. This is the
"one function for it, not two" point #59 raises against #60, which also wants
the day number.

**The band table.** A named table beside the helpers above, and the single place
in the game that says what part of the day a minute falls in:

```js
const TIME_OF_DAY_BANDS = [
  { from: 0,     label:"late night" },
  { from: 5*60,  label:"dawn" },
  { from: 7*60,  label:"morning" },
  { from: 12*60, label:"midday" },
  { from: 14*60, label:"afternoon" },
  { from: 18*60, label:"evening" },
  { from: 21*60, label:"night" }
];
```

Invariants, which the comment must state: entries are sorted ascending by
`from`, the first is `from: 0`, and a band runs until the next one's `from`.

```js
function timeOfDayBand(){
  const tod = minutesIntoDay();
  return TIME_OF_DAY_BANDS.filter(b => tod >= b.from).pop().label;
}
function getVagueClockText(){ return "Day " + dayNumber() + ", " + timeOfDayBand(); }
```

The boundaries are **a judgment call with no prior convention and are
retunable** — say so in the comment and in the changelog. They are chosen to be
plausible as *light* boundaries, because the weather layer's light/darkness pass
is meant to read this table rather than pick its own; two opinions about when
evening starts is precisely the duplicated fact this table exists to prevent.
That reason goes in the comment because a table whose every key is present
cannot show it.

**The render.** `renderLocationPanel()` (`:5389`) becomes:

```js
document.getElementById("clockLabel").textContent = hasWatch() ? getClockText() : getVagueClockText();
```

Labels are lowercase so they compose as `"Day 3, evening"`, matching the watch
form's `"Day 3, 14:22"`. Per the Project Guide, this is functional UI text held
to clarity, not to the prose tone — plain band words, no atmosphere.

**Settled, from the issue and not to be revisited:** the day number shows with or
without a watch; the reading is never randomised or made unreliable; it does not
depend on being able to see outside.

**The watch stays worth carrying.** Bands are 2–5 hours wide. Precise time is
what lets a player plan against `room.fireMinutesLeft` and
`estimateSleepMinutes()`, both of which print minutes. Confirm this holds when
you see it on screen; a watch reduced to decoration would be a regression.

The game-over branch at `:5597` keeps blanking `#clockLabel`. Do not route it
through either function.

### 3. Fixed-quantity transfer buttons (#81)

In `getItemActions()` only. **`doTake()`, `doStore()` and `normalizeQty()` are
not touched.**

World side, in this order:

| button | quantity | shown when |
|---|---|---|
| `Take All` | whole stack — `doTake(index)` | always |
| `Take Half` | `doTake(index, Math.ceil(it.qty/2))` | stackable gate **and** `it.qty >= 3` |
| `Take 1` | `doTake(index, 1)` | stackable gate **and** `it.qty > 1` |

Inventory side mirrors it exactly, with the existing destination-dependent label:
`Place All`/`Store All`, `Place Half`/`Store Half`, `Place 1`/`Store 1`, calling
`doStore(index)`, `doStore(index, Math.ceil(it.qty/2))`, `doStore(index, 1)`.

"Take" is renamed to "Take All" (and "Place"/"Store" likewise) because "Take"
beside "Take Half" no longer says which it is.

The stackable gate is the existing one and is not re-invented:
`STACKABLE.has(it.category) && !it.durability`.

**Half rounds up**: `Math.ceil(it.qty/2)`. Half of 7 takes 4 and leaves 3.
Retunable, and to be recorded as a choice.

**The `qty >= 3` gate on Half is a rule, not a magic number**: at qty 2, half is
1 and the button would duplicate "Take 1". Write it inline with a comment saying
that, rather than as a constant — a named constant here would only restate the
digit. Flag it as a judgment call.

The keychain `disabled` predicate currently on Take and Take 1 must apply to
**Take Half** as well, unchanged:
`state.invTab==="keychain" && !keychainAllows(it)`.

**Expected detail-view behaviour after a partial take, which is correct and must
not be "fixed":** `doTake()` decrements the source stack in place and only
splices at zero, so the source keeps its `_uid` and `renderCraftPanel()`
re-resolves to it — the detail view stays open on the shrinking stack, which is
what makes repeated halving usable. `Take All` splices the stack, `findItemByUid()`
returns null, and the panel falls back to the recipe list. That is today's
behaviour for "Take" and is unchanged.

**Delete the dead `button.mini.step` rule at `:105`.** This pass settles that the
picker is a button set in the detail view, so nothing will ever apply a `.step`
class to a `.mini` button. Removing it is in scope precisely so it does not sit
there implying a control that was decided against.

The inline list rows in `renderItemList()` are **unchanged** — one whole-stack
button each, still labelled "Take"/"Place"/"Store" (see Design decisions).

## Design decisions to make during implementation

Each must be recorded in the changelog's Notes/assumptions or Documentation
section rather than chosen silently.

1. **The band boundaries themselves.** The table above is the recommended
   default. They are a first guess with nothing behind them; if any boundary
   reads wrong on screen, move it and say so. Do not change the *number* of
   bands — seven is what #59 specifies.
2. **Whether the comments name issue numbers.** Recommended: **no.** The Project
   Guide is explicit that a comment naming a roadmap item number is a reference
   that goes stale on its own schedule. Both the band table and `MIN_MOVE_MIN`
   want to explain *why* they are shaped as they are, and the durable form of
   that reason is the rule ("a later light/darkness layer reads these bands"),
   not the ticket. Note that v0.4.12's `shelter` comment does cite issue
   numbers — this handoff is deliberately not following that precedent, and the
   changelog should say which way it went.
3. **Whether the inline row button is renamed too.** Recommended: **leave it as
   "Take"/"Place"/"Store".** It is the only button in the row, so "All" is
   redundant where there is no alternative to distinguish it from. If it reads
   inconsistently beside the detail view once built, rename it and say so.
4. **`Math.ceil` vs `Math.floor` for Half.** Recommended `ceil`, as specified —
   it keeps the `qty >= 3` gate at 3 rather than 4, and halving converges
   downward without stranding a 1. Either is defensible.
5. **Where `MINUTES_PER_DAY` and `MIN_DISPLAY_MIN` sit.** Recommended: CONFIG /
   CONSTANTS with the other top-level constants. `MINUTES_PER_DAY` beside
   `DAY_START_MIN` in WORLD INTERACTION is also reasonable if it reads better
   there; pick one and be consistent.

## Data / schema changes

**None.** No new or changed PLAYER STATE field, no ITEM DATA SCHEMA change, no
ROOM/CONTAINER/EXIT schema change, no `ITEM_REGISTRY` edit. `SAVE_KEY` does not
rotate and no backfill is added — existing browser saves keep loading.

This is what makes the pass a PATCH under the tier mapping, and it is not
tentative: none of the three options left open above crosses into persistent
state.

## In scope

- [ ] `MIN_DISPLAY_MIN` added; `fmtDuration()` reads it; `moveMinutes()` keeps
      `MIN_MOVE_MIN`; the journey-scale-pace decision recorded as a comment.
- [ ] `MINUTES_PER_DAY` added and used at every occurrence of `1440`.
- [ ] `absoluteMinute()` / `dayNumber()` / `minutesIntoDay()` extracted;
      `getClockText()` composed from them, output byte-identical.
- [ ] `TIME_OF_DAY_BANDS` table, `timeOfDayBand()`, `getVagueClockText()`.
- [ ] `renderLocationPanel()` shows the vague reading instead of `""`.
- [ ] `Take All` / `Take Half` / `Take 1` and the Place/Store mirror in
      `getItemActions()`, with the keychain gate on all three.
- [ ] The dead `button.mini.step` CSS rule deleted.
- [ ] `GAME_CONFIG.VERSION` bumped (PATCH), changelog entry, `Closes` lines.

## Explicitly out of scope

- **#92** — that a mid-block stop costs more than the block it sits inside (2×50 m
  is 2.00 min against 1.39 at Walk and 1.00 at Jog, but exactly equal at Sneak).
  Filed from this session's verification of #75. It is the same constant seen
  from the route side and is a real balance change; #75's pace question is
  settled here, that one is not. **Do not fix it in this pass.**
- **#75's options 2, 3 and 4** — lowering or removing the movement floor,
  retuning gait speeds, rescaling the grid. Option 1 only.
- **Sub-minute duration display.** Follows from dropping the floor, which is not
  happening. `MIN_DISPLAY_MIN` is 1 and the two sub-minute readouts
  (`"Sleep (0:01)"`, `"roughly 0:01 of fuel left"`) keep reading exactly as they
  do today.
- **Any arbitrary quantity.** "7 of 12" remains inexpressible; All / Half / 1 is
  the settled shape. No stepper, no free-text field, no prompt. #47 (fluid
  transfer) will need more than this if it ever lands, and that is #47's problem.
- **The inline list rows.** No new control there.
- **#58 (weather).** This pass lays the band table down as its seam and reads it
  for one label. It adds no light model, no darkness, no temperature.
- **Reading `shelter`.** See Relevant existing state. It stays unread by this
  pass; the see-outside refinement needs a flag that does not exist yet.
- **#70** (the empty `Ammunition` STACKABLE category, the unread tags), **#49**
  (`#rightBar` crowding, which #59 flags as wanting a single look if both land),
  **#60** (playthrough stats, which will reuse `dayNumber()`), **#81's** parent
  **#47**. None is a prerequisite and none is touched.

## Sections touched

- **CONFIG / CONSTANTS** — `MIN_DISPLAY_MIN`, `MINUTES_PER_DAY`, the comment on
  `MIN_MOVE_MIN`.
- **CORE UTILITIES** — `fmtDuration()`.
- **WORLD INTERACTION** — `DAY_START_MIN` neighbourhood: the three time helpers,
  `TIME_OF_DAY_BANDS`, `timeOfDayBand()`, `getVagueClockText()`, `getClockText()`.
- **INVENTORY / ITEM SYSTEM — item-detail action list** — `getItemActions()`.
- **RENDERING** — `renderLocationPanel()`.
- The `<style>` block — one deleted rule.

Per the Project Guide's content-vs-mechanics rule: **this is neither a content
pass nor a mechanics pass.** All three items are new surfaces onto state and
behaviour that already exist — a quantity the transfer functions already accept,
a time the clock already derives, a floor already being applied. WORLD DATA is
untouched; no rule in ACTIONS or SIMULATION changes.

## UI changes

- **`#clockLabel` is never empty during play.** Without a watch it reads
  `"Day 3, evening"` where it previously read nothing. With a watch it is
  unchanged. Blank on game over, unchanged.
- **The item detail view gains one button** for a stackable of 3 or more:
  `Take All` / `Take Half` / `Take 1`, or the Place/Store mirror. "Take" and
  "Place"/"Store" are renamed to "…All". A stack of 1 shows one button, as now;
  a stack of 2 shows two, as now.
- **No other visible change.** The `MIN_DISPLAY_MIN` split is deliberately
  invisible, and every duration label in the game — movement costs, Rest, Sleep,
  Search, fishing, craft times, the fire's fuel readout — must read exactly as it
  did at v0.4.12.

## Dependencies / issue linkage

Fulfils **#81**, **#59** and **#75** — the pull request carries `Closes #81`,
`Closes #59`, `Closes #75`.

Unblocks nothing that is currently blocked. The band table is deliberately laid
down ahead of **#58**'s light layer, and `dayNumber()` ahead of **#60**.

**Expected to leave deferred:** nothing beyond what is already filed. #92 was
filed during this planning session and covers the one finding this pass declines.
If the implementation turns up anything further, file it at wrap-time and
reference it in the pull request; if it turns up nothing, say so in the
changelog's Documentation section, per the wrap-time checklist.

## Open questions for Tom

None. The three decisions that needed him — whether the pace selector is meant
to bite at block scale (no; #75 reduces to the constant split with the intent
named), what form the quantity control takes (fixed All/Half/1 buttons, no
stepper), and whether these ship together (yes, one pass) — were answered during
this session and are written into the spec above.

## After implementation

Open one pull request carrying the `GAME_CONFIG.VERSION` bump (PATCH) and a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, naming this handoff by path
and recording every "Design decisions" resolution above. Close all three issues
from the pull request body with `Closes #81`, `Closes #59`, `Closes #75`.

Prove the "no other visible change" claim rather than asserting it:
`git diff origin/main...HEAD -- ashfall.html` is the evidence that the
`MIN_DISPLAY_MIN` split touched the constant and its two readers and nothing
else. Tag the merge commit per the wrap-time checklist, naming the commit
explicitly.
