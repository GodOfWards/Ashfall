# Ashfall Handoff — computeDirection()'s zero vector, and a build-time guard

Current shipped version: v0.4.11
Implied version-change type: PATCH
Issue: #68 — computeDirection() answers "down" for two Locations at the same point, and every building entrance is such a pair — a landmine for #8

## What this is

`computeDirection()` treats "no movement" as "pure vertical movement" and answers
`"down"` for it. Every building entrance in the game is such a pair, and nothing
is visibly wrong today only because no entrance label happens to contain a
compass word. #8 adds roughly forty more buildings, each with hand-written
entrance labels, and the first author who writes the perfectly natural
`"Head east into the pharmacy"` will have it silently rewritten at world-build
time to `"Head down into the pharmacy"` — no error, no warning.

This pass makes the zero vector answer honestly, stops the rewrite from firing
on it, and adds a build-time warning so the next content pass finds out at
authoring time instead of shipping a wrong word.

## Relevant existing state

Verified against `main` @ v0.4.11 by walking every exit in the built world.
Line numbers are v0.4.11's.

- **`computeDirection()`** (`:1557`) is four lines. Its first branch,
  `if(dx === 0 && dy === 0) return dz > 0 ? "up" : "down";`, is reached by the
  zero vector, where `dz > 0` is false and the answer is `"down"`.
- **Ten points in `LOCATIONS` are shared by more than one Location.** This is by
  design — a building floor's `(x,y)` is its street node's:
  ```
  100,0,0     maple2nd, industrial_f0
  300,0,0     maple3rd, police_f0
  100,200,0   main2nd, cornerstore_f0
  100,300,0   water2nd, storage_f0
  200,300,0   water1st, riverbank_f0
  50,100,0    mid_poplar_2_4, oak_f0
  150,100,0   mid_poplar_1_2, acorn_f0
  250,200,0   mid_main_1_3, pharmacy_f0, hardware_f0
  350,200,0   mid_main_3_5, auto_shop_f0
  250,200,3   pharmacy_f1, hardware_f1
  ```
- **Exactly 22 cross-Location exits connect two Locations at the same point**,
  and `computeDirection()` answers `"down"` for every one. **Zero of the 22
  carry a compass word**, so `applyComputedDirections()` rewrites none of them
  today. Both numbers were measured against the built world and are the
  before-state the acceptance tests below check against.
- **`applyComputedDirections()`** (`:1572`) runs once inside `makeDefaultWorld()`.
  It skips an exit whose two rooms share a `locationId`, then skips any label
  not matching `COMPASS_WORD_RE = /\b(north|south|east|west)\b/i`, then
  substitutes the computed word in place. It has no failure path.
- **`moveDirectionRank()`** (`:5328`) already tolerates an unknown direction:
  `return rank == null ? 4 : rank;`, ranking it after south. It is reached only
  for grid travel, which requires both rooms to use their own id as their
  `locationId` — and no two street nodes share a point, so it never sees a zero
  vector today. It must keep tolerating one.
- **`validateLocations()`** (`:4592`) is the model for a dev-only console helper:
  it returns an array of problem strings, `console.warn`s them when non-empty,
  and is wired to nothing.
- **`validateLoadedWorld()`** (`:4504`) is the precedent for the opposite —
  a check that runs automatically because it sits on a real code path.

## Rules / mechanics

All of this is WORLD DATA. Nothing in ACTIONS, SIMULATION or RENDERING changes.

### 1. `computeDirection()` returns `null` for the zero vector

Add the zero-vector case ahead of the vertical branch:

```js
if(dx === 0 && dy === 0 && dz === 0) return null;
if(dx === 0 && dy === 0) return dz > 0 ? "up" : "down";
```

`null` means "these two Locations are at the same point, so there is no
direction between them" — which is the truth, and is different from every
other answer the function can give.

**Genuine vertical movement is untouched.** Two Locations differing only in `z`
still answer `"up"` / `"down"`. This matters for #6 (rooftops), which will add
real `z` differences, and for the stair transitions the Elm handoff already
specs. Do not collapse the two branches.

Update the comment above the function. It currently says pure vertical movement
resolves to up/down; it must now also say that a zero vector resolves to `null`,
and why the two are not the same case.

### 2. `applyComputedDirections()` skips rather than substitutes

Inside the loop, after computing `dir`:

- If `dir` is `null`, **leave `exit.label` exactly as authored** and do not
  substitute. The author's own word stays; it is not silently replaced with a
  wrong one.
- If `dir` is a string, substitute as today.

The existing `slice`/`slice` substitution is unchanged for the non-null case.

### 3. Warn at build time when the two coincide

When `dir` is `null` **and** the label matched `COMPASS_WORD_RE`, emit one
`console.warn`. That conjunction is the whole condition — a same-point exit with
no compass word is the ordinary building entrance, all 22 of them, and must stay
silent or every page load prints twenty-two warnings.

The message must be actionable on its own, naming the room, the destination, the
word that was written and why nothing was done about it. Something of this shape:

```
applyComputedDirections: <fromRoomId> -> <exit.to> label "<exit.label>" contains
a compass word, but <fromLocationId> and <toLocationId> are the same point —
there is no direction between them. Label left as authored; rewrite it without
the compass word.
```

Exact wording is the coding session's, held to clarity rather than the game's
prose tone — this is a developer-facing diagnostic, not player text.

**Why a warn and not a dev-only helper.** #68 proposed a manual validator beside
`validateLocations()`. That is the wrong tool for this specific failure, because
a wrong compass word reads as plausible English: nothing about `"Head down into
the pharmacy"` looks broken to a reader skimming a diff, so the only moment it
can be caught is the moment it is produced. `applyComputedDirections()` already
walks every exit at build time and is the one place where the same-point pair and
the compass word are both in hand. `validateLoadedWorld()` is the precedent for
a check earning a real code path. The cost is one branch and zero output today.

## Design decisions to make during implementation

- **`null` vs. a sentinel string.** The spec above says `null`. `"here"` would
  also work and would let `MOVE_DIRECTION_RANK` name it explicitly. `null` is
  recommended because `moveDirectionRank()`'s existing `rank == null` test
  already handles it with no edit, and because a sentinel string invites a
  caller to print it. Record which was used.
- **Whether the warn carries the Location ids or just the room ids.** Both are
  useful; the ids are what a reader needs to check `LOCATIONS`. Recommended:
  include both, as sketched above. Narrow call, record it.

## Data / schema changes

**None.** No PLAYER STATE field, no ITEM DATA SCHEMA field, no room, container
or exit schema change. `SAVE_KEY` does not rotate and existing browser saves keep
loading. No world data is edited — this pass changes two functions and no room
definition.

## In scope

- `computeDirection()` — the zero-vector branch and its comment.
- `applyComputedDirections()` — the skip path and the warning.

That is the whole pass. It is deliberately small.

## Explicitly out of scope

- **The building-name line split in `renderMapClose()`.** #68's body raises it as
  a second trap in the same area; it is now **#87** and is RENDERING, not WORLD
  DATA. Do not fold it in — the content-vs-mechanics rule makes it a different
  pass, and #87 carries its own before/after obligation.
- **Changing any exit label.** No label is rewritten by this pass, and proving
  that is an acceptance test below. If an entrance label ought to read
  differently, that is a content finding for an issue.
- **Changing `LOCATIONS` so building floors stop sharing their street node's
  point.** The sharing is deliberate and is what makes a building entrance cost
  `MIN_MOVE_MIN`. Leave it.
- **#75** (`MIN_MOVE_MIN` flattening the gait ladder). A same-point exit costing
  one minute is that issue's territory, not this one's.
- **#42 and #82.** Specced separately in `handoffs/room-address-and-shelter.md`.
  They touch every room definition; this pass touches none, and the two can land
  in either order without interacting.

## Sections touched

**WORLD DATA** only — `computeDirection()` and `applyComputedDirections()`, both
of which live there per the ARCHITECTURE comment's note that WORLD DATA carries
LOCATIONS and the direction-derivation helpers that read it.

No ACTIONS, no SIMULATION, no PERSISTENCE, no RENDERING. The ARCHITECTURE comment
itself needs no change: no section gains or loses a responsibility.

## UI changes

**None.** No label changes, no button changes, no new text. The only new output
is a `console.warn` that produces nothing on the current world.

## Validation

- **Every exit label in the built world is byte-identical before and after.**
  Build the world on `origin/main` and on the branch, collect
  `{roomId, exit.to, exit.label}` for all exits in all 218 rooms, and diff.
  Zero differences is the pass condition, and it is what proves "no player-visible
  change" rather than asserting it.
- **`computeDirection()` truth table.** Zero vector → `null`. Same `(x,y)`,
  `z` greater → `"up"`. Same `(x,y)`, `z` less → `"down"`. The four compass cases
  unchanged. The `|dx| === |dy|` diagonal tie still resolves north/south.
- **A fresh `makeDefaultWorld()` prints zero warnings.** All 22 same-point exits
  stay silent because none carries a compass word.
- **The warn fires when it should.** Inject a test exit carrying a compass word
  between two Locations at the same point — `mid_poplar_1_2` → `hallway1` with
  a label like `"Head east into Acorn Apartments"` — and confirm exactly one
  warning is printed **and** the label comes back unchanged. Do this in a
  test-only shim, not by editing the shipped file.
- **`moveDirectionRank()` still ranks an unknown direction 4.** It is unreached
  by a zero vector today; the test guards the branch that catches one later.
- **No page errors** on load.
- **Diff discipline:** `git diff origin/main...HEAD -- ashfall.html` should show
  the version bump and two adjacent hunks in WORLD DATA. No `build*()` function
  and no room definition appears in the diff.

## Dependencies / issue linkage

- **Fulfils #68.** The PR says `Closes #68`.
- **Unblocks #8**, which is the reason this is worth doing now rather than later.
- **#87** was split out of #68 during planning and is deliberately not touched
  here. It is already filed; do not file it again.
- **#6 (rooftops)** will add genuine `z` differences and depends on the up/down
  branch surviving intact.

Nothing is expected to be deferred by this pass. If the implementation surfaces
something new, file it at wrap-time and reference it in the PR; if it surfaces
nothing, say so in the changelog's Documentation section.

## After implementation

Open a pull request carrying the `GAME_CONFIG.VERSION` bump and a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, naming this handoff by path
in the entry's `Implements:` field, recording both design decisions above, and
closing the issue with `Closes #68`. Tag the merge commit per `CLAUDE.md`'s
wrap-time checklist, naming the commit explicitly.
