#!/usr/bin/env python3
"""Stale-data guards for the docs (docs/02-code-practices.md, "Comments and
documentation"). Run from the repository root. Exits 1 if any check fails.

1. Every function (`name()`) and constant (`UPPER_CASE`) named in backticks
   in the docs exists in ashfall.html.
2. Every repository path named in backticks or a Markdown link in the docs
   resolves.
3. No handoff at the top level of handoffs/ is named by a changelog
   `Implements:` line: a spent handoff belongs in handoffs/archive/.
4. The newest changelog entry sits directly under the insertion marker.
5. CLAUDE.md stays at or under CLAUDE_MD_MAX_WORDS (a warning, not a failure).
"""
import glob
import os
import re
import sys

GAME = "ashfall.html"
CHANGELOG = "CHANGELOG.md"
MARKER = "<!-- New entries go directly below this line. -->"
CLAUDE_MD_MAX_WORDS = 1000

# The docs these checks read. The canon, its reference files, the changelog and
# the handoffs are records or research, not rules about the current code.
DOC_GLOBS = [
    "CLAUDE.md",
    "README.md",
    "docs/0*.md",
    "docs/systems/*.md",
    "docs/canon/reference/README.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/*.md",
]

FENCE = re.compile(r"^\s*```.*?^\s*```", re.S | re.M)
SPAN = re.compile(r"`([^`\n]+)`")
LINK = re.compile(r"\]\(([^)\s]+)\)")
FUNC = re.compile(r"(?<![\w$.])([A-Za-z_$][\w$]*)\(\)")
CONST = re.compile(r"(?<![\w.])([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)(?![\w])")
EXTENSIONS = (".md", ".html", ".yml", ".yaml", ".py", ".json")

errors = []


def fail(path, msg):
    errors.append(f"{path}: {msg}")
    print(f"::error file={path}::{msg}")


def doc_files():
    seen = []
    for pattern in DOC_GLOBS:
        for path in sorted(glob.glob(pattern)):
            if path not in seen:
                seen.append(path)
    return seen


def prose(text):
    """The text outside fenced code blocks: a block is quoted, not claimed."""
    return FENCE.sub("", text)


def path_candidates(token, doc):
    """Where a path named in `doc` may live, most likely first; None if the
    token isn't a repository path."""
    token = token.split("#")[0]
    if (not token or " " in token or token.startswith(("http", "#", "-"))
            or any(c in token for c in "<>*{}$:=")):
        return None
    if "/" in token:
        return [token, os.path.normpath(os.path.join(os.path.dirname(doc), token))]
    if token.endswith(".md"):
        return [token, os.path.join(os.path.dirname(doc), token), os.path.join("docs", token)]
    return None


def resolves(candidates):
    for c in candidates:
        if os.path.exists(c):
            return True
        # A handoff cited at the path it was read from resolves under archive/.
        if c.startswith("handoffs/") and not c.startswith("handoffs/archive/"):
            if os.path.exists(os.path.join("handoffs/archive", os.path.basename(c))):
                return True
    return False


def check_docs(game):
    words = set(re.findall(r"[A-Za-z_$][\w$]*", game))
    for doc in doc_files():
        text = prose(open(doc, encoding="utf-8").read())
        for span in SPAN.findall(text):
            cands = path_candidates(span.strip(), doc)
            if cands and not resolves(cands):
                fail(doc, f"path `{span}` does not resolve")
            if "/" in span:
                continue  # a path, not code: its capitals are a folder name
            for name in FUNC.findall(span):
                if name not in words:
                    fail(doc, f"`{name}()` is not in {GAME}")
            for name in CONST.findall(span):
                if name not in words:
                    fail(doc, f"`{name}` is not in {GAME}")
        for target in LINK.findall(text):
            cands = path_candidates(target, doc)
            if cands and not resolves(cands):
                fail(doc, f"link target `{target}` does not resolve")


def check_handoffs(changelog):
    for path in sorted(glob.glob("handoffs/*.md")):
        if f"Implements: {path}" in changelog:
            fail(path, "shipped (named by an Implements: line in CHANGELOG.md) "
                       "but still at the top level; git mv it to handoffs/archive/")


def check_marker(changelog):
    lines = changelog.splitlines()
    hits = [i for i, line in enumerate(lines) if line.strip() == MARKER]
    if len(hits) != 1:
        fail(CHANGELOG, f"expected the marker line exactly once, found {len(hits)}")
        return
    if any(line.startswith("## v") for line in lines[:hits[0]]):
        fail(CHANGELOG, "an entry sits above the marker line; entries go below it")
    rest = [line for line in lines[hits[0] + 1:] if line.strip()]
    if not rest or not rest[0].startswith("## v"):
        fail(CHANGELOG, "the newest entry must sit directly under the marker line")


def check_claude_md():
    count = len(open("CLAUDE.md", encoding="utf-8").read().split())
    if count > CLAUDE_MD_MAX_WORDS:
        print(f"::warning file=CLAUDE.md::CLAUDE.md is {count} words; "
              f"keep it at or under {CLAUDE_MD_MAX_WORDS} (one line per rule).")


def main():
    game = open(GAME, encoding="utf-8").read()
    changelog = open(CHANGELOG, encoding="utf-8").read()
    check_docs(game)
    check_handoffs(changelog)
    check_marker(changelog)
    check_claude_md()
    if errors:
        print(f"{len(errors)} problem(s).")
        return 1
    print("Docs check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
