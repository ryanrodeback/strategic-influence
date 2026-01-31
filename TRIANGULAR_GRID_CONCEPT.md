# PLACE OR ATTACK - Triangular Grid Variation
## Game Concept Sketch

---

## Executive Summary

This document explores adapting Strategic Influence to a **triangular tessellation grid**, where each cell is a triangle with exactly **3 edge-sharing neighbors**. This constraint fundamentally alters attack dynamics, defensive strategy, and board control compared to the square grid's 4-neighbor system.

**Key Finding:** The triangular grid creates a more **volatile, chess-like** game where attacks are riskier but territorial defense is structurally easier. The geometry naturally creates "forward" and "backward" facing triangles, enabling directional strategy absent from square grids.

---

## 1. Proposed Board Design

### 1.1 Recommended Shape: Hexagonal Boundary

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

**Why Hexagonal:**
- **Symmetry:** Both players have equal positional opportunities
- **No corners:** Eliminates corner-camping strategies (triangular corners have only 1-2 neighbors)
- **Natural aesthetic:** Hexagonal boundaries feel complete and elegant
- **Historical precedent:** Hex wargames demonstrate this works well for strategy

### 1.2 Alternative Shapes Considered

| Shape | Pros | Cons | Verdict |
|-------|------|------|---------|
| **Hexagonal** | Symmetrical, no weak corners, elegant | Slightly harder to render | **RECOMMENDED** |
| **Large Triangle** | Thematic consistency | Asymmetric starting positions | Interesting variant |
| **Rectangle Approximation** | Easy to render, familiar | Jagged edges, awkward corners | Avoid |
| **Diamond (Rhombus)** | Two-axis symmetry | Still has weak corners | Secondary option |

### 1.3 Optimal Size Analysis

For triangular grids, count **cells** not rows:

| Total Cells | Hex Rings | Square Grid Equivalent | Game Length Estimate | Verdict |
|-------------|-----------|------------------------|----------------------|---------|
| 19 | 2 rings | 4x4 (16) | Too short | Too small |
| 37 | 3 rings | 6x6 (36) | 15-20 turns | **Ideal for core game** |
| 61 | 4 rings | 8x8 (64) | 25-35 turns | Extended variant |
| 91 | 5 rings | 10x10 (100) | 40+ turns | Tournament format |

**Recommendation: 37-cell hexagonal board (3 rings from center)**

This provides:
- 12 edge cells (exposed, contested)
- 18 mid-ring cells (strategically valuable)
- 6 inner cells + 1 center (core territory)
- Enough space for maneuvering without overwhelming complexity

---

## 2. Core Mechanics (Adapted)

### 2.1 Base Rules (Preserved)

- **One stone per territory** (or growth system if using full Strategic Influence rules)
- **Each turn:** PLACE on empty OR ATTACK enemy territory
- **Attack:** Each adjacent friendly stone has **50% independent chance** to flip target

### 2.2 Key Mechanical Difference: 3-Neighbor Maximum

**Attack Probability Table:**

| Adjacent Allies | Success Probability | Failure Probability |
|-----------------|---------------------|---------------------|
| 1 | 50.0% | 50.0% |
| 2 | 75.0% | 25.0% |
| 3 (MAX) | 87.5% | 12.5% |

**Compare to Square Grid:**

| Adjacent Allies | Triangular | Square |
|-----------------|------------|--------|
| 1 | 50.0% | 50.0% |
| 2 | 75.0% | 75.0% |
| 3 | 87.5% | 87.5% |
| 4 | N/A | 93.75% |

**Critical Insight:** On triangular grids, even a "perfect" attack (3 adjacent attackers) still has **12.5% failure rate**. On square grids, the maximum is reduced to 6.25%. This makes triangular attacks inherently riskier.

---

## 3. Strategic Impact Analysis

### 3.1 Attack Reliability: "Always Some Risk"

**On Square Grid:**
- 4-stone coordinated attacks feel "safe" (93.75% success)
- Players can set up near-guaranteed captures
- Defensive investment in contested territories feels futile against massed attacks

**On Triangular Grid:**
- Maximum attack still fails 1-in-8 times
- Even overwhelming force carries meaningful risk
- Creates "should I push my luck?" decisions

**Design Implication:** Players must weigh whether to:
1. Attack with 2-3 stones and accept risk
2. Wait and consolidate (but opponent may do same)
3. Make multiple weaker attacks to spread risk

This encourages **wave-based aggression** rather than single decisive strikes.

### 3.2 Defensive Positioning: Structurally Easier

**Triangle Orientation Creates Natural Defense:**

```
     /\          \/
    /  \   vs   /  \
   /____\      /____\

  "Point-Up"   "Point-Down"
  (Forward)    (Backward)
```

On a triangular grid, triangles alternate between "point-up" and "point-down" orientations. This creates:

**Defensive Advantage #1: Natural Chokepoints**
- A line of point-up triangles can only be attacked from 1 direction by point-down triangles
- Creates natural "front lines" with clear facing

**Defensive Advantage #2: Fewer Attack Vectors**
- Each position can only be attacked from 3 directions (vs 4)
- Easier to "cover" all approaches with fewer pieces

**Defensive Advantage #3: Staggered Formations**
- Two triangles sharing an edge + a third behind creates a "V formation"
- V formations naturally protect the rear triangle with 2 forward defenders

```
    /\  /\      <- Front line (2 triangles)
   /  \/  \
   \  /\  /     <- Protected rear (1 triangle defended by both above)
    \/  \/
```

### 3.3 Front Line Shapes: Inherently Jagged

**Square Grid Front Lines:**
```
1 1 1 1 1    <- Smooth, straight
. . . . .
2 2 2 2 2
```

**Triangular Grid Front Lines:**
```
    1   1   1
   / \ / \ / \
  /   1   1   \    <- Zig-zag is MANDATORY
 / \ / \ / \ / \
    2   2   2
```

On triangular grids, **straight lines don't exist**. Every "line" is inherently a zig-zag. This has profound implications:

1. **No clean defensive walls:** Every "line" has protrusions that can be picked off
2. **Penetration is easier:** Jagged lines have weak points to exploit
3. **Encirclement is harder:** Surrounding a position requires more pieces
4. **Flanking is natural:** The geometry encourages side attacks

---

## 4. Game Experience Analysis

### 4.1 Does Lower Max Adjacency Make Attacks Scarier?

**Yes, significantly.**

In square grid play, players often reach a point where an attack becomes "inevitable" - 4 adjacent stones means 93.75% success, low enough risk to commit without hesitation.

On triangular grids, even the "best possible" attack (87.5%) still fails noticeably often. Over a 20-turn game with 10 attacks:
- Square grid (93.75%): Expected 0.6 failures, 54% chance of zero failures
- **Triangular (87.5%): Expected 1.25 failures, 27% chance of zero failures**

Players will experience more attack failures, making each attack feel like a **genuine gamble**.

**Psychological Effect:**
- Square grid: "I have overwhelming force, attack is routine"
- Triangular: "I have overwhelming force, but I've been burned before..."

This creates **tension** and **memorable moments** when attacks fail against the odds.

### 4.2 More Back-and-Forth Territory Swapping?

**Prediction: Yes, with a specific pattern.**

The combination of:
- Riskier attacks (12.5% failure rate at max)
- Easier defense (fewer attack vectors)
- Natural zig-zag front lines (always exploitable weak points)

Creates a **dynamic equilibrium** where:

1. **Early game:** Rapid expansion into neutral territory
2. **Mid game:** Front lines stabilize into zig-zag patterns
3. **Late game:** Probing attacks at weak points, occasional breakthroughs
4. **Endgame:** Accumulated small advantages determine winner

This is closer to **WWI trench warfare** than **blitzkrieg** - territory changes hands in small, hard-fought exchanges rather than sweeping captures.

### 4.3 Emergent Formations

**The Triangle Defense:**
```
       1
      / \
     1   1
```
Three stones in a triangle mutually protect each other. Each stone has 2 neighbors, meaning attacking any one faces 75% defense (from the 2 adjacent allies of the defender being able to potentially counterattack... wait, let me reconsider).

Actually, in this game, defense doesn't work that way - we need to think about this differently. The key is that with only 3 neighbors, an attacker can bring at most 3 supporting stones. If one is the target, the attacker has at most 2 OTHER adjacent positions for support.

**The Spearhead:**
```
       1
      / \
     /   \
    1-----1
   / \   / \
  /   \ /   \
 1     1     1
```
A V-shaped formation pointing into enemy territory. The tip (top triangle) can be supported by 2 stones behind it. If lost, the next layer becomes the new front.

**The Phalanx:**
A row of alternating up/down triangles, all filled. Creates a wall that's individually weak but collectively resilient.

---

## 5. Comparison: Triangular vs Square Grid

| Aspect | Square Grid | Triangular Grid |
|--------|-------------|-----------------|
| **Neighbors per cell** | 4 | 3 |
| **Max attack success** | 93.75% | 87.5% |
| **Max attack failure** | 6.25% | 12.5% |
| **Front line shape** | Straight possible | Always zig-zag |
| **Defensive feel** | "Walls can be overwhelmed" | "Chokepoints are defensible" |
| **Offensive feel** | "Mass enough force, victory is certain" | "Even superior force can fail" |
| **Positional complexity** | Medium | High (triangle orientation matters) |
| **Comeback potential** | Moderate | Higher (lucky defense saves games) |
| **Game pace** | Faster, decisive | Slower, grinding |
| **Player agency** | Higher (less RNG impact at high skill) | More variance (RNG always present) |

### 5.1 Which Creates Better Gameplay?

**For casual players:** Triangular grid may be **more fun** because:
- More dramatic "against the odds" moments
- Easier to defend means trailing player has hope
- Unique geometry is novel and interesting

**For competitive players:** Square grid may be **fairer** because:
- Skill converts to wins more reliably
- Less variance in outcomes
- Clear "correct" plays exist

**For AI training:** Triangular grid may be **more interesting** because:
- Unique geometry requires novel heuristics
- Higher variance creates more diverse training data
- Less risk of "solved" optimal play

**Recommendation:** Triangular grid for **novel game experience**; square grid for **competitive balance**.

---

## 6. AI Considerations

### 6.1 Does Triangular Geometry Help or Hurt AI Development?

**Helps:**

1. **Smaller branching factor:** With 3 neighbors instead of 4, each position has fewer moves to consider (3 attack directions vs 4)
2. **Clearer evaluation:** Triangle orientation creates natural "forward/backward" concepts for positional evaluation
3. **Novel research opportunity:** Triangular grid games are underexplored in AI research
4. **Pattern recognition:** V-formations and spearheads create recognizable patterns to learn

**Hurts:**

1. **Unusual representation:** Most neural network architectures (CNNs) assume square grids; triangular requires custom handling
2. **Higher variance:** 12.5% attack failure rate means more noisy training signal
3. **Less transferable:** Skills learned don't transfer to other games as easily
4. **Smaller community:** Fewer reference implementations and research papers

### 6.2 AI Implementation Approaches

**Option A: Convert to Equivalent Representation**
- Map triangular grid to hex-based representation (well-studied)
- Use existing hex game AI techniques (e.g., from Hex, Havannah)

**Option B: Custom Triangular Architecture**
- Design network to understand triangle adjacency directly
- Could use graph neural networks (GNNs) for natural representation

**Option C: Flattened Feature Vector**
- Treat each cell as independent feature
- Let network learn adjacency relationships
- Simplest to implement but may be less efficient

**Recommendation:** Start with Option C for rapid prototyping, explore Option A if performance matters.

---

## 7. Ratings

### Elegance: 8/10

**Strengths:**
- Triangle tessellation is mathematically elegant
- 3-neighbor rule is clean and intuitive
- Triangle orientation creates natural "facing" without explicit rules
- Hexagonal boundary is aesthetically pleasing

**Weaknesses:**
- Harder to visualize than square grid
- Rendering requires more effort
- Less familiar to players

### Strategic Depth: 8/10

**Strengths:**
- Triangle orientation adds layer of positional thinking
- Lower attack cap creates more difficult decisions
- Natural formations (V, spearhead) emerge organically
- Zig-zag front lines create tactical complexity

**Weaknesses:**
- Higher variance may frustrate deep strategists
- May devolve into "position and pray" at high level
- Less explored, optimal strategies unknown

### AI-Friendliness: 6/10

**Strengths:**
- Smaller neighbor count reduces branching
- Clear geometric patterns to learn
- Novel research opportunity

**Weaknesses:**
- Non-standard grid requires custom implementation
- Higher variance in outcomes
- Less existing research to build upon
- Requires specialized neural network architectures or representations

---

## 8. What Makes Triangular Grids Special?

After this analysis, the unique properties of triangular grids for this game are:

### 8.1 Intrinsic Uncertainty
The 12.5% failure rate on maximum attacks means **certainty is never achievable**. Every attack is a meaningful decision with real risk. This prevents the "I've already won, just executing" feeling.

### 8.2 Directional Geometry
Unlike square grids (4-way symmetry) or hex grids (6-way symmetry), triangular grids have inherent **asymmetry** - each triangle "faces" a direction. This creates natural concepts of "advancing" and "retreating" without explicit rules.

### 8.3 Forced Jagged Lines
The inability to create straight lines means **perfect defense is impossible**. There's always a weak point to exploit, keeping games dynamic.

### 8.4 Mutual Protection
Three stones in a triangle is the minimum stable formation, and it's also the maximum attack force. This creates elegant **economy** - the same number (3) governs both offense and defense.

---

## 9. Recommended Next Steps

1. **Prototype the 37-cell hexagonal board** - Create visual representation and basic game logic
2. **Playtest against square grid version** - Same rules, both board types, compare player experience
3. **Implement basic AI** - Random and simple heuristic agents to establish baseline
4. **Tune parameters if needed** - If 87.5% max feels too low, consider adding "momentum" bonus for consecutive attacks
5. **Explore hybrid variant** - Triangular grid with higher attack bonus to compensate for geometry

---

## 10. Conclusion

The triangular grid variation of PLACE OR ATTACK creates a **distinctly different game experience** from the square grid version. The 3-neighbor constraint produces:

- More uncertain, tense attacks
- More defensible positions
- More dynamic, grinding gameplay
- More dramatic comeback potential

This makes it potentially more **engaging for casual play** while possibly being **too random for serious competition**.

The geometry is elegant and underexplored, making it an excellent choice for **novel game design research** and **unique player experience**.

**Final Verdict:** Worth prototyping. The triangular grid's unique properties create genuine gameplay innovation rather than just being a cosmetic change.

---

*Game Concept Sketch v1.0*
*Strategic Influence - Triangular Grid Exploration*
