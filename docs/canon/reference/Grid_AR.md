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
  Its failing to act is what made 2019 total (below).

## When it failed: 16 June 2019

The whole grid's one total collapse. **Primary for the sequence:** the
technical study the ENRE commissioned from the Facultad de Ingeniería of the
Universidad de Buenos Aires (FIUBA), *Estudio del evento ocurrido el 16 de
junio de 2019* (version 2, rev. 26; 236 pages), read in full text
2026-09-29:
[ENRE / FIUBA](http://www.enre.gov.ar/web/bibliotd.nsf/203df3042bad9c40032578f6004ed613/d50f985c66ad65cd032586d9004ccbd1/$FILE/INFORME_FIUBA-version2%20rev26.pdf).
Times are UTC−3. (Corrects this file's earlier line, from Wikipedia, that
the fault was on the Colonia Elía–Campana line: that line was out of
service; the fault was on its neighbour.)

**Before (a weakened configuration, for two months)**
- **18 April 2019:** the 500 kV **Colonia Elía–Campana** line was taken out
  to replace **tower 412**, one of the towers at the Paraná Guazú crossing,
  whose base the river had eroded "with the risk of its collapse". The new
  tower went up about 100 m back from the bank; the work needed at least 70
  days, and **the line returned on 2 July 2019**.
- **The same day, Transener connected the ET Campana into the Colonia
  Elía–Manuel Belgrano line in a "T" (the bypass)**, adjusting the
  protections and the automatic generation disconnection (DAG NEA);
  CAMMESA accepted it. The grid ran for over 70 days one line short on its
  main corridor from the north-east (Yacyretá, Salto Grande, Brazil) to
  Buenos Aires.
- In that period the DAG's selected shedding **exceeded 1,200 MW 45 % of the
  time**, at moments nearly 3,000 MW: the corridor was run hard.
- **The night before:** a storm alert from 01:30 for northern Buenos Aires
  province, Entre Ríos and Santa Fe (50–100 mm of rain), lifted only in
  part at 03:30.

**07:00, Sunday (Father's Day):** SADI demand **13,200 MW**; thermal 54.2 %,
hydro 29.4 %, nuclear 5.9 %, renewables 4.1 %, imports 6.4 %. About
**2,600 MW** was arriving from the north-east at Rincón (970 MW of it from
Brazil), and **1,662 MW** flowing from Colonia Elía towards Manuel
Belgrano and Campana.

**The collapse (about 30 seconds)**
- **07:06:22.177:** a **single-phase fault on the 500 kV Colonia
  Elía–Mercedes line**, about 21 km from Colonia Elía. Its protections open
  the faulted phase and start to reclose, correctly.
- **The same instant:** the T line's protections at **Campana** and Manuel
  Belgrano also see the fault (set to overreach, to cover the T) and open
  the same phase to reclose.
- **About 150 ms later, at Campana:** an overvoltage blocks the reclose and
  **Campana opens for good**, on all three phases, **without sending a trip
  signal to the T's other two ends**. The DAG registers it as an event
  assigned **0 MW**, and that event **locks the DAG for 20 seconds**.
- **About 0.9 s:** Colonia Elía–Mercedes recloses successfully (the fault
  was transient). But at **Colonia Elía** the T line trips on ground
  overcurrent and trips Manuel Belgrano: **the T is now fully open.** This
  is the event that should have shed **1,200 MW at Yacyretá** — and the
  DAG is locked. **Nothing is shed.**
- **About 1.1 s after the T opened:** the 500 kV Rincón–Paso de la Patria
  line trips. **Yacyretá and Salto Grande lose synchronism**, and the
  north-east separates: an **island** of Misiones, parts of Corrientes and
  Entre Ríos, and Uruguay, with too much generation (it too collapses later).
- **The rest of the SADI loses about 3,200 MW** against 12,800 MW of
  demand. Frequency falls. Several generators trip **earlier than the rules
  allow**; the automatic under-frequency load relief falls short — large
  users shed about **1,300 MW of the 4,840 MW committed**, 98 % of them
  shedding nothing, and distributors about 80 % of what was needed
  (Infobae). Generators' under-frequency protections (below 49 Hz for 20 s)
  time out one after another: **the final collapse**, by frequency
  instability.
- **Counterfactuals the study simulated:** had the T's protections acted
  as intended, the system would have stayed stable; with the actual
  protections but a working DAG, it would have stabilised, with some
  overloads.

**Afterwards (about 14 hours)**
- **07:09:** Transener's control centre (COT) receives CAMMESA's (COC)
  confirmation of the **total collapse of the SADI**. Plants able to start
  without outside power (*arranque en negro*) are instructed. One regional
  transmission company (Transcomahue) got the confirmation only at 07:25:
  **communications failed for lack of power**, and the control centres
  disagreed during the restart.
- **Atucha II stayed in service feeding its own auxiliaries, and Atucha
  I's** (Atucha I was shut down); the restart **gave Atucha II priority**.
- **08:07:** all 500 kV stations ready to start restoring. **08:23:**
  Yacyretá starts two machines; three times they trip while taking load
  (too little load connected). **08:50:** Ensenada Barragán starts in an
  island. **09:44:** a 500 kV busbar at Rodríguez is energised from Salto
  Grande, and Edenor takes load at 09:48–09:49. **10:33:** Ezeiza–Rodríguez
  energised from Rodríguez, because El Chocón couldn't.
- **14:15:** the Litoral fully restored; **15:00:** Greater Buenos Aires at
  92 %, held back by the Litoral–GBA corridor's limit; **16:22:** the NEA
  fully restored; the whole system **a little over 14 hours** after the
  fault (CAMMESA, via Infobae), around 20:30.
- **Many plants struggled to start on their own:** Yacyretá's units
  couldn't hold on the 500 kV lines; Genneia failed its first start; San
  Miguel de Tucumán restarted about six hours later; Río Grande took about
  three and a half hours; El Chocón had breaker and protection trouble;
  Guillermo Brown started only once it got 500 kV from outside; **Alto
  Valle didn't start, its batteries too low**; Pilar tripped and cut
  Embalse nuclear plant's auxiliary supply.
- **Responsibility** (the study's 0–10 scale): Transener 10 for the first
  stage; in the slide to collapse, large users 7, distributors 6,
  generators 5; CAMMESA 5 for the dispatch it adopted. ENRE sanctioned
  Transener in 2021 for "negligent action" ($31,367,069.25).
- Secondary for the news detail, 2026-09-29:
  [Infobae, 2023-03-01](https://www.infobae.com/economia/2023/03/01/como-fue-el-apagon-del-siglo-del-dia-del-padre-de-2019-que-dejo-sin-electricidad-a-50-millones-de-personas/),
  [es.wikipedia](https://es.wikipedia.org/wiki/Apag%C3%B3n_de_Argentina,_Paraguay_y_Uruguay_de_2019).
- **Lima's region was at the centre of it:** the T was the ET Campana's
  connection, about 14 km beyond Zárate (`Lima.md`). Only two towns with
  their own generation (Ticino, Los Toldos) stayed lit in Argentina, and
  Tierra del Fuego, which isn't on the SADI.

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

## Keeping crews uninfected, and what a shrunken grid runs on (2026-09-29)

For the question Tom asked: how most of the grid could hold on, given that
the airborne strain can be protected against.

- **Nuclear control rooms are built to keep airborne contamination out.**
  "Habitability systems" isolate the control room, **pressurize it** (at
  least 0.125 inches of water above its surroundings, so unfiltered air
  can't leak in) and pass outside air through **redundant HEPA and charcoal
  filter trains**, with the sustenance and sanitation for operators to stay
  inside through an accident. Designed for radioactive particles and
  iodine, not microbes; HEPA filters also stop particles of virus size, but
  no source read tests them against a virus. Secondary (US NRC plant
  safety reports), 2026-09-29:
  [NRC, Susquehanna FSAR 6.4](https://www.nrc.gov/docs/ML2329/ML23291A398.pdf),
  [NRC, Engineered Safety Features 6.4](https://www.nrc.gov/docs/ML0916/ML091671494.pdf),
  [NRC Regulatory Guide 1.197](https://www.nrc.gov/docs/ML0314/ML031490664.pdf)
  (search summaries). **Whether Atucha's control rooms have the same is
  unconfirmed** (`Atucha.md` doesn't say).
- **Respirators help, if fitted.** Reviews find N95/FFP2 respirators prevent
  more respiratory infections among health workers than surgical masks
  (about 73 fewer clinical infections per 1,000 workers, low-quality
  evidence), and that **fit-testing decides whether they work at all**;
  there's no high-quality evidence specific to SARS-CoV-2. Secondary,
  2026-09-29:
  [PMC7269249 (GRADE rapid review)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7269249/),
  [PMC4868605 (meta-analysis)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4868605/),
  [J Infect Dis (fit-tested N95 + HEPA)](https://academic.oup.com/jid/article/226/2/199/6582941).
- **Sequestration worked in 2020, with supplies coming in.** NYISO's team of
  37 (31 operators, 2 managers, 2 facilities staff, 2 café workers) was
  **tested before going in** and sequestered from **23 March 2020**, about
  three weeks after New York's first case, for what was expected to be
  weeks to months; by early May it was winding down, with no infections
  reported. Food and supplies came from outside. Secondary, 2026-09-29:
  [POWER](https://www.powermag.com/nyiso-workers-now-living-at-grid-control-centers/),
  [Daily Energy Insider](https://dailyenergyinsider.com/infrastructure/24894-in-isolation-nyiso-volunteers-work-to-keep-power-running-for-nearly-20-million-new-yorkers/),
  [S&P Global](https://www.spglobal.com/marketintelligence/en/news-insights/latest-news-headlines/falling-covid-19-cases-may-signal-beginning-of-the-end-for-nyiso-sequestration-58409473)
  (search summaries; the last refused a direct read).
- **Atucha had COVID-19 cases.** The ARN reported positive cases at the
  Atucha complex and at Embalse in December 2020; the page refused a direct
  read, so the numbers and measures are unconfirmed. Secondary:
  [ARN](https://www.argentina.gob.ar/arn/sucesos-notificados/informacion-sobre-casos-positivos-de-covid-19-en-las-centrales-nucleares-23122020).
- **What the grid could shrink to without gas.** Hydro and nuclear need no
  fuel chain. In 2019 the SADI had **10,812 MW of hydro and 1,755 MW of
  nuclear** installed (above), against a February 2025 peak of 30,240 MW.
  Hydro depends on river flow: in **April 2020 hydro generation fell 38.8 %**
  year on year, mostly from low flows at Yacyretá and Salto Grande.
  Secondary, 2026-09-29:
  [Extra long Argentinian lockdown (PMC9007721)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9007721/).
- **Atucha II refuels on line, about one fuel element a day at full
  power**, so its core is kept going by a working crew. What happens to its
  output if refuelling stops is unconfirmed. Secondary, 2026-09-29:
  [Petrotecnia, "Atucha II"](https://www.petrotecnia.com.ar/petro_08/AtuchaII_SP.pdf)
  (search summary).
- **The gas pipelines' own reserve (line pack)** in hours: not found. TGS
  runs about 9,248 km of pipeline, TGN about 40 % of the gas injected into
  the trunk lines. Secondary:
  [TGS](https://en.wikipedia.org/wiki/Transportadora_de_Gas_del_Sur),
  [TGN](https://www.tgn.com.ar/en/operations-and-services/tgn-system/).

## Anchors for the estimates below (2026-09-29)

- **Buenos Aires province's electricity cooperatives:** FEDECOBA's
  member cooperatives serve about **500,000 electricity users** with **more
  than 2,100 employees**, about **240 users per employee**. (All the
  province's cooperatives together: about 1,057,711 users, some 200
  cooperatives.) Secondary, 2026-09-29:
  [FEDECOBA via ESSApp](https://www.essapp.coop/cooperativas/fedecoba-federacion-de-cooperativas-de-electricidad-y-servicios-publicos-de-la),
  [Provincia de Buenos Aires](https://gba.gob.ar/comunicacion_publica/gacetillas/las_200_cooperativas_el%C3%A9ctricas_de_la_provincia_recibir%C3%A1n_un)
  (search summaries).
- **Edenor, for scale:** 4,682 direct employees plus about 6,000
  contractors (2023). Secondary:
  [Edenor, company profile](https://www.edenor.com/inversores/es/compania/perfil-de-la-compania)
  (search summary).
- **The 2020 lockdown cut demand.** National consumption in April 2020 fell
  **11.5 %** year on year, the steepest fall in 20 years; the last week of
  April averaged **12,166 MW** against 14,377 MW a year before (−15.4 %).
  **Large industrial users drew about 60 % less** in the first stage of the
  lockdown; commercial and industrial demand together fell 21 % in April.
  Secondary, 2026-09-29:
  [Infobae, 2020-05-21](https://www.infobae.com/economia/2020/05/21/coronavirus-en-la-argentina-en-abril-la-demanda-electrica-en-las-industrias-fue-la-mas-baja-de-los-ultimos-20-anos/),
  [La Arena, 2020-05-25](https://www.laarena.com.ar/la-pampa/2020-5-25-0-47-32-la-peor-caida-del-consumo-electrico-de-la-historia),
  [IDB blog](https://blogs.iadb.org/energia/es/demanda-y-precio-de-la-energia-electrica-en-argentina-impacto-de-la-pandemia-y-tendencias/).

## Estimates — not facts (#346, Tom asked, 2026-09-29)

**Status: unconfirmed.** Reasoned from the facts in this file, for design
use until something better is found. Replace them the moment a source
turns up.

- **CEZ's staff: about 150–200 people.** At the cooperatives' average of
  about 240 users per employee, CEZ's roughly 39,000–41,000 users give
  about 165; its large industrial load and extra services (fibre, TV)
  suggest the upper end.
  - **Who keeps the network running at night: a handful.** Most likely one
    or two people at a network desk in Zárate and two or three on-call
    crews of two for Zárate and Lima together, perhaps one based at the
    Lima office. The pattern of passive on-call rotas is Transener's
    (above); CEZ's own is unknown.
  - **The local network is passive.** Its feeders and 829 transformer
    substations need no one while nothing breaks; fuses and reclosers cut
    a fault off on their own. **Without crews, each fault leaves its part of
    the network dark for good**: a transformer failing in the heat, a
    branch on a line. So Lima would lose power **street by street, at
    random**, for as long as the supply above it holds.
- **How long the national grid lasts: probably days, not weeks.**
  - **With no one at all:** hours to about a day (the informal estimate
    above; nothing better found).
  - **As staff are lost:** the airborne strain kills over about a week, so
    control rooms, plants and crews thin out with everyone else rather than
    all at once. Lockdown sequestration (2020 practice) doesn't save them:
    the strain is silent for 5–10 days, so teams would be sequestered
    already infected. The resistant would remain, a few in each room.
  - **What holds it up meanwhile:** demand falls, as in 2020 (industry
    first, 60 % less in the first lockdown stage), which eases the load.
    Automatic protections ride out single faults by shedding load, but
    **nobody restores what is shed**, so the grid shrinks with each fault.
  - **What brings it down:** the daily swing between the afternoon peak
    and the night with no one re-dispatching; thermal plants tripping as
    their crews die, with no one to restart or switch them to stored fuel;
    and the pipelines' pressure falling after 1–3 days without their
    control rooms.
  - **Estimate:** most of the grid fails **within a few days to about ten
    days of the wave breaking**, in pieces rather than one event. Islands
    around hydro plants or a determined resistant crew could last longer,
    perhaps two weeks. **Three weeks (the game's `POWER_FAILS_DAY = 21`) is
    at the far end** and needs a reason: a crew that held on.
- **If crews sealed themselves in before they were exposed** (Tom: the
  airborne strain can be protected against):
  - **Who has to hold:** CAMMESA's and Transener's control rooms at Pérez
    (the backup centre takes 15 operators), the main plants' shift crews,
    and — for the thermal half of the grid — the gas chain's control rooms.
    Substations and pipeline compressors run unattended.
  - **When they would have to seal:** before the airborne strain reached
    them, so **during the news from abroad**, not at the lockdown. In 2020
    it took NYISO about three weeks from New York's first case; with the
    2020 playbook in hand, a quicker start is plausible.
  - **What they can't seal:** field crews. Every fault out on the lines is
    permanent, so the grid **shrinks by pieces** even while its centre holds.
  - **What it runs on if the gas chain fails:** hydro and nuclear, about
    12.5 GW installed in 2019, which could plausibly carry a demand that has
    collapsed (industry shut, most households gone), river flows
    permitting.
  - **What ends it:** the sealed crews' food and water, with nothing coming
    in (2020's sequestrations were supplied from outside); faults piling up;
    a breach by the dead; the operators' own endurance.
  - **Estimate:** a shrinking national grid held by sealed crews could last
    **weeks, perhaps two to six**, while individual towns and streets drop
    out of it one fault at a time. On this reading **three weeks is
    plausible for the grid as a whole**, but not for every street in Lima.

## Not yet known

- How many operators per shift CAMMESA's COC and Transener's and Transba's
  control centres run, and whether any of them sequestered staff in 2020.
- CEZ's staff, network control and repair crews.
- The under-frequency relief thresholds and shares.
- Any study (rather than an informal estimate) of how long an unattended
  grid stays up.
