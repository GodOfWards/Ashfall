# 03 — Workflow

How work moves from an idea to a tagged version. The home of the session
mechanics, issues, versioning, the handoff lifecycle and the wrap. Which
session reads what is `CLAUDE.md`'s, and is not repeated here.

## Sessions

Work moves through four kinds of session. A **coding session** implements
one handoff and ends in one pull request. A **planning session** designs a
change and may end in a handoff. A **design session** only designs. A
**research session** only finds facts. All run against the repository. A
claim about what the code already does is checked against the file when it
is made, never recalled.

**Planning.** Discusses scope, rules, trade-offs and open questions. Files
issues as they surface (see Issues). Produces a handoff only if it reaches a
conclusion ready to become code; an unresolved thread is better than a
premature spec. The handoff carries only what was decided: not the
discussion, not questions already answered, not what became issues.

**Design.** Exists so a design can take as long as it needs. Nothing in it
aims at a handoff or a wrap: the session ends when Tom ends it, and wherever
the discussion stands is fine. Decisions go into issue bodies as they're
made; what's still open stays open, written as an open question in the body.
Never propose wrapping up, writing a handoff, or moving on to implementation.

**Research.** The only session that searches the web. It works the open
`research` issues, following `docs/canon/reference/README.md`; a fact no
issue asks for gets one filed first.

**Coding.** Implements exactly what the handoff specifies, resolving any
"Design decisions to make during implementation" it left open. Works on a
branch, never on `main`.

- **The version check, before building.** The spec's recorded version (a
  handoff's `Current shipped version:`, a `designed` issue's
  `Checked against:`) is compared with `GAME_CONFIG.VERSION`. If they
  differ, every premise the spec rests on is re-checked against the file,
  not only the identifiers it names: a premise can go false without
  anything failing. One that no longer holds stops the session: it asks
  Tom and builds nothing. A spec with no recorded version is checked as if
  it differed.
- **Phases.** A handoff large enough to build in phases is committed per
  phase, each message starting `Phase N:`, and the branch is pushed after
  every phase commit, so a reclaimed session loses nothing.
- **The pull request opens at the wrap.** CI runs on pull requests into
  `main`, not on pushes, so earlier pushes trigger nothing.

**A pass Tom asks for directly.** Tom can ask any session to make a change
without a handoff, when the spec already exists (an issue body, say). The
approval covers that scope and nothing past it, and the version check and
the wrap are the same.

## Asking and deciding

**Nothing is edited, committed or pushed without being asked**: `ashfall.html`,
`docs/`, `CLAUDE.md`, every file, and every commit, push, tag and pull
request. A question about a file ("how could we clarify this?") is a
question: propose the wording and wait. Once a change is asked for, it is
asked for: a coding session told to implement a handoff doesn't re-ask per
edit, and stops at the boundary of what was approved. The next good idea
along the way gets asked or filed.

**GitHub Issues are the one standing exception.** Filing, labelling and
editing issues as work surfaces is authorised outright. Holding one back to
ask about it breaks the rule to file as things come up.

**Design decisions are Tom's; implementation choices aren't.**

- A **design decision** changes scope, what the player sees or does, tone, or
  the versioning tier. It is asked and waited on. Flagging it as retunable
  records it; it doesn't license it.
- An **implementation choice** (a data-structure shape, a helper's name,
  which of two equivalent renderings, where a guard goes) is made on the spot
  and named in the changelog or the pull request, never made silently.
- **When it isn't obvious which kind a choice is, it is a design decision.**
  A question costs one exchange; an unasked design decision costs a pass to
  undo.

The handoff template's split between "Design decisions to make during
implementation" and "Open questions for Tom" is this same line, drawn at
handoff time.

## Issues

The backlog is GitHub Issues. If the tracker is unreachable, say so and carry
on; file what surfaced once it's back.

**Labels.** Every issue carries one tier, one kind and, when it applies, one
state, and `designed` once it is. Status never goes in a title.

| Kind | For |
|---|---|
| `research` | A real-world fact the game needs (`docs/canon/reference/README.md`) |
| `mechanic` | A new rule or system, or a change to one |
| `content` | World data: rooms, items, placements, text, wiring a building type |
| `ui` | A new way of showing or reaching existing state |
| `bug` | Something the player sees go wrong |
| `code-health` | Structure, stale comments, performance; no intended behaviour change unless stated |
| `hub` | Tracks a group of issues; its design links to `docs/systems/`, never restates it |
| `process` | How the project works: sessions, docs, CI |

State: `deferred` (decided later), `parked` (not planned for now; a comment
says what would revive it). An idea Tom drops for good is closed instead (see
Closing).

Readiness: `designed` means every design decision is Tom's and made, the
facts it needs are in `docs/canon/reference/` or quoted in the body, and the
body is the spec: a handoff, or a pass from the spec, can be written from it
without more discussion. Only implementation choices a coding session names
are left. A planning or design session applies it when Tom confirms the design is done,
and removes it if the scope reopens. A `designed` body opens with
`Checked against: vX.Y.Z`, the `GAME_CONFIG.VERSION` its premises were last
verified at: set when `designed` is applied, updated whenever the body is
re-verified against the file, and compared by the coding session's version
check (see Sessions). `designed` says nothing about whether the work can
start: what an issue waits on is in GitHub's blocking links, and a
`designed` issue may still be `deferred`.

**Templates.** Each kind has a template in `.github/ISSUE_TEMPLATE/`, and an
issue body follows its kind's template, however it is filed. Filing through
the API bypasses GitHub's forms, so whoever files it opens the template.
Titles read "Subject — elaboration".

**Bodies.**

- **The body is the current truth; comments are history.** When scope
  changes, the body is edited. An issue overtaken by shipped work is edited
  down to what is left, never left standing on a stale claim.
- **Facts are linked, not copied.** Real-world figures live in
  `docs/canon/reference/`, a system's design in `docs/systems/`, shipped
  status in the changelog. An open `research` issue is the exception: its
  findings go in its body the moment they're found, until its pull request
  merges them into the reference folder.
- **Relations use GitHub's own links** (sub-issues, blocked-by), not
  hand-kept tables.

**Filing.** A session files an issue the moment work surfaces (a cleanup, a
bug, scope that belongs later), while the reasoning is fresh, not at the
wrap. Before starting a change, name its issue and its ARCHITECTURE section;
if no issue covers it, file one first. Don't file an issue to record what a
session shipped.

**Closing.** Only by the pull request that fulfils it (`Closes #NN`), never
by hand, with one exception: an idea Tom drops for good is closed by hand as
not planned, with a comment naming the decision, and every issue that
depended on it is edited the same day.

**Choosing a tier.** Two questions, in order:

1. **Does the work need new persistent state?** No: `tier-0` or `tier-1`
   (PATCH). Yes: `tier-2` or `tier-3` (MINOR). A one-line change that adds a
   save field is still MINOR.
2. **How big is it, within the pair?**
   - `tier-0`: a small, local change; one fix, one rename, one data or wording
     correction.
   - `tier-1`: a larger PATCH-sized pass; a fix across several functions, a
     content pass, a new view onto existing state.
   - `tier-2`: one new mechanic or one new piece of persistent state.
   - `tier-3`: a whole system; several mechanics that only make sense
     together, or a change across many sections.

The number within a pair is size, never priority, and never moves work
across the pair.

## Versions

`MAJOR.MINOR.PATCH`, held in `GAME_CONFIG.VERSION`. `SAVE_KEY` derives from
`MAJOR.MINOR` only (`versionCompat()`).

- **PATCH**: no new persistent state. Fixes, hardening, reorganisation,
  wording, and content or rendering that needs no new save field. Existing
  browser saves keep loading.
- **MINOR**: new persistent state. The save key rotates, so existing browser
  saves no longer auto-load (Export and Import still carry them). A real
  seam, never a formality. A new MINOR starts its PATCH at `0`.
- **MAJOR**: stays `0` until a deliberate decision to leave the prototype
  phase. Never automatic.

**A handoff states the type of change, never the number.** `PATCH` or
`MINOR`; the coding session computes `X.Y.Z` from whatever has shipped when
it runs. When the type depends on a choice the handoff leaves open, it is
marked tentative, with which option keeps it PATCH; the changelog records
which applied and why.

**A pass that doesn't touch `ashfall.html` ships no version.** No bump, no
changelog entry, no tag: the game didn't change. Its handoff, if it has one,
says `None — documentation only`. The test is that one question, not a list
of exempt paths, and it is exactly what CI gates on.

## Handoffs

A handoff is the spec a coding session implements: exact rules, thresholds,
formulas and edge cases, leaving nothing Tom should have been asked about.
The template is `04-handoff-template.md`.

**One live at a time.** The top level of `handoffs/` holds at most one live
handoff; sibling handoffs landed together by one planning session count as
one. A planning session that would land a handoff while another is live
doesn't land it: it waits, or supersedes the live one (archived and
bannered, see Superseded), and Tom decides which.

**Writing one, at the end of a planning session:**

1. Nothing else is live at the top level of `handoffs/` (see One live at a
   time).
2. Every question that needs Tom has an answer in it. A narrow implementation
   choice may be left open under "Design decisions to make during
   implementation"; a design question may not. If any "Open questions for
   Tom" remain, the handoff isn't ready, and says so.
3. State the change type (see Versions).
4. Fill the template, omitting sections that don't apply.
5. Save it as `handoffs/<feature-name>.md` and land it on `main` at the wrap,
   directly or by pull request. A handoff left on a branch is invisible to the
   coding session.

The planning conversation is never carried forward: if something in it
mattered, it's in the handoff. Landing the spec before the code is what lets
`git log` show it came first.

**Naming.** `handoffs/<feature-name>.md` while it is live;
`handoffs/archive/<feature-name>.md` once it isn't. By feature, never by
version, and never renamed: the name is how the changelog cites it.

**Live or not.** One test: would a coding session given this file and today's
`ashfall.html` produce the right change? It is run twice: by the planning
session that lands a handoff, on whatever is already live, and by the coding
session's version check (see Sessions), on a handoff that went stale while it
waited. If not, it isn't live, and it moves to `handoffs/archive/` with
`git mv` (never delete-and-recreate, which loses the commit date). The folder claims one thing only: everything at the top
level is an instruction. Nothing moves back; new work on the same ground is
a new handoff.

- **Spent** (it shipped): the coding session's own pull request moves it, in
  the same pull request as the changelog entry that names it. Which version
  shipped it stays derivable with
  `grep -l "Implements: handoffs/<name>.md" CHANGELOG.md`; the handoff itself
  is never bannered, which would hand-copy the changelog. A documentation-only
  pass writes no entry, so for its handoff the archive move is the whole
  record.
- **Superseded** (never shipped, or only partly, and the code moved
  underneath it): moved the moment it is found stale, and bannered: a
  blockquote as its very first line saying it is superseded and must not be
  implemented, what is true now, and where the live truth is. Nothing below
  the banner is edited; the body records what was known when it was written.

A changelog entry cites the path a handoff was read at. One that no longer
resolves resolves under `handoffs/archive/`.

## The wrap

Every pull request that changes `ashfall.html` carries all six:

1. **The version bump** in `GAME_CONFIG.VERSION` (see Versions).
2. **A changelog entry** at the top of `CHANGELOG.md`, per
   `05-changelog-guide.md`, naming the handoff by the path it was read at.
3. **The handoff archived** in the same pull request (`git mv`, filename
   unchanged).
4. **`Closes #NN`** in the description, for each issue it fulfils.
5. **New issues for anything deferred**: cut scope, and follow-ups the pass
   surfaced. If nothing was deferred, the changelog's Documentation section
   says so.
6. **The tag block, as the last thing in the session's final message** (not
   the pull request): Tom pushes tags by hand, and the merge commit doesn't
   exist until he merges.

**Performance.** The Performance check fails a pull request that makes the
sleep, the action, `render()` or `serializeGame()` slower than `main` beyond
its tolerance. Only Tom applies the `perf-accepted` label, which waives it,
judging the slowdown against the handoff's Costs section; a session never
applies it. A coding session whose pull request trips the check says, in the
pull request, what the handoff's Costs predicted and what was measured.

A pass that leaves `ashfall.html` untouched carries 3, 4 and 5 only: the
archive move, if there is a handoff; `Closes #NN`; and the deferred issues,
listed in the pull request, or a line saying nothing was deferred.

**The tag block**, filled in with the pull request number (`NN`) and the
version (`X.Y.Z`):

```sh
git fetch origin main
C=$(git log origin/main --merges -1 --format=%H --grep="^Merge pull request #NN from")
if [ -n "$C" ] && git show "$C:ashfall.html" | grep -qF 'VERSION: "X.Y.Z"'; then
  git tag vX.Y.Z "$C" && git push origin vX.Y.Z
else
  echo "Not tagged: PR #NN has no merge commit on main, or it isn't X.Y.Z"
fi
```

It finds the merge commit by pull request number rather than tagging `HEAD`,
and checks the commit carries the version before tagging, so a wrong tag is
never created. Keep its safeguards as written:

- `[ -n "$C" ]`, because with an empty `$C`, `git show` reads the index and
  could pass;
- the trailing ` from`, which keeps `#12` from matching `#123`.

A squash or rebase merge finds no merge commit and falls through to the
`else`. It assumes a POSIX shell (bash, zsh, Git Bash). A version that
shipped as a commit inside someone else's pull request still gets its own
tag, on the commit carrying its `GAME_CONFIG.VERSION`.
