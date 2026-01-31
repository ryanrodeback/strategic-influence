# Strategic Influence - AI Agents Documentation

## Overview

Strategic Influence includes multiple AI agents with different strategies, strengths, and weaknesses. Each agent implements the `Agent` protocol:

```python
class Agent(Protocol):
    @property
    def name(self) -> str: ...
    def reset(self) -> None: ...
    def choose_setup(state, player, config) -> SetupAction: ...
    def choose_actions(state, player, config) -> PlayerTurnActions: ...
```

## Agent Comparison Table

| Agent | Strategy | Speed | Strength | Best Against |
|-------|----------|-------|----------|--------------|
| **RandomAgent** | Random | Very Fast | Weak | N/A (baseline) |
| **GreedyStrategicAgent** | Heuristic scoring | Very Fast | Strong | Weak agents |
| **DefensiveAgent** | Defense-focused | Very Fast | Moderate | Aggressive agents |
| **AggressiveAgent** | Attack-focused | Very Fast | Moderate | Defensive agents |
| **IntuitionAgent** | Growth-first | Very Fast | Moderate | Balanced agents |
| **MinimaxAgent** | Game tree search | Slow | Strongest* | All (but slow) |
| **OptimizedMinimaxAgent** | Fast minimax | Medium | Strong | Heuristic agents |
| **ImprovedMCTSAgent** | Monte Carlo search | Medium | Strong | Tactical agents |

*Minimax is strongest but too slow for practical use (20s+ per move).

## Detailed Agent Descriptions

### RandomAgent

**Location**: `agents/random_agent.py`

**Strategy**: Makes completely random valid moves.

**How it works**:
```
For each owned territory:
    1. Generate all valid moves
    2. Pick one at random
    3. (GROW or MOVE in random direction)
```

**Setup**: Picks random position in setup zone.

**Strengths**:
- Unpredictable (can upset stronger agents by luck)
- Very fast (baseline for benchmarking)
- Good for testing

**Weaknesses**:
- No strategic understanding
- Loses to any semi-competent agent
- Not useful for learning

**Best used for**:
- Baseline comparison
- Testing game engine
- Stress testing with randomness

**Tuning**:
- `seed`: For reproducibility

### GreedyStrategicAgent

**Location**: `agents/greedy_strategic_agent.py`

**Strategy**: Fast heuristic that encodes strategic knowledge without search.

**How it works**:

1. **For each territory**, considers these options:
   - STAY (grow): Score = 10.0
   - SEND_HALF to neutral neighbor: Score based on neutral neighbor's future potential
   - SEND_ALL/SEND_HALF to enemy: Score based on combat advantage
   - Reinforce friendly threatened neighbor: Score if it saves territory

2. **Scoring logic**:
   - Neutral expansion: `200 + (neutral_neighbors * 30)` (more expansion options = better)
   - Enemy attack: `100` if half wins, `90` if all wins
   - Friendly defense: `80` if reinforcement resolves threat
   - STAY (fallback): `10`

3. **Decision**: Pick highest-scored option per territory

**Setup**: Prefer positions near center with many neighbors.

**Strengths**:
- Encodes real strategic insights (without search overhead)
- Very fast (~1ms per move)
- Strong against weak agents
- Transparent decision-making (easy to understand)

**Weaknesses**:
- No lookahead (can't predict multi-turn consequences)
- Greedy (doesn't sacrifice now for future gain)
- Vulnerable to prepared opponents
- Simple heuristic (easy to exploit patterns)

**Example decisions**:
```
Territory with 4 stones in open area:
- GROW: 10
- SEND to neutral with 3 neighbors: 200 + 90 = 290 (CHOOSE THIS)
- SEND to enemy with 2 stones: 100 (win half)

Territory with 3 stones next to threat:
- GROW: 10
- REINFORCE friendly (3+2 stones): 80 (CHOOSE THIS)
- Other moves: < 80
```

**Best used for**:
- Quick games
- Benchmarking against
- Understanding what "obvious" moves are
- Rapid testing

**Tuning**:
- `seed`: For reproducibility

### DefensiveAgent

**Location**: `agents/defensive_agent.py`

**Strategy**: Prioritizes safety and consolidation over expansion.

**Core principles**:
1. **Defend threatened territories**: If enemy can attack, reinforce or retreat
2. **Only expand when safe**: 2-3 stones minimum for expansion
3. **Grow strong positions**: Stack stones for overwhelming defense
4. **Avoid risky combat**: Only attack when clear advantage

**Decision algorithm**:

```
For each territory:
    1. Check if threatened (enemy neighbor with more stones)
    2. If threatened:
        a. Try to defend (reinforce with friendly neighbor)
        b. If can't defend, consider retreating
    3. If not threatened:
        a. If territory is weak (1-2 stones): GROW
        b. If territory is strong (3+) and safe: Consider expansion
        c. Expansion only to neutral with 2-3 stones minimum
    4. Otherwise: GROW
```

**Setup**: Cautious position selection, prefers solid flanking positions.

**Strengths**:
- Very defensive (good for learning to play safely)
- Preserves territories well
- Hard to break through (strong turtle defense)
- Stable win rate against varied opponents

**Weaknesses**:
- Too passive (misses expansion opportunities)
- Slow territory acquisition
- Can lose to patient aggressive players
- Vulnerable to being surrounded

**Example decisions**:
```
Territory with 2 stones, neighbor has 3 (threatened):
- Defend: SEND_HALF to friendly that will reinforce = HIGH PRIORITY
- If can't defend: GROW (accept loss of territory)
- Never: Attack the superior enemy

Territory with 4 stones, surrounded by neutrals:
- GROW: Safe, builds strength
- Expand: Only if absolutely safe (2-3 stones minimum)
```

**Best used for**:
- Learning safe play
- Playing against aggressive opponents
- Testing defensive scenarios
- Turtle strategy implementation

**Tuning**:
- `seed`: For reproducibility
- Consider different threat thresholds

### AggressiveAgent

**Location**: `agents/aggressive_agent.py`

**Strategy**: Prioritizes territorial expansion and combat over consolidation.

**Core principles**:
1. **Attack enemy constantly**: Any advantage is attacked
2. **Expand to neutral**: Don't wait for perfect safety
3. **Pressure the board**: Control more territory
4. **Trade blows**: Willing to take losses for position

**Decision algorithm**:

```
For each territory:
    1. If can attack enemy with advantage: ATTACK (high priority)
    2. If can expand to neutral: EXPAND (medium priority)
    3. Otherwise: GROW (low priority)
```

**Setup**: Aggressive position selection, pushes toward center quickly.

**Strengths**:
- Gains territory quickly
- Creates constant pressure
- Forces opponent into reactive play
- Can overwhelm passive opponents

**Weaknesses**:
- Over-commits to expansion
- Loses many battles (even attacking ones)
- Vulnerable to being counter-attacked
- High casualty rate

**Example decisions**:
```
Territory with 2 stones, neighbor has 1 (advantage):
- SEND_ALL to attack = HIGH PRIORITY

Territory with 2 stones, neutral neighbor available:
- SEND_HALF to expand = MEDIUM PRIORITY

Otherwise:
- GROW = DEFAULT
```

**Best used for**:
- Learning aggressive play
- Tournament testing
- Playing against defensive opponents
- Rush strategy experimentation

**Tuning**:
- `seed`: For reproducibility
- Adjust minimum stone advantage threshold

### IntuitionAgent

**Location**: `agents/intuition_agent.py`

**Strategy**: Combines multiple strategic principles into weighted decision-making.

**Core approach**:
Uses the evaluation function with `INTUITION_WEIGHTS` that emphasizes:
- Growth potential (very high weight)
- Expansion opportunities (if safe enough)
- Threat awareness (medium weight)
- Territory connectivity (moderate weight)

**Decision algorithm**:

```
For each territory:
    1. Evaluate all possible moves:
        - GROW: Score based on growth potential
        - MOVE to neighbor: Score based on outcome type

    2. Scoring factors:
        - Growth potential: How many stones territory will gain
        - Expansion safety: Likelihood of success
        - Threat resolution: Does this move help defense
        - Connectivity: Can this merge with allied forces

    3. Pick highest-scored option
```

**Setup**: Similar to GreedyStrategic, prefer strong center positions.

**Strengths**:
- Balanced approach (growth + expansion + defense)
- Transparent scoring (weights are clear)
- Decent against varied opponents
- Good teaching tool (shows multi-factor decision making)

**Weaknesses**:
- Still no lookahead (doesn't plan multi-turn sequences)
- Weights may not be optimal for all situations
- Less specialized than focused agents
- Vulnerable to meta-strategies

**Example decisions**:
```
Territory with 2 stones, multiple options:
- GROW: Score = growth_potential + threat_penalty
- EXPAND to neutral: Score = expansion_opportunity + center_control
- REINFORCE friend: Score = threat_resolution + connectivity

Pick option with highest total score.
```

**Best used for**:
- Learning decision-making diversity
- Testing evaluation function changes
- Balanced play
- Educational purposes

**Tuning**:
- Modify `INTUITION_WEIGHTS` to change priorities
- Experiment with weight ratios
- Test different configurations

### MinimaxAgent

**Location**: `agents/minimax_agent.py`

**Strategy**: Game tree search with alpha-beta pruning and "paranoid" simultaneous move handling.

**How it works**:

1. **Search depth**: Look ahead N turns (default 2)
2. **Move generation**: For each territory, generate 3-9 options (STAY, SEND_HALF, SEND_ALL per neighbor)
3. **Evaluation**: Use board evaluation function at leaf nodes
4. **Paranoid search**: Assume opponent sees our move and plays optimal counter

**Pseudocode**:
```
function minimax(state, depth, is_our_turn):
    if depth == 0:
        return evaluate(state)

    if is_our_turn:
        best_score = -infinity
        for our_move in generate_moves(state, OUR_PLAYER):
            opponent_response = minimax(after_move, depth-1, false)
            best_score = max(best_score, opponent_response)
        return best_score
    else:
        best_score = +infinity
        for opponent_move in generate_moves(state, OPPONENT):
            future = minimax(after_move, depth-1, true)
            best_score = min(best_score, future)
        return best_score
```

**Setup**: Prefer central positions with many strategic options.

**Strengths**:
- Strongest agent (look-ahead finds best moves)
- Plans multi-turn strategies
- Adapts to opponent play
- Handles complex situations well

**Weaknesses**:
- Very slow (~20s per territory at depth 2)
- Impractical for 3+ territories
- Search space explodes with more territories
- Limited by evaluation function quality

**Performance**:
- Depth 1: ~100ms (too shallow)
- Depth 2: ~5-20s per move (practical for 1-2 territories)
- Depth 3: ~minutes (impractical)
- With move limiting: Can reduce by 50-70%

**Best used for**:
- Single-territory endgames
- Strong opponent for testing
- Tournament finals (if time permits)
- Understanding optimal play

**Tuning**:
```python
MinimaxAgent(
    seed=42,
    max_depth=2,           # Depth of search (1-3 practical)
    max_moves=20,          # Limit moves per position
    weights=BALANCED_WEIGHTS,  # Evaluation function
    verbose=True           # Print search statistics
)
```

**Search statistics** (if verbose=True):
```
Nodes searched: 45,200
Nodes pruned: 12,000
Search time: 18.5s
```

### OptimizedMinimaxAgent

**Location**: `agents/optimized_minimax_agent.py`

**Strategy**: Faster minimax variant with move ordering and better pruning.

**Improvements over MinimaxAgent**:
1. **Move ordering**: Evaluate most promising moves first (better pruning)
2. **Iterative deepening**: Time-bounded search (stop when time runs out)
3. **Transposition table**: Cache evaluated positions
4. **Move limits**: Sample moves instead of exploring all

**Performance**:
- Roughly 2-3x faster than basic minimax
- Can handle 2-3 territories at depth 2
- Good balance of strength and speed

**Best used for**:
- Practical game play (faster than pure minimax)
- Tournaments with time limits
- Medium complexity positions

**Tuning**:
```python
OptimizedMinimaxAgent(
    seed=42,
    max_depth=2,
    max_time_seconds=5.0,  # Stop after 5 seconds
    max_moves=20,
)
```

### ImprovedMCTSAgent

**Location**: `agents/improved_mcts_agent.py`

**Strategy**: Monte Carlo Tree Search - play out random games to evaluate positions.

**How it works**:

1. **Selection**: Navigate tree based on UCB formula (balance exploration vs. exploitation)
2. **Expansion**: Add new node to tree
3. **Simulation**: Play out random game from new position
4. **Backpropagation**: Update statistics with result

**Pseudocode**:
```
for each iteration (time-bounded):
    node = select_best_child(root, UCB)
    if node not fully expanded:
        node = expand(node)
    result = simulate_random_game(node)
    backprop(node, result)

return child with best win rate
```

**Setup**: Reasonable heuristic, not specialized.

**Strengths**:
- Better than minimax at partial information (good for exploration)
- Scales better (can handle more territories)
- Adapts with more iterations (anytime algorithm)
- Practical speed (2-5s for reasonable iteration count)

**Weaknesses**:
- Requires many iterations to be strong
- Depends on simulation quality (bad playouts = bad decisions)
- Less guaranteed optimal than minimax
- Harder to tune (iterations vs. search time)

**Performance**:
- 100 iterations: ~0.5-1s (weak)
- 1000 iterations: ~5-10s (moderate)
- 10000 iterations: ~50-100s (strong but slow)

**Best used for**:
- Exploration-heavy scenarios
- Learning to try unexpected moves
- Good balance agent for tournaments
- Positions with many options

**Tuning**:
```python
ImprovedMCTSAgent(
    seed=42,
    num_iterations=1000,   # 1000 playouts
    exploration_c=1.414,   # UCB exploration constant
    max_depth=20,          # Max depth per simulation
)
```

## Evaluation Function

All heuristic agents use the board evaluation function from `evaluation.py`:

```python
def evaluate_board(board: TerritoryBoard, player: Owner, weights: EvaluationWeights) -> float:
```

**Factors evaluated**:
- `territory_count`: Number of territories (most important)
- `stone_advantage`: Your stones vs opponent stones
- `growth_potential`: Stones you'll gain if territories GROW
- `expansion_opportunity`: Count of neutral neighbors
- `center_control`: Control of board center
- `attack_opportunity`: Count of attackable enemies
- `threatened_penalty`: Count of threatened territories (subtracted)
- `connectivity`: How connected your territories are
- `merge_potential`: Ability to merge forces back together

**Weight presets**:

```python
BALANCED_WEIGHTS          # Default balanced
AGGRESSIVE_WEIGHTS        # Attack-focused
DEFENSIVE_WEIGHTS         # Defense-focused
INTUITION_WEIGHTS         # Growth-first, threat-aware
GROWTH_FIRST_MODERATE     # Experimental growth focus
```

## Using Agents

### In Code

```python
from strategic_influence.agents import GreedyStrategicAgent, MinimaxAgent

agent1 = GreedyStrategicAgent(seed=42)
agent2 = MinimaxAgent(max_depth=2, seed=43)

from strategic_influence.engine import simulate_game
from strategic_influence.config import create_default_config

config = create_default_config()
final_state = simulate_game(config, agent1, agent2, seed=100)
```

### From CLI

```bash
# Watch two agents play
strategic-influence watch --p1 greedy --p2 minimax

# Run tournament
strategic-influence tournament --agents greedy defensive random minimax

# Benchmark agent performance
python benchmark_agents.py
```

## Comparison Strategies

### How to Compare Agents

1. **Head-to-head games**: Agent1 vs Agent2 (run multiple, alternating colors)
2. **Round-robin**: All agents play each other
3. **Win rate**: Track wins/losses
4. **Territory differential**: Count final territories
5. **Statistical significance**: Need ~10-20 games per matchup

### Interpreting Results

```
GreedyStrategic vs Defensive (10 games):
- GreedyStrategic wins: 7 (70%)
- Defensive wins: 2 (20%)
- Draws: 1 (10%)

Conclusion: GreedyStrategic has advantage against defensive play
(likely due to constant pressure)
```

## Creating Custom Agents

### Template

```python
from strategic_influence.types import Owner, GameState, SetupAction, PlayerTurnActions
from strategic_influence.config import GameConfig

class MyCustomAgent:
    def __init__(self, seed: int | None = None):
        self._initial_seed = seed

    @property
    def name(self) -> str:
        return "MyCustom"

    def reset(self) -> None:
        # Reset any internal state for new game
        pass

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        # Place initial stone in setup zone
        board_size = config.board_size
        # ... logic to choose position ...
        return SetupAction(player=player, position=chosen_position)

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        actions = []
        for pos in state.board.positions_owned_by(player):
            # Decide: GROW or MOVE to which neighbor
            action = self._choose_action_for_territory(pos, state, player, config)
            actions.append(action)
        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _choose_action_for_territory(self, pos, state, player, config):
        # Your logic here
        pass
```

### Adding to CLI

1. Create agent class in `agents/my_agent.py`
2. Add import to `agents/__init__.py`
3. Add case to `cli/app.py` in `get_agent()` function
4. Add tests in `tests/unit/test_agents.py`

## Agent Performance Notes

### Reliability

All agents are deterministic with seeding:
- Same seed = same moves
- Good for testing and reproducibility
- Good for tournaments (fair play)

### Strength Progression

For learning:
1. Start with **GreedyStrategic** (fast, reasonable)
2. Try **DefensiveAgent** (learn to be safe)
3. Try **AggressiveAgent** (learn to push)
4. Try **MinimaxAgent** (learn optimal play - if you can wait)

### Tournament Recommendations

- **Quick games (< 1 minute)**: RandomAgent, GreedyStrategic, Defensive, Aggressive, Intuition
- **Medium games (< 10 seconds)**: ImprovedMCTS, OptimizedMinimax
- **Serious games**: MinimaxAgent (if you can wait 20s+ per move)

## Future Agent Improvements

Potential enhancements:
1. **Neural network evaluation**: Learn weights from data
2. **Better MCTS**: UCT improvements, RAVE, etc.
3. **Opening book**: Pre-computed strong opening sequences
4. **Endgame tablebases**: Perfect play in endgame
5. **Multi-agent learning**: Train agents against each other
