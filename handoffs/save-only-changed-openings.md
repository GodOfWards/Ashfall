# Ashfall Handoff — Saves keep only the doors and windows that changed

Current shipped version: v0.10.0
Implied version-change type: PATCH (no new state field; the save format
  stays readable in both directions, see Rules)
Issue: #302 — Saves write every door and window — ~240 KB now that Lima has
  1,732 doors

## What this is

Since the Lima release, rooms save only what differs from their definition
(`savedRoomState()`), but doors and windows still save one entry per id,
whatever its state. #302: "Saving only the doors and windows whose state
differs from their definition's would shrink this to a handful of entries.
`buildDoors()` / `buildWindows()` already fall back to the definition for an
id the save lacks, so the load side needs no change."

## Relevant existing state

Verified against `ashfall.html` at v0.10.0.

- **PERSISTENCE:**
  - `savedDoorState()` writes `{ locked, open, broken }` for every id in
    `doors`.
  - `savedWindowState()` writes `{ state }` for every id in `windows`.
  - `serializeGame()` writes `{ version, state, rooms, doors, windows }`
    with `JSON.stringify(…, null, 2)`.
  - The PERSISTENCE comment above `savedDoorState()` says `doors` and
    `windows` "carry `{ locked, open, broken }` per door and `{ state }` per
    window". That sentence changes.
- **WORLD INTERACTION (doors and windows):**
  - `buildDoors(saved)` starts from `makeDefaultDoors()`, sets `open` and
    `broken` to `false`, applies a saved id's well-typed `locked` / `open` /
    `broken`, then forces `locked = false` where `!doorLocks(d)` and
    `open = false` where `locked`.
  - `buildWindows(saved)` starts from `makeDefaultWindows()` and applies a
    saved id's `state` when it is one of `WINDOW_STATES`.
  - An id the save lacks keeps its definition's state. That is the fallback
    this pass relies on, and neither function changes.
- **The definitions never read `state`.** `makeDefaultDoors()` and
  `makeDefaultWindows()` build from `authoredDoors()` / `authoredWindows()`
  (both `{}`), `expandOpenings(WIRING, WIRING_TEMPLATES)` (`WIRING` is `{}`)
  and `expandBuildings()`. A generated home's locked front door comes from
  `stableHash(id) % 100 < HOME_LOCKED_PCT`, not from `state.seed`. So the
  defaults are the same on every load of every run.
- **What changes a door or window in play:**
  - lock and unlock, by key or by hand;
  - Open and Close;
  - `doForceDoor()` sets `broken = true` and unlocks;
  - `doOpenWindow()`, `doCloseWindow()` and the break action set a window's
    `state`.
- **Measured on v0.10.0, headless Chromium, a new game saved at once:**
  - the save is **243,210 characters**: doors 163,054, windows 55,461,
    `state` 960, `rooms` 956;
  - 1,732 doors, 866 windows;
  - `serializeGame()` takes about 100 ms;
  - `makeDefaultDoors()` plus `makeDefaultWindows()` take about **64 ms**
    together (each runs `expandBuildings()`).

## Rules / mechanics

1. **The baseline is a new game's state.** A door or window is written to
   the save only when its saved fields differ from what `buildDoors(null)` /
   `buildWindows(null)` give that id. Comparing against the output of the
   loader's own fallback, not the raw definitions, is what makes it exact:
   an id left out loads back as precisely that baseline.
2. **Doors:** written when any of `locked`, `open` or `broken` differs from
   the baseline door's. What's written is the full `{ locked, open, broken }`
   triple, not only the fields that differ. That keeps the entry shape the
   one `buildDoors()` already reads.
3. **Windows:** written when `state` differs from the baseline window's, as
   `{ state }`.
4. **Load is unchanged.** `buildDoors()` and `buildWindows()` are not
   edited.
5. **Compatibility:**
   - a v0.10.0 save, which carries every id, loads exactly as before;
   - a save from this version, which carries only changed ids, loads in
     v0.10.0 too, since the missing ids take their definitions.

   No `SAVE_KEY` change, so PATCH.
6. **Known consequence, accepted:** a door or window the player never
   touched isn't in the save, so if a later version changes its default
   (for example, `HOME_LOCKED_PCT` retuned), an old save picks up the new
   default for it. Rooms have worked this way since v0.10.0.
7. **No change to the JSON's formatting.** The indent stays. With openings
   trimmed, a new game's save is on the order of 2 KB, so it no longer
   matters.

## Design decisions to make during implementation

Record the choice in the changelog's Notes / assumptions.

1. **Where the baseline comes from.** Computing `buildDoors(null)` and
   `buildWindows(null)` on every save adds about 64 ms to a save that
   already takes about 100 ms. Options:
   - **(a)** compute the baseline once, lazily, on the first save, and keep
     it for the session: as a map of id to `{ locked, open, broken }` and id
     to `state`, not the door objects themselves. This is safe because the
     definitions never read `state` (above). **Recommended.**
   - **(b)** compute it on every save, as `savedRoomState()` does with
     `makeDefaultWorld()`. Simpler, and slower.
2. **The helpers' names and shape**, for example one
   `openingBaseline()` returning `{ doors, windows }`. It's an
   implementation choice.

## Data / schema changes

- No new state field, item field or room field.
- The save's `doors` and `windows` objects change meaning from "every id"
  to "the ids that differ from a new game". Their entry shapes are
  unchanged.

## In scope

- `savedDoorState()` and `savedWindowState()` write only the entries that
  differ from the baseline (Rules 1–3).
- The baseline helper (Design decision 1).
- The PERSISTENCE comment and the DOOR / WINDOW SCHEMA comments that
  describe what a save carries: `doors` and `windows` hold only the ids
  whose state differs from a new game's.

## Explicitly out of scope

- `buildDoors()`, `buildWindows()`, `applyLoadedData()`,
  `validateLoadedWorld()`: unchanged.
- The JSON's indentation.
- The cost of `savedRoomState()`'s own `makeDefaultWorld()` per save. It's
  the rest of the ~100 ms, and it isn't part of #302. If it's worth a pass,
  file it.
- Power state (`state.power`), which the wiring passes will grow (#306 notes
  that its switch and breaker states should also save only what differs).
  That's a separate issue when it matters.

## Sections touched

PERSISTENCE only, plus the schema comments in WORLD DATA that describe the
save. Mechanics-neutral: no player-facing change.

## UI changes

None.

## Validation

In headless Chromium, as the Lima release did:
1. A new game's save is a few KB (report the figure), and its `doors` and
   `windows` objects are empty.
2. **Round trip.** On one seed:
   - unlock the home's front door by hand;
   - open a closed door;
   - draw the back door's bolt;
   - force a locked generated home's front door;
   - open one window and break another.

   Save, reload, and compare every door's `{ locked, open, broken }` and
   every window's `state` with the values before saving: all equal. Also
   compare them with `buildDoors(null)` / `buildWindows(null)` to show that
   exactly the changed ids were written.
3. **Old saves.** A save exported from v0.10.0 (every id) imports and gives
   the same door and window states as it did under v0.10.0.
4. **The reverse.** A save written by this build, imported into v0.10.0
   (the `main` before this branch), loads with the same states.
5. Save time, before and after (report both).
6. `git diff origin/main...HEAD -- ashfall.html` shows only PERSISTENCE and
   the comments named above.

## Dependencies / issue linkage

Fulfils #302. Nothing else depends on it.

## Open questions for Tom

None.

## After implementation

Open a pull request carrying the version bump (PATCH) and a new
`CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, citing
`handoffs/save-only-changed-openings.md`, recording Design decision 1, and
saying `Closes #302`. Move this handoff to `handoffs/archive/` in the same
pull request.
