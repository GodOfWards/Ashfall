# Ashfall Handoff — Reproduced defect sweep: Sleep, fire spend, load atomicity, log freshness

Current shipped version: v0.4.10
Implied version-change type: PATCH
Issues: #61 — Sleep sets Energy to the Fatigue ceiling; #62 — the first campfire
  costs no firewood; #63 — a failed load leaves the broken world in place;
  #64 — "Add fuel" at the burn cap wastes a firewood; #65 — the collapsed
  fishing summary changes brightness with the last cast

**Ready to build.** The two balance calls this handoff was blocked on were
answered by Tom during planning and are specced as settled below; see "Decisions
taken during planning" for what was decided and what follows from it.

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

### `sleepAvailable()` / `estimateSleepMinutes()` — `:4185`, `:4188`

```js
function sleepAvailable(){
  return state.totalMinutes >= state.lastWakeMinute + SLEEP_COOLDOWN_MIN;
}
function estimateSleepMinutes(){
  const ceiling = clamp(100 - state.vitals.fatigue);
  const missing = Math.max(0, ceiling - state.vitals.energy);
  return missing / SLEEP_ENERGY_RATE;
}
```

`sleepAvailable()` is purely a cooldown — nothing about tiredness. The Energy
ceiling `clamp(100 - fatigue)` is currently derived in **two** places, here and
in `doSleep()`; this pass adds a third consumer and so extracts it.

### The sleep gate in `renderHereActionsPanel()` — `:5301`

```js
if(room.sleepSpot){
  if(sleepAvailable()){
    hereBox.appendChild(actionButton("Sleep " + fmtDuration(estimateSleepMinutes()), doSleep));
  } else {
    const note = document.createElement("div");
    note.style.cssText = "color:var(--ink-faint); font-size:12.5px; padding:6px 0;";
    note.textContent = "You're not tired enough to sleep yet.";
    hereBox.appendChild(note);
  }
}
```

### `canBuildFire()` / `doBuildFire()` — `:4293`, `:4297`

```js
function canBuildFire(room){
  if(room.campfireBuilt) return room.fireMinutesLeft > 0 || countInPools("firewood") >= FIRE_BUILD_WOOD;
  return countInPools("campfire_kit") >= 1;      // <-- #62: no firewood test
}
```

```js
const firstTime = !room.campfireBuilt;
if(firstTime){
  consumeFromPools("campfire_kit", 1);
  room.campfireBuilt = true;
}
const banked = room.fireMinutesLeft > 0;
if(!banked){
  consumeFromPools("firewood", FIRE_BUILD_WOOD);
  room.fireMinutesLeft = FIRE_BUILD_WOOD * FIRE_MINUTES_PER_WOOD;   // unconditional
}
ensureHeatContainer(room, "campfire", "Campfire", HEAT_CONTAINER_CAPACITY_KG);
room.heatActive = true;
advanceTime(BUILD_FIRE_MIN);
log(firstTime ? "You set up the campfire kit and get a fire going."
  : (banked ? "You relight the fire from what's left of the wood." : "You get a fire going."), "good");
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

## Decisions taken during planning

Both were Tom's calls, made after the analysis and before this handoff was
finalised. They are settled; do not re-open them during implementation.

### A — a Sleep that would restore no Energy is refused

Sleep exists to recover Energy. When there is none to recover it is not offered,
and the free Fatigue wipe goes with it.

**A correction that matters:** the predicate first proposed was *"energy <
clamp(100 - fatigue) **or** fatigue > 0"*. That is wrong and would have closed
nothing — the `or fatigue > 0` clause is true in exactly the cases the defect
lives in. Tested against the states that matter:

```
  energy fatigue | ceiling | estimate(min) | OR-predicate | energy < ceiling
    16.1     100 |       0 |           0.0 |         true |            false
      70      40 |      60 |           0.0 |         true |            false
      50      40 |      60 |          60.0 |         true |             true
      85      20 |      80 |           0.0 |         true |            false
      85       0 |     100 |          90.0 |         true |             true
      40       0 |     100 |         360.0 |         true |             true
```

The OR-predicate permits all six. **`energy < ceiling` is the correct test** —
it is true only when the Sleep would actually run. That is what is specced
below.

**The consequence, stated plainly:** at Fatigue 100 the ceiling is 0, so
`energy < 0` is never true and **Sleep is never offered at Fatigue 100.** The
Sneak lock must be worked off through `recoveryStep()`. That is the intended
price of the decision, not a side effect.

Verified survivable, from the state a chop-and-fish grind actually reaches
(`E=16.1 St=0.0 Fa=100.0 Hu=51 Th=3`), standing still and doing nothing:

```
  + 340 min  E= 30.0 St= 60.3 Fa= 36.0 Hp= 80  collapses=2
  + 460 min  E=  3.4 St= 80.0 Fa=  0.0 Hp= 72  collapses=2
```

Fatigue clears in ~460 game minutes. Two collapses occur along the way and each
grants Energy, so recovery never stalls — **there is no softlock.** The Health
lost is to thirst, which was already at 3 on entry. 460 minutes is a little
under the 8-hour `SLEEP_COOLDOWN_MIN`, so the cost of reaching Fatigue 100 is
roughly one wasted day. That is the point.

### B — a campfire kit contains its own first load of wood

A first fire costs the kit and nothing else: 3 firewood total, not 6.
`canBuildFire()` was already right; `doBuildFire()` is what changes.

This also makes the economy internally consistent, which the alternative would
not have: a kit is 3 firewood and yields `CAMPFIRE_KIT_COST × FIRE_MINUTES_PER_WOOD`
= 180 minutes, and a rebuild in an existing campfire is 3 firewood for
`FIRE_BUILD_WOOD × FIRE_MINUTES_PER_WOOD` = 180 minutes. Same wood, same burn.
What the kit buys over loose wood is the 15 crafting minutes and the permanent
`campfireBuilt` structure in that room.

---

## Rules / mechanics

### 1. Sleep: never lower Energy, and refuse a Sleep that would restore none (#61, decision A)

**1a — extract the ceiling.** It is currently derived in `doSleep()` and
`estimateSleepMinutes()`, and this pass adds a third consumer. Put it in the
STAMINA / FATIGUE sub-block beside `sleepAvailable()`:

```js
// The Energy ceiling this Sleep can reach: Fatigue caps how much rest is
// worth. Read by doSleep(), estimateSleepMinutes() and sleepRestoresEnergy().
function sleepEnergyCeiling(){ return clamp(100 - state.vitals.fatigue); }
```

`doSleep()`'s `const ceiling = clamp(100 - fatigueAtSleep)` and
`estimateSleepMinutes()`'s local both become `sleepEnergyCeiling()`.

Keep `fatigueAtSleep` as its own local in `doSleep()` — the snapshot semantics
are load-bearing and the existing comment explains them.

**1b — split the gate.** `sleepAvailable()` becomes the conjunction of two
named halves, so the two reasons a Sleep is unavailable are separately
answerable by RENDERING:

```js
function sleepOffCooldown(){ return state.totalMinutes >= state.lastWakeMinute + SLEEP_COOLDOWN_MIN; }
function sleepRestoresEnergy(){ return state.vitals.energy < sleepEnergyCeiling(); }
function sleepAvailable(){ return sleepOffCooldown() && sleepRestoresEnergy(); }
```

`doSleep()`'s existing `if(!sleepAvailable()) return;` guard is unchanged and
now blocks the zero-duration case at the action level, not only in the UI.

**1c — Energy can only rise.** Replace the assignment at `:3994`:

```js
state.vitals.energy = Math.max(state.vitals.energy, sleepEnergyCeiling());
```

`Math.max` rather than deleting the line: the loop lands on the ceiling only
approximately (it accumulates `SLEEP_ENERGY_RATE*dt` in ≤1-minute steps) and
this assignment is what snaps it exactly. Keep that, gate it against moving
downward.

After 1b this guard is belt-and-braces — `sleepAvailable()` now requires
`energy < ceiling` before entry, and the loop only raises Energy. **Keep it
anyway.** `doSleep()` writes vitals and should be correct independently of its
caller's gate; that is the same reasoning behind `getItemAt()`'s defensive
lookup.

`state.vitals.fatigue = 0` on the following line is unchanged. A Sleep now
always runs for a real duration, so the Fatigue clear is paid for.

**1d — two notes, not one.** The sleep gate in `renderHereActionsPanel()` now
has two distinct failure reasons and must say which:

```js
if(room.sleepSpot){
  if(sleepAvailable()){
    hereBox.appendChild(actionButton("Sleep " + fmtDuration(estimateSleepMinutes()), doSleep));
  } else {
    const note = document.createElement("div");
    note.style.cssText = "color:var(--ink-faint); font-size:12.5px; padding:6px 0;";
    note.textContent = sleepOffCooldown()
      ? "You're not tired enough to sleep yet."
      : "You've slept too recently to manage it again.";
    hereBox.appendChild(note);
  }
}
```

The existing string moves to the case it was always describing — no Energy
deficit — and the cooldown gets its own. Both are functional UI text and are
held to clarity rather than to the game's prose tone, per the Project Guide.

This also removes the misleading `"Sleep (0:01)"` label without touching
`fmtDuration()`: the button only renders when the Sleep will really run, so
`estimateSleepMinutes()` is never 0 at that point. **Do not "fix"
`fmtDuration()`'s `MIN_MOVE_MIN` floor here** — that is #75's.

### 2. The kit is its own first load (#62, decision B)

`canBuildFire()` is unchanged and is now correct as written. Add one comment to
its first-build branch so the asymmetry reads as intentional:

```js
function canBuildFire(room){
  if(room.campfireBuilt) return room.fireMinutesLeft > 0 || countInPools("firewood") >= FIRE_BUILD_WOOD;
  // A kit carries its own first load of wood, so a first fire needs nothing else.
  return countInPools("campfire_kit") >= 1;
}
```

`doBuildFire()`'s spend becomes:

```js
const firstTime = !room.campfireBuilt;
const banked = !firstTime && room.fireMinutesLeft > 0;
if(firstTime){
  consumeFromPools("campfire_kit", 1);
  room.campfireBuilt = true;
  room.fireMinutesLeft = CAMPFIRE_KIT_COST * FIRE_MINUTES_PER_WOOD;
} else if(!banked){
  consumeFromPools("firewood", FIRE_BUILD_WOOD);
  room.fireMinutesLeft = FIRE_BUILD_WOOD * FIRE_MINUTES_PER_WOOD;
}
```

Three things this must preserve:

- **`banked` is hoisted above the branch** because the log ternary below reads
  it. Its value is unchanged: previously it was `room.fireMinutesLeft > 0`
  evaluated after the `firstTime` block, and on a first build that was
  `undefined > 0` — false. `!firstTime && …` is the same thing, stated.
- **The duration is written as its derivation**, `CAMPFIRE_KIT_COST *
  FIRE_MINUTES_PER_WOOD`, not as `180`. The kit is three firewood; the burn is
  those three at the per-piece rate. Retuning either input must move it.
- **`log()`'s ternary is untouched.** All three messages still reach the same
  cases.

Update the constants comment above `FIRE_BUILD_WOOD` (`:4260`), which currently
reads as though every fresh burn costs `FIRE_BUILD_WOOD`. It should say a first
fire comes from the kit and a rebuild in an existing campfire costs
`FIRE_BUILD_WOOD`.

**Leave `consumeFromPools()`'s signature alone.** Giving it a return value is
the right long-term fix and is explicitly out of scope — see below.

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
4. If it returns anything, `console.warn` the detail,
   `log("That save doesn't look valid — nothing was loaded.", "warn")`
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
— so it should always be the bright one. This makes the newest line reliably
the brightest.

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
- **Exact wording of the new cooldown note.** `"You've slept too recently to
  manage it again."` is the proposed string; anything equally plain is fine.
  Record the final text.

## Open questions for Tom

None. Both are answered above under "Decisions taken during planning".

---

## Data / schema changes

**None.**

- No new or changed PLAYER STATE fields.
- No new or changed ITEM DATA SCHEMA fields, tags or categories.
- No new or changed room / container / exit schema fields.
- No change to `ITEM_REGISTRY` or any placement.

`SAVE_KEY` does not rotate. Existing browser saves keep loading. This is the
whole reason the pass is PATCH despite touching six functions.

Two consequences worth stating rather than discovering:

- **Fix 4 makes some previously-loadable saves refuse to load** — specifically
  the malformed ones that currently load halfway and break the session. That is
  the point, and it is not a save-format change.
- **A save taken mid-run at Fatigue 100 loads into a state where Sleep is
  unavailable.** Correct under decision A, and not a compatibility problem —
  the state was already reachable before this pass.

## In scope

- [ ] New `sleepEnergyCeiling()`; `doSleep()` and `estimateSleepMinutes()` read it. (#61)
- [ ] New `sleepOffCooldown()` / `sleepRestoresEnergy()`; `sleepAvailable()` is their conjunction. (#61, A)
- [ ] `doSleep()` — Energy can only rise. (#61)
- [ ] Sleep gate in `renderHereActionsPanel()` — two notes, one per reason. (#61, A)
- [ ] `doBuildFire()` — the kit carries its own first load; `canBuildFire()` gains a comment. (#62, B)
- [ ] `FIRE_BUILD_WOOD`'s constants comment updated. (#62, B)
- [ ] `renderHereActionsPanel()` — "Add fuel" withheld unless a firewood buys its
      full `FIRE_MINUTES_PER_WOOD`. (#64)
- [ ] `applyLoadedData()` — restructured so a rejected load changes nothing;
      new `validateLoadedWorld()` in PERSISTENCE. (#63)
- [ ] `log()` — a `LOG_SUMMARIES` line is always fresh. (#65)
- [ ] `GAME_CONFIG.VERSION` → `0.4.11`.
- [ ] New `CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, naming this file
      by path, recording decisions A and B under **Open questions / decisions
      resolved** and the four implementation choices under **Notes / assumptions**.
- [ ] PR description carrying `Closes #61`, `Closes #62`, `Closes #63`,
      `Closes #64`, `Closes #65`.

## Explicitly out of scope

Named because each looks adjacent and is not:

- **`consumeFromPools()` gaining a return value.** It is the root hazard behind
  both #62 and #64 — five call sites can all silently under-pay the same way.
  It is a worthwhile change and it is a different pass, because it touches
  `doCraft()` and `doDismantleCampfire()` which are otherwise untouched here.
  If this pass surfaces a reason it must happen now, file it rather than
  widening.
- **`fmtDuration()`'s `MIN_MOVE_MIN` floor.** Fix 1d removes the symptom that
  made it visible on the Sleep button. The floor itself is **#75**.
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
  arrives without warning, and decision A makes the Fatigue-100 state more
  costly without making it more legible. Not this pass's job — but worth a line
  in the changelog noting that A raises the value of #49.
- **#78** (accessibility). The new cooldown note inherits `var(--ink-faint)`,
  which fails WCAG AA at 12.5px. Match the existing note's styling anyway;
  #78 fixes both together or neither.
- **The `", Riverbank"` location label.** Reproduced and real, but it belongs to
  #42's decision about what the `building` field means — fixing it here would
  pre-empt that. Recorded as a comment on #42.

## Sections touched

Per the ARCHITECTURE comment's own vocabulary:

- **SURVIVAL / TIME SIMULATION** — the STAMINA / FATIGUE sub-block
  (`doSleep()`, `sleepAvailable()` and its two new halves,
  `sleepEnergyCeiling()`, `estimateSleepMinutes()`).
- **FIRE / COOKING** — `doBuildFire()`, `canBuildFire()`'s comment, the
  `FIRE_BUILD_WOOD` constants comment.
- **PERSISTENCE** — `applyLoadedData()`, new `validateLoadedWorld()`.
- **CORE UTILITIES** — `log()`.
- **RENDERING** — the sleep gate and the "Add fuel" gate in
  `renderHereActionsPanel()`.

Not content. Not a new mechanic. WORLD DATA is untouched.

## UI changes

- **Sleep button** — no longer offered when there is no Energy to recover,
  including at Fatigue 100. When withheld, the note now says which reason
  applies: `"You're not tired enough to sleep yet."` for no deficit,
  `"You've slept too recently to manage it again."` for the cooldown.
  The spurious `"Sleep (0:01)"` label is gone as a consequence.
- **"Add fuel to the fire"** — disappears once the fire is within
  `FIRE_MINUTES_PER_WOOD` of `FIRE_MAX_MIN`, i.e. from 300 minutes rather than
  360. No new text.
- **"Set up the campfire kit"** — unchanged in every respect. Under decision B
  the button was already correct.
- **Log** — a collapsed `fish` / `rest` / `chop` / `fuel` summary is now
  consistently the bright (`fresh`) line. No wording changes.
- **A rejected save** — same message as today; the difference is that the
  session is still playable afterwards.

No description, item name, room label or button label is reworded other than the
sleep note.

## Dependencies / issue linkage

Fulfils #61, #62, #63, #64, #65. Blocks nothing; blocked by nothing.

**Expected to leave open:** nothing new. If the pass surfaces anything not
listed here, file it as a new issue at wrap-time and reference it in the PR
rather than absorbing it.

## Validation

Every fix has a deterministic reproduction. These are the acceptance tests.

**#61 — Sleep, decision A.** Stand in a `sleepSpot` room with
`lastWakeMinute = -9999` so the cooldown is clear.

| vitals | today | required after |
|---|---|---|
| `E=70 Fa=40` | button `"Sleep (0:01)"`; Energy → **60**, Fatigue → 0, 0.00 min | **button absent**, note reads "not tired enough" |
| `E=16.1 Fa=100` | button `"Sleep (0:01)"`; Energy → **0**, Fatigue → 0, 0.00 min | **button absent**, note reads "not tired enough" |
| `E=50 Fa=40` | 60 min, Energy → 60, Fatigue → 0 | unchanged — this one must still work |
| `E=85 Fa=0` | 90 min, Energy → 100 | unchanged |
| cooldown not elapsed | note reads "not tired enough" | note reads **"slept too recently"** |

The `E=16.1 Fa=100` state is reachable by play: chop-and-fish loop from a fresh
start, twenty cycles.

**Also assert no softlock.** From `E=16.1 St=0.0 Fa=100.0`, standing still,
Fatigue must reach 0 within roughly 460 game minutes via `recoveryStep()`, with
collapses granting Energy along the way. If Fatigue plateaus, decision A has
created a trap and the pass must stop and report rather than ship.

**#62 — first campfire, decision B.** Stand in `mid_poplar_1_3` carrying
1 `campfire_kit`, 1 `box_of_matches`, **0 firewood**.
- Before and after: `canBuildFire()` true, button offered, fire lights.
- After: `fireMinutesLeft = 170` (180 minus `BUILD_FIRE_MIN`), firewood still 0,
  and `doBuildFire()` no longer calls `consumeFromPools("firewood", …)` on the
  first-build path.
- Relight path unchanged: with `campfireBuilt` true, `fireMinutesLeft = 0` and
  0 firewood, `canBuildFire()` must still be **false**.
- With `campfireBuilt` true, `fireMinutesLeft = 0` and 3 firewood: builds,
  firewood → 0, `fireMinutesLeft = 170`.
- All three log strings still reach their cases.

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
by path. Record decisions A and B under **Open questions / decisions resolved**
— including that A's first-proposed predicate was wrong and why the shipped one
differs — and the four implementation choices under **Notes / assumptions**.
Close the five issues with `Closes #NN` lines in the PR description; do not
close any by hand. File new issues for anything deferred and reference them in
the PR — and if nothing was deferred, say so in the changelog's
**Documentation** section.

After the merge, tag the merge commit `v0.4.11` by name, not by bare `HEAD`, and
verify with `git show v0.4.11:ashfall.html | grep VERSION`.
