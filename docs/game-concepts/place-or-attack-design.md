# PLACE OR ATTACK
## Strategic Board Game Concept Sketch

---

## 1. COMPLETE RULES

### Components
- **Board**: 7x7 grid (49 territories) - optimal for 2 players
  - Small enough for decisive games (15-25 turns)
  - Large enough for strategic maneuvering
- **Stones**: Two colors (e.g., Black and White), ~25 each

### Setup
- Empty board
- Black moves first (with balancing mechanism - see below)

### Turn Structure
Each turn, the active player performs **exactly ONE action**:

#### A) PLACE
- Put one of your stones on any **empty** territory
- Territory is now claimed by you

#### B) ATTACK
- **Prerequisite**: You must have at least 1 stone orthogonally adjacent to the target
- Target any **enemy-occupied** territory
- **Resolution**: Roll independently for each of YOUR adjacent stones (50% each)
  - If ANY roll succeeds → target flips to your control
  - If ALL rolls fail → target remains enemy-controlled (no penalty)

### Adjacency
- **Orthogonal only** (4 directions: up, down, left, right)
- Diagonals do NOT count for attack purposes

### Victory Conditions
**Primary (Domination)**: Reduce opponent to 0 territories → Immediate victory

**Secondary (Turn Limit)**: After 40 total turns (20 per player):
- Most territories wins
- **Tie-breaker**: Player with the most stones in the center 3x3 region wins
- **Second tie-breaker**: Player 2 (White) wins (compensates for first-mover disadvantage)

### Rule Clarifications
| Situation | Ruling |
|-----------|--------|
| Attack with 0 adjacent stones? | **Illegal** - must have ≥1 adjacent |
| Attack your own stone? | **Illegal** - can only attack enemy |
| Place on occupied territory? | **Illegal** - place only on empty |
| Pass turn? | **Not allowed** - must take an action |
| Attack succeeds, what happens? | Enemy stone removed, YOUR stone placed |

---

## 2. GAME EXPERIENCE ANALYSIS

### The Place/Attack Tension

This is the heart of the game. Each turn presents a meaningful choice:

```
PLACE is better when:
├── Early game (territory grab phase)
├── No good attack targets (isolated enemy stones)
├── Need to extend influence to new regions
├── Building toward future attack positions
└── Opponent has strong defensive clusters

ATTACK is better when:
├── High adjacency count (3-4 stones surrounding target)
├── Target is strategically vital (cuts enemy in two)
├── Opponent is overextended (thin lines)
├── You're behind on territory (need to flip the script)
└── Attacking denies opponent a key position
```

**The Fundamental Trade-off**:
- PLACE: Guaranteed +1 territory, but uses your action on expansion
- ATTACK: Probabilistic +1 territory (you flip theirs), but you don't expand

### Attack Probability Table

| Adjacent Stones | Success Rate | Expected Value |
|-----------------|--------------|----------------|
| 1 | 50.0% | 0.50 territories gained |
| 2 | 75.0% | 0.75 territories gained |
| 3 | 87.5% | 0.875 territories gained |
| 4 | 93.75% | 0.9375 territories gained |

**Critical Mass**: 3 adjacent stones represents the threshold where attacks become "near-certain" (87.5%). At 4 stones, failure is rare (6.25%).

**Strategic Insight**: Even a 50% attack can be correct if the target is worth more than a random placement. Position matters more than pure probability.

### Front Line Dynamics

```
Turn 1-6:   LAND GRAB
            Players scatter stones across the board
            Little direct contact

Turn 7-14:  FRONT FORMATION
            Territories begin to border each other
            Players must choose: extend vs. consolidate
            First attacks become viable

Turn 15-25: ACTIVE COMBAT
            Front lines solidify
            Attacks and counter-attacks
            Momentum swings possible

Turn 26+:   ENDGAME
            Territory counts matter
            Desperate attacks or defensive holds
```

### Turn-to-Turn Interest

What makes each turn engaging:

1. **Probability Drama**: Will the 75% attack succeed? Genuine tension.
2. **Positional Puzzles**: Where should I place to threaten multiple targets?
3. **Tempo Decisions**: Attack now (risky) or build up (slower but safer)?
4. **Reading Opponent**: What are they threatening? Where will they strike?
5. **Risk/Reward**: The eternal gambler's dilemma, but with skill involved.

---

## 3. STRATEGIC DEPTH ANALYSIS

### Expansion vs. Consolidation

**Expansion Strategy**:
```
+ Claims more territory quickly
+ Threatens multiple fronts
+ Forces opponent to react
- Creates thin, vulnerable lines
- Each stone has fewer friendly neighbors
- Susceptible to divide-and-conquer attacks
```

**Consolidation Strategy**:
```
+ Stones protect each other (mutual adjacency)
+ Hard to attack (enemy needs to build up adjacency first)
+ Strong defensive posture
- Claims less territory
- Cedes initiative to opponent
- Can be surrounded and starved
```

**Optimal Play**: Likely a hybrid—expand aggressively in one direction while maintaining a consolidated core. The "expanding cluster" approach.

### Defensive Formations

```
WEAK (Linear):          STRONG (Cluster):

○ ○ ○ ○ ○              ○ ○ ○
                        ○ ○ ○
Each stone has          ○ ○ ○
only 1-2 friends
Easy to isolate         Center stones have
and attack              4 adjacent allies
                        Very hard to crack
```

**The Line Problem**: Linear expansion is efficient for claiming territory but creates weak points. Each stone in a line has at most 2 friendly neighbors, meaning you can never achieve more than 2-adjacency defense.

**The Cluster Advantage**: A 3x3 cluster has a center stone with 4 friendly neighbors. To attack any edge stone, enemy needs to approach from outside, where they'll also be adjacent to multiple defenders for counter-attack.

### Offensive Positioning

**The Fork**: Place a stone that threatens to attack two different enemy territories next turn. Opponent can only defend one.

```
Before:           After placing ○ at X:

● . .             ● . .
. . ●       →     . ○ ●
. . .             . . .

Now ○ threatens both ● stones with 50% attacks.
Opponent must choose which to reinforce.
```

**The Surround**: Methodically build adjacency to a key enemy stone before attacking.

**The Cut**: Attack the stone that connects two enemy groups. Success splits their position.

### Risk Assessment Framework

When considering an attack, evaluate:

1. **Base probability**: How many adjacent stones do I have?
2. **Strategic value**: Is this target critical to enemy position?
3. **Opportunity cost**: What placement am I giving up?
4. **Counter-attack exposure**: If I fail, am I now vulnerable?
5. **Tempo**: Does attacking now prevent enemy's plans?

**Heuristic**: Attack when `P(success) × Value(target) > Value(best placement)`

---

## 4. AI TRACTABILITY ANALYSIS

### Action Space

On a 7×7 board with `E` empty squares and `O` opponent stones:
- PLACE actions: `E` options (place on any empty)
- ATTACK actions: At most `O` options (but filtered by adjacency requirement)

**Maximum branching factor**: 49 (all squares relevant)
**Typical branching factor**: 15-25 (mid-game)

This is very manageable—much simpler than Chess (~35) or Go (~250).

### State Representation

```python
state = {
    'board': np.array((7, 7)),  # 0=empty, 1=player1, 2=player2
    'current_player': int,       # 1 or 2
    'turn_number': int,          # 1 to 40
}
```

Compact representation: 49 cells × 2 bits = 98 bits for board state.

### Position Evaluation

**Features for heuristic evaluation**:

| Feature | Weight | Rationale |
|---------|--------|-----------|
| Territory count | High | Direct victory condition |
| Center control | Medium | Tie-breaker, strategic hub |
| Average adjacency | Medium | Defensive strength |
| Frontier exposure | Negative | Vulnerable to attack |
| Connectivity | Medium | Resilience to cuts |
| Attack opportunities | Low-Medium | Potential for gains |

**Simple Evaluation Function**:
```
V(s) = (my_stones - opp_stones)
     + 0.3 × (my_center - opp_center)
     + 0.2 × (my_avg_adjacency - opp_avg_adjacency)
     - 0.1 × my_frontier_exposure
```

### Algorithm Recommendations

**1. Expectimax** (for attack decisions):
```
For ATTACK actions:
  E[value] = P(success) × V(success_state)
           + P(fail) × V(current_state)

For PLACE actions:
  value = V(new_state)  # Deterministic
```

**2. Monte Carlo Tree Search (MCTS)**:
- Natural handling of probabilistic outcomes
- No heuristic needed (simulate to terminal states)
- Proven effective for games with similar structure

**3. Minimax with Chance Nodes**:
- Treat attacks as chance nodes
- Alpha-beta still applicable with modifications

### Training Approach

Self-play reinforcement learning would work well:
1. Simple state space
2. Clear reward signal (win/loss, or territory differential)
3. Probabilistic elements add exploration naturally
4. Games are short (~20 moves per player)

---

## 5. POTENTIAL ISSUES

### Issue 1: Stalemate Conditions

**Concern**: Both players build impenetrable clusters and refuse to attack.

**Analysis**:
- The board is finite (49 squares)
- If both cluster, they'll eventually border each other
- The turn limit (40 turns) forces a decision
- Actually, clustering is suboptimal because it concedes territory

**Mitigation**: Turn limit naturally prevents infinite games. The player with more territory wins, so pure turtling loses to moderate expansion.

**Verdict**: ✅ Not a significant problem

### Issue 2: First-Mover Advantage

**Concern**: Player 1 always gets the first territory, the first attack setup, etc.

**Analysis**:
- In territory games, first move is typically advantageous
- Center square is particularly valuable (access to all regions)

**Mitigations**:
1. ✅ Tie-breaker goes to Player 2
2. 🔧 **Pie Rule**: After Player 1's first move, Player 2 can choose to swap colors
3. 🔧 **Komi**: Player 2 starts with a "virtual" 0.5 territory lead

**Recommendation**: Implement the Pie Rule for competitive play. The current tie-breaker is insufficient for strict balance.

### Issue 3: Turtle Strategies

**Concern**: Building a single massive cluster is unbeatable.

**Analysis**:
- A 5×5 cluster = 25 territories
- Opponent expanding thinly can claim 24 territories elsewhere
- BUT: the clustered player loses on territory count
- To crack a cluster, you need to surround it (possible with more stones)

**Key Insight**: Turtling is a LOSING strategy in a turn-limited game. You surrender map control while building a strong-but-small fortress.

**Verdict**: ✅ Game naturally punishes over-turtling

### Issue 4: Dominant Strategies

**Concern**: Is there an "always correct" opening or strategy?

**Analysis**:
- Center opening seems strong (maximizes future adjacency options)
- But it's predictable—opponent can respond to deny center control
- Corner openings are safe but limited
- Edge openings offer expansion lanes

**Likely Meta**: Balanced openings that secure 2-3 key positions without overcommitting. The probabilistic attacks prevent deterministic "solved" lines.

**Verdict**: ⚠️ Needs playtesting. Center control may be too important.

### Issue 5: Snowball Effect

**Concern**: Once ahead, player stays ahead forever.

**Analysis**:
- More territory = more attack opportunities
- BUT: more territory = more frontier to defend
- Concentrated forces beat spread-out forces
- A well-timed attack can flip momentum

**Rubber-banding**: The attack mechanic provides comeback potential. Even a trailing player can flip critical stones with lucky rolls or superior positioning.

**Verdict**: ✅ Comeback mechanics exist naturally

### Issue 6: Analysis Paralysis

**Concern**: Too many options each turn.

**Analysis**:
- At most 49 options per turn
- Most are obviously suboptimal (place in corner when center open)
- Attack decisions require probability calculation
- Players can develop heuristics quickly

**Verdict**: ✅ Acceptable for the depth provided

---

## 6. RATINGS

### Elegance: 8/10

**Strengths**:
- "One action, two choices" is beautifully simple
- Rules fit on an index card
- Probability mechanic (50% per adjacent) is intuitive
- No special cases or exceptions needed

**Weaknesses**:
- Turn limit feels bolted on (not emergent)
- Tie-breaker rules add complexity
- No thematic wrapper (abstract game)

### Strategic Depth: 7/10

**Strengths**:
- Genuine positional strategy (clusters, forks, cuts)
- Risk/reward calculations matter
- Multiple viable playstyles
- Decisions feel meaningful

**Weaknesses**:
- Relatively simple compared to Go or Chess
- May be "solvable" for small board sizes
- Limited combo potential (no chain reactions)
- Depth may plateau after moderate skill

### AI-Friendliness: 9/10

**Strengths**:
- Small, well-defined action space
- Simple state representation
- Probability is explicit (not hidden)
- Short games enable rapid training
- Clear evaluation metrics

**Weaknesses**:
- Randomness adds variance to evaluation
- May need many games to get statistically valid comparisons

---

## 7. VARIANT IDEAS

### 7a. Momentum Variant
After a successful attack, you may immediately attack again (still requires adjacency). Creates dramatic chain reactions but may swing games too wildly.

### 7b. Fog of War Variant
Opponent's stones are hidden until you place adjacent to them. Adds bluffing and scouting dimensions.

### 7c. Asymmetric Powers
- **Attacker Faction**: Attacks at 60% per adjacent instead of 50%
- **Defender Faction**: Each stone counts as 1.5 for territory scoring

### 7d. Hex Grid
Play on hexagonal grid (6 adjacencies per cell). Higher maximum attack power, different cluster dynamics.

---

## 8. SUMMARY

**PLACE OR ATTACK** is a elegant strategic game built on a single, meaningful decision per turn. The tension between guaranteed placement and probabilistic attack creates interesting choices throughout.

**Recommended for**:
- Quick strategic play (15-20 minutes)
- AI research (tractable but not trivial)
- Introduction to probabilistic games

**Development Priority**:
1. Implement basic version for playtesting
2. Determine if Pie Rule is necessary for balance
3. Test if 7×7 is optimal or if 8×8 provides better play
4. Explore whether attack success rate should be tuned (40%? 60%?)

---

*Design analysis complete. Ready for prototyping.*
