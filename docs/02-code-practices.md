# 02 — Code practices

How `ashfall.html` is written, and where knowledge about it lives. The home
of the development rules. Read by a planning session when the discussion
reaches mechanics or structure.

Section layout is not restated here, or anywhere else: the `ARCHITECTURE`
comment at the top of the script is the source of truth for the sections
and what each owns.

## Content, mechanics, rendering

A change normally touches one of:

- **WORLD DATA** (content): rooms, items, containers, exits, descriptions,
  and static reference data such as map coordinates.
- **ACTIONS / SIMULATION** (mechanics): only when a genuinely new mechanic
  is needed, never to accommodate one piece of content.
- **Rendering**, its own concern: a new way of displaying existing state is
  neither content nor a mechanic.

If a content request seems to need a mechanics change, stop and confirm it
really is a new mechanic.

**The one case that touches both** is data that is the mechanic's own
definition: a schema field the new rule reads, shipped on the items or rooms
the rule acts on. A mechanic that does nothing until some item carries its
property is one change, not two. Data that is an *instance* (a room, a
placement, a description, a coordinate) never rides along with a mechanics
change: a feature never gets to rewrite the world to suit itself. The
changelog's separate **New** and **New content** sections keep the two halves
visible when one entry carries both.

## Identity and tags

- **Items resolve by `_uid` at runtime, never by array index.** An index is
  fine only as a short-lived lookup inside one already-validated operation.
- **Item definitions come from `ITEM_REGISTRY`**, through
  `itemFromRegistry()` / `itemsFromRegistry()`.
- **Mechanics check tags, never names.** A new item that should behave like
  an existing one gets the same tag (`blunt`, `fishing`, `fire-starter`, …),
  never an `it.name === "Something"` check.

## One source of truth

A constant, threshold or item property is defined once. If the same fact must
hold in two places, it belongs in a shared definition: a registry entry or a
named constant.

**A game rule gets a name, not a literal.** A duration, threshold, rate,
capacity or quantity is normally a named constant, in CONFIG / CONSTANTS or
beside the system that owns it. A value derived from others is written as its
derivation (`FIRE_BUILD_WOOD * FIRE_MINUTES_PER_WOOD`, not its product), so it
follows when an input is retuned.

**The test is whether the call site reads better.** Leave the literal when
the name would only restate the digits, when the constant would sit far from
its one use, or for:

- mathematical identities (`* 180 / Math.PI`, a loop's epsilon);
- per-instance content (one building's offset, one item's weight);
- structural trivia (`0`, `1`, array bounds).

## Performance

The game must stay fast as systems are added. Three principles:

1. **Nothing checks the whole world every minute.** A system is either
   **worked out when read** (store the value as of minute T and its rate,
   and compute it when someone looks) or **driven by scheduled events** (a
   fire goes out at minute T). Only the player's own vitals step per minute.
2. **Detail depends on distance.** Full simulation where the player is,
   summary state elsewhere, filled in when the player arrives.
3. **Costs are measured, and stated up front.** Every handoff for a new
   system says what it adds per game minute and per event.

## Comments and documentation

Knowledge about the code lives in one of four places, chosen by what it is:

| What | Where |
|---|---|
| Why a line or function is the way it is; an invariant one function keeps | A comment beside it |
| A data shape (ROOM, ITEM, POWER and the other schema blocks) | Its schema comment in the code: the language has no types, so these are the only specification of the shapes, kept whole and current |
| How a system works across functions: its model, its invariants, how the pieces connect | Its doc in `docs/systems/` (that folder's `README.md` sets the format) |
| A real-world figure's source | `docs/canon/reference/`; the code keeps the named constant and a one-line pointer |

**Comments carry intent, not history.** A comment never records when
something arrived, which version or issue changed it, or which handoff asked
for it: the changelog and git already hold that, and a comment is where
nothing catches it going stale. The goal is fewer comments, not none. Before
removing one, say what a reader loses; if the answer is anything, it stays.

**Rules for every document**, so none goes stale:

1. **One home per fact.** Everything else links to it. `CLAUDE.md` is the one
   exception: one line per binding rule, pointing to its home.
2. **Rules, never examples copied from the live game.** An example is written
   for the doc and labelled illustrative.
3. **No history in rules.** Why a rule exists takes a sentence; the incident
   that prompted it belongs in the changelog or the issue.
4. **No numbers in a systems doc.** Name the constant; never copy its value.
5. **A change to a system updates its systems doc in the same pull request.**

CI checks what it can (`.github/workflows/docs-check.yml`): every function
(written with its parentheses) and every constant (capitals and underscores)
named in backticks in `docs/` and `CLAUDE.md` must exist in `ashfall.html`,
and every repository path those files name must resolve.

**Filenames carry no version.** Git tags mark releases. A doc's number is
permanent and never reused: a new doc takes the next free number.

## Judgment calls are flagged

A value or choice with no prior convention (a threshold, a balance number, a
naming choice, a pick between two options a handoff left open) is called out
as retunable, never left to read as settled. Who gets to make such a choice
at all is `03-workflow.md`'s.

## Proving "no behavior change"

A reorg, cleanup or documentation pass that claims no behaviour change proves
it with a diff, not an assertion:

```
git diff origin/main...HEAD -- ashfall.html
```

That is everything the branch changed and nothing else. Don't diff against a
tag up to and including `v0.4.3`: those carry the game at a versioned path
(`ashfall_0_4_3.html`), so a tag-to-`HEAD` diff on `ashfall.html` reports the
whole file as new. Name both blobs instead
(`git diff v0.4.3:ashfall_0_4_3.html HEAD:ashfall.html`). From `v0.4.4` on,
the plain form works.
