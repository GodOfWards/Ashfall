# Ashfall — Changelog Writing Guide

Purpose: every version bump gets one entry prepended to `CHANGELOG.md`,
written by the **coding session** that made the bump (see the Project
Guide's Workflow section for where this fits). The entry must let a
future session (human or AI) understand what changed *without re-reading
the whole script*. This doc defines the format so entries stay consistent
enough to serve that purpose.

## Where it goes

- One running, cumulative file, `CHANGELOG.md`. Never a per-version file
  holding only that version's entry, and never renamed — the filename
  carries no version (see the Project Guide's "File layout"). Its history
  goes back to the start of the project.
- New entries go at the **top**, directly under the file's intro line,
  above the most recent existing entry (reverse-chronological).
- Each entry is separated from the next by a `---` rule.

## Entry header

```
## vX.Y.Z — <short title>
```

- Version must match the bump made to `GAME_CONFIG.VERSION` in the script.
- Title is a few words describing the pass's intent, e.g. "Stamina &
  Fatigue System", "Structural reorganization pass", "Fix take-1
  disappearing bug". If the pass is single-purpose, the title can just
  name the fix.
- If the entry implements a handoff, say so and name it by path (e.g.
  "Implements #3 in full, per `handoffs/lockpicking.md`") — this links
  the record of what shipped back to the spec that produced it and to the
  issue it closed.

## Required closing line

Every entry ends with:

```
**Version**: `GAME_CONFIG.VERSION` `"X.Y.Z"` → `"X.Y.Z+1"`
```

Never omit this — it's the fastest way to confirm a bump actually
happened and match a changelog entry to a specific file.

## Choosing sections

Not every entry needs every section below — use only what applies. Bold
the section label, then bullet the content under it. Observed sections and
when to use them:

- **New** — new mechanics, systems, vitals, content types. Describe rules,
  not implementation details, unless the rule *is* the implementation
  (e.g. exact recovery formulas).
- **New content** — rooms, items, containers, exits, descriptions: WORLD
  DATA additions only. Kept separate from **New** on purpose, so the
  content-vs-mechanics split the Project Guide requires is visible at a
  glance in the changelog rather than inferred from the bullets.
- **Fixed** — bug fixes. State the root cause, not just the symptom, and
  name the fix mechanism (e.g. "stripping `_uid` whenever `addToList()`
  creates a new stack entry").
- **Removed** — deleted content, fields, functions, or constants. Say what
  is gone and what, if anything, replaced it.
- **Hardened** — defensive changes that don't alter intended behavior
  (safe lookups, input validation, atomicity guarantees).
- **Changed / Reworked** — use a section per reworked subsystem if a
  system's rules changed non-trivially (see "Rest (reworked)" / "Sleep
  (reworked)" in v0.2.1 as the model — one subheading per subsystem rather
  than one flat list).
- **UI** — anything visible in the panels/buttons/labels, kept separate
  from underlying mechanics changes.
- **Organization / Structural** — pure reorg passes with no behavior
  change. Always pair with an **Explicitly NOT changed** section (below).
- **Function relocation** — call out any function moved between sections,
  with a one-line rationale tied to the ARCHITECTURE comment's section
  definitions (why the new location is the correct owner).
- **Documentation** — changes to the ARCHITECTURE comment or inline
  schema comments themselves. Also use this section to name any issues
  this pass filed for deferred or newly-surfaced work (see the Project
  Guide's Workflow section), with a line stating nothing was deferred if
  that's the case.
- **Explicitly out of scope** — for a pass built from a handoff file,
  restate what the handoff deliberately deferred, so a reader doesn't
  have to open the handoff to know what *isn't* here.
- **Explicitly NOT changed** — required for any pass claiming "no behavior
  change" (reorg, doc-only, pure hardening). List the things a skeptical
  reader would worry about: balance constants, save format, rendering
  logic, function bodies, content.
- **Validation performed** — required for any pass claiming "no behavior
  change." State what was actually checked and cite the diff:
  `git diff origin/main...HEAD -- ashfall.html` is the proof, alongside a
  syntax check and a section-header audit. "Tested" on its own is not a
  validation record. Diff against the base branch rather than a release
  tag — tags through `v0.4.3` carry the game at a versioned filename, so
  `git diff vX.Y.Z..HEAD -- ashfall.html` silently reports the whole file
  as an addition. See the Project Guide's Validation section for the
  blob-to-blob form if a tag comparison is genuinely what you need.
- **Sections touched** — the ARCHITECTURE sections this pass implicates,
  named per the script's own vocabulary. The single most useful line for
  scoping a future request against this entry.
- **Open questions / decisions resolved** — for a pass built from a
  handoff: what the handoff left open and what this session decided.
  Use this rather than burying resolutions in Notes / assumptions when
  there is more than one, or when the choice changed player-facing
  behavior.
- **Notes / assumptions** — call out any judgment call made where no prior
  convention existed (e.g. picking a threshold value, choosing between
  two options a handoff left open), so it's flagged as retunable rather
  than looking authoritative.

If an entry doesn't fit any of these cleanly, prefer a **Summary**
paragraph up top explaining intent, the way the v0.2.2 reorg entry does,
then whatever sections actually apply.

### Use the documented label, not a variant

Pick the name from the list above rather than inventing a near-synonym —
the list is what makes entries scannable across versions. Variants that
have appeared and should not be used again: `Explicitly NOT in this pass`
(use **Explicitly NOT changed**), `Function relocation / new function`
(use **Function relocation**), `Organization` (use **Organization /
Structural**), `Content` and `Content review adjustments` (use **New
content** or **Changed**), `Design decision resolved` (use **Open
questions / decisions resolved**).

Per-subsystem subheadings *inside* a **Changed / Reworked** block are a
different thing and stay free-form — "Stamina recovery", "Exertion
costs", "Rest (reworked)" are all correct, one per subsystem.

Older entries keep whatever labels they shipped with. They are the record
of what happened; don't rewrite them to match this list.

## What to name things

- Reference the script's own vocabulary: the ARCHITECTURE comment's
  section names, and the named sub-block too when a change is scoped to
  one. That comment is the source of truth for the current list — see the
  Project Guide's Development Practices, which is where the rule lives.
- Use real function/constant names in backticks. Never describe a change
  only in vague terms like "updated the logic."
- State explicitly which section(s) were touched. This is the single most
  useful line for scoping a future request against this entry.
- Distinguish **content** changes (rooms/items/containers/exits — WORLD
  DATA only) from **mechanics** changes (new rules in ACTIONS/SIMULATION),
  per the script's own CONTENT vs MECHANICS rule. If a pass is content-only,
  say so — it tells a future reader they can skip straight to WORLD DATA
  if that's what they're touching.

## Level of detail

- Enough that someone could predict the diff without seeing it — exact
  constants, formulas, and thresholds for new mechanics; exact root cause
  for bug fixes.
- Not a line-by-line diff narration. Group related changes under one
  bullet rather than one bullet per line changed.
- Skip restating anything already covered by the schema/architecture
  comments in the script itself — link to the concept, don't re-explain it.

## Tone / format conventions

- Bold section labels, bullet lists under them, inline code for any
  identifier (function names, constants, tags, file/version strings).
- Past tense, factual, no marketing language.
- Keep each entry self-contained — a reader should not need the previous
  entry to understand this one, even though older entries remain in the
  file for history.
