# Ashfall Handoff — `shelter` corrected on five rooms, and `partial` put to use

Current shipped version: v0.5.4
Implied version-change type: PATCH
Issue: #141 — Five rooms carry the wrong `shelter` value

## What this is

`shelter` records whether a room is under cover. Five rooms record the wrong
thing: three outdoor rooms are marked `"full"`, and two street nodes with
described overhead cover are marked `"none"`. Nothing reads the field yet, so
nothing is visibly broken — which is exactly why it is worth fixing before #58
or #6 inherits it.

This pass also puts `"partial"` into service for the first time. It has been a
reserved third value since the field shipped, on the grounds that classifying
partial rooms was content for whichever pass gave `shelter` a consumer; that is
the position this pass overturns. Two balconies and two covered street nodes are
partial, they are identifiable from their own descriptions, and waiting does not
make them easier to classify.

**This is a content pass.** WORLD DATA and the schema comment that describes the
field, and nothing else — no mechanic, no rendering, no state.

## Relevant existing state

Verified against `ashfall.html` at v0.5.4.

`shelter` is `"none"` on **178** rooms and `"full"` on **40**. No room carries
`"partial"`.

The five rooms, at their current lines:

| room | line | now | description as authored |
|---|---|---|---|
| `balcony` (2A) | 1341 | `"full"` | "A narrow concrete ledge overlooking the street below. A dead plant sits in the corner, and a rusted fire escape ladder leads down." |
| `twobee_balcony` (2B) | 1429 | `"full"` | "A narrow balcony, mirroring yours. No fire escape here — just a view of the street." |
| `onea_patio` (1A) | 1527 | `"full"` | "A small concrete patio out back, low fence, a gate leading to the alley." |
| `mill2nd` | 2077 | `"none"` | "Mill and 2nd, under a conveyor bridge that crosses overhead from one building to another." |
| `mid_cedar_1_2` | 2244 | `"none"` | "A block of Cedar with a bus shelter in it. The route map inside has faded to a blank rectangle." |

`mill2nd` and `mid_cedar_1_2` are the only two of the 178 `"none"` rooms whose
description puts anything over the player's head. Four near-misses were checked
and deliberately left alone, and should stay left alone:

- `dock3rd` — "shipping containers stacked three high make the corner feel like
  a hallway": walls, not a roof.
- `main7th` — a gas station *on* the corner; its forecourt canopy is not
  described, and the room is the intersection.
- `mid_main_3_5` — the cinderblock garage is `auto_shop`, a separate room the
  player enters.
- `storage` — `"full"` and **correct**: its exit reads "Back outside", which
  places the player inside the facility rather than in a drive aisle.

**`cannotHaveFire` is currently coextensive with `shelter:"full"`** — 40 rooms
each, with no room in one set and not the other. That is the correlation the
ROOM SCHEMA comment warns must never be relied on, and this pass is the content
that breaks it. See rule 3.

`validateRoomSchema()` (5054–5066) already accepts `"partial"`:
`const legalShelter = ["none", "partial", "full"];`. It needs **no change**, and
it would not have caught any of these five — it checks that the value is legal,
not that it is right.

## Rules / mechanics

No mechanic. Three data changes.

### 1. The five values

| room | line | from | to |
|---|---|---|---|
| `balcony` (2A) | 1341 | `"full"` | `"partial"` |
| `twobee_balcony` (2B) | 1429 | `"full"` | `"partial"` |
| `onea_patio` (1A) | 1527 | `"full"` | `"none"` |
| `mill2nd` | 2077 | `"none"` | `"partial"` |
| `mid_cedar_1_2` | 2244 | `"none"` | `"partial"` |

Five single-token edits. Change nothing else on those lines and no other room.

### 2. Why each one, so the classification is reviewable

- **Both balconies → `"partial"`.** A top-floor balcony sits under the
  building's roof overhang, and a narrow concrete ledge recessed into a facade
  is enclosed on three sides. That is cover without enclosure, which is what
  `partial` is for — the schema's own gloss is "a covered porch, an open garage,
  a doorway". #141 originally argued both were `"none"` on the grounds that
  Acorn has no third storey above them; that test was judged too strict during
  planning, since it is the roof, not another flat, that covers a top-floor
  balcony. The two balconies get the same value: they are described as
  mirroring each other, and nothing distinguishes them.
- **`onea_patio` → `"none"`.** "Out back, low fence, a gate leading to the
  alley" describes nothing overhead at all. This is the one of the three that
  #141's reasoning gets right.
- **`mill2nd` → `"partial"`.** The description puts the room explicitly *under*
  a conveyor bridge. It is the least arguable of the five.
- **`mid_cedar_1_2` → `"partial"`.** A bus shelter is a partial shelter by
  construction. The shelter is an object within a 100 m block rather than the
  whole block, so this is the loosest of the four `partial` calls — at room
  granularity, standing at the node means being able to stand in it.

### 3. The ROOM SCHEMA comment

The `shelter` entry in the ROOM SCHEMA block (the `//   shelter` lines, directly
above `//   desc`) contains three statements this pass makes false:

1. the type line reads `"none" | "full"`;
2. `"partial"` is described as reserved, with "no room uses it yet, because
   classifying which rooms are genuinely partial is content for the pass that
   gives shelter its first consumer";
3. `cannotHaveFire` and `shelter` are said to "happen to be coextensive in the
   current content", with content that breaks the correlation "already specced".

All three must be corrected. After this pass the divergence runs **both ways**,
and that is the fact most worth writing down, because it is what stops a future
reader deriving one field from the other:

- three rooms carry `cannotHaveFire` without being fully under cover — the two
  balconies and the 1A patio;
- two rooms are partly covered and can still host a fire — `mill2nd` and
  `mid_cedar_1_2`, neither of which carries `cannotHaveFire`.

Replacement text, to adapt to the block's wrapping rather than transcribe
literally:

```
//   shelter       "none" | "partial" | "full" — whether the room is under
//                 cover. Required on every room. "partial" is cover without
//                 enclosure: a balcony under the building's roof overhang, a
//                 street node under a conveyor bridge, a block with a bus
//                 shelter in it. Nothing reads shelter today — it is laid down
//                 ahead of its consumers (#58 weather, #6 rooftops) the same
//                 way LOCATIONS' z is, so those passes need no retrofit across
//                 every room. An unused field here is not a dead one. It is
//                 also NOT cannotHaveFire and must never be derived from it:
//                 the two are not coextensive, and the divergence runs both
//                 ways — the two balconies and the 1A patio carry
//                 cannotHaveFire without being fully under cover, and the two
//                 partial street nodes are covered and can still host a fire.
//                 They are different facts, a fire rule against being under
//                 cover. The pass that adds the first consumer also inherits
//                 shelter's save backfill — backfillRoomAddresses()
//                 deliberately does not restore it, since nothing reads it.
```

Note what is deliberately **not** in it: no version number and no handoff name.
Per the Project Guide, a comment carries what is true now; when it arrived is
the changelog's job.

## Design decisions to make during implementation

Only one, and it is narrow: the exact line-wrapping and phrasing of the schema
comment above. Keep every statement it makes, drop none of the surviving ones —
in particular the "laid down ahead of its consumers" paragraph and the
`backfillRoomAddresses()` sentence are both still true and both still earn their
place. Record nothing unless you depart from the text above.

## Data / schema changes

- **Room schema:** no new field. `shelter`'s documented value set goes from two
  values in the comment to the three the code has always accepted — the comment
  catches up with `validateRoomSchema()`, rather than the other way round.
- **No state field, no item schema change, no container or exit change.**
- **No save migration.** `backfillRoomAddresses()` deliberately does not restore
  `shelter`, and should not start: nothing reads the field, so an old save whose
  rooms lack it is no worse off than one carrying the old value. A loaded save
  keeps whatever `shelter` it was written with — including the wrong values —
  and that is acceptable precisely because nothing consumes them. The pass that
  gives `shelter` a consumer inherits the backfill question, as the schema
  comment already says.

## In scope

- The five `shelter` values in rule 1, in `buildAcornApartments()` (three),
  `buildMillSt()` (one) and `buildCedarSt()` (one).
- The ROOM SCHEMA comment per rule 3.
- `GAME_CONFIG.VERSION` bumped (PATCH), changelog entry, handoff archived.

## Explicitly out of scope

- **Every other room's `shelter` value.** A full sweep of all 218 was considered
  during planning and declined: the remaining 213 are plainly right, and a
  re-read of every description is a content session of its own rather than a
  five-line correction. If the coding session spots a sixth room it believes is
  wrong, **file an issue — do not fix it here.**
- **Room descriptions.** No `desc` string changes. The classifications above are
  read *from* the descriptions as authored; rewriting a description to justify a
  value would be reasoning backwards.
- **`cannotHaveFire`.** No room gains or loses it. The correlation breaking is
  the point, not a thing to repair.
- **`validateRoomSchema()`** — already accepts `"partial"`; no validator change,
  and no new validator. That a value is *correct* is not a shape a validator can
  check, which is why this was found by reading.
- **#58** (weather) and **#6** (rooftops) — the eventual consumers. This pass
  gives them correct data to inherit and builds nothing on top of it.
- **#142** — the locked-door note. Sibling handoff from the same planning
  session (`handoffs/locked-door-note-from-exits.md`), rendering-side only. The
  two touch no common line and can ship in either order.
- **#89** (`room.building` duplicating `BUILDINGS[].name`) — a different room
  field, untouched.

## Sections touched

- **WORLD DATA** — five `shelter` values and the ROOM SCHEMA comment. Nothing
  else.
- **CONFIG / CONSTANTS** — `GAME_CONFIG.VERSION`.

Content-only: every other section can be skipped. No mechanic, no rendering, no
persistence.

## UI changes

**None.** Nothing reads `shelter`, so the player sees no difference of any kind.

## Dependencies / issue linkage

- Fulfils **#141** in full, as edited during the planning session that produced
  this handoff. `Closes #141` in the pull request.
- Nothing is expected to be deferred. If a sixth mis-classified room turns up,
  file it and reference it in the pull request; if nothing does, say so in the
  changelog's Documentation section.

## Verifying it

This pass cannot be validated by playing — nothing reads the field. It is
verified by reading and by counting:

- `git diff origin/main...HEAD -- ashfall.html` should show exactly six hunks:
  five one-token `shelter` edits, the schema comment, and the version constant.
  Nothing else in the file.
- `node --check` on the extracted script body.
- Counts after the change: `shelter:"full"` **37**, `shelter:"partial"` **4**,
  `shelter:"none"` **177**. They must total 218, and `cannotHaveFire` must still
  be **40** — unchanged, and no longer equal to the `"full"` count, which is the
  correlation breaking as intended.
- `ashfallDev.validateRoomSchema()` reports no problems — every room still has
  an address and a legal shelter.
- `validateLocations()`, `validateItemRegistry()` and `validateReachability()`
  against a v0.5.4 build and this one, diffed: **identical output**. None of them
  reads `shelter`, so any difference means something else moved.
- A save written by the v0.5.4 build loads under `ashfall_save_v0.5` with no
  version warning. No state field is added, read or changed; `versionCompat()`
  does not move.

## After implementation

Open a pull request carrying the version bump and a new `CHANGELOG.md` entry per
`docs/CHANGELOG_GUIDE.md`, naming this handoff by the path it was read at, and
closing #141 with `Closes #141`. The entry's **New content** section is where
the five values belong, per the changelog guide's content/mechanics split. Move
this file to `handoffs/archive/` with `git mv` in the same pull request.
