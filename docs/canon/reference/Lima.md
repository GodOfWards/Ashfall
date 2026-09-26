# Lima, Partido de Zárate, Buenos Aires — the real town

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. The game's
town since 2026-09-26 (#237), replacing Henderson, Kentucky.

## The town and its region

- **Lima** is a town (`place=town` in OSM) in the **Partido de Zárate**,
  Buenos Aires province, centred on about **34.0447 S, 59.1961 W**.
  Population **10,219 (2010 census)**; the 2022 figure is not yet read.
  Secondary, 2026-09-26: OSM Nominatim; Wikidata Q6548772.
- **Nearby towns and cities** (Wikidata, INDEC 2022 census unless marked;
  distances straight-line between town centres):
  - **Zárate**, the partido's head town: 109,443. About 16 km from Lima.
  - **Campana**: 86,860 (2010). About 14 km beyond Zárate.
  - **Baradero**: 40,002. About 37 km from Lima, the other way.
  - **San Pedro**: 75,616. About 21 km beyond Baradero.
  - **Buenos Aires** is about 100 km away (Atucha's distance, below).
  - Secondary, 2026-09-26: Wikidata entities for each town.

## The street grid

Measured 2026-09-26 from OpenStreetMap (© OpenStreetMap contributors, ODbL)
through the OSM API (`api/0.6/map`, the box 34.070–34.025 S, 59.225–59.170 W).
**Secondary**: what would confirm it is the municipality's street plan.

- **A numbered grid.** The streets are "Calle 1" to "Calle 29", plus some
  "Bis" streets. Odd numbers run one way and even numbers the other, the
  usual Buenos Aires province scheme. There are also diagonals (Diagonal 2,
  Diagonal 4, Diagonal Morgan) and a numbered 100s grid in the northern
  neighbourhood. **Avenida 11** is the one avenue named in OSM in the
  centre. The **Acceso a Lima** comes in from the south.
- **Bearings:** the grid runs at about **14°** and **104°**, square to each
  other. The northern neighbourhood's grid is turned to about 128°.
- **Blocks are about 100–112 m:** median 112 m between consecutive
  even-numbered streets, and 97.5 m between consecutive odd-numbered ones,
  from 93 measured intersections.
- **The built-up town is about 1.5 × 1.5 km.**
- **How the game uses this (decided for Henderson, carried over):** the map
  is stored in the grid's own frame, rotated by the bearing, as
  `reference/Henderson.md` describes. Local metres are about 34.0447 S,
  59.1961 W, with x = Δlon × 111,320 × cos 34.0447° and y = Δlat × 110,574.
  **Derived.**

## Rail

- **The FC Mitre** (OSM `ref=GM-1B`, `usage=main`, broad gauge, 1,676 mm;
  operator tagged as Ferrocarriles Argentinos S.A.) runs through the middle of
  town, diagonally to the grid, with a yard and sidings.
- **Estación Lima** is in the town centre. Up and down the line are the halts
  **Atucha** (about 11 km north-west) and **Las Palmas** (about 5 km
  south-east).
- **Two level crossings inside the town** (OSM `railway=level_crossing`), and
  more along the line outside it. Whether they have lights, barriers or
  bells is unconfirmed (#288).
- Secondary, 2026-09-26: OSM, as above. Whether passenger trains ran to Lima
  in the era is unconfirmed.

## The Atucha nuclear complex

- On the right bank of the **Paraná de las Palmas**, in the locality of Lima,
  Partido de Zárate, about 100 km from the city of Buenos Aires. OSM places
  Atucha I's site about **8 km north** of Lima's centre (33.9695 S,
  59.2061 W).
- **Atucha I:** connected to the grid on 19 March 1974, and in commercial
  operation from 24 June 1974. It was the first nuclear power plant in Latin
  America. **362 MW** gross, on slightly enriched uranium (0.85%).
- **Atucha II:** first criticality on 3 June 2014, synchronised to the grid on
  27 June 2014. **745 MW** gross, on natural uranium and heavy water.
- Secondary, 2026-09-26:
  [es.wikipedia](https://es.wikipedia.org/wiki/Complejo_Nuclear_Atucha);
  the operator's pages ([Atucha I](https://www.na-sa.com.ar/es/centrales-nucleares/atucha-1),
  [Atucha II](https://www.na-sa.com.ar/es/centrales-nucleares/atucha-2)) were
  listed but not read.

## Electricity in Argentina (to be researched properly)

All **secondary, 2026-09-26**, read through search summaries. Confirming
them, and the figures the power system needs, is #286. Fuel and cooking
gas are #287; the town block by block is #288.

- **220/380 V at 50 Hz** in common use. The normalised values are
  230/400 V ±5% under AEA/IRAM.
  [Wikipedia](https://en.wikipedia.org/wiki/Mains_electricity_by_country),
  [EleCalculador](https://ar.elecalculador.com/guias/normativa-aea/aea-90364-guia-completa).
- **AEA 90364** (Asociación Electrotécnica Argentina) is the regulation for
  electrical installations in buildings, based on IEC.
- **A 30 mA residual-current device** (*interruptor diferencial*,
  *disyuntor*) protects outlet circuits.
- **Plugs and sockets: IRAM 2073,** two-pole with earth, 10 A and 20 A,
  250 V.
