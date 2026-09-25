# Carbon monoxide

Real-world facts for carbon monoxide (#248, on hold). See `README.md` for the
status labels.

## Effects by concentration in air

| ppm | Time | Effect |
|---|---|---|
| 35 | 6–8 h | Headache and dizziness with constant exposure |
| 50 | 8 h | OSHA permissible exposure level in any 8-hour period |
| 100 | 2–3 h | Slight headache |
| 200 | 2–3 h | Mild frontal headache, discomfort, loss of judgment, loss of vision, irritability |
| 400 | 1–2 h | Frontal headache and nausea; life-threatening after 3 h |
| 800 | 45 min | Dizziness, nausea, convulsions; collapse within 2 h, possible death |
| 1,600 | 20 min | Headache, fast heart rate, dizziness, nausea, confusion, staggering; death < 2 h |
| 3,200 | 5–10 min | Headache, dizziness, nausea; unconscious in 10–15 min; death within 30 min |
| 6,400 | 1–2 min | Convulsions, respiratory arrest; death < 20 min |
| 12,800 | 2 min | Unconscious after 2–3 breaths; death < 3 min |

Confirmed, 2026-09-25: an OSHA-funded handout (grainsafety.org, grant
SH-27664-SH5),
[PDF](https://www.osha.gov/sites/default/files/2018-12/fy15_sh-27664-sh5_Confined_Space_Handout_Effects_of_CO.pdf).

## The body's level (carboxyhemoglobin, COHb)

- **Symptoms by level:**
  - **10–20%:** headache and nausea can begin;
  - **above 20%:** vague dizziness, weakness, difficulty concentrating,
    impaired judgment;
  - **above 30%:** breathlessness on exertion, chest pain in people with
    heart disease, confusion;
  - **higher:** fainting, seizures, obtundation;
  - **above 60%, usually:** low blood pressure, coma, respiratory failure,
    death.

  Confirmed, 2026-09-25:
  [Merck Manual, Professional](https://www.merckmanuals.com/professional/injuries-poisoning/poisoning/carbon-monoxide-poisoning).
- **Clearing (elimination half-life):** "approximately **4.5 hours** when
  breathing room air, **1.5 hours** with 100% oxygen, and **20 minutes** with 3
  atmospheres of 100% oxygen." Confirmed, 2026-09-25: Merck Manual, above.
  - Other clinical sources give **about 320 minutes** on room air and 74
    minutes on 100% oxygen. Secondary:
    [CHEST](https://journal.chestnet.org/article/S0012-3692(15)32742-2/abstract).
  - Half-lives vary widely between patients. **Use Merck's 4.5 h** unless a
    decision says otherwise.
- **Common symptoms:** "headache, dizziness, weakness, upset stomach,
  vomiting, chest pain, and confusion." And: "**People who are sleeping, drunk,
  or under the influence of other substances can die from CO poisoning before
  they have symptoms.**" Confirmed, 2026-09-25:
  [CDC](https://www.cdc.gov/carbon-monoxide/about/index.html).

## CO alarms (UL 2034)

A listed alarm must sound within these windows (UL 2034 Section 39,
sensitivity test):

| Concentration | Must sound within |
|---|---|
| 70 ± 5 ppm | 60–240 min |
| 150 ± 5 ppm | 10–50 min |
| 400 ± 10 ppm | 4–15 min |
| rising 16 ppm/min to 480 ± 15 ppm | 19–30 min |

It's time-weighted on purpose: a brief whiff doesn't sound it, a sustained
dose does. Confirmed, 2026-09-25: CPSC, *Carbon Monoxide Alarm Conformance
Testing to UL 2034*, Table 3,
[PDF](https://www.cpsc.gov/s3fs-public/pdfs/COAlarmConformanceReportPhaseI.pdf).

## Generators and placement

- **The CDC:**
  - "Only use generators outside, **more than 20 feet away from any windows,
    doors, and vents**."
  - "**Never use a generator inside your home or garage, even if doors and
    windows are open.**"
  - "When using a generator, use a battery-powered or battery backup CO
    detector in your home."

  Confirmed, 2026-09-25:
  [CDC](https://www.cdc.gov/carbon-monoxide/about/index.html).
- **NIST's test-house study:** the highest indoor concentrations came from a
  generator in an attached garage with the bay door closed and the house door
  open. A cracked window or garage door isn't enough to prevent poisoning.
  Secondary, 2026-09-24:
  [NIST news](https://www.nist.gov/news-events/news/2013/07/study-provides-details-portable-generator-emissions-and-carbon-monoxide),
  [NIST TN 1782](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=912394).
- **The CDC estimated that up to half of non-fatal CO poisonings in the 2004
  and 2005 hurricane seasons involved generators run outdoors but within
  seven feet of the home.** Secondary (a city page citing the CDC),
  2026-09-24:
  [City of Webster](https://www.cityofwebster.com/Blog.aspx?IID=91).
- **Portable generators kill about 100 people a year in the US**, per a PIRG
  summary of CPSC data. Secondary, not read in full:
  [PIRG](https://pirg.org/edfund/resources/portable-generators-kill-about-70-people-each-year-heres-how-to-protect-yourself-and-your-loved-ones/).
- **Some current generators shut off automatically on high CO** (Champion's CO
  Shield). See `Fuel_and_Generators.md`.
