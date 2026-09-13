# Ashfall — Development Roadmap

## Purpose

This document is the current development roadmap for Ashfall. It has been
audited against the game code (v0.4.0) and `CHANGELOG.md` — every item
below was confirmed as not-yet-implemented at time of writing. When an
item is completed, move it out of this file and into a changelog entry
instead of leaving it here marked "done."

Item 10 ("Coordinate System — Part 1") shipped in v0.2.9. Item 11
("Coordinate System — Part 2: Auto-Distance & Direction Wiring") shipped
in v0.3.0 — see `CHANGELOG_v0.3.0.md`. Both parts of the coordinate-system
initiative are now complete and removed from this file.

A planning session covering container/item spawn pools produced "Ashfall
Handoff — Container Spawn Pools & Population System.md," narrowing item
15's scope down to what's listed under it below and surfacing new Tier 0
item 16. The item-spawn-pool mechanism that handoff specced (`SPAWN_POOLS`,
`spawnPools`, `doOpenContainer()`'s roll-on-first-open, and the full
container/item tagging pass) has since **shipped in v0.4.0** — see
`CHANGELOG_v0.4.0.md`. Item 15 itself is not closed: its remaining scope
(container property tags, the no-respawn flag, the actual respawn
trigger, vehicle spawn pools, and fauna) is still open, below. Item 16
is also still open — untouched by the v0.4.0 pass.

The backlog is organized into tiers based primarily on **urgency,
dependencies, and implementation convenience**, rather than treating every
item as equally important.

The tiers should be interpreted as:

- **Tier 0:** Small, code-only cleanup items with no design content —
  deletions, renames, wording fixes. Safe to knock out any time, including
  opportunistically during an unrelated pass.
- **Tier 1:** Relatively accessible work that can be implemented without
  major system dependencies. These can also be used to improve the world
  and polish the current experience while larger systems are being
  developed.
- **Tier 2:** Foundational gameplay systems. These should be prioritized
  carefully because later mechanics depend on them.
- **Tier 3:** Large standalone systems. They are important to the
  eventual gameplay loop but require substantially more design and
  implementation work.

The list is a **roadmap, not a rigid implementation order**. Tier 0 and
Tier 1 work can be completed opportunistically, while Tier 2 establishes
the foundation for several later mechanics.

---

# Tier 0 — Cleanup

## 9. Split `buildStreetsAndOutdoor()` by Town/Location

The v0.2.8 WORLD DATA / RENDERING modularity pass split
`makeDefaultWorld()` into one function per building, but left every
street/outdoor room (currently 60 rooms — all of Poplar St, Main St,
Water St, Maple St, the numbered cross-streets, mid-block nodes, and
the riverbank) in a single combined `buildStreetsAndOutdoor()` function.

### Scope
- Once the street/outdoor world data grows enough to make one combined
  function unwieldy, split it further — by town or by location — rather
  than continuing to add to a single ever-growing function.
- No urgency yet; this is a forward-looking maintainability note, not a
  current blocker. Safe to defer indefinitely until the room count in
  that function actually becomes a problem.

### Note
Raised by Tom immediately following the v0.2.8 pass, as a known gap in
that pass's building-level split rather than something the v0.2.8
handoff missed — `buildStreetsAndOutdoor()` was an explicit, recommended
grouping choice in that handoff, not an oversight.

---

## 12. Strip Vestigial `distanceM` from Cross-Location Exits

Since v0.3.0, `exitMinutes()` computes travel time from `LOCATIONS` for
any exit whose target is in a different Location, regardless of whether
the exit also carries a leftover `distanceM` field — that field is
simply never read for those exits. 26 exits (building entrances/exits
and floor transitions — e.g. `cornerstore ↔ main2nd`, `stairs2 ↔
stairs1`, `pharmacy_apt ↔ pharmacy`) still carry a now-unread
`distanceM`, left in place by the v0.3.0 pass rather than expanding its
scope (see `CHANGELOG_v0.3.0.md`'s Notes/assumptions).

### Scope
- Remove `distanceM` from the 26 identified cross-Location exits so the
  EXIT SCHEMA is consistently `{ to, label }` for every cross-Location
  exit, per the "no duplicated source of truth" principle.
- No functional effect expected — confirmed in the v0.3.0 changelog that
  displayed travel time is identical with or without the field for all
  26 cases, at every gait.

### Note
Purely a cleanup item: safe to defer or knock out opportunistically
alongside unrelated WORLD DATA work, like the rest of Tier 0.

---

## 16. `bandage` / `bandages` Registry Naming Duplicate

`ITEM_REGISTRY` has two separate entries that appear to be the same
real-world item: `bandage` (singular, Medical, 0.05 kg) and `bandages`
(plural, Medical, 0.05 kg). Found while auditing the full registry during
the Container Spawn Pools planning session. Likely a naming leftover from
an earlier pass rather than two intentionally distinct items.

### Scope
- Confirm whether these are meant to be distinct (different
  `durability`/`restores`/`tags`) or true duplicates.
- If duplicates, consolidate into one entry and update the placement
  references that currently use `bandages` (the plural form) accordingly.

### Note
Purely a Tier 0 cleanup item — no gameplay effect either way until
resolved. Not touched by the Container Spawn Pools pass; flagged there,
fixed here.

---

# Tier 1 — Content / World Expansion + Low-Cost UX Improvements

## 1. Rooftops

Expand rooftop access across most buildings **where it is physically and
realistically plausible**.

### Scope
- Add rooftop areas to appropriate buildings.
- Do not assume every building should have accessible rooftops.
- Rooftop access should make architectural sense based on the building
  itself.
- Avoid adding rooftops purely for the sake of increasing map size.

### Confirmed decision
The starting apartment building (Acorn Apartments) stays at its current
2 floors (1st: 1A/1B, 2nd: 2A/2B). There is no plan to expand it to
3–4 floors — rooftop access, where it makes sense, is the intended
direction instead.

### Design principle
Rooftops should feel like a natural extension of the existing environment
rather than artificial additional locations.

---

## 13. Lore Development

Write descriptions for buildings, rooms, and items, plus dedicated lore
items (e.g. newspapers, notes) that flesh out the world's backstory.

### Scope
- Room and building descriptions, per the Project Guide's tone/writing
  checklist (understatement, absence-as-storytelling, no exposition
  dumps).
- Item descriptions.
- New lore-item type(s) — e.g. newspapers, notes, journals — readable
  content that reveals pieces of what happened without a single
  description trying to explain the whole collapse.

### Note
Purely content — no new mechanics implied unless a lore-item type needs
new schema (e.g. a "readable text" field), which would be a small
addition, not a new system.

---

## 14. Expand the Map

Add more locations to grow the game world beyond its current footprint.

### Scope
- New locations/buildings beyond the current 5×4 street grid.
- Concrete building types TBD — see planning discussion for a long
  brainstormed list of possible building categories (residential,
  commercial, civic, industrial, medical, recreational, agricultural,
  impound/vehicle storage, etc.) to draw from when this is scoped.

### Note
This is a future-reference placeholder, not a specced pass — which
buildings/locations actually get added still needs a dedicated planning
session.

---

# Tier 2 — Foundational Gameplay Systems

These systems form the mechanical foundation for several future features.

## 3. Character Creation

Implement the game's character creation system.

### Core components
- **Occupation selection**
- **Trait point-buy system**

### Dependency significance
Character creation is the first major foundational system because
several subsequent mechanics need a defined character state and character
attributes to operate against.

### Important dependency
Nothing that relies on the player's finalized character attributes should
be considered fully implementable until this system exists.

### Intended role
Character creation should establish the player's initial mechanical
identity and provide the underlying values that later systems can
evaluate.

---

## 4. Skill Checks

Implement the game's general-purpose skill-check system.

### Dependency
**Blocked on Character Creation.**

Skill checks need the character's attributes/traits/occupation-derived
values to have a defined source.

### Core purpose
Skill checks become the general mechanical framework for situations where
the character's abilities should determine success, failure, difficulty,
or outcome.

### Existing mechanic connection
This is also the point at which several previously planned modifiers can
finally become mechanically meaningful.

In particular:

- **Encumbrance** currently exists only as inventory weight/capacity
  limits (`totalWeight`, `capacityKg`) — it has no effect on checks yet.
- Skill checks provide the actual system for applying that modifier.
- This turns the earlier idea of "encumbrance affects checks" from a
  theoretical modifier into a functioning gameplay mechanic.

### Design principle
Skill checks should be designed as a reusable underlying system rather
than as isolated mechanics for individual situations.

Future systems should be able to call into the same check framework
instead of implementing their own independent probability logic.

---

## 5. Lockpicking

Implement lockpicking as a skill-check-driven mechanic.

### Dependencies
- **Character Creation**
- **Skill Checks**

### Primary purpose
Provide a natural mechanical method for interacting with locked areas
without relying exclusively on universal access items.

### Existing progression connection
The only current access method into locked units is the single `Master
key` item (`findKeyForDoor`), which opens any door in the Acorn Apartments
building. Lockpicking provides the more natural long-term route into
areas such as:

- **2B**
- **1A**
- **1B**

rather than requiring the player to obtain or use that one master key.

### Design principle
Locks should become part of the game's broader interaction system rather
than simply functioning as binary barriers.

The lockpicking system should therefore leverage the general skill-check
framework rather than becoming an isolated minigame/system.

---

# Tier 3 — Major Standalone Systems

These systems are substantially larger and should be treated as dedicated
development projects.

## 6. Zombies / Threats

Implement the game's actual hostile threats, primarily zombies.

### Current status / significance
This remains the **largest major unbuilt gameplay system** — no threat,
enemy, noise, or detection code exists yet.

It is also the system that ultimately gives several existing mechanics
their deeper purpose.

### Mechanics it will activate or reinforce
The threat system is what makes concepts such as:

- Stealth (the existing Sneak/Walk/Jog gait system)
- Noise
- Locked doors
- Avoidance
- Route selection
- Risk management

meaningfully affect survival rather than existing primarily as
environmental flavor.

### Design principle
The zombie/threat system should not be treated merely as an
enemy-placement feature.

It needs to connect to the existing gameplay systems so that the player's
actions have consequences within the environment.

### Priority rationale
This is a major standalone project and therefore belongs in Tier 3
despite its importance.

---

## 7. Hunting With Traps

Implement hunting as a gameplay system, including the use of traps.

### Scope
- Hunting mechanics.
- Trap placement/use.
- Appropriate interaction and outcome mechanics.
- Integration with the game's broader survival/resource systems as
  appropriate.

### Existing related system
Fishing already exists (`doFish`, requires `fishing` + `tackle` tags) as
a separate mechanic — hunting should be treated as its own system, not
folded into or copied from fishing.

### Design principle
Hunting should feel like a deliberate survival activity rather than
simply another method of acquiring generic loot.

---

## 8. Vehicles — Full Gameplay System

Expand vehicles beyond their current role as loot containers.

### Current limitation
Vehicles currently function only as `carContainers` — searchable,
sometimes-locked (`carLocked`) storage, forceable open with a blunt tool
(`doBreakCar`). No stats, condition, or movement exist.

### Desired direction
Vehicles should eventually have meaningful gameplay functionality,
including:

- Real vehicle statistics.
- Vehicle condition/performance considerations where appropriate.
- Actual driving.
- Movement through the game world as a gameplay mechanic.

### Design principle
A vehicle should become an actual gameplay entity rather than simply
another searchable container.

### Scope warning
This is expected to be a substantial system and should be treated
independently from simple vehicle-loot improvements.

---

## 15. Container Property Tags, Respawn Trigger & Fauna System

Implement per-container property tags, the actual respawn *trigger*, and
the fauna alive/dead behavior tied to it.

### Current status
**The item-spawn-pool mechanism itself is fully implemented, as of
v0.4.0** — see `CHANGELOG_v0.4.0.md` and "Ashfall Handoff — Container
Spawn Pools & Population System.md" (`SPAWN_POOLS`, the `spawnPools`
container field, `doOpenContainer()`'s roll-on-first-open, and the full
container/item tagging + new-item pass across every regular container
in the game). That part of this item is done — do not re-design or
re-implement it here. Everything below is what's left.

### Scope (as discussed, not yet designed in full)
- **Container property tags** — orthogonal boolean flags, not a type
  hierarchy: `equippable`, `movable`, `disassemblable`. What each flag
  actually gates mechanically is still undecided.
  - **New dependency found during the spawn-pools planning session:** an
    `equippable` *container* flag would collide with the item-side
    equip mechanism that already exists (`slotType`/`capacityKg`/
    `contents` on `ITEM_REGISTRY` entries — e.g. `worn_backpack`,
    `state.backpack`/`state.keychain`). A backpack today is an
    equippable *item*, not a room container. Adding a container-side
    `equippable` flag risks a second, duplicate source of truth for the
    same concept (see the Project Guide's "no duplicated source of
    truth" principle) — this needs resolving before the flag is
    designed, not just implemented.
  - **New dependency found:** `movable` presupposes a drag/carry/
    relocate action that does not exist in any form yet. The flag can't
    be exercised — and the no-respawn flag below can't be triggered by
    it — until a move/relocate action is designed and built.
- **No-respawn flag** — an irreversible per-container flag that flips
  from respawn-eligible to permanently ineligible the moment a player
  relocates the container (drags it within a room or carries it
  elsewhere), even to identical coordinates — the relocation action
  itself flips it, not a position comparison. Looting does not flip it.
  - Player-crafted containers are meant to be created already flagged
    ineligible — but **no container-crafting system exists in the game
    at all.** This clause has no anchor until crafting is built; noted
    explicitly as a blocking dependency, not assumed fine as-is.
- **Respawn trigger — partially specified during the spawn-pools
  session, still not implementable.** Decided: time-based, keyed to the
  player leaving "the area" (defined as the whole town), default
  threshold 1 year (525,600 minutes) since departure. The timestamp
  should be written once, on leaving the town, not checked continuously
  — and compared only when a respawn-eligible container is reopened
  later (reusing the same `doOpenContainer()` hook the initial-
  population roll already uses). Still needed before this is
  handoff-ready:
  - A region/town concept in the data model — none exists today; every
    room is implicitly "the one town," so there is currently nowhere to
    leave *to*, meaning the trigger has no way to ever fire yet.
  - The actual leave-town detection/timestamp-write logic.
  - What a "reroll" does to a container whose contents the player has
    already modified (top off vs. replace vs. skip) — not discussed.
- **Vehicle (`carContainers`) spawn pools — explicitly excluded from the
  spawn-pools pass.** `carContainers` (trunk/glovebox) uses a separate
  schema branch from regular `containers[]` and was deliberately left
  out of that pass's retrofit so it wouldn't inflate scope. An eventual
  `automotive` pool (or reuse of `tools_workshop`) for vehicle contents
  is still open work.
- **Fauna alive/dead state** — insects (e.g. cockroach) are grabbable
  while alive, with the grab action itself killing them (`Cockroach` →
  `Cockroach (Dead)`); all other fauna (e.g. rat, raccoon) must already
  be dead before they're grabbable at all. Ties to the `trash` pool
  possibly spawning entities rather than `ITEM_REGISTRY` items — entity
  spawning doesn't exist yet either.

### Explicitly open / not designed
- What `equippable` / `movable` / `disassemblable` gate mechanically,
  including the `equippable` collision noted above.
- The region/town data model and leave-detection logic the respawn
  trigger depends on.
- Whether pools need to reference creatures/entities in addition to
  `ITEM_REGISTRY` items (fauna).

### Dependency note
Needs a dedicated planning session before any handoff can be written for
this remaining scope — per the Handoff Guide, the open questions above
are genuine design questions, not narrow implementation choices left for
a coding session.

---

# Dependency / Roadmap Overview

The major system dependency chain is:

**Character Creation**
↓
**Skill Checks**
↓
**Lockpicking**

Separately:

**Zombies / Threats**
→ gives deeper mechanical purpose to stealth, noise, locked doors,
avoidance, and environmental risk.

The coordinate-system initiative (Parts 1 and 2) is complete as of
v0.3.0 — no longer tracked here.

Tier 1 items are largely independent and can be implemented without
waiting for the Tier 2 or Tier 3 systems. Tier 0 currently has three open
items (see below) — all low priority, safe to defer.

---

# Current Backlog Summary

### Tier 0 — Cleanup
9. Split `buildStreetsAndOutdoor()` by town/location — deferred until the
   combined street/outdoor world-data function actually becomes unwieldy;
   no urgency.
12. Strip vestigial `distanceM` from 26 cross-Location exits (building
    entrances/floor transitions) left unread since v0.3.0 — no
    functional effect, pure schema tidy-up.
16. `bandage`/`bandages` registry naming duplicate — confirm intentional
    or consolidate; found during the Container Spawn Pools planning
    session, not fixed there.

### Tier 1 — Content / World / UX
1. Rooftops — realistic access across appropriate buildings; apartment
   stays at 2 floors, no floor expansion planned.
13. Lore development — descriptions for buildings, rooms, items, plus
    dedicated lore items (newspapers, notes, etc.).
14. Expand the map — add more locations/buildings beyond the current
    footprint; building types still to be scoped.

### Tier 2 — Foundations
3. Character creation — occupation + trait point-buy.
4. Skill checks — reusable character-based check system; enables
   modifiers such as encumbrance.
5. Lockpicking — skill-check-based access system; natural progression
   into 2B / 1A / 1B, replacing reliance on the single master key.

### Tier 3 — Major Systems
6. Zombies / threats — major survival/threat framework; makes stealth,
   noise, locked doors, and risk meaningful.
7. Hunting with traps — hunting and trapping gameplay, separate from the
   existing fishing system.
8. Vehicles — real stats and actual driving, rather than vehicles being
   loot containers only.
15. Container property tags, respawn trigger & fauna system —
    `equippable`/`movable`/`disassemblable` tags (equippable now flagged
    as colliding with the existing item-side equip mechanism), the
    irreversible no-respawn flag (blocked on both a move/relocate action
    and a container-crafting system, neither of which exist), the actual
    time-based respawn trigger (spec'd in direction — 1 year since
    leaving town — but blocked on a region/town data model that doesn't
    exist), vehicle/`carContainers` spawn pools, and fauna alive/dead
    behavior. The item-spawn-pool mechanism itself has been carved out
    and shipped in v0.4.0 — see `CHANGELOG_v0.4.0.md` and "Ashfall
    Handoff — Container Spawn Pools & Population System.md". Needs a
    dedicated planning session for what remains.
