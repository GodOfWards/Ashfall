# Ashfall Handoff — Performance benchmark and budget

Current shipped version: v0.10.10
Implied version-change type: PATCH
Issue: #371 — Performance benchmark and budget — a late-game scenario, three timings, checked in CI

## What this is

Nothing measures the game's speed, so a slowdown is found by playing. This
pass adds a benchmark: a fixed, busy scenario built by code, five timings
taken on it, a page that runs it (`ashfall.html?bench`), and a CI job that
**fails a pull request that makes the game slower than `main`** and **warns
when a timing is over its budget**. It changes nothing in play.

It comes before #372 (the event scheduler), #373 (ageing and batteries
worked out when read) and #369 (power without per-minute resolving), so those
three have a number to beat.

## Relevant existing state

Verified against `ashfall.html` at v0.10.10.

**Boot and the dev seam.** The IIFE ends with the boot (`refreshPower()`,
`stampMissingAges()`, a log line, `render()`), then the dev seam:
`window.ashfallDev = { validateItemRegistry, …, simulatePower }`. Its comment
says it is "read-only reporting helpers, nothing that writes game state, and
nothing else belongs on it." The benchmark writes game state, so it must not
go on `ashfallDev`. The validators and `simulatePower()` live in PERSISTENCE,
between `applyLoadedData()` and `doRestart()`.

**Restart.** `doRestart(seed)` rebuilds everything: `state =
makeDefaultState(seed)`, `state.electricalRules = nextElectricalRules()`,
`world = makeDefaultWorld()`, doors, windows, `refreshPower()`,
`stampMissingAges()`, `_uidCounter = 1`, clears `#log`, logs the wake-up line,
`render()`. It takes about as long as the boot (around a second).

**Saving.** Nothing saves automatically and nothing loads automatically.
`doSaveLocal()` (the Save button) is the only writer of `SAVE_KEY` in
`localStorage`. `serializeGame()` returns the JSON and writes nothing; it
calls `savedRoomState()`, which rebuilds the world to diff against, and that
is most of its cost.

**Time.**
- `minutesSinceCollapse()` is `START_DAYS_AFTER_COLLAPSE * MINUTES_PER_DAY +
  state.totalMinutes`; `START_DAYS_AFTER_COLLAPSE` is 2.
- The grid is up until `POWER_FAILS_MIN` (day `POWER_FAILS_DAY` = 21, 22:00),
  and `gridUp()` reads `GRID_UP_SPANS`.
- `CLOCK_EVENTS` holds one event, the siren, at `POWER_FAILS_MIN +
  SIREN_AFTER_FAIL_MIN`, marked `wakes`. It fires in the step that crosses it,
  so setting `state.totalMinutes` directly fires nothing.
- `advanceTime(min)` runs `runAwakeStep()` in steps of at most one minute:
  hunger and thirst, `applyWorldTicking()`, `recoveryStep()`.
- `applyWorldTicking()` runs, each step: `stepPower()`, `refillTanks()`,
  `ageFood()`, a `forEachItemList()` walk for battery drain, and
  `tickStoveTimers()` (every container in town). Then, over every room,
  `heatActive` rooms cook and burn down. Then `fireClockEvents()`.

**Sleep.**
- `doSleep()` sleeps until Energy reaches `sleepEnergyCeiling()` (`100 −
  fatigue`), at `SLEEP_ENERGY_RATE` (10 per hour).
- It stops early if `wokenUp` is set.
- It ends with `render()`.
- `sleepAvailable()` needs `sleepOffCooldown()` (`lastWakeMinute` starts at
  −9999) and Energy below the ceiling.
- So Energy 20 and Fatigue 0 give a sleep of exactly 480 minutes.

**Power (SIMULATION → POWER, "POWER RUNS").**
- A step resolves only the busy buildings: those with an entry in
  `state.power` under one of their ids, a tank float that isn't full, or
  default-on loads that could trip (`untouchedTrippers()`).
- `POWER_INDEX = powerIndex(POWER_NET, APPLIANCES)` lists
  `POWER_INDEX.buildings` in network order. There are 429, every one with
  loads, and `POWER_INDEX.sub[b].loads` holds each building's loads.
- `setSwitchIn(power, seed, loadId, appliance, on)` stores an entry only when
  `on` differs from the rolled default (`switchOnIn()`), and does nothing for
  a `switchless` appliance.
- `refreshPower()` recomputes `powerNow` from `state.power`.

**Containers and items.**
- `doOpenContainer(room, container)` rolls a container once:
  `rolledLootFor(state.seed, roomId, container)`, then `stampAges(it,
  container, roomId)` and `addToList(container.items, it)` for each item, then
  `spawnRolled = true` and `lastRolledMinute = state.totalMinutes`.
- It uses `state.currentRoom` as the room id, so the benchmark repeats those
  steps with the container's own room id instead of calling it.
- `stampAges()` reads `minutesSinceCollapse()`, so the clock must be set
  before rolling.
- `state.enteredBuildings` lists the building ids the player has entered.

**Stoves and devices.**
- `roomStove(room)` is a room's `device`+`heat` container, or null.
- A lit stove is `room.heatActive = true` with no `fireMinutesLeft`, so it
  burns until turned off.
- A stove timer is `timerMinutes` on the stove container, counted down by
  `tickStoveTimers()`.
- `portable_radio` in `ITEM_REGISTRY` has `on:false`, time-mode `durability`
  and `drainRate: 100/2880` (48 hours).

**CI.** `.github/workflows/` holds `docs-check.yml` (Python 3.12,
`.github/scripts/docs_check.py`) and `version-changelog.yml`. The latter
gates on `ashfall.html` changing with `git diff --name-only "$BASE_SHA"
"$HEAD_SHA" | grep -qx 'ashfall.html'`. `docs_check.py` fails when a
backticked function (`name()`) or constant (`UPPER_CASE`) in `docs/`,
`CLAUDE.md`, `README.md` or the templates doesn't exist in `ashfall.html`.

**Measured in planning** (headless Chromium in a session container, one run
each, this scenario built from a hand-injected copy of v0.10.10):

| Timing | Result |
|---|---|
| 8-hour sleep | 5.4 s |
| 10-minute action and redraw | 173 ms |
| `render()` | 4.4 ms |
| `serializeGame()` | 353 ms |
| Item rows rolled | 4,262 |

These figures are far over budget, which is why the budget warns rather than
fails (#376).

## Rules / mechanics

### The bench page

- **Bench mode** is on when the page's URL has a `bench` query parameter
  (`new URLSearchParams(location.search).has("bench")`), read once at boot
  into a UI-only flag that is never saved.
- **In bench mode, `doSaveLocal()` refuses.** It logs `The benchmark page
  doesn't save.` (class `"warn"`) and writes nothing. The bench page holds a
  fabricated town and shares the real game's `localStorage`. Load, Export and
  Import are untouched.
- **The benchmark runs after the boot's first paint** (scheduled with
  `setTimeout(…, 0)` after the boot's `render()`), so the page shows
  something while it runs.
- **Its result goes on `window.ashfallBenchResults`**, set once, when the
  benchmark ends. It is also written to the log, one `"sys"` line per timing
  in the form `Sleep 480 min: median 5420.8 ms (5 runs)`, plus one line for
  the scenario counts and one for boot. A benchmark that throws sets
  `window.ashfallBenchResults = { error: <message> }` and logs it.
- **Not on `ashfallDev`.** Add one sentence to the dev seam's comment saying
  that the benchmark writes state, and so runs only on a `?bench` page.

### The scenario

Built by `benchScenario()`, a new function, on a fresh restart, in this order.
Every count and value below is a named constant in the bench code, and each
is a judgment call, retunable.

1. `doRestart(BENCH_SEED)`, a fixed seed. Then set `state.electricalRules =
   "detailed"` explicitly, because a restart otherwise inherits the Options
   choice.
2. **Clock:** set `state.totalMinutes` so that `minutesSinceCollapse()` is
   `BENCH_DAY * MINUTES_PER_DAY`, with `BENCH_DAY` = 20. That is 08:00 on
   day 20, grid up, about 38 hours before `POWER_FAILS_MIN`.
3. **Touched buildings:** take the first `BENCH_BUILDINGS` (200) of
   `POWER_INDEX.buildings`. For each one:
   - find the first load in `POWER_INDEX.sub[b].loads` whose appliance isn't
     `switchless`;
   - set its switch to the opposite of `switchOnIn()`, through
     `setSwitchIn()`, so an entry is stored and the building is busy;
   - push the building id onto `state.enteredBuildings` if it isn't there.
4. **Explored:** for every room whose `buildingId` is one of those 200, roll
   each container with `spawnPools` and not `spawnRolled`, by the three steps
   `doOpenContainer()` takes, using that room's id. This comes to about 4,260
   item rows.
5. **Stoves:** the first `BENCH_STOVES` (2) rooms, in `roomIds()` order,
   among those 200 buildings, that have a `roomStove()`: set `heatActive =
   true` and the stove's `timerMinutes = BENCH_STOVE_TIMER_MIN` (600, longer
   than any timed window).
6. **Radios:** `BENCH_RADIOS` (3) `portable_radio` items from
   `itemFromRegistry()`, with `on = true`. One goes in `state.inventory.items`;
   the others go on the floors of the first two rooms, in `roomIds()` order,
   of the 200 buildings.
7. **Vitals:** Energy 20, Fatigue 0, everything else as the restart left it.
   The player stays in the restart's start room.
8. `refreshPower()`.

It returns the counts `{ buildings, rowsRolled }` for the report.

### The timings

`performance.now()` around each timing. For the two that advance time, each
run gets a freshly built scenario, and the build is not timed. Every timing
has 1 warm-up run, discarded, then `BENCH_RUNS` (5) measured runs. Report
each timing's median and its runs, in milliseconds.

| Key | What is timed | Budget (CI warning) |
|---|---|---|
| `sleep` | `doSleep()`, the player's own tap, including its `render()` | 200 |
| `action` | `advanceTime(BENCH_ACTION_MIN)` (10) then `render()` | 30 |
| `render` | `render()` alone, repeated on one built scenario | 16 |
| `save` | `serializeGame()` alone, repeated on one built scenario; the string is discarded | none |
| `boot` | `performance.now()` read right after the boot's `render()`, before the benchmark starts: one sample per page load | none |

- **The sleep checks itself.** After each run, if `state.totalMinutes`
  didn't advance by exactly 480 (within `TICK_EPSILON`), or `wokenUp`
  interrupted it, the benchmark fails with an error naming the cause. A future
  clock event inside the window must not pass as a fast sleep.
- **The action** is a 10-minute advance plus a redraw, not a `doMove()`: no
  exit is exactly 10 minutes long, and this is the same cost.
- The budgets live in the CI script (below), not in the page. The page only
  measures, because a phone's figures aren't comparable to the reference
  runner's.

`window.ashfallBenchResults` shape:
`{ version, seed, scenario:{ buildings, rowsRolled }, boot, sleep:{ median,
runs:[…] }, action:{…}, render:{…}, save:{…} }`, where `version` is
`GAME_CONFIG.VERSION`.

### The CI job

New workflow `.github/workflows/performance.yml`, named **Performance**, with
the script `.github/scripts/perf_check.py`.

- **Triggers:** `pull_request` into `main`, types `opened`, `synchronize`,
  `reopened`, `labeled` and `unlabeled`, so adding or removing the label
  re-runs it.
- **Gate:** exit 0 at once unless `ashfall.html` changed between base and
  head, with the same test `version-changelog.yml` uses.
- **Setup:**
  - `actions/checkout@v4` with `fetch-depth: 0`;
  - `actions/setup-python@v5` with 3.12;
  - `pip install playwright==<pinned>`, then `python -m playwright install
    --with-deps chromium`.

  Record the pinned version in the changelog. There is no `package.json`: the
  game stays dependency-free.
- **Inputs:** `BASE_SHA`, `HEAD_SHA`, and `PERF_ACCEPTED: ${{
  contains(github.event.pull_request.labels.*.name, 'perf-accepted') }}`.
- **Base and head:**
  - Write `git show "$BASE_SHA:ashfall.html"` to a temp file. The head is the
    checkout.
  - If the base file has no bench mode (it lacks the string
    `ashfallBenchResults`), time the head only, report it, check budgets, and
    pass. This is the case for this pass's own pull request.
- **Runs:**
  - Load each side's page as a `file://` URL with `?bench`, in headless
    Chromium, `PAGE_LOADS` (3) times per side, interleaved: head, base, head,
    base, head, base. A runner that slows part-way through then slows both
    sides.
  - Wait for `window.ashfallBenchResults`, with a timeout of `PAGE_TIMEOUT_S`
    (600). A timeout or an `error` result fails the job.
  - Pool each timing's measured runs across a side's page loads (15 each),
    and compare medians.
- **Regression (fails):** for each of `sleep`, `action`, `render` and `save`,
  a regression is `head > base × (1 + REGRESSION_TOLERANCE)` **and** `head −
  base > REGRESSION_FLOOR_MS`, with `REGRESSION_TOLERANCE` = 0.25 and
  `REGRESSION_FLOOR_MS` = 2. The floor keeps a millisecond of noise on
  `render` from tripping it. Both values are retunable.
  - A regression prints `::error::` and the job exits 1.
  - With `PERF_ACCEPTED` true it prints `::warning::` instead, saying the
    regression was accepted by label, and the job passes.
  - `boot` is reported, never compared: it varies too much.
- **Budget (warns):** `BUDGET_MS = { sleep: 200, action: 30, render: 16 }`.
  A head median over its budget prints `::warning::`. It never fails (#376).
- **Report:** a Markdown table in `$GITHUB_STEP_SUMMARY`, with one row per
  timing: base median, head median, change in %, budget, and verdict (ok /
  over budget / regression / accepted). Below it go boot for each side and
  each side's scenario counts, so a change to spawn pools that moves
  `rowsRolled` explains its timing change.
- **Job timeout:** `timeout-minutes: 30`. At today's figures the job takes
  about five minutes. #372 will make it much faster.

Keep the budgets, the tolerance, the floor, the page count and the timeout as
named constants at the top of `perf_check.py`. That is their one home.

### Documentation

- **`docs/02-code-practices.md`, Performance, principle 3:** add that costs
  are measured by the benchmark: open `ashfall.html?bench`, or read the
  Performance job's summary on a pull request. Its budgets and regression
  tolerance live in `.github/scripts/perf_check.py`. **Name the script's
  path, not its constants:** `docs_check.py` fails on a backticked
  `UPPER_CASE` name that isn't in `ashfall.html`.
- **`docs/03-workflow.md`, The wrap:** add a short paragraph after the list.
  - The Performance check fails a pull request that makes the sleep, the
    action, `render()` or `serializeGame()` slower than `main` beyond its
    tolerance.
  - Only Tom applies the `perf-accepted` label, judging the slowdown against
    the handoff's Costs section. A session never applies it.
  - A coding session whose pull request trips the check says, in the pull
    request, what the handoff's Costs predicted and what was measured.
- No systems doc: this isn't a game system.

## Design decisions to make during implementation

- **Where the bench code sits.** Recommended: beside `simulatePower()` in
  PERSISTENCE, with the `?bench` check and the scheduling at the end of the
  IIFE, after the dev seam. If it becomes a named sub-block, the ARCHITECTURE
  comment gets a line. Record the choice in the changelog.
- **The pinned Playwright version.** Use the latest at implementation, and
  record it in the changelog.
- **`BENCH_SEED`'s value.** Any fixed integer; record it.

## Data / schema changes

None. Bench mode is a UI-only flag, never saved.

## Costs

Nothing per game minute or per event. One URL read at boot. In bench mode the
page is busy for as long as the benchmark takes: about 40 s on a desktop at
today's figures, and minutes on a slow phone.

## In scope

- Bench mode, the Save refusal, `benchScenario()`, the five timings and
  `window.ashfallBenchResults`, as above.
- `.github/workflows/performance.yml` and `.github/scripts/perf_check.py`.
- The two doc edits above, and the one-sentence addition to the dev seam's
  comment.

## Explicitly out of scope

- Making anything faster: #372, #373 and #369.
- A budget overrun failing the job: #376.
- A second scenario after the grid fails. Considered and not wanted: power
  costs little then, so it would measure less.
- Running a sleep in chunks so the page repaints. That's a UI change of its
  own; not filed.
- Creating the `perf-accepted` label in the repository. Tom creates it when
  first needed; a missing label simply means no waiver.

## Sections touched

- PERSISTENCE: the bench code, and the Save refusal in `doSaveLocal()`.
- The end of the IIFE: the `?bench` check and the dev seam's comment.
- PLAYER STATE's UI-only flags: the bench-mode flag.
- Outside the game: `.github/workflows/performance.yml`,
  `.github/scripts/perf_check.py`, `docs/02-code-practices.md` and
  `docs/03-workflow.md`.

## Systems docs

None to read; none to write.

## UI changes

None in normal play. On a page opened with `?bench`:
- the log fills with the benchmark's results;
- Save refuses with `The benchmark page doesn't save.`

## Dependencies / issue linkage

Closes #371. Gives #372, #373 and #369 their measure, and makes #376
possible. Nothing is expected to be deferred.

## Open questions for Tom

None.
