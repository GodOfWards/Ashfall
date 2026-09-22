# Ashfall Handoff — Roll core and the seeded world

Current shipped version: v0.5.6
Implied version-change type: MINOR
Issue: #51 — A roll core — one way to ask the game for a chance, before four
systems each invent their own

## What this is

One named operation for "does this happen?", backed by a seeded, stateless
source, so that illness, spoilage (#48), wounds (#50), water potability (#52) and
skill checks (#10) all ask the same way instead of each picking a convention. The
issue's own framing of the split it must respect:

> **This issue** — the character-independent core. One convention, one named
> operation, the four existing sites converted to it.
> **#10** — the character-dependent layer on top: attributes, traits,
> encumbrance, difficulty. Consumes this rather than replacing it.

The pass also uses the seed to do two things the unseeded source could not:
**block save-scumming** (reloading and repeating an action reproduces its
outcome) and make **container loot a property of the world rather than of the
player's route**. Both were decided during planning and are specified below.

This is a large pass. It is three things at once — a convention, determinism, and
a small UI surface — and it touches nine ARCHITECTURE sections plus one WORLD
DATA value. That breadth is deliberate and was chosen over splitting it; the
scope below is the whole of it and nothing beyond it.

## Relevant existing state

Verified by reading `ashfall.html` at v0.5.6.

**Every source of randomness in the file.** One helper and four bare
comparisons, in three conventions:

| Site | Line | Form | Convention |
|---|---|---|---|
| `randInt()` | 3703 | `min + Math.floor(Math.random() * (max - min + 1))` | range draw |
| `doConsume()` | 4026 | `Math.random()*100 < it.illnessChance` | percent, hit |
| `doOpenContainer()` | 4456 | `Math.random() < pool.emptyChance` | fraction, hit |
| `doOpenContainer()` | 4458 | `Math.random() >= entry.chance` | fraction, **miss** |
| `doFish()` | 4716 | `Math.random() < FISH_BITE_CHANCE` | fraction, hit |

`randInt()` has exactly one caller: the quantity draw at 4459. `weightedPick()`
does not exist — v0.5.1 removed it, and `randInt`'s own comment records that
there is "no second helper here any more".

**Scale counts.** Fraction: 178 entry `chance` values + 29 `emptyChance` values +
`FISH_BITE_CHANCE` = 208. Percent: one, `illnessChance:35` on `raw_fish` (line
620), the only `ITEM_REGISTRY` entry carrying the field. The 178 are *derived*
figures — v0.5.1 computed each from the lottery it replaced so that `P(appears)`
carried across — which is why they read `0.245069` and why they must not be
rescaled.

**Which rolling actions cost game time.** `doFish()` calls
`advanceTime(FISH_DURATION_MIN)`. `doConsume()` and `doOpenContainer()` call
`advanceTime()` **not at all** — eating and opening a container are instant. This
is why game time alone cannot key every roll.

**`illnessChance` reaches saves.** `itemFromRegistry()` (line 715) deep-clones
the registry entry onto every instance, so the field is written into every save
holding a raw fish. `raw_fish` reaches saves by two routes: the
`kitchen_perishable` pool and `doFish()`.

**Persistence shape.** `serializeGame()` (line 4835) writes `state` wholesale, so
any new field in `state` persists with no extra work — the comment at line 3644
records that this is exactly why `invTab`/`worldTab`/`mapZoomMode` are kept
*outside* `state`. `applyLoadedData()` builds `nextState` as
`{ ...base, ...data.state, vitals: {...} }` (line 5016) with `base` from
`makeDefaultState()`, so a save predating a new field inherits the default.
Five backfills run after validation (lines 5041–5046).

**`spawnRolled` is load-bearing and stays so.** `doOpenContainer()` *appends* its
roll to `container.items` (line 4460). Determinism makes the result stable but
does not prevent a second append, so the flag still guards against rolling twice
in one session, and still marks hand-authored containers as not to be topped up.

**The restart flow.** `restartMenuBtn`'s handler (line 5250) is a `confirm()`
gate on `doRestart()`. `doRestart()` (line 5198) takes no arguments and calls
`makeDefaultState()`.

**`render()` rolls nothing today**, and `doOpenContainer()` is invoked from a tab
click handler in `renderWorldItemsPanel()` (line 6238), not from a render path.

## Rules / mechanics

### The source — stateless, seeded

There is no PRNG cursor. A roll is a pure function of the seed and a **key** that
says what is being decided. One hash serves two purposes:

```js
// FNV-1a over a string, from a caller-supplied 32-bit basis. Two callers:
// hashKey() mixes in the run's seed as the basis, seedFromInput() uses the
// standard offset basis because there is no seed yet. Not cryptographic and
// does not need to be — it is a game's dice.
const FNV_OFFSET_BASIS = 2166136261;
const FNV_PRIME = 16777619;
function fnv1a(str, basis){
  let h = basis >>> 0;
  for(let i = 0; i < str.length; i++){
    h ^= str.charCodeAt(i);
    h = Math.imul(h, FNV_PRIME) >>> 0;
  }
  return h >>> 0;
}
// The key parts joined by a character that cannot occur in a room id,
// container id, pool id or item id, so ("a","bc") and ("ab","c") can never
// collide.
const KEY_SEP = "\u001F";
function hashKey(parts){ return fnv1a(parts.join(KEY_SEP), state.seed); }
// A key's value in [0,1). mulberry32's avalanche, without its stepping —
// there is no cursor to step. Strictly below 1, which both callers rely on.
function rollValue(...parts){
  let t = (hashKey(parts) + 0x6D2B79F5) | 0;
  t = Math.imul(t ^ t >>> 15, 1 | t);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
  return ((t ^ t >>> 14) >>> 0) / 4294967296;
}
```

### The primitive

```js
// The one way to ask the game whether something happens. `p` is a fraction in
// [0,1] — the file's convention everywhere but one field, and the one place a
// probability's legality is checked. Warns and clamps rather than throwing: a
// throw inside doOpenContainer() would break the game mid-action, and a
// mis-authored probability should be loud, not fatal.
function chance(p, ...keyParts){
  if(!(Number.isFinite(p) && p >= 0 && p <= 1)){
    console.warn(`chance: p ${p} is not a number in [0,1] — clamped`, keyParts);
    p = Number.isFinite(p) ? Math.max(0, Math.min(1, p)) : 0;
  }
  return rollValue(...keyParts) < p;
}
```

`p === 0` is always false and `p === 1` always true, because `rollValue()` is
strictly below 1.

`randInt()` gains a key and routes through the same source. Without this, spawn
*quantities* stay unseeded and a container's contents are not reproducible even
with a seed:

```js
function randInt(min, max, ...keyParts){
  return min + Math.floor(rollValue(...keyParts) * (max - min + 1));
}
```

### The three keys

| Roll | Key parts |
|---|---|
| Pool empty gate | `"loot", roomId, containerId, poolId, "empty"` |
| Pool entry hit | `"loot", roomId, containerId, poolId, entry.itemId` |
| Entry quantity | `"loot", roomId, containerId, poolId, entry.itemId, "qty"` |
| Fishing bite | `"fish", state.currentRoom, state.totalMinutes` |
| Illness on eating | `"illness", state.rollSeq` |

**Loot keys use `poolId` and `itemId`, not array indices**, so reordering a
container's `spawnPools` or a pool's `entries` during authoring does not reshuffle
every container in the game. The cost is that a container listing the same pool
twice, or a pool listing the same item twice, would collide — neither occurs
today, and both gain a validator guard (below).

**Fishing is keyed on time, and that is what implements the save-scum rule.**
`state.totalMinutes` at roll time — which is *after* `advanceTime()`, matching the
current order at 4714–4716. Repeating the action from a reloaded save reproduces
the roll; spending any time first (chopping, walking, resting) changes
`totalMinutes` and therefore the roll. `totalMinutes` is a float, JSON round-trips
it exactly, and it stays far below the magnitude where `String()` switches to
exponent notation, so its string form is stable.

**Illness is keyed on a counter because eating is instant.** Three raw fish eaten
at the same `totalMinutes` must roll independently. `state.rollSeq` cannot be
farmed for rerolls: the only way to advance it is to eat illness-capable food,
which consumes the food and rolls its illness anyway.

### The illness call site, restructured exactly

The existing condition short-circuits in an order that matters. At line 4026,
`Math.random()` is the *second* test, so a draw is consumed whenever
`it.illnessChance` is truthy — including when the player is already ill and the
result is discarded. Preserve that, or which draws are consumed changes:

```js
if(it.illnessChance){
  const ill = chance(it.illnessChance, "illness", state.rollSeq);
  state.rollSeq += 1;
  if(ill && state.illnessMinutesLeft <= 0){
    state.illnessMinutesLeft = ILLNESS_DURATION_MIN;
    log("It doesn't sit right. You can feel it already.", "warn");
  }
}
```

Do **not** hoist `state.illnessMinutesLeft <= 0` into the outer guard. It would
skip the draw and desynchronise `rollSeq` against a save taken before the meal.

### `illnessChance` rescaled, with a backfill

`ITEM_REGISTRY.raw_fish` becomes `illnessChance:0.35`, and the ITEM DATA SCHEMA
comment at line 526 changes from `% chance` to a fraction in `[0,1]`. The
probability is unchanged — 35% before, 35% after — so there is no balance change.

A sixth backfill repairs instances written at the old scale, run alongside the
existing five in `applyLoadedData()`:

```js
// backfillIllnessScale(): sixth companion to backfillItemIds(), run alongside
// it on every load. Instances written before illnessChance became a fraction
// carry it as a percent (raw_fish shipped 35). A value above 1 is a percent by
// construction — a legal fraction can never exceed 1 — so the test is
// unambiguous and dividing by 100 is exact. Without this, every raw fish in an
// imported pre-0.6 save would be a guaranteed illness, since 35 exceeds every
// value rollValue() can return.
function backfillIllnessScale(){
  const scan = (list)=> (list || []).forEach(it=>{
    if(it && typeof it.illnessChance === "number" && it.illnessChance > 1){
      it.illnessChance /= 100;
    }
  });
  invPools().forEach(scan);
  Object.keys(world).forEach(roomId=>{
    const room = world[roomId];
    scan(room.floor);
    (room.containers || []).forEach(c=>scan(c.items));
    (room.carContainers || []).forEach(c=>scan(c.items));
  });
}
```

`invPools()` already covers equipment slots, so an illness-bearing item in a
backpack is reached.

### The loot roll, extracted

Split the roll out of the action so it can be evaluated without mutating
anything. #150 depends on this being possible, and it is also what makes the
keyed form readable:

```js
// The items a container's pools yield, as a pure function of the run's seed and
// the container's identity. No mutation, no state read but state.seed — so the
// same container yields the same contents whether it is opened first or
// fiftieth, and whether it is opened at all.
function rolledLootFor(roomId, container){
  const out = [];
  (container.spawnPools || []).forEach(poolId=>{
    const pool = SPAWN_POOLS[poolId];
    if(!pool) return;                       // defensive, as before
    if(chance(pool.emptyChance, "loot", roomId, container.id, poolId, "empty")) return;
    pool.entries.forEach(entry=>{
      if(!chance(entry.chance, "loot", roomId, container.id, poolId, entry.itemId)) return;
      const qty = randInt(entry.qtyMin, entry.qtyMax,
        "loot", roomId, container.id, poolId, entry.itemId, "qty");
      out.push(itemFromRegistry({ id: entry.itemId, qty }));
    });
  });
  return out;
}
```

Note the entry test is now a **hit** test, inverting the `>= entry.chance` miss
form at 4458. Same behaviour, one convention.

`doOpenContainer()` keeps its existing structure and flags:

```js
function doOpenContainer(room, container){
  worldTab = container.id;
  if(container.spawnPools && !container.spawnRolled){
    rolledLootFor(state.currentRoom, container)
      .forEach(it=> addToList(container.items, it));
    container.spawnRolled = true;
    container.lastRolledMinute = state.totalMinutes;
  }
  render();
}
```

`state.currentRoom` is the correct `roomId`: the only caller is the tab click
handler at line 6238, which passes `world[state.currentRoom]`.

### The seed

```js
seed: <uint32>,   // the run's identity; set once, never mutated
rollSeq: 0,       // disambiguates rolls that share a game minute
```

`makeDefaultState(seed)` takes an optional seed and falls back to a fresh one:

```js
// The one remaining Math.random() in the file, and deliberately so: a new run
// needs an unpredictable seed, and every roll after this point derives from it
// rather than calling here again. Not a missed conversion.
seed: seed === undefined ? (Math.floor(Math.random() * 4294967296) >>> 0) : (seed >>> 0),
```

`doRestart(seed)` forwards it to `makeDefaultState(seed)`.

### Seed entry and display

Input accepts either form, so a displayed seed is always re-enterable and a
memorable word is also valid:

```js
// A run's seed from whatever the player typed. A plain decimal integer inside
// the uint32 range is taken as the seed itself, so the number the menu shows
// round-trips exactly. Anything else — a word, a phrase, an out-of-range
// number — is hashed, because taking `4294967296 >>> 0` would silently alias
// seed 0.
function seedFromInput(str){
  const s = str.trim();
  if(/^\d+$/.test(s)){
    const n = Number(s);
    if(Number.isSafeInteger(n) && n <= 4294967295) return n >>> 0;
  }
  return fnv1a(s, FNV_OFFSET_BASIS);
}
```

The restart handler replaces its `confirm()` with a `prompt()`. The prompt's
Cancel is the destructive-action guard the `confirm()` used to be, so the
protection is preserved rather than dropped:

```js
document.getElementById("restartMenuBtn").addEventListener("click", ()=>{
  const answer = prompt(
    "Restart the game? This throws away all current progress.\n\n"
    + "Leave blank for a new world, or enter a seed to replay a specific one.", "");
  if(answer === null) return;                       // cancelled
  const s = answer.trim();
  doRestart(s === "" ? undefined : seedFromInput(s));
});
```

The seed is displayed as its canonical uint32 — what a typed word hashed to,
which is what reproduces the run. A word is lossy; the number is the seed.

### Validator additions

Two new guards in `validateReachability()`, both for collision hazards this pass
creates, reported in its existing string-array style:

- A container whose `spawnPools` lists the same pool id twice.
- A pool whose `entries` list the same `itemId` twice.

And two range checks, extending guards that already exist in spirit:

- `emptyChance` outside `[0,1]`, beside the existing `entry.chance` check in
  `validateReachability()`.
- Any `ITEM_REGISTRY` entry whose `illnessChance` is outside `[0,1]`, in
  `validateItemRegistry()` — a registry fact, checked by the registry validator.

### The one ordering invariant

Loot and fishing keys are position-independent, so their draw order does not
matter. `rollSeq` is the exception. **Nothing reachable from `render()` may
advance `state.rollSeq`** — today that is one site, `doConsume()`, which is a
click handler. Record this as a comment beside `rollSeq`, because a future roll
placed in a render path would desynchronise every subsequent illness roll against
a save, in a way that is close to undebuggable.

### Version and save key

MINOR. `GAME_CONFIG.VERSION` `"0.5.6"` → `"0.6.0"`, which makes `versionCompat()`
yield `"0.6"` and `SAVE_KEY` `"ashfall_save_v0.6"`. A v0.5 browser save becomes
invisible to "Load from this browser" rather than erroring, since `doLoadLocal()`
simply finds nothing at the new key. An imported v0.5 file still loads, warns on
the version mismatch, inherits `seed`/`rollSeq` from `makeDefaultState()` through
the existing spread, and has its `illnessChance` instances repaired by the new
backfill.

## Design decisions to make during implementation

- **Where the seed line goes.** Recommended default: a new `.menu-section`
  titled **Run**, below Stats, holding one `Seed: <n>` line. Preferred over
  appending to `#statsBox` for two reasons — `render()`'s game-over branch wipes
  `statsBox`, and the seed is exactly what a player wants after dying; and #149
  will need somewhere to put run configuration, which this gives it without
  building any of it. The alternative (a line inside Stats) is acceptable and
  smaller. Record which was chosen.
- **Whether `rolledLootFor()` is extracted as specified.** Recommended: yes, as
  written. It is what lets #150 evaluate a seed without mutating a world, and it
  keeps `doOpenContainer()` about appending rather than about probability. Inlining
  the keyed rolls into `doOpenContainer()` would work today and close that door.
- **`KEY_SEP`'s value.** Recommended `"\u001F"` (unit separator). Any character
  that cannot appear in a room, container, pool or item id is equivalent; the
  point is that one exists, not which.
- **Prompt wording.** The text above is a reasonable default, not a fixed string.
  Functional UI text, held to clarity rather than to the game's descriptive tone.

## Data / schema changes

**PLAYER STATE** — two new fields in `makeDefaultState()`:

- `seed` — uint32, the run's identity. Set once, never mutated.
- `rollSeq` — integer, starts at 0. Advanced only by rolls with no natural key.

Both persist automatically via `serializeGame()`'s wholesale write of `state`,
and both are supplied to older saves by `applyLoadedData()`'s existing spread.
These two fields are what make this pass MINOR.

**ITEM DATA SCHEMA** — `illnessChance` changes unit from percent (0–100) to a
fraction in `[0,1]`. One registry value changes (`raw_fish`, `35` → `0.35`) and
the schema comment at line 526 is updated. This is definition data for the
mechanic the pass is building — the field's unit *is* part of the convention
being established — so it rides along under `CLAUDE.md`'s "definition data may
ride along" rule rather than being a content pass.

**WORLD DATA** — no room, exit, container, door or window changes. No
`SPAWN_POOLS` value changes. `spawnRolled` and `lastRolledMinute` keep their
current meanings and are neither removed nor repurposed.

## In scope

1. `fnv1a()`, `hashKey()`, `rollValue()`, `chance()` in CORE UTILITIES; `randInt()`
   widened to take a key.
2. All four existing randomness sites converted, with the exact keys above.
3. `rolledLootFor()` extracted; `doOpenContainer()` reduced to appending it.
4. `doConsume()`'s illness branch restructured to preserve draw consumption.
5. `state.seed` and `state.rollSeq`; `makeDefaultState(seed)`; `doRestart(seed)`.
6. `seedFromInput()`; the restart `prompt()`; the seed display.
7. `backfillIllnessScale()`, wired into `applyLoadedData()` beside the other five.
8. `illnessChance` rescaled on `raw_fish` and its schema comment corrected.
9. The four validator additions.
10. `GAME_CONFIG.VERSION` → `0.6.0`.

## Explicitly out of scope

- **#10** — degrees of success, opposed rolls, modifier stacking, and anything
  character-dependent. A skill check is layer 3 calling `chance()`; it is not this
  pass's business, and `chance()` returning a bare boolean rather than a result
  object is the decision that keeps the layers apart. Near-miss feedback ("that
  was a close thing") belongs on `skillCheck()`'s return, because a near miss is
  only meaningful relative to what the character could have done.
- **#150** — `simulateSeed()` / seed sampling. Filed, blocked on this pass. Build
  `rolledLootFor()` so it stays possible; build nothing of it.
- **#149** — run configuration beyond the seed: loot availability, difficulty,
  start conditions. The seed input is the seam #149 will build on, not a down
  payment on it.
- **Keyed streams beyond the three domains specified.** No general stream
  registry, no key namespacing scheme. Three domains, three key shapes.
- **`SPAWN_POOLS` values.** The 178 derived `chance` figures and 29
  `emptyChance` values are not touched. Rescaling them is explicitly wrong — see
  the registry comment on why they read `0.245069`.
- **Eating's zero duration.** It is what forces `rollSeq` to exist, and changing
  it is #120/#121 territory.
- **#15** (container respawn) — `lastRolledMinute` stays unread and reserved.
- **#133** (dead pools, unreachable items) — the pools' gaps are untouched; this
  pass changes how they are drawn, not what they contain.
- **#48, #50, #52, #23** — the consumers this exists for. None is built here.
- **#134/#116** — durability stacks and tool wear. `randInt()`'s widening does
  not touch them.

## Sections touched

- **CONFIG / CONSTANTS** — `GAME_CONFIG.VERSION`; `FNV_OFFSET_BASIS`, `FNV_PRIME`,
  `KEY_SEP`.
- **WORLD DATA** — `ITEM_REGISTRY.raw_fish`'s `illnessChance`, and the ITEM DATA
  SCHEMA comment. Nothing else.
- **PLAYER STATE** — `seed`, `rollSeq`, `makeDefaultState(seed)`.
- **CORE UTILITIES** — the hash, `rollValue()`, `chance()`, `randInt()`,
  `seedFromInput()`.
- **INVENTORY / ITEM SYSTEM** — `doConsume()`'s illness branch.
- **WORLD INTERACTION** — `rolledLootFor()`, `doOpenContainer()`.
- **FIRE / COOKING** — `doFish()`.
- **PERSISTENCE** — `backfillIllnessScale()` and its wiring; `doRestart(seed)`;
  the four validator additions.
- **UI / RENDERING** and **EVENTS / UI HELPERS** — the seed display and the
  restart prompt.

Not content-only, and not mechanics-only. The single WORLD DATA value is the
mechanic's own definition, per the Data section above.

## UI changes

- **A seed readout in the side menu**, showing the run's canonical uint32.
  Placement is the first implementation decision above.
- **The Restart flow becomes a `prompt()`** where it was a `confirm()`: same
  destructive-action guard via Cancel, plus an optional seed. Blank restarts with
  a fresh world, which is the existing behaviour.
- **No other control, panel or string changes.** Nothing about Hunger, Thirst,
  the Here panel, the Move panel, the map, the craft panel or the item lists.

Three player-visible behaviour changes to declare in the changelog, none of them
a balance change:

1. **Reloading no longer rerolls.** Repeating an action from a reloaded save
   reproduces its outcome. Changing course — anything that costs game time —
   produces a genuinely different roll. This is the intended anti-save-scum
   behaviour and is the point of the pass, not a side effect.
2. **Container loot is determined by the seed and the container's location**,
   identical regardless of the order the world is explored. A loaded save's
   already-rolled containers keep the contents they were saved with; containers
   not yet opened will roll from the new seed.
3. **Illness probability is unchanged** — 35% before and after. Only the field's
   unit moved.

## Dependencies / issue linkage

- **Fulfils #51.** The pull request carries `Closes #51`.
- **Unblocks #150** (seed-aware reachability), which is filed and waiting on the
  seed and on `rolledLootFor()` being callable without mutation.
- **Unblocks the seed half of #149** (world generation options), which will build
  on the restart input this adds.
- **Unblocks #48, #50, #52 and #23's typed illness**, which were the reason #51
  exists: each needs `chance(p, key)` and none needs #9 or #10 first.
- **Does not unblock #10**, which still waits on #9 (character creation). The
  split is deliberate — see Explicitly out of scope.
- **Nothing is expected to be deferred out of this pass.** If the coding session
  cuts anything from In scope, it files an issue for the remainder and references
  it in the pull request. Two candidates worth naming in advance, should they
  prove awkward: the seed display's placement, and the validator additions — both
  genuinely severable from the rest, neither expected to be.

## Open questions for Tom

None. Scope (one pass, not two), seeding (fully seeded and persisted), loot
determinism (yes, keyed by room and container), the `illnessChance` route
(rescale with a backfill), the return shape (plain boolean) and the seed UI
(displayed, and enterable at Restart) were all settled during planning.

## After implementation

Open a pull request carrying `GAME_CONFIG.VERSION` at `0.6.0`, a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md` naming this handoff by the
path it was read at, `Closes #51`, and this file moved to
`handoffs/archive/roll-core-and-seeded-world.md` by `git mv` in the same pull
request. Record the four "Design decisions to make during implementation" choices
in the entry's Notes/assumptions. Prove the `SAVE_KEY` rotation and the backfill
by walking a v0.5.6 save through Import, and prove the save-scum rule by the
reload-and-repeat and reload-then-spend-time cases on `doFish()`. Tag the merge
commit `v0.6.0`, naming the commit explicitly.
