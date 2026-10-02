# Reference — real-world facts, researched once

**This folder is real-world data, not lore.** It holds what the game needs to
know about the real world to be accurate (`docs/01-writing.md`, "A real place"):
codes, equipment, figures, the real town. It sits beside the canon because
both are designer knowledge the game never states outright.

## Rules

- **Look here first.** Sessions run with limited internet access, so this
  folder is the first and usually the only place a fact is looked up. A fact
  already here, with its source, isn't looked up again unless it's being
  re-verified. Check the open issues labelled `research` too: findings
  written there may not have merged here yet.
- **If it isn't here, don't guess and don't go searching on your own.** Do one
  of two things:
  - **ask Tom for network access** to research it now, if the work can't
    move without it; or
  - **file an issue labelled `research`**, from its template, saying which
    fact is needed, why, and which issue it blocks, and carry on with the
    rest, with the gap marked unconfirmed.
- **What gets researched is added here in the same session,** with its source,
  date and status. A fact found once and left in a conversation or an issue
  comment will be searched for again. A `research` issue's findings go in
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
  repeating figures. An open `research` issue is the one exception, until
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
| `Lima.md` | **The game's town:** Lima, Partido de Zárate, Buenos Aires. Its grid, rail, the Atucha complex, nearby towns, and the riverside walk; street surfaces by quarter; utilities (CEZ and its feeders into Lima, water, sewers, network gas); Cospli; the population figure's provenance; the Barrio Atucha's row houses from Street View |
| `Atucha.md` | **The Atucha complex, abandoned (#290):** the plants' state in February 2025, spent fuel and dry storage, decay heat, a station blackout, the pools' boil-off, and the three outcome cases for the canon; its crews, its 2020 pandemic measures, habitable control rooms, the 72-hour procedures, and the emergency plan that puts Lima in the 10 km zone; the diesels (4 × 50 % and 3 × 100 %), AR 3.9.1's two operators in the control room, Atucha II's heavy water, and estimates of how long the diesel fuel lasts unattended or with a crew (#350) |
| `Henderson.md` | **Retired, 2026-09-26.** The former town: its electricity, water, gas, crossings and plants; downtown's street grid, rail and buildings |
| `Gas_AR.md` | **Mains gas (#342, #329, #348, #404, #407):** Naturgy BAN, TGN's and TGS's pipelines to Buenos Aires, TGN's control room and its 2020 remote working, mechanical regulators that need no power, who uses the gas by season, ENARGAS's daily line pack for February 2025 and the operating range, plants' automatic shutdowns, which fields generate their own power; the line that feeds Zárate, Lima and Atucha from TGN's trunk, TGN's MAPO at the tap and Lima's gas users; Lima's two city gates on OSM and Naturgy BAN's network codes as pressure classes (#407); the city gates' measured pressures, distribution pressure classes, house regulators' manual-reset low-pressure cut-off and the 2025–2026 cases of it; NAG-100 on shut-offs that need a manual reset, and Lima's low-pressure streets with no house regulators (#407); marked estimates for gas outlasting the grid |
| `Grid_AR.md` | **How the national grid runs (#329, #220):** the SADI and CAMMESA's dispatch, Transener's transmission, the generation mix, automatic load relief, the 16 June 2019 blackout and its restoration, the February 2025 demand record; staffing, control rooms split under the 2020 lockdown, Transener's control room cut to one operator and a shift chief, CEZ's headcount and Guardia, how long a grid runs unattended |
| `Electrical_AR.md` | **Argentine electricity, the game's target (#286):** supply, the meter and boards (AEA 90364-7-770, OCEBA), IUG/TUG/TUE circuits and the grado de electrificación, IEC 60898-1 breakers, 30 mA RCDs, sockets and wire colours; old installations, *tapones* and gG fuses (#358); appliances at 220 V and extension cords (#311); small appliances, rating plates and the row house's board (#332, #305); cooker ratings, pump starts, compressors, lamp laws, CEZ's rules and appliance table (#316, #317, #320); feeding a building from a generator (#323); a 32" TV's draw, the washing machine's label, and front-loaders' rated power: the Longvie L8012 the game uses (#332); how the small appliances stop (#334); copper bodges, cable ampacity and PVC's limits (#365) |
| `Electrical.md` | **The US record, no longer the target:** US wiring code (NEC) and Kentucky's adoption, breakers (UL 489), panels and service, appliances and nameplates, lighting, GFCI, cords, meters, rail-crossing standby power |
| `Fuel_AR.md` | **Argentine fuel, the game's target (#287):** nafta and gasoil grades, blends and shelf life, stations and cans, garrafas (butane, propane, duration, Programa Hogar), portable generators |
| `Fuel_and_Generators.md` | **The US record, no longer the target:** gasoline (grades, shelf life, stations, cars, cans) and portable generators |
| `Calendar_AR.md` | **Around February 2025 (#329):** summer holidays by quincena, the labour law's leave, Buenos Aires province's school calendar and February's make-up modules for owed subjects, Carnival |
| `Outbreak_Response.md` | **COVID-19 as the real-world floor (#329):** Argentina's March 2020 timeline, panic buying, towns sealing their accesses (Zárate's checkpoints), ICUs at 97 %, hospital and funeral collapse in Guayaquil and Bergamo, health workers infected, Atucha running through lockdown |
| `Sound.md` | **How loud things are and how far they carry (#329, #12):** 6 dB per doubling of distance, air absorption, a quiet rural night, diesel generators' noise, and a worked distance table |
| `Batteries.md` | **What a cell reads on a voltmeter (#389):** at-rest and cutoff voltages for alkaline (AAA to D, 9 V), zinc-carbon, lithium AA, NiMH, coin cells, lithium-ion and 12 V lead-acid; charge-left tables for alkaline AA, lithium-ion and lead-acid; which cells Argentine radios and flashlights take; run times and weights of 2 × AA and 2 × D flashlights and 2 × AA pocket radios (#391); Ley 26.184 |
| `Water_Holders.md` | **What holds water (#393):** the mate thermos's sizes and empty weights (stainless, plastic with a glass liner), the 10 L household bucket, the canteen (military-style plastic with a cup, aluminium), the 20 L and 12 L returnable dispenser jugs and the 6.25 L supermarket jug |
| `Carbon_Monoxide.md` | Exposure effects, the body's level, CO alarms, generator placement |
