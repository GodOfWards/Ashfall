# Ashfall Handoff — Log: Remove Routine Lines, Collapse Repeated Ones

Current shipped version: v0.4.3
Implied version-change type: PATCH
Issues: #21 — Routine inventory actions shouldn't each write a log line
        #22 — Collapse repeated action log lines instead of printing every one

## What this is

Two complementary changes to the action log. **#21** deletes the log lines that
only confirm something the player can already see in a panel. **#22** collapses
consecutive runs of the same action into a single line, so fishing a hundred
times reports once.

They ship together because they constrain each other: what #21 removes, #22
never has to collapse, and what #21 keeps determines which collapse keys need to
be object-aware.

## Relevant existing state

Verified against the current `ashfall.html`.

- `log(text, cls)` (`ashfall.html:3426`) appends a `<p>` to `#log`, strips
  `.fresh` from every existing line, adds `.fresh` to the new one **only when
  `cls` is falsy**, trims to the newest 50 children, and scrolls to the bottom.
- `#log` is `display:flex; flex-direction:column; gap:5px; max-height:110px;
  overflow-y:auto` (`ashfall.html:63`). Line classes are `sys`, `warn`, `good`
  and `fresh` (`ashfall.html:64-68`).
- The log is **DOM-only**. Nothing about it lives in `state`, and
  `serializeGame()` (`ashfall.html:4165`) never touches it. `doRestart()` clears
  it with `innerHTML = ""`.
- `#statsBox` — the only display of Hunger/Thirst/Energy/Stamina/Health — sits
  inside `<aside id="sideMenu">` (`ashfall.html:126`), the off-canvas panel
  opened with the ☰ button. **Vitals are invisible during normal play.**
- `REST_DURATION_MIN = 60`, so each Rest is exactly one game hour.
- `doMove()` (`ashfall.html:3752`) logs nothing at all.
- `doSearch()` sets `room.searched = true`, so a given room can never be
  searched twice.

### The test this pass applies

**Does the line tell the player something the screen doesn't already show?**
If not, it is routine and goes. If it is the only channel for that information,
it stays.

## Rules / mechanics

### Part 1 — Lines to remove (#21)

Delete these `log()` calls outright:

| Call site | Line | Message | Why routine |
|---|---|---|---|
| `doTake()` | 3584 | "You take the …" | item visibly moves between the Here and Inventory panels |
| `doStore()` | 3603 | "You place/store the …" | same, in reverse |
| `doEquip()` | 3630 | "You put on the …" | a new inventory tab appears |
| `doUnequip()` | 3642 | "You take off the … and stow it away." | the tab disappears |
| battery on/off | 3683 | "You switch on/off the …" | the detail view already reads "— On" / "— Off" |
| remove batteries | 3690 | "You pull the batteries out of the …" | the battery item appears in inventory and the detail view reads "No batteries installed" |
| replace batteries | 3698 | "You put fresh batteries in the …" | the detail view's charge readout jumps to 100% |

The last two (3690, 3698) are **an extension of #21's original table by two call
sites**, added here because they fail the same test and leaving them would make
the battery controls inconsistent — silent when toggled, chatty when serviced.
Record this explicitly in the changelog rather than letting it pass unremarked.

**`doConsume()` (line 3615) stays.** Eating is the one case where the panels
don't tell the whole story: the item count drops visibly, but the actual effect
is on Hunger/Thirst, which live behind the ☰ menu. With the menu closed — the
normal state of play — this line is the only acknowledgement that anything
happened.

Everything else stays, including every `warn`, every failure and redirect
("That won't fit", "No room for the … — it drops to the floor instead", "Your
keychain can't hold that", "You're already carrying something in that slot"),
and every consequence line with no visible counterpart ("It doesn't sit right.
You can feel it already.", "Your flashlight runs out of battery and shuts off.").

### Part 2 — Collapsing repeated lines (#22)

**Rule: collapse consecutive runs only.** Given
`fish, fish, chop, eat, eat, drink, fish, eat` the log shows
`fish, chop, eat, drink, fish, eat`. A run is broken by **any** intervening
line, including a `warn` — so eating three times where the second triggers the
illness warning produces eat / illness / eat, not a run of three. That is
correct and is a stated rule, not an accident.

`log()` gains an optional third parameter:

```
log(text, cls, key)
```

- **No `key`** → append as today. The line never collapses, and nothing
  collapses into it. Every unkeyed call site keeps its current behavior exactly.
- **With a `key`** → if `#log`'s last child carries `dataset.logKey === key`,
  collapse into that element; otherwise append a new element carrying
  `dataset.logKey = key`.

Collapse state lives on the element (`dataset`), never in `state`.

#### Family A — tally actions (fixed text, prose summary)

| Action | Line | Key | Outcome ids |
|---|---|---|---|
| `doFish()` | 4053 / 4055 | `fish` | `bite` / `miss` |
| `doRest()` | 3779 | `rest` | `rest` |
| `doChopTree()` | 4154 | `chop` | `chop` |
| `doAddFuel()` | 4104 | `fuel` | `fuel` |

The element accumulates a per-outcome tally. The **first** occurrence renders
its ordinary sentence unchanged. From the **second** onward the line is
rewritten as a summary:

- **fish** — `n` attempts, `b` bites:
  - `b === 0` → `You fish {n} times. Nothing bites.`
  - `b === 1` → `You fish {n} times. One bite.`
  - `b > 1` → `You fish {n} times. {B} bites.`
- **rest** — `You rest for {n} hours.` (each Rest is exactly one hour, and a
  collapsed run is always ≥ 2, so this is always plural)
- **chop** — `You chop down {n} trees.`
- **fuel** — `You feed {n} more pieces of wood into the fire.`

`doChopTree()` sets `room.hasTree = false`, so chopping cannot repeat in place —
but `doMove()` logs nothing, so chopping in three rooms in a row still produces
a run of three. **Runs may span movement.** This is intended.

**Number words:** spell out two through ten; use digits from eleven up.
`{B}` is the same word capitalised for sentence-initial position.

**Class handling:** on the first collapse, clear any outcome class from the
element — a fish run mixes a `good` "bite" with an unclassed "miss", and the
summary is a neutral report, so it renders unclassed.

#### Family B — counted actions (text names an object)

These interpolate an item or recipe into the message, so the key **must**
include that object or the summary will lie — eating three different things must
never render as one line naming the first.

| Action | Line | Key |
|---|---|---|
| `doConsume()` | 3615 | `consume:` + `it.itemId` |
| `doCraft()` | 4042 | `craft:` + `recipe.output.id` |
| `doCookInContainer()` | 4144 | `cook:` + `recipe.id` |

The sentence is left exactly as written and a dim count is appended:

```
You eat the canned soup. ×3
```

Implemented as a trailing `<span class="logcount">`, with

```css
.logcount{ color:var(--ink-faint); font-size:11.5px; margin-left:5px; }
```

so the count reads as functional UI rather than as part of the prose. The
element keeps its original class (`doConsume` logs `good`).

`doSearch()` is deliberately **not** keyed: a room can only be searched once and
different rooms would key differently, so it could never collapse.

#### Family C — everything else

No key, no collapsing. This includes **every `warn` line**: a run of ten "That
won't fit" failures is worth seeing in full, and suppressing repeated failures
would hide a stuck player from themselves.

#### `.fresh` on a collapsed line

`log()`'s existing rule is: strip `.fresh` from all lines, then add it to the
new one when `cls` is falsy. A collapsed line follows the same rule — strip from
all, then re-apply to the rewritten element under the same condition — so the
most recent line stays highlighted whether it was appended or rewritten.

The 50-entry cap and the scroll-to-bottom behavior are unchanged.

## Design decisions to make during implementation

1. **Where the summary text lives.** *Recommended:* a small table keyed by
   action id, next to the `log()` implementation, mapping a tally object to a
   string — rather than building sentences at the four call sites. It keeps all
   four strings in one place for a future content pass to edit.
2. **How a call site passes its outcome id.** *Recommended:* a fourth optional
   parameter, defaulting to the key itself, so the three single-outcome actions
   pass nothing extra and only `doFish()` names an outcome.
3. **Number-word helper placement** — UTILITIES, beside `fmtDuration()`.
4. **Whether the first line of a tally run stores its tally immediately** or
   only starts tallying on the second occurrence. *Recommended:* tally from the
   first, so the transition at n=2 is a re-render rather than a reconstruction.

## Data / schema changes

**None.** No PLAYER STATE fields, no item schema, no world data. The log and all
collapse bookkeeping are DOM-only and are not serialized, so `versionCompat()`
stays `"0.4"`, `SAVE_KEY` is unchanged, and every v0.4.x browser save keeps
loading.

One CSS class is added (`.logcount`). `log()`'s signature gains two optional
trailing parameters; every existing unkeyed call site is unaffected.

## In scope

- Delete the seven routine `log()` calls listed in Part 1.
- Extend `log()` with an optional collapse key and outcome id.
- Collapse consecutive same-key runs, with prose summaries for the four tally
  actions and a dim `×N` for the three counted actions.
- Add the `.logcount` style.

## Explicitly out of scope

- **Resizing or restyling `#log`.** Raised in #21 — the 110px cap and 50-entry
  limit were sized for a busier feed and may want revisiting once the noise is
  gone, but that should be judged against the quieter log in play, not guessed
  at now. File it as a follow-up issue at wrap-time if it reads wrong.
- **Surfacing vitals outside the ☰ menu.** The reason `doConsume()` survives is
  that Hunger/Thirst are hidden during play; that is a real finding, and it is
  recorded in **#23** (illness system), which is deliberately not being
  addressed. Do not add a vitals readout here.
- **Any change to illness, vitals, or `doConsume()`'s mechanics.** Only its log
  call's key is touched.
- **Summarising across non-consecutive occurrences.** Rejected during planning:
  it deletes the events between survivors and implies an order that didn't
  happen.
- Collapsing `warn` lines.

## Sections touched

- **EVENTS / UI HELPERS** — `log()` and its new collapse logic.
- **INVENTORY / ITEM SYSTEM** — removal of five log calls in `doTake`,
  `doStore`, `doEquip`, `doUnequip` and the battery actions in
  `getItemActions()`; one key added in `doConsume`.
- **FIRE / COOKING** — keys added in `doFish`, `doAddFuel`, `doChopTree`,
  `doCookInContainer`.
- **CRAFTING** — key added in `doCraft`.
- **WORLD INTERACTION** — key added in `doRest`.
- The document `<style>` block for `.logcount`.

This is rendering behavior — how existing state changes are surfaced — not
content and not a new mechanic. No ACTIONS logic, no simulation rule and no
vitals math changes; the only edits inside those functions are to their `log()`
calls.

## UI changes

- Taking, storing, equipping, unequipping and servicing batteries become
  silent. Their failure warnings still appear.
- Eating and drinking still report.
- Repeating an action collapses to one line: `You fish seven times. Three
  bites.` / `You rest for three hours.` / `You chop down three trees.` /
  `You eat the canned soup. ×3`.
- Failures never collapse.

## Dependencies / issue linkage

Fulfils #21 and #22 together. Independent of #18 (exits) and #19/#20 (map).
Surfaced but deliberately not addressed: **#23** (illness system) and the
log-sizing follow-up noted above.

## Open questions for Tom

None. The collapse rule, the keying scheme, the seven removals, the retention of
`doConsume()`, and the four summary strings are all settled. The two
battery-servicing removals are flagged in Part 1 as an explicit extension of
#21's original table.

## After implementation

Open a pull request carrying the `GAME_CONFIG.VERSION` PATCH bump and a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, referencing this handoff by
path (`handoffs/log-noise-and-collapse.md`), recording the four "Design
decisions" resolutions **and the two-call-site extension to #21's table** in its
Notes/assumptions section, and closing both issues with `Closes #21` and
`Closes #22`.

Validation worth citing in the entry: a driven session showing a fishing run of
mixed outcomes collapsing to one correctly-tallied line; a run broken by an
intervening warning producing two lines; eating two different items producing
two lines rather than one; taking and equipping producing no lines while their
failure warnings still do; and `.fresh` landing on the most recent line whether
appended or rewritten.
