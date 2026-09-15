# Ashfall Handoff — Make the source self-documenting

Current shipped version: v0.4.8
Implied version-change type: PATCH
Issue: #33 — Make the source self-documenting — name the game rules, drop the
history from the comments

## What this is

One pass over `ashfall.html` with a single goal, quoted from the issue:
**"the source should say what is true now, without prose propping it up."**

Two halves, taken together because they make the same argument:

- **Part A** — drop the comments that duplicate `CHANGELOG.md` and `git blame`,
  and the pointers that resolve nowhere.
- **Part B** — give a name to the literals that encode a game rule, chiefly the
  five action durations that are currently written twice.

### Read this before touching anything

**Readability is the test; the rules below are the default.** This is a judgment
pass, not a sweep. The counts in this handoff are the size of the audit, not a
quota — finishing with fewer changes than listed is a correct outcome if that is
what reading each site honestly produced.

The two Project Guide (Part 2) sections this pass applies — *"A game rule gets a
name, not a literal"* and *"Comments carry intent, not history"* — both say this
explicitly. Read them first; they are the authority, this handoff is the worked
list.

Concretely:

- Before removing a comment, say what a reader loses. If the answer is anything,
  it stays.
- Before naming a literal, read the named form at its call site. If it reads
  worse, or the name only restates the digits, or the constant would sit far
  from its single use, leave the literal.

"Left as is, reads better" is an acceptable answer for any site here, and the
changelog entry is where it gets recorded.

## Relevant existing state

Verified by reading `ashfall.html` at `main` @ **v0.4.8** (5,320 lines). The
issue's own audit was taken at v0.4.6 and every line number in it has since
moved; the numbers below are re-anchored, and each family also carries the
command that regenerates its site list, so a coding session running after
further drift can re-derive rather than trust these.

`GAME_CONFIG.VERSION` is at `:247`, `SAVE_KEY` at `:250`.

**Nothing in the audit was fixed by v0.4.7 or v0.4.8.** All five duration pairs
still disagree, all six stale comments are still present, and the version tails
survived both passes.

### The two prerequisites the issue named are now met

- **"Sequence after #3."** Shipped in v0.4.7 — `buildOuterStreets()` is gone,
  replaced by 16 street builders and 5 building builders, so the group comments
  that pass was to promote into structure no longer exist. Nothing here collides
  with it.
- **"Sequence after the guide edit."** Landed in `4ba3e26` and `b5ab71e`. Both
  Project Guide sections exist, so this pass applies a written rule rather than
  one session's taste.

## Rules / mechanics

### Part A — comments

Four families. They **overlap**: `:254` carries both a handoff name and a
`sec. N` citation, `:261` carries a version, a handoff name and nothing else.
Work site by site, not family by family, and treat the family rules as tests to
apply to each line rather than four separate passes over the file.

#### A1 — version references (51 lines as of v0.4.8)

```
grep -nE '//.*\bv?0\.[0-9]+\.[0-9]+' ashfall.html
```

**Default: strip the version, keep the sentence.** Most of these are a
parenthetical or a clause inside a comment that is otherwise doing real work:

| Before | After |
|---|---|
| `// CONTAINER_SLOTS / SLOT_LABELS (v0.4.2): the equipment slots the player…` | `// CONTAINER_SLOTS / SLOT_LABELS: the equipment slots the player…` |
| `// SPAWN_POOLS (v0.4.0): weighted-RNG loot tables, sibling registry to…` | `// SPAWN_POOLS: weighted-RNG loot tables, sibling registry to…` |
| `// Silent: equipping makes a new inventory tab appear (v0.4.6).` | `// Silent: equipping makes a new inventory tab appear.` |
| `// Both modes are a player-centred window on their own span since v0.4.5 — Wide used to return a constant box, which is why it never panned.` | `// Both modes are a player-centred window on their own span. Wide used to return a constant box, which is why it never panned.` |

The `Silent:` comments (`:3787`, `:3799`, `:3840`, `:3848`, `:3856`, and the two
`:3741`/`:3760` capacity ones) are the clearest case for keeping the sentence:
each explains why a `log()` call is *absent*, and an absence is the one thing no
reader can see in the code.

**Where the version is the whole comment, the comment goes.** `:224`
`// Current version: 0.4.6.` is the only pure instance, and it is now
demonstrably stale — `GAME_CONFIG.VERSION` reads `"0.4.8"` twenty-three lines
below it. Delete the line.

#### A1 exception — a version naming *save-data vintage* is a live predicate, and stays

This is the one distinction the issue does not draw, and it matters.

```js
:4372  // on every load. Older saves (pre-v0.2.9) predate the locationId field —
:4386  // alongside it on every load. Older saves (pre-v0.4.0) predate both
```

These do not record when code arrived. They state **which saves the function
must cope with** — a fact about data that still exists in people's browsers, and
the reason the backfill function is there at all. Strip the version and the
comment stops meaning anything.

**Both stay, versions included.** The test to apply elsewhere: does the version
describe the code's history, or the shape of data the code still handles? Only
the first is history.

#### A1b — `sec. N` citations (18 lines)

```
grep -nE '//.*sec\. ?[0-9]+' ashfall.html
```

These cite numbered sections — `sec. 3`, `8`, `10`, `12-13`, `14`, `16`, `18`,
`22`, `24`, `26`, `28`, `38` — of the Stamina & Fatigue handoff, which is not in
the repository. The issue proposed repointing dangling references to
`CHANGELOG.md`; **that does not work for these.** The v0.2.1 entry carries the
rules in full (123 lines, checked) but has **zero numbered sections**, so there
is nothing for `(sec. 14)` to resolve to.

**Decided during planning: strip the citation, keep the sentence.**

| Before | After |
|---|---|
| `// Walking doesn't directly consume Stamina; jogging does (sec. 8).` | `// Walking doesn't directly consume Stamina; jogging does.` |
| `// Additive 15%-each penalty (sec. 24) — never compounded multiplicatively.` | `// Additive 15%-each penalty — never compounded multiplicatively.` |

Every one of these sentences stands on its own; the citation is the only part
that points nowhere. Where stripping it leaves a dangling dash or double space,
repunctuate.

Two need more than a strip because the citation is load-bearing in the sentence:

- `:271` — `// No "low hunger/thirst" threshold existed in v0.1.3 to inherit
  (sec. 24 asks us to follow existing convention if one is defined) — 30 is a
  reasonable initial balance value and lives here as a single knob.` The
  surviving fact is the last clause: 30 is an initial balance value, retunable,
  and deliberately a single knob. Rewrite to that; drop the archaeology about
  what v0.1.3 did or didn't have.
- `:253` — `// Energy baseline changed in v0.2.1 to 100 -> 0 over 24 game hours
  (was 100/960, ~16h) per the Stamina & Fatigue handoff (sec. 14). Hunger/thirst
  rates are unchanged.` All three facts are history; what is true now is the
  `DECAY` line directly below, which states itself. Delete, or reduce to a note
  that `energy` depletes over 24 game hours if that reads better than the
  fraction alone.

#### A3 — handoff-name references (13 lines)

```
grep -nE '//.*([Hh]andoff|Ashfall v0\.[0-9])' ashfall.html
```

Cited: *"Ashfall v0.2.1 — Stamina & Fatigue System"*, *"Container Spawn Pools &
Population System"*, *"Ashfall v0.2.9.md"*, *"Map Expansion to 8x8 Grid"*,
*"Ashfall v0.2.5.md"*, and "the v0.3.0 handoff". **None resolves.** `handoffs/`
holds six files — `exit-move-split`, `log-noise-and-collapse`,
`map-view-ui-fixes`, `map-zoom-and-label-collisions`, `wide-map-panning`,
`world-data-cleanup` — and not one cited name is among them. These predate the
`handoffs/<feature-name>.md` convention and several were written on deleted
branches; reconstruction is not available.

**Default, same as A1b: strip the pointer, keep the surviving prose.** Where the
pointer was carrying a provenance clause, that goes with it:

- `:473-474` — `// New entries below added in v0.4.0 for SPAWN_POOLS coverage —
  see the "Container Spawn Pools & Population System" handoff, Appendix B.` is
  provenance plus a dead pointer and nothing else. Delete both lines.
- `:512-515` — same opening, but it closes with *"Weights are estimates
  consistent with existing entries for similar real-world items; retunable."*
  That is a live judgment-call flag and exactly what the Project Guide asks to be
  preserved. Keep it; drop the provenance and the pointer.
- `:795-798` — same shape. Keep the weight convention (*"commoner items 5-8,
  rarer or bulkier ones 1-3"*) and the `retunable`; drop *"Pools added in v0.4.2
  for the categories the post-v0.4.0 audit found uncovered"* and *"rollCount/
  emptyChance are the handoff's"*.

**The one exception — repointing, where the pointer is the whole comment and the
rules genuinely exist in `CHANGELOG.md`.** See *Design decisions* below.

#### A2 — actively stale comments (6 lines)

Wrong, not merely redundant. Each needs a specific edit, not a family rule:

| Line | Comment | What to do |
|---|---|---|
| `:224` | `// Current version: 0.4.6.` | **Delete the line.** Duplicates `GAME_CONFIG.VERSION` 23 lines below (`:247`), and is already two versions stale. It sits *inside* the ARCHITECTURE block, which this pass otherwise leaves alone — deleting a version stamp is a line-level fix, not a structural edit to the section list, exactly as with `:340` inside the schema block. It is the only line of its kind in the file. |
| `:340` | `// … reserved for a future respawn cycle (roadmap item 15).` | Reword to `(#15)`. The roadmap file is gone; the number coincides by luck, and #15 is open and is the right target. **Fix the line, do not touch the schema block around it.** |
| `:543` | `// content is roadmap item 13's job, not this pass's.` | Same — `#13`. Also drop `not this pass's`, which has no referent at `main`. |
| `:4328` | `// Save format is unchanged in 0.1.3 (still { version, state, world, doors, windows }).` | **Reword, don't delete.** The format documentation is worth keeping and is the only statement of it; only the "unchanged in 0.1.3" framing is wrong. → `// Save format: { version, state, world, doors, windows }.` The rest of the comment (`_uid` is not persisted specially, `resyncUidCounter()`, `ensureUid()`) is live and stays verbatim. |
| `:4573-4578` | `// Unchanged in this revision, apart from what INVENTORY/ITEM SYSTEM changes required … Added in v0.2.5: the In-Game Viewing Map … per the "Ashfall v0.2.5.md" handoff — ported from map_demo.html …` | **Delete all six lines.** "This revision" has no referent at `main`, `renderCraftPanel`'s state at some past pass is history, and the rest is provenance plus a dead pointer. Nothing here says what is true now. The `RENDERING` banner above it stays. |
| `:4580` | `// MAP (In-Game Viewing Map — Tier 1 item 3)` | → `// MAP (In-Game Viewing Map)`. Tier is a GitHub label now; "item 3" indexes a file that is gone. Keep it as the section banner it is. |

#### What stays, untouched

Named explicitly so this pass doesn't drift into them:

- The **ARCHITECTURE block** (`:178-242`). One line inside it is stale (`:224`,
  above); the block is otherwise the source of truth for section layout.
- The **ROOM / CONTAINER / EXIT / ITEM schema block** (`:297-386`, ~90 lines).
  JS has no types and there is no build step; `ROOM SCHEMA`'s optional-properties
  list is the only enumeration of `sleepSpot`, `hasStove`, `fishable`, `hasTree`
  anywhere. Two lines inside it need the fixes above (`:330`, `:340`); the block
  itself is not up for review.
- The **LOCATIONS coordinate convention** (`:828-857`, ending at `const LOCATIONS`).
- **Invariants the code cannot state** — chiefly *"`_uid` is the stable identity;
  array indexes are not"* (`:236-241`, and the PLAYER STATE restatement).
- Genuine **why** notes: `doSearch()` being deliberately unkeyed; why firearms
  were left out (`:531`); why `isGridTravel()` is deliberately not the
  cross-Location test (`:3908-3912`, once its `(v0.4.4)` is stripped).

### Part B — literals

#### B1 — the five durations written twice (least debatable item here)

Each of these is one fact stored in two places across the ACTIONS ↔ RENDERING
boundary. Change one half and the button lies to the player about what the action
costs. This is `CLAUDE.md`'s existing *"if the same fact must hold in two places,
it belongs in a shared definition"*; the file is currently 6-for-11 on it.

| Constant | Value | ACTIONS site | RENDERING site |
|---|---|---|---|
| `FISH_DURATION_MIN` | 20 | `:4217` `advanceTime(20)` | `:5181` `fmtDuration(20)` |
| `LIGHT_STOVE_MIN` | 5 | `:4237` | `:5184` |
| `BUILD_FIRE_MIN` | 10 | `:4262` | `:5189` |
| `DISMANTLE_CAMPFIRE_MIN` | 10 | `:4293` | `:5192` |
| `CHOP_TREE_MIN` | 30 | `:4318` | `:5210` |

Names follow the existing `_MIN` suffix convention (`REST_DURATION_MIN`,
`SLEEP_COOLDOWN_MIN`, `STAMINA_RECOVERY_DELAY_MIN`, `FIRE_MAX_MIN`) and are
retunable if a better one suggests itself at the call site.

**`BUILD_FIRE_MIN` and `DISMANTLE_CAMPFIRE_MIN` are both 10 and must stay two
constants.** They are different facts that happen to share a value; merging them
means retuning one silently retunes the other.

Declare each beside the system that owns it, in FIRE/COOKING. `FIRE_MAX_MIN`
(`:4241`) is the precedent: declared inside FIRE/COOKING, read from RENDERING at
`:5196`, and visible there because everything is inside one IIFE. No constant
needs to move to CONFIG/CONSTANTS to be reachable.

#### B2 — the fire derivation

```js
:4241  const FIRE_MAX_MIN = 360;                                       // named
:4243  if(room.campfireBuilt) return … countInPools("firewood") >= 3;  // bare
:4257  consumeFromPools("firewood", 3);                                // bare
:4258  room.fireMinutesLeft = 180;                                     // bare
:4271  room.fireMinutesLeft = Math.min((… || 0) + 60, FIRE_MAX_MIN);   // one named, one bare
```

`doAddFuel()` gives **60** minutes per firewood. `doBuildFire()` burns **3**
firewood for **180** minutes. **180 = 3 × 60**, and that relationship appears
nowhere — it is a coincidence of literals in two functions 13 lines apart.

| Constant | Value | Replaces |
|---|---|---|
| `FIRE_BUILD_WOOD` | 3 | `:4243`, `:4257` |
| `FIRE_MINUTES_PER_WOOD` | 60 | `:4271` |

and `:4258` becomes `room.fireMinutesLeft = FIRE_BUILD_WOOD * FIRE_MINUTES_PER_WOOD;`
— the derivation written out, so the invariant holds by construction.

**`CAMPFIRE_KIT_COST = 3` (`:257`) is a different fact that shares the value.**
It is what the kit contains (and what `:4289` refunds half of); the bare `3` at
`:4243`/`:4257` is the fuel charge to start a burn. **Do not merge them**, and
do not express one in terms of the other.

#### B3 — the rest

Same value, two call sites:

| Constant | Value | Sites |
|---|---|---|
| `HEAT_CONTAINER_CAPACITY_KG` | 8 | `:4235` (stove), `:4260` (campfire) |

Single site, but a game rule with a name worth having:

| Constant | Value | Site | Note |
|---|---|---|---|
| `CHOP_TREE_FIREWOOD` | 6 | `:4321` | Tree yield |
| `LOG_MAX_ENTRIES` | 50 | `:3589` | **This is the number #29 exists to retune.** Name it; do not change it. Naming it is the precondition for that issue, not the fulfilment of it. |

#### B4 — candidates, each read at its call site before it changes

The issue's audit found 128 substantive literals from PLAYER STATE onward. These
encode a game rule and are worth *considering*. None is mandatory:

| What | Where (v0.4.8) |
|---|---|
| Starvation / dehydration / illness damage rates (`min/30`, `min/15`, `tick/20`) | `:4048`, `:4049`, `:4052` |
| Illness duration (180) — also flagged in #23 | `:3774` |
| Collapse: every-3rd threshold, 300-minute blackout, 90 energy restored, 20-minute stumble, +30 energy | `:4183`, `:4186`, `:4189` |
| Sleep vs. rest energy multiplier (1 / 2 / 4) | `:4148`, `:4151` |
| Start-of-day offset (`8*60`) | `:3889` |
| Starting vitals (75 / 75 / 85 / 100 / 100 / 0) | `:3432` |
| Inventory capacity (3 kg), keychain unit weight | `:3433`, `:3434` |
| "Never happened" sentinels (`-9999` ×2) | `:3431` |
| Fishing success chance (0.55) | `:4219` |

Two ladders are **genuinely arguable and called out as such**:

```js
:4110  function energyRecoveryMultiplier(){   // 80/60/40/20 → 1.00/.90/.75/.50/.25
:4118  function staminaMaxForEnergy(){        // 40/20 → 100/80/50
```

As `if`-chains they read perfectly well today, and a table of named thresholds
may or may not be an improvement. **Implementer's call, and "left as is, reads
better" is the expected answer as often as not.** Record whichever way it goes.

#### What stays literal

1. **Mathematical identities** — `* 180 / Math.PI` and its `90` folds, the
   `1e-9` loop epsilons (`:3938`, `:3960`, `:4170`), the easing exponent in
   `Math.pow(1-t, 3)`.
2. **Per-instance content** — the 22 `MAP_BUILDINGS` label offsets (`:4639-4651`).
   One pair per building; data, not a shared fact. *(That table's section
   membership is now filed as #39 and is not this pass's problem.)*
3. **Already-named siblings** — the `MAP_*` block is the pattern to copy, not to
   change. v0.4.8 just reworked it.
4. **Structurally trivial** — `0`, `1`, `-1`, array bounds.

## Design decisions to make during implementation

Two, both narrow. Record the choice in the changelog's **Open questions /
decisions resolved**.

1. **Repointing a whole-comment pointer to `CHANGELOG.md`.** The default for a
   dead pointer is to strip it, but a handful of comments *are* nothing but the
   pointer, so stripping deletes them outright. The sharpest is `:261`:

   ```js
   // See "Ashfall v0.2.1 — Stamina & Fatigue System" handoff for full rules.
   ```

   It sits above the STAMINA/FATIGUE constants, and those rules do exist — the
   v0.2.1 `CHANGELOG.md` entry carries them in full. `:617` (Container Spawn
   Pools, → v0.4.0 entry) has the same shape.

   **Recommended: repoint these to the changelog entry** — `// See the v0.2.1
   entry in CHANGELOG.md for the full rules.` A reader following that comment
   wants the rules, and unlike a `sec. N` citation this resolves. Apply it only
   where the pointer is the comment's entire content *and* the target entry
   genuinely carries the rules; strip everywhere else. The alternative — delete
   these too, for one uniform rule — is defensible and cheaper to explain.

2. **Whether `FIRE_MAX_MIN` becomes a derivation.** It is 360, which is
   `6 × FIRE_MINUTES_PER_WOOD`. Writing it as `FIRE_MAX_WOOD *
   FIRE_MINUTES_PER_WOOD` makes the cap "six pieces of wood banked"; leaving it
   at 360 makes it "six hours, however you got there". **Recommended: leave it.**
   The cap reads as its own fact and the derived form invents a `FIRE_MAX_WOOD`
   that nothing else uses. Flip it if the call site disagrees.

## Data / schema changes

**None.** No new or changed state fields, item-schema fields, tags, categories,
or room/container/exit fields. The schema comment blocks get two line-level
wording fixes (`:330`, `:340`) and are otherwise untouched.

`SAVE_KEY` is unaffected — it derives from `MAJOR.MINOR` via `versionCompat()`,
and this is a PATCH.

## In scope

- Part A: the four comment families above, plus the six A2 rewrites.
- Part B: B1 (five duration constants), B2 (the fire derivation), B3
  (`HEAT_CONTAINER_CAPACITY_KG`, `CHOP_TREE_FIREWOOD`, `LOG_MAX_ENTRIES`).
- Part B4 candidates, to whatever extent reading each call site justifies.
- The version bump and changelog entry.

## Explicitly out of scope

- **Changing any value.** Every constant introduced equals the literal it
  replaced. This pass is not a balance pass, and a retune hiding inside it would
  be invisible in a diff this size.
- **#29** — the log cap's *value*. Name the 50; leave it at 50.
- **#23** — the illness system. Name the 180-minute timer if it reads better
  named; do not build anything on it.
- **#39** — `MAP_BUILDINGS` as world data in RENDERING. Filed during the planning
  session that produced this handoff, and deliberately not here.
- **#37, #16** — open map/UI issues. Adjacent, not prerequisites, not touched.
- **WORLD DATA.** `CLAUDE.md`: *"A change touches WORLD DATA (content) or
  ACTIONS/SIMULATION (mechanics), not both."* The comment edits reach into
  WORLD DATA's *comments* (registry provenance, schema wording) but no room,
  item, container, exit or description changes. If a content change starts
  looking necessary, stop — it belongs to a different pass.

## Sections touched

Per the script's own ARCHITECTURE comment: **CONFIG / CONSTANTS**, **WORLD DATA**
(comments only), **PLAYER STATE** (comments only), **SURVIVAL / TIME SIMULATION**
including its STAMINA/FATIGUE sub-block, **ACTIONS** — chiefly FIRE/COOKING —
**PERSISTENCE** (comments only), and **UI / RENDERING** including the MAP
sub-block.

Wide, but shallow: outside Part B's constant introductions, no executable line
changes.

## UI changes

**None intended, and none expected.** No label, button, panel or wording the
player sees changes. The five duration buttons render the same strings they do
today — they just read the same constant the action spends, instead of a second
copy of the number.

If any player-visible string changes, that is a defect in this pass, not a
feature of it.

## Dependencies / issue linkage

- **Fulfils #33.** The pull request carries `Closes #33`.
- **Unblocks #29** — retuning the log cap is a different proposition once the
  number has a name and one home.
- **Prerequisites, both met:** #3 (shipped v0.4.7) and the Project Guide sections
  (`4ba3e26`, `b5ab71e`).
- **Expected to defer:** the Part B4 candidates not taken, and either ladder if
  left as an `if`-chain. These do not need new issues — they are judgment calls
  recorded in the changelog, not cut scope. File an issue only if this pass
  surfaces something genuinely new.

## Proof of no behaviour change

Both halves are mechanically checkable, and the changelog's **Validation
performed** section should cite the actual commands rather than assert the claim.

- **Part A** — the diff touches no non-comment line. Strip comments from the
  before and after and compare; the result must be byte-identical. A single
  non-comment difference means a comment edit ran into code.
- **Part B** — every new constant's value equals the literal it replaced, which
  is checkable constant by constant against the tables above. For the five
  duration pairs, both halves now read the same constant, so the button and the
  action *cannot* disagree by construction — state that, since it is the point of
  the change.
- Plus the usual: a syntax check, and
  `git diff origin/main...HEAD -- ashfall.html` as the diff of record. Diff
  against the base branch, not a tag.

Pair this with an **Explicitly NOT changed** section naming what a skeptical
reader would worry about: balance constants, save format, rendering logic,
function bodies, world content, and every player-visible string.

## Open questions for Tom

**None.** The three questions this handoff's planning session raised were
resolved during it:

- Part A and Part B ship as **one pass**, not two — per the issue's own framing,
  splitting would mean two passes making the same argument.
- The 18 `sec. N` citations get **stripped, sentence kept** — repointing was
  considered and rejected, because the v0.2.1 changelog entry has no numbered
  sections to resolve them against.
- The v0.4.4 / v0.4.5 tag correction (#32) is **Tom's, run locally**, and is not
  part of this pass.

## After implementation

Open a pull request carrying:

1. `ashfall.html` with `GAME_CONFIG.VERSION` bumped — PATCH, so **v0.4.9** if
   nothing else has shipped in between.
2. A new `CHANGELOG.md` entry at the top per `docs/CHANGELOG_GUIDE.md`, naming
   this handoff by path (`handoffs/source-self-documenting.md`), with
   **Organization / Structural**, **Explicitly NOT changed**, **Validation
   performed**, **Sections touched**, and **Open questions / decisions resolved**.
   The interesting content is **every place this pass chose the literal or kept
   the comment, and why** — not the mechanical substitutions.
3. `Closes #33` in the PR description.
4. New issues for anything genuinely deferred, or a line in the changelog's
   **Documentation** section saying nothing was.

Then tag the merge commit `v0.4.9`, naming the commit explicitly — see the
wrap-time checklist in `CLAUDE.md`.
