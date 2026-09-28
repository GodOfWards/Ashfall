# Ashfall Handoff — Home breakers on curve C, and the gas range's real rating

Current shipped version: v0.10.3
Implied version-change type: PATCH (one constant, one appliance's data, and a
  third nameplate form; no persistent state, and power definitions aren't
  saved)
Issues: #321 — Home breakers default to curve C; #327 — The gas range at
  220 V: 0 W while idle, a 16 W nameplate

## What this is

Two small corrections to the power figures #289 shipped in v0.10.3, both
learned after its handoff was in use:

- **#321.** Real Lima homes mostly have **curve C** breakers (Tom, first-hand),
  not the curve B that #289 took from AEA 770's worked example. The default
  curve becomes C.
- **#327.** The gas range still carries a US standby draw (4 W) and #289's
  placeholder nameplate (0.1 A). Argentine cookers' real figures replace both:
  **0 W while idle**, and a **16 W nameplate printed in watts**. That needs a
  nameplate form that prints its own watts, separate from the draw.

No building is wired yet (`WIRING = {}`), so no player sees either change. The
proof is `simulatePower()` and `validateWiring()`.

## Relevant existing state

Verified against `ashfall.html` at v0.10.3.

- **CONFIG/CONSTANTS, lines ~563–570:**

  ```js
  const BREAKER_CURVES = { B:{ instant:5 }, C:{ instant:10 }, D:{ instant:20 } };
  const DEFAULT_BREAKER_CURVE = "B";
  ```

  The comment above them ends "Home breakers are curve B: a breaker without
  its own `curve` is DEFAULT_BREAKER_CURVE."
- **Where the default applies.** `breakerCurve(def)` (~line 6987) returns
  `def.curve || DEFAULT_BREAKER_CURVE`. It's used for the board main, the
  panel main, feeders and circuits in `expandWiring()` (~lines 7006–7033).
  **No definition sets its own `curve` today**, the dev `apartment` template
  included, so every breaker takes the default.
- **The heat curve is the same for B, C and D** (IEC 60898-1). Only the
  instant trip changes: `resolvePowerStep()` (~line 7272) trips a closed
  breaker when its momentary current exceeds
  `BREAKER_CURVES[br.curve].instant × rating`.
- **`APPLIANCES.gas_range`** (~line 4502):

  ```js
  gas_range: { name:"Gas range", watts:4, volts:220, switchless:true, nameplate:{ amps:0.1 } }
  ```

  The comments at ~lines 4470–4478 (draw) and ~4487–4489 (nameplate) call
  the 4 W a US standby source (Engineer Fix) and the 0.1 A a placeholder
  awaiting #316.
- **The nameplate has two forms today** (POWER SCHEMA comment, ~lines
  4440–4449):
  - `{ amps }`, printed "`<volts>` V · `<amps>` A";
  - `{ printsWatts:true }`, printed as the entry's own `watts`.

  They're read in two places:
  - `nameplateWatts(a)` (~line 4507): `a.watts` for `printsWatts`,
    `a.volts * n.amps` otherwise, or null;
  - `nameplateText(a)` (~line 10632): "Nameplate: " plus the printed form.

  `validateWiring()` (~lines 8603–8604) reports an appliance with no nameplate,
  or one rated below its own `watts`.
- **What reads the stove's power.** `stoveLighting()` (~line 7640) asks
  `containerPowered()`: the load's switch and its circuit being live, **not
  its watts**. A 0 W load is still powered and still counted as drawing; it
  adds 0 to its breakers' currents (`powerSnapshot()`, ~line 7235). So the
  stove lighting itself with power (#259) is unaffected. The stove-timer
  comment (~line 7967) says "whose standby draw is `gas_range`"; that wording
  goes stale.

### Reference figures this pass depends on

From `docs/canon/reference/Electrical_AR.md`, quoted because a coding session
doesn't read it.

- **Curve in homes: mostly C** (Tom, first-hand, 2026-09-28). The retail
  two-pole breakers sold in Argentina are curve C too (Schneider Easy9 2P).
  AEA 770's worked example uses B; that's the standard's illustration, not
  what's installed. IEC 60898-1's magnetic band for C is 5–10 × In.
- **A cooker's electrical rating** (Domec's manual, Tabla 3, "Consumo
  eléctrico máximo", 220 V, 50 Hz; primary for the maker):

  | Appliance | Max electrical power |
  |---|---|
  | Cooker with oven light | 15 W |
  | Cooker with oven light and ignition | **16 W** |
  | Hob, ignition only | 1 W |

  So the spark ignition draws about 1 W, only while the button is held. **A
  basic cooker lists no standby draw**: no clock or display. Orbis's C9500
  lists its oven lamp at 25 W (primary).

## Rules / mechanics

### 1. The default curve is C (#321)

- `DEFAULT_BREAKER_CURVE = "C"`.
- Its comment's last sentence becomes: home breakers are curve C, as Lima's
  mostly are (Tom, first-hand) and as the two-pole breakers sold in Argentina
  are. AEA 770's worked example uses B. A breaker without its own `curve` is
  `DEFAULT_BREAKER_CURVE`.
- **Effect:** the instant trip moves from 5× to **10×** the rating: a B16's
  80 A becomes a C16's **160 A**. The heat curve is unchanged. `BREAKER_CURVES`
  is unchanged.

### 2. The gas range draws nothing while idle (#327)

- `gas_range.watts: 0`. The power model counts `watts` continuously while a
  load is powered, and a basic cooker has no continuous draw. The spark's
  second of about 1 W is too brief for the model, and `startWatts` is a
  motor's start surge, not this.
- It stays `switchless`. It stays a powered load, and #259's rule is
  unchanged: it lights itself when powered, and by hand otherwise.
- Its comment replaces the US standby source with Domec's figures (above),
  and says the draw is 0 because the cooker has no clock or display. The oven
  lamp (15–25 W while lit) is left unmodelled with the oven (#259).

### 3. A nameplate that prints its own watts (#327, Tom: option b)

- **A third nameplate form**, rated in watts independently of the load's draw.
  Recommended shape: **`{ watts }`**, e.g. `nameplate:{ watts:16 }`.
  - `nameplateWatts(a)` returns `n.watts` for it.
  - `nameplateText(a)` prints "Nameplate: 16 W".
  - `validateWiring()`'s existing check (rated ≥ `a.watts`) holds unchanged:
    16 ≥ 0.
- `gas_range.nameplate: { watts:16 }`. Its comment cites Domec, Tabla 3 (16 W
  with oven light and ignition), and drops "placeholder" and "unconfirmed".
- **The POWER SCHEMA comment** for `nameplate` lists all three forms:
  - `{ amps }`;
  - `{ printsWatts:true }`, which prints the entry's own `watts`, as a bulb's
    base does;
  - `{ watts }`, a rating printed in watts that isn't the draw, as a cooker's
    plate is.

  Keep "never a second copy of either" in meaning: `{ watts }` is not a copy
  of the draw, it's a different figure.
- **The stove-timer comment** (~line 7967): "whose standby draw is
  `gas_range`" becomes, for example, "whose electrics are `gas_range`", or
  similar. It's the timer's comment, not its behaviour.

## Design decisions to make during implementation

Record which was picked in the changelog's Notes/assumptions.

- **The third form's shape.** `{ watts }` is recommended. Any clear shape will
  do, as long as `nameplateWatts()` and `nameplateText()` are its only readers
  and `printsWatts` keeps its meaning.
- **Whether `validateWiring()` also reports a nameplate carrying more than
  one form** (e.g. both `amps` and `watts`). Optional; it's a guard.

## Data / schema changes

- **No PLAYER STATE changes.**
- **POWER SCHEMA:**
  - `nameplate` gains a third form, `{ watts }`;
  - `gas_range` is `watts:0, nameplate:{ watts:16 }`;
  - `DEFAULT_BREAKER_CURVE` is "C".
- No item, room, container or exit schema changes.

## In scope

- [ ] `DEFAULT_BREAKER_CURVE = "C"` and its comment (§1).
- [ ] `gas_range` at 0 W, with its comment (§2).
- [ ] The `{ watts }` nameplate form, read by `nameplateWatts()` and
      `nameplateText()`, and the schema comment (§3).
- [ ] `gas_range.nameplate: { watts:16 }` and its comment; the stove-timer
      comment's wording (§3).

## Explicitly out of scope

- **Wiring any building** (#305) and the diferencial (with #305).
- **The oven and its lamp** (#259).
- **`STANDARD_BREAKER_RATINGS`.** Its 8 A is disputed between sources
  (`Electrical_AR.md`), but nothing is decided; leave the list alone.
- **Any other appliance's figures.**
- **Any change to the heat curve or `BREAKER_CURVES`.**

## Sections touched

- **CONFIG/CONSTANTS:** `DEFAULT_BREAKER_CURVE`.
- **WORLD DATA → POWER SCHEMA:** `APPLIANCES.gas_range`, the `nameplate`
  schema, and `nameplateWatts()`. This is the mechanic's own definition data,
  not instance data.
- **RENDERING:** `nameplateText()`, one more printed form.
- **DEV:** nothing new; `validateWiring()` may gain the optional guard.
- **Comments only:** the stove timer (ACTIONS).

## UI changes

None in play, since nothing is wired. In a dev run, the Electrical view's
stove row reads "Nameplate: 16 W" instead of "Nameplate: 220 V · 0.1 A".

## Validation (for the changelog)

- `validateWiring()`: no problems.
- `ashfallDev.simulatePower()` on a one-unit test building using `apartment`:
  1. **Every expanded breaker's `curve` is "C".**
  2. **Fridge start:** the fridge starts at ≈ 5.9 A momentary on `sockets`
     (1,300 W ÷ 220 V), under the 160 A instant trip (C16 × 10). No trip.
  3. **Instant trip:** a test appliance drawing more than 160 A momentary on
     `sockets` trips it `"instant"`. One drawing 100 A momentary, over B's old
     80 A but under C's 160 A, **doesn't** trip instantly.
  4. **Heat trip unchanged:** a 7,040 W test load (2 × 16 A × 220 V) on
     `sockets` still trips by heat on the 5th one-minute step.
  5. **The stove:** it is powered and drawing, and adds 0 A to `sockets`.
     `nameplateWatts()` returns 16; `nameplateText()` prints
     "Nameplate: 16 W".
- `git diff origin/main...HEAD -- ashfall.html` shows nothing else touched.

## Dependencies / issue linkage

- **Fulfils #321 and #327.** Their pull request says `Closes #321` and
  `Closes #327`.
- Unblocks nothing directly. #305 (wiring the row house) will wire its
  circuits on curve C by default.

## Open questions for Tom

None. Curve C (#321) and the stove's figures and nameplate form (#327, option
b) were decided by Tom on 2026-09-28.

## After implementation

Open a pull request carrying the version bump (PATCH) and a new `CHANGELOG.md`
entry per `CHANGELOG_GUIDE.md`. The entry names this handoff by path
(`Implements: handoffs/curve-c-and-stove-nameplate.md`) and records the
implementation choices above. Move this file to `handoffs/archive/` in the
same pull request, and close #321 and #327.
