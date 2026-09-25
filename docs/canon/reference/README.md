# Reference — real-world facts, researched once

**This folder is real-world data, not lore.** It holds what the game needs to
know about the real world to be accurate ("The world is real", `CLAUDE.md`):
codes, equipment, figures, the real town. It sits beside the canon because
both are designer knowledge the game never states outright.

## Rules

- **Look here first.** Sessions run with limited internet access, so this
  folder is the first and usually the only place a fact is looked up. A fact
  already here, with its source, isn't looked up again unless it's being
  re-verified. Check the open `Research:` issues too: findings written there
  may not have merged here yet.
- **If it isn't here, don't guess and don't go searching on your own.** Do one
  of two things:
  - **ask Tom for network access** to research it now, if the work can't
    move without it; or
  - **file a `Research:` issue** saying which fact is needed, why, and which
    issue it blocks, and carry on with the rest, with the gap marked
    unconfirmed.
- **What gets researched is added here in the same session,** with its source,
  date and status. A fact found once and left in a conversation or an issue
  comment will be searched for again. A `Research:` issue's findings go in
  two places:
  - **the issue's body, edited as soon as they're found,** with sources, dates
    and status, so a session running before the merge can read them;
  - **this folder, in a pull request that says `Closes #NN`.** Once it merges,
    the file is the record and the closed issue is history.
- **Every fact carries its source and the date it was checked.** Its status is
  one of:
  - **Confirmed:** read on the primary source (the maker, the regulator, the
    standard, the utility).
  - **Secondary:** read on a trade article, retailer listing or search summary
    that quotes or restates the primary, but not on the primary itself.
  - **Unconfirmed:** a figure the game uses without a source that states it.
    Say so, and say what would confirm it.
- **One source of truth.** Issues and handoffs point here rather than
  repeating figures. An open `Research:` issue is the one exception, until
  its pull request merges. A handoff **quotes** the figures its pass needs, because a
  coding session never reads this folder (`CLAUDE.md`, "The canon is private").
  The issue comments that first recorded a fact stay as history.
- **When a figure here and a figure in the game disagree,** the file wins as
  the record of the real world. The disagreement is filed as an issue (or
  noted on a live handoff), not silently fixed in either place.

## Who reads it

A **planning session reads it whenever the discussion needs real-world facts**,
not only for lore. The lore file (`../Ashfall_Canon.md`) keeps its stricter
rule. A coding session reads neither.

## Files

| File | Covers |
|---|---|
| `Henderson.md` | The real town: its electricity, water, gas, crossings and plants; downtown's street grid, rail and buildings |
| `Electrical.md` | US wiring code (NEC) and Kentucky's adoption, breakers (UL 489), panels and service, appliances and nameplates, lighting, GFCI, cords, meters, rail-crossing standby power |
| `Fuel_and_Generators.md` | Gasoline (grades, shelf life, stations, cars, cans) and portable generators |
| `Carbon_Monoxide.md` | Exposure effects, the body's level, CO alarms, generator placement |
