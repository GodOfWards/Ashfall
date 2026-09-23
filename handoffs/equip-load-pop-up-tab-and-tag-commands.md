# Ashfall Handoff — Equip load delta, pop-up tab guard, wrap-time tag commands

Current shipped version: v0.7.4
Implied version-change type: PATCH (two fixes to `ashfall.html`, no new state; the third part is documentation)
Issues: #203 — Carry load: equipping a bag stowed in a lower-factor worn bag can raise the load past the hard limit
        #201 — The item pop-up acts on the wrong item after a keyboard switch of the Here tab
        #205 — Wrap-time tagging: session hands Tom the tag commands instead of tagging

## What this is

Three tier-0 fixes in one pass, so there is one pull request, one version and one tag:

- **#203.** Equip is checked against the hard limit by what it actually adds to the load, on both sides.
- **#201.** The item pop-up closes whenever its item is no longer on its side's current tab.
- **#205.** A coding session can't tag: Tom pushes tags by hand, and the merge commit doesn't exist until he merges. The session's final message therefore ends with a ready-to-run block that tags the merge commit.

## Relevant existing state

Verified against `main` at v0.7.4. Line numbers are approximate.

- **`doEquip(sourceKind, index)`** (~4404) resolves `src` as `worldSlot(room, worldTab)` or `invSlot(invTab)`. It checks the hard limit only when `sourceKind === "world"`: `playerLoad() + itemUnitWeight(it) * carryFactorOf(it) > CARRY_HARD_LIMIT_KG` logs `"You can't carry any more."` (warn) and returns.
- **`carryFactorOf(thing)`** (~4130) returns a registry `carryFactor` looked up by `itemId`, and 1 for anything without one. The loose inventory (`state.inventory`) and the keychain slot have no `itemId`, so they get 1, and so does any `worldSlot()` result.
- **`playerLoad()`** (~4140) counts the loose inventory in full, and each worn slot as `(unitWeight + contents) × carryFactorOf(slot)`. `itemUnitWeight()` includes a bag's `contents`.
- **Bag factors:** backpack 0.72, fanny pack 0.76, duffel 0.81, purse 0.85, tote 0.85.
- **Two comments disagree with the code today:**
  - The carry-limits comment (~4112) says nothing may add load past the limit and only Unequip can take it there. After this pass that is true again.
  - The comment in `doEquip` (~4409–4411) says "Only a bag picked up from the world adds load… Equipping from the inventory side is never refused on load." That is false today and is rewritten below.
- **`renderItemPop()`** (~6965) resolves `found = findItemByUid(detailItem.uid)` and closes only when `found` is null. `detailItem.side` is `"world"` or `"inv"`.
- **The transfer functions don't use the item's list.** `doTake`, `doStore`, `doConsume`, `doOpen` and `doEquip` each re-resolve their list from the *current* tab, not from `found.list`. That is the bug in #201.
- **`render()`** calls `renderInventoryPanel()` and `renderWorldItemsPanel()` before `renderItemPop()`. Those two reset a vanished `invTab`/`worldTab` first, so both tabs are final by the time the pop-up renders.
- **`findItemByUid()` returns the same arrays the tabs resolve to:** `room.floor`, `c.items`, `bag.contents`, `state.inventory.items`, `state[slot].items`. So comparing by identity works.
- **`doOpen()`** puts the opened unit back into the list it came from and re-points `detailItem` at it. So the guard below leaves it open.
- **Tagging is written in two places:** `CLAUDE.md`, wrap-time checklist item 6 ("After the merge, tag it…"), and `docs/Ashfall_Project_Guide.md` Part 3, coding session ("Tag the merge commit `vX.Y.Z`", ~489). Every PR so far merged as a merge commit titled `Merge pull request #NN from …`.

## Rules / mechanics

### #203 — Equip is refused only when it raises the load past the hard limit

In `doEquip()`, replace the world-only check with one rule for both sides:

```js
const srcFactor = sourceKind === "world" ? 0 : carryFactorOf(src);
const added = itemUnitWeight(it) * (carryFactorOf(it) - srcFactor);
if(added > 0 && playerLoad() + added > CARRY_HARD_LIMIT_KG){
  log("You can't carry any more.", "warn");
  return;
}
```

- **The world side needs its explicit 0.** `carryFactorOf(worldSlot(...))` returns 1, which would be wrong: a bag in the world counts for nothing now.
- **Inventory side:** the loose inventory and the keychain count at 1, and a worn bag at its own factor, all through `carryFactorOf(src)`.
- **`added > 0` is part of the rule.** A player already past the limit (Unequip can do that) may still equip a bag when doing so lowers the load or leaves it unchanged.
- **World-side behavior is unchanged.** With `srcFactor` 0, `added` is exactly today's expression, and every bag has `unitWeight > 0`.
- **Same refusal line, and the Equip button stays offered,** as the world-side refusal already works.
- **Rewrite the `doEquip` comment** to say that. Equipping is refused only when it would raise the load past `CARRY_HARD_LIMIT_KG`. A bag counts at 0 in the world and at its source's factor in the inventory, so a bag in a lower-factor worn bag can add load. Leave the carry-limits comment as is: it is accurate once this ships.

### #201 — The pop-up closes when its item leaves its side's current tab

In `renderItemPop()`, after `found` is resolved, close the pop-up (set `detailItem = null`) when either:

- `found` is null, as today, or
- `found.list` is not the list its side's current tab resolves to, compared with `===`:
  - `side === "world"`: `worldSlot(world[state.currentRoom], worldTab)`. A null slot counts as a mismatch.
  - otherwise: `invSlot(invTab)`. A null slot counts as a mismatch.

This one check covers every way a tab changes:
- a tab-strip click or keypress
- `doOpenContainer()`
- a tab that vanished and fell back to Floor/Inventory
- `doEquip()` setting `invTab`

Resulting behavior:
- **Switching the item's own side's tab closes the pop-up.**
- **Switching the other side's tab leaves it open.** The Take/Place/Store destination follows that tab by design, and the pop-up's label already updates (Place ↔ Store).
- **Pointer use is unchanged:** the backdrop already closes the pop-up before a tab can be tapped.
- **Focus** after the guard closes the pop-up lands wherever a keyboard tab switch already leaves it. That is `<body>` today; fixing it is #206, not this pass.

Update the comment above `renderItemPop()` to add this to its list of close reasons: its tab no longer shows it.

### #205 — The session hands Tom the tag commands

**`CLAUDE.md`, checklist item 6**, becomes: the session does not tag. Its **final message** (not the PR description) ends with this block, with `NN` (the PR number) and `X.Y.Z` (the version) filled in, for Tom to run after merging:

```sh
git fetch origin main
C=$(git log origin/main --merges -1 --format=%H --grep="^Merge pull request #NN from")
if [ -n "$C" ] && git show "$C:ashfall.html" | grep -qF 'VERSION: "X.Y.Z"'; then
  git tag vX.Y.Z "$C" && git push origin vX.Y.Z
else
  echo "Not tagged: PR #NN has no merge commit on main, or it isn't X.Y.Z"
fi
```

It finds the merge commit by PR number and checks that it carries the version *before* tagging, so a wrong tag is never created. The block's safeguards:
- **`[ -n "$C" ]` must stay.** With an empty `$C`, `git show ":ashfall.html"` reads the index and could pass.
- **The trailing ` from`** keeps `#12` from matching `#123`.
- **A squash or rebase merge** finds no merge commit and fails safe, into the `else`.

Keep in item 6:
- why the commit is named explicitly (the `v0.4.4`/`v0.4.5` → #32 history), rewritten as the reason the block resolves the commit instead of using `HEAD`;
- the paragraph after the list ("The merge ships the version…", including a version shipped inside someone else's PR).

Add, where the documentation-only exception says "no tag": **a documentation-only pass sends no tag commands.**

**`docs/Ashfall_Project_Guide.md`, ~489:** "Tag the merge commit `vX.Y.Z`" becomes a pointer. Tom tags the merge commit from the commands the session's final message hands him; `CLAUDE.md`'s checklist item 6 owns the block. The block is written once, in `CLAUDE.md`, never copied into the guide. Line ~305 ("Every shipped version is tagged…") stays: it is still true.

**This pass's own wrap** is the first to use the new item 6. Its final message ends with the block, filled in for this PR and its version.

## Design decisions to make during implementation

- **Wording.** The exact sentences in `CLAUDE.md` item 6, the Project Guide line, and the two code comments are the session's, within the content above. Record them in the changelog's Documentation section.
- **Shell.** The block assumes a POSIX shell (bash, zsh, Git Bash), the same assumption item 6's existing `grep` already makes. That is retunable if Tom tags from somewhere else; no change is needed unless he says so.

## Data / schema changes

None. No state fields, no item or world schema, so `SAVE_KEY` is unchanged.

## In scope

- The `doEquip()` load check and its comment (#203).
- The `renderItemPop()` guard and its comment (#201).
- `CLAUDE.md` item 6 and the documentation-only exception line; `docs/Ashfall_Project_Guide.md` ~489 (#205).
- The `GAME_CONFIG.VERSION` PATCH bump, the changelog entry, and the archive move, per the wrap-time checklist.

## Explicitly out of scope

- **Making the transfer functions act on `found.list`** (#201's option b). The guard makes the pop-up's list and the tab's list the same whenever an action can fire, so the signatures stay as they are.
- **Trapping focus in the pop-up** (#201's option c), which overlaps #78.
- **Focus loss when a tab strip is rebuilt** (#206).
- **Hiding or disabling Equip when it would be refused.** It stays offered and logs a warning, as the world side does today.
- **Any change to Unequip's "always allowed".**
- **#200** (carry limit from the character) and **#152** (parallel handoffs).

## Sections touched

- **ACTIONS:** `doEquip()`, mechanics.
- **RENDERING:** `renderItemPop()`.
- **Documentation:** `CLAUDE.md`, `docs/Ashfall_Project_Guide.md`.
- **No WORLD DATA.**

## UI changes

- Equipping a bag from inside a lower-factor worn bag near 32.5 kg can now fail, with "You can't carry any more."
- Switching a tab on the same side as an open pop-up's item closes the pop-up.
- Nothing else is visible.

## Dependencies / issue linkage

The PR description carries `Closes #201`, `Closes #203` and `Closes #205`. The only known follow-up is #206, which is already filed. Anything else this pass surfaces gets filed at the wrap.

## After implementation

- Open a pull request with the PATCH bump and a new `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`. The entry's `Implements:` field names this handoff by path and records the wording choices above.
- `git mv` this file to `handoffs/archive/`.
- End the final message with the tag block from the new `CLAUDE.md` item 6, filled in.
