# Ashfall Handoff — Documentation drift: the shipped test, three stale Project Guide claims, and two changelog gaps

Current shipped version: v0.4.11
Implied version-change type: **None — documentation only.** This pass changes no
  line of `ashfall.html`, ships no version, writes no changelog entry and gets no
  tag. That third case does not exist in the Handoff Guide's Part 1 today; adding
  it is part of this pass's own scope (edit B2 below), and #83 is where the
  decision is recorded.
Issue: #72, #73, #74, #83 — four issues, one pass, because between them they
  touch `CLAUDE.md` and all three files in `docs/`, and two of them are the same
  wrong sentence written in two places.

## What this is

Four documentation defects, all the same failure: a claim that was true when
written, about files that moved since, with nothing that can catch it drifting.

- **#72** — the documented "has this handoff shipped?" test reports false
  positives, including on the file the Handoff Guide names as its own worked
  example.
- **#73** — the Project Guide carries three claims `ashfall.html` no longer
  supports, including a worked example that was fixed by the very pass the
  passage was written to justify.
- **#74** — `CHANGELOG.md` has a version that shipped with no entry, an entry
  missing the field its guide calls mandatory, and two invented section labels.
- **#83** — a `docs/`-only pass cannot satisfy the wrap-time checklist, which is
  why this handoff has no version-change type to state.

#72 is the one with teeth. `handoffs/building-placement-and-elm-st.md` is the
spec for #8, the next substantial content pass, and the documented test tells a
session picking it up that it already shipped. The failure mode is a session that
does nothing because it believes the work is done — silent, and guaranteed by the
"never banner a spent handoff" rule to be written down nowhere.

## Relevant existing state

Every claim below was re-verified against `main` @ **v0.4.11** during planning.
Two of the issues were filed at v0.4.10 and one of their claims has changed since;
that is noted where it applies.

### The shipped test, as it behaves today

Ten handoffs exist. The documented `grep -l "handoffs/<name>.md" CHANGELOG.md`
returns **ten hits**. Eight are correct:

| handoff | implemented by |
|---|---|
| `exit-move-split.md` | v0.4.4 |
| `wide-map-panning.md` | v0.4.5 |
| `log-noise-and-collapse.md` | v0.4.6 |
| `world-data-cleanup.md` | v0.4.7 |
| `map-zoom-and-label-collisions.md` | v0.4.8 |
| `source-self-documenting.md` | v0.4.9 |
| `map-building-identity-and-label-fit.md` | v0.4.10 |
| `reproduced-defect-sweep.md` | v0.4.11 |

Two are false positives:

- `building-placement-and-elm-st.md` — cited twice in the v0.4.10 entry, both
  times saying it has **not** shipped. It is the next handoff due to be built.
- `map-view-ui-fixes.md` — cited once in v0.4.10 as context. Its own first line
  is `> **SUPERSEDED — do not implement this handoff.**`, so the repository holds
  a handoff the documented test calls spent while carrying the banner the guide
  says must never sit on a spent handoff. The Handoff Guide names this exact file
  as its worked example for the superseded case.

The root cause is that `grep -l` matches any **mention**. A changelog entry has
three legitimate reasons to name a handoff path — it implemented it, it unblocked
it, or it cited it as context — and only the first means spent.

Tightening the pattern to the mandated citation shape does not work either:
`CHANGELOG.md` is hard-wrapped at ~78 columns and v0.4.10's citation straddles a
line break, so any line-oriented test produces a false negative on a handoff that
genuinely is spent. The problem is not only the pattern; it is that no
line-oriented test can be reliable against a hard-wrapped file when the token it
looks for is prose.

### The rule is stated in two places, and is wrong in both

- `CLAUDE.md:113`, Conventions.
- `docs/Ashfall_Handoff_Guide.md:128`, Part 2, "When a handoff is no longer live".

`CLAUDE.md` is the one that binds when the guides go unread, so it matters most.

### The Project Guide's three stale claims

**1. The worked example under "A game rule gets a name, not a literal"
(`docs/Ashfall_Project_Guide.md:133-137`). Both halves are wrong, not just the
one #73 reports.**

The bad half was fixed in v0.4.9 by `handoffs/source-self-documenting.md` — the
very pass the section was written to justify:

```
ashfall.html:4271   const FISH_DURATION_MIN = 20;
ashfall.html:4289     advanceTime(FISH_DURATION_MIN);                       // doFish()
ashfall.html:5407     actionButton("Go fishing " + fmtDuration(FISH_DURATION_MIN), doFish)
```

The good half — "`doCraft()` and `doCookInContainer()` spend `recipe.minutes`,
and the buttons that launch them display `recipe.minutes`" — is half true.
`doCookInContainer()`'s button displays it:

```
ashfall.html:5433   actionButton(`Cook the ${...} ` + fmtDuration(recipe.minutes), ...)
```

`doCraft()`'s does not. `renderCraftPanel()` prints the recipe's inputs and no
duration at all, so the Craft button reads `Craft a bandage (needs Cloth x2,
Duct tape x1)` and the player is never shown the 5 minutes it costs:

```
ashfall.html:5283   const need = r.inputs.map(inp=>`${ITEM_REGISTRY[inp.id].name} x${inp.qty}`)...
ashfall.html:5287   btn.innerHTML = `${r.label} <span class="cost">(needs ${need})</span>`;
```

`recipe.minutes` remains a single source of truth for what is *spent*. It is
simply not displayed on that path — a different claim from the one the guide
makes. This finding is recorded as a comment on #73; it means the paragraph
cannot be repaired by swapping the bad example alone.

**2. The `tier-0` pointer under "Identity is explicit, never positional"
(`docs/Ashfall_Project_Guide.md:107-111`).**

All six `giveItem()` call sites resolve through `itemFromRegistry()`
(`ashfall.html:3874, 3892, 4292, 4367, 4398`, plus `4262` which passes an
already-registry-resolved item). Closed in v0.2.6. No `tier-0` issue is open — the
tracker's 44 open issues are `tier-1` through `tier-3`. A session following the
guide's instruction to "check whether that issue is still open" gets an empty
result and reasonably concludes the rule is fully satisfied. It is not: the gap
moved to `doEquip()` / `doUnequip()`, which hand-build an item object and drop
`itemId`, tracked as #71.

**3. The tag situation under Part 3 → Validation
(`docs/Ashfall_Project_Guide.md:366-381`).**

All twelve tags exist, each declaring the version it names, each on a distinct
commit:

```
v0.4.0   f3251fc   ashfall_0_4_0.html   0.4.0
v0.4.1   82a6259   ashfall_0_4_1.html   0.4.1
v0.4.2   19f0b55   ashfall_0_4_2.html   0.4.2
v0.4.3   90f38a6   ashfall_0_4_3.html   0.4.3
v0.4.4   7fc1c82   ashfall.html         0.4.4
v0.4.5   c6c7166   ashfall.html         0.4.5
v0.4.6   fbd416d   ashfall.html         0.4.6
v0.4.7   5536de7   ashfall.html         0.4.7
v0.4.8   0d534d2   ashfall.html         0.4.8
v0.4.9   def0c0f   ashfall.html         0.4.9
v0.4.10  c8f3062   ashfall.html         0.4.10
v0.4.11  6684557   ashfall.html         0.4.11
```

Two corrections follow. The guide's "Two versions have no tag at all — see the
open issue on `v0.4.4` and `v0.4.5`" is wrong twice over: both are tagged, and
**#32 is closed** (`state_reason: completed`). And the cutoff is wrong — v0.4.4
and v0.4.5 already carry `ashfall.html`, so the plain diff form works from
**v0.4.4** onward, not v0.4.6. The versioned-path caveat covers v0.4.0–v0.4.3
only.

The same caveat in `CLAUDE.md:80-83` and `docs/CHANGELOG_GUIDE.md:95` says "tags
through `v0.4.3`", which is correct in both. Neither needs changing.

### The changelog's two gaps and two labels

**v0.2.3 shipped and left no entry.** The version sequence runs 0.4.11 … 0.2.4,
0.2.2, 0.2.1, 0.1.3 — 22 entries, with 0.2.3 absent between 0.2.2 and 0.2.4. The
file proves it shipped: v0.2.4's closing line reads ``**Version**:
`GAME_CONFIG.VERSION` `"0.2.3"` → `"0.2.4"` ``, and two later entries name v0.2.3
directly. There is no `v0.2.3` tag — tagging begins at v0.4.0 — so `git log` is
the only remaining trace.

**v0.2.1 is the only entry of 22 missing the mandatory `**Version**:` line.** It
is also the entry both other guides hold up as exemplary: the Handoff Guide calls
it the model spec, and `CHANGELOG_GUIDE.md` cites its "Rest (reworked)" / "Sleep
(reworked)" structure as the model for per-subsystem sections. What preceded it is
derivable from the file itself and does not need inventing: v0.2.2's line reads
`"0.2.1"` → `"0.2.2"`, v0.2.1's own Notes section says "All existing **v0.1.3**
systems … are unchanged apart from the specific hooks listed above", and no 0.2.0
appears anywhere in the file. So the bump was `"0.1.3"` → `"0.2.1"`.

**Two invented labels, not three.** #74 names three; verification splits them:

- `New constants` (`CHANGELOG.md:743`) and `Derivations named`
  (`CHANGELOG.md:755`) are genuine top-level section labels in v0.4.8, on neither
  the allowed nor the deprecated list.
- `WORLD DATA only` (`CHANGELOG.md:1054`) is **not** an invented label. It sits
  inside v0.4.7's **Sections touched** block, three lines below that heading —
  free-form content under a documented label, which the guide already permits.
  **It needs no change and must not be touched.**

The four older entries using deprecated variants (v0.4.1, v0.4.0, v0.2.9, v0.1.3)
are covered by the older-entries exemption and are likewise out of scope.

### Why this pass has no version-change type

`CLAUDE.md`'s wrap-time checklist opens "Every PR carries all five", the first
being "`ashfall.html` with `GAME_CONFIG.VERSION` bumped". `CHANGELOG_GUIDE.md`
defines its **Documentation** label as "changes to the ARCHITECTURE comment or
inline schema comments" — in-script, not the `docs/` set. A pass whose entire
diff is `.md` files outside the game can satisfy neither. Fabricating compliance
would mean bumping a version in a byte-identical file and tagging a release where
nothing shipped, which — given that tagging has been got wrong four times, per
#32 — is the wrong direction. #83 records the decision: such a pass ships as its
own PR with no bump, no entry and no tag.

## Rules / edits

Fifteen edits across five files. Every one is settled; none requires the coding
session to choose wording except where "Design decisions" below says so.

**Read this handoff and the five files it edits. `ashfall.html` is not one of
them and does not need opening** — every claim it would be consulted for is
quoted above with a line number, verified at v0.4.11.

---

### A. `CLAUDE.md`

**A1 — Wrap-time checklist: make the exception explicit.**

Change the preamble line from `Every PR carries all five:` to:

```
Every PR that changes `ashfall.html` carries all five:
```

Items 1–5 themselves are unchanged apart from A3. After the existing closing
paragraph ("The merge ships the version; the tag is what makes it reachable
afterwards. …"), add:

```
**A pass whose diff is only `CLAUDE.md` and `docs/` is the exception.** No version
bump, no changelog entry, no tag — the game did not change, and a tag pointing at
a commit where nothing shipped is a new way to get tagging wrong. Items 3 and 4
still apply, in the PR body rather than the changelog: `Closes #NN`, and new
issues for anything deferred, or a line saying nothing was. The diff and the PR
are the whole record. The test is that the pass touched *only* those files — one
that touches `ashfall.html` as well ships normally, under all five.
```

Note the consequence for item 4, whose current text says "If nothing was
deferred, say so in the changelog's Documentation section": under the exception
there is no changelog entry, so that line goes in the PR body instead. The
paragraph above states this; item 4's own wording stays as it is.

**A2 — Conventions, the handoffs bullet: replace the test.**

In the sentence

> Whether one already **shipped** is derivable — `grep -l "handoffs/<name>.md"
> CHANGELOG.md` — so it never gets marked by hand.

replace the command with:

```
grep -l "Implements: handoffs/<name>.md" CHANGELOG.md
```

Nothing else in that bullet changes.

**A3 — Item 5's #32 parenthetical: mark it as history.**

Current:

> A bare `git tag vX.Y.Z` tags whatever `HEAD` happens to be, which is how
> `v0.4.4` and `v0.4.5` ended up on the same commit as `v0.4.7` (#32).

The sentence is past tense and #32 is closed, but a reader checking the tags today
finds all three on distinct commits and may conclude the sentence is false. Change
`(#32)` to `(#32, since corrected)`. The rest of item 5 stands — it is the
explanation of why the rule exists, and it is still the right rule.

---

### B. `docs/Ashfall_Handoff_Guide.md`

**B1 — Part 2, the "Spent" block: replace the test and say why the field
exists.**

Replace from "This is already recorded, because…" through the fenced command,
keeping the "A hit means spent…" sentence and the "Never banner a spent handoff"
rule that follow. New text:

```
**Spent** — it shipped. Re-implementing it is redundant at best. This is
already recorded, because every changelog entry that implements a handoff
carries an `Implements:` field naming it by path (`CHANGELOG_GUIDE.md`), so
status is derivable with no new bookkeeping:

    grep -l "Implements: handoffs/<name>.md" CHANGELOG.md

A hit means spent, and the `## vX.Y.Z` heading above it says which version
consumed it. The field is what makes this reliable. A changelog entry has three
reasons to name a handoff path — it implemented it, it unblocked it, or it cited
it as context — and only the first carries the field, so a mention can no longer
be mistaken for an implementation. **Never banner a spent handoff** — that would
hand-maintain a copy of the changelog, which is what one-source-of-truth exists
to prevent, and it would drift.
```

(The indented command above is the existing fenced block, unchanged in form —
keep whichever fence style the file already uses.)

**B2 — Part 1: add the documentation-only case.**

At the end of "Stating the version-change type for a handoff", after the existing
tentative-PATCH-vs-MINOR bullets, add:

```
### Documentation-only passes

A pass whose entire diff is `CLAUDE.md` and the `docs/` set ships no version at
all, so it has no change type to state. Write `None — documentation only` where
the header asks for one, and say in a sentence why. `CLAUDE.md`'s wrap-time
checklist says what such a pull request carries instead of a bump, an entry and a
tag.
```

This is what lets this handoff's own header be valid. Without it the Part 1
instruction "What the handoff *can* and must state … is the **type** of change it
implies: `PATCH` or `MINOR`" admits no third answer.

---

### C. `docs/Ashfall_Project_Guide.md`

**C1 — Part 2, "Identity is explicit, never positional": drop the stale
pointer.**

Replace the second bullet entirely. New text:

```
- Item *definitions* are ID-based: `ITEM_REGISTRY` plus
  `itemFromRegistry()` / `itemsFromRegistry()` are the single source of
  truth for item properties, used throughout `makeDefaultWorld()`, and
  every `giveItem()` call site resolves through it. Gaps in this rule are
  tracked in the backlog rather than named here — search the open issues
  for the current one, rather than assuming either that the rule is fully
  satisfied or that whichever gap was last written down is still the one
  that's open.
```

Deliberately naming no issue number and no function: the original broke because
it named both, and the gap moved. The instruction to check the tracker was the
half that was right, and it survives.

**C2 — Part 2, "A game rule gets a name, not a literal": rewrite the worked
example so it cannot go stale again.**

Replace the whole paragraph beginning "The file already shows both halves." with:

```
The file shows the rule working. `doCraft()` and `doCookInContainer()` both spend
`recipe.minutes` — the duration is declared once per recipe and read wherever it
is needed, including the Cook button, which prints `fmtDuration(recipe.minutes)`
beside its label. Retune a recipe and every reader of it follows.

The rule's other half is easier to state than to illustrate, because the
illustrations keep getting fixed. A duration spent as a literal in one place and
printed as the same literal in another is two facts that have to agree, with
nothing making them: whichever call site is edited first, the other starts lying
to the player. That shape is what to look for, not a particular function — a
worked example drawn from live code goes stale by being acted on, which is
exactly what happened to the one this passage used to name.
```

The claim about the Cook button is verified (`ashfall.html:5433`). The Craft
button is deliberately not cited, because it displays no duration — see
"Relevant existing state" above.

**C3 — Part 3, Validation: correct the tag cutoff and drop the closed issue.**

Replace the final paragraph of the tag-diffing block:

> From `v0.4.6` onward the tag carries `ashfall.html` and the plain form works.
> Two versions have no tag at all — see the open issue on `v0.4.4` and `v0.4.5` —
> so for those, diff against the merge commit or the base branch.

with:

```
From `v0.4.4` onward the tag carries `ashfall.html` and the plain form works; the
versioned-path caveat covers `v0.4.0`–`v0.4.3` only. If a version you need has no
tag, diff against the merge commit or the base branch instead.
```

The fallback advice is kept and generalized rather than tied to two named
versions — the specific claim is what drifted, the advice is still useful.

The paragraph above it, about tags through `v0.4.3` living at a versioned path,
is correct and unchanged.

---

### D. `docs/CHANGELOG_GUIDE.md`

**D1 — Require the `Implements:` field.**

First, replace the last bullet of **Entry header**:

> - If the entry implements a handoff, say so and name it by path (e.g.
>   "Implements #3 in full, per `handoffs/lockpicking.md`") — this links the
>   record of what shipped back to the spec that produced it and to the issue it
>   closed.

with:

```
- If the entry implements a handoff, carry the `Implements:` field described
  below **and** say so in the entry's opening prose (e.g. "Implements #3 in full,
  per `handoffs/lockpicking.md`"). The field is what a command reads, the prose is
  what a person reads, and together they link the record of what shipped back to
  the spec that produced it and to the issue it closed.
```

Then add a new section immediately after **Entry header** and before **Required
closing line**:

```
## Required implements line

If the entry implements a handoff, the line directly under the entry header is:

    Implements: handoffs/<name>.md

Plain text — no bold, no backticks, one line, nothing else on it. That is
deliberate, and it is the one place this guide's "inline code for any identifier"
convention does not apply: this line is read by a command, not only by a person.

    grep -l "Implements: handoffs/<name>.md" CHANGELOG.md

is how `CLAUDE.md` and `docs/Ashfall_Handoff_Guide.md` both answer "has this
handoff shipped?", and bold or backticks would break a grep anyone can type from
memory. Prose elsewhere in the entry still cites handoff paths in backticks as
normal — being distinguishable from that prose is the entire point of the field.

Omit the line when the entry implements no handoff. An entry that merely mentions
one — because it unblocked it, or cited it for context — must not carry the field
for it. That distinction is what the field exists to make.
```

**D2 — Deprecate the two invented labels.**

In "Use the documented label, not a variant", extend the list of variants that
should not be used again with:

- `New constants` → use **New**.
- `Derivations named` → use **Changed / Reworked**.

Both appeared in v0.4.8. Its headings stay exactly as they shipped, under the
older-entries exemption the section already states — only the guide changes.

**D3 — Scope the Documentation label.**

Extend the **Documentation** bullet's first sentence to say "in `ashfall.html`",
and append:

```
Edits to `CLAUDE.md` or the `docs/` set are not this section's subject — a pass
whose diff is only those files ships no version and writes no entry at all (see
`CLAUDE.md`'s wrap-time checklist).
```

---

### E. `CHANGELOG.md`

**E1 — Retro-fit the `Implements:` field into the eight spent entries.**

Directly under each entry's `## vX.Y.Z — <title>` line, separated by one blank
line and followed by one blank line before the existing body:

```
Implements: handoffs/exit-move-split.md                      → v0.4.4
Implements: handoffs/wide-map-panning.md                     → v0.4.5
Implements: handoffs/log-noise-and-collapse.md               → v0.4.6
Implements: handoffs/world-data-cleanup.md                   → v0.4.7
Implements: handoffs/map-zoom-and-label-collisions.md        → v0.4.8
Implements: handoffs/source-self-documenting.md              → v0.4.9
Implements: handoffs/map-building-identity-and-label-fit.md  → v0.4.10
Implements: handoffs/reproduced-defect-sweep.md              → v0.4.11
```

(The arrows are this table's notation, not part of the line. Each entry gets only
the bare `Implements: handoffs/<name>.md`.)

No other entry gets the field. In particular **neither
`building-placement-and-elm-st.md` nor `map-view-ui-fixes.md` gets one anywhere**
— that is the whole fix, and adding either would restore the bug.

This is additive: no existing sentence is edited, and the prose citations already
in those eight entries stay exactly as they are. It is not the kind of rewriting
the older-entries exemption forbids, which is about relabelling sections to match
a later list.

Verify afterwards that the test now returns 8, and that it returns nothing for the
two handoffs that have not shipped.

**E2 — Give v0.2.1 its closing line.**

Append to the end of the `## v0.2.1 — Stamina & Fatigue System` entry, after its
**Notes / assumptions** section and before the `---` rule:

```
**Version**: `GAME_CONFIG.VERSION` `"0.1.3"` → `"0.2.1"`
```

Derived, not invented — see "Relevant existing state" for the three pieces of
evidence in the file itself. This adds the field the guide calls mandatory; it
alters no word of the record.

**E3 — Mark the v0.2.3 gap in place.**

Insert between the `## v0.2.4` entry and the `## v0.2.2` entry, in sequence
position, with `---` rules on both sides as every entry has:

```
## v0.2.3 — no entry was written

This version shipped and no entry was written for it. `v0.2.4`'s closing line
records the bump as `"0.2.3"` → `"0.2.4"`, and two later entries name v0.2.3
directly, so the gap is an omission rather than a skipped number. Nothing has
been reconstructed: `git log` is the only surviving record of what it changed,
and a reconstruction written this long after the fact would not be the record
this file exists to keep. There is no `v0.2.3` tag either — tagging begins at
v0.4.0.

This placeholder exists so the gap reads as known rather than as an oversight
waiting to be found again.

**Version**: `GAME_CONFIG.VERSION` `"0.2.2"` → `"0.2.3"`
```

The closing line is derivable from the entries on either side and is included so
the stub satisfies the guide like any other entry.

**E4 — Record that the file's start is genesis, not a gap.**

Extend the file's intro paragraph with:

```
The file begins at v0.1.3; 0.1.0–0.1.2 predate it and are project genesis, not
missing entries. The one genuine gap, v0.2.3, is marked in place.
```

## Design decisions to make during implementation

Three narrow calls. Record whichever is chosen in the PR body — there is no
changelog entry to record it in.

1. **Exact placement of the `Implements:` field.** The recommendation is
   immediately under the `## vX.Y.Z — <title>` line, one blank line either side,
   above the entry's opening prose. The alternative is beside the `**Version**:`
   closing line, where the other machine-read field lives. Recommendation stands
   on the grounds that a reader scanning headings should see what a version
   implemented without reading to the bottom. Either is greppable; pick one and
   apply it to all eight identically.

2. **Wording of A3's parenthetical.** `(#32, since corrected)` is the
   recommendation. Anything that makes the sentence unambiguously historical will
   do — this is a clarity fix, not a factual one, and is retunable.

3. **Whether E3's stub uses the entry title `no entry was written`.** Recommended
   as written, because it is what the entry is. Any plain alternative is fine; it
   should not read as a title for a pass that never got described.

## Data / schema changes

None. No PLAYER STATE field, no ITEM DATA SCHEMA field, no room/container/exit
schema change, no `SAVE_KEY` rotation, no change of any kind to `ashfall.html`.

## In scope

- `CLAUDE.md` — A1, A2, A3.
- `docs/Ashfall_Handoff_Guide.md` — B1, B2.
- `docs/Ashfall_Project_Guide.md` — C1, C2, C3.
- `docs/CHANGELOG_GUIDE.md` — D1, D2, D3.
- `CHANGELOG.md` — E1, E2, E3, E4.

## Explicitly out of scope

- **`ashfall.html`, entirely.** No version bump, no changelog entry, no tag. If
  this pass produces a diff in the game file, something has gone wrong.
- **Whether the Craft button should display its duration.** Surfaced while
  verifying C2 and deliberately left alone — it is a UI question about
  `renderCraftPanel()`, not a documentation one. Not filed as an issue either:
  it may well be intentional, and C2's rewrite no longer depends on the answer.
- **v0.4.7's `WORLD DATA only`.** Verified to sit inside its **Sections
  touched** block, which the guide permits. #74 lists it alongside the two real
  cases; it is not one. Do not touch it.
- **The four older entries using deprecated variants** (v0.4.1, v0.4.0, v0.2.9,
  v0.1.3) and the `Changed — <SECTION>` compound labels in v0.3.0, v0.2.9,
  v0.2.7 and v0.2.6. All covered by the older-entries exemption. D2 changes the
  guide, never those entries.
- **Reconstructing v0.2.3.** Decided against; E3 is the whole treatment.
- **`CHANGELOG.md`'s size** (3,244 lines, 179 KB). #74 raises it as context and
  explicitly not as a defect — the existing mitigations are working, and splitting
  the file would break every citation by path.
- **#46** — the content-vs-mechanics rule stated absolutely in the guides and as
  a default in the source. The fourth member of this family, already open, already
  correct, and a different kind of fix: it reconciles two documents that disagree
  rather than correcting one that drifted.
- **#71** — the `doEquip()` / `doUnequip()` registry gap. C1 stops the Project
  Guide pointing at the wrong place; fixing the code is that issue's job.
- **#8 and `handoffs/building-placement-and-elm-st.md`.** This pass makes the
  shipped test stop lying about that handoff. It does not implement it.

## Sections touched

**None — this pass touches no `ashfall.html` section.** It is neither a content
pass nor a mechanics pass nor a rendering pass; the ARCHITECTURE comment is not
implicated and does not need reading.

## UI changes

None.

## Dependencies / issue linkage

Fulfils **#72**, **#73**, **#74** and **#83** — all four, in one pass, per #74's
own recommendation that the documentation corrections be done together and #83's
that it decides what their pull request looks like.

#83 is resolved by A1 and B2 specifically. It was filed during the planning
session that produced this handoff, from the question of how this pass itself
could ship.

Nothing is expected to be deferred. If the coding session does defer anything, it
files an issue and says so in the PR body rather than in a changelog entry.

## Open questions for Tom

None. All four decisions were taken during planning:

- **A `docs/`-only pass ships as its own PR** with no bump, no entry and no tag
  (#83 option 1) → A1, B2, D3.
- **The shipped test becomes true by construction**, via a required greppable
  `Implements:` field, rather than by a cleverer regex (#72 option 2) → A2, B1,
  D1, E1. This is the same move the project made in deriving `CONTAINER_SLOTS`
  from the registry instead of listing it by hand.
- **v0.2.3 gets a one-line placeholder**, not a reconstruction (#74) → E3, E4.
- **Both invented labels are deprecated**, and the label list does not grow
  (#74) → D2.

## After implementation

Open a pull request whose body states the pass's intent and carries `Closes #72`,
`Closes #73`, `Closes #74` and `Closes #83`. Under the exception this handoff
establishes, that PR carries **no** version bump, **no** `CHANGELOG.md` entry for
itself, and gets **no** tag on merge — `CHANGELOG.md` is edited by E1–E4, but as
the subject of the corrections, not as a record of this pass.

Record the three "Design decisions" resolutions in the PR body, along with a line
saying nothing was deferred if nothing was.

Two things are worth checking before opening it:

- `grep -l "Implements: handoffs/<name>.md" CHANGELOG.md` returns a hit for each
  of the eight spent handoffs and nothing for `building-placement-and-elm-st.md`
  or `map-view-ui-fixes.md`.
- `git diff origin/main...HEAD -- ashfall.html` is empty.
