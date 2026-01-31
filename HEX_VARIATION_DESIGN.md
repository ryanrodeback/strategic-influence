# ATTENTION + INFLUENCE: HEX VARIATION

## Game Concept Sketch
**Version:** 1.0
**Status:** Design Exploration
**Base Game:** Strategic Influence (5x5 grid territorial control)

---

## EXECUTIVE SUMMARY

After analyzing multiple hex adaptation approaches, I propose **stones placed on hex vertices** with **triangular regions as the claimable areas**. This creates a fundamentally different game that feels more organic while preserving the core tension of probabilistic territorial control.

**The Core Insight:** In a triangular lattice, every claimed region has exactly 3 corners of influence - creating natural 33/33/33 splits that feel more intuitive than the original's binary expansion/combat system.

---

## PART 1: THE RECOMMENDED DESIGN

### 1.1 Topology Choice: Vertices + Triangles

```
PLACEMENT OPTIONS ANALYZED:

Option A: Stones on Hex Centers
  [X] Just a connectivity change (6 neighbors vs 4)
  [X] Mechanically identical to square grid
  [X] Misses the unique potential of hex geometry

Option B: Stones on Hex Vertices, Claim Hexes
  [?] Each hex surrounded by 6 vertices
  [?] Would need 6-way influence calculations (complex)
  [X] Loses the elegance of simple majority

Option C: Stones on Hex Vertices, Claim Triangles  <<<< RECOMMENDED
  [+] Each triangle has exactly 3 corners
  [+] Natural probability: 33% per corner stone
  [+] Creates gradient/contested territories
  [+] Beautiful emergent patterns
```

### 1.2 The Triangular Lattice

When you place stones on hex vertices, the space between them naturally divides into triangles:

```
          Vertex (stone placement)
              o
             /|\
            / | \
           /  |  \
          o---+---o
         / \ /|\ / \
        /   X | X   \
       /   / \|/ \   \
      o---+---o---+---o
       \   \ /|\ /   /
        \   X | X   /
         \ / \|/ \ /
          o---+---o
               |
               o

  Each TRIANGLE (marked by the grid) is a claimable region.
  Each triangle has exactly 3 VERTEX positions (corners).
  Stones placed at vertices determine who controls the triangle.
```

### 1.3 Board Size Recommendation

**Recommended: Radius-3 Hexagonal Board**

```
Radius-3 board statistics:
- 19 hex faces in the underlying grid
- 24 vertex positions (stone placement spots)
- 42 triangular regions (claimable areas)

This gives:
- Similar territory count to 5x5 square (25 cells vs 42 triangles)
- Slightly higher strategic complexity
- Compact enough for reasonable game length
```

Visual layout (radius 3):
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

  24 vertices (o), 42 triangles
```

---

## PART 2: THE PROBABILITY MODEL

### 2.1 Triangle Influence Calculation

Each triangle's control is determined by its 3 corners:

```
Triangle Ownership States:
=========================

[P1][P1][P1]  ->  100% Player 1 (CLAIMED)
[P2][P2][P2]  ->  100% Player 2 (CLAIMED)

[P1][P1][P2]  ->  CONTESTED (P1 advantage)
[P1][P2][P2]  ->  CONTESTED (P2 advantage)

[P1][P1][ ]   ->  67% P1, 33% neutral (SOFT CLAIM)
[P2][P2][ ]   ->  67% P2, 33% neutral (SOFT CLAIM)

[P1][P2][ ]   ->  33% each + 33% neutral (FULLY CONTESTED)
[P1][ ][ ]    ->  33% P1, 67% open (WEAK INFLUENCE)

[ ][ ][ ]     ->  100% neutral (UNCLAIMED)
```

### 2.2 Resolution Mechanism (Two Options)

**Option A: Probabilistic Resolution (Preserves Base Game Feel)**
```
At game end, each CONTESTED triangle resolves:
- Roll based on influence percentages
- 2 P1 corners vs 1 P2 corner: 67% P1 wins, 33% P2 wins
- Creates dramatic end-game tension
```

**Option B: Continuous Scoring (More Strategic)**
```
Each triangle contributes fractional points:
- [P1][P1][P2] = 0.67 points to P1, 0.33 to P2
- Removes randomness, pure positional play
- More chess-like, less poker-like
```

**RECOMMENDATION:** Option A for casual play (preserves excitement), Option B for competitive/AI play (rewards precise calculation).

### 2.3 The Math: Why 33% Feels Right

In the original game:
- Expansion to neutral: 50% per stone sent
- Combat: 50% hit chance per roll

In hex variant with triangles:
- Each corner = 33.33% influence
- Two corners = 66.67% control
- Three corners = 100% guaranteed

**The elegance:** Committing 2 of 3 corners gives you a 2:1 advantage - similar risk/reward profile to sending 2 stones in the original (75% success vs 50%).

```
Commitment Comparison:
                    Square Grid          Hex/Triangle
                    -----------          ------------
Minimal risk:       2 stones (75%)       2 corners (67%)
Safe bet:           3 stones (87.5%)     3 corners (100%)
Coin flip:          1 stone (50%)        1 corner (33%)
```

---

## PART 3: MOVEMENT AND ACTIONS

### 3.1 Adjacency in Triangular Lattice

Each vertex connects to **exactly 3 other vertices** (vs 4 in square grid):

```
        o
       /|\
      / | \
     o--+--o
      \ | /
       \|/
        o

  Center vertex has 3 neighbors.
  Movement is to adjacent vertices only.
```

### 3.2 Actions Per Stone

**GROW:** Stay at vertex, gain +1 stone (same as base game)

**MOVE:** Send stones to ONE of 3 adjacent vertices
- Fewer movement options than square grid (3 vs 4)
- Creates tighter tactical decisions
- "Funneling" effect - harder to spread thin

### 3.3 Expansion Into Empty Vertices

When moving to an unoccupied vertex:
```
Each stone has 50% chance to "take root"
- ANY success: All stones claim the vertex
- ALL fail: All stones lost

This is IDENTICAL to the base game mechanic.
```

### 3.4 Combat At Occupied Vertices

When moving to an enemy-occupied vertex:
```
Alternating roll combat (same as base game):
1. Defender rolls (50% to eliminate 1 attacker)
2. Attacker rolls (50% to eliminate 1 defender)
3. Continue until one side eliminated
```

---

## PART 4: GAME EXPERIENCE ANALYSIS

### 4.1 How Hex Geometry Changes Strategy

**Reduced Mobility, Increased Commitment:**
- 3 movement options vs 4 means each move is more consequential
- Harder to "probe" in multiple directions
- Encourages building focused lines of influence

**Gradient Control:**
- Unlike square grid where you either own a cell or don't
- Here, you can have "soft claims" (2 corners) that may flip
- Creates tension throughout the game, not just at expansion moments

**Natural Flanking:**
- 120-degree angles create natural "pincer" opportunities
- Surrounding a vertex from 2 directions threatens 2 shared triangles
- More intuitive tactical patterns

### 4.2 Connection Patterns

```
Square Grid Patterns:        Hex/Triangle Patterns:
==================          ====================

Line (4 in a row):          Triangle Ring:
o-o-o-o                         o
                               / \
Cross formation:              o---o
  o                            \ /
o-o-o                           o
  o                     (surrounds 1 central triangle)

Corner defense:             Wedge:
o-o                            o
  |                           /|
  o                          o-o
                       (controls 2 triangles solidly)

Diagonal expansion:         Spiral:
o . .                       o-o
. o .                        \|
. . o                         o-o
                               \|
                                o
                        (efficient expansion pattern)
```

### 4.3 Does It Feel More "Organic"?

**YES, for these reasons:**

1. **No Grid Artifacts:** Square grids create artificial "horizontal vs diagonal" distinctions. Triangular lattices are isotropic - all directions equally valid.

2. **Smoother Boundaries:** Contested regions blend naturally. A 2-1-0 triangle feels like "mostly mine" rather than binary owned/unowned.

3. **Natural Clustering:** The 3-neighbor limit encourages stone groups that look like organic growths rather than rectangular blocks.

4. **Visual Beauty:** Hex/triangle patterns have intrinsic aesthetic appeal (see: Islamic geometric art, honeycombs, crystal structures).

---

## PART 5: AI TRACTABILITY ANALYSIS

### 5.1 State Representation

**Board State:**
```python
# Square grid: 5x5 = 25 cells, each with (owner, stone_count)
# Hex variation: 24 vertices, each with (owner, stone_count)

# SIMILAR complexity for raw state size
# But derivable state (triangle control) adds complexity:
#   42 triangles, each with computed influence values
```

**State Space Size:**
```
Square 5x5:
- 25 positions
- Each: 3 states (empty, P1, P2) * variable stones
- Rough upper bound: 3^25 * stone_variations ~ 10^14

Hex R3 (24 vertices):
- 24 positions
- Same ownership states
- Rough upper bound: 3^24 * stone_variations ~ 10^13

CONCLUSION: Slightly smaller raw state space, but more complex
derived state (triangle calculations).
```

### 5.2 Action Space

```
Square grid (interior cell, 4 stones):
- GROW: 1 option
- MOVE: 4 directions * (send 1, 2, 3, or 4) = 16 options
- Plus splits... ~50+ options per cell

Hex vertex (3 neighbors, 4 stones):
- GROW: 1 option
- MOVE: 3 directions * (send 1, 2, 3, or 4) = 12 options
- Plus splits... ~30 options per vertex

CONCLUSION: ~40% smaller action space per position.
This is GOOD for AI - faster search, more tractable tree.
```

### 5.3 Symmetry Exploitation

**Hex geometry offers BETTER symmetry:**

```
Square grid symmetries: 8 (4 rotations + 4 reflections)
Hexagonal board symmetries: 12 (6 rotations + 6 reflections)

More symmetries = more state equivalences
More equivalences = smaller effective state space
Better for AI training and search pruning
```

**Rotational Canonicalization:**
- Any hex board state can be canonicalized to one of 12 equivalent forms
- Transposition tables can be 12x more efficient
- Neural network training sees 12 augmented views per position

### 5.4 Heuristic Evaluation

**Easier or Harder?**

EASIER aspects:
- Triangle influence is directly calculable (simple counting)
- Territorial advantage is continuous, not binary
- Gradient allows more nuanced position evaluation

HARDER aspects:
- Must evaluate 42 triangles, not just 25 cells
- Contested regions require probability-weighted scoring
- "Potential influence" (empty corners that could flip) adds lookahead

**OVERALL:** Slightly more complex evaluation, but the continuous nature actually helps gradient-based learning (neural networks love smooth gradients).

### 5.5 AI Algorithm Suitability

```
Algorithm         Square Grid    Hex Variant    Notes
---------         -----------    -----------    -----
Minimax           Good           Good           Smaller branching factor helps
Alpha-Beta        Good           Good+          Better pruning with symmetry
MCTS              Good           Good+          Smaller action space = deeper rollouts
Neural Eval       Good           Better         Continuous influence = smooth gradients
RL Training       Good           Better         More symmetry augmentation

CONCLUSION: Hex variant is MORE AI-friendly, not less.
```

---

## PART 6: COMPARISON TO GRID VERSION

### 6.1 Direct Comparison Table

| Aspect | Square Grid | Hex/Triangle | Winner |
|--------|-------------|--------------|--------|
| **Board Positions** | 25 cells | 24 vertices | Tie |
| **Claimable Areas** | 25 territories | 42 triangles | Hex (more granular) |
| **Neighbors per Position** | 4 (interior) | 3 | Square (more mobility) |
| **Symmetry Group** | D4 (8) | D6 (12) | Hex |
| **State Space** | ~10^14 | ~10^13 | Hex (smaller) |
| **Action Space** | ~50/cell | ~30/vertex | Hex (smaller) |
| **Rules Complexity** | Simple | Medium | Square |
| **Territorial Nuance** | Binary | Gradient | Hex |
| **Visual Appeal** | Standard | Striking | Hex |
| **Physical Prototype** | Easy | Medium | Square |

### 6.2 Is Hex BETTER or Just DIFFERENT?

**Hex is BETTER if you value:**
- Richer territorial dynamics (gradient control)
- More elegant geometry (isotropic, beautiful patterns)
- AI training efficiency (more symmetry, smaller action space)
- Strategic depth through contested regions
- Novel gameplay feel (not "just another grid game")

**Square is BETTER if you value:**
- Simpler rules explanation
- Easier physical prototype
- Faster casual play
- Familiarity (chess/checkers muscle memory)
- More movement flexibility (4 vs 3 directions)

**MY ASSESSMENT:**
Hex variant is **objectively better for AI research** (smaller search space, more symmetry) and **subjectively better for strategic depth** (gradient control creates more nuance). It is "just different" in terms of fun - both can be enjoyable.

---

## PART 7: EMERGENT PROPERTIES

### 7.1 Beautiful Patterns That Emerge

**The Central Vertex Gambit:**
```
In a radius-3 board, the center vertex touches 6 triangles.
Controlling the center with high stone count is immensely powerful.
But it's equidistant from all starting positions - creates natural
race-to-center dynamics without artificial "center bonus" rules.
```

**The Edge Squeeze:**
```
Edge vertices touch fewer triangles (3-4 vs 6 for center).
This creates natural "interior is valuable" pressure.
But edges are easier to defend (fewer attack angles).
Trade-off emerges naturally from geometry, not arbitrary rules.
```

**Triangle Chains:**
```
A sequence of triangles sharing edges:
   o---o---o---o
    \ / \ / \ /
     o---o---o

Controlling all top vertices claims the entire chain.
Creates "line of control" strategy similar to Go.
But breaking ONE vertex breaks the whole chain - creates weakness.
```

**The Surrounding Trap:**
```
        P2
       / \
     P1---P1
      \ /
       P1

P1 controls all 4 triangles adjacent to the center.
P2's stone is "surrounded" but still influences 2 triangles.
Creates partial isolation - P2 gets 33% of 2 triangles.
Unlike Go, surrounded stones aren't captured - they persist with reduced influence.
```

### 7.2 Novel Tactical Concepts

**Influence Dilution:**
Spreading stones to touch many triangles each at 33% influence.
Hedging strategy - wins more ties but loses to focused opponents.

**Hard Claiming:**
Committing 3 corners to lock in territories with 100% certainty.
Safe but slow. Costs 3 "stone placements" per territory.

**Soft Claiming:**
Committing 2 corners (67%) to many triangles simultaneously.
Efficient but risky. May lose to focused counter-play.

**Vertex Denial:**
Placing stones to BLOCK enemy triangle completion without claiming your own.
Defensive play - prevents them from reaching 67%+.

---

## PART 8: RATINGS

### Elegance: 9/10

**Justification:**
- The 3-corner = 33% each mapping is beautiful and intuitive
- Geometry creates natural balance (center value, edge safety) without artificial rules
- Single rule change (hex vertices instead of square cells) creates dramatically different game
- The isotropic nature eliminates ugly "diagonal vs orthogonal" distinctions

Minor deduction: Triangle counting requires more explanation than "you own the cell."

### Strategic Depth: 9/10

**Justification:**
- Gradient control (67% vs 33%) creates nuanced decisions absent from binary systems
- Fewer movement options (3 vs 4) makes each move more consequential
- Triangle chains and surrounding patterns create emergent tactical vocabulary
- Contested regions persist throughout game, maintaining tension

Minor deduction: Reduced mobility might feel constraining to some players.

### AI-Friendliness: 8/10

**Justification:**
- Smaller action space per position (30 vs 50 options)
- More symmetries for state equivalence (12 vs 8)
- Continuous influence values = smooth gradients for neural networks
- Smaller overall state space (~10^13 vs ~10^14)

Deduction: Triangle influence calculation adds evaluation complexity. 42 derived values vs 25 direct values.

### Overall: 8.7/10

**This hex variation is not just different - it's a genuine improvement for strategic depth and AI tractability, with only minor increases in rules complexity.**

---

## PART 9: IMPLEMENTATION NOTES

### 9.1 Data Structures

```python
@dataclass(frozen=True)
class HexVertex:
    """Position in axial coordinates (q, r)."""
    q: int  # Column in axial system
    r: int  # Row in axial system

    def neighbors(self) -> tuple[HexVertex, HexVertex, HexVertex]:
        """Returns exactly 3 adjacent vertices."""
        return (
            HexVertex(self.q + 1, self.r),
            HexVertex(self.q, self.r + 1),
            HexVertex(self.q - 1, self.r - 1),
        )

@dataclass(frozen=True)
class Triangle:
    """A claimable region defined by 3 corner vertices."""
    v1: HexVertex
    v2: HexVertex
    v3: HexVertex

    def influence(self, board: HexBoard) -> dict[Owner, float]:
        """Calculate influence percentages."""
        corners = [board.get_owner(v) for v in (self.v1, self.v2, self.v3)]
        counts = Counter(corners)
        return {owner: count / 3.0 for owner, count in counts.items()}
```

### 9.2 Coordinate System

Use **axial coordinates** for hex math:
```
Axial: (q, r) where q + r + s = 0 (s is implicit)

This simplifies:
- Neighbor calculation: just add offset vectors
- Distance: max(|q1-q2|, |r1-r2|, |s1-s2|)
- Rotation: rotate offset vectors by 60 degrees
```

### 9.3 Rendering

For visualization, convert axial to pixel:
```python
def axial_to_pixel(q: int, r: int, size: float) -> tuple[float, float]:
    x = size * (3/2 * q)
    y = size * (sqrt(3)/2 * q + sqrt(3) * r)
    return (x, y)
```

---

## CONCLUSION

The hex variation transforms Strategic Influence from a solid territorial game into something with genuine geometric elegance. The key innovations:

1. **Triangular regions** create natural 33/33/33 probability splits
2. **3-neighbor vertices** force committed, consequential moves
3. **Gradient control** maintains tension throughout the game
4. **Rich symmetry** benefits AI training and search algorithms

This isn't just "the same game on a hex board" - it's a fundamentally different strategic experience that leverages hex geometry's unique properties.

**RECOMMENDATION:** Implement this as "Strategic Influence: Hex Edition" - a distinct variant that appeals to players seeking deeper tactical nuance and researchers wanting a more AI-tractable game system.

---

*Design sketch created for game design exploration.*
*Base game: Strategic Influence (square grid territorial control)*
