# Ashfall Handoff — Door labels named by the far side

Current shipped version: v0.5.3
Implied version-change type: PATCH
Issue: #136 — DOOR_LABELS names a door by its destination, but a door has two sides

## What this is

`DOOR_LABELS` gives each door one name, and both readers render it as *where the
door leads*. A door has two sides, so the name is only correct from one of them:
standing in apartment 2A with the door locked, the Here panel reads **"The door to
2A is locked."**

This pass deletes `DOOR_LABELS` and derives the name from the side of the door the
player is *not* on. #136's option 1, chosen because — in the issue's own words —
it "removes `DOOR_LABELS` as a hand-maintained table, which is the one-source-of-truth
shape the project prefers", and because it is the only one of the three that also
settles the master-key case below.

## Relevant existing state

Read from `ashfall.html` at v0.5.3. Three facts in #136's body are wrong or
incomplete against the current file; the corrected versions are what this handoff
specs against.

### The table and its three readers

```js
// WORLD DATA, line 1253
const DOOR_LABELS = { "2a":"2A", "2b":"2B", "1a":"1A", "1b":"1B", "1a-patio":"the patio" };
```

**#136 says "the two call sites". There are three.** Two are in `renderHereActionsPanel()`
(RENDERING) and one is in `getItemActions()` (INVENTORY / ITEM SYSTEM — item-detail
action list), which #136 missed:

```js
// getItemActions(), line 4153 — the master-key branch
const label = (doors[doorId].locked ? "Unlock " : "Lock ") + (DOOR_LABELS[doorId] || doorId);

// renderHereActionsPanel(), line 6041 and its two uses
const label = DOOR_LABELS[doorId] || doorId;
...
hereBox.appendChild(actionButton(`Unlock the door to ${label}`, ()=> doToggleLock(doorId)));
...
hereBox.appendChild(hereNote(`The door to ${label} is locked.`));
```

A fourth site names no door at all — `getItemActions()`'s non-master branch, for a
key with a `doorId` (today only `acorn_apt_2a_key`):

```js
// line 4157
actions.push({ label: doors[it.doorId].locked ? "Unlock" : "Lock", onClick:()=>doToggleLock(it.doorId) });
```

### The doors

```js
// WORLD DATA, makeDefaultDoors(), line 1239
"2a":        { locked:false, sides:["hallway2","living"],     building:"acorn" },
"2b":        { locked:true,  sides:["hallway2","twobee"],     building:"acorn" },
"1a":        { locked:true,  sides:["hallway1","onea"],       building:"acorn" },
"1b":        { locked:true,  sides:["hallway1","onebee"],     building:"acorn" },
"1a-patio":  { locked:true,  sides:["onea_patio","onea"],     building:"acorn" }
```

`sides` always holds exactly two room ids. `doorsForRoom(roomId)` returns every door
whose `sides` includes that room — so the near room is always one of the two, at every
site that calls it. All three label readers are inside a `doorsForRoom()` loop or
guarded by `sides.includes(state.currentRoom)`, so the helper below can rely on that.

### The `area` / `room` fields of the seven door-side rooms

Every one has a non-null `area`. Only `onebee` has a null `room`.

| room | `area` | `room` |
|---|---|---|
| `hallway1` | `"1st Floor"` | `"Hallway"` |
| `hallway2` | `"2nd Floor"` | `"Hallway"` |
| `living` | `"2A"` | `"Living Room"` |
| `twobee` | `"2B"` | `"Living Room"` |
| `onea` | `"1A"` | `"Living Room"` |
| `onebee` | `"1B"` | `null` |
| `onea_patio` | `"1A"` | `"Patio"` |

**`area` alone is not enough, and `room` alone is not enough.** `"1a-patio"`'s two
sides — `onea` and `onea_patio` — share the area `"1A"`, so naming by `area` reproduces
#136's exact bug on the patio door. Naming by `room` collides in `hallway2`, where
doors `"2a"` and `"2b"` both lead to a `"Living Room"`. The rule below is the
composition that survives both.

### The master-key duplicate, which is reachable today

`getItemActions()` pushes one action per door in `doorsForRoom()`. Standing in `onea`
with the master key, that is two doors — `"1a"` and `"1a-patio"` — and under a naive
by-far-side rule keyed on `area` both resolve to `"1A"`, giving two identical buttons.
#136 calls this "not reachable today"; **it is reachable today**, because v0.5.2 opened
the alley gate and the patio is a day-one route into `onea`. v0.5.2 worked around it by
hand-writing `"the patio"`; this pass removes the need for the workaround.

### Save compatibility

`DOOR_LABELS` is a module `const` and is never serialized. `doors` is serialized
wholesale, and a v0.5.1 save has no `"1a-patio"` entry at all (v0.5.2's changelog
records this) — which is fine, since the helper only ever runs for doors that exist in
`doors`. No save field is added, read or changed.

## Rules / mechanics

### The helper

One new function, `doorLabel(doorId, fromRoomId)`, in **WORLD INTERACTION**, beside
`doorsForRoom()` and `findKeyForDoor()` — it is a world query, and it has readers in two
different ARCHITECTURE sections, so it belongs in neither of them.

```
doorLabel(doorId, fromRoomId):
  1. far = the entry of doors[doorId].sides that is not fromRoomId.
     If fromRoomId is not in sides, or far does not resolve in world, return doorId.
  2. If world[far].area and world[far].area !== world[fromRoomId].area
        -> return world[far].area verbatim.
  3. Else if world[far].room
        -> return world[far].room.toLowerCase().
  4. Else if world[far].area
        -> return world[far].area verbatim.
  5. Else return doorId.
```

Step 2 is the ordinary case: the far side is in a different unit, so the unit names it.
Step 3 is the same-unit case: the two sides are both inside 1A, so the *room* is what
distinguishes them. Steps 1, 4 and 5 are fail-safes that no current door reaches.

Case is deliberate and asymmetric: an `area` is a proper name and keeps its capitals
(`"2A"`, `"2nd Floor"`); a `room` is a common noun and is lowercased (`"patio"`,
`"living room"`). The template below supplies no article, so neither needs one.

### The template

The sentence changes shape, and this is not cosmetic — it is what makes the derivation
work. `"The door to 2A is locked."` cannot take `"2nd Floor"` or `"patio"` without an
article, and which strings need one is not a property the data carries. Moving the name
in front of "door" removes the article from the sentence entirely:

| | before | after |
|---|---|---|
| locked note | `The door to 2A is locked.` | `The 2A door is locked.` |
| unlock button (Here) | `Unlock the door to 2A` | `Unlock the 2A door` |
| master key (detail) | `Unlock 2A` / `Lock 2A` | `Unlock the 2A door` / `Lock the 2A door` |
| single key (detail) | `Unlock` / `Lock` | `Unlock the 2A door` / `Lock the 2A door` |

This is #136's option 3 wording, adopted here as the carrier for option 1's derivation
rather than as an alternative to it. The issue already endorses it: it "works from both
sides and loses nothing the current wording provides".

The Here panel's unlock button and the master key's now produce the **same string**,
where today they differ (`Unlock the door to 2A` against `Unlock 2A`). That is
intended — they are the same action offered in two panels, and they should read alike.

### Every label this produces

All ten sides of all five doors, which is the full space. No two doors in one room
collide.

| standing in | door | far side | rule | label | note reads |
|---|---|---|---|---|---|
| `hallway2` | `2a` | `living` | 2 | `2A` | The 2A door is locked. |
| `living` | `2a` | `hallway2` | 2 | `2nd Floor` | The 2nd Floor door is locked. |
| `hallway2` | `2b` | `twobee` | 2 | `2B` | The 2B door is locked. |
| `twobee` | `2b` | `hallway2` | 2 | `2nd Floor` | The 2nd Floor door is locked. |
| `hallway1` | `1a` | `onea` | 2 | `1A` | The 1A door is locked. |
| `onea` | `1a` | `hallway1` | 2 | `1st Floor` | The 1st Floor door is locked. |
| `hallway1` | `1b` | `onebee` | 2 | `1B` | The 1B door is locked. |
| `onebee` | `1b` | `hallway1` | 2 | `1st Floor` | The 1st Floor door is locked. |
| `onea` | `1a-patio` | `onea_patio` | 3 | `patio` | The patio door is locked. |
| `onea_patio` | `1a-patio` | `onea` | 3 | `living room` | The living room door is locked. |

In `onea`, the two doors now read `1st Floor` and `patio` — distinct, which is the
master-key duplicate resolved.

### The one flagged cost

`"2nd Floor"` / `"1st Floor"` replaces what a hand-written table would have called
`"the hallway"`, in the four inside-an-apartment-looking-out cases. It is accurate —
from inside 2A the door does lead to the 2nd floor — and it is the price of deriving
rather than tabulating. **Retunable**, and the fallback if it reads wrong in play is
documented under Design decisions below rather than left to be rediscovered.

## Design decisions to make during implementation

1. **Helper name and signature.** `doorLabel(doorId, fromRoomId)` is the recommended
   default. Argument order matters only for consistency with `doorsForRoom(roomId)`
   nearby; either order is fine if the other reads better at the call sites. Record the
   choice in the changelog's Notes/assumptions.

2. **Where the `|| doorId` fallback lives.** Both current readers write it at the call
   site. The recommended default is to absorb it into the helper (steps 1 and 5 above)
   so no caller repeats it. If the coding session finds a reason to keep it at the call
   sites, say so in the changelog.

3. **Not a decision: the prose fallback.** If `"2nd Floor"` reads wrong, the fix is a
   room-first variant of step 2 with collision detection per room, which needs a
   different helper shape (`doorLabels(roomId)` returning a map). That is a **new
   planning question for Tom, not an implementation choice** — do not build it in this
   pass. File it if play says the wording is wrong.

## Data / schema changes

**None.** No state field, no item schema field, no room/container/exit schema field.
`DOOR_LABELS` is deleted, which is the removal of a WORLD DATA table, not a schema
change — no room, door, exit or item definition is touched. `doors[].sides`,
`doors[].building`, `doors[].locked` and `findKeyForDoor()` are all unchanged, as #136
says they should be under every option.

`SAVE_KEY` stays `ashfall_save_v0.5`. `versionCompat()` does not move.

## In scope

- Delete `DOOR_LABELS` (line 1253) and its comment.
- Add `doorLabel(doorId, fromRoomId)` to WORLD INTERACTION.
- Rewrite the two `renderHereActionsPanel()` strings to the new template.
- Rewrite `getItemActions()`'s master-key branch label to the new template.
- Give `getItemActions()`'s **non-master key branch** the same label. Today it renders a
  bare `Unlock` / `Lock` with no object. This is beyond #136's literal text and is
  included deliberately: it is the same sentence in the same panel, and a pass that
  fixes door wording everywhere except one button leaves an inconsistency someone files
  next week. One line.
- A comment on `doorLabel()` recording why the composition is `area`-then-`room` and not
  either alone — the `"1a-patio"` shared-area case and the `hallway2` shared-room case
  are the two facts that make it non-obvious, and neither is visible from the function
  body. This is the "invariants code can't state" case the Project Guide keeps comments
  for.

## Explicitly out of scope

- **#142** — `doors[].sides` and the exits carrying `doorId` disagree. Filed from this
  same planning session. 2A's front door gates only one way, and six rooms lose an exit
  with no note at all. That issue is about **whether the note appears**; this pass is
  only about **what it says**. They can ship independently, in either order. Change no
  `doorId` and no `sides` entry in this pass.
- **#141** — three outdoor rooms marked `shelter:"full"`. Also filed from this session.
  Touches `onea_patio`, which this pass reads, but `shelter` and door labels have
  nothing to do with each other. Change no `shelter` value.
- **#89** — `room.building` duplicating `BUILDINGS[].name`. The helper reads `area` and
  `room`, never `building`, so it neither helps nor hinders this.
- **#29** — the log's size and entry cap. Tier-1 and it came up in the same session, but
  it is blocked on a play session by its own terms.
- **#78** — the accessibility pass. No ARIA, no roles, no focus handling. `hereNote()`
  and `actionButton()` are used exactly as they are.
- No new door, no new key, no change to `makeDefaultDoors()` or `DOOR_LABELS`' five
  door ids. No exit label changes — `"Enter apartment 2A"`, `"Leave 2B"` and the rest
  are untouched.

## Sections touched

- **WORLD DATA** — deleting `DOOR_LABELS` and its comment. Nothing else.
- **WORLD INTERACTION** — the new `doorLabel()` helper, beside `doorsForRoom()` and
  `findKeyForDoor()`.
- **INVENTORY / ITEM SYSTEM — item-detail action list** — `getItemActions()`, both key
  branches.
- **RENDERING** — `renderHereActionsPanel()`, the unlock button and the locked note.
- **CONFIG / CONSTANTS** — `GAME_CONFIG.VERSION` only.

Untouched: PLAYER STATE, CORE UTILITIES, the rest of INVENTORY / ITEM SYSTEM,
SURVIVAL / TIME SIMULATION, STAMINA / FATIGUE, CRAFTING, FIRE / COOKING, PERSISTENCE,
EVENTS, RENDERING / MAP, and the document `<style>` and `<body>` blocks.

## UI changes

Four strings, listed in the template table above. No new button, no button removed, no
panel or layout change. A player who never locks a door from the inside sees only the
re-wording: `The 2A door is locked.` where it used to say `The door to 2A is locked.`

The behaviour change a player can actually notice is that the label is now correct from
inside — `The 1st Floor door is locked.` standing in 1A, where it used to say
`The door to 1A is locked.` — and that the two doors of `onea` no longer offer two
identical master-key buttons.

All four strings are functional UI text, held to clarity rather than to the game's
descriptive tone, and all four are retunable.

## Dependencies / issue linkage

- **Fulfils #136.** The pull request carries `Closes #136`.
- **Unblocks nothing** and is blocked by nothing. #142 and #141 are independent.
- **Nothing is expected to be deferred.** Everything this pass cuts is already an open
  issue and is named under *Explicitly out of scope*. If the coding session surfaces
  something new, it files it and references it in the pull request; if it surfaces
  nothing, the changelog's Documentation section says so, per the wrap-time checklist.

### Validation the coding session should perform

- `grep -c DOOR_LABELS ashfall.html` → **0**.
- `git diff origin/main...HEAD -- ashfall.html`, mapped hunk by hunk to the five sections
  above. Diff against `origin/main`, not `main` — at the time of writing the local `main`
  ref in a fresh clone can sit behind.
- `node --check` on the extracted script body.
- `ashfallDev.validateRoomSchema()`, `validateLocations()`, `validateItemRegistry()` and
  `validateReachability()` all still report as they do at v0.5.3 — this pass changes no
  world data, so all four must be byte-identical in output.
- In a browser, **all ten rows of the label table above**. Every one is reachable:
  `"2a"` locks from either side with `acorn_apt_2a_key`; `"2b"` and `"1b"` are lockable
  from inside via the master key after entering through the transom and alley windows
  respectively; `"1a"` and `"1a-patio"` are reachable from inside via the alley gate and
  the patio. Check the locked note, the unlock button, and — with the master key —
  that `onea` shows two buttons with **different** labels.
- A save written by the v0.5.3 build loads under `ashfall_save_v0.5` with no version
  warning, and its doors label correctly. A v0.5.1 save, which has no `"1a-patio"`
  door, must not produce an error anywhere near `doorLabel()`.

## Open questions for Tom

**None.** The one genuinely open call — which of #136's three shapes — was settled during
this planning session as option 1, label by the far side. The template change to
`"The <label> door is locked."` is a consequence of that choice rather than a separate
question: the derivation produces strings that the old template cannot take without an
article, and the data carries no fact saying which ones need one. It is flagged in
*Rules / mechanics* and in *UI changes* so it reads as a decision rather than as drift.

## After implementation

Open a pull request carrying the `GAME_CONFIG.VERSION` bump (PATCH) and a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, naming this handoff by the path it
was read at, recording the two *Design decisions* resolutions above, and closing the
issue with `Closes #136`. Move this file to `handoffs/archive/` with `git mv` in the same
pull request, filename unchanged. Tag the merge commit, naming it explicitly.
