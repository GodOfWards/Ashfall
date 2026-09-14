# Ashfall

A quiet-apocalypse survival game: one self-contained file, `ashfall.html`
(~4,900 lines, no build step, no dependencies). Open it in a browser to run it.

## Read before you change anything

- **`docs/Ashfall_Project_Guide.md`** — tone, conventions, and the session workflow.
  Read it once per session, before making changes.
- **`docs/Ashfall_Handoff_Guide.md`** — versioning scheme, and how a plan becomes a spec.
- **`docs/CHANGELOG_GUIDE.md`** — how to write the changelog entry.
- **The `ARCHITECTURE` comment** at the top of the script (`ashfall.html:175`) is
  the source of truth for section layout. No document restates that list; check
  the comment.

The rules below are the ones that bite if you skip those documents. They are a
summary, not a replacement.

## Which session is this?

Every version moves through two session types. Identify which one you're in
before starting — they have different inputs and different outputs.

- **Planning session** — designs a feature. Reads the Project Guide,
  `ashfall.html`, the open issues, and recent `CHANGELOG.md` entries. Files
  issues as they surface. Produces a handoff in `handoffs/` *only* if it
  reaches a conclusion; commits it to `main` at the wrap. Never writes game code.
- **Coding session** — implements one handoff. Reads `ashfall.html` and that
  handoff, and nothing else. Works on a branch. Output is one pull request.

Full detail in the Project Guide, Part 3.

## Rules that bind

**Content vs. mechanics stay separated.** A change touches WORLD DATA (content)
or ACTIONS/SIMULATION (mechanics), not both. Rendering is its own concern — a
new way of displaying existing state is neither. If a content request seems to
need a mechanics change, stop and confirm it's genuinely a new mechanic.

**Mechanics check tags, never names.** A new item that should behave like an
existing one gets the same tag (`blunt`, `fishing`, `fire-starter`, …). Never
`it.name === "Something"`.

**Identity is explicit, never positional.** Items resolve by `_uid` at runtime,
never by array index. Item definitions come from `ITEM_REGISTRY` via
`itemFromRegistry()` / `itemsFromRegistry()`.

**One source of truth.** A constant, threshold, or item property is defined
once. If the same fact must hold in two places, it belongs in a shared
definition.

**New persistent state rotates the save key.** `SAVE_KEY` derives from
`MAJOR.MINOR` (`ashfall.html:244`). A PATCH bump keeps existing browser saves
loading; a MINOR bump breaks them. So: new state fields mean MINOR, and MINOR is
a real seam — never a formality.

**Flag judgment calls.** A threshold, balance number, or naming choice with no
prior convention gets called out as retunable, not left to read as settled.

**Prove "no behavior change".** `git diff vX.Y.Z..HEAD -- ashfall.html` is the
proof. Assertion is not.

## Wrap-time checklist (coding sessions)

Every PR carries all four:

1. `ashfall.html` with `GAME_CONFIG.VERSION` bumped (`ashfall.html:243`).
2. A new `CHANGELOG.md` entry at the top, per `docs/CHANGELOG_GUIDE.md`, naming the
   handoff by path.
3. `Closes #NN` in the PR description for the issue this fulfils. Never close an
   issue by hand.
4. New issues for anything deferred — cut scope, follow-ups this pass surfaced.
   If nothing was deferred, say so in the changelog's Documentation section.

The merge ships the version. Tag the merge commit `vX.Y.Z`.

## Conventions

- **Filenames carry no version.** Git tags mark releases. Never rename a file to
  add a version number.
- **The backlog is GitHub Issues**, labelled `tier-0` through `tier-3`.
  `tier-0`/`tier-1` maps to PATCH, `tier-2`/`tier-3` to MINOR.
- **Handoffs are kept**, not deleted once implemented. Their commit date records
  that the spec predated the code. Whether one already **shipped** is derivable —
  `grep -l "handoffs/<name>.md" CHANGELOG.md` — so it never gets marked by hand. A
  handoff that is **superseded** (never shipped, and the code moved) is the one case
  nothing else records: it gets a banner on the file's first line, body untouched,
  because a coding session reads the handoff and nothing else. Never rename or move a
  handoff to show status — changelog entries cite them by path. Handoff Guide, Part 2.
- If the issue tracker is unreachable, say so and continue — the repo's files
  stand alone.

## Writing game text

Second person, present tense, plain sentences. Understatement over drama — the
horror is in the mundane detail. Tell the story through what people left behind,
never through exposition, and never explain the collapse itself. One to three
sentences. Functional UI text is held to clarity instead, not to this tone.

The Project Guide, Part 1 has the full checklist and examples. Match the
existing descriptions; don't invent a new voice.
