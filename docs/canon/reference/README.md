# Reference — real-world facts, researched once

**This folder is real-world data, not lore.** It holds what the game needs to
know about the real world to be accurate ("The world is real", `CLAUDE.md`):
codes, equipment, figures, the real town. It sits beside the canon because
both are designer knowledge the game never states outright.

## Rules

- **Look here first.** Sessions run with limited internet access, so this
  folder is the first and usually the only place a fact is looked up. A fact
  already here, with its source, isn't looked up again unless it's being
  re-verified. Check the open `Research:` issues too: findings written there
  may not have merged here yet.
- **If it isn't here, don't guess and don't go searching on your own.** Do one
  of two things:
  - **ask Tom for network access** to research it now, if the work can't
    move without it; or
  - **file a `Research:` issue** saying which fact is needed, why, and which
    issue it blocks, and carry on with the rest, with the gap marked
    unconfirmed.
- **What gets researched is added here in the same session,** with its source,
  date and status. A fact found once and left in a conversation or an issue
  comment will be searched for again. A `Research:` issue's findings go in
  two places:
  - **the issue's body, edited as soon as they're found,** with sources, dates
    and status, so a session running before the merge can read them;
  - **this folder, in a pull request that says `Closes #NN`.** Once it merges,
    the file is the record and the closed issue is history.
- **Every fact carries its source and the date it was checked.** Its status is
  one of:
  - **Confirmed:** read on the primary source (the maker, the regulator, the
    standard, the utility).
  - **Secondary:** read on a trade article, retailer listing or search summary
    that quotes or restates the primary, but not on the primary itself.
  - **Unconfirmed:** a figure the game uses without a source that states it.
    Say so, and say what would confirm it.
- **One source of truth.** Issues and handoffs point here rather than
  repeating figures. An open `Research:` issue is the one exception, until
  its pull request merges. A handoff **quotes** the figures its pass needs, because a
  coding session never reads this folder (`CLAUDE.md`, "The canon is private").
  The issue comments that first recorded a fact stay as history.
- **When a figure here and a figure in the game disagree,** the file wins as
  the record of the real world. The disagreement is filed as an issue (or
  noted on a live handoff), not silently fixed in either place.

## Who reads it

A **planning session reads it whenever the discussion needs real-world facts**,
not only for lore. The lore file (`../Ashfall_Canon.md`) keeps its stricter
rule. A coding session reads neither.

## Files

| File | Covers |
|---|---|
| `Lima.md` | **The game's town:** Lima, Partido de Zárate, Buenos Aires. Its grid, rail, the Atucha complex, nearby towns, and the riverside walk; street surfaces by quarter; utilities (CEZ, water, sewers, network gas); the Barrio Atucha's row houses from Street View |
| `Atucha.md` | **The Atucha complex, abandoned (#290):** the plants' state in February 2025, spent fuel and dry storage, decay heat, a station blackout, the pools' boil-off, and the three outcome cases for the canon; its crews, its 2020 pandemic measures, habitable control rooms, the 72-hour procedures, and the emergency plan that puts Lima in the 10 km zone |
| `Henderson.md` | **Retired, 2026-09-26.** The former town: its electricity, water, gas, crossings and plants; downtown's street grid, rail and buildings |
| `Gas_AR.md` | **Mains gas (#342, #329):** Naturgy BAN, TGN's and TGS's pipelines to Buenos Aires, mechanical regulators that need no power, who uses the gas by season, line pack, plants' automatic shutdowns; marked estimates for gas outlasting the grid |
| `Grid_AR.md` | **How the national grid runs (#329, #220):** the SADI and CAMMESA's dispatch, Transener's transmission, the generation mix, automatic load relief, the 16 June 2019 blackout and its restoration, the February 2025 demand record; staffing, control rooms split under the 2020 lockdown, how long a grid runs unattended |
| `Electrical_AR.md` | **Argentine electricity, the game's target (#286):** supply, the meter and boards (AEA 90364-7-770, OCEBA), IUG/TUG/TUE circuits and the grado de electrificación, IEC 60898-1 breakers, 30 mA RCDs, sockets and wire colours; old installations, *tapones* and gG fuses (#358); appliances at 220 V and extension cords (#311); small appliances, rating plates and the row house's board (#332, #305); cooker ratings, pump starts, compressors, lamp laws, CEZ's rules and appliance table (#316, #317, #320); feeding a building from a generator (#323) |
| `Electrical.md` | **The US record, no longer the target:** US wiring code (NEC) and Kentucky's adoption, breakers (UL 489), panels and service, appliances and nameplates, lighting, GFCI, cords, meters, rail-crossing standby power |
| `Fuel_AR.md` | **Argentine fuel, the game's target (#287):** nafta and gasoil grades, blends and shelf life, stations and cans, garrafas (butane, propane, duration, Programa Hogar), portable generators |
| `Fuel_and_Generators.md` | **The US record, no longer the target:** gasoline (grades, shelf life, stations, cars, cans) and portable generators |
| `Calendar_AR.md` | **Around February 2025 (#329):** summer holidays by quincena, the labour law's leave, Buenos Aires province's school calendar and February's make-up modules for owed subjects, Carnival |
| `Outbreak_Response.md` | **COVID-19 as the real-world floor (#329):** Argentina's March 2020 timeline, panic buying, towns sealing their accesses (Zárate's checkpoints), ICUs at 97 %, hospital and funeral collapse in Guayaquil and Bergamo, health workers infected, Atucha running through lockdown |
| `Sound.md` | **How loud things are and how far they carry (#329, #12):** 6 dB per doubling of distance, air absorption, a quiet rural night, diesel generators' noise, and a worked distance table |
| `Carbon_Monoxide.md` | Exposure effects, the body's level, CO alarms, generator placement |
