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

A text-driven survival prototype set in Lima, a small town in Buenos Aires
province, Argentina, after a collapse nobody explains. Real streets and
buildings to search; hunger, thirst and fatigue that run down on a clock;
power that fails; and whatever you can scavenge, carry, craft, cook or burn.
The horror is in the mundane detail: what people left behind.

## Project layout

| Path | What's in it |
|---|---|
| `ashfall.html` | The whole game. Script sections are mapped by the `ARCHITECTURE` comment at the top. |
| `CLAUDE.md` | Start here: which session you're in, what to read, and the binding rules. |
| `CHANGELOG.md` | One entry per version, newest first. |
| `docs/01-writing.md` | Tone, the real town, language and naming. |
| `docs/02-code-practices.md` | How the code is written, and where knowledge about it lives. |
| `docs/03-workflow.md` | Sessions, issues, versions, handoffs, and the wrap. |
| `docs/04-handoff-template.md` | The template a handoff is written from. |
| `docs/05-changelog-guide.md` | How a changelog entry is written. |
| `docs/systems/` | One doc per game system, written when the system is next changed. |
| `docs/canon/` | The world's private lore, and `docs/canon/reference/`: real-world facts researched once. Read only on purpose. |
| `handoffs/` | Feature specs. The top level holds only live ones — usually nothing or one file. |
| `handoffs/archive/` | Spent and superseded specs. Kept, never deleted; never implemented from. |
| `.github/` | Issue and pull request templates, and the CI checks. |

## Contributing

Read `CLAUDE.md` first; it's binding. The essentials:

- Work on a branch; changes reach `main` through a pull request.
- Content (world data) and mechanics (actions/simulation) change separately.
- Mechanics check item tags, never item names.
- Every change to `ashfall.html` bumps `GAME_CONFIG.VERSION` and adds a
  `CHANGELOG.md` entry. A change that leaves the game untouched does neither.

The backlog lives in GitHub Issues, each labelled with a tier (`tier-0` to
`tier-3`) and a kind.
