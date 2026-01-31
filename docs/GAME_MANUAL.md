# Strategic Influence - Game Manual

## Overview

Strategic Influence is a turn-based territorial strategy game for two players on a 5x5 grid. Players compete to control the most territory by growing their forces and conquering enemy positions. The core design centers on **stone count** as the resource, with mechanics that reward both growth and tactical aggression.

**Winning condition**: After **20 turns**, the player controlling the most **territories** (intersections) wins.

## Game Phases

### Phase 1: Setup (2 turns total)
Both players place their initial stones one at a time:
- Each player places **1 stone** with **3 stones per placement**
- Player 1 (White) places in their setup zone
- Player 2 (Black) places in their setup zone
- Setup zones are designed to be asymmetric but balanced (left vs. right side)

### Phase 2: Main Game (20 turns)
Players simultaneously choose actions for each territory they control, then all actions resolve in a fixed order.

### Phase 3: Game Over
After 20 turns, territory count is tallied. Winner is the player with more territories (or draw).

## Board Layout

The 5x5 board uses **Go-style notation**:
- Coordinates: Rows 0-4 (bottom to top), Columns 0-4 (left to right)
- Labeled: Rows "1-5", Columns "A-E"
- Example: Position (2, 2) = C3 (center)

### Player Setup Zones

**Player 1 (White)**: Left side
- Columns A-B (columns 0-1)
- Plus rows 0-1 of column C (center column, bottom part)
- Center C3 (2,2) is FORBIDDEN

**Player 2 (Black)**: Right side
- Columns D-E (columns 3-4)
- Plus rows 3-4 of column C (center column, top part)
- Center C3 (2,2) is FORBIDDEN

This asymmetry encourages different strategic approaches but remains balanced.

## Core Mechanics

### Territories and Stone Count

A **territory** is an intersection on the board with:
- **Owner**: One of NEUTRAL, PLAYER_1 (White), PLAYER_2 (Black)
- **Stone count**: Integer >= 0 (represents control strength)

**Key insight**:
- Higher stone count = stronger in combat, safer in expansion
- Territory count (not stone count) determines victory
- This creates tension between depth (stones) and breadth (territories)

### Stones

Stones represent control strength. Each territory you own has 1+ stones:
- 1 stone = weak territory (loses to larger forces)
- 5+ stones = strong territory (likely to win combat)
- Maximum: 10 stones per territory (growth stops)

### Territory Actions

Each turn, for **every territory you control**, you must choose exactly one action:

#### Action 1: GROW (Stay)
- Stones stay in place
- Territory gains +1 stone (up to the maximum)
- No movement, no combat, no risk
- Good for: building strength, defending, consolidating

#### Action 2: MOVE (Send Stones)
- Stones leave the territory and move to adjacent positions
- If some stones stay behind, that territory still GROWS at turn end
- Territory may be abandoned if all stones leave
- Movement may resolve as:
  - **Reinforcement** (to friendly territory): Always succeeds
  - **Expansion** (to neutral territory): 50% success per stone
  - **Attack** (to enemy territory): Combat is resolved

### Movement Mechanics

**Adjacency**: Stones can only move to orthogonally adjacent positions:
- Up (row +1)
- Down (row -1)
- Left (col -1)
- Right (col +1)

Diagonal movement is NOT allowed.

**Split Movement**: You can split stones from a single territory in multiple directions:
- Send 2 stones up and 1 stone left from the same position
- Each destination is a separate "movement" resolved independently
- This is the key tactical depth of the game

**Stone Limits**:
- You can send all stones (territory becomes neutral after resolution)
- You can send some stones (territory keeps remainder, which grows)
- You cannot send more stones than you have
- Destinations must be adjacent

### Expansion (Into Neutral Territory)

When your stones move into an unoccupied (neutral) territory:

**Resolution**:
- Each stone has a 50% independent chance of success
- **If ANY stone succeeds**: All stones claim the territory (success)
- **If ALL stones fail**: All stones are lost (failure)

**Examples**:
- 1 stone: 50% success, 50% lose the stone
- 2 stones: 75% success (only if both fail = lose both), 25% lose both
- 3 stones: 87.5% success, 12.5% all lost
- 4+ stones: 93%+ success

**Strategic implications**:
- Committing more stones = higher success rate
- Single-stone expansion is high-risk
- Spreading force thin across many expansions is dangerous
- Patience (growing first) reduces risk

### Reinforcement (Into Friendly Territory)

When your stones move into your own territory:
- Movement always succeeds
- Stones are added to the target territory
- Simple accumulation of strength
- No combat, no risk

### Combat (Against Enemy Territory)

When your stones attack an enemy territory:

**Combat Resolution** (simultaneous defender rolls):
1. **Defender rolls first**: 50% chance to eliminate 1 attacker stone
2. **Attacker rolls**: 50% chance to eliminate 1 defender stone
3. **Alternate**: Continue until one side has 0 stones
4. **Combat outcome**:
   - **Attacker Wins**: Surviving attackers claim the territory
   - **Defender Holds**: Survivors stay in territory; attackers are lost
   - **Mutual Destruction**: Both sides eliminated; territory becomes neutral

**Combat Examples**:

Example 1: 3 Attackers vs 1 Defender
```
Round 1: Defender rolls (50% to hit) - say HITS
  Attackers: 2 remaining
Round 2: Attacker rolls (50% to hit) - say HITS
  Defenders: 0 remaining
RESULT: Attackers win with 2 survivors
```

Example 2: 2 Attackers vs 2 Defenders
```
Round 1: Defender rolls - say MISS
Round 2: Attacker rolls - say HIT
  Defenders: 1 remaining
Round 3: Defender rolls - say HIT
  Attackers: 1 remaining
Round 4: Attacker rolls - say MISS
Round 5: Defender rolls - say HIT
  Attackers: 0 remaining
RESULT: Defender holds with 1 survivor
```

**Strategic implications**:
- Higher stone count = higher combat probability
- 1v1 is pure coin flip
- 2v1 gives attacker advantage
- 3v2 gives attacker strong advantage
- Combat is risky, but necessary for expansion

### Growth

After all movement and combat resolves, territories that:
- Chose GROW action, OR
- Had any stones remain in place during a move action

...gain **+1 stone** at the end of the turn.

**Growth stops at maximum** (typically 10 stones per territory).

## Turn Resolution Order

To understand simultaneous movement with clear resolution:

1. **Departure Phase**: All stones leave their source territories simultaneously
   - Deduct from all source territories
   - Sources with all stones leaving become neutral

2. **Reinforcement Phase**: Friendly reinforcements arrive
   - Stones moving to your own territory are added
   - Always succeeds, can't fail

3. **Expansion Phase**: Neutral territory expansion attempts
   - Each expansion rolls independently
   - If any stone succeeds, the territory is claimed
   - If all fail, all stones sent to that territory are lost

4. **Attack Phase**: Enemy territory combat
   - Combat rolls happen (defender rolls first, then alternates)
   - Winners claim the territory

5. **Growth Phase**: Territories that grew gain stones
   - All territories that didn't move (or partially moved) gain +1 stone

This order ensures:
- True simultaneous movement (all depart at same time)
- Predictable combat (no chain reactions)
- Growth is always last (no interaction with combat)

## Scoring and Winning

### Determining the Winner
After 20 turns, count the territories each player controls:
- **More territories** = Win
- **Equal territories** = Draw
- **Fewer territories** = Loss

**Not based on stone count**, only territory count. This is crucial:
- A player can have many stones but lose if spread across few territories
- A player can win with fewer total stones if controlling more territories

### Example End Game
```
Player 1: 14 territories (37 stones)
Player 2: 11 territories (45 stones)
Result: Player 1 wins (more territories)
```

## Strategic Concepts

### Depth vs. Breadth

The core tension:
- **Growth (Depth)**: Make fewer territories very strong
  - Safer expansion (more stones = higher success)
  - Stronger combat position
  - But slower territory acquisition

- **Expansion (Breadth)**: Control more territories with fewer stones each
  - Fast territory acquisition
  - But risky single-stone expansion
  - Vulnerable to attack

### Board Control Zones

Different areas of the board have different strategic values:
- **Center (column C, rows 2-4)**: High connectivity, many expansion options
- **Flanks (columns A, B vs D, E)**: Less flexible, more isolated
- **Edges**: Restricted to 2-3 neighbors, bottleneck positions

### Threat Assessment

Key concepts for planning:
- **Threatened territory**: Neighbor territory has more stones
- **Defended territory**: Friendly neighbor can reinforce quickly
- **Isolated territory**: Far from friendly support
- **Expansion opportunity**: Neutral territory adjacent to your strength

### Common Patterns

#### The Greedy Expand
- GROW for a few turns to accumulate stones
- SEND with majority to safe neutral territory
- Quick territory gain, but requires careful sequencing

#### The Fortified Defense
- Keep territories strong (5+ stones)
- Only expand when overwhelming advantage
- Reactive play, depends on opponent mistakes

#### The Aggressive Attack
- Hunt down weak enemy territories
- Accept some losses to break enemy control
- Requires risk tolerance and reading opponent

## Controls and Interface

### CLI Commands

Basic game play:
```bash
# Watch two AI agents play
strategic-influence watch --p1 greedy --p2 defensive

# Play a single game
strategic-influence play --opponent greedy --seed 42

# Run a tournament
strategic-influence tournament --agents greedy defensive random
```

### Configuration

Game parameters can be adjusted via YAML configuration:
- Board size
- Number of turns
- Combat hit chance
- Growth per turn
- Maximum stones per territory
- Expansion success rate

See `DEVELOPMENT.md` for configuration details.

## Common Questions

### Why do we count territories, not stones?
Stone count is too easy to manipulate. Territory count rewards **actual control** - you must hold land to win.

### Why is expansion risky?
Risk creates interesting decisions: Do I play it safe and grow, or risk single-stone expansion for quick territory grab? The game is more interesting with this tension.

### What if I run out of territories to move from?
If all your territories have all stones leaving (empty territories), you lose those positions. Plan carefully to maintain some GROW actions to preserve territory.

### Can I move to a diagonal position?
No, only orthogonal (up/down/left/right) movement is allowed. This limits movement to 4 adjacent positions per territory.

### What happens if both players have same territory count?
Draw - the game ends in a tie. Both players should play for win, not draw.

### Is there a best strategy?
Not exactly. The game is balanced so that different strategies can win depending on execution and opponent play. Greedy expansion beats strong defense if it's fast enough, but strong defense beats greedy expansion if the expansions fail.

## Advanced Notes

### Immutability and Reproducibility

The game engine is built with immutable data structures:
- Every action returns a new game state (doesn't modify the original)
- This enables:
  - Deterministic replay (same seed = same game)
  - Simulation for AI lookahead
  - Parallel game execution without race conditions

### RNG (Random Number Generator)

Randomness comes from:
- **Expansion rolls**: 50% per stone
- **Combat rolls**: 50% per hit
- Both use the seeded RNG for reproducibility

With the same seed, the exact same sequence of rolls happens, making games replayable.

### Performance Notes

- Full 20-turn game: ~100ms with random agents
- Minimax depth-2 search: ~20 seconds per turn (2-3 territories)
- Greedy heuristic: ~1ms per turn (no lookahead)
