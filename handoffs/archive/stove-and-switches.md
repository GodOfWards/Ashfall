# Ashfall Handoff — The stove needs power or a flame, and a load's own switch

Current shipped version: v0.9.1
Implied version-change type: PATCH (no new persistent state: `state.power.switches` already exists and saves)
Issue: #259 — A gas stove's igniter needs power — without it, burners light with a match and the oven not at all
Also closes: #264 — An appliance's own switch has no control; #266 — One left-on chance for every load

## What this is

The 0.9.2 bundle after Acorn's wiring. It has three parts, and they only make
sense together:

1. **The stove becomes a load** on its kitchen circuit. With power it lights
   itself, as today. Without power, a burner is lit by hand with a small flame.
2. **A load's own switch gets a control**, on the Fridge and Freezer tabs,
   through the Here strip and the device pop-up. The switch action is built so
   the electrical view (#242) can call it later.
3. **Each appliance carries its own left-on chance** instead of one 0.9 for
   every load. A gas range and a smoke alarm have no user switch at all: they
   are always on and offer no control.

Part 3 is what makes part 1 safe. With one chance for everything, one stove in
ten would start switched off, with no control and no explanation.

From #259: "Electric-ignition burners need power to spark. In an outage they
light with a match: hold a lit match at the burner and turn the knob to low."
([GE Appliances](https://products.geappliances.com/appliance/gea-support-search-content?contentId=19226))

## Relevant existing state

Verified against `ashfall.html` at v0.9.1.

**Switches (SIMULATION, POWER).**
- `SWITCH_LEFT_ON_CHANCE = 0.9` (CONFIG, beside the breaker constants). It is
  read by `switchOnIn(power, seed, loadId)`, which returns the stored boolean
  in `power.switches[loadId]`, else
  `chanceFor(seed, SWITCH_LEFT_ON_CHANCE, ["power", "switch", loadId])`.
  Pure and render-safe.
- `switchOnIn()` has two callers:
  - `powerSnapshot()`, where `powered[l.id]` needs the switch on. It has the
    `appliances` table and the load `l` in hand.
  - `effectiveAge()`, which passes `{ switches:{} }` to get a load's
    as-found state for items untouched since the collapse.
- Nothing in play writes `state.power.switches`. Only `simulatePower()`'s
  script does (`power.switches[c.switch] = !!c.on`).
- The readers and writers beside `switchOnIn()` follow one convention: "A
  default is never written: a writer that returns an entry to its default
  deletes it" (see `setBreakerIn()`).
- `isPowered(loadId)` reads `powerNow.powered`.
- `containerPowered(roomId, container)` looks up
  `POWER_NET.containerLoad[roomId + KEY_SEP + container.id]` and falls back
  to `gridUp()` for a container no load claims.

**Appliances and the template (WORLD DATA, POWER SCHEMA).**
- `APPLIANCES` entries: `fridge_freezer`, `led_light`, `bath_fan`,
  `range_hood`, `smoke_alarm`. The shape is
  `{ name, watts, volts, startWatts?, dutyCycle?, cycleMinutes? }`, and the
  comment above lists each one's source.
- `WIRING_TEMPLATES.apartment.fixtures` has nine entries. `KITCHEN 2`
  (`kitchen2`, 20 A, 120 V) carries no fixture. The comment says so: "it is
  the second countertop circuit, whose load is whatever gets plugged in."
- A fixture's `containers` are container ids in the room its `role` maps to.
  `expandWiring()` writes `containerLoad` from them.
- `validateWiring()` reports a fixture container missing from its room.

**Stoves.** There are four, all in Acorn, each tagged `["device","heat"]`:

| Room | Container id |
|---|---|
| `kitchen` (2A) | `stove` |
| `twobee_kitchen` (2B) | `stove` |
| `onea_kitchen` (1A) | **`stove1a`** |
| `onebee` (1B, all roles on one room) | `stove` |

- `RENAMED_CONTAINERS` (PERSISTENCE) is `{ onea_kitchen: { fridge1a:"fridge", freezer1a:"freezer" } }`.
  It is read by `backfillRenamedContainers()` on every load.
- `roomStove(room)` finds the container tagged both `device` and `heat`.
- `doLightStove()`:
  - sets `room.heatActive = true`, spends `LIGHT_STOVE_MIN` (5) and logs
    "You light the stove.";
  - its comment says "A gas stove lights itself, so it needs no fire-starter
    and spends none (#234)";
  - the same comment names `stove1a` as the reason it never creates a
    container (#177).
- `doExtinguish()` turns the stove off.
- The stove's timer (`doAddStoveTimer()`, `tickStoveTimers()`) "needs
  neither the stove on nor power". This pass leaves that as it is (#270).

**Flame sources (ACTIONS).**
- `findFireStarter()` finds the first carried item tagged `fire-starter` with
  `durability.current > 0`. Those are `box_of_matches` and `lighter`.
- `consumeMatchUse()` spends one use, splices the item at zero, logs "The
  <name> is spent.", and returns true.
- `hasMatchUses()` is `!!findFireStarter()`.
- `hasTool(tag)` checks carried items. `propane_torch` is tagged `["heat"]`
  and has no durability or fuel.
- The campfire's note when nothing will light it is "Nothing you're carrying
  will light a fire." (`renderHereActionsPanel()`).

**The Here strip and the device pop-up (UI/RENDERING).**
- The strip (`#worldStrip`, holding `#worldDeviceState` and
  `#deviceOptionsBtn`) shows only while the selected tab is either a
  container tagged `device` or a panel's or board's tab.
- The strip's text is the stove's `stoveOnText() · stoveTimerText()`, or
  `deviceStripText()` for a panel.
- `resolveDeviceTarget()` accepts a `{ kind:"container" }` target only if
  the container is tagged `device`.
- `renderDevicePop()` draws the container's name, then returns early unless
  it is tagged `heat` (the stove). The stove's controls are "Turn on the
  stove <5 min>" / "Turn off the stove", then the timer's step buttons.
- `device` also drives `shownWithoutSearch()`. Fridges are tagged only
  `fridge` / `freezer`, so they need a search to show. **That does not
  change.**

## Rules / mechanics

### Per-appliance switch behaviour (#266)

Every `APPLIANCES` entry declares exactly one of:

- `leftOnChance: p`: its switch is found on with probability `p`, rolled per
  load with the existing key `["power", "switch", loadId]`;
- `switchless: true`: it has no user switch. `switchOnIn()` returns `true`,
  ignores any stored entry, and no control is ever offered for it.

Values. Every chance is a judgment call, retunable, and chosen by Tom:

| Appliance | Setting |
|---|---|
| `fridge_freezer` | `leftOnChance: 0.99` |
| `led_light` | `leftOnChance: 0.3` |
| `range_hood` | `leftOnChance: 0.05` |
| `bath_fan` | `leftOnChance: 0.05` |
| `smoke_alarm` | `switchless: true` (hardwired, no user switch) |
| `gas_range` (new, below) | `switchless: true` (plugged in, no power switch) |

`switchOnIn()` takes the appliance entry, so both callers resolve it:
`powerSnapshot()` from `appliances[l.appliance]`, and `effectiveAge()` from
`APPLIANCES[POWER_NET.loads[loadId].appliance]`. `SWITCH_LEFT_ON_CHANCE` is
removed: every appliance states its own figure, so a fallback would be a
second source of truth. `validateWiring()` reports an appliance that declares
neither field, or both.

### The stove as a load (#259)

- New appliance: `gas_range: { name:"Gas range", watts:4, volts:120, switchless:true }`.
  - The figure is a pick inside the sourced range. In standby a gas range
    powers only its control board, clock and display, "generally less than 5
    watts" ([Engineer Fix](https://engineerfix.com/how-many-watts-does-a-gas-oven-use/)).
  - The spark module's burst while igniting is left unmodelled: no
    `startWatts`.
  - The 372–432 W glow-bar figure is the oven's igniter. The oven isn't
    modelled (#259).
  - Add it to the source comment above `APPLIANCES`.
- New template fixture, in `apartment.fixtures` straight after `fridge`:
  `{ key:"stove", appliance:"gas_range", circuit:"kitchen2", role:"kitchen", containers:["stove"] }`.
  - NEC 210.52(B)(2) Exception No. 2 allows "receptacles installed to provide
    power for supplemental equipment and lighting on gas-fired ranges" on a
    small-appliance branch circuit.
  - Replace the template comment's "KITCHEN 2 has no fixture" with this
    citation. `KITCHEN 2` is still the countertop circuit as well.
  - It expands to `acorn.<unit>.stove`: four new loads, 44 in all.
- **1A's stove is renamed `stove1a` → `stove`**, so the template's
  `containers` find it. This is the same shape as v0.9.1's fridge rename:
  - rename the id in `buildAcornApartments()`;
  - add `stove1a:"stove"` to `RENAMED_CONTAINERS.onea_kitchen`, and extend
    the comment line above that table;
  - rewrite the `doLightStove()` comment so it no longer names `stove1a`.
    The #177 reason (never create a container by id) stays, stated without
    the old id.

### Lighting the stove

Whether the stove has power is
`containerPowered(state.currentRoom, roomStove(room))`. That is the load's
`isPowered()` for all four wired stoves, and the grid fallback for any stove
no load claims.

| Stove has power | Flame source carried | Result |
|---|---|---|
| yes | — | Lights itself, as today: `heatActive = true`, `LIGHT_STOVE_MIN`, log "You light the stove." Spends nothing. |
| no | a carried `heat` tool (the propane torch) | Lit by hand. Spends nothing, since the torch has no fuel model. `LIGHT_STOVE_MIN`, log "You light a burner by hand." |
| no | a `fire-starter` with uses (matches, lighter) | Lit by hand. `consumeMatchUse()` spends one use, then `LIGHT_STOVE_MIN`, log "You light a burner by hand." |
| no | none | Can't be lit. No action runs. |

- **The torch is checked before a fire-starter**, so a player carrying both
  keeps their matches.
- **Mechanics check tags only:** `hasTool("heat")` and `findFireStarter()`.
  No item names.
- **Power matters only at the moment of lighting.** A lit burner keeps
  burning when its power is lost: the gas valve is manual and the flame
  holds itself. So a power loss never sets `heatActive` false, and nothing in
  SIMULATION changes for the stove.
- `doExtinguish()` is unchanged.
- The oven isn't modelled.
- The kitchen text ("no power needed to light it") is not touched here. It
  is #235's.

### A load's switch control (#264)

- **New writer** beside `switchOnIn()`: `setSwitchIn(power, seed, loadId, appliance, on)`.
  - It stores `on`, or deletes the entry when `on` equals the load's rolled
    starting state, per the existing no-default-written convention.
  - It is a no-op for a `switchless` appliance.
- **New action** in ACTIONS: `doSwitchLoad(loadId, on)`.
  - It returns early for an unknown load, a switchless one, or one already
    in that position.
  - Otherwise it calls `setSwitchIn(state.power, …)`, logs
    `You switch the <appliance name, lower-cased> ${on ? "on" : "off"}.`
    ("You switch the fridge-freezer on."), and calls `render()`.
  - It is instant, and the next step's resolution sees it, as
    `doSwitchBreaker()` does. Switching a fridge on can start it, with its
    surge, through the existing engine.
  - Nothing else writes `state.power.switches` in play. #242 will call
    `doSwitchLoad()`.
- **Which containers get it:** any room container that
  `POWER_NET.containerLoad` ties to a load whose appliance is not
  `switchless`.
  - Today that is the Fridge and Freezer in each of Acorn's four kitchens.
    Both tabs control the one `fridge_freezer` load.
  - No tag is added, and `shownWithoutSearch()` is unchanged, so a fridge
    is still found by searching.
  - The stove is claimed by a load but its appliance is switchless, so it
    gets no switch control and keeps exactly its current strip and pop-up.

## Data / schema changes

- **APPLIANCES schema:** exactly one of `leftOnChance` (0–1) or
  `switchless: true` per entry. Update the POWER SCHEMA comment.
- **New appliance:** `gas_range`.
- **New template fixture:** `apartment.fixtures` `stove`.
- **Container id:** 1A's `stove1a` → `stove`, with the `RENAMED_CONTAINERS`
  entry.
- **Removed constant:** `SWITCH_LEFT_ON_CHANCE`. Update the judgment-call
  comment above it, which names it.
- **No state fields.** `state.power.switches` already exists and saves.

## In scope

- Everything under Rules / mechanics.
- `validateWiring()`:
  - reports an appliance with neither or both of `leftOnChance` and
    `switchless`;
  - still passes with no problems on a new game, and 1A's stove resolves.
- The UI changes below.

## Explicitly out of scope

- **The stove timer and power** (#270). It keeps running unpowered.
- **Candles** as a flame source (#271). They need a lit state, which is new
  persistent state.
- **The propane torch lighting campfires**, and the rest of #96. Only the
  stove reads the torch here.
- **Room text following power** (#235), including the kitchen's "no power
  needed to light it".
- **Switch controls for loads that aren't containers** (lights, hood, fan).
  They come with the electrical view (#242), which calls `doSwitchLoad()`.
- **A clock or display readout** showing the stove's power.
- **Meters and nameplates** (#249). No watts are shown anywhere.
- **The oven.** Fridge coasting on its cold (#217).
- **Templates carrying windows and doors** (#267), and the other buildings.

## Sections touched

- **WORLD DATA:**
  - `APPLIANCES` and the POWER SCHEMA comment;
  - `WIRING_TEMPLATES.apartment` and its comment;
  - 1A's stove id in `buildAcornApartments()`.
- **CONFIG:** removal of `SWITCH_LEFT_ON_CHANCE`, and its comment.
- **SIMULATION (POWER):**
  - `switchOnIn()`'s signature and rule;
  - new `setSwitchIn()`;
  - the calls in `powerSnapshot()` and `effectiveAge()`.
- **ACTIONS:** `doLightStove()` and its comment; new `doSwitchLoad()`.
- **PERSISTENCE:** `RENAMED_CONTAINERS` and its comment.
- **UI/RENDERING:**
  - the Here strip block in `render()`;
  - `resolveDeviceTarget()`;
  - `renderDevicePop()` and its comment.
- **Dev seam:** `validateWiring()`. `simulatePower()` also needs the rule
  applied: it resolves switches through `powerSnapshot()`, so it follows
  automatically. Check that a script entry for a switchless load is ignored.

This is not a content pass. The fixture, the appliance and the rename are the
mechanic's own definition (CLAUDE.md, "The one case that touches both").
Without them the stove reads no power.

## UI changes

All wording is functional UI text, held to clarity. Retunable.

- **Fridge and Freezer tabs** (a container tied to a switchable load) now
  show the Here strip. Its text is what the player can observe with the door
  open:
  - powered: `Light on`
  - unpowered with its switch on: `Dark · switched on` (a tripped breaker, a
    dead grid)
  - unpowered with its switch off: `Dark · switched off`

  Device Options opens the device pop-up: the container's name in bold, the
  same status line, then one button, `Switch on` or `Switch off`, calling
  `doSwitchLoad()`. It stays open and updates in place, as the stove's does.
- **The stove's pop-up:**
  - With power: unchanged, `Turn on the stove <5 min>`.
  - Unpowered, with a carried `heat` tool or a fire-starter:
    `Light the stove by hand <5 min>`.
  - Unpowered with neither: no light button, and a note line in the pop-up,
    `Nothing you're carrying will light it.`, styled as the Here panel's
    campfire note.
  - Turn off and the timer buttons are unchanged.
  - The stove's strip text is unchanged.
- **Log lines:**
  - "You light a burner by hand." (unpowered lighting)
  - "You switch the fridge-freezer on." / "…off."
  - "The <name> is spent." still comes from `consumeMatchUse()`.

## Design decisions to make during implementation

- **How `renderDevicePop()` branches.** It needs a stove branch and a
  switchable-load branch, where today it has one early return. The shape
  and the helper names are yours. Keep "the stove" found by
  `roomStove()`/`heat`, and "a switchable load" found through
  `containerLoad`. Record the shape in the changelog.
- **Where the note line gets its style**: reuse `hereNote()` or an
  equivalent inside the pop-up. Record which.
- **How `resolveDeviceTarget()` accepts the new target.** Widen its test to
  `device`-tagged or tied to a switchable load, through one shared
  predicate that the strip also uses, so the two can't disagree. Name the
  predicate in the changelog.

## Dependencies / issue linkage

- Fulfils #259, #264 and #266. The PR carries `Closes #259`, `Closes #264`
  and `Closes #266`.
- Unblocks #242, which calls `doSwitchLoad()`, and #235, whose kitchen text
  can now describe a stove that needs power.
- **Save compatibility, accepted:**
  - Changing the fridge's chance from 0.9 to 0.99 turns some 0.9.1 fridges
    that were found off to on. The roll key is unchanged, and raising `p`
    only flips off → on.
  - Lights go from 0.9 to 0.3, which is invisible: nothing reads a light.
  - Items already stamped keep their ages. What they gain from here uses the
    new state.
  - A 0.9.1 save whose 1A stove was never opened may roll different contents
    under the new id, as v0.9.1's freezer rename noted.
- Nothing is expected to be deferred beyond #270 and #271, both filed. If
  implementation surfaces more, file it.

## Open questions for Tom

None. Every design question was settled in planning:

- #266 folded in;
- the control keyed on the wiring, with the search unchanged;
- the light-based wording;
- the flame sources (fire-starter, then the torch; candles deferred);
- the left-on values;
- the timer deferred.

## After implementation

Open one pull request with:

- the PATCH version bump;
- a new `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, citing
  `Implements: handoffs/stove-and-switches.md` and recording the three
  implementation decisions above;
- this handoff moved with `git mv` to `handoffs/archive/`;
- `Closes #259`, `Closes #264` and `Closes #266` in the description.
