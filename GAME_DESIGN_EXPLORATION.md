# Game Design Exploration - Elegant Simplicity Edition

This document explores new game mechanics built around the principles of **emergent elegance from simple rules**, inspired by Go's depth-to-complexity ratio.

---

## Design Philosophy

**Core Principles (Inferred from Your Preferences):**

1. **One stone per territory** - Clean state representation
2. **One decision per turn** - Reduced cognitive load, increased decision quality
3. **Simple win conditions** - Easy to understand, hard to master
4. **Probability at resolution moments** - Tension without mid-game chaos
5. **AI tractability** - Minimax/expectimax friendly, manageable branching factor
6. **Starting simple** - Complexity can be added later through variants

**What We're Avoiding:**
- Multiple interacting systems
- Excessive tracking overhead
- Many decision types per turn
- Designed complexity over emergent depth

---

## Game Concepts Overview

### Primary Explorations (Your Ideas)

| Game | Core Mechanic | Randomness | Elegance | Depth | AI |
|------|---------------|------------|----------|-------|-----|
| **Attention + Influence** | Place stones, areas claim probabilistically | Per-area resolution | 7/10 | 8/10 | 7/10 |
| **A+I Rolling Score** | Same, but cumulative scoring each turn | None (deterministic) | 7/10 | 8/10 | 7/10 |
| **A+I Hex Variation** | Triangular regions, 33% per corner | Per-triangle resolution | 9/10 | 9/10 | 8/10 |
| **Place or Attack** | Place OR attack, 50% per adjacent | Per-attack | 8/10 | 7/10 | 9/10 |
| **P/A Triangular Grid** | Same, but 3-neighbor maximum | Per-attack (capped) | 8/10 | 8/10 | 6/10 |

### Additional Concepts (Based on Your Preferences)

| Game | Core Mechanic | Randomness | Elegance | Depth | AI |
|------|---------------|------------|----------|-------|-----|
| **Watershed** | Voronoi proximity claims territory | None | 9/10 | 7/10 | 10/10 |
| **Creep** | Place 3 seeds, automatic spreading | None | 8/10 | 6/10 | 10/10 |
| **Fault Lines** | Groups survive based on size probability | End-game only | 8/10 | 8/10 | 9/10 |

---

## GAME 1: ATTENTION + INFLUENCE (Base Grid)

### Concept
Place stones to corner areas; areas claim probabilistically based on corner presence.

### Complete Rules
- **Board**: 5x5 intersections (creating 4x4 = 16 claimable squares)
- **Turn**: Both players simultaneously select one empty intersection; reveal; place (collisions = both lose turn)
- **Resolution**: After placement, each unclaimed square is contested:
  - 25% claim chance per corner stone you own
  - Roll once per square to determine outcome (yours / opponent's / unclaimed)
- **Victory**: Most squares claimed when board fills

### Strategic Texture
- **Collision Gambit**: High-value spots create chicken-game dynamics
- **Probabilistic Commitment**: Lock in 100% squares (safe, slow) or spread thin for more chances?
- **Positional Multipliers**: Interior intersections touch 4 squares; corners touch 1
- **Tempo vs Territory**: Guaranteed claims vs maximum exposure

### AI Analysis
- **State space**: ~10^12-10^14 reachable positions
- **Branching**: 25 choices per player, but simultaneous creates 625 joint outcomes (prunable to ~50-100)
- **Best approach**: MCTS or expectimax; simultaneous moves require game-theoretic reasoning

### Ratings: Elegance 7/10 | Depth 8/10 | AI 7/10

---

## GAME 2: ATTENTION + INFLUENCE - Rolling Score

### Variation
Areas resolve EVERY turn; successful claims add to cumulative score. Same area can score for different players on different turns.

### Key Difference
Transforms the game from "capture territory" to "maximize yield." More like an economic engine than territorial conquest.

### Complete Scoring
- 4 corners same color: +4 points
- 3 corners same color: +2 points
- 2-2 split: +1 point each
- 1 corner: 0 points

### Strategic Texture
- **Marathon feel**: Every turn matters equally; no "locked" regions
- **Compound investment**: Central stones generate returns each turn
- **Comeback potential**: High - no locked territory means trailing player can always contest
- **Denial calculus**: Worth blocking opponent's +3 even if you gain +0

### AI Analysis
- **Easier**: Deterministic scoring, clear objective
- **Harder**: Requires multi-turn horizon thinking; evaluation must capture "income streams"

### Ratings: Elegance 7/10 | Depth 8/10 | AI 7/10

---

## GAME 3: ATTENTION + INFLUENCE - Hex Variation

### Design Choice
**Stones on hex vertices; triangular regions as claimable areas**

This creates the most elegant adaptation:
- Each triangle has exactly 3 corners = natural 33%/33%/33% probability split
- Board: Radius-3 hexagon (24 vertices, 42 triangles)

### Why This Works
| Configuration | Influence |
|---------------|-----------|
| 3 same corners | 100% claimed |
| 2 same + 1 other | 67% vs 33% |
| 1 each | 33% each |

The elegance: Committing 2 of 3 corners (67%) feels similar to sending 2 stones in the base (75%) - comparable risk/reward.

### Strategic Texture
- **Tighter decisions**: 3 neighbors vs 4 means each move is more consequential
- **Gradient control**: Territories can be "67% yours" - creates persistent tension
- **Natural patterns**: Central vertex touches 6 triangles (valuable); edges easier to defend
- **Triangle chains**: Control all top vertices to claim entire row; breaking ONE breaks the chain

### AI Analysis
- **40% smaller action space** (3 directions vs 4)
- **50% more symmetry** (12 vs 8) for state canonicalization
- **Continuous influence** = better for neural network gradients
- **Verdict**: MORE AI-friendly than grid version

### Ratings: Elegance 9/10 | Depth 9/10 | AI 8/10

**This is the recommended version of Attention + Influence.**

---

## GAME 4: PLACE OR ATTACK (Base Grid)

### Concept
Each turn: Place a stone on empty space OR attack an enemy territory.

### Complete Rules
- **Board**: 7x7 grid
- **Turn**: Choose ONE action:
  - **PLACE**: Put stone on any empty territory (guaranteed claim)
  - **ATTACK**: Target enemy territory; each adjacent friendly stone has 50% chance to flip it
- **Adjacency**: Orthogonal only (4 directions)
- **Victory**: Domination (opponent at 0) or most territory after 40 turns

### Attack Probability
| Adjacent | Success |
|----------|---------|
| 1 | 50.0% |
| 2 | 75.0% |
| 3 | 87.5% |
| 4 | 93.75% |

**Critical mass**: 3 adjacent stones makes attacks near-certain.

### Strategic Texture
- **Place/Attack Tension**: PLACE = guaranteed +1; ATTACK = probabilistic flip
- **Front Line Evolution**: Land grab → consolidation → active combat
- **Defensive Formations**: Lines are weak (max 2 neighbors); clusters are strong (center has 4)
- **Offensive Positioning**: Forks (threaten two targets), surrounds (build adjacency), cuts (split enemy)

### AI Analysis
- **Action space**: At most 49 options per turn (typically 15-25)
- **State**: Compact (98 bits for full board)
- **Evaluation**: Territory + center control + average adjacency - frontier exposure
- **Best approach**: Expectimax handles probabilistic attacks naturally

### Ratings: Elegance 8/10 | Depth 7/10 | AI 9/10

---

## GAME 5: PLACE OR ATTACK - Triangular Grid

### Design Choice
**37-cell hexagonal boundary (3 rings from center)**

Key property: Each triangle has exactly 3 neighbors (edge-sharing).

### The 3-Neighbor Difference

| Adjacent | Triangular | Square |
|----------|------------|--------|
| Max attack success | 87.5% | 93.75% |
| Max attack failure | 12.5% | 6.25% |

**Critical insight**: Even "overwhelming force" still fails 1-in-8 times. Over 20 turns with 10 attacks, expect ~1.25 failures (vs 0.6 on square grid). Every attack is a meaningful gamble.

### Strategic Texture
- **Attack psychology**: Scarier to attempt - "I've been burned before"
- **Defensive positioning**: Easier (fewer attack vectors, natural chokepoints)
- **Front lines**: Inherently jagged (straight lines are geometrically impossible)
- **Emergent formations**: Triangle Defense (mutual protection), Spearhead (V-shape advance), Phalanx (resilient wall)

### Unique Properties
1. **Intrinsic uncertainty**: Certainty is never achievable
2. **Directional geometry**: Triangles have natural "facing" without explicit rules
3. **Forced imperfection**: Always a weak point to exploit
4. **Elegant economy**: The number 3 governs both maximum attack force AND minimum stable defense

### Ratings: Elegance 8/10 | Depth 8/10 | AI 6/10

**Worth prototyping for novel experience; may be too random for competitive play.**

---

## GAME 6: WATERSHED (Voronoi Control)

### Concept
Place stones; territory belongs to nearest stone owner. Pure geometric elegance.

### Complete Rules
- **Board**: 7x7 grid
- **Turn**: Place ONE stone on any empty intersection
- **Territory**: Each empty space belongs to player with nearest stone (Manhattan distance); ties = neutral
- **Victory**: Most territory when board fills

### Strategic Texture
- **Local vs Global**: Lone stones claim large areas but are vulnerable to midpoint insertions
- **Geometric intuition**: Must visualize shifting influence regions
- **Blocking vs Claiming**: Expand your territory or disrupt opponent's?

### AI Analysis
- **Fully deterministic** - no randomness
- **Perfect information**
- **Simple evaluation**: Just count controlled spaces
- **Well-suited for alpha-beta** with transposition tables

### Ratings: Elegance 9/10 | Depth 7/10 | AI 10/10

**Purest design. Closest to Go's aesthetic of simple rules, deep emergence.**

---

## GAME 7: CREEP (Seed and Spread)

### Concept
Place 3 stones each, then watch them spread automatically. Your seeds determine everything.

### Complete Rules
- **Phase 1**: Each player places exactly 3 stones (alternating)
- **Phase 2**: Automatic spreading - each stone grows to one adjacent empty space per turn
- **Collisions**: Different players' spreading into same space = space stays empty (mutual block)
- **Victory**: Most stones when spreading stops

### Strategic Texture
- **3 decisions determine everything**: Placement is critical
- **Deterministic chaos**: Simple rules, hard to predict cascades
- **Resource scarcity**: No recovery from bad opening

### AI Analysis
- **Only 6 decisions total** (3 per player)
- **Resolution is pure simulation**
- **Can enumerate entire decision space**

### Ratings: Elegance 8/10 | Depth 6/10 | AI 10/10

**Novel mechanics, minimal decisions. Great for AI training.**

---

## GAME 8: FAULT LINES (Probabilistic Stability)

### Concept
Place stones to form groups; at end, each group is tested - larger groups survive more reliably.

### Complete Rules
- **Turn**: Place ONE stone on empty space
- **Groups**: Connected same-color stones
- **Resolution**: At game end, each group rolls d6; survives if roll <= group size
- **Victory**: Most surviving stones

### Survival Probability
| Size | Survival |
|------|----------|
| 1 | 16.7% |
| 2 | 33.3% |
| 3 | 50.0% |
| 4 | 66.7% |
| 5 | 83.3% |
| 6+ | 100% |

### Strategic Texture
- **Spreading vs Connecting**: Small groups claim more but collapse; large groups are safe but slow
- **The 6-threshold**: Jump from 5 to 6 stones (83% to 100%) is critical
- **Connection priority**: Rush to form stable 6+ groups
- **Splitter moves**: Prevent opponent groups from connecting
- **Risk portfolio**: Balance one large safe group vs multiple risky small groups

### AI Analysis
- **Expectimax-friendly**: Probability only at end
- **Clear evaluation**: sum of (group_size * survival_probability)
- **No mid-game randomness**: Cleaner search trees

### Ratings: Elegance 8/10 | Depth 8/10 | AI 9/10

**Most interesting risk/reward decisions. Connection tactics are deeply engaging.**

---

## Comparative Analysis

### By Play Style

| If you want... | Choose... |
|----------------|-----------|
| Pure geometric elegance | **Watershed** |
| Rich positional play with probability | **Attention+Influence Hex** |
| Simple decisions, dramatic attacks | **Place or Attack** |
| Novel spreading mechanics | **Creep** |
| Connection tactics with risk management | **Fault Lines** |
| Economic engine feeling | **A+I Rolling Score** |
| Maximum drama from attack uncertainty | **P/A Triangular Grid** |

### By AI Research Goals

| Priority | Recommendation |
|----------|----------------|
| Smallest search space | Creep (6 decisions total) |
| Fully deterministic | Watershed |
| Expectimax practice | Fault Lines or Place or Attack |
| Novel geometry | A+I Hex or P/A Triangular |
| Fastest to implement | Watershed (< 1 day) |

### By Elegance

1. **Watershed** (9/10) - One rule determines everything
2. **A+I Hex** (9/10) - Beautiful 3-corner = 33% mapping
3. **Place or Attack** (8/10) - "One action, two choices"
4. **Fault Lines** (8/10) - Connection + end-game probability
5. **Creep** (8/10) - Minimal decisions, emergent complexity

---

## Recommendations

### For Immediate Prototyping

**Tier 1 (Most Promising):**
1. **Attention + Influence (Hex)** - Best balance of elegance, depth, and AI-friendliness
2. **Place or Attack** - Simplest to implement, strong strategic core
3. **Fault Lines** - Most interesting human decisions

**Tier 2 (Worth Exploring):**
4. **Watershed** - Purest design, perfect for AI baselines
5. **A+I Rolling Score** - Different feel, good variant

**Tier 3 (Experimental):**
6. **P/A Triangular** - Novel but may be too random
7. **Creep** - Interesting but shallow (only 6 decisions)

### Implementation Priority

1. **Place or Attack** (1-2 days) - Simplest core, immediate playability
2. **Watershed** (< 1 day) - Deterministic baseline for AI comparison
3. **A+I Hex** (2-3 days) - Best overall design, worth the geometry complexity
4. **Fault Lines** (2 days) - Needs group detection + end-game resolution

---

## Summary

These eight game concepts all share your core values:
- **One stone per place**
- **One primary decision per turn**
- **Simple, clear rules**
- **Emergent depth from constraints**
- **AI-tractable state spaces**

The key insight across all designs: **Constraints create strategy.** By limiting options (single stone, single action, simple adjacency), we create meaningful choices where every decision matters.

The best games here don't need complex systems to be interesting - they need one elegant rule that reveals depth through play.

---

*Design exploration complete. Ready for prototyping and playtesting.*
