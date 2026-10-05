#!/usr/bin/env python3
"""The Performance check (docs/02-code-practices.md, Performance). Run from
the repository root by .github/workflows/performance.yml, which runs it only
when ashfall.html changed. Exits 1 on a failure.

It opens the game's benchmark page (ashfall.html?bench) in headless Chromium,
PAGE_LOADS times for the pull request's head and as many for its base,
interleaved, so a runner that slows part-way through slows both sides. Each
load runs the benchmark to its end and leaves its result on
window.ashfallBenchResults. Each timing's measured runs are pooled across a
side's loads, and the two medians compared:

- A regression fails the job: head slower than base by more than
  REGRESSION_TOLERANCE and by more than REGRESSION_FLOOR_MS. The
  `perf-accepted` label (PERF_ACCEPTED) turns it into a warning.
- A head median over its BUDGET_MS warns, and never fails.
- Boot is reported, never compared.

A base with no benchmark page (one without the ashfallBenchResults string)
is not timed: the head is reported and checked against the budgets alone.

Chromium is launched with gc() exposed (GC_FLAGS), and the page forces a
full collection before every run it times (benchTiming() in ashfall.html),
so a timing measures its own work, not the collector catching up on garbage
the runs before it left. A base whose page doesn't call gc() is timed as it
always was.

The report is a Markdown table in the job's summary ($GITHUB_STEP_SUMMARY),
and on stdout.

Environment:
  BASE_SHA, HEAD_SHA  the commits compared; the head is the checkout
  PERF_ACCEPTED       "true" when the pull request carries `perf-accepted`
  PERF_CHROMIUM       optional: a Chromium to launch instead of Playwright's
                      own, for a run outside CI
"""
import os
import pathlib
import statistics
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

GAME = "ashfall.html"
# The string a page with a benchmark carries.
BENCH_MARKER = "ashfallBenchResults"

# Every figure below is a judgment call, retunable, and this is its one home.
# The budgets are on the reference runner (ubuntu-latest), in milliseconds:
# what a timing should cost there. Over one warns (#376 makes it fail).
BUDGET_MS = {"sleep": 200, "action": 30, "render": 16}
# A regression is a head median above the base's by both of these: the
# fraction, and the floor that keeps a millisecond of noise on a fast timing
# from tripping it.
REGRESSION_TOLERANCE = 0.25
REGRESSION_FLOOR_MS = 2
# Page loads per side, and how long one may take before the job fails.
PAGE_LOADS = 3
PAGE_TIMEOUT_S = 600
# Exposes gc() to the page, which benchTiming() calls before each run.
GC_FLAGS = ["--js-flags=--expose-gc"]

# The compared timings, in report order, with what each times.
TIMINGS = {
    "sleep": "8-hour sleep",
    "action": "10-minute action and redraw",
    "render": "render()",
    "save": "serializeGame()",
}

errors = []


def fail(msg):
    errors.append(msg)
    print(f"::error::{msg}")


def base_page(base_sha, tmp):
    """The base's ashfall.html, written to `tmp`, or None when the base has
    no benchmark page."""
    text = subprocess.run(["git", "show", f"{base_sha}:{GAME}"], check=True,
                          capture_output=True, text=True).stdout
    if BENCH_MARKER not in text:
        return None
    path = pathlib.Path(tmp) / GAME
    path.write_text(text, encoding="utf-8")
    return path


def load(browser, path):
    """One page load's result, or None after reporting why there is none."""
    context = browser.new_context()
    try:
        page = context.new_page()
        page.goto(path.resolve().as_uri() + "?bench", wait_until="commit", timeout=PAGE_TIMEOUT_S * 1000)
        page.wait_for_function(f"window.{BENCH_MARKER} !== undefined", polling=1000,
                               timeout=PAGE_TIMEOUT_S * 1000)
        result = page.evaluate(f"window.{BENCH_MARKER}")
    except Exception as e:  # a timeout or a page that died
        fail(f"{path}: no benchmark result within {PAGE_TIMEOUT_S} s ({e.__class__.__name__}: {e})")
        return None
    finally:
        context.close()
    if "error" in result:
        fail(f"{path}: the benchmark failed: {result['error']}")
        return None
    return result


def pooled(results):
    """A side's loads, pooled: each timing's measured runs across every load
    and their median, the boot samples' median, and the scenario counts."""
    out = {"runs": {}, "median": {}}
    for key in TIMINGS:
        runs = [t for r in results for t in r[key]["runs"]]
        out["runs"][key] = runs
        out["median"][key] = statistics.median(runs)
    out["boot"] = statistics.median(r["boot"] for r in results)
    out["scenario"] = results[0]["scenario"]
    out["version"] = results[0]["version"]
    if any(r["scenario"] != out["scenario"] for r in results):
        fail(f"v{out['version']}: the scenario's counts differ between page loads")
    return out


def ms(v):
    return "—" if v is None else f"{v:.1f} ms"


def main():
    base_sha = os.environ["BASE_SHA"]
    accepted = os.environ.get("PERF_ACCEPTED", "").lower() == "true"
    head_path = pathlib.Path(GAME)
    rows, notes = [], []
    with tempfile.TemporaryDirectory() as tmp:
        base_path = base_page(base_sha, tmp)
        sides = {"head": head_path} if base_path is None else {"head": head_path, "base": base_path}
        results = {side: [] for side in sides}
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get("PERF_CHROMIUM") or None,
                                        args=GC_FLAGS)
            try:
                for n in range(PAGE_LOADS):
                    for side, path in sides.items():
                        print(f"Load {n + 1} of {PAGE_LOADS}: {side}", flush=True)
                        r = load(browser, path)
                        if r is not None:
                            results[side].append(r)
            finally:
                browser.close()
    if errors:
        return 1
    head = pooled(results["head"])
    base = pooled(results["base"]) if "base" in results else None
    if base is None:
        notes.append(f"The base ({base_sha[:7]}) has no benchmark page, so only the head is timed.")

    regressions = False
    for key, label in TIMINGS.items():
        h = head["median"][key]
        b = base["median"][key] if base else None
        change = f"{(h - b) / b * 100:+.1f}%" if b else "—"
        budget = BUDGET_MS.get(key)
        verdicts = []
        if b is not None and h > b * (1 + REGRESSION_TOLERANCE) and h - b > REGRESSION_FLOOR_MS:
            if accepted:
                verdicts.append("accepted")
                print(f"::warning::{label}: {ms(h)} against {ms(b)} on the base ({change}), "
                      "a regression accepted by the perf-accepted label.")
            else:
                verdicts.append("regression")
                regressions = True
                print(f"::error::{label}: {ms(h)} against {ms(b)} on the base ({change}), "
                      f"slower by more than {REGRESSION_TOLERANCE:.0%} and {REGRESSION_FLOOR_MS} ms.")
        if budget is not None and h > budget:
            verdicts.append("over budget")
            print(f"::warning::{label}: {ms(h)}, over its {budget} ms budget.")
        rows.append(f"| {label} | {ms(b)} | {ms(h)} | {change} | "
                    f"{'—' if budget is None else f'{budget} ms'} | {', '.join(verdicts) or 'ok'} |")

    runs = len(head["runs"]["sleep"])
    lines = [
        "## Performance",
        "",
        f"Medians of {runs} runs per timing, pooled over {PAGE_LOADS} page loads per side.",
        "",
        "| Timing | Base | Head | Change | Budget | Verdict |",
        "|---|---|---|---|---|---|",
        *rows,
        "",
    ]
    shas = {"Base": base_sha, "Head": os.environ.get("HEAD_SHA", "")}
    for side, r in (("Base", base), ("Head", head)):
        if r is None:
            continue
        s = r["scenario"]
        lines.append(f"- **{side}** (v{r['version']}, {shas[side][:7] or 'working tree'}): boot {ms(r['boot'])}; "
                     f"scenario {s['buildings']} buildings, {s['rowsRolled']} item rows rolled.")
    lines += [""] + notes
    report = "\n".join(lines) + "\n"
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report)
    return 1 if regressions or errors else 0


if __name__ == "__main__":
    sys.exit(main())
