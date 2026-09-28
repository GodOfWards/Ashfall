# Ashfall Handoff — English names in game text

Current shipped version: v0.10.1
Implied version-change type: PATCH
Issue: #310 — English names in game text — only streets, districts and towns stay in Spanish

## What this is

Tom's rule (2026-09-28): "Names should stay in English, just the streets and
districts/towns are staying in Spanish." `CLAUDE.md` ("Writing game text", "The
world is real") and the Project Guide, Part 1, "A real place", already say so.
This pass brings `ashfall.html` into line with them: it renames four items and
five places, rewrites the text that uses those names, and makes item names
reach existing saves.

The rule as it applies here:

- **Stay Spanish:** streets (Calle 15, Avenida 11, Camino a Baradero, Acceso a
  Lima, Camino Provincial 038-03), districts and towns (Lima, Zárate, Barrio
  Atucha, Nueve de Julio), and state institutions' proper names (Banco Nación,
  Correo Argentino, San Isidro Labrador). The railway address **FC Mitre**
  stays too, as the line's proper name (Tom, this session).
- **Stay as they are:** words with no English equivalent: *yerba mate*,
  *mate*, *dulce de leche*, *alfajores*, *asado*. "Plaza" and "chalet" are
  already English usage.
- **Everything else goes English**, named by what it is.

## Relevant existing state

Verified against `ashfall.html` at v0.10.1.

**Items** (`ITEM_REGISTRY`, WORLD DATA):
- `cedula_verde` (line ~1071): `name:"Cédula verde"`.
- `mate_bombilla` (~1181): `name:"Mate and bombilla"`.
- `galletitas` (~1183): `name:"Pack of galletitas"`.
- `dni_card` (~1184): `name:"DNI card"`.
- "Bag of yerba mate", "Box of alfajores", "Jar of dulce de leche" stay.
- `crackers` is a separate item named "Crackers". The new name below does not
  collide with it. Registry names must stay unique, because `backfillItemIds()`
  and `backfillSlotItemIds()` match by name.

**How item names reach a save.** `itemFromRegistry()` deep-copies the entry,
`name` included, onto every instance. `name` is not in
`REGISTRY_ONLY_FIELDS`. So an item already in a 0.10 save keeps its old name,
and `sameStackState()` stacks by `itemId`: an old "Pack of galletitas" and a new
copy merge into one row under whichever name the target row had.
`backfillRegistryTags()` (PERSISTENCE) is the precedent for fixing this. On
every load it gives every item `forEachItemList()` reaches, and every equipped
slot object (`CONTAINER_SLOTS`), a fresh copy of its registry entry's `tags`,
and leaves alone an item with no `itemId` or one the registry doesn't know. It
runs after `backfillItemIds()` and `backfillSlotItemIds()`. The one runtime
rename is a cooked dish: `buildDish()` sets `dish.name = dishName(t, units)`
when its `DISH_TEMPLATES` entry has `named:true` (soup, stew, roast, stir-fry).
`named:false` dishes (boiled pasta, boiled rice) keep the entry's name. No
world placement overrides an item's `name` today.

**Places and text** (WORLD DATA). Ids stay: `almacen`, `comisaria`,
`delegacion`, `school_ep9`, `estacion`, `estacion_lima`, and the map offset keys
that use them. Saves and code key on ids.
- `LIMA_STOP_TEXT`: `m_av11_c8_c6` (Escuela Primaria Nº 9), `m_c8_av11_c13`
  (Delegación Municipal), `m_c117_c88_c84` ("The barrio's club"),
  `m_c12_c13_c15` (Comisaría Zárate 2), `x_c113_c50` (almacén), `estacion_lima`
  (Estación Lima).
- `STOP_TEXT.barrio.corner[0]`: "A junction of the barrio's lanes."
- `stopAddress()`: `if(stop.kind === "s") return "Estación Lima";`.
- `NAMED_SCENERY`: `school_ep9`, `delegacion`, `estacion` names.
- `BUILDING_TYPES.row_house`, the garden's `desc`: "A brick parrilla…".
- `landmarkInstances()`:
  - the home's `garden` override: "The parrilla's grill…";
  - `comisaria`'s `name`, `enter`, `layout.label` (`"comisaría"`: the
    fallback for name and Enter label, unseen today because the instance sets
    both) and the `desk` room's `desc`;
  - `almacen`'s `name`, `enter` and `shop` `desc`;
  - `goods_shed`'s `address:"Estación Lima"`.

Room names and text are rebuilt from WORLD DATA on every load (v0.10.0), so the
place renames reach existing saves with no further work.

## Rules / mechanics

### Items

| id | Now | Becomes |
|---|---|---|
| `galletitas` | Pack of galletitas | Pack of biscuits |
| `cedula_verde` | Cédula verde | Vehicle registration card |
| `dni_card` | DNI card | ID card |
| `mate_bombilla` | Mate and bombilla | Mate and metal straw |

Ids do not change. "Mate and metal straw" is retunable wording.

### Places

| Where | Now | Becomes |
|---|---|---|
| `almacen` `name` | Almacén | Corner store |
| `almacen` `enter` | Enter the almacén | Enter the corner store |
| `comisaria` `name` | Comisaría Zárate 2 | Police station |
| `comisaria` `enter` | Enter the comisaría | Enter the police station |
| `comisaria` `layout.label` | comisaría | police station |
| `NAMED_SCENERY.delegacion` | Delegación Municipal | Municipal office |
| `NAMED_SCENERY.school_ep9` | Escuela Primaria Nº 9 | Primary school |
| `NAMED_SCENERY.estacion` | Estación Lima | Lima station |
| `stopAddress()`, kind `"s"` | Estación Lima | Lima station |
| `goods_shed` `address` | Estación Lima | Lima station |

Sentence case, like the file's other building names ("Repair shop",
"Municipal hospital").

### Text

| Where | Becomes |
|---|---|
| `LIMA_STOP_TEXT.m_av11_c8_c6` | Avenida 11. The Banco Nación is on this block, its shutter down, and the primary school a little further on. |
| `LIMA_STOP_TEXT.m_c8_av11_c13` | Calle 8, by the municipal office. Through the window, a row of plastic chairs where people used to wait. |
| `LIMA_STOP_TEXT.m_c117_c88_c84` | The neighbourhood's club runs along here behind a wire fence: tennis courts, a hall, a pool with leaves floating in it. |
| `LIMA_STOP_TEXT.m_c12_c13_c15` | Calle 12, outside the police station. A patrol car is parked across the entrance with its doors open. |
| `LIMA_STOP_TEXT.x_c113_c50` | A corner in the Nueve de Julio neighbourhood. The corner store's door opens right onto it, under a faded awning. |
| `LIMA_STOP_TEXT.estacion_lima` | Lima station. Its buildings, the platform, and the goods shed beside them. The platform is empty. |
| `STOP_TEXT.barrio.corner[0]` | A junction of the neighbourhood's lanes. Red-tile roofs show between the trees. |
| `row_house` garden `desc` | A patch of grass behind the house. A brick grill against the back wall, a clothesline, and the concrete lid of the septic tank. |
| home `garden` override `desc` | Your back garden. The grill is still greasy from the last asado. |
| `comisaria` `desk` `desc` | The front desk of the police station. Papers on the floor, a chair on its side. |
| `almacen` `shop` `desc` | A small corner store: a counter, a fridge for drinks, shelves to the ceiling. |

"Barrio Atucha" stays wherever it appears, including
`STOP_TEXT.barrio.mid[0]` and `m_c90b_c117_c119`. Only *barrio* used as a
generic noun becomes "neighbourhood".

### Item names reach existing saves

On every load, every item `forEachItemList()` reaches, and every equipped slot
object in `CONTAINER_SLOTS`, takes its registry entry's `name`. The same
conditions as `backfillRegistryTags()`, plus one:

- An item with no `itemId`, or one `ITEM_REGISTRY` doesn't know (the
  keychain), is left as it is.
- **A named dish keeps its name.** An item whose `itemId` is the `item` of a
  `DISH_TEMPLATES` entry with `named:true` got its name from `dishName()`, and
  is skipped.
- It runs after `backfillItemIds()` and `backfillSlotItemIds()`, since it keys
  off the `itemId` they assign. Those two match by name against the current
  registry. That's safe with these renames: the four renamed items were
  introduced in 0.10 with `itemId` already set, and pre-0.10 saves are refused
  before any backfill runs.
- A new game needs none of this; its items come from the registry already.

This is general, not a migration for these four ids: any later rename in
`ITEM_REGISTRY` reaches old saves the same way.

## Design decisions to make during implementation

1. **Where the name refresh lives.** (a) Fold it into `backfillRegistryTags()`'s
   `resync`, and rename or re-comment the function to say it resyncs registry
   fields (tags and name). (b) A sibling, `backfillRegistryNames()`, called
   right after it in `applyLoadedData()`. Either is fine. Recommended: (a),
   since both are the same walk under the same conditions. Record the choice.
2. **The named-dish test's shape**, e.g. a set of the `item` ids of
   `named:true` templates, built once. It's an implementation choice; name it
   in the changelog.

## Data / schema changes

- No new state fields. No new item schema fields. No save-format change, and
  `SAVE_KEY` is unchanged.
- `ITEM_REGISTRY`: four `name` values change.
- Comments that quote the old player-facing names update to match, so the
  source doesn't disagree with itself. For example, the spawn-probability
  comment's "the mate and bombilla" and "the DNI card", and `BUILDING_TYPES`'
  `row_house` comment "the parrilla". Comments naming a thing by its id or by
  its real-world name as research (the `Lima.md` references, "Comisaría Zárate
  2" as the real station's name in a comment) may stay.

## In scope

- The four item renames.
- The place renames and text rewrites in the three tables above.
- The load-time name refresh, with the named-dish skip.
- The comment updates named above.

## Explicitly out of scope

- Any id: item ids, building ids, type ids (`galpon`, `shop_home`), stop ids,
  `NAMED_SCENERY` keys, map label-offset keys.
- Street, district and town names, and FC Mitre.
- Making `name` registry-only. It was considered and rejected: about 77 `.name`
  reads, and too big for a text pass.
- `docs/` and `CLAUDE.md`: already updated in #312.
- #296 (Argentine items and spawn pools) beyond these four names.

## Sections touched

- **WORLD DATA:** `ITEM_REGISTRY`, `LIMA_STOP_TEXT`, `STOP_TEXT`,
  `stopAddress()`, `NAMED_SCENERY`, `BUILDING_TYPES` (the row house's garden),
  `landmarkInstances()`.
- **PERSISTENCE:** the load-time name refresh beside `backfillRegistryTags()`,
  and its call in `applyLoadedData()`.

This is content, plus one small load-time repair of the same kind as the
existing backfills. No rule the player acts under changes.

## UI changes

Names and text only, as tabled above: the map's markers and labels, Walk to…,
the Here panel's addresses, Enter labels, and item rows all read the new names
through the fields they already read.

## Validation the coding session should show

- A 0.10.1 save holding a Pack of galletitas, a Cédula verde, a DNI card and a
  Mate and bombilla loads with all four renamed. Put at least one of them in a
  container, one inside an equipped bag's `contents`, and one in the
  inventory.
- A named dish (a stew, say) in that save keeps its `dishName()` name, and a
  boiled pasta keeps "Boiled pasta".
- In the loaded 0.10.1 save, an old galletitas pack stacks with a newly spawned
  one under "Pack of biscuits".
- A grep of `ashfall.html`'s string literals finds none of: galletitas,
  Cédula, DNI, bombilla, Almacén/almacén, Comisaría/comisaría, Delegación,
  Escuela, Estación, parrilla, "barrio's". Ids and comments aside.
- `git diff origin/main...HEAD -- ashfall.html` touches only the version, the
  lines tabled above, the named comments, and PERSISTENCE's refresh. No page
  errors on load.

## Dependencies / issue linkage

Fulfils #310. Nothing is expected to be deferred. If something is, file it at
the wrap.

## After implementation

Open a pull request carrying the version bump (PATCH) and a new `CHANGELOG.md`
entry per `CHANGELOG_GUIDE.md`, referencing this handoff by path, recording the
two design decisions above, and closing #310 with `Closes #310`. Move this file
to `handoffs/archive/` in the same pull request.
