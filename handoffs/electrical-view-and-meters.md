# Ashfall Handoff — The electrical view, meters and nameplates, and room text that follows power

Current shipped version: v0.9.2
Implied version-change type: PATCH (no new persistent state: the view's toggle is a preference kept outside the save, and the meters are ordinary items)
Issue: #242 — Electrical view: a Menu toggle that turns Inventory and Here into their electrical views
Also closes: #235 — Room text follows power; #249 — Meters and nameplates; #267 — Wiring templates don't carry windows and interior doors; #270 — The stove timer runs without power

## What this is

The power PATCHes that don't wait on #237, as one pass in six phases. Build them
in this order, because each phase leans on the ones before it:

1. **Templates carry windows and interior doors** (#267). A refactor with no
   behavior change, proven by a diff of the expanded definitions.
2. **The stove timer is a wind-up timer** (#270). Only the comment changes.
3. **Room text follows power** (#235). Nine descriptions get a variant for
   when their power is on and one for when it is off.
4. **The electrical view** (#242). A toggle in the ☰ Menu turns Inventory and
   Here into their electrical views.
5. **Nameplates and meters** (#249, mechanics and item definitions). Each load
   shows its nameplate, and two new tools read what the network is doing.
6. **The meters' placements** (#249, content).

Commit each phase as `Phase N: …` and push the branch after every phase commit
(Project Guide, Part 3).

From #242: "The simulation is identical with it on or off. It only changes
what's shown and what's offered." From #249: "Watts are hidden. The player
learns the network through real tools and labels."

## Relevant existing state

Verified against `ashfall.html` at v0.9.2.

**Doors and windows (WORLD DATA).**
- `makeDefaultDoors()` returns hand-authored entries keyed by id.
  - Entry doors: `2a`, `2b`, `1a`, `1b`.
  - `1a-patio`: `locked:true`, lockable (no `lockable` field).
  - Twelve lockless interior doors (`lockable:false`), four per unit for 2A,
    2B and 1A: `<u>-bedroom` (living↔bedroom), `<u>-bathroom`
    (living↔bathroom), `<u>-bath-bedroom` (bedroom↔bathroom) and
    `<u>-balcony` (living↔balcony). 1A has no `1a-balcony`: its living↔patio
    door is `1a-patio`.
  - Every door carries `building:"acorn"`.
- `makeDefaultWindows()` returns the following:
  - `2a-transom` (hallway2↔living, climbable) and `1b-alley` (alley↔onebee,
    climbable).
  - Twelve outside windows, `<u>-living-window`, `<u>-kitchen-window`,
    `<u>-bedroom-window` and `<u>-bathroom-window` for 2A, 2B and 1A, each
    `{ state:"closed", rooms:[room], breakTag:"blunt", label:"window" }`.
  - 1B has none of these, and neither balcony nor patio has a window.
- Exits name their door inline by `doorId` in `makeDefaultWorld()`, in the
  room definitions (e.g. `living`'s exits carry `doorId:"2a-bedroom"`).
- `let doors = buildDoors(null)` and `let windows = buildWindows(null)` run at
  script load, **above** `const WIRING_TEMPLATES` and `const WIRING` in the
  file. Code called from them that reads either const hits the temporal dead
  zone and throws.
- Saves key on door and window ids (`buildDoors()` / `buildWindows()` merge
  the saved fields by id). The ids must not change.

**The wiring (WORLD DATA, POWER SCHEMA; SIMULATION, POWER).**
- `WIRING_TEMPLATES.apartment` is `{ main, circuits, fixtures }`. Each circuit
  carries `roles`, the rooms it serves.
- `WIRING.acorn.panels` has four unit panels (`2A`, `2B`, `1A`, `1B`), each
  `{ id, name, room, template:"apartment", rooms:{ role: roomId } }`. 1B maps
  every role to `onebee`, and 1A maps `balcony` to `onea_patio`.
  `WIRING.acorn.common` is the house panel, with an inline `layout`.
- `expandWiring()` builds `POWER_NET`: `{ boards, panels, breakers, loads,
  containerLoad, devices, byLayer, problems }`.
  - A breaker is `{ id, layer, label, rating, volts, device, room, loads }`;
    a circuit also carries `roles`.
  - A panel carries `roles` (role → room) and `circuits` in panel order.
  - `devices[roomId]` lists what hangs there, the board before panels.
- `powerSnapshot()` returns, among other things:
  - `live`: whether power reaches past a board's, panel's or circuit's
    breaker;
  - `supplied`: a panel's feeder side;
  - `powered`: a load's switch is on and its path is live;
  - `running`: amps through each breaker, as the watts of drawing loads ÷
    the breaker's `volts`.

  Simplified rules skip feeders and circuits.
- Other helpers:
  - `loadPoweredNow(loadId)` is a render-safe fresh look.
  - `isPowered(loadId)` reads the last step.
  - `gridUp(m)` is `m < POWER_FAILS_DAY * MINUTES_PER_DAY`, where
    `POWER_FAILS_DAY = 21` and a run starts on day 2
    (`START_DAYS_AFTER_COLLAPSE`).
  - `containerPowered()` falls back to `gridUp()` for a container no load
    claims.
- `doSwitchLoad(loadId, on)` is a load's own switch. Its comment says it is
  built for the electrical view to call.
- `APPLIANCES` has six entries: `fridge_freezer`, `led_light`, `bath_fan`,
  `range_hood`, `smoke_alarm` and `gas_range`. `validateWiring()` checks their
  shape.

**The stove timer (ACTIONS, FIRE/COOKING).**
- The comment above `doAddStoveTimer()` reads: "The stove timer: an analog
  kitchen timer on the stove container … It needs neither the stove on nor
  power, and turns nothing off."
- `tickStoveTimers()` counts it down regardless of power. CONTAINER SCHEMA's
  `timerMinutes` line calls it "a stove's analog timer".

**Room text (WORLD DATA; RENDERING).**
- Room `desc` is a plain string. It is read in one place:
  `roomDesc.textContent = room.desc + heatNote` in `render()`.

**The UI.**
- `HUB_BUTTONS` lists the ☰ Menu's hub-row buttons. Each is
  `{ label, opens }`, opening a `FULL_PANELS` panel. There is no toggle kind
  yet.
- The Here panel's tabs (`renderWorldItemsPanel()`) run Floor, then floor
  bags, then containers, then one tab per panel or board hanging in the room
  (`powerDevicesIn()`, `powerTab()`).
- A device tab has no item list. Its strip shows `deviceStripText()` and
  Device Options, which opens `renderPowerDevicePop()` with one row per
  breaker (`deviceBreakers()`: MAIN, then circuits or feeders). Simplified
  rules show only the main.
- The Inventory panel (`renderInventoryPanel()`) has tabs for Inventory and
  each equipped bag.
- Nothing is stored outside the save today. The Options rules choice
  (`nextRulesChoice`) is in memory only. The save lives under `SAVE_KEY` in
  `localStorage`.

**Items and spawns (WORLD DATA).**
- `screwdriver` sits in the `tools_workshop` (chance 0.20) and
  `hardware_store` (0.23) pools. Those two chances are the first entries in
  the pools comment's list of chosen, not derived, figures. Every other
  six-decimal chance there is derived and must not be touched.
- A pool's roll is keyed by pool id and entry key, so adding an entry does not
  move any other entry's roll.
- 1B's `toolcabinet` (in `onebee`) is `spawnRolled:true`, with hand-placed
  crowbar, duct tape ×2, wrench and bolt cutters.

## Rules / mechanics

### Phase 1 — Templates carry windows and interior doors (#267)

- **The template gains two fields, by role.** `WIRING_TEMPLATES.apartment`
  gets `doors` and `windows` beside `main`, `circuits` and `fixtures`:
  - `doors`: `{ key, between:[role, role] }` for `bedroom` (living↔bedroom),
    `bathroom` (living↔bathroom), `bath-bedroom` (bedroom↔bathroom) and
    `balcony` (living↔balcony). Each is lockless (`locked:false,
    lockable:false`).
  - `windows`: `{ key, role, label:"window", breakTag:"blunt" }` for `living`,
    `kitchen`, `bedroom` and `bathroom`. Each is closed and not climbable.
- **Ids are the unit's panel id, lowercased, then the key.** Doors are
  `<unit>-<key>` and windows `<unit>-<role>-window`, so `2A` gives
  `2a-bedroom` and `2a-kitchen-window`. These must equal today's ids exactly,
  because saves key on them. A door's `building` is the WIRING key
  (`acorn`).
- **A door whose two roles map to the same room is not made.** That is why
  1B gets no interior doors.
- **A panel can override the template, for its own unit only:**
  - **1A:** its `balcony` door is `1a-patio`, `locked:true` and lockable.
    That is today's door exactly.
  - **1B:** it takes none of the template's windows. Its only window is the
    hand-authored `1b-alley`.
- **Hand-authored doors and windows stay where they are:**
  - the four entry doors;
  - `2a-transom`;
  - `1b-alley`.

  These are the building's, not the unit template's.
- **Exits get the doorId of every template door.** An exit from one of the
  door's two rooms to the other carries its `doorId`. The authored `doorId`s
  for template doors come out of the room definitions.
- **The proof.** Compare the following, as JSON with sorted keys, before
  (`origin/main`) and after the phase, and record the comparison in the
  changelog's Validation section:
  - `makeDefaultDoors()`;
  - `makeDefaultWindows()`;
  - every room's exits with their `doorId`.

  All three must be identical. `validateWiring()` reports a template door or
  window whose role has no room, and an id clash.

### Phase 2 — The stove timer is a wind-up timer (#270)

Tom's decision: the stove's timer is an analog **wind-up** timer. It has no
battery and never needs power. **The mechanic does not change.** Update the
comment above `doAddStoveTimer()` and CONTAINER SCHEMA's `timerMinutes` line
to say this: wind-up, needing neither power nor a battery. It is separate from
the range's own electronics (`gas_range`'s standby draw in APPLIANCES).

### Phase 3 — Room text follows power (#235)

- **A description can carry a variant per power state.** The shape (variants
  per room, or tokens inside one string) is the coding session's to choose
  and name. It must be reusable for other world state later: weather (#58),
  time of day, damage. Rendering picks the text. The rule it reads is:
  - **a room's own load**: `loadPoweredNow(loadId)`, so throwing the load's
    own switch shows at once, as its readout does;
  - **street equipment**: `gridUp()`;
  - **the rail crossing**: the grid, plus its standby battery (below).
- **The rail crossing runs on standby power after the grid fails.** US law
  requires a grade crossing's warning system to have "a standby source of
  power … with sufficient capacity to operate the warning system for a
  reasonable length of time during a period of primary power interruption"
  (49 CFR 234.251). No length is set, so one named constant holds it,
  **24 hours, unconfirmed and retunable**.
  - The crossing's lights are on while `gridUp()`, or while the time since
    the grid failed is under that standby.
  - This is the only place the standby figure lives.
- **A cycling fridge counts as powered, not as drawing.** The kitchen reads
  "hums" whenever its load is powered, even in the off part of its cycle.
  That is a simplification, retunable.
- **The text, approved by Tom.** Quote it verbatim.

| Room id | Reads | Powered / grid up | Unpowered / grid down |
|---|---|---|---|
| `kitchen` (Acorn 2A) | load `acorn.2A.fridge` | Grease and old coffee grounds. The fridge still hums, though something inside it has already given up. | Grease and old coffee grounds. The fridge has gone quiet, and something inside it gave up well before it did. |
| `hallway2` (Acorn) | load `acorn.house.light_hallway2` | A dim corridor lit by one flickering bulb. Your door is one of two here, with a small transom window set beside it. | A dark corridor, its one bulb dead. Your door is one of two here, with a small transom window set beside it. |
| `oak_hallway1` | `gridUp()` (unwired; #252 swaps in its load) | Narrower than Acorn's hallway, and darker — half the bulbs are out. | Narrower than Acorn's hallway, and darker — none of the bulbs work now. |
| `mill4th` | `gridUp()` | The corner of Mill and 4th. A weighbridge is set into the pavement, its readout showing zeros. | The corner of Mill and 4th. A weighbridge is set into the pavement, its readout dark. |
| `mid_maple_2_4` | `gridUp()` | Maple St, mostly gravel shoulder and one working streetlight. | Maple St, mostly gravel shoulder and one streetlight, out like the rest. |
| `poplar4th` | `gridUp()` | The last residential stretch before Poplar runs into 4th St. Fewer porch lights than a block ago. | The last residential stretch before Poplar runs into 4th St. Not a porch light on the block. |
| `main7th` | `gridUp()` | Main and 7th, where a gas station's canopy lights still burn over empty pumps, price signs stuck at numbers that don't matter. | Main and 7th, where a gas station sits dark on the corner, price signs stuck at numbers that don't matter. |
| `mid_1st_mp_p` | `gridUp()` | 1st St running down toward Maple. Fewer houses with lights ever left on. | 1st St running down toward Maple. None of the houses have a light on. |
| `mid_2nd_d_mi` | grid + standby | 2nd St crossing the rail spur at a shallow angle. The crossing lights blink for a train that isn't coming, but the bell housing's still up there. | 2nd St crossing the rail spur at a shallow angle. The crossing lights are dark, the bell housing still up there. |

The 2A kitchen's sentence "The gas stove works too — no power needed to light
it." is removed from both texts. It is wrong on the facts (#259), and the
stove's strip already shows its state.

**Swept and left alone, because each holds in both states:**
- `living`: a dark television;
- `onebee`: a small gas stove;
- `cedar2nd`: the bulb's gone;
- `mid_9th_e_mp`: a streetlight, dark, which reads as burnt out or off by day;
- `main5th`: the OPEN sign, switched off at closing;
- `mid_maple_3_5` and `mid_maple_5_7`: where the streetlights stop.

### Phase 4 — The electrical view (#242)

- **A toggle in the ☰ Menu's hub row,** labelled `Electrical`. It shows its
  on or off state and opens no panel. While it is on, **Inventory and the
  Here item panel become their electrical views**. Move, Here actions, the
  log and everything else are unchanged.
- **The simulation is identical with it on or off.** It changes only what is
  shown and what is offered.
- **The toggle persists outside the save,** as a player preference.
  - It is stored in `localStorage` under its own key, not `SAVE_KEY`, and the
    key carries no version, so a MINOR bump doesn't reset it.
  - Every read and write is wrapped in try/catch. It defaults to off when
    storage is missing or throws.
  - It is not in `state`, and never in a save or an export.
- **The electrical Here panel.** Its tabs run upstream first:
  1. **Device tabs** for the panels and boards hanging in the room, in the
     order they have today (board, then panel). Each has the strip and
     Device Options it has today.
  2. **Circuit tabs**, one per circuit that serves this room: every circuit
     breaker whose `roles` include a role its panel maps to this room. They
     run in their panel's breaker order and are labelled with the breaker's
     hand-written label ("KITCHEN 1").

  Containers, Floor and floor bags have no tab in this view.
- **A circuit tab's content.** It has two parts.
  - **The loads on this circuit in this room**, one row each. A row shows:
    - the appliance's name;
    - for a switchable load, its readout (`loadStatusText()`) and one
      Switch on / Switch off control, which calls `doSwitchLoad()` (not a
      re-implementation);
    - its nameplate (Phase 5);
    - the meter controls (Phase 5).

    A switchless load (the smoke alarm, the gas range) shows no readout and
    no switch.
  - **Beneath them, loads elsewhere on the same circuit**, by appliance
    name and the room they are in (the room's label as the header shows
    it). They have no status and no control: you can't see them from here.
- **A room with no device and no circuit** shows no tabs, only a short
  functional note in the list's place. Unwired rooms still fall back to the
  grid; the note must not claim anything about the room's wiring.
- **Simplified rules** (#243) keep the toggle.
  - Device tabs show what their pop-ups already show under simplified rules.
  - Circuit tabs are still shown. They are how a room's loads are listed.
  - The meters' reach narrows (Phase 5).
- **The electrical Inventory** lists only carried items tagged `electrical`,
  in every Inventory and bag tab. Each item's detail view and actions are as
  they are today. An empty list shows a short functional note. The weight
  readout is unchanged.
- **Watts are shown nowhere.** They come only from nameplates and meters.

### Phase 5 — Nameplates and meters (#249)

- **Every `APPLIANCES` entry carries a nameplate:** the rated figure a real
  one prints. It is higher than the running draw, as real nameplates are.
  `validateWiring()` reports an entry without one, and a nameplate rated
  below its own `watts`.

| Appliance | Nameplate | Source |
|---|---|---|
| `fridge_freezer` | 120 V · 6 A | Frigidaire FFTR1821QW's listed "Amps at 120 Volts: 6", from a retailer listing, because Frigidaire's own page could not be read. **Unconfirmed.** |
| `led_light` | its own `watts`, printed on the base (10 W) | Derived from `watts`, never a second copy (One source of truth). |
| `bath_fan` | 120 V · 0.9 A | Broan 688: "120 VAC, 0.9 A" |
| `range_hood` | 120 V · 2.0 A | Broan 413004: "120V ~ 60 Hz, drawing 2.0 amps" |
| `smoke_alarm` | 120 V · 0.04 A | BRK 9120 data sheet: "Operating Current: .04 amps (standby/alarm)" |
| `gas_range` | 120 V · 12 A | Frigidaire FCFG3062AS: "Amps @ 120 Volts: 12 Amps". The rating covers its oven igniter and oven, which aren't modelled; that is why it sits far above the 4 W standby. |

  Picking one real model per appliance is a judgment call, retunable. Put
  each source in the comment beside its figure, as APPLIANCES' existing
  figures are.
- **Where the nameplate shows:** on the load's row in the electrical view's
  circuit tab, as a line such as `Nameplate: 120 V · 0.9 A` (or
  `Nameplate: 10 W` for a bulb). Nowhere in the normal view.
- **Two new items**, in `ITEM_REGISTRY`, category `Tool`:
  - `multimeter`: "Multimeter", `unitWeight:0.55`, a Fluke 115's 550 g. It
    tests voltage only. A multimeter measures current up to 10 A and only by
    breaking into the circuit (Fluke 115), so it can't safely read a
    household circuit, and the game doesn't offer it.
  - `clamp_meter`: "Clamp meter", `unitWeight:0.265`, a Fluke 323's 265 g.
    It clamps current (400 A AC range) and also tests voltage (600 V AC).
  - Both carry `electrical`, plus capability tags that the mechanics check,
    never the names: a voltage-test tag on both, and a current-clamp tag on
    the clamp meter. The tag names are the coding session's (see below).
  - **No battery is modelled.** Real meters run on a 9 V battery or AA
    cells; that belongs to #261 (noted there).
- **Test (voltage), with a voltage-test tool carried.** It costs
  `METER_READING_MIN = 1` game minute (retunable), then reads the state after
  that minute.
  - **On a load row in a circuit tab:** the load's supply, up to its own
    switch. That is the circuit's `volts` when `live[circuit]` (simplified:
    `live[panel]`), else 0.
  - **On a breaker row in a device pop-up, while the electrical view is on:**
    that breaker's load side, at the breaker's `volts`. The load side is:
    - for a circuit, `live[circuit]`;
    - for a panel main, `live[panel]`;
    - for a feeder, `supplied[panel]`;
    - for the board main, `live[board]`.
  - The reading is a whole number of volts.
- **Clamp (current), with a current-clamp tool carried, on breaker rows
  only.** It clamps one conductor at the panel. It costs
  `METER_READING_MIN`, then reads `running[breakerId]` to one decimal (the
  Fluke 323's 0.1 A resolution).
  - A main or feeder reads its total, as the model already treats a panel's
    two legs as balanced. Unbalanced legs are not modelled.
  - A cycling fridge reads whatever it is doing that minute, which is how a
    player finds its cycle.
- **Simplified rules:** Test works on load rows and on a device's main. Clamp
  works on the main only, matching what simplified shows.
- **Each reading logs one line.** It is functional and retunable, e.g. "The
  meter reads 120 V." / "The clamp reads 1.3 A." Nothing else records a
  reading.
- **Opening a panel to clamp a live conductor has no consequence yet.** Shock
  is #247.

### Phase 6 — The meters' placements (#249, content)

- **Spawn chances.** `multimeter` and `clamp_meter` are each added to
  `hardware_store` and `tools_workshop` at **chance 0.20**. That is chosen
  beside the screwdriver's, retunable. Add all four entries to the pools
  comment's list of chosen, not derived, figures.
- **A hand-placed multimeter** goes in 1B's `toolcabinet`
  (`itemsFromRegistry`, qty 1), so the player's own building has one.
- **The stores stay generic.** A generic hardware store stocking meters makes
  no claim about a real business. The store's real identity is #237's, not
  this pass's.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

- **The shape of state-following text (Phase 3):** variants per room, or
  tokens inside one description. Choose the one a later reader, such as
  weather or time of day, can reuse. Name it in the ROOM SCHEMA comment.
- **How exits get their `doorId` (Phase 1):**
  - **(a)** Stamp it at world build. Recommended.
  - **(b)** Keep it authored, with `validateWiring()` checking that it matches
    the template.

  Either way, the proof covers the exits.
- **The shape of a panel's override (Phase 1),** for 1A's patio door and 1B's
  lack of windows. It could be a per-key override map, or an omit list plus
  an extra door. Either is fine.
- **Sidestepping the temporal dead zone (Phase 1).** `buildDoors()` and
  `buildWindows()` run above `WIRING`. Move the template and wiring
  definitions above them, or defer building doors and windows until after
  them. Show that the load order works by loading the page.
- **The nameplate's schema (Phase 5).** For example `nameplate:{ volts, amps }`,
  with the bulb's derived from `watts`.
- **The capability tag names (Phase 5).** For example `voltage-test` and
  `current-clamp`.
- **How the hub row carries a toggle (Phase 4).** For example a
  `HUB_BUTTONS` entry with `toggles` in place of `opens`. Name the preference
  key.
- **Where the meter controls sit on a row (Phase 5):** inline buttons beside
  the switch, or a small group. Only while the tool is carried.

## Data / schema changes

- **State fields:** none. The electrical view's toggle is a `localStorage`
  preference outside `state` and the save.
- **Item schema:** two new registry items (`multimeter`, `clamp_meter`). New
  tags: `electrical`, plus the two capability tags.
- **APPLIANCES:** a nameplate on every entry. This is definition data for
  Phase 5's rule.
- **WIRING_TEMPLATES:** `doors` and `windows` by role, and per-panel
  overrides. Document them in the POWER SCHEMA comment, and extend the
  DOOR/WINDOW SCHEMA comments to say where template doors and windows come
  from.
- **Room `desc`:** the variant shape for nine rooms (Phase 3).
- **Spawn pools:** four new entries. 1B's tool cabinet: one new placed item.

## In scope

- Phase 1: template doors and windows, overrides, exits, and the equality
  proof.
- Phase 2: the timer comments.
- Phase 3: the variant mechanism, nine rooms' text, and the crossing's
  standby constant.
- Phase 4: the hub toggle, the preference, the electrical Here tabs (devices
  and circuits) and the electrical Inventory filter.
- Phase 5: nameplates on every appliance, the two meters, Test and Clamp,
  their log lines and time cost, and simplified rules' reach.
- Phase 6: the meters' pool entries and the 1B placement.

## Explicitly out of scope

- **Wiring any other building** (#252–#257; gated on #237). #258 is the
  fallback's removal.
- **Candles** (#271). They are MINOR and belong in the v0.10.0 bundle.
- **Cords, plugging and plug swapping** (#244), **generators** (#245),
  **inlets** (#246), **shock and GFCI** (#247), **carbon monoxide** (#248)
  and **batteries** (#261, including the meters' own).
- **Outlets as network nodes.** The meters test loads and breakers only.
- **Real names for streets and stores** (#237).
- **The grid's own structure,** substations and faults by area (#220, "Not
  owned by any pass yet"). The crossing's standby is its only grid-side
  detail.
- **Temperature and fridge coasting** (#217). **Time of day** (#58). The
  streetlights' photocells are not modelled.
- **A UI-preferences system** (#165). This pass stores one toggle and builds
  no Options page for it.

## Sections touched

- **WORLD DATA:**
  - `WIRING_TEMPLATES` and `WIRING`: panel overrides;
  - `makeDefaultDoors()` and `makeDefaultWindows()`;
  - room definitions: exits' `doorId`, and the nine rooms' text;
  - `APPLIANCES`: nameplates;
  - `ITEM_REGISTRY` and `SPAWN_POOLS`;
  - 1B's tool cabinet.
- **SIMULATION, POWER:** `expandWiring()`, or a sibling that expands doors
  and windows; `validateWiring()`. A meter reading reads `powerNow`; it adds
  no rule to the resolver.
- **ACTIONS:** the Test and Clamp actions (WORLD INTERACTION). The timer
  comment (FIRE/COOKING).
- **RENDERING:** the text variants, the hub toggle, the electrical Here and
  Inventory views, and the nameplate lines.
- **PERSISTENCE:** untouched, apart from what the preference's storage key
  needs; the save is not touched.

Phases 3 and 6 carry instance data. That is by Tom's decision, as their own
phases: the approved texts (#235), and the meters' placements, so the tools
don't ship unobtainable (#133).

## UI changes

- **☰ Menu, hub row:** an `Electrical` toggle that shows its state.
- **Here, with the toggle on:** device tabs, then circuit tabs; load rows with
  a readout, a switch, a nameplate and Test; loads elsewhere by name and room.
  The device pop-up's breaker rows gain Test and Clamp while a meter is
  carried.
- **Inventory, with the toggle on:** electrical items only.
- **Room text:** nine descriptions follow power.
- **Log:** one line per meter reading.

## Dependencies / issue linkage

- **Fulfils** #242, #235, #249, #267 and #270. The pull request says `Closes`
  for each.
- **Unblocks** #252. Oak reuses the template, doors and windows included.
- **When #252 wires Oak**, `oak_hallway1`'s text should read its hall light's
  load in place of `gridUp()`. This is already noted on #252.
- **At the wrap,** file anything deferred. If nothing was, say so.

## Open questions for Tom

None. Everything above was decided in the planning session at v0.9.2.

## After implementation

- Open one pull request carrying:
  - the PATCH bump;
  - a `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, with
    `Implements: handoffs/electrical-view-and-meters.md`, the Phase 1 equality
    proof, and the design decisions above as resolved;
  - this handoff moved to `handoffs/archive/`;
  - `Closes #242`, `Closes #235`, `Closes #249`, `Closes #267` and
    `Closes #270`.
- End the session's final message with the tag commands (`CLAUDE.md`,
  wrap-time checklist, item 6).
