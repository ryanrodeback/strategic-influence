# Three New Game Concepts

Based on the user's preferences for Go-like elegance, these designs emphasize:
- One stone per place maximum
- One primary decision per turn
- Simple win conditions
- AI tractability (minimax/expectimax friendly)
- Probability at resolution moments only
- Emergent depth from simple rules

---

## GAME 1: WATERSHED

### One-Line Pitch
**Place stones to claim territory through proximity; each empty space belongs to whoever has a closer stone.**

### Core Rules

**Setup:**
- 7x7 board (or configurable), all empty
- Two players: Black and White
- Black plays first

**Turn Structure:**
- On your turn, place ONE stone on any empty intersection
- Stones are permanent once placed (never removed)
- Alternate until the board fills OR both players pass consecutively

**Territory Determination (Voronoi):**
- Each empty intersection belongs to the player with the NEAREST stone
- Distance = Manhattan distance (|row1-row2| + |col1-col2|)
- Ties = neutral (no one controls)
- Your own stones count as +1 territory for you

**Win Condition:**
- When the game ends, count controlled intersections
- Player with more territory wins
- Ties are draws

**Complete Rules Summary:**
```
1. Place one stone on empty space
2. Each space belongs to nearest stone's owner (Manhattan distance)
3. Ties are neutral
4. Most territory wins
```

### What Makes It Interesting

The key tension is **local vs. global efficiency**:
- A single stone in empty space claims a large area
- But spreading thin leaves you vulnerable to opponent insertions
- Placing near opponent stones creates contested (neutral) zones
- The optimal distance between your own stones is non-obvious

**Geometric Intuition Required:**
Players must visualize influence regions that shift with each placement. A stone placed at the "midpoint" between two opponent stones can flip large territories.

**Blocking vs. Claiming:**
Do you expand your own territory or disrupt your opponent's stronghold?

### Emergent Strategies

1. **Corner Opening:** Corners claim triangular regions efficiently (3 sides bounded by board edge)

2. **Midpoint Insertions:** Placing exactly between two opponent stones creates maximum disruption

3. **Defensive Clusters:** Placing stones near each other creates "anchor points" that resist insertions

4. **Territory Estimation:** Expert players will develop intuition for which placements yield net territory gains

5. **Endgame Optimization:** As the board fills, precise calculation of neutral boundaries becomes crucial

6. **Tempo vs. Territory:** Sometimes playing in contested zones to force responses is better than pure expansion

### AI Analysis

**State Space:**
- 49 intersections on 7x7
- Each can be: empty, black, white
- Upper bound: 3^49 states (practical space much smaller due to turn alternation)
- Typical games: ~40 stones placed

**Branching Factor:**
- Starts at 49, decreases by 1 each turn
- Average: ~25 per turn
- Very manageable for deep search

**Evaluation Heuristics:**
1. **Territory Count:** Direct count of controlled + tied spaces (weighted 0.5 for ties)
2. **Influence Maps:** Precompute nearest-stone distances for fast evaluation
3. **Threat Detection:** Identify "insertion points" where opponent can flip territory
4. **Efficiency Score:** Territory per stone (diminishing returns detection)

**AI-Friendliness:**
- Fully deterministic (no randomness)
- Perfect information
- Simple evaluation function
- Board state is compact (49 cells)
- Well-suited for alpha-beta pruning with transposition tables

**Minimax Depth Estimates:**
- Depth 4: trivial (<1 second)
- Depth 6: easy (<5 seconds)
- Depth 8+: feasible with good move ordering

### Ratings

| Aspect | Score | Notes |
|--------|-------|-------|
| **Elegance** | 9/10 | Pure Voronoi mechanics; one rule determines everything |
| **Strategic Depth** | 7/10 | Rich positioning strategy; may have solvable endgames |
| **AI-Friendliness** | 10/10 | Deterministic, clear evaluation, moderate branching |

---

## GAME 2: CREEP

### One-Line Pitch
**Place stones that spread automatically each turn; control territory by having the largest connected group when spreading stops.**

### Core Rules

**Setup:**
- 7x7 board, all empty
- Two players: Black and White
- Each player starts with 3 "placement tokens" (can place 3 stones total)

**Turn Structure - Two Phases:**

**Phase 1: PLACEMENT (First ~6 turns)**
- Players alternate placing ONE stone on any empty space
- Each player places exactly 3 stones total
- After all 6 stones are placed, Phase 2 begins

**Phase 2: SPREADING (Automatic)**
- No player decisions - spreading resolves automatically
- Each turn, every stone "spreads" to ONE adjacent empty space
- Spreading priority: orthogonal neighbors, clockwise from north
- If all neighbors are occupied, that stone doesn't spread
- Continue until no stone can spread (board stable)

**Collision Rules (when two stones try to spread to same space):**
- If same player's stones: one claims it (no conflict)
- If different players' stones: the space stays EMPTY (mutual block)

**Win Condition:**
- After spreading completes, count each player's stones
- Player with more stones wins

**Complete Rules Summary:**
```
1. Place 3 stones each (alternating)
2. Stones spread automatically to one adjacent empty space per turn
3. Collisions between opponents = empty space
4. Most stones when spreading stops wins
```

### What Makes It Interesting

The key tension is **seeding position for optimal growth**:
- Your 3 initial placements determine everything
- Spreading is deterministic, so you can simulate outcomes
- But opponent's placements create blocking patterns
- The "collision = empty" rule creates defensive barriers

**Deterministic Chaos:**
Despite simple rules, predicting final positions 10+ spreads ahead is cognitively challenging. Small initial differences cascade dramatically.

**Resource Scarcity:**
Only 3 placements means every choice is critical. There's no recovery from a bad opening.

### Emergent Strategies

1. **Corridor Control:** Place stones to spread into the longest unblocked corridors

2. **Blocking Placements:** Put a stone where it will collide with opponent spreading, creating dead zones

3. **Corner Traps:** Corner placements are bounded but defensible

4. **Timing Attacks:** Place stones that will collide with opponent mid-spread, wasting their growth

5. **Maximum Separation:** Starting stones far apart may reach more total territory

6. **Simulation Depth:** Expert players will mentally simulate 5-10 spread cycles before placing

### AI Analysis

**State Space:**
- Phase 1: Choose 3 positions from 49 per player = C(49,3) * C(46,3) = very manageable
- Phase 2: Deterministic simulation, no search needed

**Branching Factor:**
- Phase 1 only: ~49 * 48 * 47 / 6 = ~17,000 possible opening configurations per player
- But turn-by-turn: 49, 48, 47, 46, 45, 44 for 6 placements
- After Phase 1: zero (deterministic)

**Evaluation Heuristics:**
1. **Simulate Forward:** Just run the spreading simulation to completion
2. **Corridor Length:** Count maximum unblocked spread potential
3. **Collision Prediction:** Identify inevitable collision points
4. **Board Coverage:** Estimate final stone count from starting positions

**AI-Friendliness:**
- Phase 1 is searchable (limited branching)
- Phase 2 is deterministic (just simulate)
- Can evaluate any state by simulating to completion
- Perfect for minimax with full lookahead

**Minimax Depth Estimates:**
- Can search entire game tree with alpha-beta
- Phase 1 fully enumerable
- Evaluation = run simulation = O(board_size) per leaf

### Ratings

| Aspect | Score | Notes |
|--------|-------|-------|
| **Elegance** | 8/10 | Simple spreading rule; placement-only decisions |
| **Strategic Depth** | 6/10 | Limited decisions (only 3 per player); deep reading required |
| **AI-Friendliness** | 10/10 | Tiny decision space; deterministic resolution |

---

## GAME 3: FAULT LINES

### One-Line Pitch
**Place stones to form groups; at game end, each group's survival is tested with probability based on size - larger groups are more stable.**

### Core Rules

**Setup:**
- 7x7 board, all empty
- Two players: Black and White
- Black plays first

**Turn Structure:**
- On your turn, place ONE stone on any empty intersection
- Stones are permanent
- Game ends when board fills OR both players pass consecutively

**Groups:**
- Orthogonally connected stones of the same color form a "group"
- Single stones are groups of size 1

**Resolution Phase (End of Game):**
Each group is tested for "stability":
- Roll one die per group (not per stone)
- Group survives if: roll <= group_size
- Die has 6 sides (or adjust for balance)

**Survival Probabilities:**
| Group Size | Survival Chance |
|------------|-----------------|
| 1 stone | 16.7% (1/6) |
| 2 stones | 33.3% (2/6) |
| 3 stones | 50% (3/6) |
| 4 stones | 66.7% (4/6) |
| 5 stones | 83.3% (5/6) |
| 6+ stones | 100% (guaranteed) |

**Win Condition:**
- After stability resolution, count surviving stones
- Player with more surviving stones wins

**Complete Rules Summary:**
```
1. Alternate placing one stone on empty space
2. Connected same-color stones form groups
3. At game end, each group rolls: survives if roll <= size
4. Most surviving stones wins
```

### What Makes It Interesting

The key tension is **spreading vs. connecting**:
- Spreading claims more board space initially
- But small groups have high collapse probability
- Connecting stones into larger groups is safer but slower
- The 6+ threshold creates a critical "stability goal"

**Risk Management:**
Every placement is a choice between:
- Extending an existing group (safer)
- Starting a new group (riskier but more territory)
- Disrupting opponent connections (offensive)

**Probability at Resolution Only:**
During play, the game is fully deterministic. All randomness happens at the end, which enables deep planning while maintaining tension.

**Expectimax-Friendly:**
AI can compute expected surviving stones for any position.

### Emergent Strategies

1. **Connection Priority:** Rush to form 6+ stone groups for guaranteed survival

2. **Splitter Moves:** Place stones that prevent opponent groups from connecting

3. **Risk Portfolio:** Balance between one large safe group vs. multiple risky small groups

4. **Endgame Calculation:** Compute expected value of different board states

5. **Opponent Fragmentation:** Force opponent into many small groups

6. **Sacrifice Plays:** Accept low-survival stones to block critical connections

7. **Threshold Awareness:** The jump from 5 to 6 stones is huge (83% to 100%)

### AI Analysis

**State Space:**
- Same as Watershed: 3^49 upper bound
- Typical games: ~40-49 stones placed

**Branching Factor:**
- Starts at 49, decreases by 1
- Average: ~25

**Evaluation Heuristics:**
1. **Expected Survival:** For each group, size * (min(size,6)/6) stones expected
2. **Connection Potential:** Groups one move from merging
3. **Opponent Fragmentation:** Count of opponent groups (more = better for you)
4. **Guaranteed Territory:** Stones in 6+ groups

**AI-Friendliness:**
- Expectimax handles the probabilistic resolution naturally
- State is compact and easy to evaluate
- Clear expected-value calculations
- No mid-game randomness (cleaner search trees)

**Minimax/Expectimax Depth Estimates:**
- Depth 4-6: easy
- Can use expected value as deterministic proxy for deeper search
- Monte Carlo rollouts straightforward

### Ratings

| Aspect | Score | Notes |
|--------|-------|-------|
| **Elegance** | 8/10 | Connection + end-game probability is clean |
| **Strategic Depth** | 8/10 | Risk/reward balancing; connection tactics |
| **AI-Friendliness** | 9/10 | Expectimax-perfect; clear evaluation |

---

## Comparison Matrix

| Aspect | WATERSHED | CREEP | FAULT LINES |
|--------|-----------|-------|-------------|
| **Core Mechanic** | Voronoi proximity | Automatic spreading | Group survival probability |
| **Decisions/Turn** | 1 (place) | 1 (place, Phase 1 only) | 1 (place) |
| **Stones/Space** | 1 max | 1 max | 1 max |
| **Randomness** | None | None | End-game only |
| **Captures** | No | No (collisions) | No (groups collapse) |
| **Win Condition** | Most territory | Most stones | Most surviving stones |
| **AI Method** | Minimax | Minimax + simulation | Expectimax |
| **Elegance** | 9/10 | 8/10 | 8/10 |
| **Depth** | 7/10 | 6/10 | 8/10 |
| **AI-Friendly** | 10/10 | 10/10 | 9/10 |

---

## Recommendation

**For Pure Elegance:** WATERSHED
- Closest to Go's aesthetic of simple rules, deep emergence
- Fully deterministic
- Beautiful geometric reasoning

**For Novel Mechanics:** CREEP
- Unique "plant seeds, watch them grow" feel
- Minimal decisions with maximum consequence
- Great for AI training (tiny search space)

**For Strategic Depth:** FAULT LINES
- Most interesting risk/reward decisions
- Connection tactics are deeply engaging
- Probability adds tension without mid-game chaos

---

## Implementation Priority

All three games share:
- Simple board representation (same as existing code)
- One-stone-per-space constraint
- Minimal state tracking

**Easiest to Implement:** WATERSHED (< 1 day)
- Territory calculation is just distance comparison
- No special resolution phase

**Medium:** FAULT LINES (1-2 days)
- Needs group detection (flood fill)
- End-game probability resolution

**Most Work:** CREEP (2-3 days)
- Spreading simulation logic
- Collision detection
- Two-phase game structure

---

## Design Philosophy Notes

These games follow the "Elegant Constraint" principle:
1. **Constraint creates strategy** - One stone per space forces careful placement
2. **One decision per turn** - Reduces cognitive overhead, increases depth per decision
3. **Probability at resolution** - Tension without mid-game chaos
4. **Emergent complexity** - Simple rules, complex play

Each game asks one core question:
- **WATERSHED:** "Where is the most valuable empty space?"
- **CREEP:** "Where should I seed for maximum growth?"
- **FAULT LINES:** "How do I balance risk and connection?"

These questions are simple to understand but deep to master.
