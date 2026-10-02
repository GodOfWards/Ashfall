# Mains gas — how it reaches Lima, and what keeps it flowing

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Gathered for
the lore session (#329) on whether Lima's mains gas outlasts the grid
(#342), at Tom's request (2026-09-30). Lima's distributor and the Barrio
Atucha's connection are in `Lima.md`, "Utilities in Lima and the region";
garrafas are in `Fuel_AR.md`; the grid is in `Grid_AR.md`.
Line pack, the fields' power and TGN's control room were added for #348
(2026-10-01). The line that feeds Lima and Atucha, the city gates' pressures
and the house regulators' low-pressure cut-off were added for #404
(2026-10-02). Lima's two city gates, what the network codes mean, NAG-100 on
low-pressure trips and Lima's low-pressure streets were added for #407
(2026-10-02).

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
- **TGN's trunk lines are 24" and 30" pipes that carried gas at "a variable
  pressure of between 20 and 70 kg/cm²"**, with 16 compressor plants, as of
  1999. **Primary** (the privatisation record):
  [Memoria de las Privatizaciones, TGN, "Producción"](https://mepriv.mecon.gob.ar/gas/memybces/transpgasdelnorte/produccion.htm),
  read 2026-10-02. Dated. The MAPOs at Lima's tap are in "The line to Lima
  and Atucha".
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
- **What feeds Zárate, Lima and Atucha** is in "The line to Lima and
  Atucha" below.
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

## The line to Lima and Atucha (#404)

**Source: one dataset**, ENARGAS's pipeline layers, published by the
Secretaría de Energía:
[Gasoductos (ENARGAS)](http://datos.energia.gob.ar/dataset/transporte-hidrocarburos-ductos-troncales-gasoductos).
- **Distribution layer:**
  [CSV](http://datos.energia.gob.ar/dataset/8758101a-1e0d-413f-8cc5-83e21ece6391/resource/3f7f87ab-bdcf-4a21-b361-f59732754330/download/gasoductos-de-distribucin.csv),
  last modified 2026-09-02. It holds trunk mains only, not street pipes.
- **Transmission layer:**
  [SHP](http://datos.energia.gob.ar/dataset/8758101a-1e0d-413f-8cc5-83e21ece6391/resource/5af07e15-f356-40b9-a369-63dbf38a938a/download/gasoductos-de-transporte-enargas-.zip),
  last modified 2023-12.

Read 2026-10-01. **What the data states is Confirmed:** each segment's
pipeline name, operator, type and geometry.

**The route is reconstructed** by joining segments whose ends meet within
about 30 m, and the lengths are measured along them. **No document states
that this line feeds Lima, and none names a city gate at the tap**;
OpenStreetMap maps an unnamed station there ("Lima's two city gates",
below). Town
positions are `Lima.md`'s (Lima's centre, Atucha I's site).

- **Lima is not on a transmission line.** TGN's Gasoducto Norte trunk (N1T,
  segment "San Nicolás – Los Cardales") and its parallel (N3P, "Ramallo –
  Los Cardales") pass about **13 km south-west** of Lima. At their nearest
  point, about 34.13 S, 59.30 W, they are in the Partido de San Antonio de
  Areco (OSM reverse geocoding, secondary).
  - Both run on to Los Cardales. There they meet the Mercedes–Cardales
    line (TGS/TGN) and the Escobar–Cardales LNG line.
- **Lima and Atucha hang off one Naturgy BAN main, named "25.06 T" in the
  data.**
  - **It leaves TGN's lines** at about **34.205 S, 59.172 W**, 0.2–0.4 km
    from them, in the **Partido de Exaltación de la Cruz** (OSM reverse
    geocoding, secondary). That is about 19 km south of Lima as the crow
    flies.
  - **It runs north for about 27–28 km of pipe to Lima**, passing **0.5 km**
    from the town's centre.
  - **It goes on about 9 km to the Atucha complex** and ends at 33.971 S,
    59.206 W, **0.1 km** from Atucha I's site.
  - **So the town sits on the branch the plant needed**, as Perfil said in
    2013 (`Lima.md`, "Utilities").
  - **Segment IDs** (`nombretram`), to check the route against the file:
    - 79933063, from south-east of Zárate towards Lima;
    - 120703, through Lima;
    - 77982819, 77979592, 56860036, 58243583 and 58243376, from Lima
      north;
    - 56860359, the end of the line at Atucha.
- **Zárate city is on the same network**, by a branch from south-east of the
  city (34.151 S, 59.022 W) towards Lima. The network meets TGN's lines a
  second time, at about 34.276 S, 59.088 W, near Marín, towards Campana.
  **There is a second city gate there** (see "Lima's two city gates" below).
- **TGN's lines at the tap.** **Primary**: ENARGAS's GIS server, layer
  [Gasoductos de Transporte](https://sig.enargas.gov.ar/arcgis/rest/services/Enargas_ext/Gsoductos_de_Transporte/MapServer/0),
  queried 2026-10-02.
  - **The trunk (N1T)**, from about 34.151 S, 59.270 W to Los Cardales
    (32.47 km): **22" X52 pipe**, design pressure 59.8, **MAPO 40.0**.
  - **The parallel (N3P):** **30" X52**, design pressure 60.35, **MAPO
    59.8**.
  - Which of the two the tap draws from isn't stated.
  - The layer gives no units. **kg/cm² is most likely**, TGN's own unit;
    unconfirmed.
- **Lima has natural gas service with 2,150 users; Zárate city has 25,146.**
  **Primary**: ENARGAS's GIS server, layer
  [Localidades Abastecidas](https://sig.enargas.gov.ar/arcgis/rest/services/Enargas_ext/Localidades_Abastecidas/MapServer/0),
  queried 2026-10-02, undated. Lima's users by residential category:
  - R1: 561;
  - R2 (sub-categories 1–3): 713;
  - R3 (sub-categories 1–4): 876.
- **What the name "25.06" means: the first number is very likely the
  pressure class in bar, the second a network number.** Only Naturgy BAN's
  mains carry such names, across 12,231 segments, as *first.second*
  followed by T or D. No document found spells the code out; ENARGAS's data
  dictionary calls the field only the pipeline's *denominación*. The reading
  is inferred from the data and supported by the sources below (#407).
  - **The first number takes only four values: 10 (3,731 segments), 25
    (8,326), 45 (94) and 60 (80).** It is the same along a whole network,
    from the tap to Atucha's end.
  - **Naturgy BAN's own steel mains come in pressure classes of 10, 25 and
    45 bar.** Its replacement-cost price list for pipelines and ramales, by
    diameter (3" to 16") and pressure, has rows for those three classes
    only. **Primary** (an audit commissioned by ENARGAS, quoting the
    distributor's figures): FIUBA,
    [Informe de avance N.º 5, Naturgy BAN, 2020-08-31](https://www.enargas.gob.ar/secciones/banco-de-datos/recursos/informes/INFORME-DE-AVANCE-N5-naturgy-ban-sa.pdf),
    PDF page 14, read 2026-10-02. The 60 class isn't in that list. It may be
    ramales built to the transporters' rating; unconfirmed.
  - **Its regulator stations step down between those classes.** ENARGAS's
    list of large works authorised in 2022 gives Naturgy BAN's as **"ERP
    25/7 bar"** (a new branch to Pan American Energy's refinery, Campana) and
    **"ERP 45/25 bar"** (Escobar's gated estates). Other distributors' ERPs
    are written the same way, inlet/outlet in bar (60/25, 70/25, 25/1.5,
    25/4, 10/1.5). **Primary**:
    [ENARGAS, Informe Anual 2022](https://www.enargas.gov.ar/secciones/publicaciones/informes-anuales-de-balance-y-gestion/pdf/anuales/2022/informe-anual-2022.pdf),
    PDF page 45, read 2026-10-02.
  - **The gate at Marín fits it:** one station on TGN's line that starts a
    45, a 25 and a 10 network ("Lima's two city gates", below).
  - **The second number runs from 01 to 24 and counts networks within a
    class, not across them.** Each pair covers one compact area: "25.06" is
    the Zárate–Lima–Atucha network and nothing else, while 10.06 is near
    Ezeiza. 10.16 (inside Zárate city) and 10.17 (around Campana) lie
    inside 25.06's area, most likely fed from it by 25/10 stations
    (unconfirmed).
  - **T marks the spine and D its stubs and branches** (perhaps *troncal* and
    *derivación*; a guess).
  - **It isn't a volume or a flow.** A flow falls along a branch as each town
    takes its share, but the name stays the same from the tap to the end of
    the line.
  - **A coincidence, ruled out:** ENARGAS's daily report for 22–23 June 2017
    shows 25.06 MMm³/d entering the Gasoducto Norte from the Norte basin.
    That is one day's figure: on 3, 14 and 24 February 2025 it was 4.6,
    2.57 and 4.48.

### Lima's two city gates (#407)

- **The 25.06 network takes gas from TGN at two stations, both mapped on
  OpenStreetMap as fenced gas facilities beside TGN's lines.** A volunteer
  traced both from Maxar imagery and the Ministry of Energy's pipeline WMS
  in December 2021 (changeset comment "completo gasoducto"). Neither carries
  a name or an operator. **Secondary** (OSM, read 2026-10-02). Which
  networks meet each one was found by matching the stations against
  ENARGAS's two layers (above):

  | OSM way | Where | Fenced area | What meets there |
  |---|---|---|---|
  | [1011928589](https://www.openstreetmap.org/way/1011928589) | 34.2058 S, 59.1740 W, Partido de Exaltación de la Cruz | about 3,500 m² | TGN's N1T and N3P about 100 m away; **25.06 T** and three 25.06 D stubs end 110–140 m from it. The tap above. |
  | [1011928586](https://www.openstreetmap.org/way/1011928586) | 34.2763 S, 59.0879 W, Marín, near Capilla del Señor (Exaltación de la Cruz) | about 1,300 m² | On TGN's N1T (about 20 m). **Three Naturgy BAN networks start there: 25.06 T, 45.10 D and 10.24 D.** |

  - **So Lima's network can draw on TGN at two points about 11 km apart.**
  - The town names are OSM reverse geocoding (secondary).
  - OSM also maps the **60.10** network's station at Puente Castex (San
    Antonio de Areco),
    [way 1060215630](https://www.openstreetmap.org/way/1060215630), about
    740 m², on N1T and N3P. Not Lima's.
- **The gates' names, set pressures and capacities, and whether they trip
  on low pressure, are not public.** These sources don't give them:
  - ENARGAS's datasets, and every public folder of its GIS server
    (`Enargas_ext`, `Demanda`, `Hosted`, `Pruebas`, `ADUP`, `Geobase`,
    `Zona_Fria`), which have no layer of delivery points or regulator
    stations. Two folders, `SE` and `Protocolo_SD`, need a login.
  - ENARGAS's annual reports for 2020–2024: no works at Lima, Zárate or
    Exaltación de la Cruz.
  - TGN's hearing reports (2017, 2024) and its 2019 open-season notice,
    which list contracts by delivery zone ("GBA"), not by point.
  - Naturgy BAN's press releases, its tariff filings and hearing
    presentations (AP 102–104), and the privatisation record of 1994–95.
  - The Boletín Oficial.

  ENARGAS's figures for gas delivered stop at the distributor and subzone
  ("Buenos Aires Norte" for the whole of Naturgy BAN). Only Naturgy BAN or
  ENARGAS, asked directly, could give the settings. **A request under Ley
  27.275** (access to public information) must be answered in 15 working
  days, extendable once by 15; silence counts as an unjustified refusal,
  which may be taken to the Agencia de Acceso a la Información Pública or a
  federal court within 40 working days. ENARGAS may refuse because it
  doesn't hold the data. **Primary**:
  [Ley 27.275](https://www.argentina.gob.ar/normativa/nacional/ley-27275-265949/texto),
  arts. 11, 13–15, read 2026-10-02.

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
- **But a regulator built with a low-pressure cut-off shuts the gas off when
  its inlet can't hold the outlet, and stays shut until reset by hand.**
  Argentina's house regulators work this way; city gates may. Without power,
  nothing resets them.

## Distribution pressures and house regulators (#404)

- **Distribution pressure classes** (NAG-100 §3, definitions 25–27):
  - **high:** above 4 bar;
  - **medium:** 0.5 to 4 bar;
  - **low:** 18 to 28 mbar in the main.

  **Primary**:
  [ENARGAS, NAG-100](https://www.enargas.gob.ar/secciones/normativa/pdf/normas-tecnicas/NAG-100.pdf),
  read 2026-10-02.
- **House regulators on medium-pressure networks** take **0.5 to 4 bar in**
  and give **19 mbar out**. **Primary**:
  [NAG-235 (1995)](https://www.enargas.gob.ar/secciones/normativa/pdf/normas-tecnicas/NAG-235_1995.pdf),
  §2.2–2.3, read 2026-10-02.
  - **For a low inlet pressure, the 1995 standard (§5.5.2) allows either:**
    - (a) **a cut-off valve with manual reset** that shuts the gas off when
      the outlet pressure reaches **13 mbar (±10 %)**; or
    - (b) normal regulation with the inlet down to **0.150 bar**.
  - **The 2019 draft makes the cut-off mandatory**, with **manual reset**,
    before the outlet falls below **8 mbar**. **Primary**:
    [NAG-235 (2019, in public consultation)](https://www.enargas.gob.ar/secciones/normativa/pdf/normas-discusion/NAG-235.pdf),
    §5.5.2.
- **A low-pressure service has no house regulator.** "If the service is low
  pressure, the regulator need not be fitted" (Figure 2.7, note 2). The
  regulator belongs to the customer's installation, "installed at the
  customer's expense by a registered fitter" (§2.2.2 n). **Primary**:
  [NAG-200 (2025)](https://www.enargas.gov.ar/secciones/normativa/pdf/normas-discusion/IF-2025-103868516-APN-GIYN-ENARGAS.pdf),
  read 2026-10-02.
  - **So a regulator in the meter niche marks a medium-pressure street**: a
    round domed body with a vent, beside the meter.
  - **Lima's meter niches have no regulator** (Tom, Street View,
    2026-10-02). **So Lima's streets are most likely low-pressure**, 18 to
    28 mbar in the main, with no house regulator and so no house cut-off to
    reset by hand.
    - A regulator could still sit out of sight, in a closed niche or a
      separate one; the observation is of the niches as seen.
    - The Barrio Atucha's "low box fed by a yellow pipe" (`Lima.md`) was
      read in #404 as possibly a regulator. Whether it holds one is
      unconfirmed.
  - **Naturgy BAN runs both kinds of network.** Its renewal of Ciudad
    Evita's network replaces cast iron run at **low pressure (22 mbar)**,
    built by Gas del Estado over 50 years ago, with polyethylene at
    **medium pressure (1.5 bar)**. **Primary**: FIUBA audit (above, "The
    line to Lima and Atucha"), PDF pages 35–36, read 2026-10-02. So
    low-pressure streets in its area are older Gas del Estado networks; that
    new ones are all medium pressure is inferred from this one project.
    When Lima's street network was built was not found.
  - **A low-pressure town still needs a district regulator** between the
    25-bar main and the streets. Where Lima's is, and whether it has a
    low-pressure trip, is unconfirmed.
- **It has happened.**
  - **Mar del Plata, 3 July 2025** (Camuzzi, in a cold wave):
    - supply "upstream" fell short;
    - **each home's regulator cut off when the network fell below 500 g/cm²
      (0.5 bar)**;
    - reconnecting takes a technician to check the pressure and reset each
      one by hand;
    - about 1.5 % of households were cut off. Camuzzi sent 150 technicians,
      and 2,700 homes were back by the next evening.

    Secondary (press), 2026-10-02:
    [EconoJournal](https://econojournal.com.ar/energia/corte-de-gas-a-hogares-que-fue-lo-que-paso-en-mar-del-plata/),
    [Infobae, 2025-07-03](https://www.infobae.com/sociedad/2025/07/03/mar-del-plata-se-reactiva-tras-la-crisis-por-el-corte-de-gas-sin-clases-y-hubo-comercios-cerrados-durante-la-noche/).
  - **Paraná, early July 2026** (Redengas):
    - gas "stopped entering the system";
    - the network recovered overnight, but **regulators were reactivated
      house by house**;
    - each has a reset button, and the distributor asked residents to wait
      for its crews.

    Secondary (press), 2026-10-02:
    [Elonce](https://www.elonce.com/parana/gas-en-parana-la-red-ya-fue-normalizada-pero-deben-reactivar-reguladores-en-los-domicilios.htm),
    [APF Digital, 2026-07-03](https://www.apfdigital.com.ar/noticias/2026/07/03/462004-corte-de-gas-en-parana-el-servicio-se-restablece-y-redengas-intensifica-el-operativo-de-reconectar-casa-por-casa).
- **City-gate slam-shut valves can trip on under-pressure as well as
  over-pressure, and need a manual reset.** Secondary (makers' literature),
  2026-10-02:
  [Fiorentini SBC 187](https://www.fiorentini.com/wp-content/uploads/2023/06/sbc187_technicalbrochure_ENG_revB.pdf),
  [Mooney Flowgrid Slam Shut](https://dam.bakerhughes.com/m/7b3fca4b23df85d1/original/Mooney-Flowgrid-Slam-Shut-1-Manual-English.pdf).
  - The transporters keep **automatic high/low pressure protection** at the
    Buenos Aires ring's delivery points (NAG-601 §5.4.4, below).
- **ENARGAS's code asks only for protection against over-pressure, and
  advises against shut-offs that need a manual reset where they would cut
  off many customers.** NAG-100's guidance lists an automatic shut-off
  valve as one way to protect a high-pressure distribution system, then
  says (translated): "since this device stays closed until reset by hand,
  it should not be used where it could interrupt service to a considerable
  number of customers". Nothing in it asks for an under-pressure trip.
  **Primary**:
  [ENARGAS, NAG-100](https://www.enargas.gob.ar/secciones/normativa/pdf/normas-tecnicas/NAG-100.pdf),
  Section 195, guidance 2.2 e), PDF page 91, read 2026-10-02.
  - **This leans towards Lima's gates having no low-pressure trip.** It is
    still **unconfirmed** for them: a slam-shut can be fitted by choice, and
    the transporters do keep low-pressure protection on the ring (above).

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
- **The Buenos Aires ring's delivery points have a contract pressure of
  20 kg/cm² and a minimum of 17 kg/cm² in winter**, "to assure service
  quality". The ring's points are Gutiérrez, Ezeiza, Pacheco, Buchanan I,
  Rodríguez and Marcos Paz. For 18 hours a day the pressure is at the normal
  figure or above; for the other 6 it may dip, but never below the minimum.
  The transporters keep **automatic high/low pressure protection** there,
  recalibrated when a distributor can't run at the minimum. **Primary**:
  NAG-601 (above), §5.2 and §5.4.4, read 2026-10-02.
  - This is a contractual and service-quality floor, not a physical one.
  - No such figure was found for a delivery point off the ring, such as
    Lima's.
- **The city gates' measured minimum pressures** for each 06:00–06:00 day,
  upstream (Pe) and downstream (Ps) of the regulators, in **bar**. **Primary**:
  ENARGAS, *Parte Diario Operativo*, provisional data from the transporters,
  read 2026-10-02:
  [22 Jun 2017](https://www.enargas.gov.ar/secciones/transporte-y-distribucion/descarga.php?tipo=transporte&path=partes-diarios/transporte&file=20170623.pdf)
  (found by Tom),
  [3 Feb 2025](https://www.enargas.gov.ar/secciones/transporte-y-distribucion/descarga.php?tipo=transporte&path=partes-diarios/transporte&file=20250203.pdf),
  [14 Feb 2025](https://www.enargas.gov.ar/secciones/transporte-y-distribucion/descarga.php?tipo=transporte&path=partes-diarios/transporte&file=20250214.pdf),
  [24 Feb 2025](https://www.enargas.gov.ar/secciones/transporte-y-distribucion/descarga.php?tipo=transporte&path=partes-diarios/transporte&file=20250224.pdf).

  | City gate | 22 Jun 2017 (winter) Pe / Ps | 3 Feb 2025 Pe / Ps | 14 Feb 2025 Pe / Ps | 24 Feb 2025 Pe / Ps |
  |---|---|---|---|---|
  | Pacheco Sur | 26.30 / 18.80 | 30.5 / 20.8 | 30.80 / 19.90 | 26.10 / 20.80 |
  | Pacheco Norte | 27.90 / (a) | 26.0 / (a) | 31.20 / (a) | 25.20 / (a) |
  | Rodríguez Sur | 31.50 / 18.80 | 33.4 / 21.4 | 33.40 / 20.60 | 32.10 / 20.70 |
  | Rodríguez Norte | 31.60 / 18.40 | 29.1 / 0.0 | 33.20 / 0.00 | 28.00 / 0.00 |
  | Ezeiza | 28.30 / 21.00 | 33.6 / 20.6 | 34.50 / 19.90 | 33.00 / 20.60 |
  | Gutiérrez | 33.40 / 16.40 | 35.5 / 20.8 | 35.00 / 20.70 | 35.50 / 20.30 |
  | La Plata | 33.70 / – | 39.7 / – | 38.90 / – | 38.10 / – |

  (a) "Chamber with no transfer to the ring". Rodríguez Norte's Ps of 0.0
  in 2025 is as printed.
  - **In February 2025 the day's minimum upstream of a gate was 25 to
    40 bar.**
  - **Downstream, the gates hold about 19 to 21 bar**, close to the ring's
    contract figure of 20. The winter day of 2017 went down to 16.4.
  - **The same reports give the system's line pack as 334.9, 326.83 and
    337.43 MMm³** on the three February days, which agrees with the table
    above.
  - **The reports cover only the ring around Buenos Aires.** Lima's gate
    isn't in them.

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

## Estimates — not facts (2026-10-02)

**Status: unconfirmed.** Reasoned from the facts above, for design use.
Revises the estimate of 2026-10-01: Lima's line, the city gates' pressures
and the house regulators' cut-off are now known (#404). Revised again for
#407 (2026-10-02): Lima has two gates, its streets are most likely
low-pressure, and NAG-100 leans against low-pressure trips. The figure the
estimate turns on, whether a gate or Lima's district regulator trips on low
pressure, is still unknown; the evidence leans to no.

- **Once the grid fails, gas demand collapses.** Power generation stops
  burning it, industry is already shut, and most households are gone.
  What's left is a small summer load of cooking and water heating, well
  under the 14–17 MMm³/d of February's priority demand.
- **Above the operating floor the system holds about 15–30 MMm³**: a few
  hours of normal February demand, or **one to two days** of residential
  demand alone.
- **Lima's pressure chain, by analogy with the Buenos Aires ring's gates:**
  - TGN's lines, MAPO 40–60, normally 25–40 bar at a gate;
  - two city gates, at the tap and at Marín, each most likely holding a set
    pressure at or below the network's 25-bar class;
  - Naturgy BAN's 25.06 network;
  - a district regulator, down to low pressure, about 20 mbar;
  - the streets and houses, with no house regulator.
- **Once TGN's pressure falls below a gate's set point, the gate's
  regulator opens fully** and passes on whatever pressure the line has.
  Gas keeps flowing until the pressure is too low for the district
  regulator, a few bar or less. The exception is a station with an
  under-pressure slam-shut: that one shuts at its trip point, which is
  unknown.
- **So how much of the ~330 MMm³ Lima can draw depends on a trip.**
  - **With no trip, the likelier case**, the system can be drawn down to a
    few bar: roughly **two-thirds to nine-tenths** of it. Against a load of
    a few MMm³/d, that is **weeks to months**.
  - **With a trip near 17–20 bar**, only the top **quarter to half**, very
    roughly, against February's 25–40 bar at the gates. That is **days to
    weeks**.
  - With two gates, a trip at one still leaves the other, unless both have
    one.
  - Both cases are before leaks and broken pipes.
- **Injection need not stop with the grid.** Fields with their own power,
  such as Fortín de Piedra, and compressors that burn the gas they move,
  keep going while their crews last and nothing trips them. Grid-fed
  operations, such as Vista's electric compressor, stop with the grid.
  Exports to Chile draw on the same pipes while anyone takes them.
- **Lima's gas most likely outlasts the grid by weeks to months**; by days
  to weeks if a trip cuts it off.
- **It most likely fades rather than stops.** With low-pressure streets and
  no house regulators, nothing in the houses cuts off: as the pressure
  falls, **a cooker's flame shrinks before it goes out**, and the gas comes
  back by itself if pressure recovers.
  - **Only a trip upstream would make it stop at once**, at a gate or at
    the district regulator, cutting off the whole town until someone resets
    it by hand.
  - On a medium-pressure street it would be the other way: house regulators
    cut off below about 0.5 bar, as in Mar del Plata (2025) and Paraná
    (2026), and stay off until reset one by one.
- **This disagrees with `Grid_AR.md`'s "gas pipelines hold pressure 1–3
  days unattended"**, an anonymous North American estimate. That figure
  fits normal demand with no injection, not the collapse's small load. It
  comes closest to the case of a gate that trips early.
