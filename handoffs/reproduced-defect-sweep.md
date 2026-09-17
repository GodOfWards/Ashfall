# Ashfall Handoff — Reproduced defect sweep: Sleep, fire spend, load atomicity, log freshness

Current shipped version: v0.4.10
Implied version-change type: PATCH
Issues: #61 — Sleep sets Energy to the Fatigue ceiling; #62 — the first campfire
  costs no firewood; #63 — a failed load leaves the broken world in place;
  #64 — "Add fuel" at the burn cap wastes a firewood; #65 — the collapsed
  fishing summary changes brightness with the last cast

> **NOT READY TO BUILD AS-IS.** Two questions under "Open questions for Tom"
> must be answered first. Both are one-line balance calls, and everything else
> in this handoff is fully specced and buildable the moment they land. Do not
> start without them — guessing either one changes player-facing balance.

## What this is

Five defects, all found by executing the real code rather than reading it, all
PATCH, all independent of each other. They are bundled into one pass because
each is small, none needs new state, and three of the five sit in the same two
functions' worth of "spend before checking" pattern.

This is a correctness pass. It adds no mechanic, no content, and no save field.

**Every claim below was reproduced.** Where a number appears, it came out of a
run, not out of reading. The reproductions are restated here as the acceptance
tests, so the coding session does not have to rebuild the harness.

---

## Relevant existing state

Verified against `ashfall.html` at v0.4.10. Line numbers are from that file and
will shift as the pass edits; the code is quoted so the target is unambiguous.

### `doSleep()` — `:3976`

```js
function doSleep(){
  if(!sleepAvailable()) return;
  const fatigueAtSleep = state.vitals.fatigue;
  const ceiling = clamp(100 - fatigueAtSleep);
  const missingEnergy = Math.max(0, ceiling - state.vitals.energy);
  let remaining = missingEnergy / SLEEP_ENERGY_RATE;
  while(remaining > 1e-9){
    const dt = Math.min(1, remaining);
    state.totalMinutes += dt;
    applyHungerThirst(dt);
    applyWorldTicking(dt);
    state.vitals.energy = Math.min(ceiling, state.vitals.energy + SLEEP_ENERGY_RATE*dt);
    remaining -= dt;
  }
  state.vitals.energy = clamp(ceiling);          // <-- #61 lives here
  state.vitals.fatigue = 0;                      // <-- and here
  state.lastWakeMinute = state.totalMinutes;
  state.lastExertionMinute = state.totalMinutes;
  checkGameOver();
  log("You get real sleep. You wake up feeling considerably better.", "good");
  render();
}
```

`sleepAvailable()` (`:4185`) is `state.totalMinutes >= state.lastWakeMinute + SLEEP_COOLDOWN_MIN`
— purely a cooldown, nothing about tiredness.

`estimateSleepMinutes()` (`:4188`) returns `missing / SLEEP_ENERGY_RATE`, the same
quantity the loop uses, so the button and the action already agree. That is not
the bug and must stay true.

### `canBuildFire()` / `doBuildFire()` — `:4293`, `:4297`

```js
function canBuildFire(room){
  if(room.campfireBuilt) return room.fireMinutesLeft > 0 || countInPools("firewood") >= FIRE_BUILD_WOOD;
  return countInPools("campfire_kit") >= 1;      // <-- #62: no firewood test
}
```

```js
const banked = room.fireMinutesLeft > 0;
if(!banked){
  consumeFromPools("firewood", FIRE_BUILD_WOOD);
  room.fireMinutesLeft = FIRE_BUILD_WOOD * FIRE_MINUTES_PER_WOOD;   // unconditional
}
```

`consumeFromPools()` (`:3647`) takes what it can and returns nothing — there is
no shortfall signal anywhere in the file.

Relevant constants: `CAMPFIRE_KIT_COST = 3` (`:265`), `FIRE_BUILD_WOOD = 3`,
`FIRE_MINUTES_PER_WOOD = 60`, `FIRE_MAX_MIN = 360`, `BUILD_FIRE_MIN = 10`.

### `doAddFuel()` — `:4318`, and its gate at `:5341`

```js
function doAddFuel(){
  if(countInPools("firewood") < 1) return;
  const room = world[state.currentRoom];
  consumeFromPools("firewood", 1);
  room.fireMinutesLeft = Math.min((room.fireMinutesLeft || 0) + FIRE_MINUTES_PER_WOOD, FIRE_MAX_MIN);
  log("You feed the fire more wood.", "good", "fuel");
  render();
}
```

```js
if(room.fireMinutesLeft != null && countInPools("firewood") >= 1 && room.fireMinutesLeft < FIRE_MAX_MIN){
  hereBox.appendChild(actionButton("Add fuel to the fire", doAddFuel));
}
```

### `applyLoadedData()` — `:4467`

```js
function applyLoadedData(data){
  if(!data || !data.state || !data.world || !data.world[data.state.currentRoom]){
    log("That save doesn't look valid — nothing was loaded.", "warn");
    return false;
  }
  …version WARNING only, never a refusal…
  const base = makeDefaultState();
  state = { ...base, ...data.state, vitals: { ...base.vitals, ...(data.state.vitals || {}) } };
  world = data.world;                                   // <-- #63: committed before anything can fail
  doors = data.doors || doors; windows = data.windows || windows;
  detailItem = null;
  gameOver = false;
  resyncUidCounter();          // can throw
  backfillItemIds();           // can throw
  backfillLocationIds();       // can throw
  backfillContainerFields();   // can throw
  render();                    // can throw
  return true;
}
```

Both callers swallow the throw and report "nothing was loaded":

```js
// doLoadLocal()  :4541
catch(e){ log("Couldn't read a save from this browser.", "warn"); }
// doImportSave() :4556
catch(e){ log("That file couldn't be read as a save.", "warn"); }
```

`doRestart()` is wired to `#restartMenuBtn` with a direct listener and never
goes through `render()`, so it still works from a broken state. That is the
only recovery path and nothing surfaces it.

### `log()`'s tail — `:3611`

```js
if(LOG_SUMMARIES[key]){
  p.className = "";                          // summary path clears the class
  p.textContent = LOG_SUMMARIES[key](tally);
} else { …counted run keeps its class… }
logDiv.querySelectorAll("p.fresh").forEach(el=>el.classList.remove("fresh"));
if(!cls) p.classList.add("fresh");           // <-- #65: tests the CALLER's argument
```

`doFish()` is the only call site that varies `cls` within one `key` — `"good"`
on a bite, `null` on a miss. `rest`, `chop` and `fuel` each pass a constant.

---

## Rules / mechanics

### 1. Sleep must never lower Energy (#61)

Replace the assignment at `:3994` so it can only raise:

```js
state.vitals.energy = Math.max(state.vitals.energy, clamp(ceiling));
```

`Math.max` rather than deleting the line: the loop lands on `ceiling` only
approximately (it accumulates `SLEEP_ENERGY_RATE*dt` in ≤1-minute steps), and
the existing assignment is what snaps it exactly. Keep that, gate it on not
moving downward.

**After this change, `state.vitals.fatigue = 0` on the next line still runs
unconditionally.** That is the subject of Open question A and must not be
touched until A is answered.

### 2. The gate and the spend must agree about a first fire (#62)

Subject to Open question B. Both options are specced; implement exactly one.

**Option B1 — make the gate match the spend.**

```js
function canBuildFire(room){
  if(room.campfireBuilt) return room.fireMinutesLeft > 0 || countInPools("firewood") >= FIRE_BUILD_WOOD;
  return countInPools("campfire_kit") >= 1 && countInPools("firewood") >= FIRE_BUILD_WOOD;
}
```

`doBuildFire()` is unchanged. A first fire costs 1 kit + 3 firewood = 6 wood
total. The button is withheld when the player cannot pay, which is how every
other gated action in the file behaves.

**Option B2 — make the spend match the gate.**

```js
if(firstTime){
  consumeFromPools("campfire_kit", 1);
  room.campfireBuilt = true;
  room.fireMinutesLeft = CAMPFIRE_KIT_COST * FIRE_MINUTES_PER_WOOD;
} else {
  const banked = room.fireMinutesLeft > 0;
  if(!banked){
    consumeFromPools("firewood", FIRE_BUILD_WOOD);
    room.fireMinutesLeft = FIRE_BUILD_WOOD * FIRE_MINUTES_PER_WOOD;
  }
}
```

`canBuildFire()` is unchanged. The kit *is* its own first load; a first fire
costs 3 wood and the code stops pretending otherwise. Note the derivation is
written as `CAMPFIRE_KIT_COST * FIRE_MINUTES_PER_WOOD`, not `180` — per the
Project Guide's rule that a derived value is written as its derivation.

Under B2, add a one-line comment on `canBuildFire()`'s first-build branch
saying the kit carries its own wood, so the asymmetry reads as intentional.

**Under both options:** leave `consumeFromPools()`'s signature alone. Giving it
a return value is the right long-term fix and is explicitly out of scope here —
see "Explicitly out of scope".

### 3. "Add fuel" only when a firewood buys its full value (#64)

Tighten the render gate at `:5341`:

```js
if(room.fireMinutesLeft != null && countInPools("firewood") >= 1
   && room.fireMinutesLeft <= FIRE_MAX_MIN - FIRE_MINUTES_PER_WOOD){
  hereBox.appendChild(actionButton("Add fuel to the fire", doAddFuel));
}
```

`doAddFuel()` itself is unchanged — its `Math.min` remains correct and is now
never the binding constraint from the UI path.

This makes the cap mean "you cannot usefully add more", which is what a player
reading the button already assumes. `renderLocationPanel()` already prints the
fire's remaining fuel, so the button's disappearance is explicable on screen.

**Do not add a warning line instead.** A `"warn"` would break the `fuel` tally
run, and the collapsed summary (`"You feed three more pieces of wood into the
fire."`) is the better reading.

**Whether Add fuel should cost game time is out of scope** — see below.

### 4. The load must be atomic (#63)

Restructure `applyLoadedData()` so nothing is committed until everything has
succeeded. Shape:

1. Keep the existing cheap guard and both version warnings exactly as they are.
2. Build `nextState`, `nextWorld`, `nextDoors`, `nextWindows` as locals.
3. Run a new `validateLoadedWorld(nextWorld, nextState)` over the locals. It
   returns an array of problem strings, empty on success — the shape
   `validateItemRegistry()` (`:4495`) and `validateLocations()` (`:4513`)
   already use.
4. If it returns anything, `log("That save doesn't look valid — nothing was loaded.", "warn")`
   and `return false`. The module-level `state` / `world` / `doors` / `windows`
   have not been touched.
5. Only then assign the four bindings, run the four backfills and `render()`.

`validateLoadedWorld()` must cover exactly the four shapes that throw today,
and no more — this is a shape check, not a schema validator:

- every room in `nextWorld` has `Array.isArray(room.floor)`
- every room has `Array.isArray(room.exits)`
- every room has `Array.isArray(room.containers)`
- `nextState.inventory` exists and `Array.isArray(nextState.inventory.items)`
- every populated `CONTAINER_SLOTS` entry on `nextState` has an array `items`

`carContainers` is optional on a room and must stay optional — check it only
when present.

**The backfills run after validation, not before.** They are repair passes for
old-but-well-formed saves; they are not the thing that makes a malformed save
safe.

**Put `validateLoadedWorld()` in PERSISTENCE**, next to the backfills, not in
the dev-helper block — unlike its two siblings it is wired into a real code
path and runs on every load.

### 5. Log freshness follows the rendered line, not the caller (#65)

In the summary branch, mark the line fresh explicitly, and skip the `cls`-based
decision for it:

```js
let summarised = false;
if(LOG_SUMMARIES[key]){
  p.className = "";
  p.textContent = LOG_SUMMARIES[key](tally);
  summarised = true;
} else { … }
logDiv.querySelectorAll("p.fresh").forEach(el=>el.classList.remove("fresh"));
if(summarised || !cls) p.classList.add("fresh");
```

A `LOG_SUMMARIES` line always renders unclassed — the existing comment says so
— so it should always be the bright one. This is the "follow the rendered line"
option from #65; it makes the newest line reliably the brightest.

Update the comment above `p.className = ""` to say that the summary is
unclassed *and therefore fresh*, so the coupling is stated rather than implied.

---

## Design decisions to make during implementation

Narrow calls the coding session can make and must record in the changelog's
Notes / assumptions section.

- **Whether `validateLoadedWorld()` returns strings or booleans.** Strings match
  the two existing validators and are more useful in a `console.warn`; a boolean
  is less code. Recommended: strings, and `console.warn` them the way
  `validateLocations()` does, so a failed import leaves something diagnosable in
  the console even though the player-facing message stays generic.
- **Whether the two `catch` messages change.** Once the load is atomic,
  `"That file couldn't be read as a save."` is no longer a lie, so leaving both
  alone is defensible. A distinct third message for a shape failure is also
  defensible. Recommended: leave them, and let the validator's `console.warn`
  carry the detail. Record whichever.
- **Where the `summarised` flag lives in `log()`.** A local as above, or
  re-testing `LOG_SUMMARIES[key]` at the bottom. Recommended: the local — the
  second test would be a second source of truth for the same condition.

## Open questions for Tom

**This section is non-empty, so the handoff is not ready to build as-is.** Both
are balance calls with player-facing consequences, which per the Handoff Guide
is exactly what must not be decided by a coding session.

### A. Should a zero-duration Sleep still clear all Fatigue? (#61)

After fix 1, Energy can no longer drop. But when `energy >= ceiling` the loop
still does not run, and `state.vitals.fatigue = 0` still executes — so Sleep
remains a way to delete up to 100 Fatigue in **zero game minutes**, and it is
strictly cheaper than the ~200 minutes of in-system recovery
(`FATIGUE_RECOVERY_RATE = 0.5`/min at the ×4 Energy surcharge in
`recoveryStep()`).

Three answers, each fully buildable:

- **A1 — leave it.** Sleep clears Fatigue, full stop; the zero-duration case is
  a quirk, not an exploit, because it still burns the 8-hour `SLEEP_COOLDOWN_MIN`.
  No further code change. The `"Sleep (0:01)"` button label stays.
- **A2 — refuse it.** `sleepAvailable()` gains a second condition: there must be
  something to sleep off (`state.vitals.energy < clamp(100 - state.vitals.fatigue)`
  or `state.vitals.fatigue > 0`). The button is replaced by the existing note.
  **If A2 is chosen, the note's wording must change too** — it currently reads
  `"You're not tired enough to sleep yet."` (`:5307`) while being gated purely
  on the cooldown, which is already misleading and becomes more so.
- **A3 — charge for it.** A zero-Energy-deficit Sleep still runs for the time
  the Fatigue clear is worth. Needs a rate, which is a new balance constant.
  Largest change; the only one that makes Sleep a *priced* Fatigue cure rather
  than a free one or a refused one.

Recommended: **A2**, with the note reworded. It keeps Sleep meaning "recover
Energy", makes the Fatigue clear a consequence of sleeping rather than a
mechanic to farm, and needs no new constant. But this is a real design call
about how expensive the Fatigue-100 Sneak lock should be to escape, and that is
not mine to make.

### B. Does a campfire kit contain its own first load of wood? (#62)

B1 (gate matches spend, first fire costs 6 wood) or B2 (spend matches gate,
first fire costs 3 wood). Both are specced above; pick one.

Context for the call: firewood is **strictly finite in a run** — 17 hand-placed,
plus 5 `hasTree` rooms × 6 from `doChopTree()`, which sets `hasTree = false`
permanently. The `fuel_fire` pool that would otherwise supply more never rolls
(#66). **47 firewood for a whole playthrough.** B1 halves how much fire that
buys relative to today's behaviour; B2 blesses today's behaviour and makes the
code honest about it.

Recommended: **B1.** It is the conservative reading, it keeps `FIRE_BUILD_WOOD`
meaning what its name says, and it makes fire a real cost in a game where wood
does not renew. B2 is defensible fiction and I would not argue hard against it.

---

## Data / schema changes

**None.**

- No new or changed PLAYER STATE fields.
- No new or changed ITEM DATA SCHEMA fields, tags or categories.
- No new or changed room / container / exit schema fields.
- No change to `ITEM_REGISTRY` or any placement.

`SAVE_KEY` does not rotate. Existing browser saves keep loading. This is the
whole reason the pass is PATCH despite touching five functions.

One consequence worth stating: **fix 4 makes some previously-loadable saves
refuse to load** — specifically the malformed ones that currently load halfway
and break the session. That is the point, and it is not a save-format change.

## In scope

- [ ] `doSleep()` — Energy can no longer be lowered by sleeping. (#61)
- [ ] `canBuildFire()` **or** `doBuildFire()` — gate and spend agree, per answer B. (#62)
- [ ] `renderHereActionsPanel()` — "Add fuel" withheld unless a firewood buys its
      full `FIRE_MINUTES_PER_WOOD`. (#64)
- [ ] `applyLoadedData()` — restructured so a rejected load changes nothing;
      new `validateLoadedWorld()` in PERSISTENCE. (#63)
- [ ] `log()` — a `LOG_SUMMARIES` line is always fresh. (#65)
- [ ] Per answer A: `sleepAvailable()` and the sleep note's wording, if A2.
- [ ] `GAME_CONFIG.VERSION` → `0.4.11`.
- [ ] New `CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, naming this file
      by path, recording answers A and B and the three implementation choices.
- [ ] PR description carrying `Closes #61`, `Closes #62`, `Closes #63`,
      `Closes #64`, `Closes #65` — and `Closes #61` **only if A is resolved in
      the same pass**; if A is deferred, say so and leave #61 open with the
      Energy half noted as shipped.

## Explicitly out of scope

Named because each looks adjacent and is not:

- **`consumeFromPools()` gaining a return value.** It is the root hazard behind
  both #62 and #64 — five call sites can all silently under-pay the same way.
  It is a worthwhile change and it is a different pass, because it touches
  `doCraft()` and `doDismantleCampfire()` which are otherwise untouched here.
  If this pass surfaces a reason it must happen now, file it rather than
  widening.
- **Whether "Add fuel", "Put out the fire" and Eat/Drink should cost game time.**
  All three are currently free while every other action charges. That is a
  balance question spanning three subsystems. #64 notes it; this pass does not
  answer it.
- **#66** (ten spawn pools never roll) and **#67** (single-copy tool gates).
  Both are cited above as context for the firewood economy. Neither is touched.
  Do not "fix" the firewood supply while here.
- **#29** (re-judge the log's size and 50-entry cap). Fix 5 touches `log()`;
  it must not touch `LOG_MAX_ENTRIES` or `#log`'s `max-height`.
- **#49** (player condition UI). Fatigue is displayed nowhere, which is why #61
  arrives without warning. Not this pass's job.
- **The `", Riverbank"` location label.** Reproduced and real, but it belongs to
  #42's decision about what the `building` field means — fixing it here would
  pre-empt that. Recorded as a comment on #42.

## Sections touched

Per the ARCHITECTURE comment's own vocabulary:

- **SURVIVAL / TIME SIMULATION** — the STAMINA / FATIGUE sub-block (`doSleep()`,
  and `sleepAvailable()` under A2).
- **FIRE / COOKING** — `canBuildFire()` or `doBuildFire()`.
- **PERSISTENCE** — `applyLoadedData()`, new `validateLoadedWorld()`.
- **CORE UTILITIES** — `log()`.
- **RENDERING** — one gate in `renderHereActionsPanel()`, and the sleep note's
  wording under A2.

Not content. Not a new mechanic. WORLD DATA is untouched.

## UI changes

- **Sleep button** — under A2 it disappears when there is nothing to sleep off,
  and the accompanying note is reworded. Under A1 or A3, no change.
- **"Add fuel to the fire"** — disappears once the fire is within
  `FIRE_MINUTES_PER_WOOD` of `FIRE_MAX_MIN`, i.e. from 300 minutes rather than
  360. No new text.
- **"Set up the campfire kit"** — under B1 it is withheld when the player lacks
  3 firewood. Under B2, no change.
- **Log** — a collapsed `fish` / `rest` / `chop` / `fuel` summary is now
  consistently the bright (`fresh`) line. No wording changes.
- **A rejected save** — same message as today; the difference is that the
  session is still playable afterwards.

No description, item name, room label or button label is reworded except the
sleep note under A2.

## Dependencies / issue linkage

Fulfils #61, #62, #63, #64, #65. Blocks nothing; blocked by nothing except
answers A and B.

**Expected to leave open:** nothing new, if A and B are both answered. If A is
deferred, #61 stays open carrying only the Fatigue half.

If the pass surfaces anything not listed here, file it as a new issue at
wrap-time and reference it in the PR rather than absorbing it.

## Validation

Every fix has a deterministic reproduction. These are the acceptance tests.

**#61 — Sleep.** Set `vitals = { energy: 70, fatigue: 40 }`, `lastWakeMinute = -9999`,
stand in a `sleepSpot` room, Sleep.
- Before: Energy 70 → **60**, Fatigue 40 → 0, 0.00 minutes elapsed.
- After: Energy stays **70**. Fatigue per answer A.

The harder case, reached by play: chop-and-fish loop from a fresh start, twenty
cycles, lands on `E=16.1 St=0.0 Fa=100.0`. Sleeping there currently sets Energy
to **0**. After the fix it must stay 16.1.

**#62 — first campfire.** Stand in `mid_poplar_1_3` carrying 1 `campfire_kit`,
1 `box_of_matches`, **0 firewood**.
- Before: `canBuildFire()` true; after building, `fireMinutesLeft = 170`, firewood 0.
- After B1: `canBuildFire()` false, button absent. With 3 firewood: builds, firewood → 0.
- After B2: builds, `fireMinutesLeft = 170`, and the code no longer calls
  `consumeFromPools("firewood", …)` on that path.

**#64 — add fuel.** Lit fire, `fireMinutesLeft = 350`, carrying firewood in a
backpack (the base 3 kg inventory will not hold 5 × 0.8 kg — this tripped the
original investigation and will trip the test).
- Before: button shown; one firewood spent; `fireMinutesLeft` 350 → 360.
- After: button absent at 350. Present at 300. At 300, one firewood → 360.

**#63 — load atomicity.** Twelve shapes; the four that must now be rejected
cleanly, with `state` / `world` / `doors` / `windows` provably unchanged:
missing `room.floor`, missing `room.containers`, missing `room.exits`,
non-array `inventory.items`. The three already rejected (empty object, missing
`world`, unknown `currentRoom`) must still return `false`. **A well-formed save
must still round-trip byte-identically** — `serializeGame()` output, loaded and
re-serialised, is byte-identical today and must remain so.

**#65 — log.** Three casts ending on a bite, then three ending on a miss.
- Before: `[(none)]` then `[fresh]` — same text, different class.
- After: `[fresh]` both times.
- Regression guards: a `warn` line still breaks a tally run into separate lines;
  the 50-entry cap still trims from the front; `craft:` runs still keep their
  `good` class and their `×N` counter.

**Diff discipline.** `git diff origin/main...HEAD -- ashfall.html` is the proof
of what moved. WORLD DATA must show zero changes — if the diff touches any
`build*()` function, something has gone wrong.

## After implementation

Open a pull request carrying the `GAME_CONFIG.VERSION` bump to `0.4.11` and a
new `CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, referencing this handoff
by path and recording answers A and B plus the three implementation choices in
**Open questions / decisions resolved**. Close the five issues with `Closes #NN`
lines in the PR description; do not close any by hand. File new issues for
anything deferred and reference them in the PR — and if nothing was deferred,
say so in the changelog's **Documentation** section.

After the merge, tag the merge commit `v0.4.11` by name, not by bare `HEAD`, and
verify with `git show v0.4.11:ashfall.html | grep VERSION`.
