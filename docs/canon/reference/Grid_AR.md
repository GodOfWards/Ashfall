# How Argentina's grid runs — the national system

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Gathered for
the lore session on how the grid fails after the collapse (#329, #220), at
Tom's request (2026-09-29): how the grid operates normally, before deciding
how it stops. Lima's own distributor (CEZ) and its feeds are in `Lima.md`,
"Utilities in Lima and the region"; household wiring is in
`Electrical_AR.md`.

## The system and who runs it

- **The SADI** (*Sistema Argentino de Interconexión*) is the national grid.
  It covers every province but Tierra del Fuego, and interconnects with
  Chile, Paraguay, Uruguay and Brazil. Secondary, 2026-09-29:
  [en.wikipedia](https://en.wikipedia.org/wiki/Argentine_Interconnection_System).
- **CAMMESA** (*Compañía Administradora del Mercado Mayorista Eléctrico*),
  created in 1992, is the **dispatcher** (*Organismo Encargado del
  Despacho*, OED): it coordinates generators, transmission companies and
  distributors, sets wholesale prices and runs the market. Private
  management with a public purpose, non-profit; 80 % owned in equal 20 %
  shares by the associations of generators, distributors, transmission
  companies and large users. Offices in Buenos Aires and Pérez (Santa Fe).
  Secondary, 2026-09-29:
  [CAMMESA, "Empresa"](https://cammesaweb.cammesa.com/empresa/),
  [Editores](https://www.editores.com.ar/institucion/cammesa).
- **Its operations centre (COC) keeps generation and demand in balance
  "instant by instant"**: it dispatches hydro and thermal generation in real
  time, assigns primary and secondary frequency regulation, and supervises
  the operating reserves. Secondary (search summary), 2026-09-29:
  [Mercado Eléctrico](https://www.melectrico.com.ar/web/index.php?option=com_content&view=article&id=1882:cammesa-la-seguridad-de-la-operacion-del-sistema-argentino-de-interconexion-es-nuestra-principal-prioridad&catid=1:latest-news&Itemid=1).
  **Where the COC is, and how it is staffed (shifts, a backup centre), is
  unconfirmed:** the pages read don't say.

## Transmission

- **Transener** runs the high-voltage network: **20,296 km**, of which
  **14,197 km at 500 kV**, the backbone; also 220 kV and 132 kV. Many lines
  up to 220 kV hang on concrete pylons. Secondary, 2026-09-29:
  [en.wikipedia](https://en.wikipedia.org/wiki/Argentine_Interconnection_System).
- In Buenos Aires province the 132 kV regional network is **Transba**'s,
  which feeds Lima's distributor (`Lima.md`).

## Generation

- **Installed capacity, September 2024: 42,920 MW**, of which **59 %
  thermal, 37 % renewable (hydro included), 4 % nuclear.** Secondary,
  2026-09-29:
  [Argendata](https://argendata.fund.ar/topico/transicion-energetica/)
  (search summary).
- **Energy produced, by source (recent year, as reported):** hydro 16.5 %,
  wind 11 %, **nuclear 7.1 %**, solar 2.7 %, bioenergy 1.6 %; the rest
  thermal. Renewables covered a little over 34 % in 2024. Secondary
  (search summaries), 2026-09-29: Argendata, above;
  [CAMMESA, "Resumen Anual 2024"](https://cammesaweb.cammesa.com/2025/01/29/resumen-anual-2024/)
  (listed, not read).
- **Thermal plants burn natural gas from the pipelines**, with **gasoil or
  fuel oil as backup** in winter and at demand peaks. How many days of
  backup fuel a plant stores is unconfirmed. Secondary, 2026-09-29:
  [MSU Energy](https://msuenergy.com/que-combustibles-se-utilizan-en-la-generacion-de-energia-en-argentina/)
  (search summary).

## Automatic protection

- **Under-frequency load relief (*alivio de carga*).** When frequency
  falls, relays at the distributors, large users and self-generators
  **disconnect demand automatically**, as a short-term reserve that keeps
  the system standing. CAMMESA sets the scheme; the thresholds (Hz) and
  shares of demand shed are in its *Instructivo Alivio de Carga*, not read.
  Secondary, 2026-09-29:
  [CAMMESA, "Alivio de Cargas"](https://cammesaweb.cammesa.com/alivio-de-cargas/).
- **Automatic generation disconnection (DAG).** When a line is lost,
  generators are signalled to drop output so they don't flood what's left.
  Its failure is what made 2019 total (below).

## When it failed: 16 June 2019

- **07:06, Sunday 16 June 2019:** a short circuit on the **500 kV Colonia
  Elía–Campana line**, while Transener worked on **tower 412**, eroded by
  the Paraná Guazú. A bypass had been installed but **not entered in the
  DAG**, so generators never got the signal to reduce: **1,200 MW of excess
  generation**.
- **Argentina (all but Tierra del Fuego) and Uruguay went dark in about 30
  seconds**, more than 50 million people. Only two towns with their own
  generation (Ticino, Los Toldos) stayed lit.
- **Restoration took about 13–14 hours**, finishing around 20:30, by
  coordinated work with **Yacyretá** as the largest contributor; the
  Litoral came back first; El Chocón and other regional plants were slow to
  start. Atucha II ran on house load and was generating 250 MW during the
  recovery (see also `Atucha.md`).
- ENRE sanctioned Transener in 2021 for "negligent action".
- Secondary, 2026-09-29:
  [es.wikipedia](https://es.wikipedia.org/wiki/Apag%C3%B3n_de_Argentina,_Paraguay_y_Uruguay_de_2019),
  [Infobae, 2023-03-01](https://www.infobae.com/economia/2023/03/01/como-fue-el-apagon-del-siglo-del-dia-del-padre-de-2019-que-dejo-sin-electricidad-a-50-millones-de-personas/).
- **The failing line ends at Campana**, about 14 km beyond Zárate
  (`Lima.md`), where Transba runs the 500 kV ET Campana: the fault was in
  Lima's region. Where exactly tower 412 stands is unconfirmed.

## February 2025: the summer peak

- **Monday 10 February 2025, 14:45: a record national demand of
  30,240.2 MW**, in a heat wave (over 40 °C in several provinces, over
  37 °C in the Buenos Aires metropolitan area). The previous record was
  29,653 MW on 1 February 2024.
- Thermal plants supplied **more than 17,000 MW**; about **1,500 MW** came
  from Brazil. A **voltage collapse in the NEA shed 700 MW** around 14:00,
  and there were **power cuts in several provinces**.
- Secondary, 2026-09-29:
  [EconoJournal](https://econojournal.com.ar/2025/02/ola-de-calor-argentina-supero-el-record-historico-de-consumo-de-energia-con-30-240-mw/),
  [Infobae, 2025-02-10](https://www.infobae.com/economia/2025/02/10/ola-de-calor-la-argentina-alcanzo-un-nuevo-record-de-consumo-de-electricidad-y-hay-cortes-de-luz-en-el-interior/),
  [La Nación](https://www.lanacion.com.ar/economia/ola-de-calor-se-registro-un-nuevo-record-de-consumo-electrico-nid10022025/).

## Staffing, and running without people

- **Power stations are staffed around the clock.** Combined-cycle plants
  commonly run a **five-shift rotation of 12-hour shifts**; a 300–600 MW
  combined-cycle plant has about **25–40 staff** in all, not all on shift.
  Secondary (an O&M consultancy's benchmark, US-oriented), 2026-09-29:
  [USPE Global](https://uspeglobal.com/articles/power-plant-om-staffing-levels/)
  (search summary). Argentine plants' own figures are unconfirmed.
- **Gas pipeline compressor stations are built to run unattended**,
  started, stopped and set remotely over SCADA from a control centre, with
  small maintenance crews on site. The transmission system is robust: if a
  compressor station drops out, gas bypasses it and pressure falls
  gradually; gas plants keep running while their inlet pressure holds.
  Secondary, 2026-09-29:
  [ASME IPC 2002, "Remote Operation of Unattended Pipeline Compressor Stations"](https://asmedigitalcollection.asme.org/IPC/proceedings/IPC2002/36207/1049/293609),
  [NETL, "Natural Gas Compressors and Processors"](https://www.netl.doe.gov/projects/files/NGCompressorsandProcessors%E2%80%93OverviewandPotentialImpactonPowerSystemReliability_071817.pdf)
  (search summaries). Argentina's pipelines (TGS, TGN) not checked.
- **Argentine distributors under the 2020 lockdown split their control
  rooms so one crew could be isolated without losing the network.** Edesur
  added two backup centres, making **four** (two for low voltage, two for
  medium and high), each with its own team of operators; Edenor already had
  **two identical control centres in separate buildings**, each able to run
  100 % of the network. The aim: "to be ready if one of the work groups had
  to be isolated". Secondary, 2026-09-29:
  [La Nación, 2020-03-15](https://www.lanacion.com.ar/economia/coronavirus-edesur-edenor-se-preparan-seguir-prestando-nid2343596/).
- **In the US, grid operators were sequestered on site in 2020.** NYISO
  kept 37 people living in trailers at its control centre and a backup site
  15 miles away (14 operators each), on 12-hour shifts, with a cook and
  cleaners sequestered too; PJM and National Grid (about 200 people) did the
  same from April 2020. Secondary, 2026-09-29:
  [Smart Energy International](https://www.smart-energy.com/industry-sectors/energy-grid-management/new-york-grid-operators-self-isolate-over-covid-19-fears/),
  [NBC News](https://www.nbcnews.com/tech/security/prepared-worst-electrical-grid-workers-isolate-coronavirus-spreads-n1173171),
  [APPA](https://www.publicpower.org/blog/power-industrys-mission-essential-workers-ensure-flow-power-during-pandemic).
  Whether CAMMESA or Transener did the same in 2020 wasn't found.
- **CEZ runs a 24-hour telephone line for Lima's complaints**, with
  operators "exclusive" to Lima (2015). Primary:
  [CEZ, "Call Center Lima"](https://cezarate.com/2015/01/call-center-lima/).
  How CEZ's network control and repair crews are staffed is unconfirmed.
- **How long a grid lasts with no one at all: an informal estimate only.**
  A Straight Dope column (Science Advisory Board, undated), citing unnamed
  plant operators and pipeline engineers and the 2003 North American
  blackout report, puts it at: scattered blackouts within **4–6 hours**, much
  of the system unstable by **12 hours**, most of the continent dark within
  **24 hours**, a few isolated sites by a week. By plant: coal needs an
  operator response to a critical alarm every 1–3 hours and trips within
  12–18 hours; nuclear might run a few days to a week; hydro days or weeks;
  gas pipelines hold pressure 1–3 days unattended. The weak link is the
  interconnected grid, not any one plant's fuel.
  [Straight Dope](https://www.straightdope.com/21343298/when-the-zombies-take-over-how-long-till-the-electricity-fails).
  **Unconfirmed**: a North American estimate by an anonymous columnist, not
  a study; it is the only one found.

## Who operates each layer (#346, 2026-09-29)

- **CAMMESA's operations centre (COC) is at Pérez, Santa Fe**, near
  Rosario: "the highest operating authority of the SADI", coordinating the
  system and dispatch in real time. A **backup emergency operations centre
  at the Polo Tecnológico de Rosario** holds **up to 15 operators**
  (CAMMESA staff and outside agents), for events that "could affect
  operation from the Control Centre at Pérez". Shift pattern and operators
  per shift at the COC: unconfirmed. Secondary, 2026-09-29:
  [Argentina.gob.ar](https://www.argentina.gob.ar/noticias/el-subsecretario-de-energia-electrica-inauguro-el-nuevo-centro-de-operaciones-de-emergencia)
  (undated), [ETDEWEB, "CAMMESA control center controllers qualification"](https://www.osti.gov/etdeweb/biblio/20930150)
  (search summary).
- **Transener runs its whole high-voltage network remotely from a single
  control centre at the ET Rosario Oeste, also in Pérez**, "with a reduced
  staff of highly qualified personnel". Its substations are **unattended**:
  technicians assigned permanently to each station do the maintenance and
  keep **passive on-call rotas (*guardias pasivas*)**, going to the station
  at once in an emergency. Secondary (search summary of Transener's
  "Operaciones de líneas y estaciones transformadoras"; the page itself
  wouldn't load), 2026-09-29:
  [Transener](https://www.transener.com.ar/en/operacionesdelineas/).
- **Transba (Lima's 132 kV supplier) is telecontrolled** over SCADA from its
  **COTDT at the Ezeiza substation**, which controls **75 high-to-medium
  voltage transformer stations** across the province, with regional centres
  at Bragado, San Nicolás, Olavarría and Bahía Blanca. Remote command from
  the operations centre is "the usual operating mode"; local operation is
  inhibited while it holds. About 5,500 km of 500/220/132/66 kV lines.
  Secondary, 2026-09-29:
  ["Sistema de telecontrol de Transener y Transba"](http://www.luisosens.com.ar/archivos/Telecontrol_Transener.pdf),
  [silo.tips copy](https://silo.tips/download/sistema-de-telecontrol-de-transba-sa-tema-01-centros-de-control)
  (search summaries; the paper's date unconfirmed).
- **Yacyretá** (20 Kaplan turbines, about 14 % of the SADI's energy in
  2019): a main control room with a **shift chief and operators** for
  dispatch and load control, plus an extra control room per five turbines;
  **about 420 workers** in all, over 300 of them in maintenance (140
  Argentine and 170 Paraguayan in the main plant area). Secondary,
  2026-09-29:
  [La Nación, 2019-07-25 (updated 2024-01-10)](https://www.lanacion.com.ar/economia/negocios/yacyreta-dentro-como-es-central-produce-14-nid2270742/).
  How long it would keep generating unattended: only the informal estimate
  above (hydro: days to weeks).
- **CEZ, Lima's distributor:** about **38,961 users** by another count (the
  41,000 in `Lima.md` is CEZ's own). Its staff, crews and on-call rotas were
  **not found**. Secondary, 2026-09-29:
  [Unión Industrial de Zárate](http://www.uizarate.com.ar/asociadas/cez/)
  (search summary).

## Backup fuel at thermal plants (#346)

- **Central Termoeléctrica Guillermo Brown** (General Daniel Cerri, near
  Bahía Blanca): **two 290 MW turbines** (580 MW) that burn gas, gasoil or
  biodiesel. **Three 10,000 m³ gasoil tanks and one 5,000 m³ biodiesel
  tank**; consumption about **1,800 m³ a day per 300 MW turbine**. Secondary,
  2026-09-29:
  [Casa Rosada, inauguration](https://www.casarosada.gob.ar/pdf/Inauguraci_n_Central_Termoel_ctrica_Guillermo_Brow.pdf),
  [Cooperativa CALF](https://www.cooperativacalf.com.ar/la-central-guillermo-brown-ya-aporta-580-megavatios-al-sistema-interconectado-nacional/)
  (search summaries).
  - **Derived, not stated by the source:** 35,000 m³ at 3,600 m³ a day is
    **about 10 days with both turbines at full load**, about 19 with one.
- **Central Térmica Ensenada Barragán:** two Siemens gas turbines, up to
  567 MW, gas or diesel, **two tanks totalling 45,000 m³**. Its consumption
  wasn't given. Secondary, 2026-09-29:
  [0221, 2023-01-30](https://www.0221.com.ar/nota/2023-1-30-18-27-0-como-es-la-obra-que-inauguro-alberto-fernandez-en-ensenada)
  (search summary).
- So a dual-fuel plant's own tanks hold **days to a couple of weeks** of
  full-load running, if someone is there to switch it to liquid fuel and
  run it. Two plants only; not a figure for the fleet.

## What the industry says about losing its staff (#346)

- **No study was found that says how long a grid stays up as its operators
  are lost.** What was found:
  - NERC (the North American reliability body) called **the loss of
    critical staff "the most fundamental threat"** to the bulk power system
    in its *Pandemic Preparedness and Operational Assessment*, spring 2020,
    and warned that control centres or plants could be **temporarily shut
    down** if enough of their operators fell ill, despite sequestration.
  - **Real-time operation "is not fully automated and requires continuous
    human intervention"**, in normal running and in faults alike (an IEEE
    Access paper, 2020).
  - The US utilities' association (EEI) planned for **up to 40 % of the
    workforce out sick**.
  - Secondary (search summaries), 2026-09-29:
    [APPA on NERC's report](https://www.publicpower.org/periodical/article/nerc-highlights-potential-summer-power-grid-issues-tied-pandemic),
    [Utility Dive](https://www.utilitydive.com/news/grid-operators-cancel-travel-shift-to-remote-meetings-as-industry-preps-f/573988/),
    [IEEE Access, doi:10.1109/ACCESS.2020.3041247](https://doi.org/10.1109/ACCESS.2020.3041247),
    [Utility Products](https://www.utilityproducts.com/covid-19/article/14175992/workforce-supply-chain-disruptions-key-elements-in-ongoing-pandemic-preparations).

## Not yet known

- How many operators per shift CAMMESA's COC and Transener's and Transba's
  control centres run, and whether any of them sequestered staff in 2020.
- CEZ's staff, network control and repair crews.
- The under-frequency relief thresholds and shares.
- Any study (rather than an informal estimate) of how long an unattended
  grid stays up.
