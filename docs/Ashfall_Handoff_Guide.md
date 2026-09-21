# Ashfall — Handoff Template & Versioning Guide

## Purpose

A handoff is the output of a **planning session**, produced only once
that session has concluded and is ready to become code — see the Project
Guide's Workflow section for where this sits in the planning → coding
sequence. A handoff exists for exactly one reason: to be the instruction
set a **coding session** implements against. It is not carried through
open-ended discussion, and it is not a session summary.

It's a spec — the same kind of document the script's own comments
already reference (the Stamina & Fatigue system was built from exactly
this pattern: exact rules, exact thresholds, exact formulas, nothing
left for the implementer to infer or decide). A good handoff means a
coding session never has to come back and ask Tom "wait, what did we
mean by X" for anything that could have been settled during planning.

This guide covers what goes *in* a handoff and how it's versioned/named.
For how handoffs relate to the other three documents and to planning vs.
coding sessions, see the Project Guide's Workflow section — that
relationship isn't repeated here.

---

## Part 1 — Versioning Scheme

Ashfall is still in its `0.x` prototype phase — `MAJOR` stays `0` until a
deliberate decision to leave that phase (see below). Format is
`MAJOR.MINOR.PATCH`.

### PATCH (the last number)

For work that doesn't add new persistent state: bug fixes, hardening,
reorg/documentation-only passes, wording/UX fixes, and content or
rendering additions (new rooms, items, descriptions, new views onto
existing state) that don't require new save fields.

Maps to **`tier-0`** and **`tier-1`** issues by default.

Technical anchor: `versionCompat()` derives the save key from
`MAJOR.MINOR` only, so a PATCH bump keeps the same `SAVE_KEY` — existing
browser saves keep loading under "Save to this browser" with no extra
step.

### MINOR (the middle number)

For new mechanics or systems, especially ones introducing new persistent
state (new vitals, new state fields, new gameplay systems).

Maps to **`tier-2`** and **`tier-3`** issues by default.

Technical anchor: a MINOR bump changes `SAVE_KEY`. Existing browser saves
won't auto-load under the new key — still recoverable via Export/Import,
but the automatic browser-slot continuity resets. Treat a MINOR bump as a
real seam, not a formality.

Convention going forward: a new MINOR version starts its PATCH counter at
`0` (e.g. `0.3.0`). Historical `CHANGELOG.md` entries don't all follow
this — that's fine, this is the clean rule from here on.

### MAJOR (the first number)

Reserved for a deliberate exit from the `0.x` prototype phase — e.g. once
the core `tier-2`/`tier-3` systems are all in place and the game is a
complete loop. Not automatic from any single feature; call it out
explicitly if a handoff genuinely thinks it applies.

### Stating the version-change type for a handoff

A handoff does **not** predict or lock the exact next version number
(`X.Y.Z`) — that number depends on the current shipped version at the
moment the coding session actually runs, which the handoff can't know in
advance, especially since handoffs may queue up. What the handoff *can*
and must state, using the tier mapping above, is the **type** of change
it implies: `PATCH` or `MINOR`.

Sometimes the PATCH-vs-MINOR call genuinely depends on an implementation
decision the handoff has deliberately left to the coding session (see
Part 3's "Design decisions to make during implementation" — e.g. a
feature that stays PATCH under one option but crosses into new persistent
state, and MINOR, under another). In that case:
- Mark the version-change type **tentative** in the header and state
  which option keeps it a PATCH vs. which pushes it to MINOR.
- The coding session resolves it when the decision is made, computes the
  actual `X.Y.Z` from whatever version is current at implementation time,
  and bumps `GAME_CONFIG.VERSION` accordingly.
- Record which type actually applied (and why, if it was the tentative
  case) in the changelog entry's Notes/assumptions section.

### Documentation-only passes

A pass that leaves `ashfall.html` untouched ships no version at all, so it
has no change type to state. Write `None — documentation only` where the
header asks for one, and say in a sentence why. `CLAUDE.md`'s wrap-time
checklist owns that test and says what such a pull request carries instead
of a bump, an entry and a tag.

---

## Part 2 — Handoff File Naming

Every handoff file is named:

```
handoffs/<feature-name>.md          while it is live
handoffs/archive/<feature-name>.md  once it is not
```

The name never changes; only the directory does. Feature name, not
version — the handoff doesn't lock a target version (see Part 1), so it
can't be named by one. Traceability runs through GitHub: the handoff names
its issue, the pull request implementing it says `Closes #NN`, and the
changelog entry names the handoff path. Issue
→ PR → commits → changelog entry → handoff is then walkable in either
direction without a hand-maintained cross-reference anywhere in it.

The handoff lands on `main` when the planning session wraps (by whichever
route — Project Guide, Part 3), and is kept after it ships — moved to
`handoffs/archive/`, never deleted. Its commit date is the record that the
spec predated the code; there's no delete-when-consumed step.

### When a handoff is no longer live

Keeping handoffs means most of them are not instructions any more. The
test is one question: **would a coding session handed this file and
`ashfall.html` today produce the right change?** If not, for any reason,
it is not live. That is the coding session's literal contract, so it is
the only question worth asking.

A handoff that fails it moves to `handoffs/archive/`, and the move is the
answer to that question: a coding session opens the top level of
`handoffs/` and everything it finds there is an instruction. That is the
whole purpose of the folder, and it is deliberately the *only* thing the
folder claims. Which version consumed a handoff, and whether its body can
still be trusted, are separate questions answered separately — below.

There are two ways to fail the live test, and they are recorded
differently.

**Spent** — it shipped. Re-implementing it is redundant at best. This is
already recorded, because every changelog entry that implements a handoff
carries an `Implements:` field naming it by path (`CHANGELOG_GUIDE.md`),
so status is derivable with no new bookkeeping:

```
grep -l "Implements: handoffs/<name>.md" CHANGELOG.md
```

A hit means spent, and the `## vX.Y.Z` heading above it says which version
consumed it. The path in that field is where the handoff was read from —
the top level, since that is where a live handoff sits — so an
`Implements:` line that no longer resolves resolves under
`handoffs/archive/`. Entries are history and are not rewritten when a
handoff is archived; the grep matches changelog text, not the filesystem,
so archiving never breaks it.

The field is what makes this reliable. A changelog entry has three reasons
to name a handoff path — it implemented it, it unblocked it, or it cited
it as context — and only the first carries the field, so a mention can no
longer be mistaken for an implementation. **Never banner a spent
handoff** — that would hand-maintain a copy of the changelog, which is
what one-source-of-truth exists to prevent, and it would drift. Moving
it to `handoffs/archive/` is not that: the folder records only that the
file is no longer an instruction, which is the one fact the changelog
cannot be consulted for by a session that has been told not to open it.

One class of handoff has no changelog entry to grep at all. A
documentation-only pass ships no version and writes no entry (Part 1,
"Documentation-only passes"), so its handoff can never register as spent
by the test above — `handoffs/archive/documentation-drift.md` is the first
instance. For that class the archive move is the whole record, which is
why the wrap-time checklist asks for it on a documentation-only pass too.

**Superseded** — it never shipped, or only partly, and the code moved
underneath it. Implementing it would now be actively wrong. Signs: code it
names by identifier is gone from `ashfall.html`; its "Relevant existing
state" no longer describes the file; its findings were fixed by a
different mechanism; its issue was closed by a pull request that did not
use it.

Nothing in the repository knows this — a handoff can be wrong while every
other file stays silent — so it is the one case that must be written down,
and it is written **in the handoff itself**. Marking it in the issue does
not reach anyone: a coding session opens the handoff and `ashfall.html`
and nothing else, which is the workflow working as intended.

- The move to `handoffs/archive/`, same as any inert handoff — being
  superseded is one way of not being live, not a separate shelf.
- A blockquote at the very top, above the title, saying it is superseded
  and must not be implemented. First line, so `head -1
  handoffs/archive/*.md` reports the whole shelf without opening a file.
  The folder already says it is not live; the banner is what says the body
  is wrong, which matters the moment anyone reads the file for history.
- What is true now, finding by finding where the handoff had several —
  including which parts shipped and which code it names no longer exists.
- Where the live truth lives: the issue carrying the re-verified findings.

Nothing below the banner is edited or deleted. The point of keeping a
handoff is that it records what was known when it was written; correcting
the body destroys exactly that, and the banner is what lets the stale text
stand without misleading anyone. `handoffs/archive/map-view-ui-fixes.md`
is the worked example.

### Where the move happens

An inert handoff is moved the moment it goes inert, by whoever is already
there:

- **Spent** — the coding session's own pull request moves it, alongside
  the changelog entry that names it. Item 3 of the wrap-time checklist in
  `CLAUDE.md`. `git mv handoffs/<name>.md handoffs/archive/<name>.md`;
  never a delete-and-recreate, which would lose the commit date that
  proves the spec predated the code.
- **Superseded** — moved and bannered together, when it is found stale,
  not at the next wrap. The gap is when someone implements it.

Status is still never put in the *filename*. The name is what the
changelog cites, and renaming one would break every historical reference
to it; the directory carries the status instead, and the name survives the
move intact. A changelog entry written before the archive convention cites
the path the handoff had then, and one written after cites the top-level
path it was read at — both resolve the same way, under
`handoffs/archive/`, which is where every handoff a changelog entry can
name has since arrived.

Nothing moves back. A handoff that fails the live test does not start
passing it again; a new pass on the same ground is a new planning session
and a new handoff.

---

## Part 3 — Handoff Template

Copy this structure for every new handoff. The goal of every section is
the same: leave nothing for the coding session to have to decide *that
Tom should have been asked about*. A narrow implementation choice that
the coding session can make and document on its own (see the fourth
section below) is fine to leave open — that's different from an
unresolved design question.

```markdown
# Ashfall Handoff — <Feature / System Name>

Current shipped version: vX.Y.Z
Implied version-change type: PATCH | MINOR (mark "tentative" if the tier
  depends on a decision below — see Part 1)
Issue: #NN — <name>

## What this is
One or two sentences: the feature/system this handoff specs out, and why
it's being built now (the issue it fulfils, or the problem it solves).
Quote the issue's scope/design-principle wording verbatim if it's short
enough — it's the anchor for everything else in the doc.

## Relevant existing state
What the code already has that this feature builds on or must account
for — verified by reading the current WORLD DATA / PLAYER STATE in
`ashfall.html`, not assumed from memory. This is what lets "Design
decisions" below reason about real constraints instead of guessed ones.

## Rules / mechanics
The actual spec, for anything genuinely settled during planning. Exact
formulas, thresholds, constants, edge cases — written with enough
precision that the implementer isn't inferring intent. This is the
section that should look like the Stamina & Fatigue changelog: rates,
caps, interactions, all stated explicitly, not gestured at.

## Design decisions to make during implementation
Optional — only include this if some choices are genuinely narrow
implementation calls (a coordinate scheme, a data-structure shape,
which of two similarly-simple rendering approaches to use) rather than
decisions that change scope, versioning tier, or player-facing behavior
in a way Tom should weigh in on. For each one: state the options, name a
recommended default if there is one, and require the coding session to
record which it picked (in the changelog's Notes/assumptions or
Documentation section) rather than choosing silently. If a choice would
change the versioning tier (e.g. one option needs new persistent state
and the other doesn't), say so explicitly and cross-reference Part 1.

## Data / schema changes
- New or changed **state fields** (PLAYER STATE).
- New or changed **item schema** fields, tags, or categories (ITEM DATA
  SCHEMA).
- New or changed **room/container/exit** schema fields (WORLD DATA), if
  applicable.
- Anything relevant to the Item Registry direction (see the `tier-0`
  issues), if this handoff touches item definitions.

## In scope
What this pass covers, concretely enough to check off against.

## Explicitly out of scope
Anything discussed and deliberately deferred, so the coding session
doesn't accidentally over-build. Name adjacent open issues that might
look related but aren't a prerequisite or aren't being touched.
This section matters as much as what's in scope.

## Sections touched
Name the ARCHITECTURE sections this implicates, per the script's own
section list and the Project Guide's content-vs-mechanics rule. If this
handoff is content-only, say so explicitly — it tells the coding session
it can skip everything else.

## UI changes
What the player sees or interacts with as a result — new buttons, panel
changes, new status displays, wording. Skip if none.

## Dependencies / issue linkage
Which issue(s) this fulfils or unblocks, by number. Flag explicitly if
implementing this pass is expected to leave anything deferred, postponed,
or open for later — the coding session files those as new issues at
wrap-time (see the Project Guide's Workflow section). The issue this
handoff fulfils needs no closing instructions here: the pull request's
`Closes #NN` does it on merge.

## Open questions for Tom
Only for things that genuinely need Tom's input and weren't resolved
during planning — a real scope or design call, not an implementation
detail (those belong in "Design decisions to make during implementation"
instead). If this section is non-empty, the handoff is not yet ready to
build from as-is; flag that plainly rather than letting the coding
session guess.

## After implementation
Reminder for the coding session: open a pull request carrying the version
bump and a new `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, referencing
this handoff by path, recording any "Design decisions" or "Open questions"
resolutions in it, and closing this handoff's issue with `Closes #NN`.
```

---

## Part 4 — Using this at the end of a planning session

1. Confirm every question that needed Tom's input has an answer in the
   document. A genuinely narrow implementation choice can be left for the
   coding session (via "Design decisions to make during implementation")
   — that's expected, not a gap. An unresolved design/scope question is
   different: put it under "Open questions for Tom" and treat the
   handoff as not-yet-final until it's answered.
2. State the version-change *type* using Part 1's tier mapping — `PATCH`
   or `MINOR`, marked tentative if it depends on a deferred decision.
   Don't pick an `X.Y.Z`; the coding session computes that from whatever
   is current when it runs (see Part 1).
3. Fill out the template in Part 3, omitting sections that don't apply.
4. Save it as `handoffs/<feature-name>.md` and get it onto `main` — see
   the Project Guide's Workflow section for the route.
5. That's the whole handover. A coding session reads the handoff and
   `ashfall.html` and needs nothing else to start — per the Project
   Guide's Workflow section, the changelog and the backlog come into play
   only at wrap-time. The planning conversation itself is never carried
   forward; if something in it mattered, it belongs in the handoff.
