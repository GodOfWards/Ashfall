# 05 — Changelog guide

Every version bump gets one entry in `CHANGELOG.md`, written by the session
that made the bump. An entry lets a later reader understand what changed
without re-reading the script. Whether a pass writes an entry at all, and what
else its pull request carries, is `03-workflow.md`'s (The wrap).

## Adding an entry

The file is long, and nothing in it is needed to add to it.

- **Read only its first 25 lines.** They hold the intro and the marker line
  `<!-- New entries go directly below this line. -->`.
- **Insert directly below the marker:** the new entry, then a line holding
  only `---`, which separates it from the entry below.
- **Don't read earlier entries to copy their format.** This guide is the
  format, and older entries keep whatever labels they shipped with.

CI checks that the newest entry sits directly under the marker, that its
version matches `GAME_CONFIG.VERSION`, and that it ends with the closing line.

## Header

```
## vX.Y.Z — <short title>
```

The version matches the bump. The title is a few words naming the pass's
intent, or just the fix for a single-purpose pass.

## The `Implements:` line

When the entry implements a handoff, the line directly under the header is:

```
Implements: handoffs/<name>.md
```

Plain text: no bold, no backticks, nothing else on the line. It is read by a
command (`grep -l "Implements: handoffs/<name>.md" CHANGELOG.md` answers
"has this handoff shipped?"), and formatting would break a grep anyone can
type from memory. The path is the one the handoff was read at, the top level,
even though the same pull request archives it.

Only an entry that implements a handoff carries the line. An entry that
mentions one (it unblocked it, or cites it) doesn't. The opening prose also
says what the entry implements, for a person reading it: "Implements #NN in
full, per `handoffs/<name>.md`."

## Closing line

Every entry ends with:

```
**Version**: `GAME_CONFIG.VERSION` `"X.Y.Z"` → `"X.Y.Z+1"`
```

## Sections

Use only the sections that apply, with these exact labels, bolded, and
bullets under each. Older entries keep their labels and are never rewritten.

- **New** — new mechanics, systems, vitals. Rules, not implementation, unless
  the rule is the implementation (an exact formula).
- **New content** — WORLD DATA additions only. Kept apart from **New** so the
  content-vs-mechanics split shows at a glance; an entry with both is the
  mechanic shipped with its defining data (`02-code-practices.md`).
- **Fixed** — the root cause and the fix mechanism, not just the symptom.
- **Removed** — what is gone, and what replaced it.
- **Hardened** — defensive changes that don't alter intended behaviour.
- **Changed / Reworked** — a system's rules changed non-trivially. One
  free-form subheading per subsystem inside it.
- **UI** — anything visible in panels, buttons, labels.
- **Organization / Structural** — a pure reorganisation. Always paired with
  **Explicitly NOT changed**.
- **Function relocation** — a function moved between sections, with a one-line
  reason tied to the ARCHITECTURE comment.
- **Documentation** — changes to the ARCHITECTURE comment, schema comments or
  `docs/systems/` made by this pass, and the issues filed for deferred work,
  or a line saying nothing was deferred.
- **Explicitly out of scope** — what the handoff deliberately deferred.
- **Explicitly NOT changed** — required for a "no behaviour change" pass: what
  a sceptical reader would worry about (balance constants, save format,
  rendering, function bodies, content).
- **Validation performed** — required for a "no behaviour change" pass: what
  was checked, citing the diff (`02-code-practices.md`, Proving "no behavior
  change"). "Tested" alone is not a record.
- **Sections touched** — the ARCHITECTURE sections, in the script's own words.
  The most useful line for scoping later work against this entry.
- **Open questions / decisions resolved** — what the handoff left open and
  what was decided.
- **Notes / assumptions** — judgment calls with no prior convention, flagged
  retunable.

If an entry fits none of these cleanly, start with a **Summary** paragraph,
then whichever sections apply.

Don't invent near-synonyms. Labels that have appeared and are not to be
used again: `Explicitly NOT in this pass`, `Function relocation / new
function`, `Organization`, `Content`, `Content review adjustments`, `Design
decision resolved`, `New constants`, `Derivations named`.

## Naming and detail

- Use the script's own vocabulary: ARCHITECTURE section names, and the named
  sub-block when a change is scoped to one.
- Name real functions and constants in backticks; never "updated the logic".
- Say whether a pass is content only: a reader can then skip straight to
  WORLD DATA.
- Enough detail that someone could predict the diff without seeing it: exact
  constants, formulas and thresholds for new mechanics, the exact root cause
  for fixes. Not a line-by-line narration: group related changes.
- Don't re-explain what the schema comments or `docs/systems/` already say;
  point to them.

## Tone

Bold section labels, bullets under them, inline code for every identifier.
Past tense, factual, no marketing language. Each entry stands on its own: a
reader never needs the previous one.
