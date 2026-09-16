# Ashfall

A quiet-apocalypse survival game: one self-contained file, `ashfall.html` — no
build step, no dependencies. Open it in a browser to run it.

## Start here — which session is this?

Every version moves through two session types. Identify which one you're in
**before reading anything else**. They have different inputs, different outputs,
and each one's inputs are the complete list. Reading the other type's inputs
costs context and buys nothing.

### Planning session

Designs a feature. Never writes game code.

**Read, before starting:**
- `docs/Ashfall_Project_Guide.md` — tone, conventions, workflow.
- `ashfall.html`, in full. Claims about what already exists get checked against
  the file, never recalled.
- The open issues for the area under discussion.
- The last few `CHANGELOG.md` entries — not the whole file.

**Output:** issues filed as they surface, and — only if the session reaches a
conclusion — a handoff at `handoffs/<feature-name>.md`, committed to `main` at
the wrap. Read `docs/Ashfall_Handoff_Guide.md` **at the wrap, when writing the
handoff** — it is not needed before then.

### Coding session

Implements one handoff.

**Read, before starting:** `ashfall.html`, and the one file in `handoffs/` that
specs this work. **Nothing else** — not the changelog, not the backlog, not the
guides. The rules below are what make that sufficient; they're stated here so
implementation never has to open a guide to find them.

Work on a branch. Never commit directly to `main`. Output is one pull request —
see the wrap-time checklist. Read `docs/CHANGELOG_GUIDE.md` **at the wrap, when
writing the entry** — it is not needed before then.

Full detail on both: Project Guide, Part 3.

## Rules that bind

**Section layout lives in the source.** The `ARCHITECTURE` comment at the top of
the script is the source of truth. No document restates that list; check the
comment.

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
`MAJOR.MINOR` (see `versionCompat()`). A PATCH bump keeps existing browser saves
loading; a MINOR bump breaks them. So: new state fields mean MINOR, and MINOR is
a real seam — never a formality.

**Tier maps to version bump.** Issues are labelled `tier-0` through `tier-3`.
`tier-0`/`tier-1` maps to PATCH, `tier-2`/`tier-3` to MINOR.

**Flag judgment calls.** A threshold, balance number, or naming choice with no
prior convention gets called out as retunable, not left to read as settled.

**Prove "no behavior change".** A diff is the proof; assertion is not. Use
`git diff origin/main...HEAD -- ashfall.html` — everything this branch changed
and nothing else. Don't diff against a tag: tags through `v0.4.3` carry the game
at a versioned path, so `git diff v0.4.3..HEAD -- ashfall.html` matches nothing
on the left and reports the whole file as new. It looks like a diff and is not
one. (Project Guide, Part 3 → Validation, if you need the tag-form workaround.)

## Wrap-time checklist (coding sessions)

Every PR carries all five:

1. `ashfall.html` with `GAME_CONFIG.VERSION` bumped.
2. A new `CHANGELOG.md` entry at the top, per `docs/CHANGELOG_GUIDE.md` — read it
   now, at the wrap. The entry names the handoff by path.
3. `Closes #NN` in the PR description for the issue this fulfils. Never close an
   issue by hand.
4. New issues for anything deferred — cut scope, follow-ups this pass surfaced.
   If nothing was deferred, say so in the changelog's Documentation section.
5. After the merge, tag it: `git tag vX.Y.Z <commit>`. **Name the commit
   explicitly.** A bare `git tag vX.Y.Z` tags whatever `HEAD` happens to be, which
   is how `v0.4.4` and `v0.4.5` ended up on the same commit as `v0.4.7` (#32).
   Verify with `git show vX.Y.Z:ashfall.html | grep VERSION` — it must print the
   version you just tagged.

The merge ships the version; the tag is what makes it reachable afterwards. A
version that shipped as a commit inside someone else's PR still gets its own tag,
on the commit carrying its `GAME_CONFIG.VERSION`.

## Conventions

- **Filenames carry no version.** Git tags mark releases. Never rename a file to
  add a version number.
- **The backlog is GitHub Issues**, labelled `tier-0` through `tier-3`.
- **Handoffs are kept**, not deleted once implemented. Their commit date records
  that the spec predated the code. Whether one already **shipped** is derivable —
  `grep -l "handoffs/<name>.md" CHANGELOG.md` — so it never gets marked by hand. A
  handoff that is **superseded** (never shipped, and the code moved) is the one case
  nothing else records: it gets a banner on the file's first line, body untouched,
  because a coding session reads the handoff and nothing else. Never rename or move a
  handoff to show status, and never sort them into status subfolders — changelog
  entries cite them by path, and a moved path breaks every historical reference.
  Handoff Guide, Part 2.
- If the issue tracker is unreachable, say so and continue — the repo's files
  stand alone.

## Writing game text

Second person, present tense, plain sentences. Understatement over drama — the
horror is in the mundane detail. Tell the story through what people left behind,
never through exposition, and never explain the collapse itself. One to three
sentences. Functional UI text is held to clarity instead, not to this tone.

The Project Guide, Part 1 has the full checklist and examples. Match the
existing descriptions; don't invent a new voice.
