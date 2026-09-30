# 04 — Handoff template

Copy this for every new handoff. How a handoff is written, landed, named and
archived is `03-workflow.md`'s. Every section has one goal: leave nothing for
the coding session to decide that Tom should have been asked about.

```markdown
# Ashfall Handoff — <Feature / System Name>

Current shipped version: vX.Y.Z
Implied version-change type: PATCH | MINOR | None — documentation only
  (mark "tentative" if it depends on a decision below, and say which option
  keeps it PATCH)
Issue: #NN — <name>

## What this is
One or two sentences: what this specs, and why now. Quote the issue's scope
wording if it's short; it anchors everything below.

## Relevant existing state
What the code already has that this builds on or must account for, verified
by reading the current `ashfall.html`, never recalled. Any canon fact or
reference figure the work depends on is quoted here, with its source: the
coding session reads neither.

## Rules / mechanics
The spec, for everything settled in planning: exact formulas, thresholds,
constants and edge cases, precise enough that nothing is inferred.

## Design decisions to make during implementation
Optional. Only genuinely narrow implementation calls (a data-structure shape,
which of two equally simple renderings). For each: the options, a recommended
default, and the requirement to record the pick in the changelog. If a choice
would change the version type, say so.

## Data / schema changes
- New or changed state fields (PLAYER STATE).
- New or changed item schema fields, tags or categories.
- New or changed room, container or exit schema fields (WORLD DATA).

## Costs
For a new system or a change to a per-minute one: what it adds per game minute
and per event, and how it avoids checking the whole world every minute
(`02-code-practices.md`, Performance). Omit for content and UI.

## In scope
What this pass covers, concretely enough to check off.

## Explicitly out of scope
What was discussed and deliberately deferred, and adjacent open issues that
look related but aren't touched. This matters as much as the scope.

## Sections touched
The ARCHITECTURE sections this implicates. If it is content only, say so: the
coding session can skip everything else.

## Systems docs
The `docs/systems/` docs to read before starting, and the ones this pass must
create or update in the same pull request.

## UI changes
What the player sees or does differently: buttons, panels, readouts, wording.
Omit if none.

## Dependencies / issue linkage
Which issues this fulfils or unblocks. Flag anything this pass is expected to
leave deferred: the coding session files it at the wrap.

## Open questions for Tom
Only real scope or design calls not resolved in planning. If this section is
not empty, the handoff is not ready to build from, and says so.
```
