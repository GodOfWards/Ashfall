# Sound — how loud things are, and how far they carry

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Gathered
2026-09-30 in the lore session (#329), first for how far Atucha's diesels
could be heard, at Tom's request; kept general because the threat system's
noise (#12) will need the same figures. The listener throughout is a human
ear; the canon has the dead hearing no better than that.

## How sound falls off with distance

- **From a point source in open air, the level drops about 6 dB each time
  the distance doubles** (the inverse square law): 90 dB at 1 m is 84 dB at
  2 m, 78 dB at 4 m, and so on. Secondary, 2026-09-30:
  [Engineering ToolBox, "Inverse Square Law"](https://www.engineeringtoolbox.com/inverse-square-law-d_890.html),
  [University of Manchester, "Basic Acoustics"](https://personalpages.manchester.ac.uk/staff/richard.baker/BasicAcoustics/4_inverse_square_law.html).
- **The air absorbs sound on top of that**, more at high frequencies: about
  **0.25 dB per 100 m at 2 kHz** (30 % relative humidity, 20 °C). Absorption
  matters from about 1 kHz upwards and depends on temperature and humidity,
  so **low rumbles carry further than high whines**. ISO 9613-1 is the
  standard method. Secondary, 2026-09-30:
  [ETH Zürich, "Sound propagation outdoors"](https://people.ee.ethz.ch/~isistaff/courses/ak1/acoustics-sound-propagation-outdoors.pdf),
  [ISO 9613-1](https://www.iso.org/standard/17426.html).
- **The ground, barriers and buildings take more off** (ISO 9613-2's ground
  effect and barrier attenuation). Figures depend on the site. Secondary:
  [DIN ISO 9613-2 summary (EPA Western Australia)](https://www.epa.wa.gov.au/sites/default/files/PER_documentation2/Appendix%2010%20-%20Noise%20Modelling.pdf).

## How quiet it is

- **A quiet rural night: about 20 dBA.** Wilderness and sparsely populated
  areas average about **30–40 dBA** over a day and night (Ldn). The US EPA
  took a night level of about **32 dB** as protecting sleep, and an outdoor
  Ldn of 55 dB as allowing normal speech at about 3 m. Secondary,
  2026-09-30:
  [Engineering ToolBox, "Outdoor Ambient Sound Pressure Levels"](https://www.engineeringtoolbox.com/outdoor-noise-d_62.html),
  [US EPA (archive)](https://archive.epa.gov/epa/aboutepa/epa-identifies-noise-levels-affecting-health-and-welfare.html),
  [Noise Pollution Clearinghouse, EPA "Levels" document](https://www.nonoise.org/library/levels74/levels74.htm).
- After the collapse there is no traffic, no industry and no mains hum, so
  a night near Lima would sit at the quiet end. **Derived, not measured.**

## Diesel generators

- **Industry measures generator noise at 7 m.** Typical diesel sets run
  about **75–85 dBA**; **open-frame sets 85 dBA and above at 7 m**; a canopy
  or sound-attenuating enclosure can take **up to 40 dBA** off; a 1,500 kW
  set is quoted at about **105 dB** (distance not given). Secondary
  (manufacturers and dealers), 2026-09-30:
  [Power Continuity](https://www.powercontinuity.co.uk/knowledge-base/how-to-define-noise-levels-in-diesel-generators/),
  [FW Power](https://fwpower.co.uk/knowledge-centre/noise-and-dba-in-generators/),
  [Generator Store](https://generatorstore.com.au/blogs/default-blog/how-loud-is-a-generator).

## Worked example: an open diesel at 85 dBA (derived)

Spreading only, then with air absorption at 2 kHz (0.25 dB/100 m). Ground
and obstacles would take more; low frequencies lose less to the air.

| Distance | Spreading only | With 2 kHz air absorption |
|---|---|---|
| 7 m | 85 dBA | 85 |
| 56 m | 67 | 67 |
| 224 m | 55 | 54 |
| 448 m | 49 | 48 |
| ~900 m | 43 | 41 |
| ~1.8 km | 37 | 33 |
| ~3.6 km | 31 | 22 |
| ~7.2 km | 25 | 7 |

**Reading it against a quiet night of about 20 dBA:** such a generator is
**plainly audible within about a kilometre, faint at two to four, and lost
beyond** — its low rumble outlasting its higher notes. **Inside a building
or enclosure (20–40 dB less), the same machine drops out within a few
hundred metres.** Estimates from the rules above, not measurements.
