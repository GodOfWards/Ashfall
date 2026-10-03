# Daylight: sunrise, sunset and civil twilight in Lima (#441)

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Researched
2026-10-03 for #441: #439 shows Atucha's lights on the horizon only after dark,
and #58's day and night will need the same figures.

## Local time

- **Argentina is on UTC−3, with no daylight saving in 2025. Confirmed.**
  - The Observatorio Naval Buenos Aires (part of the SHN) keeps the official
    time, under Decreto 1792/83. Its table of adopted time zones ends with
    **UTC−3 from 15 March 2009, "Continúa"**.
  - The last summer time ran from 19 October 2008 to 14 March 2009. Thirteen
    provinces stayed on UTC−3 even then; Buenos Aires province wasn't one of
    them.
  - **Ley 26.350** (28 December 2007) sets UTC−3 in winter and allows UTC−2
    in summer, on dates the national executive sets each year. None has
    been set since 2009.
  - [SHN, "Husos Horarios adoptados en la República Argentina"](https://www.hidro.gov.ar/Observatorio/LaHora.asp?op=3),
    read 2026-10-03. USNO's table for 2025 also gives `isdst: false`.

## Lima, February to July 2025

**Confirmed**, read 2026-10-03: the US Naval Observatory's
[one-day sun table](https://aa.usno.navy.mil/api/rstt/oneday?date=2025-02-15&coords=-34.0447,-59.1961&tz=-3),
at Lima's centre as `Lima.md` gives it (**34.0447 S, 59.1961 W**), at UTC−3.

- **USNO's convention:** sunrise and sunset are the sun's upper limb on the
  horizon, with standard refraction (the centre at −0.833°). Civil twilight
  is the centre 6° below the horizon. Sea level, flat horizon.
- **Checked independently:** PyEphem 4.2.1 and Astral 3.2 agree with USNO
  to the minute on 107 of these 108 values. The one exception is a tie at
  :30 seconds.
- **Day length** is sunset minus sunrise, from the computed seconds.
  **Derived.**

| Date | Civil dawn | Sunrise | Sunset | Civil dusk | Day length |
|---|---|---|---|---|---|
| 2025-02-01 | 05:51 | 06:18 | 20:02 | 20:29 | 13h 43m |
| 2025-02-08 | 05:59 | 06:25 | 19:56 | 20:23 | 13h 31m |
| 2025-02-15 | 06:06 | 06:32 | 19:49 | 20:15 | 13h 17m |
| 2025-02-22 | 06:13 | 06:39 | 19:41 | 20:07 | 13h 03m |
| 2025-03-01 | 06:19 | 06:45 | 19:33 | 19:58 | 12h 48m |
| 2025-03-08 | 06:25 | 06:51 | 19:24 | 19:49 | 12h 33m |
| 2025-03-15 | 06:31 | 06:56 | 19:14 | 19:39 | 12h 18m |
| 2025-03-22 | 06:37 | 07:02 | 19:05 | 19:30 | 12h 03m |
| 2025-04-01 | 06:44 | 07:09 | 18:51 | 19:16 | 11h 42m |
| 2025-04-08 | 06:49 | 07:15 | 18:42 | 19:07 | 11h 27m |
| 2025-04-15 | 06:55 | 07:20 | 18:33 | 18:58 | 11h 13m |
| 2025-04-22 | 07:00 | 07:25 | 18:25 | 18:50 | 11h 00m |
| 2025-05-01 | 07:06 | 07:32 | 18:15 | 18:41 | 10h 43m |
| 2025-05-08 | 07:11 | 07:37 | 18:09 | 18:35 | 10h 31m |
| 2025-05-15 | 07:16 | 07:43 | 18:03 | 18:30 | 10h 21m |
| 2025-05-22 | 07:20 | 07:48 | 17:59 | 18:26 | 10h 12m |
| 2025-06-01 | 07:26 | 07:54 | 17:55 | 18:23 | 10h 01m |
| 2025-06-08 | 07:30 | 07:58 | 17:54 | 18:22 | 9h 56m |
| 2025-06-15 | 07:33 | 08:01 | 17:54 | 18:22 | 9h 54m |
| 2025-06-22 | 07:35 | 08:02 | 17:55 | 18:23 | 9h 53m |
| 2025-07-01 | 07:35 | 08:03 | 17:59 | 18:26 | 9h 55m |
| 2025-07-08 | 07:35 | 08:02 | 18:02 | 18:29 | 10h 00m |
| 2025-07-15 | 07:33 | 08:00 | 18:06 | 18:33 | 10h 06m |
| 2025-07-22 | 07:29 | 07:56 | 18:10 | 18:37 | 10h 14m |

- **In February, dark falls (civil dusk) at about 20:30 at the start of the
  month and 20:05 by its end.** The sky lightens from about 05:50–06:15.
- **Extremes (USNO):** the earliest sunset is 17:54, around 8–15 June; the
  latest sunrise is 08:03, around 29 June–1 July; the shortest day is about
  20 June (9h 53m).
- **Interpolating linearly between rows is safe**: no time moves more than
  83 seconds from one day to the next. **Derived**, from the daily
  computation.
- **Civil twilight lasts 25–28 minutes**, the longest at midwinter.
  **Derived.**
- **Zárate city** (34.098 S, 59.029 W) runs about 40 seconds earlier than
  Lima. **Derived.**

## The SHN's official tables

- The SHN's ["Salida y Puesta de Sol – ciudad"](https://www.hidro.gov.ar/Observatorio/Astronomia.asp?op=1)
  covers 36 cities. **Lima and Zárate aren't among them.** The nearest is
  **Buenos Aires**.
- Its 2025 Buenos Aires figures for February to July, against the same
  calculation at central Buenos Aires: **all 724 values within one minute,
  610 exact.** The SHN appears to **truncate to the minute rather than
  round**, so its times run up to a minute earlier than USNO's. **Derived**
  from the comparison, read 2026-10-03.
- For comparison, the SHN's Buenos Aires on 1 February 2025: civil dawn
  05:46, sunrise 06:13, sunset 19:59, civil dusk 20:26. **Lima runs 3–5
  minutes later**, since it lies 0.8° further west.

## Not yet researched

- Nautical and astronomical twilight, and when the sky is fully dark: not
  needed yet. USNO's table doesn't give them; its other services or the SHN
  would.
- Moonrise, moonset and the moon's phase over the same months. USNO's table
  gives them, but they weren't recorded.
