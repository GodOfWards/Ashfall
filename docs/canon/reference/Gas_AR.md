# Mains gas — how it reaches Lima, and what keeps it flowing

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Gathered for
the lore session (#329) on whether Lima's mains gas outlasts the grid
(#342), at Tom's request (2026-09-30). Lima's distributor and the Barrio
Atucha's connection are in `Lima.md`, "Utilities in Lima and the region";
garrafas are in `Fuel_AR.md`; the grid is in `Grid_AR.md`.

## The distributor: Naturgy BAN

- **30 municipalities of the northern and western Buenos Aires suburbs**;
  **more than 1,631,000 residential customers, 47,515 commercial, 1,219
  industrial, 394 CNG stations and 3 sub-distributors**; **27,389 km** of
  distribution network. It runs a **peak-shaving plant** (natural gas
  storage) to cover the months of peak demand. Primary:
  [Naturgy BAN, "Conocenos"](https://www.naturgyban.com.ar/conocenos/),
  read 2026-09-30 (undated). Whether the 30 include Zárate isn't stated
  there; `Lima.md` has Naturgy BAN as Zárate's distributor from its own
  site.
- **Most of the gas its users get comes from Vaca Muerta** (Neuquén).
  Secondary (search summary), 2026-09-30:
  [Diario Anticipos, 2026-07-24](https://diarioanticipos.com/2026/07/24/naturgy-la-empresa-espanola-que-distribuye-gas-en-gran-parte-del-gran-buenos-aires-y-te-cobra-lo-que-quiere/).
- **Its control centre and emergency service:** not found for Argentina.
  Naturgy's Mexican distributor runs a distribution control centre that
  watches pressure, temperature and flow over SCADA, and an emergency
  centre, **24 hours a day, 365 days a year**. Secondary, 2026-09-30:
  [Naturgy México](https://www.naturgy.com.mx/blog/hogar/conoce-nuestro-sistema-de-vigilancia-24-7-y-nuestro-ccau/)
  (search summary). BAN's own arrangement is unconfirmed.

## Transmission: TGN and TGS

- **TGN** holds the licence for the North and Centre-West systems
  (regulator: ENARGAS, Ley 24.076). **Primary**: TGN's report for the
  January 2024 public hearing,
  [TGN, "Audiencia Pública Ene. 2024"](https://www.tgn.com.ar/assets/media/2024/01/2024-01%20Informe%20AP%20-%20TGN.pdf),
  read in full text 2026-09-30:
  - the **Gasoducto Norte** runs from Campo Durán (Salta) to the **San
    Jerónimo** compressor plant (Santa Fe): 4,550 km, 12 compressor
    plants, 204,620 HP;
  - the **Gasoducto Centro Oeste** runs from **Loma La Lata (Neuquén)** to
    San Jerónimo: 2,256 km, 8 compressor plants, 171,000 HP;
  - **"From San Jerónimo, two parallel trunk lines connect with the
    high-pressure ring that feeds Greater Buenos Aires and the Federal
    Capital."**
  - TGN carries **40 % of the gas injected into Argentina's trunk
    pipelines**; operates about 11,100 km and **21 compressor plants
    (391,000 HP)**; **734 direct employees**; its critical systems include
    the compressor plants' and turbocompressors' control systems and
    SCADA.
- **TGS** runs about 9,248 km of pipelines from the south and west.
  Secondary: [Wikipedia](https://en.wikipedia.org/wiki/Transportadora_de_Gas_del_Sur).
- **Which trunk line or city gate feeds Zárate and Lima is unconfirmed.**
  The line to Lima came "above all" to supply the Atucha plant (Perfil,
  2013; `Lima.md`).
- **Compressor stations are built to run unattended**, steered over SCADA
  from a control centre (`Grid_AR.md`).

## Distribution runs without electricity

- **Gas pressure regulators are mechanical**: they hold a steady outlet
  pressure with no external power, throttling as demand rises and falls.
  Modern regulators with electronic control keep **mechanical pilots that
  take over if the electronics lose power**. So the network under the
  streets, and a house's cooker, keep working in a blackout for as long
  as there is pressure upstream. Secondary (manufacturers and DNV),
  2026-09-30:
  [Emerson](https://www.emerson.com/en/final-control/catalog/solutions/common-applications/natural-gas-distribution/natural-gas-pressure-regulators),
  [Alicat](https://www.alicat.com/articles/natural-gas-distribution-pressure-control/),
  [DNV, 2023](https://www.dnv.com/news/2023/managing-regulator-station-risk-mitigating-overpressure-and-outage-risks-in-pipelines-246245/)
  (search summaries).

## Who uses the gas, and when

- **Shares of daily production (recent year):** power generation **34 %**,
  industry **30 %**, residential **14 %**, CNG **5.5 %**.
- **Residential demand is seasonal:** about **17–20 million m³ a day**
  from October to April, rising to **55–70** in winter; heating is about
  56 % of residential use. Total demand in 2025 ranged from **96 MMm³/d**
  (November) to **144** (July).
- Under shortage, supply is cut in order: interruptible contracts, then
  power generation, industry and CNG, to protect priority (residential)
  demand.
- Secondary (search summaries), 2026-09-30:
  [Alpes Energy, 2025-05-30](https://www.alpesenergy.com/blog/2025/05/30/quien-consume-el-gas-natural-en-argentina/),
  [Alpes Energy, 2026-04-08](https://www.alpesenergy.com/ar/blog/2026/04/08/como-cambia-la-demanda-de-gas-entre-el-pico-invernal-y-el-mes-de-menor-consumo-del-ano/),
  [EconoJournal](https://econojournal.com.ar/destacada/cual-es-la-particularidad-del-mercado-argentino-de-gas/).

## The pipelines' own reserve (line pack)

- **Line pack** is the gas held in the pipelines by their pressure. Reports
  cite a loss of **2 MMm³** of line pack when compressor plants went off,
  and a **26.1 MMm³ deficit** that "compromised the stability of the
  national transport system". Secondary (search summary), 2026-09-30:
  [EconoJournal](https://econojournal.com.ar/energia/petrobras-enarsa-cortes-gas-industrias-crisis-servicio/);
  the events' dates and the system's normal line pack are **unconfirmed**.

## Production and processing

- **Process plants shut themselves down automatically when they lose
  their utilities**: emergency shutdown systems close isolation valves and
  bring the plant to a safe state, typically flaring what is in the units.
  A US refinery did exactly this on losing power on 13 September 2026.
  Secondary, 2026-09-30:
  [Wikipedia, "Process plant shutdown systems"](https://en.wikipedia.org/wiki/Process_plant_shutdown_systems),
  [ChemNet](https://news.chemnet.com/news-9890.html).
  **Whether Argentina's gas treatment plants run on their own generation
  or on the grid is unconfirmed.**

## Estimates — not facts (2026-09-30)

**Status: unconfirmed.** Reasoned from the facts above, for design use.

- **Once the grid fails, gas demand collapses**: power generation (34 %)
  stops burning it, industry is already shut, and most households are
  gone. What's left is a small summer load of cooking and water heating.
- **The supply side fails where people or electricity are needed**:
  treatment plants that draw on the grid shut down with it; wells and
  compressors are steered from control rooms.
- **So Lima's gas most likely outlasts the grid**, by however long the
  pipelines' pressure holds against that tiny load once supply stops — a
  period that can't be put in figures without the system's line pack, but
  **days at least**, plausibly longer. It **fades rather than stops**: the
  pressure falls, and a cooker's flame shrinks before it goes out.
- **If the gas companies sealed crews in, as the grid operators did,** the
  chain from Vaca Muerta could keep running far longer than the grid: its
  compressors burn the gas they move, and the demand left is small.
