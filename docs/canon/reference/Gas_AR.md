# Mains gas — how it reaches Lima, and what keeps it flowing

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Gathered for
the lore session (#329) on whether Lima's mains gas outlasts the grid
(#342), at Tom's request (2026-09-30). Lima's distributor and the Barrio
Atucha's connection are in `Lima.md`, "Utilities in Lima and the region";
garrafas are in `Fuel_AR.md`; the grid is in `Grid_AR.md`.
Line pack, the fields' power and TGN's control room were added for #348
(2026-10-01).

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
- **TGN's map** draws the trunk from San Jerónimo straight to the Buenos
  Aires ring, with the **Escobar** LNG delivery point beside it and the
  **Escobar–Cardales** pipeline (31 km, YPF-GNL, run by TGN). **Primary but
  schematic**:
  [TGN, "Sistema TGN y gasoductos vinculados", 2023](https://www.tgn.com.ar/assets/media/2023/05/tgn_mapa_2023.pdf),
  read 2026-10-01. Too schematic to show whether the trunk crosses the
  Partido de Zárate.
- **The Mercedes–Cardales pipeline** (30", 80 km) joins TGS's system to
  TGN's at **Cardales**, where there is a compressor plant; up to
  **15 MMm³/d**. **Primary**: TGN, Audiencia Pública Ene. 2024 (above),
  p. 41, read 2026-10-01; secondary:
  [EconoJournal, 2023-12](https://econojournal.com.ar/2023/12/el-gasoducto-mercedes-cardales-ya-entro-en-operacion-y-comenzo-a-transportar-gas-de-vaca-muerta/).
- **Which trunk line or city gate feeds Zárate and Lima is unconfirmed**,
  as is the Atucha plant's line. Naturgy BAN's site, TGN's reports and OSM
  name none (2026-10-01). The line to Lima came "above all" to supply the
  Atucha plant (Perfil, 2013; `Lima.md`). ENARGAS's list of Naturgy BAN's
  delivery points (*puntos de entrega*) would confirm it.
- **TGN runs its whole system from one control room at its Buenos Aires
  headquarters, 24 hours a day, 365 days a year.** **Primary**: TGN,
  Audiencia Pública Ene. 2024 (above), p. 4, read 2026-10-01.
- **In the 2020 lockdown TGN moved its staff onto remote access**: mass
  remote access to corporate systems, remote access to operational
  workstations, and mixed-reality headsets ("Remote Eye") so a field crew
  could be talked through a task by specialists elsewhere. **Primary**:
  [TGN, talk at the Centro Argentino de Ingenieros, 2020-07](https://www.tgn.com.ar/assets/media/2020/07/CharlaCAI.pdf),
  read 2026-10-01. **Whether TGN, TGS or Naturgy BAN sealed control-room
  crews in, as the grid operators did, was not found.**
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

- **Line pack** is the gas held in the pipelines by their pressure.
  **ENARGAS publishes the whole transmission system's line pack every
  day**, as of 06:00, with its change from the day before. **Primary**
  (ENARGAS, *Reporte Diario del Sistema*), read 2026-10-01:

  | Day | Line pack | Change | Demand in the system | Of which priority (residential) |
  |---|---|---|---|---|
  | 2 Jan 2020 | 348.5 MMm³ | +8.29 | 107.1 MMm³/d | 14.1 |
  | 3 Feb 2025 | 343.4 MMm³ | +1.1 | 136.5 MMm³/d | 14.5 |
  | 14 Feb 2025 | 327.6 MMm³ | −0.4 | 123.9 MMm³/d | 17.3 |
  | 24 Feb 2025 | 340.1 MMm³ | +2.8 | 137.6 MMm³/d | 17.0 |

  In February 2025 the power plants (CAMMESA) took **52–69 MMm³/d**,
  industry about **35**, CNG about **5–6**, and the system's own fuel
  (compressors) about **4**. Exports ran at about **7 MMm³/d** through TGN
  and **2** through TGS. The demand figures exclude power plants at the
  wellhead.
  [2020-01-02](https://www.enargas.gob.ar/secciones/transporte-y-distribucion/reporte-diario-sistema/RDS_20200102.pdf),
  [2025-02-03](https://www.enargas.gob.ar/secciones/transporte-y-distribucion/reporte-diario-sistema/RDS_20250203.pdf),
  [2025-02-14](https://www.enargas.gob.ar/secciones/transporte-y-distribucion/reporte-diario-sistema/RDS_20250214.pdf),
  [2025-02-24](https://www.enargas.gob.ar/secciones/transporte-y-distribucion/reporte-diario-sistema/RDS_20250224.pdf).
- **The dispatch rule makes line pack a daily input**: the transporters
  report it at 06:00 with its change, alongside hourly inlet pressures,
  regulated pressures and flow at each delivery point on the **Anillo de
  Buenos Aires**. **Primary**:
  [ENARGAS, NAG-601 (2019, in public consultation)](https://www.enargas.gob.ar/secciones/normativa/pdf/normas-discusion/NAG-601.pdf),
  read 2026-10-01.
- **The system operates between 312 and 368 MMm³.** It fell from 357
  (10 May 2024) to **308** (17 May), "below the recommended minimum". In
  the July 2025 cold wave it lost **almost 30 MMm³ in 24 hours**, falling to
  319.2. Earlier reports cite a loss of **2 MMm³** when compressor plants
  went off, and a **26.1 MMm³ deficit** that "compromised the stability of
  the national transport system" (dates unconfirmed). Secondary (press
  citing ENARGAS data), 2026-10-01:
  [LM Neuquén, 2024-05-20](https://mase.lmneuquen.com/energia/cortes-gas-las-alternativas-del-sistema-evitar-una-crisis-n1114936),
  [Agendar, 2025-07-04](https://agendarweb.com.ar/2025/07/04/el-sistema-de-gas-natural-al-limite-ante-la-ola-polar-las-interrupciones-en-hogares-e-industrias/),
  [EconoJournal](https://econojournal.com.ar/energia/petrobras-enarsa-cortes-gas-industrias-crisis-servicio/).
- **How low line pack can fall and still feed a city gate** (the
  distribution networks' minimum inlet pressure) is **unconfirmed**.

## Production and processing

- **Process plants shut themselves down automatically when they lose
  their utilities**: emergency shutdown systems close isolation valves and
  bring the plant to a safe state, typically flaring what is in the units.
  A US refinery did exactly this on losing power on 13 September 2026.
  Secondary, 2026-09-30:
  [Wikipedia, "Process plant shutdown systems"](https://en.wikipedia.org/wiki/Process_plant_shutdown_systems),
  [ChemNet](https://news.chemnet.com/news-9890.html).
- **What the fields and plants run on is mixed; some don't need the grid.**
  - **Fortín de Piedra** (Tecpetrol), one of Vaca Muerta's largest gas
    fields: a 33 kV line, 12.5 km long, feeds **all its gas wells** and its
    fracking water pumps with **self-generated power**, burning treated gas
    from its own processing plant (CPF). Supply is available 99.8 % of the
    time. **Primary**:
    [Tecpetrol, "Crecer con energía propia", 2023-04-24](https://www.tecpetrol.com/es/noticias/2023/fortin-de-piedra-energia-autogenerada),
    read 2026-10-01. The CPF processes up to **17 MMm³/d** (secondary:
    [EconoJournal](https://econojournal.com.ar/oilgas/tecpetrol-inauguro-su-planta-central-de-procesamiento-de-gas-en-vaca-muerta/)).
  - **Vista** connected its operations, including an electric compressor,
    to the national grid through EPEN's Loma Campana substation. Secondary:
    [Ámbito, 2024-04-05](https://www.ambito.com/energia/vista-electrifico-el-primer-equipo-perforacion-vaca-muerta-n5976679),
    2026-10-01.
  - **Oil wells generally run on their own generation**, mostly diesel
    engines. Secondary (search summary), 2026-10-01:
    [UNMdP thesis](https://rinfi.fi.mdp.edu.ar/handle/123456789/1133).
  - **TGS's Tratayén conditioning plant** (15 MMm³/d, expanding to 28)
    imported motor-generators for its expansion. Secondary (search
    summary), 2026-10-01:
    [Mejor Energía, 2025-06-16](https://www.mejorenergia.com.ar/noticias/2025/06/16/4265-tgs-avanza-con-la-ampliacion-de-su-capacidad-de-tratamiento-de-gas-en-tratayen-y-la-expansion-en-bahia-blanca).
    Whether it also draws on the grid is unconfirmed.
- **What happened to gas production in the 16 June 2019 blackout** was not
  found (2026-10-01).

## Estimates — not facts (2026-10-01)

**Status: unconfirmed.** Reasoned from the facts above, for design use.
Revises the estimate of 2026-09-30, which had no line-pack figures.

- **Once the grid fails, gas demand collapses**: power generation stops
  burning it, industry is already shut, and most households are gone.
  What's left is a small summer load of cooking and water heating, well
  under the 14–17 MMm³/d of February's priority demand.
- **Above the operating floor the system holds about 15–30 MMm³**: a few
  hours of normal February demand, or **one to two days** of residential
  demand alone.
- **Below the floor, gas keeps flowing at falling pressure.** The floor is
  set so that full demand still reaches the far ends, not a trickle. So a
  large share of the **~330 MMm³** in the pipes can be drawn, how large
  depending on the unconfirmed city-gate pressure. Against a load of a few
  MMm³/d that is **weeks to months**, before leaks and broken pipes.
- **Injection need not stop with the grid.** Fields with their own power,
  such as Fortín de Piedra, and compressors that burn the gas they move,
  keep going while their crews last and nothing trips them. Grid-fed
  operations, such as Vista's electric compressor, stop with the grid.
  Exports to Chile draw on the same pipes while anyone takes them.
- **So Lima's gas most likely outlasts the grid by weeks, plausibly
  months.** It **fades rather than stops**: the pressure falls, and a
  cooker's flame shrinks before it goes out.
- **This disagrees with `Grid_AR.md`'s "gas pipelines hold pressure 1–3
  days unattended"**, an anonymous North American estimate. That figure
  fits normal demand with no injection, not the collapse's small load.
