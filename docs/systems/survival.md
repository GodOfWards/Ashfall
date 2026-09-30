# Survival

ARCHITECTURE sections: CONFIG / CONSTANTS (STAMINA / FATIGUE SYSTEM
CONSTANTS); SURVIVAL / TIME SIMULATION (the STAMINA / FATIGUE SYSTEM
sub-section).

## Purpose

Effort costs something, and the cost lingers. Work and hurrying spend
Stamina, then build Fatigue; staying awake and recovering spend Energy; and
sleep is what gives Energy back, as far as Fatigue lets it. Low Hunger or
Thirst slows recovery, so neglecting the body makes every effort dearer.

## Model

**The vitals it owns.** Stamina, Fatigue and Energy, each on the 0–100 scale
of `state.vitals`, with two marks in `state`: `lastExertionMinute`, the last
minute anything was spent, and `lastWakeMinute`, the end of the last completed
sleep. Hunger and Thirst fall in every clock step (`applyHungerThirst()`,
[Time](time.md)); this system only reads them.

**Exertion.** A task never touches Stamina or Fatigue. It declares an
Exertion figure, beside itself, and hands it to `applyExertion()`: Stamina
pays first, and whatever Stamina can't cover becomes Fatigue, which stops at
the top of its scale. Every spend stamps `lastExertionMinute`. The tasks that
spend today: jogging, per minute moved (`JOG_EXERTION_PER_MIN`, in
`doMove()`); moving over the carry limit, at every gait
(`OVERLOAD_MAX_EXERTION_PER_MIN`); chopping a tree (`CHOP_TREE_EXERTION`);
fishing (`FISH_EXERTION`); forcing a door (`FORCE_DOOR_EXERTION`).

**Awake recovery.** Awake time runs in steps of at most a minute
(`runAwakeStep()`), each a clock step and then `recoveryStep()`, so the
rules below are read at minute resolution however long the action. One step,
in order:

1. Within `STAMINA_RECOVERY_DELAY_MIN` of the last Exertion
   (`isExertionDelayActive()`), nothing recovers; Energy drains at the
   baseline.
2. Otherwise, below its cap, Stamina recovers. The cap is set by Energy, in
   bands (`staminaMaxForEnergy()`). The rate awake is
   `BASELINE_STAMINA_RATE`, times an Energy band's multiplier
   (`energyRecoveryMultiplier()`), less the Hunger and Thirst penalty
   (`hungerThirstRecoveryPenalty()`). Energy drains at a multiple of the
   baseline meanwhile: recovering costs Energy.
3. Otherwise, with Stamina at its cap and Fatigue above zero
   (`fatigueRecoveryAllowed()`), Fatigue falls at `FATIGUE_RECOVERY_RATE`,
   and Energy drains at a larger multiple still.
4. Otherwise Energy drains at the baseline alone (`applyEnergyBaseline()`).

The Hunger and Thirst penalty is a fixed share for each of the two below its
threshold (`LOW_HUNGER_THRESHOLD`, `LOW_THIRST_THRESHOLD`), added, never
multiplied.

**Rest** (`doRest()`) is `REST_DURATION_MIN` of the same steps in rest mode:
Stamina recovers at `REST_STAMINA_RATE` whatever Energy and the vitals say,
and recovery adds nothing to Energy's baseline drain. Rest never restores
Energy.

**Sleep** (`doSleep()`) suspends the awake system: its steps are clock steps
alone, and Energy rises at `SLEEP_ENERGY_RATE` instead of draining. Fatigue
sets how far: the ceiling is what Fatigue leaves of the scale
(`sleepEnergyCeiling()`), read once at the start. A sleep is offered only off
cooldown, `SLEEP_COOLDOWN_MIN` after the last one ended
(`sleepOffCooldown()`), and only while Energy is below the ceiling
(`sleepRestoresEnergy()`); its button shows how long it will take
(`estimateSleepMinutes()`).

- **Completed:** Energy is set exactly to the ceiling, Fatigue clears, and
  both marks are stamped, so the cooldown starts.
- **Woken early** by a waking clock event ([Time](time.md)): Energy keeps
  what it gained, Fatigue falls by the share of the sleep taken, and no
  cooldown starts, so Sleep is offered again at once.

**The gait lock.** At `FATIGUE_GAIT_LOCK` the pace is held to Sneak
(`gaitLocked()`). The player's chosen pace, `state.gait`, is left as it is;
`effectiveGait()` is the pace actually kept, and the choice returns by itself
once Fatigue falls.

**Collapse.** When an advance of time (`advanceTime()`) leaves Energy at zero,
the player collapses. Every `COLLAPSE_BLACKOUT_EVERY`-th collapse is a
blackout: `COLLAPSE_BLACKOUT_MIN` of awake steps, counted as asleep for clock
events, after which Energy is set to `COLLAPSE_BLACKOUT_ENERGY` (or its share
for the minutes taken, if a waking event cut it short). Any other is a
stumble: `COLLAPSE_STUMBLE_MIN` of steps, then `COLLAPSE_STUMBLE_ENERGY`
added.

## Invariants

- **Only this system writes Stamina and Fatigue.** Tasks declare Exertion
  through `applyExertion()`; recovery (`recoveryStep()`) and sleep
  (`doSleep()`) are the only other writers.
- **Fatigue recovers only at the current Stamina cap**, the Energy-set one
  (`staminaMaxForEnergy()`), never a flat full scale, so a low-Energy cap
  can't be worked around.
- **Sleep never lowers Energy**, and a sleep that would restore nothing is
  not offered. At full Fatigue the ceiling is zero: that Fatigue is worked
  off awake, never wiped by an empty sleep.
- **One pace for pricing and charging.** Everything that prices or charges
  movement reads `effectiveGait()`: `moveMinutes()` and `doMove()`'s jogging
  Exertion. `doMove()` reads it once, before time passes, since recovery
  during the move can lift the lock part-way. `state.gait` is written only by
  the pace bar.

## Entry points

- `applyExertion()`: what a task calls to spend.
- `advanceTime()`: awake time, with recovery and collapse; `doRest()`,
  `doSleep()`: the other two ways time passes ([Time](time.md)).
- `recoveryStep()`: one step of awake recovery, for those callers alone.
- `effectiveGait()`, `gaitLocked()`: the pace kept, and whether it is held.
- `sleepAvailable()`, `sleepOffCooldown()`, `sleepRestoresEnergy()`,
  `estimateSleepMinutes()`: what RENDERING reads to offer Sleep or say why
  not.

## Constants

- `STAMINA_RECOVERY_DELAY_MIN`: how long after an Exertion recovery waits.
- `BASELINE_STAMINA_RATE`: Stamina recovered per minute awake, before the
  multipliers. Chopping's Exertion is derived from it.
- `REST_STAMINA_RATE`: Stamina recovered per minute of Rest.
- `FATIGUE_RECOVERY_RATE`: Fatigue recovered per minute, awake or resting.
- `REST_DURATION_MIN`: how long one Rest lasts.
- `SLEEP_ENERGY_RATE`: Energy regained per minute asleep.
- `SLEEP_COOLDOWN_MIN`: how long after waking before Sleep is offered again.
- `LOW_HUNGER_THRESHOLD`, `LOW_THIRST_THRESHOLD`: below these, recovery
  slows.
- `FATIGUE_GAIT_LOCK`: the Fatigue at which the pace is held to Sneak.
- `COLLAPSE_BLACKOUT_EVERY`, `COLLAPSE_BLACKOUT_MIN`,
  `COLLAPSE_BLACKOUT_ENERGY`, `COLLAPSE_STUMBLE_MIN`,
  `COLLAPSE_STUMBLE_ENERGY`: how often a collapse is a blackout, and what
  each kind costs and gives back.
- `DECAY`: Energy's baseline drain per minute, shared with Hunger and
  Thirst.

## Costs

- **Per step:** a handful of comparisons on the player's own vitals. Nothing
  here reads the world.
- **Per event:** none. The system has no scheduled events; a collapse is
  checked once per advance of time.

Nothing in it is proportional to the world.
