# Fuel and generators

Real-world facts for gasoline (#239) and generators (#245). See `README.md`
for the status labels.

## Gasoline

- **US pumps show 87 (regular), 88–90 (midgrade) and 91–94 (premium)**, in
  large black numbers on a yellow label. 85 is sold in some high-elevation
  areas; Kentucky isn't one of them. Confirmed, 2026-09-25:
  [fueleconomy.gov](https://www.fueleconomy.gov/feg/octane.shtml).
- **The number is the Anti-Knock Index, (R+M)/2:** the average of the
  Research and Motor octane numbers. Argentina's "95" is a RON figure, a
  different scale. Secondary, 2026-09-24:
  [BMW MOA](https://bmwmoa.org/understanding-octane-aki-mon-and-ron-oh-my-2/).
- **Shelf life:** "gasoline lasts three to six months before it goes bad";
  ethanol-blended fuel shows "reduced combustibility occurring in just one to
  three months." A fuel stabilizer "can extend the usable life of gasoline
  during storage, although it cannot preserve fuel indefinitely." Confirmed,
  2026-09-25:
  [AAA Club Alliance](https://cluballiance.aaa.com/the-extra-mile/advice/car/how-to-keep-gas-from-going-bad).
- **Gas can start to degrade in as little as 30 days.** Briggs & Stratton's
  stabilizer claims up to 3 years; ASTM studies cited by Family Handyman give
  up to about a year. Secondary, 2026-09-24:
  [Briggs & Stratton](https://www.briggsandstratton.com/na/en_us/support/maintenance-how-to/browse/the-importance-of-fuel-stabilizer-by-briggsandstratton-stratton.html),
  [Family Handyman](https://www.familyhandyman.com/article/what-to-know-about-fuel-stabilizers/).
- **E10 phase separation:** ethanol absorbs water. Past about 0.4–0.5% by
  volume the water and ethanol drop out of the fuel and sink to the bottom of
  the tank. Secondary:
  [Bell Performance](https://www.bellperformance.com/blog/essentials-of-ethanol-fuel-stabilizers).

## Getting gasoline

- **Gas stations pump from underground tanks with submersible turbine pumps**,
  standard in the US since the 1970s. They're electric, so **without power the
  dispensers don't work.** Hand pumps made for underground tanks exist, through
  the fill port. Secondary, 2026-09-24:
  [John W. Kennedy Co.](https://jwkblog.com/wordpress/gas-station-equipment-guide-submersible-turbine-pumps/),
  [Northwest Pump](https://www.nwpump.com/petroleum/petroleum-products/submersible-pump-systems-and-leak-detectors/),
  [Source North America](https://shop.sourcena.com/Underground-Storage-Tank-Equipment/Hand-Pump).
- **Modern cars resist siphoning:**
  - a mesh screen inside the filler neck;
  - an anti-siphon (rollover) valve whose ball closes against anything pushed
    in;
  - one-way valves and internal barriers.

  The ways fuel is actually drawn out are **at the tank**, where the filler
  neck joins it, or **at the fuel rail's Schrader valve** in the engine bay,
  using the car's own fuel pump in repeated cycles. Both are labor-intensive.
  Confirmed, 2026-09-25:
  [Jalopnik](https://www.jalopnik.com/2060324/why-gas-cant-siphon-out-of-modern-cars/).
- **A typical car tank holds 13–16 gallons.** Car tanks range from about 10
  to 20. Secondary, 2026-09-24:
  [Mechanic Base](https://mechanicbase.com/cars/average-gas-tank-size/).
- **Gas cans come in 1, 2, 2.5 and 5 gallons, in red.** Since 2009, EPA rules
  require new portable fuel containers to be spill-proof to CARB standards,
  with auto-shutoff spouts. Secondary, 2026-09-24:
  [AMLEO / No-Spill](https://www.amleo.com/no-spill-carb-fuel-can-red-5-gallon/p/NS50).

## Portable generators

| | Champion 3500 W (model 201296, dual fuel) | Honda EU2200i (inverter) |
|---|---|---|
| Running | 3,500 W on gasoline (3,150 W on propane) | 1,800 W (15 A) |
| Starting / maximum | 4,375 W (3,950 W on propane) | 2,200 W (18.3 A) |
| Tank | 4.7 gal | 0.95 gal |
| Run time | 14 h at 50% load (10.5 h on a 20 lb propane tank) | 3.2 h at rated load, 8.1 h at 1/4 load |
| Engine | 224 cc, 4-stroke, 3,600 RPM | 121 cc (GXR120) |
| Weight | 104.7 lb | 47.4 lb |
| Noise | 68 dB(A) at 23 ft | — |
| Outlets | 120 V duplex (5-20R), 120 V 30 A RV (TT-30R), 120 V 30 A locking (L5-30R) | — |
| CO safety | **CO Shield**: auto shutoff when CO reaches unsafe levels | CO-MINDER, on some versions (not confirmed) |
| Status | **Confirmed**, 2026-09-25: [Champion 201296](https://www.championpowerequipment.com/product/201296-3500w-dual-fuel-generator/) | **Secondary**: Honda's press release and product page refuse automated readers; figures from search summaries of [Honda News](https://hondanews.com/en-US/power-equipment/releases/release-60f8b86b82a14607a3e13e208c572efc-honda-eu2200i-super-quiet-series-generator-technical-specifications) |

- **Fuel burn, derived from the table (not quoted):**
  - Champion: about **0.34 gal/h at 50% load**;
  - Honda: about **0.30 gal/h at rated load** and **0.12 gal/h at 1/4 load**.

  Burn rises with load but isn't proportional, because an idling generator
  still burns fuel.
- **Two kinds.** Open-frame generators give more watts for the money.
  Inverters are quieter and lighter, and their clean output suits electronics.
  Confirmed: Generac's worksheet (see `Electrical.md`).
- **Many current generators shut themselves off on high CO** (Champion's CO
  Shield above). Worth knowing for #248: a new generator may protect the
  player; an old one may not.
