# Boiling water — what makes it safe, and where a kettle cuts out

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Gathered
2026-10-02 for #421: #385 needs to know whether water a kettle brings to the
boil and cuts out on is safe to drink, beside the stove's flat
`BOIL_MINUTES` (5). Brands are named here as sources only; none appears in
the game.

## Does reaching the boil make water safe?

**The authorities disagree.** WHO says reaching a rolling boil is enough;
the CDC and Argentina's own health authorities ask for a sustained boil of
one to three minutes. None asks for five.

- **WHO: reaching a rolling boil is enough, with no hold time, at any
  altitude.** "The process of heating water to a rolling boil … is
  sufficient to inactivate pathogenic bacteria, viruses and protozoa. After
  the water has reached a rolling boil, it should be removed from the heat,
  allowed to cool naturally, without the addition of ice, and protected from
  post-treatment recontamination during storage." Boiling kills pathogens
  "even in turbid water and at high altitude." **Confirmed**, 2026-10-02:
  WHO, *Boil water*, technical brief WHO/FWC/WSH/15.02, last updated January
  2015 ([IRIS](https://iris.who.int/server/api/core/bitstreams/6d37bdcd-04b0-48d7-9a88-1e18b36c2b56/content)).
- **WHO's *Guidelines for drinking-water quality* say the same.** "Bringing
  water to a rolling boil is the simplest and most effective way to kill all
  disease-causing pathogens, even in turbid water and at high altitudes"
  (§6.12; Table 6.1: "Bring water to a rolling boil and allow to cool").
  Boil water advisories "should indicate that the water can be made safe by
  bringing it to a rolling boil … This procedure is effective at all
  altitudes and with turbid water" (§7.6.1). For water with nitrate, "care
  should be taken to ensure that water is heated only until the water
  reaches a rolling boil" (§8.7.5): longer boiling concentrates it.
  **Confirmed**, 2026-10-02: WHO, *Guidelines for drinking-water quality*,
  4th edition incorporating the first and second addenda, 2022, ISBN
  978-92-4-004506-4
  ([IRIS](https://iris.who.int/server/api/core/bitstreams/69c17edd-ee26-425b-9d34-33799377e886/content)).
- **Why no hold is needed (WHO's Table 1).** Bacteria die at under a minute
  per 90 % above 65 °C; hepatitis A and poliovirus lose more than 99.999 % in
  under a minute above 70–85 °C; *Cryptosporidium* oocysts are inactivated
  in under a minute above 70 °C. Water heating to 100 °C passes through
  those temperatures on the way up. Confirmed, same brief.
- **CDC: a rolling boil for 1 minute; 3 minutes above 6,500 ft (≈ 2,000 m).**
  "Bring clear water to a rolling boil for 1 minute (at elevations above
  6,500 feet, boil for 3 minutes). Let the boiled water cool." **Confirmed**,
  2026-10-02: CDC, *How to Make Water Safe in an Emergency*, 19 September 2024
  ([cdc.gov](https://www.cdc.gov/water-emergency/about/index.html)).
- **Argentina's Ministerio de Salud: 2 to 3 minutes.** "Si no tenés agua
  potable, hervila entre 2 y 3 minutos, o agregale 2 gotas de lavandina por
  litro, media hora antes de usarla." **Confirmed**, 2026-10-02:
  [Usá siempre agua segura](https://www.argentina.gob.ar/salud/crecerconsalud/cuidadosverano/aguasegura);
  the same wording on
  [Alimentación segura](https://www.argentina.gob.ar/salud/verano/alimentacionsegura).
- **ANMAT: 3 minutes.** "Si no se dispone de agua potable: Hervila durante 3
  minutos." **Confirmed**, 2026-10-02:
  [ANMAT, Agua segura y salud](https://www.argentina.gob.ar/anmat/comunidad/informacion-de-interes-para-tu-salud/agua).
- **Altitude doesn't apply to Lima.** The CDC's longer boil starts at
  6,500 ft, about 2,000 m; WHO's needs none at any altitude. Lima is near
  sea level (`Lima.md`).
- **Not found:** AySA's own boil-water advice (its site didn't answer,
  2026-10-02), and the Buenos Aires province health ministry's.

## Does a kettle cut out at a full boil?

**Yes, a standard automatic kettle cuts out after the water boils, not
before**: the switch is tripped by the boil's own steam. Two exceptions
matter to the game: a kettle set to a lower temperature, and one furred with
limescale.

- **The switch is tripped by steam.** A tube or vent carries steam from the
  top of the water chamber to a bimetallic disc; "when the hot water reaches
  boiling point, the steam produced hits the bimetallic thermostat and makes
  it suddenly snap," which trips the switch. Secondary, 2026-10-02:
  [Explain that Stuff, *How do electric kettles work?*](https://www.explainthatstuff.com/how-electric-kettles-work.html).
  Strix's patents describe the same steam-sensing bimetal
  ([EP1312290B1](https://patents.google.com/patent/EP1312290B1/en),
  [US6914514B2](https://patents.google.com/patent/US6914514); search summary,
  not read in full). The steam switch is separate from the boil-dry cut-out,
  a second bimetal under the element (Secondary, 2026-10-02,
  [Davinci Technology](https://www.davinci-machine.com/info/understanding-the-electric-kettle-thermostat-101209981.html)).
- **A health authority accepts it as a rolling boil.** "Water used for
  drinking or food preparation should be brought to a rolling boil to make
  it safe. Kettles with automatic shut off switches can do this."
  **Confirmed**, 2026-10-02: NSW Health (Australia), *What to do if a boil
  water alert is in place*, current as at 23 May 2025
  ([health.nsw.gov.au](https://www.health.nsw.gov.au/environment/water/Pages/bwa-what-to-do.aspx)).
- **The boil lasts a few seconds before the switch trips.** Owners' reports
  describe a rolling boil for a few seconds before it cuts out. Secondary
  (search summary, 2026-10-02); how many seconds wasn't found, and it varies
  with the kettle and the fill. Not near the CDC's one minute.
- **A temperature-select kettle cuts out below the boil.** The Atma PE1821
  has six levels, one for mate (`Electrical_AR.md`, "How the small
  appliances stop"). At a mate setting the water never boils.
- **Limescale makes a kettle cut out early.** AEG: "Kettle switches off
  before boiling … Cause: Too much limescale at the base of the kettle."
  Secondary (maker's support page, a cause, not a test), 2026-10-02:
  [AEG](https://support.aeg.co.uk/support-articles/article/kettle-switches-off-before-boiling).
- **Not researched:** IEC 60335-2-15's wording on the boil switch (the
  standard is paywalled); electronic-thermostat kettles, which cut out at a
  sensed temperature rather than on steam; and whether an open lid stops a
  kettle cutting out.

## For #385

- **A kettle's cut-out meets WHO's test, not the CDC's or Argentina's.** The
  kettle cutting out at the boil is a rolling boil by WHO's guidance and NSW
  Health's, and so safe whatever the volume. By the CDC's (1 min) or
  Argentina's (2–3 min), it isn't.
- **The game's stove figure, 5 minutes, is longer than any authority asks.**
  Recorded here, not fixed: which test the game follows is Tom's call.
