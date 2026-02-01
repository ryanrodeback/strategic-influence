# TRIANGULAR ASSAULT
## Complete Game Design Document

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Complete Rules](#2-complete-rules)
3. [Mechanics Deep Dive](#3-mechanics-deep-dive)
4. [Gameplay Analysis](#4-gameplay-analysis)
5. [Game Experience](#5-game-experience)
6. [Strategic Depth](#6-strategic-depth)
7. [Elegant Enhancements](#7-elegant-enhancements)
8. [Appendices](#8-appendices)

---

## 1. Game Overview

### 1.1 The Core Concept

**Triangular Assault** is a two-player abstract strategy game built on a single, elegant decision: each turn, you must choose between two mutually exclusive actions.

```
PLACE: Claim new territory (guaranteed)
   OR
ATTACK: Contest enemy territory (probabilistic)
```

This "one action, two choices" structure creates the heart of the game. Every turn presents a meaningful decision where both options have clear value but compete for your limited action economy.

### 1.2 The Triangular Innovation

What sets Triangular Assault apart from similar territory games is its use of a **triangular tessellation grid** within a hexagonal boundary. Each territory is a triangle with exactly **three edge-sharing neighbors** - never more, never less.

This geometric constraint has profound implications:

- **Maximum attack strength is capped at 87.5%** - certainty is never achievable
- **Defense is structurally easier** - fewer attack vectors to protect
- **Front lines are inherently jagged** - straight defensive walls are geometrically impossible
- **The number 3 governs everything** - maximum attackers, maximum defenders, corners of each cell

### 1.3 Design Philosophy

Triangular Assault embraces the principle that **constraints create strategy**. By limiting options (single stone, single action, three neighbors), we create meaningful choices where every decision matters.

The game achieves depth through:

- **Simple rules** that fit on an index card
- **Emergent complexity** from geometric constraints
- **Persistent tension** from probabilistic outcomes
- **Natural formations** that arise from optimal play

### 1.4 What Makes It Elegant

| Element | Implementation | Why It Works |
|---------|---------------|--------------|
| Decision structure | ONE action per turn | No paralysis, every move matters |
| Territory claim | ONE stone per cell | Clean state, clear ownership |
| Attack mechanic | 50% per adjacent ally | Intuitive probability, scales naturally |
| Board geometry | Triangular grid | Novel, constrained, creates unique strategy |
| Victory | Domination or majority | Simple to understand, hard to achieve |

---

## 2. Complete Rules

### 2.1 Components

- **Board**: 37-cell hexagonal boundary (3 rings from center) with triangular grid
- **Stones**: Two colors (Black and White), approximately 20 each
- **Optional**: Dice or random number generator for attack resolution

### 2.2 Board Geometry

```
             /\  /\  /\
            /  \/  \/  \
           /\  /\  /\  /\
          /  \/  \/  \/  \
         /\  /\  /\  /\  /\
        /  \/  \/  \/  \/  \
         \/  \/  \/  \/  \/
          \  /\  /\  /\  /
           \/  \/  \/  \/
            \  /\  /\  /
             \/  \/  \/
```

**Board Composition:**
- 12 edge cells (exposed, highly contested)
- 18 mid-ring cells (strategically valuable)
- 6 inner cells + 1 center (core territory)
- Total: 37 triangular territories

**Key Property**: Every triangle shares edges with exactly 3 other triangles. There are no corners with fewer neighbors and no interior cells with more.

### 2.3 Setup

1. Place the empty board between both players
2. Determine first player (Black moves first)
3. For competitive play: implement the **Pie Rule** (after Black's first move, White may choose to swap colors)

### 2.4 Turn Structure

Each turn, the active player performs **exactly ONE action**:

#### Option A: PLACE

- Select any **empty** triangle on the board
- Place one of your stones on that triangle
- That territory is now claimed by you
- **This action always succeeds**

#### Option B: ATTACK

- **Prerequisite**: You must have at least 1 stone adjacent (edge-sharing) to the target
- Select any **enemy-occupied** triangle
- **Resolution**: Roll independently for each of YOUR adjacent stones (50% success each)
  - If **ANY** roll succeeds: Target flips to your control (replace enemy stone with yours)
  - If **ALL** rolls fail: Target remains enemy-controlled (no penalty to attacker)

### 2.5 Attack Resolution Details

**Probability Table:**

| Adjacent Allies | Success Rate | Failure Rate | Expected Value |
|-----------------|--------------|--------------|----------------|
| 1 | 50.0% | 50.0% | 0.50 territories |
| 2 | 75.0% | 25.0% | 0.75 territories |
| 3 (MAXIMUM) | 87.5% | 12.5% | 0.875 territories |

**Resolution Methods:**

- **Physical**: Flip a coin for each adjacent attacker; any heads = success
- **Digital**: Generate random boolean for each adjacent attacker
- **Dice**: For each adjacent attacker, roll 1d6; 4+ = that attacker succeeds

**Critical Rule**: All dice/rolls are independent. With 3 adjacent attackers, you roll 3 times. Success on ANY roll means the attack succeeds.

### 2.6 Adjacency Rules

- **Only edge-sharing counts** - triangles touching at a single point are NOT adjacent
- Each triangle has exactly 3 adjacent triangles
- Your OWN stones adjacent to a target count for attack strength
- Enemy stones adjacent to your target do NOT defend (they simply occupy space)

```
Adjacent (edge-sharing):        NOT Adjacent (point-only):

    /\                              /\
   /  \                            /  \
  / A  \                          / A  \
 /______\                        /______\
 \      /                       /\      /\
  \ B  /                       /  \    /  \
   \  /                       / C  \  / D  \
    \/                       /______\/______\

A and B: ADJACENT              A and C: NOT adjacent
                               A and D: NOT adjacent
```

### 2.7 Victory Conditions

**Primary Victory (Domination)**:
- Reduce your opponent to **0 territories**
- This triggers **immediate victory**

**Secondary Victory (Territory Majority)**:
- After a set number of turns (recommended: 30-40 total turns)
- Player controlling the **most territories wins**
- **Tie-breaker 1**: Player controlling more inner-ring territories (the 7 central cells)
- **Tie-breaker 2**: Second player (White) wins (compensates for first-mover advantage)

### 2.8 Rule Clarifications

| Situation | Ruling |
|-----------|--------|
| Attack with 0 adjacent stones? | **Illegal** - must have at least 1 adjacent |
| Attack your own stone? | **Illegal** - can only attack enemy territories |
| Place on occupied territory? | **Illegal** - place only on empty cells |
| Pass turn? | **Not allowed** - must take one action |
| Attack fails, then what? | Nothing changes; opponent's stone stays; your turn ends |
| Attack succeeds, what happens? | Enemy stone removed, YOUR stone placed there |
| Can I attack the same target twice in one turn? | **No** - one action per turn |

---

## 3. Mechanics Deep Dive

### 3.1 Place vs Attack Decision Tension

The fundamental tension in Triangular Assault emerges from the mutually exclusive nature of PLACE and ATTACK.

**PLACE Analysis:**

```
Advantages:
+ Guaranteed success (100% probability)
+ Expands your territory count
+ Creates new attack vectors for future turns
+ Denies that cell to opponent forever

Disadvantages:
- Doesn't reduce opponent's territory
- May place in suboptimal location
- Slower path to domination victory
- New stone may be isolated and vulnerable
```

**ATTACK Analysis:**

```
Advantages:
+ Success both claims new territory AND removes enemy's
+ Swings territory differential by 2 (not 1)
+ Can eliminate strategically vital enemy positions
+ Disrupts opponent's formations and plans

Disadvantages:
- Probabilistic outcome (maximum 87.5% success)
- Failed attack wastes your turn completely
- Requires positional setup (adjacency prerequisite)
- May leave you overextended if you fail
```

**The Decision Framework:**

```
Consider PLACE when:
- Early game (empty board, no adjacencies)
- No enemy stones adjacent to your position
- Building toward future attack positions
- Opponent has strong defensive clusters
- You need guaranteed progress

Consider ATTACK when:
- You have 2-3 adjacent stones (75-87.5% success)
- Target is strategically vital (center, connection point)
- You're behind on territory (need the 2-point swing)
- Opponent is overextended with weak positions
- The expected value exceeds your best placement
```

**The Mathematics of When to Attack:**

An attack with success probability P is worth attacking when:

```
P * 2 > 1
P > 0.5
```

This means ANY attack with greater than 50% success has higher expected value than placement. However, this ignores:
- Positional value of the placement alternative
- Strategic value of the attack target
- Risk tolerance based on game state

### 3.2 The 3-Neighbor Maximum

The triangular grid's most profound impact is the **hard cap on maximum adjacency**.

**Comparison with Square Grid:**

| Adjacent Allies | Triangular Grid | Square Grid |
|-----------------|-----------------|-------------|
| 1 | 50.0% | 50.0% |
| 2 | 75.0% | 75.0% |
| 3 | 87.5% (MAX) | 87.5% |
| 4 | N/A | 93.75% (MAX) |

**Implications of the 3-Neighbor Cap:**

1. **Certainty is Unachievable**
   - On square grids, 4 adjacent attackers feels "near-certain" (93.75%)
   - On triangular grids, the best possible attack still fails 1-in-8 times
   - This creates permanent tension in every attack decision

2. **Defensive Geometry Changes**
   - Fewer directions to protect (3 vs 4)
   - Easier to "cover" all approaches with fewer pieces
   - Natural chokepoints emerge from the geometry

3. **Attack Coordination Limits**
   - Cannot achieve overwhelming force through numbers alone
   - Quality of position matters more than quantity of stones
   - Encourages wave-based aggression over single decisive strikes

4. **The Magic of Three**
   - Maximum attack force: 3 stones
   - Minimum stable formation (Triangle Defense): 3 stones
   - This creates elegant economy where offense and defense are governed by the same number

### 3.3 Probability Mathematics

**Independent Trial Mechanics:**

Each adjacent attacker makes an independent 50% success check. The attack succeeds if AT LEAST ONE check passes.

```
P(success with n attackers) = 1 - P(all fail)
                            = 1 - (0.5)^n

n=1: 1 - 0.5 = 0.500 (50.0%)
n=2: 1 - 0.25 = 0.750 (75.0%)
n=3: 1 - 0.125 = 0.875 (87.5%)
```

**Expected Value Calculations:**

| Attackers | P(success) | E[territory gain] | E[differential swing] |
|-----------|------------|-------------------|----------------------|
| 1 | 50% | 0.5 | 1.0 |
| 2 | 75% | 0.75 | 1.5 |
| 3 | 87.5% | 0.875 | 1.75 |

**Comparison**: A guaranteed PLACE gives expected territory gain of 1.0 and differential swing of 1.0.

**Over Many Attacks:**

In a 30-turn game where a player makes 10 attacks at maximum strength (87.5%):

```
Expected successes: 10 * 0.875 = 8.75
Expected failures: 10 * 0.125 = 1.25
Standard deviation: sqrt(10 * 0.875 * 0.125) = 1.04

Probability of zero failures: (0.875)^10 = 26.3%
Probability of 2+ failures: 1 - (0.875)^10 - 10*(0.875)^9*(0.125) = 45.6%
```

This means in nearly half of all games, a player will experience 2 or more "surprise" failures even when attacking with maximum force.

### 3.4 Why Uncertainty Persists

**The Psychology of 12.5% Failure:**

The 12.5% failure rate on maximum attacks creates several psychological effects:

1. **The Availability Heuristic**
   - Players vividly remember failed attacks
   - These "bad beats" feel more significant than they mathematically are
   - Creates hesitancy even when attacking is correct

2. **The Gambler's Fallacy**
   - After several successes, players expect a failure is "due"
   - After a failure, players feel the next attack "should" succeed
   - Neither is mathematically true, but both affect decisions

3. **Loss Aversion**
   - A failed attack feels like losing a turn (negative)
   - A successful attack feels like "breaking even" (neutral)
   - This asymmetry makes players attack less than optimal

4. **The Certainty Effect**
   - Players disproportionately value guaranteed outcomes
   - 100% PLACE vs 87.5% ATTACK feels like larger gap than 8.5%
   - Leads to conservative play patterns

**Design Insight:**

This persistent uncertainty is a feature, not a bug. It:
- Prevents "solved" optimal play lines
- Creates dramatic moments when attacks fail
- Rewards risk management over pure calculation
- Ensures comebacks are always possible

---

## 4. Gameplay Analysis

### 4.1 Land Grab Opening Phase (Turns 1-10)

**Characteristics:**
- Empty board means no valid attack targets
- Pure PLACE decisions
- No direct conflict yet
- Establishing presence across the board

**Typical Opening Patterns:**

```
Opening Strategy 1: CENTER CONTROL
- Place first stone in or adjacent to center
- Maximizes future adjacency options
- Creates natural expansion base
- Becomes obvious target for opponent

Opening Strategy 2: EDGE ANCHOR
- Place first stone on outer ring
- Less contested, safer
- Limited expansion directions
- May cede center control

Opening Strategy 3: SPREAD FORMATION
- Place stones in non-adjacent cells
- Claims more "sphere of influence"
- Vulnerable to concentrated opponent
- Difficult to defend later
```

**Opening Phase Principles:**
1. Every placement is permanent - choose wisely
2. Consider future attack angles, not just territory count
3. Balance expansion with creating defensible positions
4. Watch opponent's formation to identify weak points

### 4.2 Consolidation Strategies (Turns 11-18)

**The Transition:**
- Territories begin to border each other
- First attack opportunities emerge
- Players must choose: extend or consolidate

**Consolidation Pattern: The Triangle Defense**

```
       1
      / \
     1   1
```

Three stones forming a triangle mutually support each other. Any attack on one stone can be counter-threatened, and the formation is the minimum stable structure.

**Consolidation Pattern: The Connected Line**

```
    /\  /\  /\
   / 1\/ 1\/ 1\
   \  /\  /\  /
    \/  \/  \/
```

A zig-zag of stones along the natural grid creates a continuous presence but with vulnerable protrusions.

**The Consolidation Dilemma:**

```
Heavy Consolidation:
+ Stones protect each other
+ Difficult for opponent to crack
+ Resilient defensive posture
- Claims less total territory
- Cedes initiative to opponent
- Can be surrounded and starved

Light Consolidation:
+ Claims maximum territory
+ Threatens multiple fronts
+ Forces opponent to react
- Creates thin, vulnerable lines
- Each stone has fewer friendly neighbors
- Susceptible to divide-and-conquer
```

### 4.3 Active Combat Dynamics (Turns 19-30)

**Front Line Formation:**

On triangular grids, front lines have unique properties:

```
Square Grid Front Line (straight):
1 1 1 1 1
. . . . .
2 2 2 2 2

Triangular Grid Front Line (inherently jagged):
    1   1   1
   / \ / \ / \
  /   1   1   \
 / \ / \ / \ / \
    2   2   2
```

The zig-zag nature of triangular grid lines means:
- Every "line" has natural protrusions
- These protrusions can be isolated and attacked
- Perfect defensive walls are geometrically impossible
- Flanking attacks are structurally natural

**Combat Rhythm:**

Active combat tends to follow a pattern:
1. **Probe**: 1-attacker strikes (50%) to test defenses
2. **Build**: PLACE to create adjacency for stronger attacks
3. **Strike**: 2-3 attacker assault on key targets (75-87.5%)
4. **Respond**: Defender counter-attacks or shores up position
5. **Repeat**: Cycle continues with shifting front lines

**The Attack Tempo:**

```
Conservative Play:
- Wait for 3-adjacent setups
- Maximize success probability
- Slower but more reliable
- Opponent has time to prepare

Aggressive Play:
- Attack with 1-2 adjacency
- Accept more failures
- Keeps opponent off-balance
- Higher variance outcomes

Adaptive Play (Recommended):
- Attack when opportunity cost is low
- Strike at strategic targets even with lower odds
- Adjust aggression based on game state
```

### 4.4 Territory Control Patterns

**Regional Dominance:**

The 37-cell board naturally divides into regions:

```
             /\  /\  /\
            / OUTER   \        Outer Ring: 12 cells
           /\  /\  /\  /\      (most contested)
          / MIDDLE     \       Middle Ring: 18 cells
         /\  /\  /\  /\  /\    (strategically valuable)
        / CORE   C      \      Core: 6+1 cells
         \/  \/  \/  \/  \/    (tie-breaker, defensible)
```

**Control Strategies:**

| Strategy | Territory Focus | Playstyle |
|----------|-----------------|-----------|
| Core Fortress | Inner 7 cells | Defensive, turtle |
| Rim Runner | Outer 12 cells | Aggressive, spread |
| Wedge | Slice through center | Dividing, tactical |
| Engulf | Surround opponent | Patient, positional |

**The Division Play:**

One powerful strategy is to cut opponent's forces in two:

```
Before Cut:           After Cutting Attack:

    2   2   2            2   2   2
   / \ / \ / \          / \ / \ / \
  2   2   2   2        2   1   2   2
 / \ / \ / \ / \      / \ / \ / \ / \
    2   2   2            2   2   2

Opponent's left and right groups can no longer support each other.
Each group is now individually weaker.
```

---

## 5. Game Experience

### 5.1 The Psychology of Attack Uncertainty

**The Moment of Decision:**

Every attack in Triangular Assault creates a micro-drama:

```
Setup: You have 3 stones surrounding an enemy
Probability: 87.5% success (excellent odds)
Stakes: Control of a key position

Your internal monologue:
"I have great odds. I should attack."
"But last game I failed with 87.5% twice..."
"Maybe I should place another stone nearby first?"
"But that gives opponent time to reinforce!"
"Just attack. The math says attack."
*rolls dice*
*holds breath*
```

This tension exists because:
- The outcome meaningfully affects the game
- You have no control once committed
- Past experiences (positive and negative) weight the decision
- The 12.5% failure is large enough to feel real

### 5.2 "I've Been Burned Before" Moments

**The Memory of Failure:**

Players develop attack aversion through experience. Consider a player who has experienced:
- Game 1: 87.5% attack fails, loses game by 2 territories
- Game 2: 75% attack fails twice in critical moments
- Game 3: Finally hits an 87.5% attack, but only after hesitating

By Game 4, this player has an emotional "database" of failures. Even though the math hasn't changed, their perception has.

**Manifestations of Attack Aversion:**

1. **Over-preparation**: Building 3 adjacency when 2 would suffice
2. **Target avoidance**: Attacking "unimportant" cells instead of key positions
3. **Placement bias**: Choosing guaranteed PLACE over positive-EV attacks
4. **Timing delays**: Waiting "one more turn" indefinitely

**The Experienced Player's Response:**

Skilled players recognize attack aversion and compensate:
- Remind themselves that past outcomes don't affect future probability
- Evaluate attacks on expected value, not emotional memory
- Accept that failures will happen and plan for them
- View failures as acceptable variance, not mistakes

### 5.3 Risk/Reward Emotional Rollercoaster

**The Emotional Arc of a Game:**

```
TURN 1-5: Calm
"Just placing stones, building position..."

TURN 6-10: Anticipation
"Front lines forming, first attacks possible soon..."

TURN 11-15: Tension
"Should I attack now? What if it fails?"

TURN 16-20: Drama
"I attacked and failed!" / "I attacked and succeeded!"
"Opponent just stole my key position!"

TURN 21-25: Desperation or Dominance
"I'm behind, need to take risks!"
"I'm ahead, need to hold on!"

TURN 26-30: Resolution
"Every attack matters now..."
"Final territory count incoming..."
```

**The Emotional Spectrum:**

| Event | Emotional Response | Player State |
|-------|-------------------|--------------|
| Successful 50% attack | Elation, "I'm lucky!" | Confident |
| Failed 87.5% attack | Frustration, "Of course..." | Tilted |
| Opponent's 50% succeeds | Indignation, "Unfair!" | Defensive |
| 3 successes in a row | Invincibility, "Can't lose!" | Overconfident |
| 2 failures in a row | Dejection, "Nothing works" | Risk-averse |

### 5.4 What Makes Attacks Feel Meaningful

**The Components of Meaningful Attacks:**

1. **Stakes**: The target matters to the game outcome
2. **Agency**: You chose to attack (not forced)
3. **Uncertainty**: Outcome is genuinely in doubt
4. **Consequence**: Success or failure changes the game
5. **Narrative**: The attack fits into the game's "story"

**Why Triangular Assault Achieves This:**

- The 37-cell board makes every cell matter
- PLACE alternative means attacking is a choice
- 12.5% failure rate on maximum attacks maintains tension
- Successful attacks swing momentum; failures create opportunities
- Formations have names (Spearhead, Phalanx) that create narrative

**The "Perfect Attack" Experience:**

The most satisfying attacks occur when:
- You've carefully built adjacency over several turns
- The target is strategically critical
- You understand the risk you're taking
- The dice roll in your favor
- The game shifts noticeably in your direction

This combination of preparation, risk acceptance, and favorable outcome creates a powerful sense of earned success.

---

## 6. Strategic Depth

### 6.1 Defensive Formations and Their Weaknesses

**Formation 1: The Triangle Defense**

```
       1
      / \
     1   1
```

Strengths:
- Minimum stones for mutual protection
- Each stone threatens counter-attack on attackers
- Efficient use of pieces

Weaknesses:
- Small territorial footprint
- Can be surrounded
- Single successful attack breaks the formation

**Formation 2: The Spearhead**

```
       1
      / \
     /   \
    1-----1
   / \   / \
  /   \ /   \
 1     1     1
```

Strengths:
- V-shape points into enemy territory
- Tip is supported by 2 stones behind
- If tip falls, next layer becomes new front
- Creates natural expansion vector

Weaknesses:
- Flanks are exposed
- Loss of tip costs initiative
- Requires continuous forward pressure

**Formation 3: The Phalanx**

```
    /\  /\  /\  /\
   / 1\/ 1\/ 1\/ 1\
   \  /\  /\  /\  /
    \/  \/  \/  \/
```

Strengths:
- Wide front creates multiple threats
- Interior stones have 2 friendly neighbors
- Difficult to penetrate without creating opening

Weaknesses:
- Edge stones are vulnerable (only 1 friendly neighbor)
- Inherent zig-zag creates attack opportunities
- Resource-intensive to build

**Formation 4: The Fortress**

```
      /\
     / 1\
    /\  /\
   / 1\/ 1\
   \  /\  /
    \/ 1\/
     \  /
      \/
```

Strengths:
- Central stone protected by all others
- Extremely difficult to crack
- Can serve as anchor for expansion

Weaknesses:
- Uses many stones for small territory
- Passive, cedes initiative
- Opponent can surround and starve

### 6.2 Offensive Positioning

**Tactic 1: The Fork**

Position a stone to threaten two enemy territories simultaneously.

```
Before:           After placing at X:

    2   .            2   .
   / \ / \          / \ / \
  .   .   2   ->   .   1   2
   \ / \ /          \ / \ /
    .   .            .   .

Stone at X threatens both 2s with 50% attacks.
Opponent can only reinforce one.
```

**Tactic 2: The Surround**

Methodically build adjacency to a key enemy stone before attacking.

```
Turn 1:    Turn 2:    Turn 3:    Turn 4:
           1                     1
  2   ->  / 2  ->   1-2   ->   /1 1
         /            \         \/

Now attack with 87.5% success.
```

**Tactic 3: The Cut**

Attack the stone that connects two enemy groups.

```
Before Cut:              After Successful Cut:

    2   2   2               2   2   2
   / \ / \ / \             / \ / \ / \
  2  [2]  2   2   ->      2   1   2   2
   \ / \ / \ / \           \ / \ / \ / \
    2   2   2               2   2   2

The bracketed [2] was the connection point.
Now opponent has two separate, weaker groups.
```

**Tactic 4: The Probe**

Low-investment 50% attacks to test defenses and create chaos.

```
Philosophy:
- Attack with 1 adjacent stone
- If successful: unexpected gain!
- If failed: minimal investment lost
- Either way: opponent must react
```

### 6.3 Tempo Management

**Understanding Tempo:**

In Triangular Assault, tempo refers to which player is dictating the action.

```
You have tempo when:
- Opponent must respond to your threats
- You're choosing which battles to fight
- Your attacks are forcing defensive placements
- You're expanding while opponent consolidates

Opponent has tempo when:
- You're reacting to their moves
- You're reinforcing instead of attacking
- Your stones are being picked off
- You're contracting while they expand
```

**Gaining Tempo:**

1. **Successful attacks** - Opponent loses a turn's worth of position
2. **Fork threats** - Force opponent into no-win defensive decisions
3. **Initiative placement** - Put stones that create immediate threats
4. **Unexpected probes** - 50% attacks that succeed steal tempo

**Spending Tempo:**

Sometimes it's correct to give up tempo:

- **Consolidation**: Shore up weaknesses before opponent exploits them
- **Deep defense**: Build impenetrable position, then counter-attack
- **Resource advantage**: If ahead on territory, trade tempo for stones

### 6.4 When to Expand vs When to Attack

**The Decision Matrix:**

| Game State | Recommended Action |
|------------|-------------------|
| Early game, no adjacencies | PLACE (expand) |
| Behind on territory | ATTACK (need 2-point swings) |
| Ahead on territory | PLACE (extend lead safely) |
| Equal territory, good attack setup | ATTACK (try to pull ahead) |
| Opponent overextended | ATTACK (punish weakness) |
| Own position weak | PLACE (consolidate first) |
| Late game, close score | ATTACK (variance helps underdog) |
| Late game, significant lead | PLACE (reduce variance) |

**The Risk Gradient:**

```
RISK-AVERSE <-------------------------> RISK-SEEKING

Guaranteed     Conservative    Adaptive      Aggressive
PLACE only     attacks (2-3    attacks       attacks (1+
               adjacent)       based on      adjacent)
                               context

Best when:     Best when:      Best when:    Best when:
- Ahead        - Equal or      - Unknown     - Behind
- Stable       slightly ahead  - Testing     - Need
  position     - Building      opponent      comeback
               position
```

---

## 7. Elegant Enhancements

The following enhancements preserve the game's core elegance while adding strategic dimensions. Each is optional and can be combined or used independently.

### 7.1 Enhancement: Momentum

**The Enhancement:**
After a successful attack, you may immediately attack again (still requires adjacency to new target). Chain continues until an attack fails or you choose to stop.

**Why It Works:**
- Rewards aggressive play without changing base probability
- Creates dramatic "breakthrough" moments
- Punishes overextended positions more severely
- Single rule addition with significant impact

**What Gameplay It Creates:**
- Attacking becomes higher-risk, higher-reward
- Defensive clustering becomes more important
- "All eggs in one basket" positioning is punished
- Games can swing dramatically on hot streaks
- Creates narrative moments ("The three-stone rampage!")

**Balance Note:**
This increases variance. Consider reducing turn limit if implementing, or requiring adjacency-2 minimum for chain attacks.

### 7.2 Enhancement: Influence Aura

**The Enhancement:**
Each stone exerts "influence" on adjacent empty cells. When you PLACE on a cell where you have influence advantage (more adjacent stones than opponent), gain +1 bonus territory anywhere on the board.

**Why It Works:**
- Rewards positional play without complicating attacks
- Creates new considerations for placement decisions
- Encourages surrounding and cutting strategies
- Simple to track (just count adjacent stones when placing)

**What Gameplay It Creates:**
- "Sphere of influence" becomes literal
- Empty buffer zones between forces become valuable
- Racing to place in contested areas
- Defensive formations project "no man's land"
- Accelerates mid-game resolution

**Balance Note:**
Bonus territory must be placed on empty cell, and opponent can contest it normally next turn.

### 7.3 Enhancement: Stubborn Defense

**The Enhancement:**
The first time each game that an enemy attacks your stone with 3 adjacent attackers, that attack automatically fails. (One-time-use per player)

**Why It Works:**
- Protects against "perfect storm" scenarios
- Gives trailing players comeback hope
- Creates strategic decision of when to "spend" the defense
- Single exception, easy to remember

**What Gameplay It Creates:**
- Attackers must bait out the stubborn defense before key strikes
- Defenders must choose: use it now or save for later?
- Mindgames around whether defense has been used
- Guarantees at least one "dramatic save" moment per game
- Reduces frustration from unlucky key-position losses

**Balance Note:**
Consider tracking with a physical token that gets removed when used.

### 7.4 Enhancement: Sacred Ground

**The Enhancement:**
At game start, each player secretly selects one cell as their "sacred ground." Reveal at game end. If you control your sacred ground, gain +3 territories for final scoring.

**Why It Works:**
- Adds hidden information without mid-game complexity
- Creates asymmetric objectives
- Encourages reading opponent's priorities
- Single pre-game decision with lasting impact

**What Gameplay It Creates:**
- Players must defend apparent "sacred ground" candidates
- Feinting toward false sacred grounds becomes viable
- End-game reveals create dramatic moments
- Encourages center control (safer to protect)
- Adds bluffing layer to an otherwise perfect-information game

**Balance Note:**
Consider requiring sacred ground selection from inner 7 cells to prevent trivial edge placements.

### 7.5 Enhancement: Rising Tide

**The Enhancement:**
After every 10 turns, the outermost ring of remaining cells becomes "flooded" and removed from play. Stones on flooded cells are removed.

**Why It Works:**
- Natural game-length control
- Creates escalating pressure
- Rewards central positioning
- Prevents stalemate through attrition

**What Gameplay It Creates:**
- Early outer-ring investments become temporary
- Central territory becomes increasingly valuable
- Forces engagement (can't turtle in corners)
- Creates natural "chapters" in the game narrative
- Dramatic moments when key outer positions flood

**Implementation:**
- Turns 1-10: Full 37-cell board
- Turns 11-20: Outer ring floods, 25 cells remain
- Turns 21-30: Middle outer ring floods, ~12 cells remain
- Endgame: Final central fight

---

## 8. Appendices

### 8.1 Quick Reference Card

```
TRIANGULAR ASSAULT - Quick Rules

SETUP: Empty 37-cell board. Black moves first.

EACH TURN: Do ONE action:
  PLACE: Put your stone on any empty cell (guaranteed)
  ATTACK: Target enemy cell you're adjacent to
          Roll 50% for each adjacent ally
          ANY success = you capture the cell

ADJACENCY: Edge-sharing only (each cell has 3 neighbors)

ATTACK SUCCESS RATES:
  1 adjacent: 50%
  2 adjacent: 75%
  3 adjacent: 87.5% (MAXIMUM)

VICTORY:
  - Domination: Opponent has 0 stones (instant win)
  - Majority: Most territories after 30 turns
  - Tiebreaker: Most inner-ring cells, then Player 2 wins
```

### 8.2 Probability Reference

| Attackers | Success | Failure | Expected Value | vs PLACE EV |
|-----------|---------|---------|----------------|-------------|
| 1 | 50.0% | 50.0% | 1.00 swing | Equal |
| 2 | 75.0% | 25.0% | 1.50 swing | +50% |
| 3 | 87.5% | 12.5% | 1.75 swing | +75% |

**Over 10 Attacks at 87.5%:**
- Expected successes: 8.75
- P(all succeed): 26.3%
- P(2+ fail): 45.6%

### 8.3 Formation Reference

```
TRIANGLE DEFENSE (Minimum Stable)
       1
      / \
     1   1

SPEARHEAD (Offensive Advance)
       1
      / \
     1   1
    / \ / \
   1   1   1

PHALANX (Defensive Wall)
    /\  /\  /\
   / 1\/ 1\/ 1\
   \  /\  /\  /
    \/  \/  \/

FORTRESS (Defensive Anchor)
      /\
     / 1\
    /\  /\
   / 1\/ 1\
   \  /\  /
    \/ 1\/
```

### 8.4 Glossary

| Term | Definition |
|------|------------|
| **Adjacency** | Edge-sharing relationship between triangles |
| **Attack** | Action to capture enemy territory (probabilistic) |
| **Cut** | Attack that separates enemy groups |
| **Domination** | Victory by eliminating all opponent stones |
| **Fork** | Position threatening multiple enemy cells |
| **Place** | Action to claim empty territory (guaranteed) |
| **Probe** | Low-adjacency attack to test defenses |
| **Sacred Ground** | (Enhancement) Secret objective cell |
| **Spearhead** | V-shaped offensive formation |
| **Stubborn Defense** | (Enhancement) One-time attack immunity |
| **Tempo** | Initiative; which player dictates action |
| **Triangle Defense** | Minimum stable defensive formation |

### 8.5 Design Credits and Version History

**Triangular Assault** is based on the "Place or Attack - Triangular Grid" concept from the Strategic Influence game design exploration project.

**Core Mechanics:**
- Place/Attack decision structure
- 50% independent probability per adjacent attacker
- Triangular tessellation grid (3-neighbor maximum)
- Hexagonal boundary (37 cells)

**Version:** 1.0
**Document Date:** 2026-02-01

---

*This document represents a complete game design specification. Triangular Assault is ready for prototyping and playtesting.*
