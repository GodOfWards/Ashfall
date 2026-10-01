# Batteries — what a cell reads on a voltmeter, and what takes which

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Gathered
2026-10-01 for #389, so that #388's Test action (any `voltage-test` tool put
across a loose battery) can print a real reading for each charge level. Kept
general: every cell a household might hold, not only the flashlight's and
the radio's.

Two readings matter throughout. **At rest** (open circuit) is what a meter
reads across a cell lying loose, after it has recovered. **Under load** is the
voltage while a device draws from it; it is lower, and it is the figure a
device's cutoff is set by. A cell that stopped a device recovers at rest, so a
"dead" cell never reads near 0 V.

## Alkaline (the common 1.5 V cell)

- **Fresh: 1.5–1.6 V at rest, nominal 1.5 V, every cylindrical size (AAA,
  AA, C, D).** Duracell: "Open circuit voltage ranges from 1.5 to 1.6 volts.
  Nominal voltage is 1.5 volts … In most instances, 0.8 volts is considered
  to be the end-voltage." Energizer's worked example uses 1.6 V. Confirmed,
  2026-10-01:
  [Duracell Alkaline-Manganese Dioxide technical bulletin](https://www.microbattery.com/pub/media/tech-specs/duracell/duracell-alkaline-battery-017-2014.pdf)
  (the maker's bulletin, from a distributor's mirror);
  [Energizer Alkaline Handbook and Application Manual](https://data.energizer.com/pdfs/alkaline_appman.pdf)
  (2018).
- **A device gives up at 0.8–0.9 V per cell, under load.** Makers rate
  capacity to 0.8 V. Energizer sets 0.8 V as the minimum because of gassing,
  and says that by then "approximately 95% of the batteries usable capacity
  has been removed". Devices "are designed to operate within a voltage range
  (for example from 1.6 volts to 0.9 volts per cell)". The industry
  flashlight tests run to 0.9 V ("D – Flashlight – 2.2 ohms, 4
  minutes/hour to 0.9 volts"; "AA – Flashlight – 3.9 ohms, 4 minutes/hour to
  0.9 volts"). Confirmed, 2026-10-01: the handbook and bulletin above.
- **Sizes** (Energizer datasheets, all "continuous discharge to 0.8 volts";
  shelf life 10 years at 21 °C):

  | Size | IEC | Weight |
  |---|---|---|
  | AAA | LR03 | 11.5 g |
  | AA | LR6 | 23.0 g |
  | C | LR14 | 66 g |
  | D | LR20 | 139 g |

  Confirmed, 2026-10-01:
  [E92](https://data.energizer.com/pdfs/e92.pdf),
  [E91](https://data.energizer.com/pdfs/e91.pdf),
  [E93](https://data.energizer.com/pdfs/e93.pdf),
  [E95](https://data.energizer.com/pdfs/e95.pdf).

### Charge left against the reading (AA, measured)

| Charge left | 100 % | 90 % | 80 % | 70 % | 60 % | 50 % | 40 % | 30 % | 20 % | 10 % | 0 % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| At rest (V) | 1.59 | 1.44 | 1.38 | 1.34 | 1.32 | 1.30 | 1.28 | 1.26 | 1.23 | 1.20 | 1.10 |
| Under 330 mW load (V) | 1.49 | 1.35 | 1.27 | 1.20 | 1.16 | 1.12 | 1.10 | 1.08 | 1.04 | 0.98 | 0.62 |

- Source: Texas Instruments, *Single-cell Battery Discharge Characteristics
  Using the TPS61070 Boost Converter* (SLVA194, August 2004), Figure 3: one
  AA alkaline at a constant 330 mW, open-load and loaded curves.
  ["When the terminal voltage is discharged to < 0.9 V, almost all of the
  battery's usable energy is depleted. However, sometime after the load is
  removed, the terminal voltage recovers to nearly 1.2 V although the
  battery energy is still almost empty."](https://www.ti.com/lit/an/slva194/slva194.pdf)
- Status: **Confirmed** as a measurement, 2026-10-01. Read off TI's graph to
  about ±0.02 V. The same values are tabled on
  [Wikipedia, "Alkaline battery"](https://en.wikipedia.org/wiki/Alkaline_battery),
  which cites the same note. The percentages are shares of run time at
  constant power, close to energy left.
- **Caveats.** It is one cell at one load. Energizer warns that a reading at
  rest "can be misleading and at best will only yield a rough estimate" of
  service left. Energizer's better test is a reading under a load of about
  10 Ω for 1–2 s: fresh reads about 1.5 V, and a cell reading 1.1 V has
  about 20 % left. Confirmed, 2026-10-01: the Energizer handbook above.
- **Other sizes.** AAA, C and D share the chemistry and the fresh reading.
  No source gives their at-rest table. Applying the AA table to them is
  **Unconfirmed**; a D-size discharge curve with rest readings would
  confirm it.
- **At 0.1 V (derived):** a meter tells fresh (1.6), used (1.4–1.3) and
  nearly flat (1.2–1.1) apart, and no finer.

## Alkaline 9 V

- Six cells in series: IEC 6LR61, nominal 9.0 V, 45 g, rated "continuous
  discharge to 4.8 volts" (0.8 V a cell), shelf life 5 years at 21 °C.
  Confirmed, 2026-10-01: [Energizer 522](https://data.energizer.com/pdfs/522.pdf).
- At rest, six times the AA table: about **9.5 V fresh**, about 6.6–7.2 V
  flat. **Derived, Unconfirmed.**

## Zinc-carbon (the cheaper cell)

- Sold in three grades: General Purpose, Heavy Duty and Super Heavy Duty.
  Most are zinc chloride, a few Leclanché. "A Zinc Chloride battery is
  typically over 1.60 volts" fresh, with "higher open circuit and initial
  closed circuit voltage than LeClanche or alkaline". Rated to 0.75–0.8 V.
  Confirmed, 2026-10-01:
  [Energizer Carbon Zinc Handbook](https://data.energizer.com/pdfs/carbonzinc_appman.pdf).
- **Sizes** (Eveready Super Heavy Duty, Zn/MnO₂, metal jacket; rated at
  25 mA continuous to 0.8 V; the 9 V is Leclanché):

  | Size | IEC | Weight | Capacity |
  |---|---|---|---|
  | AA | R6 | 15.0 g | 1,100 mAh |
  | C | R14 | 45.0 g | 3,800 mAh |
  | D | R20 | 89.0 g | 8,000 mAh |
  | 9 V | 6F22 | 37.0 g | to 4.8 V |

  Confirmed, 2026-10-01:
  [1215](https://data.energizer.com/pdfs/1215.pdf),
  [1235](https://data.energizer.com/pdfs/1235.pdf),
  [1250](https://data.energizer.com/pdfs/1250.pdf),
  [1222](https://data.energizer.com/pdfs/1222.pdf).
- No source gives a zinc-carbon at-rest table by charge. **Unconfirmed.**

## Lithium AA (Li/FeS₂, 1.5 V)

- **Fresh: 1.79–1.83 V at rest; good above 1.74 V; flat below 1.70 V once
  recovered.** Energizer: "the OCV of fresh batteries can range from 1.79 to
  1.83V … A 'good' battery will generally have an OCV >1.74 volts. Any
  battery with an OCV <1.70 (after it has been allowed to recover) is
  completely discharged. Although an alkaline battery may read 'good' at 1.6
  volts, this reading on a LiFeS2 battery indicates the product has been
  discharged." Rated to 0.8–0.9 V under load. Confirmed, 2026-10-01:
  [Energizer Cylindrical Primary Lithium Handbook](https://data.energizer.com/pdfs/lithiuml91l92_appman.pdf).
- IEC FR6, 15 g, shelf life 25 years at 21 °C. Confirmed, 2026-10-01:
  [Energizer L91](https://data.energizer.com/pdfs/l91.pdf).
- A meter tells good from flat, not how much is left.

## NiMH (rechargeable, 1.2 V)

- **Charged: 1.25–1.35 V at rest (Duracell); about 1.4 V straight off the
  charger (Energizer).** It falls quickly to a flat plateau near 1.2 V and
  stays there for most of the discharge. Cutoff 0.9–1.0 V. Duracell: "The
  charged open circuit voltage … ranges from 1.25 to 1.35 volts per cell. On
  discharge, the nominal voltage is 1.2 volts per cell and the typical end
  voltage is 1.0 volt per cell." Energizer: "The initial drop from an
  open-circuit voltage of approximately 1.4 volts to the 1.2 volt plateau
  occurs rapidly." Energizer's cutoff is 0.9 V per cell. Confirmed,
  2026-10-01:
  [Duracell Ni-MH technical bulletin](https://www.farnell.com/datasheets/59865.pdf),
  [Energizer NiMH Handbook](https://data.energizer.com/pdfs/nickelmetalhydride_appman.pdf).
  The two makers' full readings likely differ because one is rested and one
  is fresh off the charger. **Unconfirmed.**
- **A meter can't tell its charge.** Energizer: "voltage sensing cannot be
  used to accurately determine state-of-charge." Confirmed, same handbook.
- **Self-discharge:** NiMH cells "will typically retain approximately 50% to
  80% of their capacity after 12 months of storage", faster when warm.
  Confirmed, same handbook.
- Energizer NH15 AA: IEC HR6, 2,300 mAh, 28 g. Confirmed, 2026-10-01:
  [NH15](https://data.energizer.com/pdfs/nh15-2300.pdf).
- An empty cell's at-rest reading: no source. **Unconfirmed.**

## Coin cell (CR2032, Li/MnO₂, 3 V)

- Nominal 3.0 V, 235 mAh to 2.0 V, 3.0 g, self-discharge about 1 % a year.
  Confirmed, 2026-10-01: [Energizer CR2032](https://data.energizer.com/pdfs/cr2032.pdf).
- Fresh at rest: about **3.2–3.3 V**. Energizer's worked example cell reads
  3.279 V. Confirmed for that cell, 2026-10-01:
  [Energizer Lithium Coin Handbook](https://data.energizer.com/pdfs/lithiumcoin_appman.pdf).
- The discharge is flat, so a meter tells little until the cell is nearly
  spent. **Unconfirmed** as a table.

## Lithium-ion (18650 and 21700, 3.6 V)

- **Charged to 4.2 V; end voltage 2.5 V; nominal 3.6 V.** Samsung SDI
  INR18650-25R: nominal 3.6 V (typical 3.64), charge CC-CV to 4.2 ± 0.05 V,
  end voltage 2.5 V, 43.8 g. Molicel INR-21700-P42A: 3.6 V nominal, charge
  4.2 V, discharge 2.5 V, 4 Ah. Confirmed, 2026-10-01:
  [Samsung INR18650-25R](https://www.powerstream.com/p/INR18650-25R-datasheet.pdf)
  (the maker's sheet, from a retailer's mirror);
  [Molicel INR-21700-P42A](https://www.molicel.com/wp-content/uploads/INR21700P42A-V4-80092.pdf).

### Charge left against the reading (measured)

| Charge left | 100 % | 90 % | 80 % | 70 % | 60 % | 50 % | 40 % | 30 % | 20 % | 10 % | 5 % | 0 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| At rest (V) | 4.15–4.2 | 4.08 | 4.02 | 3.91 | 3.84 | 3.74 | 3.65 | 3.58 | 3.47 | 3.34 | 3.17 | about 2.6 |

- Source: Pillai, Balasingam et al., *Performance Analysis of Empirical
  Open-Circuit Voltage Modeling in Lithium Ion Batteries, Part-3:
  Experimental Results*, Fig. 7: 28 low-rate curves from 16 Molicel
  INR-21700-P42A cells.
  [arXiv 2306.16575](https://arxiv.org/pdf/2306.16575).
- Status: **Confirmed** as a measurement, 2026-10-01. The values were
  digitized from the figure's pixels against its axis labels, to about
  ±0.02 V; the 28 curves spread about ±0.02 V. They agree with the paper's
  zoomed inset (3.76–3.77 V at 52.5–53.5 %). Part 2 gives the round
  figures: "when the battery is completely empty (SOC = 0%), the OCV is
  about 2.8V; and, when the battery is completely full (SOC = 100%), the OCV
  is about 4.2V" ([arXiv 2306.16547](https://arxiv.org/pdf/2306.16547)).
- The table is from a 21700. An 18650 of similar chemistry follows it
  closely. Applying it to an 18650 of unknown make is **Secondary**.
- Unlike every primary cell above, the reading tracks charge well at 0.1 V.

## Lead-acid, 12 V (a car battery)

- **Full: 12.73 V at rest (flooded); 12.10 V at half; 11.51 V at 10 %.**
  Read after the battery has stood "idle at least 6 hours, preferably up to
  24 hours".

  | Charge left | 100 % | 90 % | 80 % | 70 % | 60 % | 50 % | 40 % | 30 % | 20 % | 10 % |
  |---|---|---|---|---|---|---|---|---|---|---|
  | Flooded 12 V (V) | 12.73 | 12.62 | 12.50 | 12.37 | 12.24 | 12.10 | 11.96 | 11.81 | 11.66 | 11.51 |
  | Specific gravity | 1.277 | 1.258 | 1.238 | 1.217 | 1.195 | 1.172 | 1.148 | 1.124 | 1.098 | 1.073 |

  | Charge left | 100 % | 75 % | 50 % | 25 % | 0 % |
  |---|---|---|---|---|---|
  | AGM 12 V (V) | 12.84 | 12.54 | 12.24 | 11.94 | 11.64 |
  | Gel 12 V (V) | 12.84 | 12.66 | 12.36 | 12.00 | 11.82 |

  Per cell, flooded: 2.122 V full. The guide also gives 6 V and 8 V
  columns. Confirmed, 2026-10-01: Trojan Battery Company, *Battery User's
  Guide*, Table 7 and section 8.4
  ([PDF](https://ressupply.com/documents/trojan_battery/Battery_User's_Guide.pdf)).
- Trojan makes deep-cycle batteries. A car's starting battery is the same
  flooded chemistry, so the table carries over by chemistry: **Secondary**.
  A car battery maker's own table would confirm it.

## A set of cells

- Cells in series add their voltages: three fresh alkaline cells read about
  4.5 V. Secondary, 2026-10-01:
  [Wikipedia, "Alkaline battery"](https://en.wikipedia.org/wiki/Alkaline_battery),
  citing Linden, *Handbook of Batteries* (2002). A meter across a two-AA set
  reads double a cell's figure: about 3.2 V fresh, 2.2–2.4 V flat at rest.
  **Derived.**

## What the flashlight and the radio take

- **Portable radios sold in Argentina, one maker's 2024 range.** Pocket
  AM/FM radios, 6×10×2 cm to 7×12×3 cm: **2 × AA**. Larger 220 V or battery
  radios: **4 × C**. Rechargeable radios with a built-in LED light: **2 × D**
  or a built-in 18650 lithium-ion cell. Confirmed, 2026-10-01, for that
  range: Daihatsu, distributor price list No. 19, June 2024
  ([PDF](https://gruphogar.com.ar/wp-content/uploads/2023/04/LISTA-ELECTRO-HOGAR-DAIHATSU-No19-JUNIO-2024-1.pdf)).
  Another Argentine shop sells a 2 × AA pocket radio. Secondary:
  [La Colón](https://www.lacolon.com.ar/productos/radio-portatil-suono-am-fm-con-antena-a-pilas-aa/).
- **Flashlights.** A plastic LED flashlight on **2 × D**: 180 lm, 40 h on
  one set, 225 g, alkaline D cells included. Confirmed as its spec,
  2026-10-01; a Mexican maker, not confirmed on sale in Argentina:
  [Truper LIPLA-180](https://www.truper.com/ficha_tecnica/Linterna-plastica-LED-luz-directa-2-pilas-D-180-Lm-10599.html).
  An LED headlamp on **3 × AAA**: 100 lm, 6.5 h high, 7.5 h low, 75 g.
  Confirmed as its spec, 2026-10-01:
  [Pretul/Truper 27083](https://www.truper.com/ficha_tecnica/Linterna-para-cabeza-3-pilas-AAA-28-lumenes-3-LEDs-252665.html).
  2 × AA and 3 × AAA LED flashlights are both sold on Mercado Libre
  Argentina. Secondary, from a search summary; the site refuses automated
  reads.
- Which device is "typical" no source says. **Unconfirmed**, and a design
  choice.

## Cells sold in Argentina

- **The same two primary chemistries.** Ley 26.184 (sanctioned 29 November
  2006) covers cylindrical and prismatic cells, "comunes de carbón zinc y
  alcalinas de manganeso". It caps mercury at 0.0005 %, cadmium at 0.015 %
  and lead at 0.200 % by weight. It requires each cell to meet the
  minimum-duration discharge tests of IRAM, IEC or ANSI standards, and
  certification by the national technical body.
- **Every cell carries an expiry date:** "En el cuerpo de cada pila deberá
  figurar la fecha de vencimiento con indicación de mes y año."
- Confirmed, 2026-10-01:
  [Ley 26.184, INTI](https://www.inti.gob.ar/assets/uploads/files/certificaciones/pilas-y-baterias/ley26184.pdf).
  The figures above apply unchanged.
- Local names: *pila AA* (*doble A*), *AAA* (*triple A*), *pila tipo C*,
  *pila tipo D*, *batería de 9 V*.

## Not reached

- IEC 60086 itself (iec.ch refused the connection). The makers' figures
  stand in for it.
- At-rest tables by charge for D cells, zinc-carbon and coin cells, and an
  empty NiMH cell's at-rest reading.
- A car battery maker's own voltage table.
