# Ashfall Handoff — Reachable Tools & Content Corrections

Current shipped version: v0.5.1
Implied version-change type: PATCH
Issues: #123 — a screwdriver; #67 — every gated action but one depends on a
single reachable tool; #77 — two content details that no longer match the world
model; #135 — every mid-block node labels one of its two exits "Continue"

> **There is a sibling handoff at the top level.**
> `handoffs/presentation-and-signal-pass.md` is the other half of the same
> planning session. The two are independent — neither reads the other's code —
> but **do this one first**, so the version numbers fall in the order the
> changelog entries describe. Implement one handoff per pull request; do not
> merge the two.

## What this is

A pure WORLD DATA pass. Four issues, one rule holding them together: **every
one of them is instance content, and none of them touches a mechanic.** That is
why they ship as one pass and why the sibling handoff exists — `CLAUDE.md`'s
bound is that instance data "never rides along with a mechanics change", and
#126 (in the sibling) is a mechanics change.

The four:

- **#67** — five of the six tool tags that gate an action have exactly **one**
  reachable copy. The whole game's fire is one `box_of_matches` in the room the
  player wakes up in. Tom's decision: **hand-place a second copy of each
  load-bearing tool, in a different place from the first.** The upstream fix
  (unfreezing containers so the dead pools feed tools again) is deliberately
  **not** this pass — it is #133.
- **#123** — a screwdriver, the improvised can opener everyone reaches for,
  does not exist in `ITEM_REGISTRY`. Deferred out of the sealed-food pass
  because it is instance content.
- **#77** — `outside`'s description claims an asymmetry the grid does not have,
  and `onea_patio → alley` is the world's only unexplained one-way exit.
- **#135** — 112 mid-block exit labels say "Continue" where their sibling says
  "Head", encoding a direction of travel the room does not know.

## Relevant existing state

Verified by reading `ashfall.html` at v0.5.1, not recalled.

### Tool scarcity, as it stands

`validateReachability()` at v0.5.1 reports, for the tags in
`REPORTED_TOOL_TAGS`:

| tag | hand-placed | live pools | where the one copy is |
|---|---|---|---|
| `fire-starter` | 1 | none | `box_of_matches` — `living/bookshelf` (Acorn 2A) |
| `fishing` | 1 | none | `fishing_rod` — `storage/unit3` |
| `tackle` | 1 | none | `tackle_box` — `storage/unit3` |
| `chopping` | 1 | `tools_workshop` | `hand_axe` — `hardware/toolwall` |
| `cutting` | 1 | `tools_workshop` | `bolt_cutters` — `hardware/toolwall` |
| `prying` | 2 | none | gates nothing; see #111 |
| `heat` | 1 | `tools_workshop` | `propane_torch` — `hardware/paintaisle` |
| `can-opening` | 5 | `kitchen_tools`, `tools_workshop` | — |
| `blunt` | 10 | several | — |

`fishing_rod` and `tackle_box` are in the **same container**, and
`renderHereActionsPanel()` requires both:

```js
if(room.fishable && hasTool("fishing") && hasTool("tackle")){
```

`hand_axe` and `bolt_cutters` are likewise both in `hardware/toolwall`.

`lighter` — the only other `fire-starter` in the registry — is one of the twelve
items `validateReachability()` reports as unreachable: it appears only in
`retail_stock_general` and `fuel_fire`, both of which are dead pools.

### The hand-placement constraint that governs every placement below

Of 80 containers, **24 still roll** — they ship empty with `spawnPools` and no
`spawnRolled`. Hand-placing anything into one of those requires setting
`spawnRolled:true`, which would kill a live pool draw and make #133 worse.

The 24 are: Acorn `twobee_kitchen/fridge`, `twobee_kitchen/pantry`,
`twobee_bathroom/undersink`, `twobee_bedroom/dresser`, `onebee/closet`; all 8 in
Oak Apartments; all 4 in the Auto Workshop; all 4 in Riverside Freight; all 3 in
the Police Station.

**Every placement in this handoff goes into an already-frozen container
(`spawnRolled:true`), a `carContainer` (which has no pools at all), or a room
floor.** No `spawnRolled` value changes anywhere in this pass.

### The `outside` room

```js
outside: { locationId:"outside", address:"Poplar St & 1st St", area:null, room:null, shelter:"none",
  desc:"A quiet intersection. 1st St runs both ways here — Poplar continues in both directions too, though the block to the west feels like it goes on longer than the one to the east. Your building's stoop is partway down the block to the west.",
```

`poplar2nd` is at `x:100`, `outside` at `x:200`, `poplar3rd` at `x:300` — both
blocks are 100 m and both cost the same at every gait. At 236 characters this is
the longest description in the game; the next is 173.

The second sentence is **verified correct** and must survive: the
`Step into the block (west)` exit leads to `mid_poplar_1_2` at `(150,100)`,
which is `acorn_f0`, Acorn Apartments.

(#77's body quotes this room with a `building:` field. That is stale — the
address/building split shipped after #77 was filed, and the room now carries
`address:` and no `building`. The finding itself is unaffected.)

### The patio gate

```js
onea_patio: { …
  exits:[
    { to:"onea", label:"Go to the living room", distanceM:3 },
    { to:"alley", label:"Go through the back gate", distanceM:6 } ]
},
alley: { locationId:"acorn_f0", …
  exits:[
    { to:"mid_poplar_1_2", label:"Head out to the street" },
    { to:"balcony", label:"Climb the fire escape" } ]
},
```

`alley` and `onea_patio` share `locationId:"acorn_f0"`, so the return exit is a
**same-Location** exit and needs a hand-authored `distanceM`.

`alley` is reachable from turn one — `mid_poplar_1_2` offers "Duck into the
alley" with no gate and no tool.

Doors at v0.5.1:

```js
function makeDefaultDoors(){
  return {
    "2a": { locked:false, sides:["hallway2","living"], building:"acorn" },
    "2b": { locked:true,  sides:["hallway2","twobee"], building:"acorn" },
    "1a": { locked:true,  sides:["hallway1","onea"],   building:"acorn" },
    "1b": { locked:true,  sides:["hallway1","onebee"], building:"acorn" }
  };
}
const DOOR_LABELS = { "2a":"2A", "2b":"2B", "1a":"1A", "1b":"1B" };
```

`findKeyForDoor()` matches a `masterKey` on `building`, so `master_key`
(`building:"acorn"`) opens any door added with `building:"acorn"`.

### The movement labels

Every mid-block node has exactly two exits, worded asymmetrically:

| form | count |
|---|---|
| `Head west toward <Street>` | 56 |
| `Continue east toward <Street>` | 56 |
| `Head south toward <Street>` | 56 |
| `Continue north toward <Street>` | 56 |

Intersections use `Head <dir> on <Street>` and `Step into the block (<dir>)` and
are **not** touched.

## Rules / mechanics

None. This pass adds no rule, changes no rule, and reads no new field. Every
change below is data.

## Data / schema changes

**No schema change.** One new `ITEM_REGISTRY` entry, two new `SPAWN_POOLS`
entries, one new `doors` entry, one new `DOOR_LABELS` entry, one new exit, one
`doorId` added to two existing exits, six item placements, one description
rewrite, 112 label edits. No new field on any item, room, container or exit.

## In scope

### 1 — #135: the movement wording (112 labels)

Replace `Continue` with `Head` in every mid-block exit label. Concretely, 112
occurrences of the literal `label:"Continue ` become `label:"Head `:

```js
{ to:"dock4th", label:"Continue east toward 4th St" },   // before
{ to:"dock4th", label:"Head east toward 4th St" },       // after
```

Every mid-block then offers `Head <dir> toward <Street>` twice, differing only
in direction and destination.

Nothing else in any label changes — not `to`, not `distanceM`, not `doorId`, and
not the compass word. `applyComputedDirections()` matches the first compass word
and splices around it, so its behaviour is identical before and after; both
exits of every mid-block are cross-Location and are rewritten today and after.

**Acceptance:** `grep -c 'label:"Continue ' ashfall.html` returns 0, and
`grep -c 'label:"Head ' ashfall.html` returns 451 (339 today + 112).

### 2 — #123: the screwdriver

**Registry entry**, placed among the other small tools:

```js
screwdriver: { name:"Screwdriver", category:"Tool", unitWeight:0.15, tags:["can-opening"] },
```

`0.15` is a judgment call, retunable: `can_opener` and `box_cutter` are 0.1,
`kitchen_knife` 0.15. `can-opening` and nothing else — a screwdriver is not a
blade and not blunt.

**Pool entries.** Both are **chosen** numbers, and they are the first chosen
numbers in `SPAWN_POOLS` — every other `chance` in the table was derived from
the lottery v0.5.1 replaced. Tom's decision: the screwdriver is a common shop
item.

```js
// tools_workshop, in descending-chance position (after box_cutter)
{ itemId:"screwdriver", chance:0.20, qtyMin:1, qtyMax:1 },

// hardware_store, in descending-chance position (after plank)
{ itemId:"screwdriver", chance:0.23, qtyMin:1, qtyMax:1 },
```

`0.20` matches `tools_workshop`'s `box_cutter`/`metal_pipe`/`motor_oil` band;
`0.23` matches `hardware_store`'s `plank`. Both are retunable balance values and
must be flagged as such in the changelog.

**Two things the coding session must not miss:**

1. **`hardware_store` is a dead pool** (#133) — no container that still rolls
   draws from it. That entry therefore spawns nothing today. It is added anyway
   so the pool is correct when #133 unfreezes it; say so in the changelog rather
   than letting it read as a live placement.
2. **The `SPAWN_POOLS` block comment is now false** and must be rewritten. It
   currently says:

   > Every `chance` below is derived, not chosen. […] An ugly number here is the
   > signal that nobody has picked it yet.

   Replace with wording that says every `chance` *except the two screwdriver
   entries* is derived, that those two are chosen and retunable, and that an
   ugly six-decimal number still marks a derived one. Do not delete the
   derivation note — it is what makes the other 175 entries re-checkable.

**Hand placement:** `mid_main_1_3`'s `cab` carContainer (the parked work truck,
beside the work gloves and thermos). `capacityKg:5`, currently 0.6 kg.
A carContainer has no `spawnPools`, so nothing is frozen by this.

### 3 — #67: second copies of the load-bearing tools

Five placements. Each is in a different place from the first copy, and the
fishing pair is split across two rooms so no single loss removes fishing.

| item | qty | goes to | why there |
|---|---|---|---|
| `lighter` | 1 | Corner Store `register` (frozen) | a lighter at a shop register; also lifts `lighter` out of #133's unreachable twelve |
| `hand_axe` | 1 | `poplar6th` **floor** | the corner already has "a hand-painted sign on a post reads FIREWOOD" |
| `bolt_cutters` | 1 | `onebee/toolcabinet` (frozen) | the superintendent's half-workshop, a different building from the hardware store |
| `fishing_rod` | 1 | `mid_water_7_9` **floor** | riverfront, beside the firewood already there |
| `tackle_box` | 1 | `water9th` **floor** | the cracked boat ramp, one node along from the rod |

Capacity checks, all verified against the file:

- `cornerstore/register` — cap 5 kg, holds `loose_change` (0.3). +0.05 → 0.35.
- `onebee/toolcabinet` — cap 25 kg, holds crowbar 2.5 + duct_tape ×2 0.6 +
  wrench 0.8 = 3.9. +1.2 → 5.1.
- `poplar6th` — `floorCap:100`, empty. +1.4.
- `mid_water_7_9` — `floorCap:20`, holds firewood ×2 = 1.6. +0.8 → 2.4.
- `water9th` — `floorCap:100`, empty. +1.2.

All five use `itemsFromRegistry()`, never a repeated definition.

**Acceptance — run `validateReachability()` on a fresh world and compare
against v0.5.1's figures:**

| report | v0.5.1 | after this pass |
|---|---|---|
| dead pools | 10 | **10** (unchanged — no `spawnRolled` moves) |
| unreachable items | 12 | **11** (`lighter` is placed) |
| `fire-starter` hand-placed | 1 | **2** |
| `fishing` hand-placed | 1 | **2** |
| `tackle` hand-placed | 1 | **2** |
| `chopping` hand-placed | 1 | **2** |
| `cutting` hand-placed | 1 | **2** |
| `can-opening` hand-placed | 5 | **7** (the second `hand_axe` and the screwdriver) |
| `blunt` hand-placed | 10 | **11** (the second `hand_axe`) |
| `prying` / `heat` | 2 / 1 | **unchanged** |

If any of those lands somewhere else, a placement went into a rolling container
or a registry tag was mistyped.

### 4 — #77 item 1: the `outside` description

Replace the `desc` string with:

```js
desc:"A quiet intersection. 1st St runs both ways here, and Poplar continues in both directions too. Your building's stoop is partway down the block to the west.",
```

The clause claiming the west block "feels like it goes on longer" is dropped;
the verified stoop sentence is kept verbatim. 236 → 153 characters, three
sentences → two. Nothing else about the room changes — the `// The Poplar St /
1st St intersection, under an id that predates the grid` comment above it stays
exactly as it is, because it explains the room id, not the description.

### 5 — #77 item 2: open the gate, lock the patio door

Four edits, which together make the patio reachable from the alley while leaving
1A's interior behind a lock.

**a.** `makeDefaultDoors()` gains a fifth door:

```js
"1a-patio": { locked:true, sides:["onea_patio","onea"], building:"acorn" }
```

`building:"acorn"` means `master_key` opens it, the same as `"1a"`.
`acorn_apt_2a_key` carries `doorId:"2a"` and does not.

**b.** `DOOR_LABELS` gains `"1a-patio":"the patio"`.

The label must not be `"1A"`: `doorsForRoom("onea")` now returns both `"1a"` and
`"1a-patio"`, and `getItemActions()`'s master-key branch pushes one action per
door, so two doors sharing a label would give two identical `Unlock 1A` buttons.
With `"the patio"` they read `Unlock 1A` and `Unlock the patio`.

`"The door to the patio is locked."` reads oddly from the patio side. That is
#136 — `DOOR_LABELS` names a door by its destination and a door has two sides —
and it is a **pre-existing** wart, reproducible today by locking 2A from inside
it. Do not fix it here; #136 owns it.

**c.** Both existing exits between `onea` and `onea_patio` gain the doorId:

```js
// in onea
{ to:"onea_patio", label:"Go to the patio", distanceM:3, doorId:"1a-patio" },
// in onea_patio
{ to:"onea",       label:"Go to the living room", distanceM:3, doorId:"1a-patio" },
```

(`onea`'s current label is `"Go to the patio"`; keep whatever it says.)

**d.** `alley` gains the return exit:

```js
{ to:"onea_patio", label:"Go through the gate", distanceM:6 }
```

`distanceM:6` matches the reverse exit. Both rooms are `locationId:"acorn_f0"`,
so this is a same-Location exit and `distanceM` is required; it carries no
compass word, so `applyComputedDirections()` leaves it alone. `isGridTravel()`
is false, so it renders in the **Here** panel, which is correct.

**Consequences to state in the changelog, both intended:**

- **The patio's storage bin becomes reachable on day one.** `onea_patio` holds
  `storagebin1a` with firewood ×3 and nails ×1, previously behind 1A's locked
  front door. It is now reachable through the alley with no key and no tool.
  That is the point of opening the gate, but it is an early-game supply change
  and should not go unremarked.
- **The patio is not a trap.** While `"1a-patio"` is locked, `getExitsForRoom()`
  drops the `onea` exit and leaves the alley gate, so a player who walks in
  through the gate can always walk back out.
- **1A's interior is no better protected and no worse.** Reaching it still needs
  `master_key`, which is in `onebee/desk`, behind either door `"1b"` or the
  breakable `1b-alley` window — unchanged.

**Save compatibility.** `applyLoadedData()` assigns `world = data.world` and
`doors = data.doors` wholesale, and no backfill adds an exit or a door. An
existing save therefore gets neither the new exit nor the new door and is
internally consistent — no `doors["1a-patio"]` lookup can fire, because no
exit in that save carries the id. New games and restarts get both. Say this in
the changelog; it is the same wrinkle #77 records.

## Design decisions to make during implementation

Narrow calls. Record whichever is picked in the changelog's Notes/assumptions.

1. **Where in `ITEM_REGISTRY` the `screwdriver` entry sits.** The registry has
   loose thematic grouping rather than a sort order. Recommended: beside
   `box_cutter`, which it is nearest in kind and weight.
2. **Where in each pool's `entries` array the screwdriver sits.** Entries land
   in a container in declaration order and the tables read roughly
   descending-chance. Recommended: after `box_cutter` in `tools_workshop`, after
   `plank` in `hardware_store`.
3. **Whether `onea`'s exit label to the patio changes.** It currently reads
   "Go to the patio". Recommended: leave it — the door is signalled by the panel,
   not the label.

## Explicitly out of scope

Restated so this needn't be reopened to know what isn't here.

- **#133 — the ten dead pools and the eleven remaining unreachable items.** No
  `spawnRolled` value changes. `hardware_store` stays dead and the screwdriver
  entry in it stays inert. Unfreezing containers is that issue's decision, not
  this pass's.
- **#126 — the spent fire-starter and the missing fire signal.** In the sibling
  handoff. This pass adds a second fire-starter; it does not change what happens
  when one runs out.
- **#136 — `DOOR_LABELS` naming a door by its destination.** The new door works
  around it with a label that reads acceptably from both sides. The fix is #136's.
- **#111 — gating vehicle forcing on `prying`.** `prying` stays at 2 hand-placed
  and gates nothing.
- **Rebalancing any existing pool.** No `chance`, `emptyChance`, `qtyMin` or
  `qtyMax` already in the file changes. The only new numbers are the two
  screwdriver chances.
- **New registry items beyond `screwdriver`.** No second `can_opener`, no new
  fire-starter type, nothing to make the Medical category do anything (#23).
- **#7 lore, #8 map expansion, #6 rooftops.** No room, street or building is
  added; no description other than `outside`'s is touched.
- **#121, #116, #15, #51.** Untouched.

## Sections touched

**WORLD DATA only.** This is a content pass — the coding session can skip every
other section of the script.

- `ITEM_REGISTRY` — one entry.
- `SPAWN_POOLS` — two entries and the block comment.
- `makeDefaultDoors()` and `DOOR_LABELS` — one entry each.
- `buildAcornApartments()` — `onea`, `onea_patio`, `onebee`.
- `buildPoplarSt()` — `outside`, `alley`, `poplar6th`.
- `buildCornerStore()` — `cornerstore`.
- `buildWaterSt()` — `water9th`, `mid_water_7_9`.
- `buildMainSt()` — `mid_main_1_3`.
- Every street builder — the 112 `Continue` → `Head` labels.

Nothing in CONFIG/CONSTANTS beyond the version string. Nothing in PLAYER STATE,
CORE UTILITIES, INVENTORY / ITEM SYSTEM, WORLD INTERACTION, SURVIVAL / TIME
SIMULATION, STAMINA / FATIGUE, CRAFTING, FIRE / COOKING, PERSISTENCE, EVENTS or
RENDERING.

## UI changes

No panel, button or layout changes. What the player sees differently:

- 112 mid-block movement buttons read "Head …" instead of "Continue …".
- `outside`'s room description is two sentences instead of three.
- A new "Go through the gate" button in the alley.
- A "The door to the patio is locked." note on the patio, or an "Unlock the door
  to the patio" button when carrying the master key.
- Six more items exist to be found.

## Dependencies / issue linkage

Fulfils **#123**, **#67**, **#77** and **#135** in full. The pull request carries
`Closes #123`, `Closes #67`, `Closes #77`, `Closes #135`.

Unblocks nothing; blocked by nothing.

Expected to leave deferred: nothing new. Everything cut from this pass is
already an open issue — #133, #136, #111 — and named above. If the pass surfaces
something else, file it and reference it in the pull request, per the wrap-time
checklist. If it surfaces nothing, say so in the changelog's Documentation
section.

## Open questions for Tom

**None.** Every design call this pass needed was settled in the planning session:
the second-copy approach and the five placements (#67), the screwdriver's chance
band and that it may be the first chosen number in `SPAWN_POOLS` (#123), the
rewrite rather than the comment on `outside` (#77 item 1), opening the gate while
gating the patio door (#77 item 2), and the wording change (#135).

## After implementation

Open a pull request carrying:

1. `ashfall.html` with `GAME_CONFIG.VERSION` bumped — **PATCH**, so
   `versionCompat()` does not move and `SAVE_KEY` stays `ashfall_save_v0.5`.
2. A new `CHANGELOG.md` entry at the top per `docs/CHANGELOG_GUIDE.md`, with
   `Implements: handoffs/reachable-tools-and-content-corrections.md`, recording
   the two chosen screwdriver chances as retunable balance values, the
   day-one reachability of the patio storage bin, the `SPAWN_POOLS` comment
   rewrite, and the save-compat note.
3. `Closes #123`, `Closes #67`, `Closes #77`, `Closes #135` in the description.
4. This file moved: `git mv handoffs/reachable-tools-and-content-corrections.md
   handoffs/archive/reachable-tools-and-content-corrections.md`.
5. New issues for anything deferred, or a line saying nothing was.

After the merge, tag it — `git tag vX.Y.Z <commit>`, naming the commit
explicitly, then verify with
`git show vX.Y.Z:ashfall.html | grep VERSION`.

**Validation to perform**, beyond the syntax check:

- `git diff origin/main...HEAD -- ashfall.html` — confined to the sections named
  above and to WORLD DATA.
- `validateReachability()` on a fresh world, against the acceptance table in
  section 3. `validateItemRegistry()`, `validateLocations()` and
  `validateRoomSchema()` must still report clean.
- `grep -c 'label:"Continue ' ashfall.html` → 0.
- In a browser: walk alley → gate → patio and back; confirm the patio door is
  locked without the master key and opens with it; confirm the patio's storage
  bin is reachable from the alley; confirm `onea` offers two distinct unlock
  buttons with the master key.
- Load a v0.5.1 save and confirm it still reports "Progress loaded from this
  browser." with no version warning, and that its `alley` has no gate exit.
