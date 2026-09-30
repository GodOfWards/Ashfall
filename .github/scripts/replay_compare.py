#!/usr/bin/env python3
"""Compares the game's replay on two commits (#372). Run by hand from the
repository root, never in CI:

    python .github/scripts/replay_compare.py BASE HEAD [--ignore KEY]... [--tolerance X]

What it is for: proving what a change to the time loop changed, and that it
changed nothing else. The replay page (ashfall.html?replay, runReplay() in
the game's PERSISTENCE section) plays a fixed scenario step by step and
leaves, per step, the lines it logged and a digest of the game state after
it. This loads that page on each commit in headless Chromium, written out
with `git show` as perf_check.py does (`.` stands for the working tree's
ashfall.html), and reports every step whose log or digest differs: the
differing lines, and the differing keys by path. It exits 1 on any
difference, on a replay that fails, and on a step whose consistency check
(`problems`) found anything, on either side.

  BASE, HEAD      the commits (anything `git show` takes), or `.`
  --ignore KEY    leave every object key named KEY out of the digests, at any
                  depth; repeatable
  --tolerance X   numbers in the digests equal within X (default 0: exactly)

Environment:
  REPLAY_CHROMIUM  optional: a Chromium to launch instead of Playwright's own
"""
import argparse
import difflib
import json
import os
import pathlib
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

GAME = "ashfall.html"
RESULT = "ashfallReplayResult"
PAGE_TIMEOUT_S = 600
# How many differing keys a step reports before it only counts the rest.
MAX_KEYS_SHOWN = 40


def page_for(rev, tmp, name):
    """The page for `rev`, as a file."""
    if rev == ".":
        return pathlib.Path(GAME)
    text = subprocess.run(["git", "show", f"{rev}:{GAME}"], check=True,
                          capture_output=True, text=True).stdout
    path = pathlib.Path(tmp) / name / GAME
    path.parent.mkdir()
    path.write_text(text, encoding="utf-8")
    return path


def replay(browser, path):
    context = browser.new_context()
    try:
        page = context.new_page()
        page.goto(path.resolve().as_uri() + "?replay", wait_until="commit", timeout=PAGE_TIMEOUT_S * 1000)
        page.wait_for_function(f"window.{RESULT} !== undefined", polling=500, timeout=PAGE_TIMEOUT_S * 1000)
        return page.evaluate(f"window.{RESULT}")
    finally:
        context.close()


def diff_values(a, b, path, ignore, tol, out):
    """Every path at which `a` and `b` differ, into `out`."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in ignore:
                continue
            p = f"{path}.{k}" if path else k
            if k not in a:
                out.append(f"{p}: only in head: {json.dumps(b[k])[:200]}")
            elif k not in b:
                out.append(f"{p}: only in base: {json.dumps(a[k])[:200]}")
            else:
                diff_values(a[k], b[k], p, ignore, tol, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: {len(a)} entries in base, {len(b)} in head")
        for i, (x, y) in enumerate(zip(a, b)):
            diff_values(x, y, f"{path}[{i}]", ignore, tol, out)
    elif (isinstance(a, (int, float)) and isinstance(b, (int, float))
          and not isinstance(a, bool) and not isinstance(b, bool)):
        if abs(a - b) > tol:
            out.append(f"{path}: {a!r} in base, {b!r} in head")
    elif a != b:
        out.append(f"{path}: {json.dumps(a)[:200]} in base, {json.dumps(b)[:200]} in head")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("base")
    ap.add_argument("head")
    ap.add_argument("--ignore", action="append", default=[])
    ap.add_argument("--tolerance", type=float, default=0.0)
    args = ap.parse_args()
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        pages = {"base": page_for(args.base, tmp, "base"), "head": page_for(args.head, tmp, "head")}
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get("REPLAY_CHROMIUM") or None)
            try:
                for side, path in pages.items():
                    print(f"Replaying {side} ({getattr(args, side)})", flush=True)
                    results[side] = replay(browser, path)
            finally:
                browser.close()
    failed = False
    for side, r in results.items():
        if "error" in r:
            failed = True
            print(f"\n{side}: the replay failed after {len(r.get('steps', []))} steps:\n{r['error']}")
        for s in r.get("steps", []):
            if s.get("problems"):
                failed = True
                print(f"\n{side}, step \"{s['label']}\": the consistency check failed:")
                for line in s["problems"]:
                    print(f"  {line}")
    base, head = results["base"].get("steps", []), results["head"].get("steps", [])
    if len(base) != len(head):
        failed = True
        print(f"\n{len(base)} steps in base, {len(head)} in head")
    ignore = set(args.ignore)
    for n, (a, b) in enumerate(zip(base, head), 1):
        lines, keys = [], []
        if a["label"] != b["label"]:
            lines.append(f"  label: {a['label']!r} in base, {b['label']!r} in head")
        if a["log"] != b["log"]:
            lines += ["  log:"] + [f"    {d}" for d in difflib.unified_diff(a["log"], b["log"], "base", "head", lineterm="", n=1)]
        diff_values(json.loads(a["digest"]), json.loads(b["digest"]), "", ignore, args.tolerance, keys)
        if keys:
            lines.append(f"  digest: {len(keys)} difference{'' if len(keys) == 1 else 's'}")
            lines += [f"    {k}" for k in keys[:MAX_KEYS_SHOWN]]
            if len(keys) > MAX_KEYS_SHOWN:
                lines.append(f"    … and {len(keys) - MAX_KEYS_SHOWN} more")
        if lines:
            failed = True
            print(f"\nStep {n}, \"{b['label']}\":")
            print("\n".join(lines))
        else:
            print(f"Step {n}, \"{b['label']}\": identical")
    print("\nDifferences found." if failed else "\nNo differences.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
