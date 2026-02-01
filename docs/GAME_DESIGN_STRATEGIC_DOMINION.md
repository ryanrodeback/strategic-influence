# STRATEGIC DOMINION
## A Risk-Inspired Hexagonal Territory Game

*"The supreme art of war is to subdue the enemy without fighting."* - Sun Tzu

---

# TABLE OF CONTENTS

1. [Design Philosophy](#design-philosophy)
2. [Core Constraints](#core-constraints)
3. [Variation 1: FORTIFIED REALM](#variation-1-fortified-realm)
4. [Variation 2: MARCH OF EMPIRES](#variation-2-march-of-empires)
5. [Variation 3: STRONGHOLD](#variation-3-stronghold)
6. [Elegant Enhancements](#elegant-enhancements)
7. [Comparative Analysis](#comparative-analysis)

---

# DESIGN PHILOSOPHY

This document explores three distinct approaches to creating a Risk-like territory control game with elegant simplicity. Each variation uses the same foundational constraints but emphasizes different strategic pillars:

| Variation | Core Focus | Complexity | Primary Tension |
|-----------|------------|------------|-----------------|
| Fortified Realm | Defensive positioning | Lowest | Build vs. Expand |
| March of Empires | Time/distance as strategy | Medium | Speed vs. Strength |
| Stronghold | Fortification levels | Medium | Concentrate vs. Spread |

**Shared Design Goals:**
- Rules explainable in 5 minutes
- Strategic depth discoverable over many plays
- Tension between expansion and consolidation
- Meaningful decisions every turn
- No runaway leader problem

---

# CORE CONSTRAINTS

All three variations share these foundational elements:

## The Board

```
     Hexagonal Tile Layout (19 tiles for 2 players)

              ⬡ ⬡ ⬡
             ⬡ ⬡ ⬡ ⬡
            ⬡ ⬡ ⬡ ⬡ ⬡
             ⬡ ⬡ ⬡ ⬡
              ⬡ ⬡ ⬡

     Each ⬡ represents a hexagonal tile
     Settlements are placed on CORNERS (vertices)
```

**Key Geometry:**
- Each hexagon has 6 corners (vertices)
- Each corner is shared by up to 3 hexagons
- A standard 19-hex board has 54 unique corner positions
- Corners are connected along hex edges (each corner connects to 3 others)

**Why Corners, Not Tiles:**
- Creates natural chokepoints and defensive lines
- Mirrors Catan's settlement placement
- More nuanced positioning than tile control
- Naturally limits expansion (fewer valid positions)

## Starting Conditions

- Each player begins with exactly ONE settlement
- Starting positions are on opposite sides of the board
- All terrain is uniform (no bonuses, no variation)

## Victory Condition

The player who controls the most settlements when the game ends wins.

---

# VARIATION 1: FORTIFIED REALM

*"In war, the way is to avoid what is strong and strike at what is weak."* - Sun Tzu

## 1.1 Game Overview

**FORTIFIED REALM** is the simplest of the three variations. Each settlement has a single "strength" number representing combined troops and fortifications. The core tension is between strengthening existing positions and expanding to new corners.

**The Hook:** Your settlements grow stronger each turn they don't act, creating a natural push-pull between patient fortification and aggressive expansion.

**Unique Feature:** Passive growth - settlements gain strength simply by waiting, rewarding patience and punishing overextension.

---

## 1.2 Complete Rules

### Components
- 19 hexagonal tiles (arranged in standard Catan pattern)
- 54 corner markers (small discs or cubes)
- Strength tokens (1, 3, 5 denominations) or a track
- 2 player colors

### Setup
1. Arrange the 19 hex tiles in the standard pattern
2. Each player places ONE settlement on a corner of their choice
   - Player 1 chooses a corner on the "south" edge of the board
   - Player 2 chooses a corner on the "north" edge
   - Starting corners must be at least 4 connections apart
3. Each starting settlement begins with Strength 3
4. Determine first player randomly

### Turn Structure

On your turn, for EACH settlement you control, choose exactly ONE action:

#### Action A: FORTIFY (Rest)
- The settlement does nothing this turn
- At end of turn, it gains +1 Strength
- Maximum Strength is 7

#### Action B: EXPAND (Build New Settlement)
- Choose an unoccupied corner connected to this settlement
- Spend 2 Strength from the origin settlement
- Place a new settlement with Strength 1
- Origin must have at least 3 Strength to expand

#### Action C: ATTACK (Assault Enemy Position)
- Choose an enemy settlement connected to this settlement
- Compare attacker's Strength vs defender's Strength
- **Combat Resolution:**
  - If Attacker > Defender: Attacker wins
  - If Attacker <= Defender: Defender wins
  - Winner keeps their settlement; loser's settlement is removed
  - Winner's settlement loses Strength equal to the loser's Strength
  - If winner would drop to 0 or below, both settlements are destroyed

**Connection Rule:** Two corners are "connected" if they share the edge of the same hexagon (there are exactly 3 connections per corner).

### Turn Resolution Order
1. All FORTIFY actions happen first (order doesn't matter)
2. All EXPAND actions happen simultaneously
3. All ATTACK actions happen simultaneously
   - If two players attack each other, resolve as mutual combat (both are attackers)
4. Strength growth from FORTIFY happens last

### Game End

The game ends when:
- One player controls no settlements (immediate loss), OR
- 25 turns have passed

After 25 turns, the player with more settlements wins. Ties are broken by total Strength.

### Visual Reference: Corner Connections

```
          A ─── B
         / \   / \
        /   \ /   \
       F ─── G ─── C
        \   / \   /
         \ /   \ /
          E ─── D

From corner G, you can:
- EXPAND to A, B, C, D, E, or F (if empty)
- ATTACK enemy at A, B, C, D, E, or F (if occupied by enemy)
- FORTIFY (do nothing, gain +1 strength)
```

---

## 1.3 Mechanics Deep Dive

### Why This Works: The Fortification Economy

The core mechanic is the Strength economy:

| Action | Strength Cost | Strength Gain | Net Effect |
|--------|---------------|---------------|------------|
| Fortify | 0 | +1 at end of turn | Slow accumulation |
| Expand | -2 | Creates Str 1 settlement | Territory gain, resource split |
| Attack | -Enemy Str (if win) | N/A | Territory flip, attrition |

**The Central Tension:**
- Expanding costs 2 Strength and creates a weak position
- Fortifying gains Strength but doesn't gain territory
- Attacking risks losing everything but can flip territory

### The Fortify-Expand-Attack Triangle

```
        FORTIFY
       /        \
      /          \
     /    WINS    \
    / (patient     \
   /   beats        \
  /    overextended) \
 /                    \
EXPAND ──────────── ATTACK
        LOSES TO
    (weak targets
     for attack)
```

- **Fortify beats Expand:** A player who expands creates weak Str 1 settlements that are easy targets
- **Attack beats Fortify:** A player who only fortifies gets surrounded and eventually overwhelmed
- **Expand beats Attack:** A player who attacks constantly depletes strength while expander grows territory

### Connection Geometry

The 3-connection limit per corner creates natural strategic formations:

**Defensive Line:** A row of settlements blocking advancement
```
     ● ─── ● ─── ●
      Enemy cannot pass without engaging
```

**Forward Position:** A settlement behind enemy lines
```
     ○ ─── ○
      \   /
       \ /
        ●   (Your settlement behind their line)
```

**Chokepoint Control:** Corners where 3 hexes meet
```
     These corners have maximum 3 connections
     but can be attacked from 3 different directions
```

---

## 1.4 Gameplay Analysis

### Opening Phase (Turns 1-5)

**Objective:** Establish 2-3 strong settlements before contact

**Typical Opening:**
1. Turn 1: Fortify (starting settlement now Str 4)
2. Turn 2: Expand toward center (Str 4 -> Str 2 origin, new Str 1)
3. Turn 3: Fortify both (now Str 3 and Str 2)
4. Turn 4: Expand from stronger position
5. Turn 5: Prepare for contact with opponent

**Opening Principles:**
- Don't expand too quickly (creates weak targets)
- Don't fortify too long (opponent claims territory)
- Expand toward the center (more connections = more options)

### Mid-Game Phase (Turns 6-18)

**Objective:** Control the center, set up attack opportunities

**Key Patterns:**
- **Overextension Punishment:** Attack opponent's weak Str 1-2 settlements
- **Line Formation:** Create connected settlements that protect each other
- **Flanking:** Expand around enemy strong points rather than attacking directly

**Critical Decision:**
```
Opponent has Str 5 at center.
You have Str 4 adjacent to it.

Option A: Attack now (you lose if Str 4 vs Str 5)
Option B: Fortify to Str 5, attack next turn (even odds)
Option C: Expand elsewhere, surround them
Option D: Let them attack you (defender wins ties)
```

### End-Game Phase (Turns 19-25)

**Objective:** Maximize settlement count or secure lead

**End-Game Calculation:**
- Count settlements: Who is ahead?
- Calculate attack potential: Can you flip the lead?
- Evaluate fortify value: Strength only matters for tiebreaker

**Closing Moves:**
- If ahead: Fortify everything, avoid risky attacks
- If behind: Aggressive expansion or attacks to flip territories
- If tied: Look for attacks with favorable Strength differentials

---

## 1.5 Game Experience

### Emotional Arc

**Opening:** Anticipation, planning, hope
- "I'll build a fortress here and control the center..."

**Mid-Game:** Tension, calculation, adaptation
- "Do I attack their Str 3 with my Str 4? What if they fortified it?"

**End-Game:** Drama, risk-taking, resolution
- "I'm down by one settlement. I MUST attack or I lose."

### Decision Quality

Every decision in Fortified Realm has:
1. **Clear options:** 3 possible actions per settlement
2. **Meaningful tradeoffs:** Each action has distinct costs/benefits
3. **Opponent interaction:** Your choice depends on their likely response
4. **Future impact:** This turn's decision affects next turn's options

### What Makes It Fun

- **Satisfying buildup:** Watching your Str 3 become Str 7 feels powerful
- **Tense attacks:** "Will my Str 5 beat their unknown Strength?"
- **Punishing mistakes:** Overextension is clearly punished
- **Comeback potential:** A well-timed attack can flip the game

---

## 1.6 Strategic Depth

### Advanced Concepts

**1. Strength Efficiency**
- A Str 6 beats a Str 5, leaving a Str 1
- Two Str 3s can't be beaten by a single Str 6
- Conclusion: Spread strength across multiple settlements

**2. The Defense Advantage**
- Ties go to defender (Attacker must be strictly greater)
- This means you should let opponents attack into your prepared positions
- "Invite attack, then counter-attack their weakened force"

**3. Expansion Timing**
- Expanding costs 2 Strength (40-66% of typical holdings)
- Best to expand AFTER opponent has committed their actions
- Since actions are simultaneous, this requires prediction

**4. Positional Play**
- Center positions have more connections = more flexibility
- Edge positions are easier to defend but harder to expand from
- Control center corners to limit opponent's expansion options

**5. Tempo and Initiative**
- The player with more settlements has more actions per turn
- Leading player can afford to fortify while ahead
- Trailing player must take risks to catch up

### Hidden Complexity

The simple ruleset hides sophisticated strategic layers:

| Surface Rule | Deep Implication |
|--------------|------------------|
| Strength cap of 7 | Prevents infinite turtling |
| Expand costs 2 | Creates critical timing windows |
| Defender wins ties | Rewards patience and prediction |
| Simultaneous resolution | Enables bluffing and prediction games |
| 3 connections max | Creates natural defensive formations |

---

## 1.7 Why It Works

### Simplicity Analysis

**Total Rules to Learn:**
- 3 actions (Fortify, Expand, Attack)
- 1 combat resolution (compare Strength)
- 1 board geometry (corners, 3 connections)
- 1 victory condition (most settlements)

**Emergent Complexity:**
- Timing decisions (when to attack vs. fortify)
- Positional play (which corners matter most)
- Resource management (Strength allocation)
- Opponent modeling (what will they do?)

### Risk DNA

How FORTIFIED REALM captures Risk's essence:

| Risk Element | Fortified Realm Equivalent |
|--------------|---------------------------|
| Territory control | Settlement control |
| Troop accumulation | Strength growth via Fortify |
| Calculated attacks | Strength comparison combat |
| Expansion pressure | Expand action economics |
| Defensive positioning | Corner connection geometry |

### The "One More Turn" Factor

Players want to keep playing because:
- "I need one more turn to reach Str 7"
- "If I can just expand there, I'll cut them off"
- "Their position is weak - one good attack changes everything"

---

# VARIATION 2: MARCH OF EMPIRES

*"Let your plans be dark and impenetrable as night, and when you move, fall like a thunderbolt."* - Sun Tzu

## 2.1 Game Overview

**MARCH OF EMPIRES** introduces time as the critical strategic dimension. Armies don't teleport - they march across the board, and distant objectives require multiple turns to reach. This creates opportunities for interception, flanking, and the fog of war.

**The Hook:** When you commit forces to a march, they're locked in for multiple turns - revealing your intentions and creating windows of vulnerability.

**Unique Feature:** Multi-turn movement creates commitment, anticipation, and interceptibility.

---

## 2.2 Complete Rules

### Components
- 19 hexagonal tiles
- 54 corner markers
- March tokens (numbered 1, 2, 3 to show turns remaining)
- Army tokens (flat strength number)
- 2 player colors

### Setup
1. Arrange hexagonal board in standard pattern
2. Each player places ONE settlement on their starting edge
3. Each starting settlement has an Army of Strength 4
4. Settlements always have Strength 0 (they're static positions)

**Key Distinction:** Settlements and Armies are separate. Settlements are static positions; Armies are mobile forces.

### Core Concepts

**Settlements:**
- Cannot move
- Have no intrinsic strength
- Can spawn new armies (through MUSTER action)
- Are captured when an enemy army enters their corner

**Armies:**
- Have a Strength value (1-6)
- Can move between connected corners
- Can attack enemy armies
- Must end movement on a corner (cannot stop mid-march)

**March Tokens:**
- When you give a MARCH order, you place tokens showing the path
- Each turn, the army advances one connection
- Enemy can see your march tokens (no hidden movement)

### Turn Structure

On your turn, for each ARMY you control:

#### Action A: MUSTER (Create Army)
- Your army must be ON a settlement you control
- Reduce army strength by X, create new army with Strength X
- New army appears at the same corner
- Minimum strength for any army is 1

#### Action B: GARRISON (Defensive Stance)
- Army remains in place
- Gains +1 Strength (max 6)
- If on your settlement, that settlement cannot be captured this turn

#### Action C: MARCH (Multi-Turn Movement)
- Declare a path of 1-3 corners (each connected to the previous)
- Place march tokens numbered 1, 2, 3 (or fewer for shorter marches)
- Army will move one step per turn until reaching destination
- March cannot be canceled once started
- Marching army CAN be attacked while moving

For each SETTLEMENT you control (without a garrisoned army):

#### Action D: BUILD (Create New Settlement)
- Spend nothing
- Place a new settlement on any empty corner CONNECTED to this settlement
- You may only BUILD once per settlement per turn
- New settlement is undefended unless you march an army to it

### March Resolution

At the START of each turn (before new orders):
1. All marching armies advance one step on their path
2. If two armies meet on the same corner, combat occurs
3. If an army reaches an undefended enemy settlement, it is captured

### Combat Resolution

When armies meet (from march or attack):
- Higher Strength wins
- Winner loses Strength equal to loser's Strength
- Loser is destroyed
- If tie: Both are destroyed

**Interception Rule:** If an army intercepts a marching army mid-path, the marching army must fight immediately (even if not at its destination).

### Game End

The game ends when:
- One player has no settlements (immediate loss), OR
- 20 turns have passed

Most settlements wins. Tiebreaker: highest total army Strength.

---

## 2.3 Mechanics Deep Dive

### The March Mechanic: Commitment and Vulnerability

The multi-turn march creates unique strategic dynamics:

**Commitment:**
```
Turn 1: You order a 3-turn march toward enemy settlement
        Path is visible to opponent
        Your army is now "committed" for 3 turns

Turn 2: Army advances (no new orders possible)
        Opponent can see it coming

Turn 3: Army advances again
        Opponent has prepared defenses

Turn 4: Army arrives (if not intercepted)
        Combat or capture occurs
```

**Vulnerability Windows:**
- A marching army cannot reinforce your settlements
- Opponent can attack your undefended positions
- Opponent can intercept your marching army with their own force

### The Muster-Garrison-March Triangle

```
     MUSTER (split forces)
           │
           │ Creates new armies
           │ but weakens existing
           ▼
    ┌──────────────┐
    │              │
    │   GARRISON   │◄── Defensive, gains strength
    │   (defend)   │     but yields initiative
    │              │
    └──────┬───────┘
           │
           │ Launch offensive
           │ but reveal plans
           ▼
     MARCH (attack)
```

### Timing and Distance

Movement speed creates strategic geography:

| Distance (connections) | Turns to Reach | Opponent Response Time |
|------------------------|----------------|------------------------|
| 1 | 1 turn | Immediate |
| 2 | 2 turns | 1 turn to react |
| 3 | 3 turns | 2 turns to react |

**Strategic Implications:**
- Short marches are harder to intercept but have less reach
- Long marches telegraph your intentions
- The center of the board has shorter paths to everything

### Build vs. March Tension

Expanding via BUILD creates undefended settlements:
- Opponent can march an army to capture it
- You must march your own army to defend it
- This creates a race condition

```
You BUILD at corner X (1 turn)
Opponent starts MARCH toward X (3 turns away)
You start MARCH toward X (2 turns away)

Who arrives first?
```

---

## 2.4 Gameplay Analysis

### Opening Phase (Turns 1-5)

**Objective:** Establish 2-3 settlements with army coverage

**Typical Opening:**
1. Turn 1: BUILD toward center, GARRISON your army
2. Turn 2: MARCH army toward new settlement (1-2 turns)
3. Turn 3: Army arrives, MUSTER to split forces
4. Turn 4: One army GARRISONs, one MARCHes to next settlement
5. Turn 5: Continue expansion pattern

**Opening Principles:**
- Don't build faster than you can defend
- Maintain army near your settlements
- Control center for shorter march times

### Mid-Game Phase (Turns 6-14)

**Objective:** Control key routes, threaten enemy settlements

**Key Patterns:**
- **Feint:** Start a march, then MUSTER reinforcements at home
- **Fork:** March toward a point that threatens two targets
- **Interception:** Move to block an enemy march path

**Reading the Board:**
```
Enemy army is 3 turns from your settlement.
Your nearest army is 2 turns away.

Option A: March to intercept (meet mid-path)
Option B: March to defend (arrive before them)
Option C: Counter-attack their undefended settlement
```

### End-Game Phase (Turns 15-20)

**Objective:** Secure settlement lead or execute decisive attack

**End-Game Tempo:**
- Calculate march distances to all enemy settlements
- Determine which can be captured before game ends
- Execute on the fastest path to victory

---

## 2.5 Game Experience

### Emotional Arc

**Opening:** Exploration, anticipation
- "I'm building my empire, watching my neighbor..."

**Mid-Game:** Tension, calculation, cat-and-mouse
- "They're marching toward me. Do I intercept or counter-attack?"

**End-Game:** Racing, commitment, resolution
- "Three turns left. I must capture their settlement NOW."

### The Weight of Commitment

March orders cannot be canceled. When you send an army on a 3-turn march:
- You're saying "I bet this is the right move for the next 3 turns"
- Opponent can exploit this by attacking elsewhere
- Creates genuine strategic commitment rarely seen in simple games

### What Makes It Fun

- **Visible threats:** Watching enemy armies approach creates dread
- **Interception drama:** Will you cut them off in time?
- **Strategic timing:** Long-term planning that pays off (or doesn't)
- **Bluffing potential:** Start a march, then use remaining armies differently

---

## 2.6 Strategic Depth

### Advanced Concepts

**1. March Geometry**
- Hexagonal grids have multiple paths between points
- Choose paths that keep you near friendly settlements
- Avoid paths that pass through enemy-controlled corners

**2. The Two-Army Principle**
- Always maintain at least two armies
- One to defend, one to threaten
- Losing your only army is devastating

**3. Settlement Topology**
- Settlements connected in a line are easy to march between
- Scattered settlements require longer marches to reinforce
- Compact settlement clusters are easier to defend

**4. Interception Mathematics**
```
Enemy starts 3-turn march to target A.
You are 2 turns from the midpoint of their path.

If you intercept at midpoint:
- Your army vs. their (marching) army
- Winner proceeds to their objective
- Interception is HIGH RISK, HIGH REWARD
```

**5. The Build-Race Dilemma**
- Building settlements grows your victory potential
- But undefended settlements are captured easily
- Balance between expansion and army strength

---

## 2.7 Why It Works

### Simplicity Analysis

**Total Rules:**
- 4 actions (Muster, Garrison, March, Build)
- 1 combat resolution (compare Strength)
- 1 movement rule (1 connection per turn)
- March commitment (cannot cancel)

**Emergent Complexity:**
- Distance creates reaction windows
- Visible marches enable counter-play
- Multiple armies create coordination challenges
- Settlement defense requires army positioning

### Risk DNA

| Risk Element | March of Empires Equivalent |
|--------------|---------------------------|
| Continental bonuses | Compact settlement clusters |
| Troop movement | Multi-turn marching |
| Fortification | Garrison action (+1 Str) |
| Attack decisions | March path selection |
| Territory defense | Army positioning |

### Captain Moroni's Influence

**"Cutting off supply/reinforcement lines":**
- Intercepting marches mid-path
- Capturing settlements that connect enemy territories

**"Strategic defensive positioning":**
- Garrisoning armies at key chokepoints
- Building settlements that create defensive perimeters

---

# VARIATION 3: STRONGHOLD

*"Whoever is first in the field and awaits the coming of the enemy, will be fresh for the fight."* - Sun Tzu

## 3.1 Game Overview

**STRONGHOLD** focuses on fortification levels as the primary strategic dimension. Settlements can be upgraded through three tiers of fortification, each dramatically stronger than the last. Attackers must commit significant force to breach fortified positions.

**The Hook:** A Level 3 fortress is nearly impregnable, but building one takes time and resources - time your opponent can use to surround you.

**Unique Feature:** Fortification tiers create asymmetric combat where defenders have massive advantages.

---

## 3.2 Complete Rules

### Components
- 19 hexagonal tiles
- 54 corner markers
- Fortification markers (Level 1, 2, 3)
- Troop tokens (1, 3, 5 denominations)
- 2 player colors

### Setup
1. Arrange hexagonal board in standard pattern
2. Each player places ONE Level 1 settlement on their starting edge
3. Each starting settlement has 3 Troops
4. First player determined randomly

### Core Concepts

**Settlements have two attributes:**
- **Fortification Level (1, 2, or 3):** Defensive strength
- **Troops (1-10):** Offensive capability

**Fortification Levels:**

| Level | Name | Defense Bonus | Upgrade Cost |
|-------|------|---------------|--------------|
| 1 | Outpost | +0 | (starting) |
| 2 | Fort | +2 | 3 Troops |
| 3 | Stronghold | +5 | 5 Troops (from L2) |

**Defense Bonus:** Added to Troops when defending against attacks.

### Turn Structure

On your turn, for EACH settlement you control, choose ONE action:

#### Action A: MUSTER (Train Troops)
- Settlement gains +2 Troops (max 10)
- Troops represent your fighting force

#### Action B: FORTIFY (Upgrade Settlement)
- Spend Troops to increase Fortification Level
- Level 1 -> 2: Costs 3 Troops
- Level 2 -> 3: Costs 5 Troops
- Cannot exceed Level 3

#### Action C: EXPAND (Establish Outpost)
- Choose an empty connected corner
- Spend 2 Troops from this settlement
- Place a new Level 1 settlement with 1 Troop
- Origin must have at least 3 Troops

#### Action D: ATTACK (Assault Enemy Position)
- Choose an enemy settlement at a connected corner
- Send Troops from your settlement (leave at least 1 behind)
- **Combat Resolution:**
  - Attacker Power = Troops sent
  - Defender Power = Troops + Fortification Bonus
  - Higher Power wins
  - Ties: Defender wins
  - Winner loses Troops equal to opponent's Power
  - If attacker wins: They claim the settlement (Fortification resets to L1)
  - If defender wins: Attacker's Troops are lost

#### Action E: REINFORCE (Move Troops)
- Send any number of Troops to an adjacent FRIENDLY settlement
- No combat, just movement
- Origin must keep at least 1 Troop

### Game End

The game ends when:
- One player has no settlements (immediate loss), OR
- 30 turns have passed

Most settlements wins. Tiebreaker: highest combined Fortification levels.

---

## 3.3 Mechanics Deep Dive

### The Fortification Economy

Fortification creates a fundamental decision between offense and defense:

**Path to Level 3 Stronghold:**
```
Start: Level 1 with 3 Troops

Turn 1: MUSTER (+2 Troops) -> 5 Troops
Turn 2: FORTIFY Level 2 (-3 Troops) -> 2 Troops, Level 2
Turn 3: MUSTER (+2 Troops) -> 4 Troops
Turn 4: MUSTER (+2 Troops) -> 6 Troops
Turn 5: FORTIFY Level 3 (-5 Troops) -> 1 Troop, Level 3

Result: Level 3 Stronghold with Defense Power 6 (1 + 5 bonus)
Cost: 5 turns of dedicated investment
```

**Alternative: Expansion Path:**
```
Start: Level 1 with 3 Troops

Turn 1: MUSTER (+2 Troops) -> 5 Troops
Turn 2: EXPAND (-2 Troops) -> 3 Troops, new settlement with 1 Troop
Turn 3: MUSTER both -> 5 Troops and 3 Troops
Turn 4: EXPAND from main (-2) -> 3 Troops, second new settlement
Turn 5: MUSTER all three

Result: 3 Level 1 Outposts with combined ~9 Troops
Cost: 5 turns, but 3x territory
```

### The Defense Multiplier

Fortification bonuses make attacks costly:

| Attacking | Level 1 (3 Troops) | Level 2 (3 Troops) | Level 3 (3 Troops) |
|-----------|--------------------|--------------------|---------------------|
| 4 Troops | Win (lose 3) | Lose | Lose |
| 5 Troops | Win (lose 3) | Win (lose 5) | Lose |
| 6 Troops | Win (lose 3) | Win (lose 5) | Lose |
| 7 Troops | Win (lose 3) | Win (lose 5) | Lose |
| 8 Troops | Win (lose 3) | Win (lose 5) | Lose |
| 9 Troops | Win (lose 3) | Win (lose 5) | Win (lose 8) |

**Observation:** Level 3 Strongholds are extremely expensive to attack. Even with 9 Troops, you only win with 1 survivor.

### The Reinforce Mechanic

Troop movement via REINFORCE enables:
- **Concentration of force:** Gather Troops for a decisive attack
- **Defensive redeployment:** Move Troops to threatened positions
- **Strategic flexibility:** Adapt to opponent's moves

**The Tradeoff:**
- Reinforcing leaves origin weaker
- One-turn action cost (not immediate)
- Creates visible troop movements opponent can read

---

## 3.4 Gameplay Analysis

### Opening Phase (Turns 1-8)

**Objective:** Establish territory while building defensive foundation

**The Opening Dilemma:**
- Rush to Level 3? (Safe but small empire)
- Expand aggressively? (Large but vulnerable empire)
- Balanced approach? (Moderate risk, moderate reward)

**Sample Balanced Opening:**
```
Turn 1: MUSTER (5 Troops)
Turn 2: FORTIFY L2 (2 Troops, Level 2)
Turn 3: MUSTER (4 Troops)
Turn 4: EXPAND (2 Troops, new Level 1)
Turn 5: MUSTER both
Turn 6: FORTIFY original to L3
Turn 7-8: Continue expansion from secure base
```

### Mid-Game Phase (Turns 9-22)

**Objective:** Control territory through fortified network

**Key Patterns:**
- **Stronghold Anchor:** Build one L3, expand around it
- **Fort Network:** Multiple L2s that can reinforce each other
- **Raiding:** Attack weak outposts with concentrated Troops

**Critical Decision Points:**
- Opponent has L3 Stronghold: Do you commit Troops to breach it?
- You have many L1s: Do you fortify or keep expanding?
- Opponent is spreading thin: Attack or build?

### End-Game Phase (Turns 23-30)

**Objective:** Secure settlement count lead

**End-Game Dynamics:**
- L3 Strongholds are almost unbreakable (need 9+ Troops)
- Territory count matters more than fortification
- Desperate attacks on weak positions

---

## 3.5 Game Experience

### Emotional Arc

**Opening:** Strategic planning, building
- "I'm going to build an impenetrable fortress..."

**Mid-Game:** Adaptation, tension
- "Their Stronghold is too powerful. I need to go around."

**End-Game:** Calculation, drama
- "I need to break through that Fort to win. All-in attack!"

### The Fortress Fantasy

Stronghold delivers the fantasy of:
- Building mighty fortifications
- Watching enemies break against your walls
- Choosing when to sally forth

### What Makes It Fun

- **Building satisfaction:** Upgrading to Level 3 feels powerful
- **Tactical attacks:** Calculating the exact force needed
- **Defensive drama:** Will my Fort hold against their assault?
- **Territory racing:** Expanding faster than opponent can fortify

---

## 3.6 Strategic Depth

### Advanced Concepts

**1. The Fortress Trap**
- Building a Level 3 too early cedes too much territory
- Opponent can surround you and win on settlement count
- Strongholds are good, but 5+ Outposts is often better

**2. Troop Concentration**
- Use REINFORCE to mass Troops at one settlement
- Launch devastating attack, then REINFORCE back to defend
- Requires multi-turn planning

**3. The Fort Line**
- Multiple Level 2 Forts in a line are very strong
- Each covers the others' flanks
- Requires significant investment but creates safe territory

**4. Attack Timing**
- Attack after opponent has Fortified (they spent Troops)
- Attack before opponent finishes fortifying (lower defense)
- Read their Troop counts to find windows

**5. Expansion vs. Fortification Curves**
```
Turns 1-10:  Expansion favored (need territory to win)
Turns 11-20: Fortification of key positions
Turns 21-30: Territory count is locked in; protect what you have
```

### Captain Moroni's Tactics

**"Building fortifications (walls, ditches, towers)":**
- The three-tier fortification system directly models this
- Level 3 Strongholds represent fully fortified cities

**"Taking strongholds through preparation":**
- Massing Troops through multiple MUSTER actions
- Using REINFORCE to concentrate forces
- Timing attack when opponent is weakest

**"The Title of Liberty (morale/rallying)":**
- Could be modeled as: When defending your LAST settlement, +3 bonus
- Creates dramatic last stands

---

## 3.7 Why It Works

### Simplicity Analysis

**Total Rules:**
- 5 actions (Muster, Fortify, Expand, Attack, Reinforce)
- 3 fortification levels with fixed bonuses
- Simple combat (compare powers)

**Emergent Complexity:**
- Troop economy and allocation
- Fortification timing decisions
- Attack calculation (how many Troops needed?)
- Defensive positioning and network effects

### Risk DNA

| Risk Element | Stronghold Equivalent |
|--------------|----------------------|
| Territory control | Settlement control |
| Troop accumulation | MUSTER action |
| Fortification bonus | Level 2 and 3 defenses |
| Mass attacks | REINFORCE to concentrate Troops |
| Card trading for troops | N/A (simplified) |

### The Art of War Influence

**"Invincibility lies in the defense":**
- Level 3 Strongholds embody this
- But "victory in the attack" requires knowing when to strike

**"Know yourself, know your enemy":**
- Troop counts and fortification levels are visible
- Perfect information enables deep strategic calculation

---

# ELEGANT ENHANCEMENTS

Based on the analysis of all three variations, **VARIATION 1: FORTIFIED REALM** best achieves the goal of "Risk feel with elegant simplicity." Here are 5 small enhancements that add depth without adding complexity:

## Enhancement 1: The Rally Action

**Rule Addition:**
- New action: RALLY
- Your settlement gains +0 Strength but becomes INSPIRED until next turn
- INSPIRED settlements have +1 when defending
- Thematic tie to "Title of Liberty"

**Why It Works:**
- Adds defender-advantage option without changing combat math
- Creates interesting bluff potential (are they rallied?)
- Maintains simplicity (just +1 defense bonus)

## Enhancement 2: Connection Chains

**Rule Addition:**
- If you control 3+ settlements in a connected chain (each linked to the next), all gain +1 max Strength (cap becomes 8)
- Creates incentive for territory continuity over scattered settlements

**Why It Works:**
- Rewards strategic expansion
- Punishes isolated outposts
- Creates "cutting" as a valid attack strategy

## Enhancement 3: Last Stand

**Rule Addition:**
- When you have only 1 settlement remaining, it gains +2 Strength when defending
- Creates dramatic comeback potential

**Why It Works:**
- Prevents runaway victories
- Creates epic last stand moments
- Only triggers in desperate situations

## Enhancement 4: Scouts

**Rule Addition:**
- Before choosing actions, you may "scout" one enemy settlement
- Scouting reveals that settlement's current Strength
- You may scout one settlement per turn for free
- Creates fog of war otherwise (don't know exact Strength)

**Why It Works:**
- Adds information asymmetry
- Creates "do I scout or guess?" decisions
- Minimal rule overhead

## Enhancement 5: The Forced March

**Rule Addition:**
- EXPAND can target a corner 2 connections away (not just adjacent)
- Cost increases to 3 Strength (instead of 2)
- New settlement still starts with Strength 1

**Why It Works:**
- Enables surprise flank maneuvers
- Adds risk/reward for aggressive expansion
- Doesn't change core mechanics

---

# COMPARATIVE ANALYSIS

## Comparison Matrix

| Criterion | Fortified Realm | March of Empires | Stronghold |
|-----------|-----------------|------------------|------------|
| **Rule Simplicity** | 10/10 | 7/10 | 8/10 |
| **Strategic Depth** | 8/10 | 9/10 | 8/10 |
| **Risk Feel** | 9/10 | 7/10 | 8/10 |
| **Turn Speed** | 10/10 | 7/10 | 8/10 |
| **Teach Time** | 3 min | 8 min | 5 min |
| **Analysis Paralysis** | Low | Medium | Medium |
| **Luck Factor** | None | None | None |
| **Comeback Potential** | Medium | High | Medium |

## Detailed Assessment

### Fortified Realm

**Strengths:**
- Simplest ruleset (3 actions)
- Fastest turns (minimal calculation)
- Cleanest strategic loop (Fortify-Expand-Attack triangle)
- Most accessible to new players

**Weaknesses:**
- Least thematic depth (no multi-turn planning)
- Can feel "samey" after many plays
- Limited tactical variety

**Best For:** Quick games, casual players, introducing new players to strategy games

### March of Empires

**Strengths:**
- Most strategic depth (multi-turn planning)
- Strongest thematic resonance (marching armies)
- Best interception mechanics
- High replayability

**Weaknesses:**
- Most complex rules (march tokens, armies vs. settlements)
- Longest turns (pathfinding decisions)
- Steepest learning curve

**Best For:** Experienced strategy gamers, players who enjoy tactical depth

### Stronghold

**Strengths:**
- Best fortification fantasy
- Clear upgrade path (visible progress)
- Strong defensive play options
- Good balance of simplicity and depth

**Weaknesses:**
- Fortification math can slow turns
- Level 3 Strongholds can create stalemates
- More actions to remember (5 vs. 3)

**Best For:** Players who enjoy building and defending

## Final Recommendation

**For the stated goal of "Risk feel with elegant simplicity," FORTIFIED REALM is the winner.**

It captures Risk's essence:
- Territory control through settlements
- Troop-like Strength accumulation
- Calculated attack decisions
- Expansion vs. consolidation tension

While maintaining elegant simplicity:
- 3 actions, all meaningful
- Single combat comparison
- No tracking between turns (beyond Strength values)
- Teachable in 3 minutes

**However**, if the target audience is experienced gamers willing to invest in learning a deeper system, **MARCH OF EMPIRES** offers the richest strategic experience through its multi-turn commitment mechanic.

---

# APPENDIX A: BOARD SETUP DIAGRAMS

## Standard 19-Hex Board

```
                  N
            ___________
           /   \   /   \
          / 1,0 \ / 2,0 \
         /_______\_______\
        /   \   /   \   /   \
       / 0,1 \ / 1,1 \ / 2,1 \
      /_______\_______\_______\
     /   \   /   \   /   \   /   \
    / 0,2 \ / 1,2 \ / 2,2 \ / 3,2 \
   /_______\_______\_______\_______\
    \   /   \   /   \   /   \   /
     \ / 0,3 \ / 1,3 \ / 2,3 \ /
      \_______\_______\_______/
       \   /   \   /   \   /
        \ / 1,4 \ / 2,4 \ /
         \_______\_______/
                  S
```

## Corner (Vertex) Positions

Each hexagon has 6 corners. Corners are shared between adjacent hexagons:
- Center hexagon (1,2) shares corners with all 6 surrounding hexagons
- Edge hexagons share corners with 2-3 neighbors
- Vertex hexagons share corners with only 1 other hexagon

## Starting Positions

**Player 1 (South):** Any corner on the bottom edge of hexagons (1,4) or (2,4)
**Player 2 (North):** Any corner on the top edge of hexagons (1,0) or (2,0)

---

# APPENDIX B: QUICK REFERENCE CARDS

## Fortified Realm - Player Aid

```
┌─────────────────────────────────────┐
│      FORTIFIED REALM - ACTIONS      │
├─────────────────────────────────────┤
│                                     │
│  FORTIFY: Do nothing, gain +1 Str   │
│           (max 7)                   │
│                                     │
│  EXPAND:  Spend 2 Str, create       │
│           new Str 1 at connected    │
│           empty corner              │
│           (need 3+ Str)             │
│                                     │
│  ATTACK:  Compare your Str vs       │
│           enemy Str at connected    │
│           corner                    │
│           Higher wins, loses loser's│
│           Str from winner           │
│           Ties: Defender wins       │
│                                     │
├─────────────────────────────────────┤
│  WIN: Most settlements after 25     │
│       turns (tiebreaker: total Str) │
└─────────────────────────────────────┘
```

## March of Empires - Player Aid

```
┌─────────────────────────────────────┐
│     MARCH OF EMPIRES - ACTIONS      │
├─────────────────────────────────────┤
│ ARMIES:                             │
│  MUSTER:  Split army (on your       │
│           settlement)               │
│  GARRISON: Stay, gain +1 Str (max 6)│
│  MARCH:   Move 1-3 corners over     │
│           1-3 turns (committed!)    │
│                                     │
│ SETTLEMENTS:                        │
│  BUILD:   Create new settlement     │
│           at connected empty corner │
│           (undefended without army) │
│                                     │
├─────────────────────────────────────┤
│ COMBAT: Higher Str wins             │
│         Winner loses loser's Str    │
│         Ties: Both destroyed        │
│                                     │
│ WIN: Most settlements after 20      │
│      turns                          │
└─────────────────────────────────────┘
```

## Stronghold - Player Aid

```
┌─────────────────────────────────────┐
│        STRONGHOLD - ACTIONS         │
├─────────────────────────────────────┤
│                                     │
│ MUSTER:    +2 Troops (max 10)       │
│                                     │
│ FORTIFY:   Level 1→2: -3 Troops     │
│            Level 2→3: -5 Troops     │
│                                     │
│ EXPAND:    -2 Troops, new L1 w/ 1   │
│            at connected corner      │
│                                     │
│ ATTACK:    Send Troops to connected │
│            enemy (keep 1 minimum)   │
│            Attacker Power = Troops  │
│            Defender = Troops + Bonus│
│            (L1: +0, L2: +2, L3: +5) │
│                                     │
│ REINFORCE: Move Troops to adjacent  │
│            friendly settlement      │
│                                     │
├─────────────────────────────────────┤
│ WIN: Most settlements after 30      │
│      turns (tiebreaker: fort levels)│
└─────────────────────────────────────┘
```

---

# APPENDIX C: DESIGN NOTES

## Why No Terrain Types?

Uniform terrain was a deliberate constraint to:
1. Focus strategic depth on positioning rather than terrain bonuses
2. Reduce rules complexity
3. Ensure every corner is equally viable
4. Avoid "best start position" problems

## Why Corners Instead of Tiles?

The corner (vertex) placement was chosen because:
1. It mirrors familiar Catan mechanics
2. It creates natural bottlenecks (3 connections vs. 6 for tile centers)
3. It enables more nuanced expansion paths
4. It makes defensive lines feel more meaningful

## Why No Dice Combat?

All three variations use deterministic combat (higher number wins) because:
1. It reduces luck, increasing strategic weight
2. It enables precise calculation
3. It speeds up combat resolution
4. Risk's frustration often comes from "bad dice" - we remove this

## Why Multi-Turn Movement in March of Empires?

The commitment mechanic creates:
1. Meaningful long-term planning
2. Visible threats that can be responded to
3. Windows of vulnerability
4. A sense of "distance" on the hex map

## Why Three Fortification Levels in Stronghold?

Three levels were chosen because:
1. Two levels don't create enough decision space
2. Four or more levels add complexity without equivalent depth
3. Three creates clear progression (Outpost → Fort → Stronghold)
4. Each upgrade represents a significant investment

---

*"Thus it is that in war the victorious strategist only seeks battle after the victory has been won, whereas he who is destined to defeat first fights and afterwards looks for victory."* - Sun Tzu

---

**Document Version:** 1.0
**Created:** Strategic Dominion Design Series
**License:** Open Game Design - Free to use and modify
