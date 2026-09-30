# Ashfall Handoff — Code health: history in comments, and containers placed by id

Current shipped version: v0.11.0
Implied version-change type: PATCH
Issue: #363 — Orphaned readout comment above nameplateText(); #374 — Comments
that point at history; #128 — Placing items in a type's containers restates them

## What this is

Three code-health fixes, built in three phases, one per issue and in this
order. None of them changes what the player sees, and none adds saved state.

1. **#363.** Delete the orphaned comment block above `nameplateText()`.
2. **#374.** Take history out of the comments: two changelog pointers, one
   handoff path and every closed-issue number. Write the overdue
   `docs/systems/survival.md`.
3. **#128.** Let a building instance place items into its type's containers by
   container id, instead of restating every container. Give the stove's
   capacity one source.

Each phase has its own proof of "no behaviour change" (below). That is why they
are separate commits.

## Relevant existing state

All of this was verified against `ashfall.html` at v0.11.0. Line numbers are
approximate.

**#363.** In RENDERING, directly after `stoveTimerText()` (~12192), a block
begins "A switchable load's readout, shared by its pop-up's status line and the
Here strip…". It ends "Functional UI text, retunable." No function follows it:
the next lines are `nameplateText()`'s own comment. The block describes
`loadStatusText()` (~12219), whose own comment covers the `readout` rule
(`idle` / `on` / `off` and the switch's position). That comment does not say
where the readout is shown, and does not flag the text as retunable.

**#374.** Today the history pointers are:

- STAMINA / FATIGUE SYSTEM CONSTANTS (~639): "See the v0.2.1 entry in
  CHANGELOG.md for the full rules."
- The SPAWN POOLS `chance` comment (~1350–1357): "The v0.5.1 conversion
  computed each one from the weight/rollCount lottery it replaced… See the
  v0.5.1 entry in CHANGELOG.md for the model and the formula." The formula,
  `P(appears) = (1 - emptyChance) * chance`, is already stated a few lines
  above it.
- LIMA'S STREETS (~1663): "Appendix A of handoffs/lima-release.md, transcribed
  in its own line format…". The source lines that follow (OpenStreetMap, ODbL,
  the read dates, Esri World Imagery, the grid frame) are what matter.
- **Issue numbers**: 111 two- and three-digit `#NN` on about 100 lines, CSS
  comments included, plus the single-digit `#6`, `#7` and `#9`. Line 216's
  `#000` is a CSS colour, not an issue.
  - These issues were **open** at planning time (2026-09-30): #6, #7, #9,
    #10, #15, #47, #58, #111, #116, #134, #149, #163, #164, #166, #179, #212,
    #217, #245, #247, #248, #250, #258, #261, #285, #288, #296, #300, #307,
    #332, #333, #334.
  - Every other number was **closed**.
  - If the tracker is reachable, re-check this list when the phase starts:
    an issue closed since then counts as closed. If the tracker is
    unreachable, say so and use this list.
- `validateWiring()`'s `console.warn` (~9781) names #258 inside a runtime
  string, not a comment.

`docs/02-code-practices.md` ("Comments carry intent, not history") says a
comment never records "which version or issue changed it". It has no
exception for open issues yet.

`docs/systems/README.md` sets a systems doc's format and lists Survival under
"One is overdue". `docs/systems/time.md` already covers the clock, including
`clockStep()`'s part in Hunger and Thirst.

The survival rules live in two places:

- STAMINA / FATIGUE SYSTEM CONSTANTS (~637): `STAMINA_RECOVERY_DELAY_MIN`,
  `BASELINE_STAMINA_RATE`, `REST_STAMINA_RATE`, `FATIGUE_RECOVERY_RATE`,
  `REST_DURATION_MIN`, `SLEEP_ENERGY_RATE`, `SLEEP_COOLDOWN_MIN`,
  `LOW_HUNGER_THRESHOLD`, `LOW_THIRST_THRESHOLD` and `FATIGUE_GAIT_LOCK`.
- The STAMINA / FATIGUE SYSTEM sub-section inside SURVIVAL / TIME SIMULATION
  (~8396): `applyExertion()`, `isExertionDelayActive()`,
  `energyRecoveryMultiplier()`, `staminaMaxForEnergy()`,
  `hungerThirstRecoveryPenalty()`, `fatigueRecoveryAllowed()`,
  `gaitLocked()`, `effectiveGait()`, `recoveryStep()`, the sleep helpers
  (`sleepEnergyCeiling()` through `estimateSleepMinutes()`), `runAwakeStep()`
  and `advanceTime()`.

**#128.** BUILDING TYPES (~3829) has these parts:

- **Schema comment.** A room override's fields replace the type's field by
  field, "so `containers` replaces the whole list".
- **Shared container lists.** `KITCHEN_CONTAINERS`, `BEDROOM_CONTAINERS`,
  `BATHROOM_CONTAINERS` and `SHED_BOX`. The stove entry in
  `KITCHEN_CONTAINERS` writes `capacityKg:8` as a literal.
- **`landmarkInstances()`.** The `home` instance (`row_house`) overrides
  `living`, `kitchen`, `bathroom`, `bedroom` and `garden`. Each override
  restates the room's full container list only to add `items`. All 13
  containers are identical to the type's definitions apart from `items`, and
  they come in the same order. The freezer has no items.
- **`buildBuilding()`.** It copies each container spec. It sets
  `spawnRolled:true` when the spec has non-empty `items` and no `spawnRolled`
  of its own (CONTAINER SCHEMA's rule for hand-placed contents). Build
  problems go in its `problems` list.
- **`HEAT_CONTAINER_CAPACITY_KG = 8`** sits in FIRE / COOKING's constants
  (~8665), commented "stove and campfire alike". Its only reader is the
  campfire's `ensureHeatContainer()` call in `doBuildFire()`.
  `KITCHEN_CONTAINERS` is a top-level `const` evaluated around line 3915,
  inside the same IIFE. Reading the constant there before its declaration
  runs would throw.
- **Saves.** A save stores only what differs from a fresh `makeDefaultWorld()`
  (`savedRoomState()`, `CONTAINER_STATE_FIELDS`). A container's name,
  capacity, pools and tags are definition data, and container ids are what
  saves key on.

## Rules / mechanics

### Phase 1: #363

- Delete the orphaned block above `nameplateText()`.
- Add two facts to `loadStatusText()`'s comment: the readout is shared by the
  load's pop-up status line and the Here strip, and it is "Functional UI text,
  retunable".
- Commit as `Phase 1: …`.

### Phase 2: #374

**The three pointers:**

- **v0.2.1.** Replace the pointer with a one-line pointer to
  `docs/systems/survival.md`.
- **v0.5.1.** Drop the pointer and the version. Keep the why: every `chance`
  is derived from the lottery it replaced so that each item's P(appears)
  carried across; its six decimals mark a derived figure, not a chosen one;
  and it is not a balance knob. The exceptions listed below that paragraph
  stay as they are.
- **Lima's streets.** Drop "Appendix A of handoffs/lima-release.md". Keep
  every word about the data's source, frame and line format.

**Issue numbers in comments:**

- **Open issue** (see the list above): keep it.
- **Closed issue:**
  1. Ask what a reader would lose without the number.
  2. If the comment doesn't already say the why, write it in words.
  3. Drop the number.
  4. Tidy the sentence it leaves behind, so no "()" or dangling "as in" is
     left.
  - A line whose only content was the history, such as "(#291)" after a
    heading, loses only the reference.
  - Before removing a whole comment, say what a reader loses; if the answer
    is anything, it stays.
- **Your decisions:** "Tom's figure (#317), not researched" becomes "Tom's
  figure, not researched". "Tom, #292 option C" becomes wording that still
  says it was your call, without the number.
- Where a closed issue was a research issue behind a figure, keep the
  figure's source as it stands. Moving sources to `docs/canon/reference/`
  is not this pass.
- Leave `validateWiring()`'s `console.warn` string as it is.

**`docs/02-code-practices.md`.** In "Comments carry intent, not history", add
the open-issue exception. Suggested wording, to be adjusted to fit the
paragraph:

> A reference to an open issue is the exception: it marks a known gap and
> where its plan lives ("deferred to #217"), so it is intent. The pass that
> closes an issue removes or rewrites every reference to it.

**`docs/systems/survival.md`.** Write it **from the code alone**: the changelog
is not a source.

- Use `docs/systems/README.md`'s format: Purpose, Model, Invariants, Entry
  points, Constants and Costs.
- **Scope:** the STAMINA / FATIGUE SYSTEM and its constants block, meaning
  Exertion, Stamina, Fatigue, Energy, rest, sleep and the gait lock, plus the
  Hunger and Thirst thresholds as they feed recovery.
- Link to `time.md` for the clock; don't restate it.
- Constants are named, never given values.
- Everything named in backticks must exist in `ashfall.html`: the docs CI
  (`.github/scripts/docs_check.py`) checks this.
- If the constants block's comment holds anything that is a system overview
  rather than intent, it moves into the doc, leaving the one-line pointer.

**`docs/systems/README.md`.** Add Survival to the index and remove the "One is
overdue" block.

Commit as `Phase 2: …`.

### Phase 3: #128

- **Items by container id.** Add a room-override field that places items into
  the type's containers by id, without replacing the list:
  - **Shape:** a map from container id to a list of placement refs, e.g.
    `items:{ stove:[…], cupboards:[…] }` inside `overrides.rooms.<role>`.
    The field's name is an implementation choice.
  - **Order.** It applies after `containers` has been resolved, whether
    that list came from the type or from an override.
  - **Placement.** Refs go through `itemsFromRegistry()`, as `items` does
    today.
  - **`spawnRolled`.** A container that receives items starts
    `spawnRolled:true` unless its spec sets `spawnRolled`, the same rule as
    today.
  - **Unknown id.** An id that isn't in the room's container list pushes a
    message onto `buildBuilding()`'s `problems`. It is never silently
    dropped.
  - **`containers` keeps its meaning:** it replaces the list.
- **The home's overrides.** Rewrite them to use the new field: every restated
  container goes, and its items stay.
  - The kitchen's `cooking_pot` with its `dishFrom()` contents is a
    placement ref like any other.
  - Room `desc` and `floor` overrides stay as they are.
- **The BUILDING TYPES schema comment.** Document the new field next to
  `containers`.
- **One stove capacity.** Move `HEAT_CONTAINER_CAPACITY_KG` up into WORLD DATA,
  above `KITCHEN_CONTAINERS`. It keeps its name and its "stove and campfire
  alike" comment. The stove entry reads it.
- Commit as `Phase 3: …`.

## Design decisions to make during implementation

- **The new override field's name** (`items` or `containerItems`, say).
  Recommended: `items`, which matches the container spec's own field. Record
  the pick in the changelog.
- **Where exactly the moved constant sits** within WORLD DATA. Recommended:
  directly above `KITCHEN_CONTAINERS`, its only other reader. Name it in the
  changelog.

## Data / schema changes

- **WORLD DATA:** one new optional field on a building instance's room
  override (Phase 3). No change to the runtime room or container shape.
- **No new or changed state fields. No save-format change.**

## In scope

- [ ] Phase 1: the orphaned block deleted, and its two facts in
      `loadStatusText()`'s comment.
- [ ] Phase 2: the v0.2.1, v0.5.1 and handoff pointers handled as above.
- [ ] Phase 2: every closed-issue `#NN` in a comment gone, its why kept in
      words.
- [ ] Phase 2: open-issue references kept.
- [ ] Phase 2: the rule added to `docs/02-code-practices.md`.
- [ ] Phase 2: `docs/systems/survival.md` written, and
      `docs/systems/README.md`'s index updated.
- [ ] Phase 3: the by-id override field, with a build problem for an unknown
      id.
- [ ] Phase 3: the home rewritten to use it, and the schema comment updated.
- [ ] Phase 3: `HEAT_CONTAINER_CAPACITY_KG` moved and read by the stove.

## Explicitly out of scope

- **A `CONTAINER_KINDS` table** (#128's first proposal). Container ids are
  reused for different containers (`cabinet`, `shelves`, `shelf`).
- **System overview comments** (POWER RUNS and the like). They move to
  `docs/systems/` with the pass that next changes each system.
- **`validateWiring()`'s runtime string naming #258.** #258 rewrites that
  line.
- **Moving figure sources out of comments into `docs/canon/reference/`.**
- **Other landmarks' container overrides.** Their types have no containers of
  their own, so their lists are the only definitions.
- **Adjacent open issues:** #380 and #376 (performance), #258 (the unwired-room
  fallback), and #307, #308, #309 and #325 (building-type passes that will add
  containers).

## Sections touched

- **Phase 1:** RENDERING (comments only).
- **Phase 2:** comments throughout `ashfall.html`, CSS included. Plus
  `docs/02-code-practices.md` and `docs/systems/`.
- **Phase 3:** WORLD DATA (BUILDING TYPES, `landmarkInstances()`,
  `buildBuilding()`) and FIRE / COOKING (the constant's old line).

## Systems docs

- **Read first:** `docs/systems/README.md` (the format) and
  `docs/systems/time.md` (so `survival.md` links to it rather than overlapping
  it).
- **Create:** `docs/systems/survival.md`.
- **Update:** `docs/systems/README.md`'s index.

## Proof of no behaviour change

- **Phases 1 and 2:** `git diff origin/main...HEAD -- ashfall.html` shows
  comment lines only, JavaScript and CSS comments alike.
- **Phase 3:** the world built on `main` and the world built on the branch
  are the same.
  - Put a scratch copy of each version of `ashfall.html` outside the repo,
    never committed, with `makeDefaultWorld` added to `window.ashfallDev`.
  - Load both in headless Chromium, and compare
    `JSON.stringify(makeDefaultWorld())` with every `_uid` stripped (as
    `stateJson()` does) and keys sorted: key order is not behaviour.
  - `validateRoomSchema()` and the build's `problems` report nothing new.
  - The replay CI (`replay_compare.py`) passes.
  - Report the comparison in the pull request.

## Dependencies / issue linkage

- **Fulfils:** `Closes #363`, `Closes #374`, `Closes #128`.
- **Deferred:** nothing is expected to be. If a closed-issue reference turns
  out to carry a why that can't be put in words without new research, keep it
  and file an issue naming it.

## Open questions for Tom

None.
