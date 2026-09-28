# The Atucha complex, abandoned: shutdown, cooling and spent fuel (#290)

Researched 2026-09-28 for #290: what happens to the Atucha nuclear complex
when nobody is left to run it, and whether neglect makes it a hazard. The
plants' history, site and surroundings are in `Lima.md`, "The Atucha nuclear
complex". See `README.md` for the status labels.

**Why it was asked** (Tom, #290): what happens to the reactors stays in the
canon, not the game, and has to be established. There is **no radiation
mechanic** ("this is a zombie apocalypse") **unless lack of maintenance really
does make radioactive material a hazard**. This file answers that: it can
(below, "The answer").

## The plants at the collapse (February 2025)

- **Atucha II: running.**
  - A pressurised heavy-water reactor, **2,160 MWt**, 745 MWe gross, 688 MWe
    net; on the grid since 2014-06-27. **Primary**, World Nuclear
    Association's reactor database
    ([WNA](https://world-nuclear.org/nuclear-reactor-database/details/atucha-2)).
  - Its core holds **451 fuel assemblies**, each 6.03 m long, of 37
    Zircaloy-clad rods, in individual coolant channels inside the heavy-water
    moderator tank. Secondary: the RELAP5/SCDAPSIM severe-accident paper,
    through its abstract ([OSTI](https://www.osti.gov/etdeweb/biblio/22750770)).
  - **Emergency power: four emergency diesel generators**, a German design
    choice from 1980, against the usual three. Secondary. **How long their
    fuel lasts is unconfirmed.**
- **Atucha I: shut down, and its reactor emptied.**
  - It stopped on **2024-09-29** for its 30-month life extension.
  - **All 241 fuel elements** (5.3 m each) were taken out of the reactor over
    126 days and moved to **the cooling pool in the radiologically controlled
    area**. **The emptying finished on 2025-02-02**, days before the collapse.
  - Framatome was contracted to decontaminate the primary circuit next. Its
    return was later put back to the second half of 2027.
  - Secondary, press: EconoJournal
    ([2025-02](https://econojournal.com.ar/2025/02/atucha-i-avanzan-las-tareas-de-extension-de-vida-de-la-central/),
    [2024-09](https://econojournal.com.ar/2024/09/nucleoelectrica-fondos-extension-de-vida-de-la-central-atucha-i/)).

## Spent fuel

- **Fuel removed from a reactor goes to cooling pools** ("piletas de
  enfriamiento diseñadas para lograr la disipación del calor"), and **once
  cooled, to dry storage, the ASECG** (*Almacenamiento en Seco de Elementos
  Combustibles Gastados*). **Primary**, NA-SA
  ([NA-SA](https://www.na-sa.com.ar/es/prensa/como-se-gestionan-los-combustibles-gastados-en-las-centrales-nucleares-argentinas)).
- **Atucha II's own dry store (ASECG II) didn't exist yet in the era.** It was
  under construction, 38 % complete in January 2026, for up to 50,000
  elements. Atucha II's pools were expected to fill around December 2027. The
  dry store is **passively ventilated**, "without needing electrical supply".
  Secondary, press.

## Decay heat: how fast it falls

- **General figures** (secondary: Wikipedia,
  [Decay heat](https://en.wikipedia.org/wiki/Decay_heat), citing standard
  sources):
  - **6.5 %** of full power at shutdown;
  - **1.5 %** after an hour;
  - **0.4 %** after a day;
  - **0.2 %** after a week.

  Spent fuel gives about **10 kW per tonne after a year**, and 1 kW/t after
  ten years. The Way–Wigner approximation covers 10 s to 100 days.
- **For Atucha II (2,160 MWt).** **Derived** from the figures above:

  | Time after shutdown | Heat |
  |---|---|
  | at shutdown | ≈ 140 MW |
  | 1 hour | ≈ 32 MW |
  | 1 day | ≈ 8.6 MW |
  | 1 week | ≈ 4.3 MW |
  | about a month (Way–Wigner) | ≈ 2–3 MW |

- **What that heat does to water.** **Derived**, from water's latent heat of
  2.26 MJ/kg: **1 MW boils off about 38 tonnes of water a day.** A month after
  shutdown, Atucha II's core would boil off roughly 100 tonnes a day with no
  cooling.

## What an unattended plant does

- **The reactor, if cooling is lost early.**
  - A station blackout at Atucha II (grid and all four diesels lost) was
    analysed with RELAP5/SCDAPSIM. In the high-pressure case, about
    **565 kg of hydrogen** had formed **by 45,000 s (about 12.5 hours)**, and
    **about 54,700 kg of UO₂ had slumped** to the lower plenum: a melted core.
  - The plant can remove decay heat **by natural circulation** as long as its
    steam generators have water. The moderator system can also serve as a
    high-pressure heat sink.
  - Secondary, through the paper's abstract
    ([OSTI](https://www.osti.gov/etdeweb/biblio/22750770)).
  - **So an Atucha II left without any cooling in its first days is a
    core-melt accident**, Fukushima-like. **With cooling for weeks first**,
    the heat left is a few MW and the timescales stretch to days or weeks.
    Derived.
- **The spent fuel pools, if cooling is lost.** This is what neglect really
  threatens: pools need circulation and make-up water, and Atucha I's holds a
  whole core only months out of the reactor.
  - Boil-off is slow because of a pool's large water inventory: "very large
    delay times". **If the water is lost**, though, fuel only **1 month** out
    of the reactor **could reach zirconium ignition in under 2 hours**, and
    fuel **3 months** out in **about 3 hours**. Decay heat is "quite
    manageable" after about a year, and a **fully drained pool is easier to
    air-cool than a partly drained one**. Secondary: the US NRC's
    spent-fuel-pool risk study, through search summaries
    ([NRC ML011020190](https://www.nrc.gov/docs/ML0110/ML011020190.pdf)).
  - **About 6 m of water** over the fuel keeps radiation acceptable; pools
    are typically **12 m** deep. Secondary: Wikipedia,
    [Spent fuel pool](https://en.wikipedia.org/wiki/Spent_fuel_pool).
  - **Fukushima Daiichi Unit 4's pool**, whose core had been offloaded months
    before, **did not boil dry**. The NRC's claim at the time that it had was
    wrong. Secondary, same source.
  - **So:** an uncooled pool boils down over **weeks to months**, derived from
    the heat and a pool's size. As the water drops below about 6 m over the
    fuel, **radiation near the pool rises sharply**. If the fuel is uncovered
    while still hot, a **cladding fire** releasing radioactivity is possible.
    That risk falls steeply with the fuel's age.

## The answer (for the canon)

**Yes, neglect can make it a hazard.** Radioactive material doesn't become
dangerous merely by being left alone. It becomes dangerous when **cooling
stops while the fuel is still hot**. Three cases:

1. **Atucha II is shut down properly and cooled for weeks by its diesels**,
   then abandoned. Its core and pools boil down slowly over **weeks to
   months**: a radiation hazard near the buildings once the water is low, and
   a possible release later.
2. **Atucha II loses all cooling in its first hours or days.** **A core melt
   within about half a day** (the station-blackout analysis), with hydrogen:
   **a Fukushima-scale release.**
3. **Atucha I's pool** holds a whole core only months old, so it is the
   **slowest and most certain** hazard: weeks to months of boil-off, then
   high radiation, and possibly a cladding fire.

These are not exclusive: case 3 happens alongside 1 or 2 unless someone keeps
the pool cooled. **Which happened is Tom's decision in the canon** (#329). The
game only shows what the road shows.

## Not yet researched

- How long Atucha II's diesels run on their tanks, and whether Atucha has
  post-Fukushima portable equipment (pumps, mobile generators).
- The pools' volumes and heat loads, for Atucha I and Atucha II.
- Heavy water and tritium: the moderator and coolant are heavy water, which
  carries tritium, and a release would come with steam or a breach.
- What is visible from outside the fence.
- The ARN's post-Fukushima stress-test report for Atucha.

Sources to try: ARN reports, NA-SA's technical pages, IAEA PRIS, and
Argentina's national report to the Convention on Nuclear Safety.
