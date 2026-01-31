# Rolling Score Variant - Game Concept Sketch

## ATTENTION + INFLUENCE with Rolling Score

### Core Concept
A placement-only territorial game where areas are contested fresh each turn, building cumulative scores rather than permanent ownership.

---

## 1. COMPLETE RULES

### Setup
- **Board**: 5x5 grid (creates 4x4 = 16 possible 2x2 "areas")
- **Players**: 2 (Black and White stones)
- **Starting**: Empty board

### Turn Structure
Each turn has two phases:

**ATTENTION PHASE**
1. Active player places ONE stone on any empty intersection
2. Constraint: One stone per cell maximum
3. Players alternate (no simultaneous play)

**INFLUENCE PHASE** (after each placement)
Resolve ALL 16 areas:
- Each 2x2 area has 4 corner positions
- Count stones of each player at those corners
- **Scoring per area**:
  - 4 corners same color: +4 points (full control)
  - 3 corners same color: +2 points (strong presence)
  - 2 corners same color: +1 point (contested, both players score if 2-2)
  - 1 corner: 0 points
  - 0 corners: 0 points

**Alternative (Simpler) Scoring**:
- +1 point per corner stone you have in each area
- Areas are worth 0-4 points, split proportionally

### Win Condition
- Game ends when board is full (25 placements) OR after N turns (e.g., 30)
- **Highest cumulative score wins**

### Worked Example (Turn 5)
```
Board state:     Areas affected:
  A B C D E
1 B . W . .      Area A1-B2 has: B,·,·,· = Black +1
2 . . . . .      Area B1-C2 has: ·,W,·,· = White +1
3 . W . B .      Area B2-C3 has: ·,·,W,· = White +1
4 . . . . .      Area C3-D4 has: W,·,B,· = Both +1
5 . . . . .      (etc for all 16 areas)
```
Scores recalculated FRESH each turn.

---

## 2. GAME EXPERIENCE ANALYSIS

### Feel vs. Permanent Claiming

| Aspect | Permanent Claiming | Rolling Score |
|--------|-------------------|---------------|
| **Tension** | Decisive moments | Sustained pressure |
| **Mistakes** | Can be fatal | Recoverable |
| **Pacing** | Front-loaded drama | Even throughout |
| **Emotion** | "I lost that area!" | "I'm behind but gaining" |

**Rolling score creates a marathon feel** rather than a sprint. Each turn matters equally late-game. No "locked in" regions—the board remains fluid.

### Emergent Strategies

**1. Sustained Control vs. Opportunistic Grabbing**
- **Sustained Control**: Place stones to maintain presence in high-value areas turn after turn. Compound interest effect—3 turns of +4 beats one turn of +6.
- **Opportunistic**: Target areas opponent neglected THIS turn. Snipe points in "dead" regions they've abandoned.

**2. Area Overlap Exploitation**
Each non-edge cell participates in 1-4 areas:
- Center cells (4 areas) → highest leverage
- Edge cells (2 areas) → moderate
- Corner cells (1 area) → lowest

**Strategy emerges**: Central placement offers more scoring surfaces but spreads thin. Corner placement offers concentrated control.

**3. Tempo Dynamics**
Since you place one stone per turn, opponent responds. Key question: do you reinforce existing areas (defensive, compound scoring) or expand to new areas (offensive, spread scoring)?

**4. Denial Play**
Worth placing a stone ONLY to deny opponent 3+ points, even if you gain 0-1. This creates interesting sacrifice calculations.

### Score Arc Feel

```
Score over time (typical game):

     ^
     |           ____----
     |      ___--        Black
     |   __-
     |  -        ____----
     |      ___--        White
     | __--
     |/
     +-----------------------> Turn
      5   10   15   20   25

Scores accelerate as board fills (more stones = more area corners occupied).
Early game: Low scoring, positioning
Mid game: Scoring ramps, lead develops
Late game: Each placement swings multiple points
```

### Comeback Potential

**MODERATE-HIGH comeback potential**:
- No locked territory means trailing player can always contest
- Late-game placements worth more (board is denser)
- However: cumulative score means early lead has "banked" points
- Key insight: A 20-point lead with 10 turns left is surmountable if you can outscore by 2+/turn

**Anti-snowball mechanic**: The board gets tighter, limiting where leader can extend advantage. Follower can exploit remaining gaps.

---

## 3. AI TRACTABILITY ANALYSIS

### State Evaluation Complexity

**Permanent claiming**: Binary ownership per area. Simple to evaluate.

**Rolling score**: Need to track:
1. Current cumulative scores (2 integers)
2. Board position (25 cells, 3 states each = 3^25 max states)
3. **Predicted future scoring** from current position

The challenge: evaluating a position requires estimating how many points it will generate over remaining turns, not just current turn.

### Heuristic Construction

**Easier aspects**:
- Point calculation is deterministic (no probability)
- Current turn's score is trivially computable
- Clear objective function (maximize score delta)

**Harder aspects**:
- Future value estimation: "This stone will score +3/turn for next 8 turns"
- Diminishing returns: Areas near full have limited growth potential
- Opponent modeling: Where will they place to maximize THEIR future flow?

**Candidate Heuristics**:
```python
def position_value(board, player):
    current_score = calculate_immediate_score(board)

    # Heuristic: value uncontested areas higher
    area_potential = sum(
        future_multiplier(area, turns_remaining)
        for area in areas_where_player_leads(board, player)
    )

    # Heuristic: central placement bonus
    positional_value = sum(
        centrality_weight(cell)
        for cell in player_stones(board)
    )

    return current_score + area_potential + positional_value
```

### Expected Value Centrality

**YES, expected value is more central** than in permanent claiming:
- Each placement has a clear EV: sum of (probability of reaching state × score in that state)
- Since scoring is deterministic, EV calculation is straightforward given opponent model
- The game resembles **repeated auctions** where you bid placement turns for point streams

**Minimax depth considerations**:
- Branching factor: ~20 average (empty cells)
- Need deeper lookahead to see point accumulation effects
- Alpha-beta pruning remains effective
- Transposition tables help (many paths to same board state)

### AI Tractability Rating

Rolling score is **MODERATELY AI-FRIENDLY**:
- Clear objective (maximize score differential)
- Deterministic scoring (no luck)
- But: requires multi-turn horizon thinking
- Heuristics need temporal discounting

---

## 4. COMPARISON TO BASE (PERMANENT CLAIMING)

### What Rolling Score ADDS

| Addition | Description |
|----------|-------------|
| **Dynamism** | Board never "settles"—every turn matters equally |
| **Comeback paths** | Trailing player always has avenues |
| **Score legibility** | Players always know exact standing |
| **Compound strategy** | "Investment" thinking—stones pay dividends over time |
| **Reduced kingmaking** | In 3+ player variant, less incentive to attack leader |

### What Rolling Score LOSES

| Loss | Description |
|------|-------------|
| **Decisive moments** | No "I just won that corner" drama |
| **Simplicity** | Must track cumulative score, not just board state |
| **Territorial instinct** | Less visceral "this is MINE" feeling |
| **Clear midgame evaluation** | Harder to see who's winning at a glance |
| **Closure** | Areas never feel "finished" |

### Strategic Texture Comparison

**Permanent claiming** → Go-like. Corners die, center matters early, then game closes region by region. Reading focuses on "can I capture this area?"

**Rolling score** → Stock-market-like. Positions have ongoing yield. Reading focuses on "what's my income rate vs. opponent?" Each stone is an asset generating returns.

---

## 5. RATINGS

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Elegance** | 7/10 | Simple rules, but score tracking adds overhead. Core mechanic (place stone, score areas) is clean. Loses points for needing cumulative bookkeeping. |
| **Strategic Depth** | 8/10 | Rich temporal dynamics. Compound scoring creates investment-style thinking. Area overlap creates interesting placement decisions. Loses point for potentially becoming "optimize the spreadsheet." |
| **AI-Friendliness** | 7/10 | Deterministic, clear objective. But requires multi-turn lookahead to evaluate properly. Heuristics are constructible but non-trivial. Better than games with hidden information or heavy randomness. |

---

## 6. DESIGN VERDICT

**Rolling score transforms the game from "capture territory" to "maximize yield."**

Best suited for players who enjoy:
- Economic/engine-building games
- Optimization puzzles
- Games where every turn feels meaningful
- Comeback-friendly competition

Less suited for players who want:
- Clear territorial ownership
- Dramatic swing moments
- Simple "I'm winning/losing" assessment
- The satisfaction of closing out regions

**Recommendation**: This variant works well for a shorter format (15-20 turns) where the score acceleration creates a natural climax. For longer games, consider adding midgame scoring bonuses or area "maturity" mechanics to maintain tension.

---

## 7. VARIANT EXTENSIONS (Optional)

**7a. Decay Scoring**: Recent turns worth more (turn 20 scores count double). Adds comeback potential.

**7b. Area Maturity**: Areas you've led for 3+ consecutive turns give bonus points. Rewards sustained control.

**7c. Threshold Scoring**: Only score areas where you have 2+ stones. Raises the bar for "contested."

**7d. Score Visibility Toggle**: Hidden scores until endgame. Changes information dynamics dramatically.

---

*Design sketch created for ATTENTION+INFLUENCE exploration.*
*Variant: Rolling Score | Status: Concept Complete*
