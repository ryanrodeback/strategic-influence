# Influence: Hex Edition
## Complete Game Design Document

**Version:** 1.0
**Status:** Design Complete
**Genre:** Abstract Strategy / Probabilistic Territorial Control

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Complete Rules](#2-complete-rules)
3. [Mechanics Deep Dive](#3-mechanics-deep-dive)
4. [Gameplay Analysis](#4-gameplay-analysis)
5. [Game Experience](#5-game-experience)
6. [Strategic Depth](#6-strategic-depth)
7. [Elegant Enhancements](#7-elegant-enhancements)

---

## 1. Game Overview

### 1.1 Core Concept

**Influence: Hex Edition** is a two-player abstract strategy game where players place stones on the vertices of a hexagonal board to compete for control of triangular regions. Unlike traditional territory games where control is binary, this game uses a **probabilistic influence system** where each triangle's ownership is determined by the stones at its three corners.

The game combines three distinct innovations:
- **Hexagonal vertex placement** creating natural triangular territories
- **Cumulative scoring** where influence resolves every turn
- **Probabilistic resolution** based on corner stone configurations

### 1.2 The Elevator Pitch

*"Place stones at hex vertices. Each triangle scores every turn based on who controls its corners. Three corners gives certain points; two gives probable points; one gives possible points. Accumulate the highest score across the game to win."*

### 1.3 What Makes This Game Unique

**Gradient Territory Control**
Unlike Go or Chess where you either control a space or you don't, Influence: Hex Edition allows for partial control. A triangle with two of your stones and one opponent stone gives you 67% influence - not guaranteed control, but favorable odds. This creates rich tension throughout the game as contested regions remain meaningful.

**Temporal Strategy**
The cumulative scoring system means that early investments compound. A triangle you've dominated since turn 3 has contributed points every single turn, while late-game territorial gains have less impact. This creates a unique "score velocity" dynamic where players balance immediate point generation against long-term positional strength.

**Natural Probability**
The three corners of each triangle create an elegant mathematical framework: 33.33% influence per corner. This feels intuitive (roughly "one third each") while creating meaningful strategic decisions about commitment levels.

**Geometric Elegance**
The hexagonal board with vertex placement is isotropic - there's no "horizontal vs diagonal" distinction like in square grids. All directions are equally valid, creating organic-looking patterns and removing artificial asymmetries from the strategic landscape.

### 1.4 Design Goals

| Goal | Implementation |
|------|----------------|
| **Simple to learn** | One action per turn (place a stone); one resolution mechanic (count corners) |
| **Deep to master** | Cumulative scoring creates multi-turn planning; probability creates risk management |
| **Visually elegant** | Hexagonal geometry; natural triangle tessellation |
| **Tension throughout** | No locked territories; every triangle can shift; every turn matters |
| **AI-friendly** | Smaller action space than square grids; more symmetries for canonicalization |

---

## 2. Complete Rules

### 2.1 Components

**Board:** A radius-3 hexagonal grid providing:
- **24 vertices** (stone placement positions)
- **42 triangular regions** (scoring areas)

```
                 o---o---o
                /|\ /|\ /|\
               o-+-o-+-o-+-o
              /|\ /|\ /|\ /|\
             o-+-o-+-o-+-o-+-o
            /|\ /|\ /|\ /|\ /|\
           o-+-o-+-o-+-o-+-o-+-o
            \|/ \|/ \|/ \|/ \|/
             o-+-o-+-o-+-o-+-o
              \|/ \|/ \|/ \|/
               o-+-o-+-o-+-o
                \|/ \|/ \|/
                 o---o---o

    Legend: o = vertex (stone placement)
            Lines connect adjacent vertices
            Each small triangle is a scoring region
```

**Stones:** Two colors (Black and White), sufficient quantity for full board coverage (approximately 12-14 per player for typical games).

**Scoring Track:** Method to track cumulative scores for both players.

### 2.2 Setup

1. Place the empty hexagonal board between players
2. Each player takes stones of their color
3. Set both players' scores to zero
4. Determine first player (Black traditionally moves first)

### 2.3 Turn Structure

Players alternate turns. Each turn consists of two phases:

**PHASE 1: PLACEMENT (Active Player)**
1. Choose any unoccupied vertex on the board
2. Place exactly one stone of your color on that vertex
3. Stones are permanent - once placed, they cannot be moved or removed

**PHASE 2: INFLUENCE RESOLUTION (After Each Placement)**
After the active player places their stone, resolve scoring for ALL 42 triangles:

For each triangle, examine its three corner vertices and award points:

| Configuration | Points Awarded |
|--------------|----------------|
| 3 Black corners | Black: +1.00, White: +0.00 |
| 3 White corners | Black: +0.00, White: +1.00 |
| 2 Black, 1 White | Black: +0.67, White: +0.33 |
| 2 White, 1 Black | Black: +0.33, White: +0.67 |
| 2 Black, 1 Empty | Black: +0.67, White: +0.00 |
| 2 White, 1 Empty | Black: +0.00, White: +0.67 |
| 1 Black, 1 White, 1 Empty | Black: +0.33, White: +0.33 |
| 1 Black, 2 Empty | Black: +0.33, White: +0.00 |
| 1 White, 2 Empty | Black: +0.00, White: +0.33 |
| 3 Empty corners | No points awarded |

Add the total points from all triangles to each player's cumulative score.

### 2.4 Influence Calculation

The influence formula is straightforward:

```
For each triangle:
    Player influence = (corners with player's stones) / 3
    Points awarded = player influence
```

**Example Calculation:**

After Black places their 5th stone, the board has:
- 12 triangles with no stones at any corner: 0 points each
- 8 triangles with exactly 1 Black corner: 8 x 0.33 = 2.67 points to Black
- 6 triangles with exactly 1 White corner: 6 x 0.33 = 2.00 points to White
- 4 triangles with 2 Black corners: 4 x 0.67 = 2.67 points to Black
- 3 triangles with 2 White corners: 3 x 0.67 = 2.00 points to White
- 2 triangles with 1 Black, 1 White corner: 2 x 0.33 = 0.67 each
- etc.

**Turn Score:** Black gains 6.00 points; White gains 4.67 points
These are added to cumulative totals.

### 2.5 Victory Conditions

The game ends when:
1. **Board Full:** All 24 vertices are occupied (12 stones each)
2. **Mutual Pass:** Both players pass consecutively (rare, typically when further play is clearly disadvantageous)
3. **Score Threshold:** (Optional variant) A player reaches a predetermined score

**Winner:** The player with the higher cumulative score wins.

**Tiebreaker:** If scores are exactly equal (extremely rare), the player who placed second wins (compensating for first-move advantage).

### 2.6 Rules Summary Card

```
INFLUENCE: HEX EDITION - Quick Reference

SETUP: Empty radius-3 hex board, scores start at 0

YOUR TURN:
  1. Place one stone on any empty vertex
  2. Score all 42 triangles based on corners:
     - Your corner = +0.33 points to you
     - (So 2 corners = +0.67, 3 corners = +1.00)
  3. Add points to cumulative scores

GAME END: When board is full (24 stones total)

WINNER: Highest cumulative score
```

---

## 3. Mechanics Deep Dive

### 3.1 Stone Placement on Vertices

**The Topology**

Unlike typical hex games where pieces occupy hex centers, Influence: Hex Edition uses vertex placement. Each vertex is a point where three hexagonal faces meet, which means:

- Each vertex touches exactly **6 triangles** (if interior) or fewer (if on edge/corner)
- Each vertex has exactly **3 adjacent vertices** (not 6 like hex-center games)
- Movement between vertices follows the triangular lattice

```
Interior Vertex:          Edge Vertex:
    o                         o
   /|\                       /|
  / | \                     / |
 o--+--o                   o--+--o
  \ | /                       |
   \|/                        |
    o                         o
(6 triangles)            (4 triangles)
```

**Strategic Implications of Vertex Placement**

The 3-neighbor constraint (vs 4 in square grids or 6 in hex-center games) creates:

1. **Forced Commitment:** With fewer expansion directions, each placement commits you to a spatial region
2. **Natural Choke Points:** Vertices where paths converge become strategically critical
3. **Efficient Coverage:** A single stone at an interior vertex influences 6 triangles simultaneously

**Vertex Categories by Influence Potential**

| Position | Triangles Touched | Strategic Value |
|----------|-------------------|-----------------|
| Center vertex | 6 | Highest - influences most regions |
| First ring | 6 | High - good influence, some edge access |
| Second ring | 5-6 | Medium - balance of influence and control |
| Edge vertices | 3-4 | Lower influence but easier to defend |
| Corner vertices | 2 | Lowest influence but nearly uncontestable |

### 3.2 Triangle Resolution Each Turn

**The Resolution Mechanic**

Every turn, after a stone is placed, all 42 triangles are evaluated. This is the heart of the game's innovative scoring system.

**Why Every Turn Matters**

Consider two triangles:

*Triangle A:* Black claims 2 corners on turn 3, maintains through turn 12
- Scores 0.67 points per turn for 10 turns = 6.70 total points

*Triangle B:* Black claims 2 corners on turn 10, maintains through turn 12
- Scores 0.67 points per turn for 3 turns = 2.01 total points

Early territorial investment yields compound returns. This creates urgency in the opening and makes "defensive" plays that protect early investments strategically valuable.

**The Probability Model**

While scoring uses expected values (0.33, 0.67, 1.00), an optional variant can use actual dice rolls:

```
For each contested triangle (not 0 or 3 corners for one player):
  Roll 1d3 (or 1d6: 1-2, 3-4, 5-6)
  - If result <= player's corners: player scores +1
  - Otherwise: no points (or opponent scores if they have more corners)
```

This adds dramatic tension but increases game length variance. The deterministic fractional scoring is recommended for strategic play.

### 3.3 Cumulative Scoring System

**Score Trajectory**

A typical game's score follows a predictable arc:

```
Score per Turn vs. Turn Number:

Points
  ^
  |                    ___---
  |               ___--
  |          ___--
  |     ___--
  |__---
  +-------------------------> Turn
   1    6    12   18   24

Early game: Low scoring (few stones on board)
Mid game: Scoring accelerates (board filling, more corners claimed)
Late game: Maximum scoring (most triangles have multiple corners occupied)
```

**Implications for Strategy**

1. **Early stones are investments** - They score every subsequent turn
2. **Late stones are sprints** - They generate immediate points but limited total contribution
3. **Lead preservation** - A 10-point lead with 5 turns left is nearly insurmountable (would need to outscore by 2+ per turn)
4. **Comeback potential** - A 10-point deficit with 15 turns left is very recoverable

**Score Velocity**

The concept of "score velocity" (points gained per turn) becomes critical:

- **Positive velocity differential:** You're gaining points faster than opponent
- **Breaking even:** Score gap stays constant
- **Negative velocity differential:** Opponent is catching up

Strategic play often involves sacrificing immediate points to establish positions that yield superior long-term velocity.

### 3.4 How Alternating Turns Changes Dynamics

**Comparison to Simultaneous Play**

The original Attention + Influence concept used simultaneous placement with collision mechanics. Alternating turns creates a fundamentally different game:

| Aspect | Simultaneous | Alternating |
|--------|--------------|-------------|
| **Information** | Imperfect (hidden moves) | Perfect (all moves visible) |
| **Strategy Type** | Game-theoretic, bluffing | Pure calculation, positioning |
| **Pacing** | Dramatic reveal moments | Methodical, chess-like |
| **AI Approach** | Requires opponent modeling | Standard minimax works well |
| **Player Preference** | Those who enjoy reading opponents | Those who enjoy perfect information |

**First-Mover Considerations**

With alternating turns, going first provides a tempo advantage:

- First player places stone #1, #3, #5... (odd numbered)
- They influence scoring for one more turn with their stones on average
- However, second player gets final placement (potentially decisive)

Playtesting suggests the advantage is slight (approximately 2-3 points over a full game). The tiebreaker rule (second player wins ties) addresses this cleanly.

**Response Windows**

Alternating turns create clear response opportunities:

1. **Immediate Response:** Counter opponent's last move directly
2. **Delayed Response:** Ignore their threat, develop elsewhere, return later
3. **Preemptive Play:** Place stones to reduce opponent's future options

The interaction between these creates rich tactical exchanges.

---

## 4. Gameplay Analysis

### 4.1 Opening Strategies

**The Central Gambit**

The center vertex touches 6 triangles - the maximum possible. Taking it first establishes immediate influence across the board's heart.

```
            o---o---o
           /|\ /|\ /|\
          o-+-o-+-o-+-o
         /|\ /|\ /|\ /|\
        o-+-o-+-B-+-o-+-o    B = Black's opening move
       /|\ /|\ /|\ /|\ /|\
      o-+-o-+-o-+-o-+-o-+-o
       \|/ \|/ \|/ \|/ \|/
        o-+-o-+-o-+-o-+-o
         \|/ \|/ \|/ \|/
          o-+-o-+-o-+-o
           \|/ \|/ \|/
            o---o---o
```

*Advantages:* Maximum triangle influence (6), forces opponent response, controls board center
*Disadvantages:* Predictable, opponent can surround, all 6 triangles become contested

**The Corner Anchor**

Taking a corner vertex (where only 2 triangles meet) is the opposite philosophy:

```
            B---o---o     B = Black's opening move
           /|\ /|\ /|\
          o-+-o-+-o-+-o
```

*Advantages:* Those 2 triangles are easy to claim (fewer corners to contest), establishes unchallenged base
*Disadvantages:* Low immediate influence, allows opponent to claim center

**The Ring Strategy**

Placing on the first ring around center - high influence (6 triangles) but with partial edge protection:

*Advantages:* 6-triangle influence, more defensible than pure center, flexible development
*Disadvantages:* Doesn't prevent center claims, slightly lower control

**Opening Principles**

1. **Influence vs. Security:** Interior positions touch more triangles but are harder to dominate; edge positions touch fewer but are more defensible
2. **Avoid Immediate Collision:** Early contested triangles score minimally for both players; consider establishing separate spheres initially
3. **Plan for Compounds:** Stones placed to share corners between multiple triangles are more efficient

### 4.2 Mid-Game Developments

**The Contested Frontier**

As the board fills, a "frontier" emerges - the boundary between each player's sphere of influence:

```
        B-+-B-+-o-+-o-+-W
       /|\ /|\ /|\ /|\ /|\
      B-+-B-+-?-+-W-+-W-+-W
       \|/ \|/ \|/ \|/ \|/
        B-+-?-+-?-+-W-+-W

    B = Black territory
    W = White territory
    ? = Contested frontier
```

**Mid-Game Decisions**

1. **Extend vs. Consolidate**
   - Extending: Place stones to claim new triangles (aggressive, spreads thin)
   - Consolidating: Place stones to complete 2-corner or 3-corner claims (defensive, maximizes existing claims)

2. **Contest vs. Concede**
   - When opponent has 2 corners of a triangle, you can:
     - Contest: Claim the 3rd corner (earning 0.33 vs their 0.67 each turn)
     - Concede: Focus elsewhere, let them have 0.67 but don't waste a stone

3. **Tempo Plays**
   - Forcing moves that demand response allow you to control game rhythm
   - Threatening to complete a 3-corner claim often forces defensive response

**The Efficiency Calculation**

At any moment, consider "points per stone" efficiency:

```
Stone at interior vertex touching 6 triangles:
  - If each has 1 of your corners: 6 x 0.33 = 2.00 points/turn
  - Per turn until game end

Stone at edge vertex touching 3 triangles:
  - If each has 1 of your corners: 3 x 0.33 = 1.00 points/turn
  - But may be easier to upgrade to 2 corners

Stone completing a 3-corner triangle:
  - Triangle goes from 0.67 to 1.00 (+0.33 increase)
  - But only affects one triangle vs potential multi-triangle placements
```

### 4.3 End-Game Considerations

**The Final Count**

With limited vertices remaining, the end-game becomes highly tactical:

**Forced Moves:** When a placement would complete an opponent's 3-corner triangle, it often must be contested (unless the defensive stone's value elsewhere is higher).

**Last Stone Advantage:** The player who places the final stone (second player, if board fills) gets their stone's full influence for only the final scoring round - but that's still valuable.

**Score Differential Awareness:**
- Large lead (20+ points): Play conservatively, avoid giving opponent efficient plays
- Close game (within 10 points): Calculate precisely, every triangle matters
- Large deficit: Take risks, contest aggressively, hope for opponent errors

**Resignation Points:** Experienced players recognize unwinnable positions. When the score differential exceeds what remaining turns could theoretically overcome, resignation is appropriate.

### 4.4 Common Patterns and Formations

**The Triangle Lock**

Three of your stones forming a triangle guarantees that central triangle:

```
        o---o---o
       /|\ /|\ /|\
      o-+-B-+-B-+-o     Triangle with 3 Black corners
       \|/ \|/ \|/       = 1.00 points to Black every turn
        o-+-B-+-o
```

**The Wedge**

Two stones sharing a triangle edge, pointing into enemy territory:

```
        B---B
       / \ / \
      o---?---o     Both stones at top form wedge
          |         Triangle "?" is contested
          o
```

**The Surround**

Encircling a single enemy stone to maximize your influence in adjacent triangles:

```
          B
         /|\
        B-+-W-+-B    White has center, but Black has
         \|/         all 6 adjacent corners
          B
```

**The Chain**

A line of stones maximizing corner coverage:

```
    B---B---B---B
   / \ / \ / \ / \
  o---o---o---o---o

This chain gives Black 2 corners on many triangles
```

**The Fortress**

Concentrated stones ensuring 3-corner control of a region:

```
        B---B
       /|\ /|\
      o-+-B-+-o     Center triangles are all fully Black
       \|/ \|/
        B---B
```

---

## 5. Game Experience

### 5.1 Decision Tension Points

**The Commitment Dilemma**

Every stone placement is permanent. The key tension is:
- Place now to secure points early (they compound)?
- Wait to see opponent's development (better information)?

Since you can't wait indefinitely, this creates constant pressure.

**The Greed Check**

When you see a high-value vertex (touches many triangles, completes favorable configurations), you must ask:
- Is it too greedy? Will opponent punish the overextension?
- Is it forcing? Will opponent have to respond, giving you tempo?

**The Sunk Cost Moment**

When a region you've invested in becomes contested:
- Throw in another stone to protect investment?
- Accept the loss and develop elsewhere?

This mirrors real investment decisions and creates emotional engagement.

**The End-Game Calculation**

With 4-6 stones left to place, the game becomes combinatorially analyzable:
- Do you calculate all possibilities?
- Do you trust your intuition?
- Do you try to induce opponent errors?

### 5.2 Emotional Arc of a Game

**Opening (Turns 1-6): Anticipation**
The board is empty, possibilities are vast. Each stone feels significant. Players establish their style - aggressive or defensive, central or peripheral.

**Early Middle (Turns 7-12): Engagement**
The board develops shape. Contact between spheres of influence creates the first real conflicts. Players experience the first "I should have..." moments.

**Late Middle (Turns 13-18): Tension**
The frontier crystallizes. Every play feels consequential. Score differentials become meaningful. The game's outcome feels uncertain.

**End Game (Turns 19-24): Resolution**
Calculations become precise. The winner often becomes apparent with 3-4 turns remaining. Satisfaction or frustration depending on outcome.

**Post-Game: Reflection**
"If I had placed there instead..." - The deterministic nature of resolution allows for clear analysis of what-if scenarios.

### 5.3 What Creates Memorable Moments

**The Unexpected Swing**

When a single stone placement suddenly flips multiple triangles from slight disadvantage (0.33) to strong advantage (0.67), or vice versa.

**The Lock-In**

Completing a 3-corner triangle that you've been building toward feels like checkmate - that territory is now guaranteed forever.

**The Perfect Response**

When opponent makes a threatening play and you find the one move that both defends AND advances your position.

**The Calculated Risk**

Choosing to contest a triangle at 33% influence because the alternative was worse - and having it matter in the final score.

**The Reading Success**

Predicting opponent's sequence of moves and preparing a counter-position that pays off 3-4 turns later.

### 5.4 Skill Expression vs. Luck Balance

**With Deterministic Fractional Scoring**

- **Skill Expression:** High - the game is pure strategy and calculation
- **Luck:** None - outcomes are fully determined by player choices
- **Feel:** Chess-like, cerebral, rewards study and practice

**With Probabilistic Resolution (Optional Variant)**

- **Skill Expression:** Medium-High - positioning still matters, but outcomes vary
- **Luck:** Moderate - 2-corner triangles (67%) fail often enough to create variance
- **Feel:** Poker-like, requires probabilistic thinking, emotional resilience

**Recommended Configuration**

For competitive play: Deterministic fractional scoring rewards skill consistently.

For casual play: Probabilistic resolution adds drama and allows weaker players to occasionally win through luck, keeping engagement high.

---

## 6. Strategic Depth

### 6.1 Positional Play

**The Influence Map**

At any game state, you can calculate each player's "influence map" - a visualization of how much each triangle contributes to each player:

```
Color intensity represents influence:
  |||  = Full control (1.00)
  || = Strong (0.67)
  | = Weak (0.33)
    = None (0.00)

      |||---||---B
     /|\ /|\ /|\
    ||--+--|-+--o     Reading the board:
   /|\ /|\ /|\ /|\    - Top-right is Black territory (full)
  |---+--?-+-W--W     - Left side is contested
   \|/ \|/ \|/ \|/    - Bottom-right is White territory
    o--+--W--+--||
```

Strong players develop intuition for reading these maps at a glance.

**Positional Principles**

1. **Central Control:** Interior vertices influence more triangles; controlling the center provides strategic flexibility

2. **Connectivity:** Stones that share corners of multiple triangles are more efficient than isolated placements

3. **Edge Anchors:** Establishing unchallenged control of edge triangles provides safe scoring base

4. **Balanced Development:** Spreading too thin leaves everything contestable; clustering too tight limits total influence

### 6.2 Tempo and Timing

**Understanding Tempo**

Tempo is the initiative - whose plan is being executed. You have tempo when opponent must respond to your threats rather than developing their own position.

**Gaining Tempo**

- **Threatening Multiple Completions:** Place a stone that threatens to complete two 3-corner triangles next turn
- **Creating Forks:** Force opponent to choose which threat to address
- **Efficient Placement:** Stones that serve multiple purposes gain tempo through efficiency

**Spending Tempo**

Sometimes losing tempo is worthwhile:
- Defensive plays that preserve high-value territories
- Consolidation moves that guarantee long-term scoring
- Blocking moves that prevent opponent development

**Timing Inflection Points**

Key moments when the game's tempo shifts:
- When the board transitions from "open" (many options) to "tight" (few options)
- When scoring velocity differential changes sign
- When one player completes a major territorial cluster

### 6.3 Risk Management

**Expected Value Calculations**

With deterministic scoring, "risk" means over-extension or misreading:

```
"Safe" play: Complete a 3-corner triangle
  - Guaranteed +1.00 per turn
  - Uses one stone for one triangle

"Aggressive" play: Start new development touching 4 triangles
  - Potentially +1.32 per turn (4 x 0.33)
  - But all four can be contested
```

**With Probabilistic Resolution:**

Expected value of a 2-corner triangle:
- 67% to score 1 point = 0.67 expected points

Expected value of two 1-corner triangles:
- Each 33% to score 1 point = 0.33 each = 0.66 expected points

The 2-corner approach is slightly better but concentrates variance.

**Portfolio Theory for Triangle Control**

Diversification principle applies:
- Many weakly-held triangles (high variance, higher ceiling)
- Few strongly-held triangles (low variance, reliable floor)

Conservative play: Prioritize 3-corner completions
Aggressive play: Maximize corner touches across many triangles

### 6.4 Counter-Strategies

**Against Central Play:**

If opponent takes center early:
1. **Surround:** Place stones around the center, contesting all 6 adjacent triangles
2. **Develop Periphery:** Claim edges and corners, ceding center entirely
3. **Split:** Take one side of the board, force opponent into only half the center's potential

**Against Peripheral Play:**

If opponent focuses on edges:
1. **Claim Center:** Take the high-influence interior positions
2. **Cut Connections:** Prevent their edge territories from linking
3. **Outpace:** Race to claim more territory while they consolidate

**Against Aggressive Extension:**

If opponent spreads thin:
1. **Contest Everything:** Place stones to block 3-corner completions
2. **Focus Fire:** Concentrate on one region to demonstrate your willingness to fight
3. **Wait and Punish:** Let them overextend, then claim the central regions they abandoned

**Against Defensive Consolidation:**

If opponent clusters stones:
1. **Expand Faster:** Claim more territory while they secure less
2. **Partial Contest:** Place stones to reduce their triangles from 1.00 to 0.67
3. **Time Pressure:** With cumulative scoring, their slow development yields fewer total points

---

## 7. Elegant Enhancements

The base game is intentionally minimal. The following enhancements can add variety without fundamentally altering the game's character.

### 7.1 The Momentum Token

**The Enhancement:**
At game start, each player receives one "Momentum Token." Once per game, after placing your stone, you may spend your token to immediately place a second stone.

**Why It Works:**
- Single use: Doesn't add ongoing complexity
- Creates one high-drama turn per player
- Timing becomes strategic (early for compound value vs. late for tactical precision)
- Balances naturally (both players have the same capability)

**What Gameplay It Creates:**
- "Token chicken" - waiting for opponent to spend theirs first
- Tempo swings - using the token to complete two threats simultaneously
- Defensive saves - token can prevent a disaster when opponent threatens multiple completions
- Opening variety - some players will use tokens on turns 1-2 for maximum compound value

### 7.2 The Keystone Triangle

**The Enhancement:**
Before the game, randomly designate one of the 42 triangles as the "Keystone." The Keystone triangle scores double points each turn. Mark it with a distinctive indicator.

**Why It Works:**
- Zero additional rules during play
- Creates a natural focal point for conflict
- Changes each game's texture slightly
- The Keystone's location (center vs. edge) dramatically affects strategy

**What Gameplay It Creates:**
- Fierce competition for Keystone corners
- Risk/reward decisions about over-committing to one triangle
- Opening variety based on Keystone location
- Some games become "Keystone games" while others see players ceding it to fight elsewhere

### 7.3 The Echo Score (Final Turn Bonus)

**The Enhancement:**
After the final stone is placed, resolve scoring one additional time. This "echo" round represents the lasting influence of the final board state.

**Why It Works:**
- Weights end-game positions more heavily
- Compensates for late-placed stones scoring fewer turns
- Creates suspense around the final placements
- No additional rules to remember during play

**What Gameplay It Creates:**
- Final positions matter more (not just "the game was decided 5 turns ago")
- Late-game planning intensifies
- Potential for dramatic reversals on the echo round
- Second player's final stone advantage is amplified (may need to adjust first-player compensation)

### 7.4 Territory Thresholds

**The Enhancement:**
Triangles with 3 corners of the same color (100% control) score 1.5 points instead of 1.0 points. This creates a bonus for "hard claims."

**Why It Works:**
- Rewards commitment and decisive control
- Creates clear incentive to complete territories
- Simple modification to scoring table
- Increases the stakes of completing vs. contesting

**What Gameplay It Creates:**
- "Closing" triangles (achieving 3 corners) becomes more valuable
- Defensive plays to prevent 3-corner completions increase
- Changes the math on when to consolidate vs. extend
- Creates more dramatic score swings when territories complete

### 7.5 The Shifting Board (Advanced Variant)

**The Enhancement:**
At the start of each round (every 4 turns), the board "rotates" 60 degrees for scoring purposes. Triangles that were on the edge are now interior, and vice versa. Stones don't move - only the scoring framework shifts.

**Why It Works:**
- Prevents static "solved" positions
- Rewards flexible positioning over rigid territorial control
- Creates unique strategic considerations
- Uses the natural 6-fold symmetry of the hexagonal board

**What Gameplay It Creates:**
- "Future rotation" planning - placing stones for positions that will be valuable after rotation
- Less emphasis on edge safety (edges become interior and vice versa)
- Dynamic tension as favorable positions become unfavorable
- Deep strategic reading for players who can track multiple rotation states

**Note:** This variant significantly increases complexity and is recommended only for experienced players seeking fresh challenges.

---

## Appendix A: Quick Reference Tables

### A.1 Influence Scoring Table

| Your Corners | Opponent Corners | Empty Corners | Your Points | Opponent Points |
|--------------|------------------|---------------|-------------|-----------------|
| 3 | 0 | 0 | 1.00 | 0.00 |
| 2 | 1 | 0 | 0.67 | 0.33 |
| 2 | 0 | 1 | 0.67 | 0.00 |
| 1 | 2 | 0 | 0.33 | 0.67 |
| 1 | 1 | 1 | 0.33 | 0.33 |
| 1 | 0 | 2 | 0.33 | 0.00 |
| 0 | 3 | 0 | 0.00 | 1.00 |
| 0 | 2 | 1 | 0.00 | 0.67 |
| 0 | 1 | 2 | 0.00 | 0.33 |
| 0 | 0 | 3 | 0.00 | 0.00 |

### A.2 Vertex Value by Position

| Position Type | Triangles Touched | Interior (6) | Second Ring | Edge | Corner |
|---------------|-------------------|--------------|-------------|------|--------|
| Vertex Count | - | 7 | 6 | 9 | 2 |
| Triangles | - | 6 | 5-6 | 3-4 | 2 |

### A.3 Game Length Estimates

| Pace | Turns | Approximate Duration |
|------|-------|---------------------|
| Blitz | 24 | 10-15 minutes |
| Standard | 24 | 20-30 minutes |
| Deep Analysis | 24 | 45-60 minutes |

---

## Appendix B: Designer Notes

### B.1 Why Hexagonal Geometry?

The choice of hexagonal vertices with triangular territories arose from seeking:

1. **Natural probability fractions:** Three corners per triangle creates 33.33% per corner - intuitive and elegant
2. **Isotropic geometry:** No privileged directions (unlike square grids with horizontal/vertical vs. diagonal)
3. **Compact action space:** 3 neighbors per vertex (vs. 4 in square grids) makes calculation more tractable
4. **Visual beauty:** Hexagonal patterns are aesthetically pleasing and culturally resonant

### B.2 Why Cumulative Scoring?

The cumulative (rolling) score system was chosen to:

1. **Reward early play:** Creates urgency and penalizes overly passive opening
2. **Maintain tension:** Every turn contributes to the score; no "dead" turns
3. **Enable comebacks:** Trailing player can catch up through superior velocity
4. **Create investment thinking:** Stones are assets that pay dividends over time

### B.3 Why Alternating Turns?

Compared to simultaneous play:

1. **Perfect information:** Reduces luck and guesswork
2. **AI tractability:** Standard search algorithms apply directly
3. **Clarity:** New players can understand what happened and why
4. **Response play:** Allows direct counters and tactical exchanges

### B.4 Balance Considerations

Through analysis and simulated play:

- First-player advantage is approximately 2-3 points (on a typical total of 200-250 points per player)
- The tiebreaker rule (second player wins ties) is a simple, elegant correction
- The 24-turn limit (board filling) provides natural game conclusion
- Score variance is low with deterministic resolution, supporting skill expression

---

## Appendix C: Implementation Notes (For Digital Versions)

### C.1 Board Representation

Use axial coordinates for the triangular lattice:

```python
@dataclass(frozen=True)
class Vertex:
    q: int  # Axial column
    r: int  # Axial row

    def neighbors(self) -> List[Vertex]:
        """Returns the 3 adjacent vertices."""
        # Exact implementation depends on lattice orientation
        pass

    def adjacent_triangles(self) -> List[Triangle]:
        """Returns triangles this vertex is a corner of."""
        pass
```

### C.2 Scoring Algorithm

```python
def calculate_turn_score(board: Board) -> Dict[Player, float]:
    scores = {Player.BLACK: 0.0, Player.WHITE: 0.0}

    for triangle in board.all_triangles():
        corners = [board.get_owner(v) for v in triangle.vertices]

        for player in [Player.BLACK, Player.WHITE]:
            player_corners = corners.count(player)
            scores[player] += player_corners / 3.0

    return scores
```

### C.3 AI Considerations

- **State space:** ~3^24 = ~2.8 x 10^11 theoretical states (much smaller in practice)
- **Action space:** Up to 24 legal moves (decreasing each turn)
- **Symmetry group:** D6 (12 symmetries) for position canonicalization
- **Evaluation:** Current cumulative scores + heuristic for remaining potential
- **Recommended approach:** Alpha-beta search with iterative deepening; neural evaluation for advanced implementation

---

*Document prepared for Influence: Hex Edition*
*A game of strategic territory control on hexagonal geometry*
