# Ashfall Handoff — Sealed food

Current shipped version: v0.4.18
Implied version-change type: MINOR
Issue: #95 — Canned food and the can opener have no relationship — `can-opening` is a tag nothing reads

## What this is

The game contains canned food, a can opener, and no relationship between them. #95
states the gap:

> `can-opening` has no consumer — no `hasTool()`, `countByTag()`, `consumeByTag()`
> or `breakTag` reads it. Meanwhile five items are eaten straight out of
> `doConsume()` with no tool required.

Planning settled on a different shape from the one #95 proposes. The issue frames
this as a **tool gate on eating**: you may not eat a can without an opener. The
decision is that opening is **an action that transforms the item**: a sealed can is
not food you cannot eat yet, it is not food. Open it and it becomes food.

That reframing is the whole design. It also covers packaged food generally, not
only cans, and it leaves a `sealed` flag behind that spoilage (#48) and rationing
(#121) both want.

## Relevant existing state

Verified against `ashfall.html` at v0.4.18.

**The `can-opening` tag is dead.** Two references in the file: the registry entry
below, and the ITEM DATA SCHEMA comment listing it under "Declared, with no
consumer yet".

```js
can_opener: { name:"Can opener", category:"Tool", unitWeight:0.1, tags:["can-opening"] },
```

**One hand placement.** `kitchen/drawers` — the starting apartment's kitchen, one
room from spawn. (#95's body claims a second in `twobee_kitchen/drawers`; that
container holds only a kitchen knife. The issue is wrong on this point.)

**Blade-bearing items** and their current tags:

```js
kitchen_knife: { …, tags:["blade"] },
box_cutter:    { …, tags:["blade"] },
combat_knife:  { …, tags:["blade"] },
hand_axe:      { …, tags:["blunt","blade","chopping"] },
```

**Opener availability across the world**, measured at v0.4.18 — this is what makes
the gate a cost rather than a wall:

| | hand-placed | in pools |
|---|---|---|
| `can_opener` | 1 | `kitchen_tools` w7 |
| `kitchen_knife` | 2 | `kitchen_tools` w6 |
| `box_cutter` | 1 | `tools_workshop` w5 |
| `hand_axe` | 1 | `tools_workshop` w2, `hardware_store` w2 |
| `combat_knife` | 0 | `self_defense` w3 |

`kitchen_tools` is drawn by 13 containers, and 13 of its 26 total roll weight is an
opener, so a player who searches kitchens will find one quickly.

**`doConsume()` has no tool concept.** Its only guard is the presence of `restores`:

```js
function doConsume(sourceKind, index){
  const room = world[state.currentRoom];
  const src = sourceKind === "world" ? worldSlot(room, worldTab) : invSlot(invTab);
  const it = getItemAt(src && src.items, index);
  if(!it || !it.restores) return;
```

**The Eat button lives in exactly one place** — `getItemActions()`, rendered by
`renderCraftPanel()`'s detail view. There is no Eat in `renderItemList()`'s row
buttons, which are Take and Store only.

```js
if(it.restores) actions.push({ label: it.verb || "Use", onClick:()=>doConsume(side, index) });
```

**`getItemActions()` already supports disabled actions**, and `renderCraftPanel()`
renders them as `.blocked` with `btn.disabled = true`. Two actions use it today: the
Take family (`disabled: keychainBlocked`) and:

```js
actions.push({ label:"Replace batteries", disabled: countByTag("battery")<1, onClick:()=>{ … }});
```

**Food is stackable, and the merge predicate knows nothing about item state:**

```js
const STACKABLE = new Set(["Food","Medical","Materials"]);

function addToList(list, item){
  if(STACKABLE.has(item.category) && !item.durability){
    const existing = list.find(i=> i.itemId===item.itemId && i.category===item.category && !i.durability);
    if(existing){ existing.qty += item.qty; return; }
```

This is the crux of the implementation. Without a `sealed` comparison here, an
opened can merges straight back into the sealed stack and either opens all of them
or vanishes.

**`addToList()` returns nothing today**, and no caller reads a return value.

**The per-instance mutable-boolean pattern already exists.** `flashlight` and
`portable_radio` carry `on` and `hasBatteries` in the registry, flipped on the
instance by actions in `getItemActions()`, read by the detail view. `sealed` is the
same pattern and should look like it.

**The detail box renders one conditional line today:**

```js
if(it.durability){
  const durLine = document.createElement("div");
  durLine.textContent = it.durability.mode === "uses"
    ? `${Math.round(it.durability.current)}/${it.durability.max} uses`
    : it.hasBatteries === false
      ? "No batteries installed"
      : `${Math.round(100*it.durability.current/it.durability.max)}% charge${it.on ? " — On" : " — Off"}`;
  box.appendChild(durLine);
}
```

**Food items with no `restores`** — currently `category:"Food"` and inedible:
`rice_bag`, `coffee_grounds`, `dry_pet_food`, `canned_pet_food`, `baby_formula`,
plus the three deliberately-inedible spoiled ones (`spoiled_milk`, `moldy_bread`,
`rotten_produce`).

**The split mechanic exists** — `normalizeQty()` plus the decrement/splice/`addToList`
sequence in `doTake()`/`doStore()`, and the safety rules commented above them.

## Rules / mechanics

### The two fields

`sealed` and `opensWith` are per-instance item fields, declared in `ITEM_REGISTRY`.

- **`sealed`** — `true` on a registry entry means every instance starts sealed. Its
  absence is the common case and means the item is simply not a packaged thing.
  Opening flips it to `false` on that instance. So three states are distinguishable
  and all three are meaningful: `undefined` (never packaged), `true` (sealed),
  `false` (opened).
- **`opensWith`** — a capability tag naming what is required to open it. Absent on a
  sealed item means it opens by hand.

### The gate is a single tag, not a set

`can-opening` is added as a second tag to every item that can get a can open. This
is CLAUDE.md's own rule — *"A new item that should behave like an existing one gets
the same tag"* — and it means the check is one existing function, `hasTool()`, with
no lookup table and no new concept.

The tag therefore means **"can get a can open"**, not "is a can opener". Update the
ITEM DATA SCHEMA comment accordingly: `can-opening` moves out of the
"Declared, with no consumer yet" list and into the list of tags read by a mechanic.

`prying` is deliberately **not** in the gate. A crowbar does not open a can, and
#111 has already designated prying's future consumer (re-gating vehicle forcing once
#66 makes the crowbar reachable). Leave it in the "no consumer yet" list.

### Eat

`doConsume()` gains a defensive guard, matching the file's existing convention that
transfer functions validate independently of their caller's gate:

```js
if(!it || !it.restores || it.sealed) return;
```

And the action is not offered at all while sealed:

```js
if(it.restores && !it.sealed) actions.push({ label: it.verb || "Use", onClick:()=>doConsume(side, index) });
```

### Open

A new `doOpen(sourceKind, index)` in **INVENTORY / ITEM SYSTEM — quantity-changing
transfers**, beside `doConsume()`, following the six safety rules commented at the
top of that block.

```
1. Resolve src and it defensively via getItemAt(). Bail silently if null.
2. Bail if !it.sealed.
3. Bail if it.opensWith && !hasTool(it.opensWith).
4. it.qty -= 1; if(it.qty <= 0) src.items.splice(index, 1);
5. const opened = addToList(src.items, { ...it, qty:1, sealed:false });
6. detailItem = { uid: ensureUid(opened), side };
7. log(…)   // see below
8. render();
```

Notes on that sequence, each of which is load-bearing:

- **Opening exactly one unit is a split.** `Canned soup ×3` becomes `×2` sealed plus
  `×1` open. Step 4 before step 5 matches the rule that a source stack is removed
  only once its qty reaches exactly zero.
- **No capacity check is needed and none should be added.** The opened unit goes back
  into the same list the sealed one came from, at the same `unitWeight`. One unit out,
  one unit in — the list's total weight is unchanged.
- **`{ ...it, qty:1, sealed:false }` copies `_uid`.** `addToList()` already deep-clones
  and strips it, so the new entry gets a fresh identity. This is why step 5 must go
  through `addToList()` rather than pushing directly.
- **Step 6 needs `addToList()` to return the entry** it created or merged into — see
  Data / schema changes. Without it, opening the last sealed unit closes the detail
  view, because `detailItem` still points at a uid that was just spliced out and
  `renderCraftPanel()` resets to the recipe list.

The action, offered only when it can be performed:

```js
if(it.sealed && (!it.opensWith || hasTool(it.opensWith)))
  actions.push({ label:"Open", onClick:()=>doOpen(side, index) });
```

### The merge predicate

`addToList()`'s find gains a `sealed` comparison:

```js
const existing = list.find(i=> i.itemId===item.itemId && i.category===item.category
                            && !i.durability && !!i.sealed === !!item.sealed);
```

`!!` on both sides so `undefined` and `false` compare equal. Opened items stack with
opened items of the same id; sealed with sealed; the two never merge.

### Log lines

Both collapse on a repeat key, the way `doConsume()` does with
`"consume:" + (it.itemId || it.name)`. Use `"open:" + (it.itemId || it.name)`.
Neither takes a CSS class — opening is neutral, not a win, and an unclassed line
takes `fresh` in `log()`.

| case | line |
|---|---|
| `opensWith` present | `You work the lid off the ${it.name.toLowerCase()}.` |
| no `opensWith` | `You break the seal on the ${it.name.toLowerCase()}.` |

"Break the seal" rather than "tear open" because the no-tool group spans a box, a
bag and a jar, and only one of them tears.

### The detail view

A line in `renderCraftPanel()`'s `detailBox`, beside the existing `durability` one:

```js
if(it.sealed !== undefined){
  const sealLine = document.createElement("div");
  sealLine.textContent = it.sealed ? "Sealed" : "Opened";
  box.appendChild(sealLine);
}
```

### The general rule this pass establishes

**An action offered on an item you are inspecting appears only if you can perform
it.** Applied here to Eat, and to one existing offender:

```js
// before
actions.push({ label:"Replace batteries", disabled: countByTag("battery")<1, onClick:()=>{ … }});
// after
if(countByTag("battery") >= 1) actions.push({ label:"Replace batteries", onClick:()=>{ … }});
```

Two things that look like the same case and are **not**, and must be left alone:

- **`renderCraftPanel()`'s recipe list.** It shows unavailable recipes with a
  `(needs …)` string. That is a catalogue — hiding them makes crafting
  undiscoverable. Unchanged.
- **Keychain-blocked Take.** With the keychain tab open, Take is disabled on every
  non-Key item. Hiding it would read as "this item cannot be taken", which is false
  — it just cannot go *there*. Stays disabled.

Add a short comment at the `disabled` sites that remain, saying why they are
disabled rather than hidden, so the rule does not read as inconsistently applied.

## Design decisions to make during implementation

- **Where `doOpen()` lives.** Recommended: INVENTORY / ITEM SYSTEM — quantity-changing
  transfers, beside `doConsume()`, since it is a stack-splitting mutation and inherits
  that block's six safety rules. The alternative is WORLD INTERACTION beside the other
  `do*` actions, which would separate it from the rules it must follow. Record the
  choice in the changelog.
- **Whether `addToList()` returns the merged entry or the pushed entry** — it must
  return whichever one the item ended up in, in both branches. No existing caller
  reads the return, so this is additive. If the implementation finds a reason not to
  change `addToList()`, the fallback is for `doOpen()` to re-find the opened entry by
  scanning `src.items`; say which was used and why.

## Data / schema changes

**New item schema fields** (ITEM DATA SCHEMA comment must document both):

- `sealed` — boolean. `true` in the registry; flipped to `false` on the instance by
  `doOpen()`. Absent means not a packaged item.
- `opensWith` — capability tag required to open. Absent on a sealed item means it
  opens by hand.

**Registry edits — `can-opening` added as a second tag** (4 items):

| item | tags after |
|---|---|
| `kitchen_knife` | `["blade","can-opening"]` |
| `box_cutter` | `["blade","can-opening"]` |
| `combat_knife` | `["blade","can-opening"]` |
| `hand_axe` | `["blunt","blade","chopping","can-opening"]` |

`hand_axe` is a judgment call — an axe opens a can brutally but it opens it. Retunable.

**Registry edits — `sealed` / `opensWith`** (9 items):

| item | `sealed` | `opensWith` |
|---|---|---|
| `canned_soup` | `true` | `"can-opening"` |
| `canned_beans` | `true` | `"can-opening"` |
| `canned_corn` | `true` | `"can-opening"` |
| `canned_tuna` | `true` | `"can-opening"` |
| `canned_pet_food` | `true` | `"can-opening"` |
| `baby_formula` | `true` | `"can-opening"` |
| `cereal_box` | `true` | — |
| `peanut_butter` | `true` | — |
| `dry_pet_food` | `true` | — |

**Registry edits — new `restores`** (3 items). All three are balance values with no
prior convention behind them and are **retunable**:

| item | `restores` | `verb` | reasoning |
|---|---|---|---|
| `canned_pet_food` | `{hunger:15}` | `"Eat"` | same can size as `canned_tuna` (20), slightly worse |
| `baby_formula` | `{hunger:18}` | `"Eat"` | dry powder; no thirst value — fluids are #47/#52 |
| `dry_pet_food` | `{hunger:25}` | `"Eat"` | a 1.5 kg bag: substantial but far worse per kg than anything else |

No `illnessChance` on any of the three. All are sealed and safe — they are grim, not
spoiled.

`dry_pet_food` carries a known awkwardness: one unit is a whole bag, and without
rationing, eating it is a single click that consumes 1.5 kg at once. That is #121's
to fix, not this pass's. The value is set on the assumption that a unit is the bag.

**Mechanic change to `addToList()`** — the merge predicate gains a `sealed`
comparison, and the function gains a return value.

**No PLAYER STATE changes. No room/container/exit schema changes.**

**Save compatibility:** `sealed` lands on item instances, which are deep-cloned into
the world and serialized. This is new persistent state, so `SAVE_KEY` rotates —
`versionCompat()` goes `0.4` → `0.5` and existing browser saves stop auto-loading.
That is the intended seam; no backfill is needed or wanted.

## In scope

- [ ] `sealed` and `opensWith` fields, documented in the ITEM DATA SCHEMA comment
- [ ] `can-opening` added to the four blade items; schema comment updated to move it
      out of the no-consumer list
- [ ] `doOpen()` with the split, per the eight steps above
- [ ] `addToList()` merge predicate learns `sealed`; returns the entry
- [ ] Eat hidden while sealed, in `getItemActions()`; `doConsume()` guards defensively
- [ ] Open offered only when performable
- [ ] `Replace batteries` conditional rather than disabled
- [ ] Comments at the two remaining `disabled` sites saying why they stay disabled
- [ ] `Sealed` / `Opened` line in the detail box
- [ ] Nine items sealed, three items given `restores`
- [ ] `GAME_CONFIG.VERSION` bumped MINOR

## Explicitly out of scope

- **A screwdriver item.** Discussed and deferred. A new registry entry plus pool
  placements is *instance* content, and CLAUDE.md forbids instance data riding along
  with a mechanics change. The gate works on day one without it. File it as a content
  issue at wrap-time; when it lands it gets `can-opening` and nothing else changes.
- **Any cost for opening a can with a blade.** Settled during planning: no reduced
  yield, no time cost, no injury risk. Opening either works or it does not. The blade
  path gets its cost from #116 (tool wear) when that ships.
- **Tool wear — #116.** Nothing in this pass decrements anything.
- **`rice_bag` and `coffee_grounds` are deliberately not sealed.** Neither has
  `restores`, so sealing them yields an Open button that produces something still
  inedible. They become sealed in the pass that makes them usable — #120.
- **Individually-wrapped snacks are deliberately not sealed**: `granola_bars`,
  `candy_bar`, `crackers`, `potato_chips`, `chewing_gum`. The wrapper is part of
  eating, and an Open click there buys a second click and no decision.
- **The three spoiled Food items** (`spoiled_milk`, `moldy_bread`, `rotten_produce`)
  stay inedible. That is #48's ground.
- **Rationing — #121.** Eat is still one whole unit.
- **Spoilage — #48.** `sealed` is laid down here and #48 is expected to read it, but
  nothing in this pass decays.
- **#119, #120, #96.** Reachable crafting, two-stage cooking, the propane torch. All
  touch food and none is a prerequisite. In particular, do **not** widen `hasTool()`
  to reach room containers — reachability is #119's to define, and defining it twice
  is exactly what that issue exists to prevent. `hasTool()` stays inventory-only here.

## Sections touched

- **WORLD DATA** — `ITEM_REGISTRY` (tags, `sealed`/`opensWith`, `restores`) and the
  ITEM DATA SCHEMA comment. This is definition data the new rule reads, which the
  Project Guide's Part 2 bound permits riding along with the mechanic.
- **INVENTORY / ITEM SYSTEM** — `addToList()`, `doConsume()`, the new `doOpen()`,
  `getItemActions()`.
- **RENDERING** — `renderCraftPanel()`'s detail box only.

Nothing in PLAYER STATE, CORE UTILITIES, WORLD INTERACTION, SURVIVAL / TIME
SIMULATION, CRAFTING, FIRE / COOKING, PERSISTENCE, or MAP.

## UI changes

- **Sealed food shows an Open button and no Eat button.** Once opened, the reverse.
- **Open is absent entirely** when the required tool is not held — not greyed out.
- **The detail box gains a `Sealed` / `Opened` line** for packaged items.
- **`Replace batteries` disappears** when no `battery`-tagged item is carried, rather
  than appearing greyed.
- **Two new log lines**, collapsing on repeat.
- **A stack visibly splits when opened** — `Canned soup ×3` becomes `Canned soup ×2`
  and `Canned soup ×1` in the same list, distinguishable only by opening the detail
  view. That is a known readability limit of the current item list, which renders
  `name ×qty — kg (category)` and has nowhere to show item state. Worth an issue at
  wrap-time if it reads badly in play; do not redesign the list in this pass.

## Dependencies / issue linkage

- **Fulfils #95.** The PR carries `Closes #95`.
- **Expected to leave deferred**, and to be filed as new issues at wrap-time:
  - the screwdriver as a content addition
  - the item-list readability limit above, if it reads badly in play
- **Related, not prerequisites:** #116 (tool wear — will charge the blade this pass
  makes useful), #48 (spoilage — the first real consumer of `sealed`), #121
  (rationing — shares the stack-splitting problem; whichever ships second extends
  the merge predicate rather than rewriting it), #120 (makes `rice_bag` and
  `coffee_grounds` worth sealing), #111 (keeps `prying` reserved).

## Open questions for Tom

None. Every design and scope question was resolved during the planning session at
v0.4.18.

## After implementation

Open a pull request carrying the MINOR version bump and a new `CHANGELOG.md` entry
per `docs/CHANGELOG_GUIDE.md`, naming this handoff by the path it was read at
(`handoffs/sealed-food.md`), recording both "Design decisions" resolutions, and
closing the issue with `Closes #95`. Move this file to `handoffs/archive/` with
`git mv` in the same pull request. Tag the merge commit, naming the commit
explicitly.
