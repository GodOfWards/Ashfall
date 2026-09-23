# Ashfall Handoff — Portrait layout, compact action buttons, tighter line spacing

Current shipped version: v0.6.3
Implied version-change type: PATCH
Issue: #159 — Portrait layout — one column by orientation, Here above Inventory, compact action buttons and tighter line spacing

## What this is

The layout is fitted to a phone held upright, and landscape keeps today's
two-column layout. From #159:

> The target is a phone held upright; landscape keeps today's layout.

Three changes:
1. **What switches the layout** changes from a width to the viewport's
   orientation, with a width floor.
2. **Portrait** gets a one-column order with Here above Inventory, and narrower
   side padding.
3. **Everywhere**, action buttons get compact sizes and the room description and
   log get tighter line spacing.

This is CSS only, plus markup only if the implementation chooses it (see
"Design decisions").

**Sibling handoffs from the same planning session:**
- `handoffs/menu-hub.md` (#157, #158, #160) removes the Craft panel from the
  sidebar and adds new rules to the `<style>` block. They touch no common line,
  and either can ship first. The approved mock-ups assumed both had shipped.
- `handoffs/device-options.md` (#161) doesn't touch layout.

## Relevant existing state

Verified against `ashfall.html` at v0.6.3. Line numbers are that file's.

**Grid and panels.**
- `main` is `display:grid; grid-template-columns:1fr 320px` (`:66`).
- `#left` (`:67`) is `padding:18px 26px`, with `border-right`.
- `#left` holds `#roomDesc`, `#log`, `#moveGroup` and `#hereGroup` (`:183`–`:188`).
- `#sidebar` (`:98`) is a flex column. It holds three `.panel`s, **without ids**,
  in this order (`:189`–`:204`):
  1. Inventory
  2. Here
  3. Craft (removed by the sibling hub handoff)

**The current switch.** The only `@media` rule is `@media (max-width:760px)`
(`:130`). It sets `main{ grid-template-columns:1fr; }`, and moves `#left`'s border
from right to bottom. Its comment (`:120`–`:129`) records:
- the grid's **476px floor** (320px sidebar plus the description's minimum),
  below which the page scrolls sideways;
- that "anything from 480 up removes the overflow";
- that 760 was a retunable judgment call.

**Sizes.**

| rule | line | today |
|---|---|---|
| `#roomDesc` line-height | `:68` | `1.6` |
| `#log p` line-height | `:70` | `1.5` |
| `.actions` gap | `:78` | `8px` |
| `button.action` font-size / padding | `:79`–`:80` | `13.5px` / `8px 13px` |
| `button.action .cost` font-size / margin-left | `:82` | `12px` / `4px` |

`button.action` is used by the Move and Here groups, the recipe buttons and the
item-detail buttons. After the hub pass it is also used by the item pop-up and
the Crafting panel.

## Rules / mechanics

### A. What switches the layout

- **The one-column layout applies when the viewport is in portrait orientation,
  or narrower than 480px:**

  ```css
  @media (orientation: portrait), (max-width: 480px)
  ```

  This replaces `@media (max-width:760px)`.
- **Why the second clause.** A landscape window narrower than the grid's 476px
  floor would otherwise scroll sideways (Tom: keep a floor). No phone in
  landscape is that narrow, but a small desktop window can be.
- **480 comes from the existing comment** ("anything from 480 up removes the
  overflow"). It is a judgment call and retunable.
- **Everything in B applies under this one query.** There is one alternative
  layout, not two.
- **Tall desktop windows get it too.** A desktop window taller than it is wide
  also gets the one-column layout. That is accepted (#159), and the changelog
  states it.

### B. The one-column layout

Top to bottom:
1. The header (☰ Menu, title), unchanged.
2. `#locBar` (location, clock, Pace), unchanged.
3. `#left`: the room description, log, **Move** group and **Here** action group,
   in today's order. They stay two separate groups.
4. The **Here** panel (the containers panel).
5. The **Inventory** panel.
6. Any other sidebar panel after those two, in its existing relative order. The
   Craft panel is there until the hub pass removes it.

Also:
- `main` is one column (`grid-template-columns:1fr`), and `#left`'s border moves
  from right to bottom, as the current rule already does.
- **`#left` padding becomes `14px 16px`,** so two action buttons fit per line on a
  ~390px-wide screen.
- **Here above Inventory applies only under this query.** In the two-column
  layout, Inventory stays above Here.

### C. Everywhere (both layouts)

| rule | new value |
|---|---|
| `button.action` font-size | `12.5px` |
| `button.action` padding | `6px 10px` |
| `.actions` gap | `6px` |
| `button.action .cost` font-size | `11px` |
| `button.action .cost` margin-left | `3px` |
| `#roomDesc` line-height | `1.4` |
| `#log p` line-height | `1.35` |

These numbers come from mock-ups Tom approved at 390×844 (portrait) and 844×390
(landscape). **All are judgment calls and retunable,** and the changelog flags
them as such.

### D. The comment

The comment at `:120`–`:129` describes the 760px rule, which this pass removes.
**Rewrite it** so it states:
- the orientation trigger;
- the 480px floor and why it exists (the 476px grid floor);
- that tall desktop windows take the one-column layout by design;
- that the numbers are retunable.

Keep its note about `#left`'s border moving from right to bottom. Don't leave any
sentence describing the 760px rule.

## Design decisions to make during implementation

Record the choice in the changelog's Notes/assumptions.

- **How Here gets above Inventory.** Options:
  - **CSS `order`** on the sidebar's panels inside the query (recommended). The
    DOM stays as it is, and landscape is untouched. The panels have no ids, so
    this needs either ids or classes on the two panels (a markup touch that
    changes no behaviour), or positional selectors. Prefer ids or classes:
    positional selectors break when the hub pass removes the Craft panel, or
    when any panel is added.
  - Moving the markup and reordering for landscape instead. Not recommended,
    because it inverts which layout is the default.

## Data / schema changes

None. `SAVE_KEY` does not rotate.

## In scope

- [ ] Media query per A, replacing the 760px rule.
- [ ] One-column order per B, with Here above Inventory in that layout only.
- [ ] `#left` padding `14px 16px` in that layout.
- [ ] Compact action buttons and tighter line spacing per C, in both layouts.
- [ ] The layout comment rewritten per D.
- [ ] A check that every `button.action` still looks right at the compact size:
      Move, Here, the recipe buttons, the item-detail buttons (or the pop-up and
      Crafting panel, if the hub pass has shipped), and the game-over Restart.
      Record the check in the changelog.

## Explicitly out of scope

- **#29**: the log's `max-height:110px` and 50-entry cap. They're unchanged here,
  although the log looks different in one column.
- **#165**: adjustable panel sizes. This pass's values become its defaults.
- **An Options toggle for the layout.** Tom: only if orientation proves
  unworkable, and nothing so far says it has.
- **The hub pass** (#157, #158, #160). Removing the Craft panel is that pass's
  job, not this one's.
- **#78**: tap-target minimums and accessibility generally.

## Sections touched

- The `<style>` block only, plus ids or classes on the two sidebar panels if the
  `order` approach is taken.
- No WORLD DATA, ACTIONS, SIMULATION, PERSISTENCE or RENDERING logic.

## UI changes

- **Portrait, or narrower than 480px:** one column, and the Here panel above
  Inventory.
- **Landscape at 480px or wider:** today's two columns.
- **Everywhere:** smaller action buttons and tighter text.
- **Known tradeoff:** compact buttons are about 30px tall (about 34px today).
  Both are below the usual 44px (iOS) and 48px (Android) tap-target minimums.
  Tom chose compact knowing this, and the changelog records it as a known
  tradeoff.

## Dependencies / issue linkage

- Fulfils **#159**. The pull request carries `Closes #159`.
- Prerequisite for **#165** (adjustable panel sizes), alongside #160.
- Anything deferred during implementation is filed as a new issue at the wrap.

## Open questions for Tom

None. The last one (narrow landscape windows) was answered in the planning
session at v0.6.3 and recorded on #159.

## After implementation

Open a pull request with:
- `GAME_CONFIG.VERSION` bumped (PATCH);
- a new `CHANGELOG.md` entry naming this handoff by path, flagging every number
  in C and the 480px floor as retunable, and stating the tall-desktop-window
  behaviour and the tap-target tradeoff;
- this handoff moved to `handoffs/archive/` with `git mv`;
- `Closes #159`.
