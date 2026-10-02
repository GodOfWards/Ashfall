# Ashfall Handoff — Street surfaces by quarter, Calle 42, and stop text that fits them

Current shipped version: v0.12.1
Implied version-change type: PATCH
Issue: #343 — Street surfaces by quarter — paved in the north-west and south-east, dirt in the north-east and south-west

## What this is

The town's street surfaces were laid down from a satellite estimate. Tom's
Street View survey replaces it: "The town is four quarters", paved in the
north-west and south-east, mostly dirt in the north-east and south-west. This
pass rewrites `LIMA_LINKS`' surfaces and `LIMA_STOPS`' types to match, names
Calle 42, and rewrites the paved and dirt stop text so it holds across whole
quarters.

It is WORLD DATA and text only. Its point beyond the text is #300 (the water
network, designed), which will read a home's street surface to decide whether
it is on the town's network. So the surfaces must be right before #300 is
built.

## Relevant existing state

Verified against `main` at v0.12.1. Line numbers are approximate; find code by
identifier.

- **`LIMA_STREET_CODES`** (~1736): `code = name` lines. `sn = unnamed`. Codes
  this pass names all exist: `cbar` (Camino a Baradero), `cp01` (Camino
  Provincial Secundario 038-01), `c2`, `c14`, `c15`, `c16`, `c17`, `c44`,
  `c46`, `c50`, `c107`, `c109`, `c111`, `dg4` (Diagonal 4). **There is no
  `c42`.**
- **`LIMA_STOPS`** (~1802): `id u v type kind streets [flags]`. Type is one of
  `core`, `gravel`, `dirt`, `barrio`, `rural`, `rail`, `station`. Kind: `c`
  corner, `m` mid, `r` rural, `t` rail, `s` station. A mid's streets field is
  `street:crossA,crossB`; a corner's is codes joined by `+`.
- **`LIMA_LINKS`** (~2581): `a b street surface`, surface `p`, `g`, `d` or `r`
  (railway). Its comment says "Only `r` is read today (the map's rail); the
  rest is laid down ahead of a consumer." That stays true after this pass;
  #300 will be the first reader.
- **Stop text:** `stopDesc()` returns `LIMA_STOP_TEXT[stop.id]` when there is
  one, else a variant of `STOP_TEXT[stop.type][corner|mid]`, picked by
  `stableHash(stop.id) % count`. The hand-written `LIMA_STOP_TEXT` entries
  name no surface except two rural stops, which this pass doesn't touch.
- **`STOP_TEXT`** (~3642) and the comment above it, which says the texts are
  "true of every stop of its type: paved around the plaza, on the main axis
  and along the railway; mostly gravel (ripio) elsewhere; dirt where the town
  meets the fields; the Barrio Atucha's lanes".
- **Addresses:** a generated casa's address is `streetName(s.street)`
  (`generatedHomes()`), so a mid stop's street code is what the player reads.
- **Stop ids are room ids**, and saves key on them. This pass changes no id.

**The facts this rests on** (`docs/canon/reference/Lima.md`, "Streets and
surfaces", Tom first-hand from Street View, March 2026; quoted because the
coding session doesn't read the reference folder):

- The railway splits north from south; Calle 111 splits east from west in the
  north, Calle 15 / Calle 17 in the south.
- **North-west: all paved, Calle 111 included.** The Barrio Atucha's row
  houses are here.
- **North-east: mostly dirt.** Paved: the Camino a Baradero, the Camino
  Provincial Secundario 038-01, the roads alongside the railway, and Calle 50.
  Gravel: Calles 42, 44, 46 and 109.
- **South-west (Calle 17 and west): mostly dirt**, little gravel. **Calle 14
  is paved all along.**
- **South-east (Calle 15 and east): all paved**, and so is the strip on
  Calle 16 between Calles 15 and 17.
- The Barrio Atucha's "streets are paved and on the network".
- The town's character, for the text: low houses and tree-lined streets;
  most homes have bars on their windows; a roof water tank on every house
  outside the Barrio Atucha.

## Rules / mechanics

None. This is a one-off rewrite of data. How it is produced (by hand, or a
throwaway script whose output is pasted in) is the coding session's choice;
no code that computes surfaces ships in `ashfall.html`.

### 1. Calle 42

Tom confirms (2026-10-02) that the unnamed street parallel to Calle 44, about
55 m nearer the railway, running east from Calle 105 at v ≈ 381–386, is
Calle 42.

- Add `c42 = Calle 42` to `LIMA_STREET_CODES`, in numeric order beside
  `c44`.
- These eight links become code `c42` (direction as they stand in the file):
  x_c105–m_sn_c105_sn, m_sn_c105_sn–x_c103, x_c103–m_sn_sn_sn_8,
  m_sn_sn_sn_8–x_c101, x_c101–m_sn_sn_sn_7, m_sn_sn_sn_7–x_sn_18,
  x_sn_18–x_sn_17, x_sn_17–m_sn_sn_sn_6.
- The streets fields of its nine stops:

  | Stop | Now | Becomes |
  |---|---|---|
  | x_c105 | `c105+sn` | `c105+c42` |
  | m_sn_c105_sn | `sn:c105,sn` | `c42:c105,sn` |
  | x_c103 | `c103+sn` | `c103+c42` |
  | m_sn_sn_sn_8 | `sn:sn,sn` | `c42:sn,sn` |
  | x_c101 | `c101+sn` | `c101+c42` |
  | m_sn_sn_sn_7 | `sn:sn,sn` | `c42:sn,sn` |
  | x_sn_18 | `sn` | `c42+sn` (it keeps other unnamed links) |
  | x_sn_17 | `sn` | `c42+sn` |
  | m_sn_sn_sn_6 | `sn:sn,sn` | `c42:sn,sn` |

  A mid stop's cross streets are left as they are. **No id changes.**
- The link m_sn_sn_sn_6–x_sn_20 stays `sn`: it is Calle 44's unnamed
  continuation east of Calle 101 (below).

### 2. The quarters

A link's quarter is decided by its midpoint (the mean of its two stops' u and
v). The boundaries are polylines through stop coordinates, linearly
interpolated between points and extended along the end segment past either
end:

- **The railway** (north from south), in u: fcm_crossing_6km, x_c15_dg4,
  estacion_lima, x_c107_c2_c7. A point is **north** when its v is greater
  than the line's v at its u.
- **Calle 111's eastern carriageway** (east from west, north only), in v: the
  stops x_c111_cbar, m_c111_c48_cbar, x_c111_c48, m_c111_c50_c48, x_c111_c50,
  x_c111_c52_dgmorgan, m_c111_c54_dgmorgan, x_c111_c54, x_c111_c88_2,
  m_c111_c84_sn, x_c111_c84_2, x_c111, m_c111_sn_sn, x_c111_2 (u ≈ 57–71). A
  northern point is **north-east** when its u is greater than the line's u at
  its v, else **north-west**. Calle 111's western branch through the barrio
  is therefore north-west.
- **Calle 15 and Calle 17** (south only), in v: each through its own mid
  stops (streets field starting `c15:` / `c17:`), at u ≈ −172 and u ≈ −285.
  A southern point is **south-east** when its u ≥ Calle 15's u − 1; in **the
  15–17 column** when its u is greater than Calle 17's u + 1; else
  **south-west**.

### 3. Each link's surface

Untouched: a link whose surface is `r`, and any link with an end at a rural,
rail or station stop (kind `r`, `t` or `s`) or at v ≥ 2000. Every other link
takes the first rule that applies:

1. **Paved (`p`)** when:
   - both its stops are `barrio` (the Barrio Atucha's lanes, in any quarter;
     Tom, 2026-10-02);
   - its code is `c111`, `c14` or `dg4`;
   - its code is `c15`;
   - it is in the 15–17 column and its code is `c16` or `c2`;
   - it is one of the roads alongside the railway in the north-east:
     x_c107_c2_c7–x_c107_cp01 and x_c107_cp01–x_c107_cbar;
   - it is in the north-west or the south-east.
2. **North-east:** `p` on `cbar`, `cp01`, `c50`; `g` on `c42`, `c44`, `c46`,
   `c109`; `d` otherwise.
3. **South-west and the rest of the 15–17 column:** `g` on `c44`, `c46`; `d`
   otherwise.

Settled by Tom (2026-10-02):
- the barrio's lanes are paved wherever they run, even east of Calle 111;
- the roads alongside the railway are paved on both sides of town: all of
  Diagonal 4 (out to Calle 35), Calle 2's blocks in the 15–17 column, and Calle 107's two
  railway-side links;
- the 15–17 column is south-west (dirt) apart from Calle 14's, Calle 16's and
  Calle 2's blocks;
- Calle 44's unnamed continuation east of Calle 101 (x_c101_c44 → x_sn_19 →
  x_sn_20) stays dirt.

### 4. Each stop's type

A stop of type `core`, `gravel` or `dirt` that isn't untouched (kind `r`,
`t`, `s`, or v ≥ 2000) takes the **best surface of its links**, `r` ignored:
`core` if any is paved, else `gravel` if any is gravel, else `dirt`. `barrio`
stops keep `barrio`. An implementation choice from #343, retunable.

### 5. Stop text (`STOP_TEXT`), approved by Tom (2026-10-02)

Replace the `core` and `dirt` sets exactly as below. `gravel` and `barrio`
are unchanged. Variant order matters (the stable hash picks by index), so
keep the order given.

```js
core: {
  mid: [
    "A paved street of low houses. Most of the windows have bars, and every door is shut.",
    "Low house fronts along the pavement, a water tank on every roof. Nothing moves behind the bars.",
    "The street is paved here, with kerbs and a line of trees. It is very quiet." ],
  corner: [
    "A paved corner. Nobody is waiting to cross.",
    "Two paved streets meet. No cars, no voices." ] },
dirt: {
  mid: [
    "A dirt street, the ruts baked hard. Low houses on either side, a water tank on every roof.",
    "Packed earth between low houses, dust along the edges. The gates are shut, the windows barred.",
    "A dirt street under a line of trees. Nothing has driven through in a while." ],
  corner: [
    "Two dirt streets cross. The ruts run straight through.",
    "A dirt corner, worn bare where the cars turned." ] },
```

### 6. Comments

- `STOP_TEXT`'s comment: replace the surface description with the quarters,
  in one or two sentences, pointing to `Lima.md` ("Streets and surfaces").
  Keep its statement that each text is true of every stop of its type.
- `LIMA_STOPS` / `LIMA_LINKS`' format comment: unchanged, apart from noting,
  if it names where surfaces come from, that they follow Tom's survey by
  quarter, not the satellite estimate.

## Expected results

Computed in planning from v0.12.1's data with exactly the rules above. The
coding session reproduces these and reports any difference in the changelog;
a difference means a rule was read differently, not that the figures are
targets to force.

- **Links changed: 704 of 1,008.** g→d 402, g→p 268, d→p 32, d→g 2. **No
  link goes from paved to anything else.**
- **Final link surfaces:** `p` 475, `d` 500, `g` 28, `r` 5.
- **Stops changed: 464.** gravel→dirt 285, gravel→core 155, dirt→core 21,
  dirt→gravel 3. **No `core` stop becomes anything else.**
- **Final stop types:** `dirt` 356, `core` 324, `barrio` 54, `gravel` 32,
  `rural` 7, `rail` 3, `station` 1.
- **The player's home stop, `m_c90b_c117_c119`:** both its links paved (it is
  gravel today). This must hold.
- **House sites:** 201 of the 427 mid stops a casa stands on have a paved
  link. All 21 barrio mid stops do.
- Three mid stops have links of two surfaces: m_c24_acc_c17 (dirt and
  paved), m_sn_c111_sn (paved and dirt), m_sn_sn_sn_6 (gravel and dirt).
  Their type follows rule 4; nothing else reads it yet.

## Design decisions to make during implementation

- **How the rewrite is produced**: by hand or by a throwaway script whose
  output is pasted into `LIMA_LINKS` / `LIMA_STOPS`. A script is recommended,
  given 704 links. Either way, nothing that computes surfaces ships. Record
  the method in the changelog.

## Data / schema changes

- PLAYER STATE: none.
- Item schema: none.
- WORLD DATA: `LIMA_STREET_CODES` gains `c42`; `LIMA_LINKS` surfaces and
  eight codes; `LIMA_STOPS` types and nine streets fields; `STOP_TEXT`'s
  `core` and `dirt` sets. No new field, and no id changes.

## In scope

- [ ] `c42` and its links and stops (rule 1).
- [ ] Every link's surface (rules 2–3), and every stop's type (rule 4).
- [ ] `STOP_TEXT`'s `core` and `dirt` sets (rule 5), and the comments (rule 6).
- [ ] Checks, in headless Chromium (`file://`, `window.ashfallDev`,
      read-only):
  - the expected results above, from the shipped data;
  - `validateLocations()` and `validateBuildings()` clean;
  - in play: the home's street reads as paved, a casa on Calle 42 gives
    "Calle 42" as its address, and a south-west dirt street shows the new
    dirt text;
  - the replay page (`?replay`) and the benchmark (`?bench`) pass.
- [ ] The wrap (`docs/03-workflow.md`): PATCH bump, changelog entry with a
      **New content** section, this handoff archived, `Closes #343`.

## Explicitly out of scope

- **Reading link surfaces for anything**: #300 (the water network), next.
- **The gravel text**, whose "low walls and wire fences" isn't sourced
  either: left as is.
- **The barrio's own stop types and extent**, and whether the 14 barrio stops
  east of Calle 111 are rightly typed: unchanged.
- Rural roads, the railway, the station and the road north of town (v ≥ 2000).
- Renaming any stop id to `c42`: ids are save keys.

## Sections touched

Content only: WORLD DATA (`LIMA_STREET_CODES`, `LIMA_STOPS`, `LIMA_LINKS`,
`STOP_TEXT`). The coding session can skip everything else.

## Systems docs

None read or changed: no system reads surfaces yet.

## UI changes

The stop descriptions: most of the town's streets read as paved or dirt
instead of gravel, with the new text above. Calle 42's houses and corners
name Calle 42.

## Dependencies / issue linkage

- Fulfils #343.
- Unblocks #300 (the water network, designed), whose handoff follows this
  pass.
- Nothing is expected to be deferred. If the pass surfaces anything, file it
  at the wrap.

## Open questions for Tom

None.
