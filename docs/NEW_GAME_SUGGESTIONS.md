# New Game Suggestions
## Preference Analysis and Concept Generation

*Based on analysis of: GAME_DESIGN_EXPLORATION.md, Influence Hex Edition, Triangular Assault, Fault Lines, and Strategic Dominion*

---

## Part 1: Preference Analysis

### 1.1 Core Mechanical Preferences

After analyzing the designer's game exploration documents, several strong mechanical preferences emerge:

**Geometry Preferences:**
- Strong preference for **hexagonal and triangular grids** over square grids
- Values the isotropy of hex geometry (no privileged directions)
- Appreciates the "3-neighbor" constraint of triangular tessellation
- Enjoys how non-square geometry creates natural chokepoints and formations

**Action Economy:**
- **One stone per territory** - Clean state representation without stacking
- **One decision per turn** - Reduced cognitive load, increased decision quality
- **Alternating turns over simultaneous** - Prefers perfect information and response play
- Avoids "analysis paralysis" from too many options

**Scoring and Resolution:**
- **Cumulative/rolling scoring** - Investment compounds over time (Influence Hex)
- **Probability at resolution moments** - Tension without mid-game chaos (Fault Lines)
- Simple victory conditions that are easy to understand but hard to achieve
- Values deterministic options for competitive play, probabilistic for drama

**Depth Mechanisms:**
- **Connection mechanics** - Groups and chains matter (Fault Lines' survival, links in Strategic Dominion)
- **Fortification/defense as meaningful choice** - Not just offense
- **Multi-turn effects** - Decisions that compound or unfold over time
- Positional play where every vertex/cell has strategic texture

**Technical Constraints:**
- **AI-tractable game states** - Manageable branching factor
- Minimax/expectimax friendly
- Symmetry for state canonicalization
- Clear evaluation functions possible

### 1.2 Aesthetic and Thematic Preferences

**Visual Elegance:**
- Organic, natural-looking board states
- Beautiful geometric patterns emerging from play
- The aesthetic of Go: stones on a clean field

**Thematic Resonance:**
- Territory control without explicit "war" theming
- Natural phenomena metaphors (fault lines, influence, watersheds)
- Abstract enough to focus on mechanics, evocative enough to create narrative

**Mathematical Beauty:**
- Clean probability fractions (33%, 50%, 67%)
- Natural thresholds (the "6-stone survival" in Fault Lines)
- Elegant relationships between numbers (3 corners = 3 neighbors = triangular harmony)

### 1.3 What They're Actively Avoiding

Based on explicit statements and design choices:

| Avoided Element | Why |
|-----------------|-----|
| Multiple interacting systems | Complexity without depth |
| Excessive tracking overhead | Mental burden, slows play |
| Many decision types per turn | Analysis paralysis |
| "Designed complexity" | Prefer emergent depth from constraints |
| Mid-game randomness/chaos | Disrupts planning, feels unfair |
| Simultaneous play | Requires game theory, opponent modeling |
| Square grids | Diagonal asymmetry, less elegant |
| Stacking/accumulation on single spaces | Tracking overhead |
| Hidden information | Prefers perfect information for calculation |

### 1.4 The "Feel" They're Seeking

Reading between the lines, this designer wants games that feel:

**Meditative yet tense:** Each decision should matter, but the decision space should be parseable. The tension comes from tradeoffs, not from being overwhelmed.

**Investment-oriented:** Stones placed early should matter throughout the game. There's satisfaction in watching a position compound in value.

**Geometrically satisfying:** The board state should look meaningful. Patterns should emerge naturally from good play.

**Dramatically resolving:** Whether through end-game probability rolls (Fault Lines) or cumulative score reveals (Influence Hex), games should build to satisfying conclusions.

**Replayable through depth:** Simple enough to teach in 5 minutes, deep enough to study for years. The Go ideal.

**Constraint-driven strategy:** "Constraints create strategy." Limiting options (single stone, single action, three neighbors) creates meaningful choices where every decision matters.

---

## Part 2: Three New Game Concepts

---

### Game Concept 1: HARMONIC CHAINS

#### 1. Elevator Pitch

Place stones on a triangular lattice to form chains that "resonate" based on their geometric properties. At game's end, each chain scores points based on its length and whether it forms closed loops. Simple placement, deep positional play, satisfying resolution.

*"Build chains that sing. Closed loops resonate forever; open chains fade."*

#### 2. Core Mechanic

**The One Elegant Rule:** When the game ends, each connected chain scores: **(length squared) if it forms a closed loop, (length) if it remains open.**

This single scoring rule creates profound strategic implications. A chain of 5 stones scores 5 points open, but 25 points if you close it into a loop. However, closing loops requires returning to your starting point without crossing yourself - a spatial puzzle.

#### 3. Board/Components

- **Board:** Triangular lattice within hexagonal boundary (37 or 61 vertices)
- **Stones:** Two colors, ~25 per player
- **Key Geometry:** Each vertex connects to exactly 6 others (hexagonal dual)
- Chains are orthogonal connections through the lattice (not diagonal)

```
      o---o---o---o
     /|\  |  /|\  |
    o-+-o-+-o-+-o-+-o
    |  \|/  |  \|/  |
    o---o---o---o---o
    |  /|\  |  /|\  |
    o-+-o-+-o-+-o-+-o
     \|/  |  \|/  |
      o---o---o---o
```

#### 4. Turn Structure

**Each turn:**
1. Place one stone on any empty vertex
2. That's it

**Chain Formation:**
- Chains are groups of same-color stones connected along lattice edges
- A chain can branch (Y-shapes, etc.)
- A closed loop requires returning to any stone in the chain without lifting

**End Game:**
- When all vertices filled OR both players pass consecutively
- Score each player's chains

#### 5. Victory Condition

**Highest total chain score wins.**

Scoring:
- Open chain of length N = N points
- Closed loop of length N = N squared points
- Branching chains score the longest simple path through them
- A chain that self-intersects into multiple loops: each loop scores squared separately

#### 6. Why It Fits This Designer

| Designer Preference | Harmonic Chains Implementation |
|---------------------|-------------------------------|
| Triangular geometry | Triangular lattice (6 connections per vertex) |
| One stone, one decision | Single placement per turn |
| Connection mechanics | Chain formation is central |
| Cumulative value | Longer chains score more |
| AI-tractable | Clear evaluation: count chain lengths |
| Elegant math | Squared scoring creates natural threshold decisions |
| End-game resolution | All scoring at game end |

#### 7. Strategic Depth Preview

**The Closing Dilemma:** A chain of 6 open = 6 points. Closing it = 36 points. But closing requires 2 more stones to complete the loop, and opponent can block your closure path.

**The Fork Gambit:** Building a chain that threatens to close in TWO directions. Opponent can only block one.

**The Sacrifice:** Sometimes leaving your own chain open to block opponent's closure is correct (deny them 25+ points to cost yourself 5).

**Length vs. Closure:** One giant chain (length 20) open = 20 points. Four small loops (length 5 each) = 100 points. But small loops are harder to complete.

#### 8. Unique Hook

The **squared scoring for loops** creates a dramatic nonlinearity. Players must balance:
- Extending chains (linear benefit)
- Closing chains (exponential benefit but geometric challenge)
- Blocking opponent closures (defensive)

No other game in the designer's collection has this "geometric closure reward" mechanic. It's novel yet fits perfectly with their preferences for connection-based, geometry-driven play.

---

### Game Concept 2: TIDAL FLOW

#### 1. Elevator Pitch

Place stones on a hexagonal board to control "sources" and "sinks." At end of each round, water flows from sources through empty spaces toward sinks. You score for each empty hex your water passes through. Build the aqueduct; own the flow.

*"Place the stones. The water finds its path."*

#### 2. Core Mechanic

**The One Elegant Rule:** After all placements, water flows from your sources toward the nearest sink, following the shortest path through empty hexes. You score 1 point for each empty hex the water traverses.

Water cannot flow through occupied hexes (stones block flow). Multiple paths of equal length split the water (each scores half). Your opponent's sinks also attract flow - so you might accidentally feed their scoring.

#### 3. Board/Components

- **Board:** Standard hex grid (19-hex Catan layout)
- **Stones:** Two colors plus "source" and "sink" markers
- **Sources:** 2 per player (placed during setup or earned)
- **Sinks:** 2 shared (neutral) in fixed positions, or player-controlled

```
          S         S = Sink (shared)
       ⬡  ⬡  ⬡      Numbers show flow distance
      ⬡  2  ⬡  ⬡
     ⬡  1  ⬡  2  ⬡
      ⬡  o  ⬡  ⬡     o = Source (yours)
       ⬡  ⬡  ⬡
          S
```

#### 4. Turn Structure

**Setup Phase:**
- Place sinks at predetermined positions (opposite corners)
- Each player places 2 source markers on the board

**Play Phase (alternating turns):**
1. Place one stone on any empty hex (not source/sink positions)
2. After placement, score immediately based on current flow

**Flow Calculation:**
- From each of your sources, calculate shortest path to any sink
- Count empty hexes on that path (not including source or sink)
- That's your score this turn

#### 5. Victory Condition

**Highest cumulative score when board fills OR both pass.**

The cumulative scoring means early source placement compounds over time. But placing stones can redirect flow - yours and opponent's.

#### 6. Why It Fits This Designer

| Designer Preference | Tidal Flow Implementation |
|---------------------|--------------------------|
| Hexagonal geometry | Standard hex board |
| Cumulative scoring | Score every turn |
| One decision per turn | Place one stone |
| Deterministic resolution | Shortest path is calculable |
| AI-tractable | Pathfinding is polynomial |
| Emergent depth | Flow routing creates complex strategy |
| Natural metaphor | Water flow is intuitive |

#### 7. Strategic Depth Preview

**Channel Building:** Place stones to create "channels" that force flow through more hexes. A source 2 hexes from a sink normally scores 1. But place blockers to force a 6-hex detour - now you score 5.

**Flow Denial:** Block opponent's channels. Force their water into direct paths (low score) or toward YOUR sinks (you control scoring opportunity).

**Source Positioning:** Sources near the center have more routing options. Sources near edges are easier to channel but limited in direction.

**The Shared Sink Tension:** Both players' water seeks the same sinks. Do you build toward a sink you're closer to, or contest the one they're developing?

**Late Game Scarcity:** As the board fills, flow paths become constrained. Final stones can dramatically reroute scoring.

#### 8. Unique Hook

The **path-scoring mechanic** is novel in this designer's collection. Unlike Influence Hex (corner counting) or Fault Lines (group survival), Tidal Flow rewards **creating longer paths through empty space**.

You're not claiming territory - you're shaping terrain to make territory more valuable. It's like building an aqueduct or irrigation system. The empty spaces are where you score, but you need stones to direct flow.

This inverts typical territory thinking and creates unique strategic puzzles.

---

### Game Concept 3: ECLIPSE LATTICE

#### 1. Elevator Pitch

Place stones on the vertices of a hex grid. Each stone "casts a shadow" along the three lattice directions. Where your shadows overlap, you have strong control. Where shadows from both players meet, you contest. The shadow map IS the score - recalculated every turn.

*"In light, you cast shadows. In shadow, you claim dominion."*

#### 2. Core Mechanic

**The One Elegant Rule:** Each stone projects influence in the 3 lattice directions passing through it. Each hex scores for whoever has more "shadow rays" passing through it.

```
Shadow Projection Example:

      *         * = Shadow extends in this direction
      |
   *--O--*      O = Your stone
      |
      *

Stone at O casts shadow along all 3 lattice axes
```

#### 3. Board/Components

- **Board:** Triangular lattice with hexagonal boundary (vertices for stones, hexes for scoring)
- **Stones:** Two colors, ~15 per player
- **Shadow tracking:** Count rays through each hex (can use mental calculation or markers)

The board has approximately 42 hexagonal cells where shadow-influence is counted, with ~24 vertices where stones are placed (the same as Influence Hex geometry, repurposed).

#### 4. Turn Structure

**Each turn:**
1. Place one stone on any empty vertex
2. Recalculate shadow-influence across all hexes
3. Score immediately: +1 for each hex where you have majority influence

**Shadow Rules:**
- Each stone projects a "ray" infinitely in each of 3 directions
- Rays are blocked by opponent's stones (not your own)
- A hex touched by more of your rays than opponent's rays = your control
- Ties = neutral (no points)

#### 5. Victory Condition

**Highest cumulative score when board fills OR both pass consecutively.**

Like Influence Hex, scoring happens every turn, so early stones contribute more to final score.

#### 6. Why It Fits This Designer

| Designer Preference | Eclipse Lattice Implementation |
|---------------------|-------------------------------|
| Vertex placement | Stones on vertices |
| Triangular geometry | 3 shadow directions |
| Cumulative scoring | Score every turn |
| One decision per turn | Place one stone |
| Deterministic | Shadow calculation is exact |
| AI-tractable | Line-of-sight is O(n) |
| Blocking/cutting | Stones block opponent shadows |

#### 7. Strategic Depth Preview

**The Shadow Web:** Place stones to maximize coverage. A single stone projects 3 infinite rays. Two stones: 6 rays. But placement matters - rays should cover different hexes, not overlap.

**Blocking Lines:** Your stones block opponent's shadows. Place strategically to "cut off" their influence from reaching valuable hexes.

**The Interior Advantage:** Center stones project influence across more hexes (rays extend in all directions). Edge stones waste shadow projection off-board.

**Shadow Stacking:** Multiple of your rays through one hex don't score more, but they protect against opponent contesting. 3 of your rays vs. 2 of theirs = still just 1 point for you, but more resilient.

**The Cut:** A single stone placed on an opponent's shadow line can deny them influence across half the board.

#### 8. Unique Hook

The **line-of-sight scoring** is entirely novel in this collection. Unlike corner-based influence (Influence Hex) or adjacency-based connection (Fault Lines), Eclipse Lattice uses **directional projection**.

Each stone has geometric "reach" far beyond its immediate neighbors. This creates:
- Long-range planning (a stone here affects hexes 5 vertices away)
- Dramatic blocking plays (cut a shadow line, flip multiple hexes)
- A unique visual language (seeing the board as overlapping shadow webs)

The metaphor of light and shadow is elegant and intuitive while creating strategy unlike anything in the existing collection.

---

## Part 3: Comparison

### 3.1 Comparison Table

| Aspect | Harmonic Chains | Tidal Flow | Eclipse Lattice |
|--------|-----------------|------------|-----------------|
| **Core Tension** | Linear vs. exponential scoring | Routing vs. blocking | Coverage vs. cutting |
| **Scoring Timing** | End-game only | Every turn (cumulative) | Every turn (cumulative) |
| **Geometry** | Triangular lattice | Hexagonal tiles | Triangular lattice |
| **What You Build** | Chains and loops | Channels and paths | Shadow webs |
| **Blocking** | Deny closure paths | Reroute opponent flow | Cut shadow lines |
| **Skill Expression** | Geometric planning | Pathfinding intuition | Line-of-sight reading |
| **Elegance Rating** | 9/10 | 8/10 | 9/10 |
| **Novelty Rating** | 9/10 | 8/10 | 10/10 |
| **Complexity** | Low | Medium | Medium |
| **AI Tractability** | High | High | Very High |

### 3.2 Most Aligned with Designer's Preferences

**Winner: HARMONIC CHAINS**

Harmonic Chains is the most aligned choice because it:

1. **Uses triangular geometry** - The designer's stated favorite
2. **Features connection mechanics** - Central to Fault Lines, which they clearly value
3. **Has end-game resolution** - Like Fault Lines, tension builds toward final scoring
4. **Embodies "elegant simplicity"** - One rule (squared scoring for loops) drives everything
5. **Creates the "feel" they seek** - Meditative placement with dramatic resolution
6. **Is genuinely simple** - No per-turn calculations, just place and observe
7. **Has natural mathematical beauty** - The squared function creates clear thresholds

The loop-closing mechanic is a natural evolution of their interest in "connection priority" from Fault Lines, but with a geometric puzzle dimension that's entirely new.

### 3.3 The "Bold Choice" That Might Surprise Them

**Bold Pick: ECLIPSE LATTICE**

Eclipse Lattice might surprise this designer because:

1. **Line-of-sight is a different paradigm** - None of their explored games use directional projection
2. **Long-range influence from single stones** - Breaks the "local effect" assumption
3. **More tactical, less territorial** - Focuses on cutting and blocking rather than pure claiming
4. **Visual complexity** - The shadow web can be hard to parse initially

However, once understood, it delivers on all their core values: simple rules, emergent depth, hexagonal geometry, AI tractability, and elegant mathematics.

The designer might initially resist Eclipse Lattice for its "busier" visual state - tracking shadow lines is more cognitively demanding than counting corners or measuring chains. But if they value the "fog of war" concepts mentioned in Strategic Dominion and the line-cutting strategies they seem drawn to, Eclipse Lattice could become a favorite.

**Why it's worth the risk:** Eclipse Lattice is the most genuinely novel of the three suggestions. It doesn't feel like a variant of anything in their collection. If they're seeking games that expand their design horizons, this is the one that offers a truly new strategic dimension while respecting their core values.

---

## Final Recommendation

**For immediate prototyping:** Start with HARMONIC CHAINS. It's closest to their established preferences, simplest to implement, and most likely to "feel right" from the first playtest.

**For design exploration:** Build ECLIPSE LATTICE as a stretch project. It offers the most learning about a new strategic space (directional projection) and could reveal new design principles.

**For balanced portfolio:** TIDAL FLOW sits comfortably between the two - cumulative scoring like Influence Hex, but with a novel routing mechanic that rewards different intuitions than their existing games.

All three games honor the designer's core philosophy: **Constraints create strategy. Simple rules create emergent depth. Elegance is not the absence of complexity, but the presence of the right complexity.**

---

*Suggestions generated based on comprehensive analysis of the Strategic Influence game design exploration project.*
