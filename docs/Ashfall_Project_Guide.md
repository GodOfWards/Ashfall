# Ashfall — Project Guide

## Purpose

This document is the third leg of the handoff set, alongside
`CHANGELOG.md` (what has changed) and the GitHub issue backlog (what's
next). Where those two are about *state*, this one is about *judgment* —
the tone, spirit, and conventions that should hold steady across every
future content pass, mechanics pass, and AI-assisted session, even as
individual features come and go. It's also the one document that
describes how a session, `CHANGELOG.md`, the backlog, and
`Ashfall_Handoff_Guide.md` all fit together (see Part 3, Workflow) — the
other guides link back here rather than each explaining it themselves.

Read this once per new session, before making changes. It changes rarely;
the changelog and the backlog change constantly.

---

## Part 1 — The Spirit of the Game

Ashfall is a quiet-apocalypse survival game. The collapse has already
happened — the player wakes up into its aftermath, not its beginning.
There is no framing cutscene explaining what happened; the world explains
itself through what people left behind.

### Tone

Pulled directly from the existing writing (room/item descriptions), not
invented for this doc:

- **Understatement over drama.** "The fridge hums no more, and something
  inside it has clearly given up." Not: "The rotting stench of decay
  fills the kitchen." The horror is in the mundane detail, not in
  adjectives.
- **Second person, present tense, plain sentences.** No purple prose, no
  narrator voice commenting on events. The player observes; the text
  doesn't editorialize.
- **Absence as storytelling.** A half-packed bag by the door. A calendar
  turned to two months ago. A suitcase abandoned mid-pack. The story of
  what happened to a place is told through what its occupants didn't
  finish doing, never through exposition.
- **Ordinary domestic detail is the texture of the world.** Coffee
  grounds, a step stool sized for a kid, a hand-painted sign. The world
  should feel like a real, specific small town that stopped rather than
  a generic "apocalypse backdrop."
- **Comparisons to the player's own space, when relevant.** Neighboring
  units are described relative to the player's own ("Same layout as
  yours, messier" / "The bed's made, unlike yours") — this reinforces
  that the player has a specific, situated life, not just a spawn point.

### Writing checklist for new descriptions

When writing a new room, item, or event description:
- Would this read the same if a person, not a game, wrote it about a real
  place they walked into? If it sounds like copy, rewrite it.
- Does it show rather than state? Prefer a concrete object or detail over
  a mood word ("dusty," "eerie," "abandoned").
- Is it short? Existing descriptions run one to three sentences. Longer
  than that risks becoming exposition.
- Does it avoid explaining the collapse itself? The player already knows
  something happened. Let individual places imply their own small piece
  of it; don't have any one description try to explain the whole event.

This applies to descriptive text specifically. Functional UI text (button
labels, movement/exit labels, status readouts) is held to clarity, not to
this tone — a movement label like "Head east toward Main St" is correct
as plain orientation text, not a missed opportunity for atmosphere.

---

## Part 2 — Development Practices

These formalize conventions the script's own ARCHITECTURE comment already
states, plus ones established across the version history. **Treat the
in-script ARCHITECTURE comment as the source of truth for section
layout and the current list of section names** (including named
sub-blocks a section may contain, e.g. STAMINA/FATIGUE inside
SURVIVAL/TIME SIMULATION, MAP inside RENDERING) — this guide and the
other two (`CHANGELOG_GUIDE.md`, `Ashfall_Handoff_Guide.md`) deliberately
don't restate that list, so it can't drift out of sync in three places at
once.

### Content vs. mechanics stay separated

A change should normally touch one of:
- **WORLD DATA** (rooms, items, containers, exits, descriptions, and
  static positional/reference data like map coordinates) — for content
  passes.
- **ACTIONS / SIMULATION** — only when a genuinely new mechanic is
  required, not to accommodate one piece of content.

Rendering is its own concern, separate from both — a new way of
*displaying* existing state (like a map view) is neither new content nor
a new mechanic, and shouldn't be forced into either bucket.

If a content request seems to need a mechanics change, that's a signal to
pause and confirm it's actually a new mechanic, not a shortcut around
existing systems.

### The one case that touches both

"Normally" rather than "exactly", because a new mechanic and the data that
*defines* it are one change, not two. `doConsume()` is the precedent: the
eating mechanic lives in ACTIONS and does nothing at all until items in
`ITEM_REGISTRY` carry `restores` and `verb`. Shipping those halves in
separate passes means shipping a rule that demonstrably does nothing,
followed by the data that switches it on — worse to review, worse to
bisect, and worse in the changelog.

The bound, so the softened rule still bites:

- **Definition data may ride along.** A schema field the new rule reads,
  added to the items or rooms the rule acts on, is part of the mechanic.
- **Instance data may not.** A room, a placement, a description, a map
  coordinate — content that is an *example* of a system rather than part
  of its definition — belongs to a content pass, whatever mechanic
  prompted it.

That line preserves the protection actually worth having: a feature never
gets to rewrite the world to suit itself, and a content request never gets
satisfied by special-casing a mechanic. Neither of those needed the word
"exactly".

`CHANGELOG_GUIDE.md`'s separate **New** and **New content** sections are
what keep the split visible when one entry carries both halves — the
changelog format already assumed this case.

### Identity is explicit, never positional

- Items resolve by `_uid` at runtime, never by array index — indexes are
  not stable across renders.
- Item *definitions* are ID-based: `ITEM_REGISTRY` plus
  `itemFromRegistry()` / `itemsFromRegistry()` are the single source of
  truth for item properties, used throughout `makeDefaultWorld()`, and
  every `giveItem()` call site resolves through it. Gaps in this rule are
  tracked in the backlog rather than named here — search the open issues
  for the current one, rather than assuming either that the rule is fully
  satisfied or that whichever gap was last written down is still the one
  that's open.
- Mechanics check **tags** (`blunt`, `fishing`, `fire-starter`, etc.), not
  item names. A new item that should behave like an existing one gets the
  same tag, not a special-cased name check.

### No duplicated source of truth

An item's shared properties, a system's constants, or a rule's threshold
should be defined in exactly one place. If the same fact needs to be true
in two places, that's a sign it belongs in a shared definition (registry
entry, named constant) instead. `ITEM_REGISTRY` is the model for this:
before it existed, item properties were duplicated inline across world
data; now they're defined once and referenced by id.

### A game rule gets a name, not a literal

The corollary to the rule above, applied to numbers. Any literal that
encodes a game rule — a duration, threshold, rate, capacity, or quantity —
should normally be a named constant, in CONFIG/CONSTANTS or beside the
system that owns it.
A bare number in a mechanic is a fact with no name, and a fact with no name
is one that can be silently duplicated.

The file shows the rule working. `doCraft()` and `doCookInContainer()`
both spend `recipe.minutes` — the duration is declared once per recipe and
read wherever it is needed, including the Cook button, which prints
`fmtDuration(recipe.minutes)` beside its label. Retune a recipe and every
reader of it follows.

The rule's other half is easier to state than to illustrate, because the
illustrations keep getting fixed. A duration spent as a literal in one
place and printed as the same literal in another is two facts that have to
agree, with nothing making them: whichever call site is edited first, the
other starts lying to the player. That shape is what to look for, not a
particular function — a worked example drawn from live code goes stale by
being acted on, which is exactly what happened to the one this passage
used to name.

When a derived value exists, write the derivation rather than the result.
Three firewood burning for sixty minutes each is `FIRE_BUILD_WOOD *
FIRE_MINUTES_PER_WOOD`, not `180` — the second form is correct today and
silently wrong the moment either input is retuned.

**The test is whether the call site reads better, not whether the rule
applies.** Naming is the default because most game rules are clearer
named, not because every number must be. If the named form is harder to
read than the number was, or the name would only restate the digits
(`TWO = 2`), or the constant would sit so far from its one and only use
that a reader has to go looking — leave the literal. A rule that makes
code worse in order to satisfy itself has stopped being useful.

Cases where the literal usually wins:

- **Mathematical identities** — `* 180 / Math.PI`, a loop's `1e-9`
  epsilon, an easing exponent. These are not game rules and a name
  obscures them.
- **Per-instance content** — one building's label offset, one item's
  weight, one room's capacity. These are data, defined once at their
  instance; they are not shared facts.
- **Structurally trivial** — `0`, `1`, array bounds, and the like.

That list is a guide, not a boundary. The question to ask at each literal
is which form a reader would rather meet, and the honest answer is
sometimes the number.

### Comments carry intent, not history

`CHANGELOG.md` records how the code got here and `git blame` records when.
The source describes what is true now. A comment that says *when* something
arrived ("added in v0.4.1", "(v0.4.6)", "unchanged in this revision") is
duplicating the changelog into a place where nothing will ever catch it
drifting — and a comment naming a handoff, a roadmap item number, or a
version is a reference that goes stale on its own schedule.

Comments that earn their place:

- **Schema blocks.** The language has no types and the project has no
  build step, so the ROOM/CONTAINER/EXIT/ITEM schema comments are the only
  specification of those shapes. Keep them whole and keep them current.
- **Invariants code can't state.** "`_uid` is the stable identity; array
  indexes are not" is the model — a rule spanning many call sites that no
  single line can express.
- **Why, where the what is already obvious.** Why `doSearch()` is
  deliberately unkeyed; why firearms were left out. A reader can see what
  the code does and still not know why it was allowed to.

Comments that usually don't: restating the line below, recording when a
change shipped, pointing at a document outside the repository, or standing
in for structure a function name would carry better.

**The goal is fewer comments, not none.** Deleting a comment that was
doing real work is a regression dressed as tidying. Where a comment is
genuinely the clearest way to convey something — and in a single-file,
no-build-step, untyped codebase it often is — keep it, whichever list
above it appears to fall under. Before removing one, say what a reader
loses; if the answer is anything, it stays.

### Every "no behavior change" claim gets proven, not asserted

Reorg, doc, and cleanup passes must be verifiable: a syntax check, a diff
against the prior version's HTML, or an explicit list of what wasn't
touched. "Should be safe" is not sufficient — see the Validation
Performed pattern in the changelog guide.

### Judgment calls get flagged, not hidden

When a pass introduces a value or a design choice with no prior
convention to follow (a threshold, a balance number, a naming choice,
a coordinate scheme, a pick between two options a handoff left open),
say so explicitly and mark it as retunable. Don't let an arbitrary first
guess read as an authoritative design decision.

### File layout

Filenames are stable and carry no version. Git tags mark releases, and
`git log` says how current any file is — a version baked into a filename
just guarantees that every document referencing it goes stale on the next
bump.

- `ashfall.html` — the game.
- `CHANGELOG.md` — one cumulative file, newest entry on top. See
  `CHANGELOG_GUIDE.md`.
- `CLAUDE.md` — the rules that bind even when these guides go unread.
- `docs/` — this guide and its two siblings. Process documentation only;
  nothing a session needs at runtime.
- `handoffs/<feature-name>.md` — one file per handoff, kept after it
  ships. Its commit date says when it was written; nothing needs deleting.
- The backlog is GitHub Issues, not a file. Tier is a label
  (`tier-0`…`tier-3`).
- Every shipped version is tagged `vX.Y.Z` on the merge commit.

### Handoff hygiene

- Every version bump gets a changelog entry, written per
  `CHANGELOG_GUIDE.md`.
- Every planning session that concludes ready to hand off produces a
  handoff file per `Ashfall_Handoff_Guide.md`, including its rule that
  genuinely open design questions (as opposed to narrow implementation
  choices) get resolved with Tom before the handoff is considered ready.
- An issue is closed by the pull request that fulfils it (`Closes #NN`),
  never by hand and never by a session tidying up after itself. If an
  issue's scope has been partly overtaken by shipped work, edit it down to
  what's actually left rather than leaving a stale claim standing.
- Before starting a change, name which issue and which ARCHITECTURE
  section it belongs to. If it maps to no open issue, file one before
  writing code.

---

## Part 3 — Workflow

Every version moves through two session types, in order. Each has fixed
inputs and outputs — a session shouldn't skip an input or improvise an
output not listed here.

Both session types run against the repository, not against attached
files. "Input" below means *read this before starting*, not *paste this
into the conversation* — the session has the repo and can open anything
in it. What hasn't changed is the obligation: a claim about what the code
already does gets checked against the file, never recalled from memory.

### 1. Planning session

**Inputs — read before starting:**
- This Project Guide.
- `ashfall.html` at `main`, in full. Planning claims about "what already
  exists" (schema fields, world-data shape, whether a system exists yet)
  must be verified against the real file, per Part 2's "proven, not
  asserted" rule. This is what the "Relevant existing state" section of a
  handoff depends on, and it's what caught the roadmap drift reconciled
  in v0.2.5.
- The open issues for the area under discussion — the backlog lives in
  GitHub Issues, labelled `tier-0` through `tier-3`. If the tracker is
  unreachable, say so and carry on: planning works without it, and
  anything this session finds gets filed once it's back.
- The most recent `CHANGELOG.md` entries — the last few versions, not the
  whole file.

**Purpose:** discuss and design a feature or system — scope, rules, open
questions, tradeoffs.

**Outputs — two, on different schedules:**

**Issues, filed as they surface.** A planning session about one feature
routinely turns up other work: related cleanups, bugs, scope that belongs
later. File each as an issue the moment it comes up, while the reasoning
is still fresh, labelled by tier. Don't hold them for the wrap — they're
independent of whether this session reaches a handoff, and a session that
ends inconclusively should still leave them behind.

**A handoff file, only at the wrap.** Produced *only* at the point the
session concludes and is genuinely ready to become code, per
`Ashfall_Handoff_Guide.md`. A planning session that doesn't reach that
point produces no handoff — better to leave the thread unresolved than to
force out a premature spec.

The handoff carries only what was decided. Not the discussion that got
there, not questions already answered during the session, not the items
that became issues. That distillation is the whole reason the handoff
exists: the coding session should never have to read around anything to
find the instruction.

Commit the handoff to `main` at the wrap, as `handoffs/<feature-name>.md`.
Committing it before any implementation exists is what lets `git log` show
the spec predated the code — "proven, not asserted" applied to the process
itself. It also means the coding session has it already; nothing needs
handing over.

### 2. Coding session

**Inputs — read before starting:**
- `ashfall.html` — implementation happens directly against this file.
- The **handoff file** in `handoffs/` that specs this work. The handoff is
  used for exactly this — it is not referenced again once implementation
  starts, and it is not a living document.

Nothing else. Not the changelog, not the issue backlog — implementation
never needs either, and the changelog is long enough that reading it up
front costs real context for no return. Both come into play at wrap-time,
below.

**Purpose:** implement exactly what the handoff specifies, resolving any
"Design decisions to make during implementation" it left open.

Work on a branch. Never commit directly to `main`.

**Output — one pull request**, opened once implementation is complete and
validated:

- **The updated `ashfall.html`**, with `GAME_CONFIG.VERSION` bumped per
  the tier mapping in `Ashfall_Handoff_Guide.md` Part 1.
- **A new `CHANGELOG.md` entry**, prepended per `CHANGELOG_GUIDE.md`,
  naming the handoff file and recording any decisions it left open that
  this session resolved. Every session, no exceptions.
- **A PR description** that states the pass's intent and closes the issue
  this work fulfils: `Closes #NN`. That one line is the traceability
  chain — issue → PR → commits → changelog entry → handoff file — with no
  hand-maintained cross-reference anywhere in it to drift.
- **New issues for anything deferred**: cut scope, a follow-up this pass
  surfaced but didn't build, anything that now belongs in the backlog and
  didn't before. File them, and reference them in the PR.

Do **not** file an issue to record what this session *shipped*, and don't
close the fulfilled issue by hand — `Closes #NN` does it on merge.

Merging the PR is what ships the version. Tag the merge commit `vX.Y.Z`.

### Validation

A "no behavior change" claim is checkable rather than assertable: a diff
shows exactly what moved. The changelog's **Validation performed** and
**Explicitly NOT changed** sections should cite that diff rather than
stand in for one — the point of both sections was always to prove the
claim, and there is a tool that can.

**Diff against the base branch, not against a tag:**

```
git diff origin/main...HEAD -- ashfall.html
```

This is what a coding session actually wants — everything this branch
changed and nothing else — and it works regardless of the tag situation
below. Prefer it.

**Diffing against a release tag needs care.** Tags through `v0.4.3`
predate the filename-normalization pass, so at those tags the game lives
at a versioned path (`ashfall_0_4_3.html`, and so on). `git diff
v0.4.3..HEAD -- ashfall.html` therefore matches nothing on the left and
reports the whole file as a new addition — it looks like a diff and is
not one. Name both blobs instead:

```
git diff v0.4.3:ashfall_0_4_3.html HEAD:ashfall.html
```

From `v0.4.4` onward the tag carries `ashfall.html` and the plain form
works; the versioned-path caveat covers `v0.4.0`–`v0.4.3` only. If a
version you need has no tag, diff against the merge commit or the base
branch instead.

### Using this at the start of a session

1. Identify which of the two session types this is.
2. Read that session type's inputs. Don't assume any of it from memory.
3. State the specific change being worked on, and which issue it belongs
   to. If it maps to no open issue, file one before starting.
4. Let the Project Guide govern *how* it's written (tone, structure,
   identity/data conventions), the issue backlog govern *what*, the
   handoff guide govern *how a plan becomes an implementable spec*, and
   the changelog guide govern *how the result gets recorded*.
