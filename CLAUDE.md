# Ashfall

A quiet-apocalypse survival game: one self-contained file, `ashfall.html`, no
build step, no dependencies. Open it in a browser to run it.

This file is the index: which session you are in, what to read, and one line
per binding rule. Each rule's home is named; the home wins if they ever differ.

## Which session is this?

Identify it **before reading anything else**. Each list is complete.

**Planning session**: designs a change. Never writes game code.

- **Up front:** the open issues list. Nothing else.
- **As the discussion needs it:**
  - `ashfall.html`, the sections the change touches, when the discussion
    reaches them;
  - individual issues, once one is relevant;
  - the last few `CHANGELOG.md` entries, when recent work bears on the design;
  - `docs/01-writing.md` for game text, `docs/02-code-practices.md` for
    mechanics and structure;
  - `docs/systems/`, for the systems touched;
  - `docs/canon/reference/`, whenever a real-world fact is needed;
  - `docs/canon/Ashfall_Canon.md`, when the discussion is about lore or Tom
    asks.
- **At the wrap:** `docs/03-workflow.md` (Handoffs) and
  `docs/04-handoff-template.md`.
- **Output:** issues filed as they surface and, only if it concludes, a
  handoff at `handoffs/<feature-name>.md`, landed on `main`.

**Design session**: discusses and designs. Never writes game code, never
writes a handoff, and has no wrap.

- **Up front:** the open issues list. Nothing else.
- **As the discussion needs it:** the same as a planning session.
- **Output:** issues filed and edited as the discussion goes, and `designed`
  applied when Tom confirms a design is done. Nothing else. A design session
  can end mid-thread; an open question is a valid place to stop.

**Research session**: looks up real-world facts, with full network access.
Never writes game code.

- **Up front:** the open `research` issues and
  `docs/canon/reference/README.md`.
- **As the research needs it:** the reference file a fact belongs in, and the
  issues a `research` issue blocks.
- **Output:** findings in the issue body as they're found, then one pull
  request into `docs/canon/reference/` that says `Closes #NN`.

**Coding session**: implements one handoff.

- **Up front:** all of `ashfall.html`, the one handoff at the top level of
  `handoffs/`, and the `docs/systems/` docs it names. Nothing else: not the
  changelog, the backlog, the canon, or `handoffs/archive/`, which is never
  implemented from.
- **At the wrap:** `docs/03-workflow.md` (The wrap) and
  `docs/05-changelog-guide.md`.
- **Output:** one pull request from a branch, never a commit to `main`. Phase
  commits (`Phase N: …`) are pushed as they're made.

A pass Tom asks for directly, from a spec that already exists, follows the
coding session's wrap without a handoff (`docs/03-workflow.md`).

## Rules that bind

- **Nothing is edited, committed or pushed without being asked**, in any file.
  A question is a question: propose and wait. GitHub Issues are the exception:
  file and edit them as work surfaces. → `docs/03-workflow.md`
- **Design decisions are Tom's; implementation choices are made and named.**
  When unsure which it is, ask. → `docs/03-workflow.md`
- **Flag judgment calls as retunable.** → `docs/02-code-practices.md`
- **The world is real.** Lima, Partido de Zárate, Buenos Aires: real names,
  facts checked against a source, never recalled or invented; unconfirmed
  facts marked so. No real brand or business trading name appears. →
  `docs/01-writing.md`
- **Facts are looked up in `docs/canon/reference/` first.** One that isn't
  there is never guessed, and is searched for only in a research session: ask
  Tom for one, or file a `research` issue. → `docs/canon/reference/README.md`
- **The canon is private.** `docs/canon/` is read by path, on purpose, never
  found by search (`.rgignore`). A coding session reads neither the canon nor
  the reference folder: its handoff quotes what it needs.
- **Writing game text:** second person, present tense, plain; understatement;
  never explain the collapse; one to three sentences. English, except streets,
  districts and towns. → `docs/01-writing.md`
- **Section layout lives in the `ARCHITECTURE` comment** at the top of the
  script. No document restates it.
- **Content, mechanics and rendering stay separate**; a mechanic may ship its
  own defining data, never instance data. → `docs/02-code-practices.md`
- **Mechanics check tags, never names.** → `docs/02-code-practices.md`
- **Identity is `_uid`, never an array index**; items come from
  `ITEM_REGISTRY` via `itemFromRegistry()`. → `docs/02-code-practices.md`
- **One source of truth**; a game rule gets a named constant. →
  `docs/02-code-practices.md`
- **Nothing checks the whole world every minute.** → `docs/02-code-practices.md`
- **Prove "no behavior change"** with
  `git diff origin/main...HEAD -- ashfall.html`, never a tag diff. →
  `docs/02-code-practices.md`
- **Knowledge has one home**: why-comments in code, systems in
  `docs/systems/`, figures in `docs/canon/reference/`, history in the changelog.
  A system change updates its systems doc in the same pull request. →
  `docs/02-code-practices.md`
- **New persistent state means MINOR**, and rotates the save key. Tiers:
  `tier-0`/`tier-1` PATCH, `tier-2`/`tier-3` MINOR; the number within a pair
  is size, never priority. → `docs/03-workflow.md`
- **Issues** carry a tier, a kind and follow their kind's template; the body
  is the current truth; closed only by `Closes #NN`. `designed` marks one
  whose design Tom has confirmed done. → `docs/03-workflow.md`
- **Handoffs**: the top level of `handoffs/` holds only live ones; spent and
  superseded ones move to `handoffs/archive/`, never renamed. →
  `docs/03-workflow.md`
- **Filenames carry no version**; a doc's number is permanent.
- If the issue tracker is unreachable, say so and continue.

## The wrap, in brief

Every pull request that changes `ashfall.html` carries: the
`GAME_CONFIG.VERSION` bump; a `CHANGELOG.md` entry; the handoff archived;
`Closes #NN`; issues for anything deferred; and the tag block as the last
thing in the session's final message. A pass that leaves `ashfall.html`
untouched has no bump, entry or tag. The full checklist and the tag block are
in `docs/03-workflow.md` (The wrap).
