# Ashfall — Project Guide

## Purpose

This document is the third leg of the handoff set, alongside
`CHANGELOG.md` (what has changed) and the development roadmap (what's
next). Where those two are about *state*, this one is about *judgment* —
the tone, spirit, and conventions that should hold steady across every
future content pass, mechanics pass, and AI-assisted session, even as
individual features come and go. It's also the one document that
describes how a session, `CHANGELOG.md`, the roadmap, and
`Ashfall_Handoff_Guide.md` all fit together (see Part 3, Workflow) — the
other guides link back here rather than each explaining it themselves.

Read this once per new session, before making changes. It changes rarely;
the changelog and roadmap change constantly.

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

A change should touch exactly one of:
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

### Identity is explicit, never positional

- Items resolve by `_uid` at runtime, never by array index — indexes are
  not stable across renders.
- Item *definitions* are ID-based: `ITEM_REGISTRY` plus
  `itemFromRegistry()` / `itemsFromRegistry()` are the single source of
  truth for item properties, used throughout `makeDefaultWorld()`. The
  one remaining gap is tracked as a roadmap Tier 0 cleanup item (a
  handful of `giveItem()` call sites that still construct a literal item
  object at runtime instead of resolving through the registry) — check
  the current roadmap for its status rather than assuming it's done.
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

### Tracker file naming

Both running trackers — the changelog and the roadmap — are named for
the version current as of their last edit, so either filename alone
tells you how current it is:

- Changelog: `CHANGELOG_vX.Y.Z.md`. See `CHANGELOG_GUIDE.md`'s "Where it
  goes" section for the full rule.
- Roadmap: `Ashfall_Development_Roadmap_vX.Y.Z.md`, where `X.Y.Z` is the
  version last shipped (i.e. the version the roadmap was last audited
  against, per its own Purpose section) — not a target/future version.
- Both are single cumulative files, renamed on each update — never a new
  per-version file holding only that update's content. Delete/replace
  the old versioned filename in the same session that renames it.

### Handoff hygiene

- Every version bump gets a changelog entry, written per
  `CHANGELOG_GUIDE.md`.
- Every planning session that concludes ready to hand off produces a
  handoff file per `Ashfall_Handoff_Guide.md`, including its rule that
  genuinely open design questions (as opposed to narrow implementation
  choices) get resolved with Tom before the handoff is considered ready.
- The roadmap must never claim an item is still pending once a handoff
  already covers it or the changelog shows it shipped — check it against
  the current code and changelog before adding to it or relying on it,
  and strip anything already done or contradicted. This check happens
  whenever the roadmap is touched — a planning session using it as an
  input, or a coding session opening it to add deferred items at
  wrap-time — not as a step any session performs solely to remove what
  it just shipped.
- Before starting a change, name which roadmap item and which
  ARCHITECTURE section it belongs to. If it doesn't map cleanly to
  either, that's worth resolving before writing code, not after.

---

## Part 3 — Workflow

Every version moves through two session types, in order. Each has fixed
inputs and outputs — a session shouldn't skip an input or improvise an
output not listed here.

### 1. Planning session

**Inputs:**
- This Project Guide.
- The current roadmap (`Ashfall_Development_Roadmap_vX.Y.Z.md` — see
  Part 2's "Tracker file naming").
- The current changelog (`CHANGELOG_vX.Y.Z.md` — see Part 2's "Tracker
  file naming").
- The **current-version HTML**, in full — not just for the coding
  session. Planning claims about "what already exists" (schema fields,
  world-data shape, whether a system exists yet) must be verified against
  the real file, per Part 2's "proven, not asserted" rule. This is what
  the "Relevant existing state" section of a handoff depends on, and
  it's what caught the roadmap drift reconciled in v0.2.5.

**Purpose:** discuss and design a feature or system — scope, rules,
open questions, tradeoffs.

**Output:** nothing, for most of the session. A handoff file is produced
**only** at the point the session concludes and is genuinely ready to
become code, per `Ashfall_Handoff_Guide.md`. A planning session that
doesn't reach that point produces no artifact — better to leave it
unresolved than to force out a premature handoff.

### 2. Coding session

**Inputs, upfront:**
- The **current-version HTML**, in full — implementation happens
  directly against this file, and the changelog's Validation Performed
  section requires diffing against it.
- The **handoff file** produced by the planning session that specced this
  work. The handoff is used for exactly this — it is not referenced
  again once implementation starts, and it is not a living document.

Nothing else is needed to start. The changelog and, conditionally, the
roadmap are requested only once the session is wrapping up — see Output
below — implementation itself never needs either.

**Purpose:** implement exactly what the handoff specifies, resolving any
"Design decisions to make during implementation" it left open.

**Output, every session — requested at wrap-time (implementation complete
and validated), not before:**
- The updated HTML, with `GAME_CONFIG.VERSION` bumped.
- Request the current changelog (versioned filename — see Part 2's
  "Tracker file naming") and prepend a new entry per `CHANGELOG_GUIDE.md`
  (including renaming the file to the just-bumped version), referencing
  the handoff by filename and recording any deferred decisions it
  resolved. This step always happens.
- Request the current roadmap **only if** this session is leaving
  something deferred, postponed, or left open for later — cut scope, a
  follow-up the pass surfaced but didn't build, anything that now
  belongs in the backlog and didn't before. Add those items and rename
  the file to the version just shipped (per Part 2's "Tracker file
  naming"). Do **not** request the roadmap just to remove the item this
  session shipped — the roadmap not listing an already-shipped item is
  enforced by the audit-before-use rule (Part 2's Handoff hygiene), not
  by this session deleting it. Note in the changelog's Documentation
  section either way, including a line stating nothing was deferred if
  that's the case.

### Using this at the start of a session

1. Identify which of the two session types this is.
2. Attach exactly that session type's inputs above.
3. State the specific change or system being worked on.
4. Let the Project Guide govern *how* it's written (tone, structure,
   identity/data conventions), the roadmap govern *what*, the handoff
   guide govern *how a plan becomes an implementable spec*, and the
   changelog guide govern *how the result gets recorded*.
