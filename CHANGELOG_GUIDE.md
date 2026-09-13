# Ashfall — Changelog Writing Guide

Purpose: every version bump gets one entry prepended to `CHANGELOG.md`,
written by the **coding session** that made the bump (see the Project
Guide's Workflow section for where this fits). The entry must let a
future session (human or AI) understand what changed *without re-reading
the whole script*. This doc defines the format so entries stay consistent
enough to serve that purpose.

## Where it goes

- One running, cumulative file — not a new per-version file containing
  only that version's entry. Its history goes back to the start of the
  project regardless of filename.
- **Filename encodes the current (latest) version**:
  `CHANGELOG_vX.Y.Z.md`, where `X.Y.Z` matches the version the entry you
  just wrote bumps *to* (e.g. `CHANGELOG_v0.2.5.md`). Every version bump
  renames the file to match — delete/replace the old versioned filename
  in the same session rather than leaving both around. This is the same
  pattern the roadmap follows (see the Project Guide's Development
  Practices section) — both trackers are named for the version current
  as of last edit, so either file's name alone tells you how current it
  is.
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
- If the entry implements a handoff file, say so and name it (e.g.
  "Implements roadmap Tier 1, item 3 in full, per the `Ashfall
  vX.Y.Z.md` handoff") — this links the record of what shipped back to
  the spec that produced it.

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
- **Fixed** — bug fixes. State the root cause, not just the symptom, and
  name the fix mechanism (e.g. "stripping `_uid` whenever `addToList()`
  creates a new stack entry").
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
  schema comments themselves. Also use this section to record the
  roadmap update that closes out this same coding session (see the
  Project Guide's Workflow section) — if the audit behind that update
  finds items the roadmap still listed as pending that were already
  implemented, or a new gap the pass surfaced, say what was added,
  removed, or renumbered and why (see v0.2.5 as the model).
- **Explicitly out of scope** — for a pass built from a handoff file,
  restate what the handoff deliberately deferred, so a reader doesn't
  have to open the handoff to know what *isn't* here.
- **Explicitly NOT changed** — required for any pass claiming "no behavior
  change" (reorg, doc-only, pure hardening). List the things a skeptical
  reader would worry about: balance constants, save format, rendering
  logic, function bodies, content.
- **Validation performed** — required for any pass claiming "no behavior
  change." State what was actually checked (syntax check, diff against
  the prior version's HTML, section-header audit), not just that it was
  "tested."
- **Notes / assumptions** — call out any judgment call made where no prior
  convention existed (e.g. picking a threshold value, choosing between
  two options a handoff left open), so it's flagged as retunable rather
  than looking authoritative.

If an entry doesn't fit any of these cleanly, prefer a **Summary**
paragraph up top explaining intent, the way the v0.2.2 reorg entry does,
then whatever sections actually apply.

## What to name things

- Reference the script's own vocabulary: the ARCHITECTURE comment's
  top-level section names, plus any named sub-block a section contains
  (e.g. STAMINA/FATIGUE inside SURVIVAL/TIME SIMULATION, MAP inside
  RENDERING) — name the sub-block too when the change is scoped to one.
  The ARCHITECTURE comment in the script is the source of truth for the
  current list; don't copy a section list into this guide, since it will
  drift as sub-blocks are added.
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
