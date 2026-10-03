# Water temperature — heating it on gas and wood, how fast it cools, and the tap's temperature

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Gathered
2026-10-03 for #432: #431 heats water at a source's power, cools it toward
the room by Newton's law, and starts new water at the tap's temperature;
#385 needs it for the boil and the kettle's fuel saving. The electric
kettle's power and efficiency are in `Electrical_AR.md`; the air
temperatures this file leans on are in `Climate.md`. Brands are named here as
sources only; none appears in the game.

## A gas burner's heat output

- **ENARGAS's ratings are already on file:** small 1,000, medium 1,400, large
  1,800 kcal/h, oven 3,000 kcal/h (`Fuel_AR.md`, "Bottled gas"). In kW,
  derived: **1.16, 1.63, 2.09 and 3.49 kW**. ENARGAS gives the same burners
  as **0.10, 0.15, 0.19 and 0.32 m³/h**. The page doesn't say which gas the m³/h assume,
  and gives one table, not one for natural gas and one for LPG. **Primary**,
  read 2026-10-03
  ([ENARGAS](https://www.enargas.gob.ar/secciones/eficiencia-energetica/consumo-artefactos.php)).
- **One maker's nominal figures run higher:** a Bosch HSF12K30NF natural-gas
  cooker sold in Argentina declares **1,696 W per small burner (75 mm),
  2,195 W for the large (85 mm) and 2,694 W for the oven**. Quoted in
  González (2010), below; **secondary** for the maker's figures.
- **Natural gas against bottled gas: no separate ratings found.** A cooker is
  built for one or converted with injectors, at 180 mm water column on
  natural gas and 280 mm on LPG (`Fuel_AR.md`). Whether a converted burner's
  output matches is unconfirmed.

## How much of it reaches the water

- **ENARGAS: about 50 % for a gas hob.** "La eficiencia media de los anafes a
  gas es del orden del 50%." Its Figure 6, measured **with lidded pots**, on
  equipment of known brands sold in 2016–2018:

  | Cooker | Efficiency |
  |---|---|
  | Natural gas hob | 49 % |
  | LPG hob | 52 % |
  | Electric kettle | 91 % |
  | Induction | 81 % |
  | Glass-ceramic | 77 % |
  | Electric coil | 74 % |
  | Microwave | 53 % |
  | Wood, three stones | 15 % |

  **A lid saves about 30 %** on gas, LPG and electric coil hobs ("el uso de
  la tapa puede aportar un ahorro del orden del 30%"). **Primary**, read
  2026-10-03: L. Mora Iannelli and S. Gil, *Eficiencia en la cocción.
  ¿Cuáles son los artefactos de cocción más eficientes en Argentina?*,
  ENARGAS, 2020
  ([PDF](https://www.enargas.gob.ar/secciones/publicaciones/divulgacion-tecnica/pdf/eficiencia-coccion.pdf)).
  The figures come from P. Sensini et al., *Avances en Energías Renovables y
  Medio Ambiente* 41, 57–67 (2018), which wasn't reachable (a 503).
- **Measured on a natural-gas cooker in Bariloche: efficiency falls as the
  flame rises, and a narrow kettle loses more than a wide pot.** A 20 cm
  stainless pot with a lid, holding 2 L, and a stovetop kettle (12 cm base)
  holding 1.2 L, both heated to 90 °C:

  | Vessel | Flame | Efficiency | Minutes to 90 °C |
  |---|---|---|---|
  | 2 L pot | low to medium | 60 % | 14–23 |
  | 2 L pot | medium to high | 50–55 % | 9–14 |
  | 1.2 L kettle | low to medium | 45–55 % | 13–17 |
  | 1.2 L kettle | medium to high | 30–45 % | 10–13 |

  The range runs from **62 % at the lowest flame to 50 % at full** in the
  pot, and **55 % to 29 %** in the kettle. Two earlier LPG readings on a
  small burner were 62 % at 1,200 W and 49 % at 1,530 W. The paper doesn't
  give the water's starting temperature. **Primary**, read 2026-10-03: A. D.
  González, "Comparación de energías y gases de efecto invernadero en
  calentamiento de agua para cocción de alimentos con electricidad y gas
  natural", *Avances en Energías Renovables y Medio Ambiente* 14 (2010),
  07.25–07.32
  ([PDF](http://sedici.unlp.edu.ar/bitstream/handle/10915/100144/Documento_completo.pdf-PDFA.pdf?sequence=1&isAllowed=y)).
  The same paper measured electric kettles at **95–96 %**, heating 1.2 L to
  90 °C in 4–4.6 min at 1,540–1,600 W.
- **A cross-check from the UK: 38–39 %.** 1 L in an uncovered (as far as the
  page says) 19 cm stainless pan, 10 °C to 100 °C, on a gas hob of about
  1,833 W. It took 80 % longer than on a 1,440 W induction hob, which was
  about 86 % efficient. **Secondary**, read 2026-10-03: M. de Podesta, "A
  Watched Pan…", *Protons for Breakfast*, 2022-01-18
  ([blog](https://protonsforbreakfast.wordpress.com/2022/01/18/a-watched-pan/));
  a metrologist's home measurement, not a standard test.
- **Derived: 1 L from 20 °C to 100 °C (335 kJ) on ENARGAS's burners at 49 %,
  lidded:** large ≈ **5.4 min**, medium ≈ **7.0 min**, small ≈ **9.8 min**.
  González's result that low flames are more efficient would bring the small
  burner nearer 8 min. **Uncovered, at about 1.4 × the energy** (the 30 %
  lid saving): large ≈ 7.8 min, which agrees with de Podesta's ≈ 7.9 min for
  the same rise. Derived, not read.

## A wood fire

- **ENARGAS: 15 % for a three-stone fire** with a lidded pot (Figure 6,
  above). **Primary**, as above.
- **The cookstove literature gives 10–15 % for an ordinary open fire, and
  20–30 % for one shielded from the wind and well tended.** Search summaries
  of Aprovecho Research Center and the Partnership for Clean Indoor Air
  ([Aprovecho](https://aprovecho.org/the-big-picture/learning-from-the-three-stone-fire/),
  [Low-tech Magazine](https://solar.lowtechmagazine.com/2014/06/well-tended-fires-outperform-modern-cooking-stoves/));
  **secondary**. One controlled-cooking study in Tanzania cites 7–12 %
  (Hafner et al., *Environmental Research Letters*, 2018,
  [IOP](https://iopscience.iop.org/article/10.1088/1748-9326/aa9da3);
  secondary, quoting earlier work).
- **A wood fire runs at several kW.** The Water Boiling Test protocol's
  worked example shows two wood stoves at **6.6 kW**, burning 23–24 g of wood
  a minute; one boiled 5 L in **36 min at 19 %**, the other in **20 min at
  28 %**. These are stoves, not open fires. **Primary** for the protocol's
  example, read 2026-10-03: Global Alliance for Clean Cookstoves, *The Water
  Boiling Test, version 4.2.3*, Table 1
  ([PDF](https://cleancooking.org/binary-data/DOCUMENT/file/000/000/399-1.pdf)).
- **An open fire boils 5 L in about 27 minutes** in a well-tended test, on
  1,112 g of wood for boiling and 45 minutes' simmer. **Secondary** (Low-tech
  Magazine quoting PCIA, 2012).
- **Derived: 1 L from 20 °C to 100 °C on a going fire takes about 6–19
  minutes:** ≈ 5.6 min at 6.6 kW and 15 %, ≈ 19 min at 3 kW and 10 %. That
  doesn't include lighting the fire and getting it going. Camping guides say
  **10–20 minutes** for 1 L over a campfire (search summaries, secondary at
  best; no measurement behind them). **Unconfirmed** for a 1 L pot on a
  small fire; a timed boil would confirm it.

## How fast water cools off the heat

- **A mate thermos: the European standard sets a floor.** EN 12546-1 (vacuum
  ware, insulated flasks and jugs) requires a vacuum **flask of 801–1,200 mL
  to be no lower than 78 °C** after its heat-loss test. Other sizes: 70 °C
  at 401–600 mL, 75 °C at 601–800 mL, 80 °C above 1,200 mL. **Secondary**,
  read 2026-10-03: the standard's table as quoted in a 2021 test report
  (No. GZHL2101000144CW, 2021-01-13,
  [PDF](https://m.media-amazon.com/images/I/810DQpbuNWL.pdf)). The test
  itself, **filled at 95 °C, in a 20 °C room, for 6 hours**, is from search
  summaries (secondary); the standard is paywalled.
  - **Derived: Newton's constant for a compliant 1 L flask is at most
    ≈ 0.043 per hour** (ln(75/58)/6 h), a time constant of at least 23 hours.
    1 L at 90 °C in a 25 °C room would be ≈ 82 °C after 3 hours at that
    limit. Many flasks do better than the floor.
  - **Argentine thermos listings claim 4–24 hours "hot"**, without saying
    what "hot" means (retail listings, search summary; secondary, not
    usable as a rate).
  - **A glass-lined plastic thermos is vacuum ware too**, so the same table
    applies.
  - **Not covered:** a mate round, where the thermos is opened and poured
    from every minute or two.
- **An open pot, a kettle: no measured curve found.** The searches turned up
  only school experiments on beakers and mugs. **Unconfirmed.** A physics
  estimate, derived here and not read:
  - **1 L in an uncovered 19 cm saucepan, in a 20 °C room, falls from 100 °C
    to 70 °C in very roughly 10–15 minutes**, which is a Newton's constant of
    about 0.03–0.04 per minute. Evaporation from the open surface carries
    most of the heat above about 80 °C, so the first minutes fall faster
    than Newton's law predicts, and the rest slower.
  - **A lid, or a closed kettle, stops most of the evaporation** and should
    roughly halve the rate. A plastic electric kettle's walls lose less
    heat than metal.
  - **What would confirm it:** a kitchen thermometer read every 5 minutes for
    an hour, on 1 L in each vessel. Tom could measure it at home; nothing
    else found would.
- **Lids make a large difference in measured mugs.** In a vacuum-insulated
  mug, removing the lid raised the initial cooling rate **7.5-fold**.
  **Secondary**, M. de Podesta, *Protons for Breakfast*, "Mug cooling: the
  lid effect", 2018-11-12
  ([blog](https://protonsforbreakfast.wordpress.com/2018/11/12/mug-cooling-the-lid-effect/),
  via search summary).

## The tap's temperature

- **Lima's water comes from electrically pumped wells** (`Lima.md`,
  "Utilities in Lima and the region"), and a roof tank on every house
  outside the Barrio Atucha stores it.
- **Argentina's hot-water planning assumes cold water at 17 °C.** Heating
  180 L "de 17°C a 42°C" takes 5.2 kWh a day. **Primary** for the figure
  used, but an assumption, not a measurement: S. Gil, Fundación Bariloche,
  *Eficiencia energética en Argentina: Agua Caliente Sanitaria*, 2020
  ([PDF](https://www.eficienciaenergetica.net.ar/img_publicaciones/04271009_03.SectorResidencial-ACS.pdf),
  read 2026-10-03; also in `Electrical_AR.md`).
- **Measured in Resistencia (Chaco), 2022–2023: network water and roof-tank
  water follow the air, warmer than it.** Data loggers on household supplies,
  fitted to an annual sine wave, coldest in July:

  | Water | Annual mean | Amplitude |
  |---|---|---|
  | Air (SMN 1991–2020) | 21.3 °C | 6.1 °C |
  | Network, no house tank | 25 °C | 7 °C |
  | 500 L tank under a roof, in an attic | 25.1 °C | 8.5 °C |
  | 500 L black polyethylene tank, exposed | 26.7 °C | 6.8 °C |

  Its summary: network water is "una oscilación armónica de periodo anual,
  con una media de 4 ºC superior a la temperatura ambiente y una amplitud de
  7 ºC, con el mínimo para el mes de julio". **Primary**, read 2026-10-03:
  G. R. Figueredo, J. J. Pochettino, H. D. Zurlo, "Temperatura del agua de
  alimentación a colectores y su influencia en la fracción solar",
  *Revista Tecnología y Ciencia* (UTN) 48 (2023), 41–55,
  [doi:10.33414/rtyc.48.41-55.2023](https://doi.org/10.33414/rtyc.48.41-55.2023)
  ([PDF](https://rtyc.utn.edu.ar/index.php/rtyc/article/download/1289/1195/7258)).
  The paper doesn't say whether that network draws on a river or wells.
- **Groundwater near Lima: one reading, uncertain.** Wells 25–70 m deep in
  the Pergamino–Arrecifes basin, northeast Buenos Aires, measured
  **20.1–29.9 °C** at sampling (search summary of a *Journal of South
  American Earth Sciences* paper on the region's water quality,
  [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0895981107000132);
  secondary). The season, and whether the water warmed in the pipe, aren't
  known; the paper was blocked (403).
- **For Lima, derived and unconfirmed:**
  - **Mains water, pumped straight from a well:** close to the year's mean,
    **about 17–20 °C in any season** (Gil's 17 °C; San Fernando's annual
    mean air temperature is 17.6 °C, `Climate.md`). Groundwater varies far
    less through the year than piped surface water.
  - **Roof-tank water** follows the air, as in Resistencia: by its exposed
    tank's offset, **about 5 °C above the month's mean air temperature**, so
    **≈ 28–29 °C in February and ≈ 15–16 °C in July** (San Fernando's means,
    `Climate.md`). The tanks' colour and placement in Lima are unknown.
  - **What would confirm it:** a reading from ENDEZA, or a thermometer in a
    Lima tap.

## Not yet researched

- Measured cooling curves for a saucepan, a pot, an aluminium stovetop kettle
  and a plastic electric kettle.
- The EN 12546-1 test procedure from the standard itself.
- Lima's well water temperature; the colour of Lima's roof tanks.
- Separate burner ratings for natural gas and LPG.
