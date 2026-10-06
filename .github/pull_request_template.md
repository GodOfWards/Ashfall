<!-- The wrap checklist in docs/03-workflow.md is the rule; this is its layout.
     Delete the lines that don't apply. -->

## What this does

<!-- One or two sentences: the pass's intent. -->

## Issues

Closes #

<!-- One `Closes #NN` line per issue this fulfils. An issue is closed by hand
     only when Tom drops it for good (docs/03-workflow.md, Closing). A pull
     request that only lands a handoff fulfils nothing yet: name its issues
     without `Closes` (e.g. "Specs #242"), or they close before the work
     exists. The coding session's pull request closes them. -->

## Handoff

<!-- `handoffs/<name>.md`, moved to `handoffs/archive/` in this PR; or "None",
     with the spec it was built from (e.g. "Built from #NN's body"). -->

## Version

- [ ] `ashfall.html` changed: `GAME_CONFIG.VERSION` bumped (PATCH / MINOR) and a `CHANGELOG.md` entry added below the marker
- [ ] `ashfall.html` unchanged: no bump, no changelog entry, no tag

## Systems docs

<!-- The `docs/systems/` docs this PR creates or updates, or "None touched". -->

## Deferred

<!-- New issues filed for cut scope or follow-ups (#NN), or "Nothing deferred". -->

## Validation

<!-- How the change was checked: the checks run, and for a "no behavior change"
     claim, `git diff origin/main...HEAD -- ashfall.html`. -->
