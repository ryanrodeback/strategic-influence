# FAULT LINES
## A Game of Probabilistic Stability

---

## 1. GAME OVERVIEW

### Core Concept

**Fault Lines** is a two-player abstract strategy game built on a singular, elegant tension: **build now, survive later**. Players take turns placing stones on a grid, forming groups through adjacency. But here's the twist: ownership is uncertain until the final reckoning. At game's end, every group must pass a survival roll. Small groups are fragile; large groups endure.

The name "Fault Lines" captures the essence of play. Like tectonic plates, your groups appear stable during placement, but the true test comes when the earthquake hits. Will your carefully positioned stones survive, or will entire regions collapse into nothing?

### The Unique Tension

Unlike traditional territory games where placed pieces are permanent, Fault Lines introduces **deferred uncertainty**. Every stone you place is a bet on the future. This creates a distinctive psychological experience:

```
Traditional Territory Game:
  Place stone -> Territory secured -> Done

Fault Lines:
  Place stone -> Territory claimed -> ...but will it survive?
```

This "build now, survive later" structure means players must constantly balance:
- **Immediate board presence** (placing stones to claim space)
- **Future survival probability** (connecting groups to ensure they persist)

The result is a game where the board state at any moment is merely a *potential* outcome. The true score emerges only through the ritual of the survival rolls.

### Design Philosophy

Fault Lines embodies three design principles:

1. **Simple Rules, Emergent Complexity**: One placement per turn, one roll per group. Everything else emerges from these foundations.

2. **Meaningful Uncertainty**: The dice don't feel random; they feel like judgment. Your decisions determine whether the odds favor you.

3. **Dramatic Resolution**: The endgame isn't a formality. It's a sequence of revelations where fortunes shift with each roll.

---

## 2. COMPLETE RULES

### Components

- **Board**: 9x9 grid (81 intersections) - recommended for standard play
  - Smaller boards (7x7) for faster games
  - Larger boards (13x13) for deeper strategic play
- **Stones**: Two colors (Black and White), 40+ each
- **One six-sided die** (d6)

### Setup

1. Place the empty board between players
2. Decide who plays Black (Black moves first)
3. Optional: Use the **Pie Rule** for tournament balance (after Black's first move, White may choose to swap colors)

### Turn Structure

On your turn, perform exactly one action:

**PLACE**: Put one of your stones on any **empty** intersection.

That's it. No attacks, no captures, no special moves. Just place.

### Groups

A **group** is a set of one or more stones of the same color that are **orthogonally connected** (sharing edges, not corners).

```
SINGLE GROUP:          TWO SEPARATE GROUPS:

  ● ● ●                    ● ●     ●
    ●                        ●
    ●

All connected            Diagonal doesn't
via edges                connect - these
                         are two groups
```

**Important**: Group membership is dynamic. Placing a stone between two groups of your color **merges** them into one larger group.

### Game End

The game ends when **both players pass consecutively**, indicating neither wishes to place more stones. (Alternatively, fixed turn limits can be used: 60 turns total for 9x9.)

### Resolution Phase

Once the game ends, resolve each group's fate:

**For each group on the board, in any order:**

1. Count the group's **size** (number of stones)
2. Roll one d6
3. The group **survives** if the roll is **less than or equal to** the group's size
4. If the group survives, all its stones count toward the owner's score
5. If the group fails, **remove all stones** in that group - they score nothing

### Survival Probability Table

| Group Size | Roll Needed | Survival Probability |
|------------|-------------|----------------------|
| 1 stone | Roll 1 | 16.7% (1 in 6) |
| 2 stones | Roll 1-2 | 33.3% (2 in 6) |
| 3 stones | Roll 1-3 | 50.0% (3 in 6) |
| 4 stones | Roll 1-4 | 66.7% (4 in 6) |
| 5 stones | Roll 1-5 | 83.3% (5 in 6) |
| 6+ stones | Roll 1-6 | 100% (guaranteed) |

### Victory

After all groups are resolved, count each player's **surviving stones**.

**Most surviving stones wins.**

In case of a tie: The player who placed fewer total stones wins (rewarding efficiency). If still tied, the game is a draw.

### Rule Clarifications

| Situation | Ruling |
|-----------|--------|
| Place on occupied space? | **Illegal** - must place on empty |
| Must I place each turn? | **No** - you may pass (but two consecutive passes end game) |
| Can I roll for groups in any order? | **Yes** - order doesn't affect outcome |
| Group reaches size 7+? | **Same as 6** - automatic survival (100%) |
| Stones touch diagonally only? | **Separate groups** - diagonals don't connect |

---

## 3. MECHANICS DEEP DIVE

### 3.1 Stone Placement and Group Formation

The placement mechanic appears trivially simple: put a stone on an empty space. Yet this simplicity conceals profound implications.

**Every placement is simultaneously:**
- A **territory claim** (this space is mine)
- A **group modification** (potentially merging or extending groups)
- A **connection opportunity** (possibly for you or blocked from opponent)
- A **survival investment** (another stone that must survive to score)

**Group Formation Dynamics:**

```
Turn 1:  ●           (1 group of size 1)

Turn 3:  ● . ●       (2 groups of size 1 each)

Turn 5:  ● ● ●       (1 group of size 3! Merging occurred)
```

The merge mechanic creates pivotal moments. A single stone placed between two friendly groups can:
- Double a group's survival probability (2 groups of 3 become 1 group of 6)
- Transform uncertainty into certainty (going from 50% to 100%)
- Fundamentally reshape the game's outcome probabilities

### 3.2 The d6 Survival Roll System

The six-sided die is not arbitrary. It's precisely calibrated to create strategic texture.

**Why d6 Works:**

1. **Intuitive Probabilities**: Sixths convert cleanly to percentages people understand (16.7%, 33.3%, 50%, etc.)

2. **Natural Threshold**: The die's maximum value (6) creates an achievable "safety" target. Unlike a d20 or d100, reaching certainty is realistic.

3. **Psychological Staging**: Each group size feels distinctly different:
   - Size 1-2: "Probably doomed" (nervous)
   - Size 3: "Coin flip" (tense)
   - Size 4-5: "Probably safe" (hopeful)
   - Size 6: "Definitely safe" (relieved)

4. **Physical Ritual**: Rolling a tangible die creates a ceremonial weight to the resolution phase. Each roll is a moment of truth.

### 3.3 The Magic Number: Why 6+ Matters

The threshold of 6 stones for guaranteed survival is the strategic sun around which all tactics orbit.

**The 6-Threshold Creates:**

```
STRATEGIC GRAVITY:

  Stones are "pulled" toward forming groups of 6

  Groups of 5 are "almost safe" - one more stone completes them

  Groups of 7+ are "wasteful safety" - overkill

  The ideal: exactly 6, no more, no less
```

**Mathematical Foundation:**

Below 6, every additional stone provides diminishing marginal survival improvement:
- 1 to 2: +16.6% survival (from 16.7% to 33.3%)
- 2 to 3: +16.7% survival (from 33.3% to 50.0%)
- 3 to 4: +16.7% survival (from 50.0% to 66.7%)
- 4 to 5: +16.6% survival (from 66.7% to 83.3%)
- 5 to 6: +16.7% survival (from 83.3% to 100%)

Above 6, additional stones add zero survival benefit but do add scoring potential *if* they contribute to keeping the group at 6+.

This creates a natural optimization puzzle: **How do I reach 6 with the minimum stones?** But also: **Do I make one group of 12 or two groups of 6?**

### 3.4 Connection vs. Expansion Trade-offs

The fundamental decision every turn: do I **expand** (claim new territory) or **connect** (secure existing territory)?

```
EXPANSION PRIORITY:            CONNECTION PRIORITY:

● . . . . ●                    ● ● ● ● ●
. . . . . .
● . . . . ●     vs.            . . . . .
. . . . . .
● . . . . ●                    . . . . .

6 stones, 6 groups             5 stones, 1 group
~16.7% each survives           100% survival
Expected: 1 stone              Expected: 5 stones

WIDER COVERAGE                 GUARANTEED SCORE
but HIGH RISK                  but LIMITED SCOPE
```

**The Trade-off Math:**

Consider 6 stones to place. You could:

**Option A - Maximum Spread**: 6 isolated stones
- Each survives with 16.7% probability
- Expected surviving stones: 6 x 0.167 = **1.0 stones**
- Best case: 6 stones | Worst case: 0 stones

**Option B - Single Chain**: 1 group of 6
- 100% survival probability
- Expected surviving stones: **6.0 stones**
- Best case: 6 stones | Worst case: 6 stones

**Option C - Two Triplets**: 2 groups of 3
- Each survives with 50% probability
- Expected surviving stones: 6 x 0.5 = **3.0 stones**
- Best case: 6 stones | Worst case: 0 stones

The math overwhelmingly favors connection... but the game isn't played in isolation. An opponent who sees you building one group can interfere. Spreading creates multiple threats they can't all address.

---

## 4. GAMEPLAY ANALYSIS

### 4.1 Early Game: Claiming vs. Connecting

**Turns 1-15: The Land Grab**

The opening phase is dominated by a classic strategic question: *establish position or build infrastructure?*

**Claiming Strategy:**
```
Turn 1:  . . ● . .      Turn 3:  . . ● . .      Turn 5:  ● . ● . ●
         . . . . .               . . . . .               . . . . .
         . . . . .               ● . . . ●               ● . . . ●
         . . . . .               . . . . .               . . . . .
         . . . . .               . . . . .               . . . . .

Scattered placement stakes out territory but creates many size-1 groups.
```

**Connecting Strategy:**
```
Turn 1:  . . ● . .      Turn 3:  . . ● . .      Turn 5:  . . ● . .
         . . . . .               . . ● . .               . . ● . .
         . . . . .               . . . . .               . . ● . .
         . . . . .               . . . . .               . . . . .
         . . . . .               . . . . .               . . . . .

Linear building creates one growing group but surrenders board presence.
```

**Optimal Early Game:**

The strongest early game typically involves **clustered claiming** - placing stones that are near each other (1-2 spaces apart) but not yet connected. This preserves:
- Future connection opportunities
- Board presence across multiple regions
- Flexibility based on opponent's response

```
CLUSTERED CLAIMING (Recommended):

Turn 5:  . . ● . .
         . . . ● .
         . ● . . .
         . . . . .
         . . . . .

Stones are close enough to connect later but spread enough to claim space.
```

### 4.2 Mid Game: The Race to 6 vs. Denial

**Turns 16-40: The Critical Phase**

By mid-game, group structures become apparent. Each player typically has:
- 1-3 "main" groups that could potentially reach size 6
- Several "satellite" stones or small groups
- Emerging connection paths

**The Race to 6:**

Both players are acutely aware of the 6-threshold. Watch for:

```
THREAT DETECTION:

Your opponent has:     ● ● ● ● ●     (Size 5 - one away from safety!)

Their obvious move:    ● ● ● ● ● ●   (Size 6 - guaranteed survival)

Your denial move:      ● ● ● ● ●
                             ○       (Block the extension point)
```

**Denial Tactics:**

Mid-game often becomes about preventing opponent's connections:

1. **The Block**: Place directly in opponent's connection path
2. **The Wedge**: Insert between two opponent groups that want to merge
3. **The Surround**: Encircle an opponent group at size 5, denying expansion

**Strategic Priority Assessment:**

Each turn, evaluate:
- How close are my groups to 6?
- How close are opponent's groups to 6?
- Can I reach 6 faster than I can deny them?
- If I connect, can they block me next turn?

### 4.3 Late Game: Surgical Connections and Blocks

**Final Turns: Every Stone Matters**

The endgame is characterized by:
- Fewer empty spaces
- Clear group boundaries
- High-stakes individual placements

**Surgical Connections:**

Late game connections are the most powerful moves. A single stone placed perfectly can:
```
BEFORE:                         AFTER:

● ● ●       ○ ● ●              ● ● ●       ○ ● ●
    . . .                           ● . .
    . . ● ● ●                       . . ● ● ●

Group 1: Size 3 (50%)          Group 1: Size 7 (100%)
Group 2: Size 3 (50%)

Expected: 3 stones             Expected: 7 stones
One stone placement = +4 expected stones!
```

**The Endgame Calculus:**

With few turns remaining, calculate precisely:
1. What's my expected score if I pass now?
2. What's my expected score if I place here?
3. What's my opponent's expected score after my placement?

Sometimes the correct play is to **pass**, ending the game before your opponent can make a crucial connection.

### 4.4 Common Patterns and Formations

**The Ladder:**
```
●
● .
● . .
● . . .
● . . . .
●

A ladder is space-efficient and guarantees size 6+.
Weakness: easily blocked if opponent cuts ahead.
```

**The Fork:**
```
    ●
    ●
  ● ● ●

This group of 5 can extend in THREE directions to reach 6.
Very hard to fully block. Premium mid-game formation.
```

**The Bridge:**
```
● ● ●   ● ● ●
      ●

Two groups of 3, connected by a single stone = one group of 7.
The bridging stone is the highest-value placement possible.
```

**The Wall:**
```
● ● ● ● ● ●

Simple horizontal or vertical line of 6.
Guaranteed survival but uses maximum space.
Vulnerable during construction (opponent can cut).
```

**The Cluster:**
```
  ● ●
● ● ● ●
  ● ●

Size 8 group that's compact and hard to interfere with.
Multiple extension directions for even more growth.
```

---

## 5. GAME EXPERIENCE

### 5.1 The Psychological Weight of End-Game Resolution

The resolution phase is where Fault Lines transcends typical strategy games. Throughout play, every placement has been probabilistic - a promise, not a certainty. Now, those promises come due.

**The Moment Before the Roll:**

When you pick up the die to roll for a group of 3, you experience genuine tension. It's 50/50. Half your games, it survives. Half, it doesn't. No skill, no clever play - just the judgment of chance on the structure you built.

This creates a unique relationship between player agency and outcome. You **chose** to leave that group at size 3. You could have connected it. You decided the 50% was acceptable. Now you live with that choice.

**The Ritual of Rolling:**

Experienced players develop rituals around the resolution phase:
- Rolling your largest (safest) groups first to "bank" points
- Rolling your smallest (riskiest) groups first to "get them over with"
- Letting your opponent roll your groups (psychological surrender to fate)

### 5.2 Watching Groups Survive or Collapse

The resolution phase is a **narrative sequence**. Each roll reveals a chapter of the story:

```
RESOLUTION DRAMA:

Group 1 (Size 6): Automatic survival. Safe.
  [SURVIVES: 6 points banked]

Group 2 (Size 4): Roll needed... 4 or less.
  [Rolls 3] SURVIVES! Relief floods in.
  [SURVIVES: 4 more points - total 10]

Group 3 (Size 2): Roll needed... 2 or less.
  [Rolls 5] FAILS.
  [REMOVED: those 2 stones are gone]

Opponent's Group 1 (Size 5): Roll needed... 5 or less.
  [Rolls 6] FAILS!
  Their largest group... gone.

Final score swings dramatically.
```

This creates **emergent drama** that no designer scripted. The game's mathematics ensure that approximately one-third of stones placed will fail to survive (weighted by group sizes), meaning every game has genuine rises and falls.

### 5.3 "All Eggs in One Basket" vs. Diversification

**The Portfolio Question:**

Fault Lines forces players to answer a question borrowed from investment theory: **Do you concentrate or diversify?**

**Concentration (One Big Group):**
```
● ● ● ● ● ● ● ● ● ● ● ●

Size 12 group = 100% survival = 12 guaranteed points
No variance. You know exactly what you'll score.
But: you've committed everything to one structure.
```

**Diversification (Many Medium Groups):**
```
● ● ● ●    ● ● ● ●    ● ● ● ●

Three size-4 groups = 66.7% survival each
Expected value: 12 x 0.667 = 8 points
High variance. Could score 12, could score 4, could score 0.
But: harder for opponent to destroy everything.
```

**The Hybrid Approach:**

Sophisticated players often build **one safe group** (size 6+) as a floor, then take calculated risks with remaining stones. This guarantees a minimum score while preserving upside.

### 5.4 What Creates Dramatic Finishes

Fault Lines is engineered for dramatic conclusions. Several factors ensure exciting endgames:

**1. The Uncertainty Principle:**
Until resolution, the winner is unknown. Even a dominant board position can collapse if groups fail their rolls.

**2. The Cascade Effect:**
When one group fails, the emotional stakes for remaining rolls increase. If your large group failed, suddenly your small group's roll becomes crucial.

**3. The Reversal Potential:**
A player behind on board presence can win if opponent's groups fail. This keeps "losing" players engaged.

**4. The Last Roll:**
Often, the game comes down to a single decisive roll. Both players watch the die, knowing the outcome hinges on this moment.

```
DRAMATIC FINISH SCENARIO:

Board state shows:
Player 1: 18 stones in groups likely to survive ~15
Player 2: 14 stones in groups likely to survive ~12

Looks like Player 1 wins. But then:
- Player 1's size-4 group fails (6 stones gone)
- Player 2's size-3 group succeeds (3 stones saved)

Actual outcome:
Player 1: 9 stones | Player 2: 12 stones

Player 2 wins from behind!
```

---

## 6. STRATEGIC DEPTH

### 6.1 Connection Priority Ordering

Not all potential connections are equal. Advanced players evaluate connections using a **priority framework**:

**Priority 1 - The Safety Connection:**
Connecting brings a group to size 6+.
```
Before: ● ● ● ● ●  (Size 5, 83.3% survival)
After:  ● ● ● ● ● ● (Size 6, 100% survival)
Value: +16.7% survival on 6 stones = +1.0 expected stones
```

**Priority 2 - The Merger Connection:**
Connecting two groups that together exceed 6.
```
Before: ● ● ●   ● ● ● (Two size-3 groups, 50% each)
After:  ● ● ● ● ● ● ● (One size-7 group, 100%)
Value: Expected stones goes from 3.0 to 7.0 = +4.0 expected stones
```

**Priority 3 - The Probability Boost:**
Any connection that materially improves survival odds.
```
Before: ● ● (Size 2, 33.3% survival)
After:  ● ● ● (Size 3, 50% survival)
Value: +16.7% survival on 3 stones = +0.5 expected stones
```

**Priority 4 - The Investment Connection:**
Connection that positions for future growth.
```
● ●
  ● <-- This stone doesn't reach size 6 yet

But it creates multiple extension paths toward 6.
```

### 6.2 Splitter Move Timing

A **splitter move** places a stone between two opponent groups to prevent their merger. Timing is critical:

**Too Early:**
```
Turn 10: Opponent has  ○ ○     ○ ○
         You play      ○ ○  ●  ○ ○

But opponent still has 30+ turns to route around your block.
Wasted move.
```

**Too Late:**
```
Turn 45: Opponent has  ○ ○ ○ ○ ○ ○
         They already connected!

Missed the window.
```

**Just Right:**
```
Turn 38: Opponent has  ○ ○ ○     ○ ○ ○
         Few turns remain, they're about to connect.
         You play      ○ ○ ○  ●  ○ ○ ○

Now they have two size-3 groups (50% each) instead of one size-6 (100%).
Expected value destroyed: 3.0 stones (from 6.0 to 3.0)
```

**Splitter Decision Framework:**
1. Can opponent route around? (If yes, wait)
2. Is connecting my own groups higher value? (Compare expected value)
3. Are they about to connect next turn? (If yes, now or never)

### 6.3 Risk Portfolio Theory

Advanced Fault Lines strategy borrows from portfolio management:

**Core Holding (Low Risk):**
One group of size 6+ that guarantees a minimum score.
```
Value: Floor establishment. You cannot score below this.
```

**Growth Holdings (Medium Risk):**
Groups of size 4-5 that are likely (but not certain) to survive.
```
Value: Expected positive return with acceptable variance.
```

**Speculative Holdings (High Risk):**
Small groups or isolated stones in valuable positions.
```
Value: High upside if they survive; positioned to block or connect.
```

**Portfolio Construction Example:**

```
BALANCED PORTFOLIO:

● ● ● ● ● ●          Size 6: 100% - Core (6 guaranteed)

● ● ● ●              Size 4: 66.7% - Growth (2.67 expected)

● ●                  Size 2: 33.3% - Speculative (0.67 expected)

●                    Size 1: 16.7% - Speculative (0.17 expected)

Total: 13 stones
Expected surviving: 6 + 2.67 + 0.67 + 0.17 = 9.5 stones
Floor: 6 stones (guaranteed from core)
Ceiling: 13 stones (if all survive)
```

### 6.4 Reading Opponent's Group Structure

**Group Assessment:**

At any point, you should know:
- How many groups does opponent have?
- What are their sizes?
- Which groups can reach 6?
- What connections are they threatening?

**Threat Assessment Matrix:**

| Opponent Group Size | Stones to Safety | Your Priority |
|---------------------|------------------|---------------|
| 5 | 1 | CRITICAL - Block or they're safe |
| 4 | 2 | HIGH - Watch for connection |
| 3 | 3 | MEDIUM - Monitor but flexible |
| 1-2 | 4+ | LOW - Likely doomed anyway |

**Reading Future Moves:**

Look at opponent's isolated stones. Are they:
- Dead ends (no connection possible)? = Likely to fail
- Bridge-able to main groups? = Threatening

```
READING THE POSITION:

    ○ ○ ○         This opponent group of 3 is at 50%.
        .         But this empty space...
    ○ ○           ...connects to another group of 2!

If opponent places there: size 6 group (100%)
If you place there: you block, they have two groups (50% + 33%)

THIS SPACE IS CRITICAL.
```

---

## 7. ELEGANT ENHANCEMENTS

The following modifications preserve Fault Lines' elegance while adding strategic texture. Each enhancement is small, thematic, and creates interesting gameplay.

### Enhancement 1: The Aftershock Rule

**The Enhancement:**
When a group **fails** its survival roll, the owner may immediately attempt to **salvage** one stone from the group. Pick one stone and roll again - on a 1, that single stone survives.

**Why It Works:**
- Adds no complexity to placement phase
- Feels thematically appropriate (searching for survivors after the earthquake)
- Maintains the dramatic tension of resolution
- 16.7% salvage chance is impactful but not game-breaking

**Gameplay It Creates:**
- Decisions about which stone to salvage (positional considerations linger even in failure)
- Additional dramatic moments during resolution
- Reduces the "feel bad" of complete group failure
- Approximately +0.17 expected stones per failed group

### Enhancement 2: Fault Line Territories

**The Enhancement:**
Before the game, mark 4-6 intersections as "Fault Lines" (using dots or different coloring). Stones placed on Fault Lines **do not connect** to adjacent stones (for group formation purposes), though they still score if they survive.

**Why It Works:**
- Pre-game setup is simple (mark a few spaces)
- Creates strategic texture without new rules
- Natural chokepoints and strategic decisions
- Thematically perfect (the name finally makes physical sense!)

**Gameplay It Creates:**
```
Without fault lines:     With fault lines (marked X):

● ● ● ● ●               ● ● X ● ●
One group of 5          Two groups: 2 and 2

The fault line SPLITS the connection!
```
- Natural barriers create distinct "regions"
- Players must route around fault lines
- New blocking strategies (force opponent toward fault lines)
- Increased value of non-fault-line territories

### Enhancement 3: Keystone Marking

**The Enhancement:**
Once per game, when placing a stone, a player may declare it a **Keystone** (flip it or mark it). A Keystone counts as **2 stones** for group size purposes (but still only as 1 for scoring).

**Why It Works:**
- One-time ability is easy to track
- Creates a crucial timing decision
- Doesn't change core mechanics
- Bridges the gap between size 5 (risky) and size 6 (safe)

**Gameplay It Creates:**
- "When do I use my Keystone?" becomes a strategic layer
- A group of 5 with a Keystone is safe (5 + 1 effective = 6)
- Mind games: has opponent used their Keystone?
- Rewards patient timing (using it for maximum impact)

### Enhancement 4: Progressive Endgame (Variant)

**The Enhancement:**
Instead of rolling for all groups at once, resolve the board in **waves**. First, roll for all size 1-2 groups. Then all size 3-4 groups. Then size 5+ groups. After each wave, players may **pass or place one stone** before the next wave.

**Why It Works:**
- Uses the same dice mechanic
- Adds mid-resolution agency
- Creates information reveals that inform decisions
- Extends dramatic tension

**Gameplay It Creates:**
- You learn which small groups survived before placing your final stone
- Emergency connections: "My size-3 survived! Quick, connect it!"
- New end-game phase with different decision calculus
- More dramatic swings as information unfolds
- Games feel like epic three-act conclusions

### Enhancement 5: Resonance Bonus

**The Enhancement:**
If **all** of a player's groups survive the resolution phase (regardless of size), that player scores a **Resonance Bonus** of +3 stones.

**Why It Works:**
- No changes to core mechanics
- Rewards clean, disciplined play
- Creates tension around diversification strategy
- Simple scoring addition

**Gameplay It Creates:**
```
RESONANCE DECISION:

You have: ● ● ● ● ● ● (size 6, 100%)
          ● ● (size 2, 33.3%)

Option A: Leave as is
  - Size 6 survives (6 pts)
  - Size 2 survives 33.3% (0.67 expected pts)
  - Resonance 33.3% chance (+1 expected pts)
  - Total expected: 7.67 pts

Option B: Connect them (spend a turn)
  - Size 8 survives (8 pts)
  - Resonance 100% (+3 pts)
  - Total expected: 11 pts

The Resonance Bonus CHANGES the math!
```

- Encourages connecting even "wasteful" connections
- Provides comeback potential (smaller but unified beats larger but fragmented)
- New strategic layer: should I pursue Resonance or maximize expected stones?

---

## 8. SUMMARY

### What Makes Fault Lines Work

**Fault Lines** succeeds through elegant alignment of mechanics and experience:

| Mechanic | Player Experience |
|----------|-------------------|
| One placement per turn | Clarity and accessibility |
| Orthogonal connection | Intuitive group formation |
| d6 survival rolls | Understandable probabilities |
| Size-based survival | Natural strategic gradient |
| 6-stone safety threshold | Clear optimization target |
| End-game resolution | Dramatic, uncertain conclusions |

### Strategic Summary

```
EARLY GAME:   Claim territory with an eye toward future connection
MID GAME:     Race to build safe groups while denying opponent
LATE GAME:    Surgical placements to finalize group structures
RESOLUTION:   Live with the consequences of your choices
```

### The Core Experience

Fault Lines delivers what few games achieve: **meaningful uncertainty**. Every decision you make shapes the probability space of outcomes, but never determines them entirely. You are not playing against randomness; you are playing *with* randomness, building structures designed to survive the final test.

The game asks a simple question each turn: *How much do you trust this group to survive?*

Your answer shapes everything.

---

### Design Recommendations for Implementation

**For Physical Play:**
- Standard Go stones work perfectly
- Any 9x9 Go board is ideal
- A single d6 is all that's needed
- Mark fault line intersections with stickers (if using Enhancement 2)

**For Digital Implementation:**
- Highlight potential connections during placement
- Show survival probabilities for each group
- Animate the resolution phase dramatically
- Track historical win rates for different strategies

**For Tournament Play:**
- Implement Pie Rule for first-move balance
- Fixed turn limit (60 turns for 9x9) prevents stalling
- Require simultaneous sealed passing (prevents pass-bluffing)
- Consider the Resonance Bonus enhancement for higher-skill play

---

*Fault Lines: Build your empire. Roll the dice. Survive the quake.*
