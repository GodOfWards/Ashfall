# Ashfall Handoff — Re-base the power system on Argentina

Current shipped version: v0.10.2
Implied version-change type: PATCH (data, constants and one formula
  generalised; no new persistent state, and power definitions aren't saved)
Issue: #289 — Re-base the power system on Argentina — 220 V, IEC breakers,
  the diferencial, AEA 90364

## What this is

The power network's engine is country-neutral, but its figures are American:
120 V loads, UL 489 trip points, NEC breaker sizes and NEC circuits. The game
moved to Lima, Buenos Aires (v0.10.0). This pass moves every one of those
figures to its Argentine counterpart:

- 220 V loads;
- IEC 60898-1 breaker curves;
- IEC ratings;
- the dev test template laid out to AEA 90364-7-770;
- appliance nameplates as sold in Argentina.

The issue: "Moves every figure above to its Argentine counterpart… Re-fits the
trip model's shape if the IEC points don't map onto the current two-point heat
meter." Planning found that **they do map**: the formula keeps its shape, and
only its two anchor points and the instant trip change.

No Lima building is wired (`WIRING = {}`), so no player sees a difference
today. The change is proven through `simulatePower()` and `validateWiring()`.

## Relevant existing state

Verified against `ashfall.html` at v0.10.2.

- **Breaker constants**, CONFIG/CONSTANTS, lines ~544–572:
  - `BREAKER_T135_MIN = [ { upTo:50, min:60 }, { upTo:Infinity, min:120 } ]`;
  - `BREAKER_T200_MIN`, six bands, 2–10 min;
  - `INSTANT_TRIP_MULTIPLE = 7.5`;
  - `HEAT_COOL_MIN = 30`;
  - `PANEL_DEFAULT_VOLTS = 240`;
  - `STANDARD_BREAKER_RATINGS`, the NEC 240.6(A) list.

  Comments cite UL 489, the NEC, and "120/208 V" apartment buildings.
- **`tripMinutes(rating, f)`** (POWER, ~line 7165): t(f) = T200 ÷ (f − 1)ⁿ,
  with n = ln(T200 ÷ T135) ÷ ln(0.35). The `0.35` is (1.35 − 1) ÷ (2.00 − 1).
  `bandMinutes(bands, rating)` picks a band.
- **`resolvePowerStep()`** (~line 7257) trips a closed breaker instantly when
  `snap.momentary[id] > INSTANT_TRIP_MULTIPLE * net.breakers[id].rating`. The
  heat check (~line 7266) calls `tripMinutes()`.
- **`expandWiring()`** (~line 6981) builds each breaker as `{ id, layer,
  label, rating, volts, device, room, loads }` (circuits add `roles`). A board
  main takes the board's `volts`; a panel main and its feeder take the panel's
  (`layout.main.volts || PANEL_DEFAULT_VOLTS`); a circuit takes its own
  `c.volts`. The schema comment at ~line 6975 says a panel "treats its loads as
  balanced across its two legs": US split-phase wording.
- **POWER SCHEMA → `APPLIANCES`** (~lines 4405–4497). The schema comment says
  `volts` is "120 or 240". Every entry is `volts:120`. The source comments
  cite Champion, Engineer Fix, Kidde, Broan and Frigidaire. The entries:

  | id | watts | start | nameplate |
  |---|---|---|---|
  | `fridge_freezer` | 150 | 525 | 6 A (duty 0.35, cycle 60 min) |
  | `led_light` | `LED_BULB_WATTS` (10) | – | prints watts |
  | `hall_light` | `LED_BULB_WATTS` (10) | – | prints watts (switchless) |
  | `bath_fan` | 36 | – | 0.9 A |
  | `range_hood` | 200 | – | 2.0 A |
  | `smoke_alarm` | 1 | – | 0.04 A (switchless) |
  | `gas_range` | 4 | – | 12 A (switchless) |

  `hall_light` is in no template today.
- **`nameplateWatts(a)`** = `a.volts * a.nameplate.amps`, or `a.watts` when
  `printsWatts`. **`nameplateText(a)`** (~line 10611) prints
  `"<volts> V · <amps> A"` or `"<watts> W"`.
- **`WIRING_TEMPLATES.apartment`** (~lines 4536–4571), an NEC layout:
  - main 100 A;
  - circuits `kitchen1` / `kitchen2` / `bath` (20 A), `lights` / `bedroom`
    (15 A), all `volts:120`;
  - fixtures: fridge, stove, hood, five lights, `bath_fan`, `smoke_alarm`.

  It carries no doors or windows. `WIRING` is `{}`. The comment at ~line 4603
  says the template "stays for the dev seam … until #289 re-bases it".
  `simulatePower()` defaults to `WIRING_TEMPLATES`.
- **`validateWiring()`** (~line 8569) checks:
  - every appliance has a nameplate rated at no less than its watts;
  - every circuit's volts is 120 or 240 (~line 8598);
  - every breaker's rating is in `STANDARD_BREAKER_RATINGS` (~line 8595,
    message "not an NEC 240.6(A) standard size").
- **The meter** (`doMeterTest()`, ~line 6611) reads a circuit's `volts`, so
  it reads 220 once the data does. Nothing else prints a voltage.

### Reference figures this pass depends on

From `docs/canon/reference/Electrical_AR.md`, quoted because a coding session
doesn't read it.

- **Supply:** 220/380 V, 50 Hz. A house is single-phase (AEA 90364-7-770
  §770.4.2, confirmed).
- **IEC 60898-1 thermal points**, the same for curves B, C and D (ABB's table
  and Enel E-BT-004, secondary for the standard):

  | Current | Result |
  |---|---|
  | 1.13 × In | no trip within 1 h (In ≤ 63 A) |
  | 1.45 × In | trip within 1 h (In ≤ 63 A) |
  | 2.55 × In | trip in 1–60 s (In ≤ 32 A), or 1–120 s (In > 32 A) |

- **Magnetic (instant) bands:** B 3–5 × In, C 5–10 × In, D 10–20 × In. At a
  band's high end the trip is under 0.1 s. At its low end it may still take up
  to 45 s (B), 15 s (C) or 4 s (D), for In ≤ 32 A.
- **Ratings:** IEC 60898-1's preferred values are said to be 6, 8, 10, 13, 16,
  20, 25, 32, 40, 50, 63, 80, 100 and 125 A. That's secondary: the standard
  wasn't read, and the list is unconfirmed as complete. The Argentine market
  shows 6, 10, 16, 20, 25, 32 and 40 A.
- **Circuits (AEA 770 Table 770.6.I, confirmed):**
  - IUG (lighting): at most 16 A; lights, fans and extractors, loads ≤ 10 A.
  - TUG (general sockets): at most 20 A; 10 A sockets.
  - TUE (special sockets): at most 32 A.

  Fixed kitchen appliances include fridges, extractor hoods and "cocinas… a gas
  que requieran alimentación eléctrica". Extractors may go on a lighting
  circuit.
- **The standard's own example board** (Annex 770-B, a *Mínimo* home):
  **B 2×10 A (IUG) and B 2×16 A (TUG)**, behind a 30 mA 2×40 A RCD. Every
  circuit breaker in a single-phase home is bipolar.
- **Appliances (researched 2026-09-28, #311):**
  - **Fridge-freezer:**
    - 310–419 kWh a year across 264–389 L class-A models (Patrick manual,
      primary); 310 kWh ÷ 8,760 h ≈ 35 W average;
    - nameplate 0.75 A (fridge) and 1.0 A (freezer) at 220–240 V (Vondom,
      primary);
    - household R600a compressors at 200–220 V, 50 Hz: locked-rotor current
      3.7–8.2 A (Embraco catalogue, primary for Embraco).
  - **LED bulbs:** E27 at 220 V, 9–12 W common; 12 W ≈ 840 lm ≈ a 60 W
    incandescent (secondary).
  - **Extractor hood:** 130–250 W maximum, printed in watts, "Potencia
    máxima 200 Watt" (Longvie, primary).
  - **Gas cooker:** electronic spark ignition and a 220 V oven lamp (≤ 15 W)
    (Longvie, primary). **The ignition's draw and the cooker's electrical
    nameplate are unconfirmed** (#316).
  - **Lima homes have no smoke alarm, and usually no bathroom extractor fan**
    (Tom, first-hand).

## Rules / mechanics

### 1. The heat (delayed) trip: same formula, IEC anchor points

Replace the UL 489 pair with the IEC pair. Decided by Tom: **1.45 × In trips
at 60 min, 2.55 × In at 60 s**, the slowest the standard allows (In ≤ 32 A).

- Constants, CONFIG/CONSTANTS, replacing `BREAKER_T135_MIN` and
  `BREAKER_T200_MIN`:
  - `BREAKER_F_LOW = 1.45` and `BREAKER_F_HIGH = 2.55`: the two anchor
    multiples.
  - `BREAKER_T_LOW_MIN = [ { upTo:Infinity, min:60 } ]`: at 1.45 × In, for
    every rating.
  - `BREAKER_T_HIGH_MIN = [ { upTo:32, min:1 }, { upTo:Infinity, min:2 } ]`:
    at 2.55 × In, 60 s up to 32 A and 120 s above. Both are the slowest the
    standard allows.
  - `BREAKER_F_NO_TRIP = 1.13` and `BREAKER_NO_TRIP_MIN = 60`: the
    conventional non-tripping point, which the curve must respect.

  The standard's 1 h at 1.45× covers In ≤ 63 A. Homes are ≤ 63 A by AEA 770's
  own scope, so the single band covers every rating, with a comment saying
  that ratings above 63 A reuse it unsourced.
- **`tripMinutes(rating, f)`** keeps its form, anchored on the new points:

  ```
  tLow  = bandMinutes(BREAKER_T_LOW_MIN,  rating)
  tHigh = bandMinutes(BREAKER_T_HIGH_MIN, rating)
  n     = ln(tLow / tHigh) / ln((BREAKER_F_HIGH − 1) / (BREAKER_F_LOW − 1))
  t(f)  = tHigh × ((BREAKER_F_HIGH − 1) / (f − 1))ⁿ
  ```

  Write the derivation, not the literal `0.35` or its IEC equivalent. It passes
  exactly through (1.45, tLow) and (2.55, tHigh). Expected values:

  | Rating | n | t(1.13) | t(1.45) | t(2) | t(2.55) | t(3) |
  |---|---|---|---|---|---|---|
  | ≤ 32 A | ≈ 3.311 | ≈ 3,660 min (≈ 61 h) | 60 min | ≈ 4.27 min | 1 min | ≈ 0.43 min |
  | > 32 A | ≈ 2.750 | ≈ 1,825 min (≈ 30 h) | 60 min | – | 2 min | – |

  Both t(1.13) values are well past `BREAKER_NO_TRIP_MIN`, as the standard
  requires.
- The heat meter's behaviour is unchanged: it rises by dt ÷ `tripMinutes()`
  while f > 1, drains by dt ÷ `HEAT_COOL_MIN` otherwise, and trips at 1.
- **These points are balance values, retunable.** The standard gives only
  bounds. Say so in the constants' comment, and cite ABB 2CDC400002D0201 and
  Enel E-BT-004 Table 12 (secondary for IEC 60898-1).

### 2. The instant (magnetic) trip: one multiple per curve

Decided by Tom: **home breakers are curve B**, and the instant trip sits at
**the high end of each curve's band**, where the standard guarantees under
0.1 s. Below it, the heat curve handles the current: the low end of a band
may take up to 45 s, which the heat curve already gives (≈ 2.8 s at 4.9 × In
for ≤ 32 A).

- Replace `INSTANT_TRIP_MULTIPLE` with
  `BREAKER_CURVES = { B:{ instant:5 }, C:{ instant:10 }, D:{ instant:20 } }` and
  `DEFAULT_BREAKER_CURVE = "B"`.
- Every expanded breaker carries a **`curve`**. It is read from an optional
  `curve` on its definition, or `DEFAULT_BREAKER_CURVE` when absent. The
  definitions are: a template circuit, a template `main`, a board, and a
  feeder.
- `resolvePowerStep()`: a closed breaker trips instantly when
  `momentary > BREAKER_CURVES[br.curve].instant × rating`. The comparison stays
  strict (`>`), as today.
- `validateWiring()` reports a breaker whose `curve` isn't a key of
  `BREAKER_CURVES`.

### 3. Volts and ratings

- `PANEL_DEFAULT_VOLTS = 220`. Its comment drops the 240 V and 120/208 V text,
  and says a home is single-phase at 220 V (AEA 770 §770.4.2).
- **The schema comments:**
  - `APPLIANCES.volts` becomes "220: single-phase, the only voltage a load
    uses";
  - the `expandWiring()` note about "two legs" becomes: a single-phase panel's
    current is its loads' total watts ÷ its volts. The same arithmetic, the
    correct reason.
- `validateWiring()`: every circuit's volts must be **220**, replacing
  "120 or 240".
- `STANDARD_BREAKER_RATINGS = [6, 8, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80,
  100, 125]`. The comment says: IEC 60898-1's preferred values as reported
  (secondary, unconfirmed as complete), and the Argentine market shows 6–40 A.
  `validateWiring()`'s message becomes "not an IEC 60898-1 preferred rating".

### 4. Appliances at 220 V

Decided by Tom. Every figure is retunable, and each one's source goes in the
APPLIANCES comment, replacing the US sources.

| id | Change |
|---|---|
| `fridge_freezer` | **watts 100, startWatts 1300, volts 220, nameplate `{ amps:1.0 }`**. dutyCycle 0.35, cycleMinutes 60, leftOnChance 0.99 and the readout stay. |
| `led_light` | volts 220. `LED_BULB_WATTS` stays 10; its comment cites the 9–12 W E27 bulbs sold at 220 V. |
| `hall_light` | volts 220. Otherwise unchanged; it stays defined for a later common area. |
| `range_hood` | volts 220. watts 200 stays. **nameplate `{ printsWatts:true }`**, since Longvie prints hoods in watts. |
| `gas_range` | volts 220. watts 4 stays, marked unconfirmed for Argentina. **nameplate `{ amps:0.1 }`, a placeholder** (see below). |
| `bath_fan` | **removed**. Lima homes usually have none (Tom). |
| `smoke_alarm` | **removed**. Lima homes have none (Tom). |

- **`fridge_freezer`, derived (say so in the comment):**
  - **running:** 100 W at the kept 0.35 duty cycle is ≈ 307 kWh a year,
    matching the 264 L class-A model's 310 kWh (Patrick, primary);
  - **starting:** 1,300 W is 6 A × 220 V, the middle of the 3.7–8.2 A
    locked-rotor range (Embraco, primary for Embraco; which compressor
    Argentine fridges carry is unconfirmed);
  - **nameplate:** 1.0 A, from Vondom's freezer at 220–240 V (primary for
    Vondom).
- **`gas_range`'s nameplate is a placeholder** (Tom): 0.1 A at 220 V (22 W),
  which covers the 4 W standby and sits above it, as `validateWiring()`
  requires. The comment says, in so many words, that it is **unconfirmed and
  awaits #316**. The standby watts' US source (Engineer Fix, "generally less
  than 5 watts") is kept in the comment as the only figure there is, marked US.

### 5. The dev test template: AEA 770's example board

`WIRING_TEMPLATES.apartment` keeps its **name**, because `simulatePower()`
and its comment name it, and its **roles**: living, kitchen, bathroom,
bedroom, balcony, with every role mapping onto one room for a one-room unit.
Its layout becomes AEA 770 Annex 770-B's example:

```js
apartment: {
  main: { rating:32 },
  circuits: [
    { key:"lights",  label:"LIGHTS",  rating:10, volts:220, roles:["living", "kitchen", "bathroom", "bedroom", "balcony"] },
    { key:"sockets", label:"SOCKETS", rating:16, volts:220, roles:["kitchen"] }
  ],
  fixtures: [
    { key:"fridge",        appliance:"fridge_freezer", circuit:"sockets", role:"kitchen", containers:["fridge", "freezer"] },
    { key:"stove",         appliance:"gas_range",      circuit:"sockets", role:"kitchen", containers:["stove"] },
    { key:"hood",          appliance:"range_hood",     circuit:"lights",  role:"kitchen" },
    { key:"light_kitchen", appliance:"led_light",      circuit:"lights",  role:"kitchen" },
    { key:"light_living",  appliance:"led_light",      circuit:"lights",  role:"living" },
    { key:"light_balcony", appliance:"led_light",      circuit:"lights",  role:"balcony" },
    { key:"light_bath",    appliance:"led_light",      circuit:"lights",  role:"bathroom" },
    { key:"light_bedroom", appliance:"led_light",      circuit:"lights",  role:"bedroom" }
  ]
}
```

- **Circuits:** B 10 A for lighting (IUG) and B 16 A for sockets (TUG), both
  curve B by default. The hood is on the lighting circuit, which AEA 770
  §770.7.1 c allows for extractors.
- **Main:** **32 A**, the largest main OCEBA allows a Tarifa 1 supply. It's a
  test figure, and #305 decides a real house's board.
- **Labels are English** (game-text rule, #310), as hand-written on the board.
  Their wording is functional UI text, retunable.
- **The comment above it** is replaced: it cites AEA 770's Annex 770-B example
  and §770.7.1, and says the template is for the dev seam. **Drop** the NEC
  text and the "until #289 re-bases it" line at the `WIRING` comment (~line
  4605).

### 6. Comments citing US rules

Every comment citing UL 489, the NEC, US brands' nameplates or °F in the
sections touched is replaced with its Argentine source, as above. Comments
elsewhere that describe history are left alone.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

- **Constant names.** The names above are recommended, not required. Any
  clear names will do, as long as the anchor multiples and times are each
  defined once and `tripMinutes()` derives `n` from them.
- **Where the no-trip check lives.** Recommended: `validateWiring()` reports
  any breaker rating for which `tripMinutes(rating, BREAKER_F_NO_TRIP)` falls
  below `BREAKER_NO_TRIP_MIN`. It's a guard for a later retune. Checking it
  once in the Validation section instead is acceptable; say which.
- **How `curve` reaches a breaker in `expandWiring()`**, for example a small
  helper that resolves `def.curve || DEFAULT_BREAKER_CURVE`.

## Data / schema changes

- **No PLAYER STATE changes.** `state.power` is keyed by breaker and load ids.
  The dev template's circuit and load ids change, but no save holds them,
  because `WIRING` is empty.
- **POWER SCHEMA:**
  - an optional `curve` on template circuits, template `main`, board and
    feeder definitions;
  - every expanded breaker gains `curve`;
  - `APPLIANCES.volts` is 220;
  - `bath_fan` and `smoke_alarm` are removed.
- **No item, room, container or exit schema changes.**

## In scope

- [ ] IEC heat-trip anchors and the generalised `tripMinutes()` (§1).
- [ ] Per-curve instant trip, `curve` on every breaker, and the validation for
      it (§2).
- [ ] 220 V default, the schema wording, the circuit-volts check, and the IEC
      ratings list (§3).
- [ ] APPLIANCES re-based, and two entries removed (§4).
- [ ] `apartment` re-based to AEA 770's example (§5).
- [ ] US-citing comments in the touched sections replaced (§6).
- [ ] `validateWiring()` reports no problems (its `unwired` warning is
      expected while `WIRING` is empty).

## Explicitly out of scope

- **The diferencial (RCD).** It enters with #305, when the first real house
  is wired: switchable, never tripping on overcurrent. Its leakage trip is
  #247. Don't add an RCD layer or device here.
- **The electric water heater and the house pump** as loads: with #305. The
  pump refilling the roof tank is #317.
- **Wiring any Lima building**, the meter pillar and outdoor main, and board
  placement: #305–#309, under #250.
- **Old installations** (fuses, *tapones*, no RCD): #305/#306.
- **Plugs, cords and inlets** (IRAM 2073): #244, #246. **Shock:** #247.
- **The gas cooker's real nameplate:** #316. **The garrafa and fuel:** #287,
  #239.
- **Bipolar breakers.** They switch both poles, and the power budget doesn't
  model poles. No label or display change.
- **Any change to what the player sees.** Nothing is wired, so there is none.

## Sections touched

- **CONFIG/CONSTANTS:** the breaker constants.
- **WORLD DATA → POWER SCHEMA:** `APPLIANCES`, `WIRING_TEMPLATES`, the
  comments. These are the mechanic's definition data, not instance data.
- **SURVIVAL / TIME SIMULATION → POWER:** `tripMinutes()`,
  `resolvePowerStep()`'s instant check, `expandWiring()`'s `curve`.
- **DEV:** `validateWiring()`.

No rendering changes. `nameplateText()` and the meter already read the data.

## UI changes

None visible in play, since no building is wired. In a dev run, the
Electrical view's nameplate and the meter read 220 V.

## Validation (for the changelog)

Check the §1 table: `tripMinutes(16, 1.45)` = 60, `tripMinutes(16, 2.55)` = 1,
`tripMinutes(40, 2.55)` = 2, and `tripMinutes(r, 1.13)` > 60 for every
standard rating.

Then run `ashfallDev.simulatePower()` on a one-unit test building using
`apartment`, and show:

1. **Idle kitchen:** no trips; the fridge cycles.
2. **Fridge start:** the fridge starts at ≈ 5.9 A momentary on `sockets`
   (1,300 W ÷ 220 V), under the 80 A instant trip (B16 × 5). No trip.
3. **Instant trip:** a test appliance drawing more than 80 A momentary on
   `sockets` trips it `"instant"`.
4. **Heat trip at 2×:** a test load of 7,040 W (2 × 16 A × 220 V) on
   `sockets` trips it by heat in ≈ 4–5 simulated minutes.
5. **No trip at 1.13×:** a load of 1.13 × 16 A × 220 V (≈ 3,978 W) doesn't
   trip within 60 minutes.

`validateWiring()`: no problems. Cite `git diff origin/main...HEAD --
ashfall.html` for everything else untouched.

## Dependencies / issue linkage

- **Fulfils #289.**
- **Unblocks:** #305 (wiring the row house), and the re-specs of #244, #246
  and #247.
- **Research this used:** #286 (closed) and #311 (closed by the planning
  pull request that adds these figures).
- **Deferred and already filed:** #316 (the cooker nameplate), #317 (the pump
  fills the tank). Anything else this pass defers is filed at the wrap.

## Open questions for Tom

None. Every design call above was made by Tom on 2026-09-28.

## After implementation

Open a pull request carrying the version bump (PATCH) and a new
`CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`. The entry names this handoff by
path (`Implements: handoffs/power-rebase-argentina.md`) and records the
implementation choices above. Move this file to `handoffs/archive/` in the
same pull request, and close #289 with `Closes #289`.
