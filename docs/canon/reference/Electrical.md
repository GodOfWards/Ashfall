# Electrical — US wiring, breakers, appliances, meters

Real-world facts for the power system (#220 and its sub-issues). See
`README.md` for the status labels. Dates are when each was checked.

## Which code applies

- **Kentucky enforces NEC 2023 for permits pulled on or after January 1,
  2025**; permits pulled before then follow **NEC 2017**. The 2018 Kentucky
  Residential Code delayed a few 2023 articles (210.52(C), 230.67, 314.27(C))
  to **July 15, 2026**. Secondary, 2026-09-25:
  [Louisville Metro](https://louisvilleky.gov/government/construction-review/2023-national-electrical-code-update),
  [KY DHBC announcement](https://dhbc.ky.gov/Documents/2023%20NEC%20Update%20Announcement.pdf).
- **Code editions are not retroactive.** A building has what the code required
  when it was wired or last renovated. So each building's age (#237) decides
  its panel size, its GFCIs and its AFCIs. Secondary: general practice, stated
  in the sources for GFCI below.

## Branch circuits and panels (NEC)

- **Kitchen:** two 20 A small-appliance branch circuits for the countertop
  receptacles, with no other outlets (210.11(C)(1)).
- **Bathroom:** at least one 120 V, 20 A circuit for its receptacles (210.11(C)(3)).
- **Laundry:** at least one 20 A circuit (210.11(C)(2)).
- Secondary, 2026-09-24:
  [up.codes 210.11](https://up.codes/s/branch-circuits-required) (a summary;
  the full text sits behind a paywall),
  [NCW Home Inspections](https://ncwhomeinspections.com/branch-circuits-for-kitchen-baths-and-laundry/),
  [EC&M](https://www.ecmweb.com/national-electrical-code/qa/article/20901729/code-qa-additional-branch-circuit-requirements-for-dwelling-units).
- **A gas range on a small-appliance circuit.** NEC 210.52(B)(2) Exception
  No. 2 allows "receptacles installed to provide power for supplemental
  equipment and lighting on gas-fired ranges" on a small-appliance branch
  circuit. Cited in `ashfall.html`'s `apartment` template (v0.9.2), from a
  planning session's reading. Secondary.
- **General lighting and room outlets: 15 A on 14 AWG copper.** A bedroom
  typically gets one or two 15 A circuits.
  - The NEC sets **no maximum number of outlets** on a dwelling's
    general-purpose circuit; 8–10 is the practical rule of thumb.
  - Bedroom circuits need **AFCI** protection (210.12(A)).
  - Secondary, 2026-09-24:
    [ExpertCE](https://expertce.com/learn-articles/how-many-outlets-on-a-circuit-nec/),
    [WireRef](https://wireref.com/wire-size/15-amp-circuit/),
    [Fine Homebuilding](https://www.finehomebuilding.com/2022/11/18/how-many-outlets-per-circuit).
- **The 80% rule is a design limit, not a trip point.** A circuit's continuous
  load (3 hours or more) stays within 80% of its breaker: **1,440 W on 15 A,
  1,920 W on 20 A** at 120 V (210.19, 210.20). Secondary, 2026-09-24:
  [EEPower](https://eepower.com/technical-articles/national-electrical-code-basics-sizing-and-protecting-branch-circuit-conductors/),
  [IAEI](https://iaeimagazine.org/2016/may2016/100-vs-80-choosing-the-right-ocpd-solution/).
- **Standard breaker ratings (NEC 2023 Table 240.6(A)):** 10, 15, 20, 25, 30,
  35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 150, 175, 200, 225, 250, 300,
  350, 400, 450, 500, 600, 700, 800, 1000, 1200, 1600, 2000, 2500, 3000, 4000,
  5000, 6000 A. The fuse-only ratings are 1, 3, 6 and 601 A.
  - **10 A became a standard breaker size in NEC 2023**; it had been fuse-only.
    It came with 14 AWG copper-clad aluminum and LED-era lighting loads.
  - Secondary, 2026-09-25:
    [Mike Holt forum](https://forums.mikeholt.com/threads/nec-table-240-6-a-the-adding-of-10amps.2583765/),
    [up.codes 240.6](https://up.codes/s/standard-ampere-ratings). The game's
    `STANDARD_BREAKER_RATINGS` (v0.9.0) follows this list.
- **Service size:**
  - a one-family dwelling's service disconnect is at least **100 A**
    (230.79(C));
  - "all other installations" are at least 60 A (230.79(D));
  - older apartments commonly have 60, 70 or 100 A.
  - Secondary, 2026-09-25:
    [up.codes 230.79](https://up.codes/s/rating-of-service-disconnecting-means)
    (summary),
    [The Building Inspector](https://thebuildinginspector.net/blog/electric-service-capacity/).
- **Each occupant has ready access to the breakers protecting their unit**
  (240.24(B)). That's why a unit's panel is inside the unit. Cited in the
  game's `WIRING.acorn` comment (v0.9.1). Secondary.
- **Apartment buildings often take a 120/208 V three-phase service,** feeding
  each unit 120/208 V from two phases through a meter bank. A unit's "240 V"
  appliances then see 208 V. A small building may be 120/240 V single-phase.
  Secondary, 2026-09-24:
  [Mike Holt forum](https://forums.mikeholt.com/threads/apartment-feeders.8526/),
  [Electrician Talk](https://www.electriciantalk.com/threads/3phase-120-208v-in-dwelling-unit.65817/).
- **Examples of apartment services:**
  - a 3-unit building with two 100 A and one 200 A unit panel;
  - an 8-unit building with 100 A per unit.

  Secondary: [Mike Holt forum](https://forums.mikeholt.com/threads/power-supply-for-multi-unit-apartments.2566659/).
  **A four-unit building's main (the game's 200 A for Acorn) is unconfirmed.**

## Breakers (UL 489)

- **100%:** "A circuit breaker shall be capable of carrying 100 percent of its
  rated current without tripping" (UL 489 7.1.2.4.1). The rating is at 40 °C
  ambient, in open air.
- **135%:** a breaker carrying 135% of its rating "shall trip within 1 hour for
  a device rated at 50 A or less, and within 2 hours for a device rated at more
  than 50 A" (UL 489 7.1.2.3.1).
- **200%:** maximum trip time by rating:

  | Rating | Max time at 200% |
  |---|---|
  | 0–30 A | 2 min |
  | 31–50 A | 4 min |
  | 51–100 A | 6 min |
  | 101–150 A | 8 min |
  | 151–225 A | 10 min |
  | … | … |
  | 1601–2000 A | 28 min |

  The rows between 225 A and 1,600 A weren't legible in the source.
- **The instant (magnetic) trip:**
  - on a **C curve** it can't act below **5×** rating and must act by **10×**;
  - manufacturers typically calibrate it at about **7.5×**;
  - **D and K curves** calibrate at about **12–13×**, for motors.
  - These letter curves describe DIN-rail miniature breakers. US plug-in panel
    breakers aren't sold by curve letter, so applying 7.5× to them is an
    approximation (the game's `INSTANT_TRIP_MULTIPLE`).
- **Inverse time:** a household breaker rides through a motor's startup
  inrush, which lasts a fraction of a second, and trips on sustained
  overcurrent, faster the bigger the overload. Secondary, 2026-09-24:
  [JADE Learning](https://www.jadelearning.com/blog/understanding-motor-starting-inrush-currents-nec-article-430-52/),
  [ExpertCE](https://expertce.com/learn-articles/what-is-inverse-time-circuit-breaker/).
- **Sources:** confirmed, 2026-09-25:
  - [ABB white paper](https://library.e.abb.com/public/4909d9de000240fe93f705f99cef6eb1/MCB_White_Paper_Tripping_Characteristics_1TQC2039E0001.pdf),
    which quotes UL 489 and gives the curves;
  - [Castor, *Molded Case Circuit Breaker Basics*, EasyPower](https://www.easypower.com/files/Molded-Case-Circuit-Breaker-Basics.pdf),
    for the 200% table and the 40 °C rating.
- **Cold-load pickup.** After a long outage, thermostatic loads (fridges,
  heaters, air conditioners) all start together and keep running. Current can
  reach **up to about 6× normal at re-energizing, easing to about 2× within 5
  minutes**, and diversity returns within about 60 minutes after outages of 4
  hours or more. Utility literature; secondary, 2026-09-25:
  [EEP](https://electrical-engineering-portal.com/download-center/books-and-guides/relays/cold-load-pickup-inrush),
  [Power Monitors](https://powermonitors.com/whitepapers/cold-load-pickup/),
  [IEEE PES PSRC report](https://www.pes-psrc.org/kb/report/075.pdf).

## Appliances: running draw, starting draw, nameplates

"Running" is what a device draws while working. The **nameplate** is the
rated figure printed on it, higher than its typical draw.

| Appliance | Running | Starting (total) | Nameplate (real model) | Status and sources |
|---|---|---|---|---|
| Refrigerator | 100–250 W measured, compressor on | 3–4× running (inverter compressors 1.2–1.5×) | Frigidaire FFTR1821QW: 120 V, **6 A**, 0.72 kW connected load, 15 A min. circuit | Running and starting: secondary ([Anker](https://www.ankersolix.com/blogs/home-power-backup/how-many-watts-does-a-refrigerator-use-get-acquainted-now), [Anker, amps](https://www.ankersolix.com/blogs/portable-power-station/refrigerator-amp-usage-guide)). Nameplate: secondary, several retailer listings agree ([Appliances Connection](https://www.appliancesconnection.com/frigidaire-fftr1821qw.html), [Abt](https://www.abt.com/Frigidaire-White-Top-Freezer-Refrigerator-FFTR1821QW/p/84520.html)); Frigidaire's own page not read. |
| Refrigerator duty cycle | Compressor on about **33–40%** of the time in a room at about 70 °F (8–10 h a day); about 30–50% across cool and warm kitchens | | | Secondary, 2026-09-25: [Refrigerators Reviewed](https://refrigeratorsreviewed.com/refrigerator-compressor-duty-cycle/), [BenchNest](https://benchnest.com/articles/how-long-should-a-refrigerator-run/). The length of one on/off cycle wasn't found; the game's 60 min is unconfirmed. |
| Refrigerator defrost | adds about 1–3 A for 20–40 min | | | Secondary: Anker, amps. |
| LED bulb (60 W equivalent, about 800 lm) | **about 9 W**; Champion's chart gives 8–15 W | none | the wattage on its base | Secondary, 2026-09-24: [Batteries N Bulbs](https://www.batteriesnbulbs.com/blogs/news/doe-light-bulb-efficiency-standards-what-the-45-lumens-per-watt-rule-means); confirmed: [Champion chart](https://www.championpowerequipment.com/generator-wattage-chart/). |
| Bathroom exhaust fan | 10–50 W, about 36 W average | not modelled | Broan 688: **120 V AC, 0.9 A** (50 CFM, 4 sones) | Running: secondary ([Engineer Fix](https://engineerfix.com/how-many-watts-is-a-bathroom-exhaust-fan/), [HomeAlliance](https://homealliance.com/faq/how-many-watts-is-an-exhaust-fan)). Nameplate: secondary, distributor listings agree ([State Electric](https://www.stateelectric.com/products/broan-nutone-688)); maker's page: [Broan 688](https://broan-nutone.com/en-us/product/ventilationfans/688). A fan with a heater can exceed 1,400 W. |
| Range hood | 150–300 W on high, 50–80 W on low | not modelled | Broan 413004: **120 V, 60 Hz, 2.0 A (240 W)** | Running: secondary ([Engineer Fix](https://engineerfix.com/how-many-amps-does-a-range-hood-use/), [Storables](https://storables.com/articles/how-many-watts-does-a-range-hood-use/)). Nameplate: secondary, retailer listings agree ([AJ Madison](https://www.ajmadison.com/cgi-bin/ajmadison/413004.html)); maker's page: [Broan 413004](https://broan-nutone.com/en-us/product/rangehoods/413004). |
| Hardwired smoke alarm | about 1–2 W standby | none | BRK 9120: 120 V AC, **0.04 A** standby and alarm; battery backup | Running: secondary ([Kidde](https://www.kidde.com/home-safety/en/us/products/fire-safety/smoke-alarms/i12040)). Nameplate: secondary, 2026-09-25, from search summaries of the data sheet ([BRK 9120 spec](https://www.brooksequipment.com/files/spec_9120.pdf)); the sheet itself wasn't opened. |
| Gas range (standby) | **under 5 W**: control board, clock and display. One user measured 4 W. | spark module burst, not modelled | Frigidaire FCFG3062AS: **120 V, 12 A** (covers the oven's igniter) | Standby: secondary ([Engineer Fix](https://engineerfix.com/how-many-watts-does-a-gas-oven-use/)). Nameplate: secondary, retailer listings agree ([Abt](https://www.abt.com/Frigidaire-30-In.-Stainless-Steel-Front-Control-Gas-Range-With-Quick-Boil-FCFG3062AS/p/187598.html)). |
| Gas oven glow bar | **flat glow bars draw 3.2–3.6 A (384–432 W at 120 V)**; round 2.5–3.0 A. One user measured 400 W with the oven lit. | | | Secondary, 2026-09-25: [solar-electric forum](https://forum.solar-electric.com/discussion/11480/gas-oven-without-an-electric-glow-bar/p2), [Engineer Fix](https://engineerfix.com/how-many-watts-does-a-gas-oven-use/). **The game's comment says 372–432 W.** The oven isn't modelled, so it only matters if one arrives. |
| Electric tank water heater | 4,500–5,500 W at 240 V (18.8 A at 4,500 W) | none | on a dedicated 30 A two-pole breaker, 10 AWG | Secondary, 2026-09-24: [Mike Holt forum](https://forums.mikeholt.com/threads/water-heater-breaker-size.2555249/), [Home Inspection Insider](https://homeinspectioninsider.com/water-heater-breaker-size/). |

**Champion's generator wattage chart** gives these as a generator-sizing
guide (running, then *additional* starting watts). Confirmed, 2026-09-24:
[Champion](https://www.championpowerequipment.com/generator-wattage-chart/).

| Appliance | Running | Starting (additional) |
|---|---|---|
| Refrigerator | 150–400 W | +800–1,200 W |
| Freezer | 100–500 W | +500–1,000 W |
| Microwave | 600–1,200 W | — |
| LED bulb | 8–15 W | — |
| TV (32–55") | 80–400 W | — |
| Space heater | 750–1,500 W | — |
| Window AC (5,000 BTU) | 450–600 W | +900–1,200 W |
| Sump pump (1/3 HP) | 500–800 W | +1,000–1,600 W |
| Furnace fan (1/2 HP) | 300–800 W | +800–1,600 W |
| Well pump (1/2 HP) | 750–1,000 W | +1,500–2,000 W |
| Electric range (one burner) | 1,200–2,400 W | — |
| Phone or laptop charger | 20–100 W | — |

**Generac's 2018 worksheet** gives refrigerator/freezer 700 W running,
microwave 1,500 W, LED/LCD TV 120 W, coffee maker 1,200 W, cell phone charger
10 W. It says starting watts are "typically 2X running watts" and all figures
are approximate. Confirmed, 2026-09-25:
[Generac worksheet](https://dam.generac.com/ImConvServlet/imconv/b807fd2cc096c5464d1d28bc6f16d391f505a6b5/original).

**Sizing charts read high on purpose.** They size a generator. The game uses
measured running draw.

## Lighting

- **DOE's 45 lumens-per-watt standard for general service lamps** has been
  fully enforced since **August 1, 2023**. It effectively ended sales of most
  incandescent and halogen general-service bulbs, so in 2026 a home's bulbs are
  mostly LED, with old incandescents still in some sockets. Secondary,
  2026-09-24:
  [Beveridge & Diamond](https://www.bdlaw.com/publications/u-s-department-of-energy-finalizes-rules-to-impose-stringent-efficiency-standard-on-most-lamps/),
  [Consumer Products Law Blog](https://www.consumerproductslawblog.com/2022/05/us-lamp-saga-continues-with-onset-of-45-lpw-rule/).
- **About 800 lumens** comes from a 9 W LED, a 45 W halogen or a 60 W
  incandescent. Secondary, same sources.

## Gas stoves in an outage

- **Electric-ignition surface burners can be lit with a match in a power
  outage:** hold a lit match at the burner, then turn the knob to low.
- **The oven can't be lit by hand in an outage.** Its glow-bar igniter and gas
  valve need power.
- Secondary, 2026-09-24: [GE Appliances, burners](https://products.geappliances.com/appliance/gea-support-search-content?contentId=19226),
  [GE Appliances, ovens](https://products.geappliances.com/appliance/gea-support-search-content?contentId=17512),
  [Whirlpool](https://www.whirlpool.com/blog/kitchen/will-a-gas-stove-work-in-power-outage.html).

## GFCI and AFCI

- **Where the NEC requires GFCI in a dwelling (210.8(A)):**
  - bathrooms;
  - garages, and accessory buildings with floors at or below grade;
  - outdoors;
  - crawl spaces;
  - basements (all of them from 2023);
  - kitchens (all kitchen receptacles in 2023; the 2026 wording is
    receptacles serving countertops and work surfaces);
  - within 6 ft of a sink, or of a bathtub or shower;
  - laundry areas;
  - boathouses;
  - indoor damp and wet locations (expanded in 2026).
  - Secondary, 2026-09-25:
    [HIITIO (2026 NEC)](https://www.hiitio.com/every-location-where-the-2026-nec-requires-gfci-protection/),
    [JourneymanIQ](https://journeymaniq.com/resources/nec-210-8-gfci-requirements),
    [JADE Learning](https://www.jadelearning.com/blog/2023-nec-section-210-8a5-gfci-protection-for-basements/).
- **Not retroactive:** an older building has what its era required, perhaps
  only a bathroom GFCI, or none.
- **AFCI:** bedroom circuits (210.12(A)). See Branch circuits.

## Extension cords

A cord's safe current falls with length, because resistance and voltage drop
build over distance.

| Gauge | Rating at 120 V |
|---|---|
| 16 AWG | 10 A (1,200 W) up to 50 ft; 7 A beyond. ESFI lists 1–13 A at 25–50 ft. |
| 14 AWG | 15 A (1,800 W) up to 50 ft; 13 A to 100 ft |
| 12 AWG | 20 A up to 50 ft; 15 A to 100 ft |
| 10 AWG | 20 A (2,400 W) to 100 ft; 15 A to 150 ft |

- **ESFI's guidance for 100 ft cords:** 1–10 A on 16 AWG, 11–13 A on 14 AWG,
  14–15 A on 12 AWG, 16–20 A on 10 AWG.
- **Voltage drop:** a 12 A load on 100 ft of 16 AWG loses about 9.5 V (8%),
  enough to overheat motors. On 12 AWG it loses 3.8 V (3%). About 3% is the
  usual design limit and 5% the upper safe limit.
- Secondary, 2026-09-24/25: these are chart guides, not cord-set ratings. A
  cord's own label wins.
  [Pro Tool Reviews](https://www.protoolreviews.com/extension-cord-size-chart-wire-gauge-amps/),
  [TRADESAFE](https://trdsf.com/blogs/news/extension-cord-gauge-guide),
  [Vantecable](https://vantecable.com/blogs/extension-cord-library/extension-cord-gauge-chart-what-size-do-you-need).

## Meters

- **Fluke 115 (multimeter):** 550 g; AC and DC voltage up to 600 V; AC and DC
  current **up to 10 A**, measured by breaking into the circuit (20 A overload
  for 30 s maximum); resistance to 40 MΩ; a 9 V battery. It can't safely read a
  household branch circuit's current. Secondary, 2026-09-25:
  [Bürklin](https://www.buerklin.com/en/p/fluke/multimeters/fluke-115/21K3132/),
  [Cole-Parmer data sheet](https://pim-resources.coleparmer.com/data-sheet/26016-30.pdf);
  maker's page: [Fluke 115](https://www.fluke.com/en-us/product/electrical-testing/digital-multimeters/fluke-115).
- **Fluke 323 (clamp meter):** 265 g; **AC current to 400.0 A** (0.1 A
  resolution), clamped around one conductor, jaw up to 30 mm; AC and DC voltage
  to 600.0 V; CAT III 600 V / CAT IV 300 V. Secondary, 2026-09-25:
  [Mouser data sheet](https://www.mouser.com/datasheet/2/159/mpdf-3179798.pdf);
  maker's page: [Fluke 323](https://www.fluke.com/en-us/product/electrical-testing/clamp-meters/fluke-323).
- **Watts from a meter:** volts × amps, with a multimeter for voltage and a
  clamp for current. There's no plug-in watt meter in the game (#249).

## Rail crossings

- **49 CFR 234.215, "Standby power system":** "A standby source of power shall
  be provided with sufficient capacity to operate the warning system for a
  reasonable length of time during a period of primary power interruption. The
  designated capacity shall be specified on the plans required by § 234.201 of
  this part." Confirmed, 2026-09-25:
  [Cornell LII](https://www.law.cornell.edu/cfr/text/49/234.215).
- **49 CFR 234.251, "Standby power":** "Standby power shall be tested at least
  once each month." Confirmed, 2026-09-25:
  [Cornell LII](https://www.law.cornell.edu/cfr/text/49/234.251).
- **No length is set in the regulation.** The game's 24 hours is
  unconfirmed.
