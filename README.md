# Ashfall

A quiet-apocalypse survival game. One self-contained HTML file — no build step,
no dependencies, no install.

## Play

Download or clone the repo, then open `ashfall.html` in any modern browser.

```bash
git clone https://github.com/GodOfWards/Ashfall.git
cd Ashfall
open ashfall.html      # macOS
start ashfall.html     # Windows
xdg-open ashfall.html  # Linux
```

That's it. Progress saves to browser local storage.

## What it is

You wake up in your apartment. Everything's exactly where you left it — for now.

Ashfall is a text-driven survival prototype set in a collapsed town: a grid of
streets and buildings to search, hunger, thirst and fatigue that run down on a
clock, and whatever you can scavenge, carry, craft, cook or burn. The horror is
in the mundane detail — what people left behind, never explained.

## Project layout

| Path | What's in it |
|---|---|
| `ashfall.html` | The whole game. Script sections are mapped by the `ARCHITECTURE` comment at the top. |
| `CHANGELOG.md` | One entry per version, reverse-chronological. |
| `docs/` | Project, handoff and changelog guides. |
| `docs/canon/` | The world's private lore, read only on purpose, and `reference/`, real-world facts researched once (see `CLAUDE.md`). |
| `handoffs/` | Feature specs. The top level holds only live ones — usually nothing or one file. |
| `handoffs/archive/` | Spent and superseded specs. Kept, never deleted; never implemented from. |
| `CLAUDE.md` | Working conventions for contributors. |

## Contributing

Read `CLAUDE.md` first — it's short and it's binding. The essentials:

- Work on a branch; changes reach `main` through a pull request.
- Content (world data) and mechanics (actions/simulation) change separately.
- Mechanics check item tags, never item names.
- Every change bumps `GAME_CONFIG.VERSION` and adds a `CHANGELOG.md` entry.

The backlog lives in GitHub Issues, labelled `tier-0` through `tier-3`.
