# Systems docs

One doc per game system: how it works across functions, which no single
comment can say. The home of the format below. Read by a planning session for
the systems a discussion touches, and by a coding session for the ones its
handoff names.

## What goes where

A systems doc holds a system's **model** (what it simulates and how the pieces
connect) and its **invariants** (what must stay true across functions). It
never holds:

- **data shapes**, which stay in the code's schema comments, edited in the
  same diff as the shape; the doc names the schema block;
- **values**: it names the constant (`FRIDGE_RATE_POWERED`), never copies its value;
- **real-world figures or their sources**, which live in
  `docs/canon/reference/`;
- **history**: what shipped when is the changelog's.

## When one is written

**On touch.** A pass that changes a system with no doc writes it, in the same
pull request. A pass that changes a system with a doc updates it
(`02-code-practices.md`, rule 5). The system's overview comments in
`ashfall.html` move here in that pass, leaving a one-line pointer in the code.

## Format

Every systems doc has these sections, in this order:

```markdown
# <System>

ARCHITECTURE sections: <the sections and named sub-blocks it lives in>

## Purpose
What the system is for, in the game, in two or three sentences.

## Model
How it works: the state it reads and writes, how the pieces connect, the
order things happen in.

## Invariants
What must stay true, and which functions keep it true.

## Entry points
The functions the rest of the game calls, and what each promises.

## Constants
The named constants that tune it, by name, each with one line on what it
controls.

## Costs
What it adds per game minute and per event, and how it avoids checking the
whole world every minute (`02-code-practices.md`, Performance).
```

## Index

Each doc is listed here as it is written.

- [Time](time.md): the clock, the scheduler, settling, and batteries.
- [Power](power.md): the network, the resolve, and when power resolves.
- [Spoilage](spoilage.md): food's ages, worked out when read.

One is overdue:

- **Survival**: the Stamina & Fatigue rules are recorded only in the
  v0.2.1 entry of `CHANGELOG.md`, which a comment in the code still points to.
