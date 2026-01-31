# Strategic Influence - AI Agents Documentation

## Overview

Strategic Influence includes tournament-proven AI agents with different strategies. Each agent implements the `Agent` protocol:

```python
class Agent(Protocol):
    @property
    def name(self) -> str: ...
    def reset(self) -> None: ...
    def choose_setup(state, player, config) -> SetupAction: ...
    def choose_actions(state, player, config) -> PlayerTurnActions: ...
```

## Agent Comparison Table

Based on a comprehensive 280-game tournament (January 2026):

| Rank | Agent | Win Rate | Speed | Recommended Use |
|------|-------|----------|-------|-----------------|
| 1 | **OptimizedMinimaxAgent(d=1)** | **100%** | 1.75s/game | Best overall performance |
| 2 | **GreedyStrategicAgent** | 78.6% | <0.1s/game | Fast alternative |
| 3 | **ImprovedMCTSAgent** | 42.9% | 4s/game | Research only |
| 4 | RandomAgent | 0% | instant | Baseline only |

## Recommended Agents

### 1. OptimizedMinimaxAgent (CHAMPION)

**Location**: `agents/optimized_minimax_agent.py`

**Tournament Results**: 100% win rate (70-0-0), undefeated

**Strategy**: Game tree search with alpha-beta pruning at depth 1.

**How it works**:
1. Generate limited candidate moves (4 best per territory)
2. For each move, simulate opponent's best response
3. Pick move with best worst-case outcome

**Why depth=1 is optimal**:
- Depth-2 search takes 6x longer but performs worse (loses 10-0 to depth-1)
- The game's stochastic nature limits value of deep search
- Move limiting + 1-ply lookahead captures most tactical patterns

**Usage**:
```python
from strategic_influence.agents import OptimizedMinimaxAgent

agent = OptimizedMinimaxAgent(
    seed=42,
    max_depth=1,           # Optimal depth
    max_moves=8,           # Moves to consider
    time_limit_sec=5.0,    # Safety limit
)
```

**Best for**:
- Competitive play
- Tournament finals
- Strongest possible AI

### 2. GreedyStrategicAgent (FAST)

**Location**: `agents/greedy_strategic_agent.py`

**Tournament Results**: 78.6% win rate, instant speed

**Strategy**: Fast heuristic scoring without search.

**How it works**:
For each territory, score all options:
- STAY (grow): Score = 10
- SEND_HALF to neutral: Score = 200 + (neutral_neighbors * 30)
- Attack enemy with advantage: Score = 100 (half wins) or 90 (all wins)
- Reinforce threatened ally: Score = 80

Pick highest-scored option.

**Usage**:
```python
from strategic_influence.agents import GreedyStrategicAgent

agent = GreedyStrategicAgent(seed=42)
```

**Best for**:
- Quick games
- Real-time play
- Baseline for comparison
- When speed matters

### 3. ImprovedMCTSAgent (RESEARCH)

**Location**: `agents/improved_mcts_agent.py`

**Tournament Results**: 42.9% win rate

**Strategy**: Monte Carlo Tree Search with random rollouts.

**Important**: Only use with `rollout_smartness=0.0` (random rollouts). Heuristic rollouts are broken.

**How it works**:
1. Generate candidate moves
2. Simulate games with random play to completion
3. Track win statistics
4. Pick move with best win rate

**Usage**:
```python
from strategic_influence.agents import ImprovedMCTSAgent

agent = ImprovedMCTSAgent(
    seed=42,
    num_simulations=100,       # Number of simulations
    rollout_smartness=0.0,     # MUST be 0.0 (random rollouts)
)
```

**Best for**:
- Research and experimentation
- Understanding MCTS behavior
- Not recommended for competition (loses to heuristics)

### 4. RandomAgent (BASELINE)

**Location**: `agents/random_agent.py`

**Strategy**: Makes completely random valid moves.

**Usage**:
```python
from strategic_influence.agents import RandomAgent

agent = RandomAgent(seed=42)
```

**Best for**:
- Baseline comparison
- Testing game engine
- Sanity checks

## Quick Usage Examples

### Run a Game

```python
from strategic_influence.agents import OptimizedMinimaxAgent, GreedyStrategicAgent
from strategic_influence.engine import simulate_game
from strategic_influence.config import create_default_config

config = create_default_config()
agent1 = OptimizedMinimaxAgent(seed=42, max_depth=1)
agent2 = GreedyStrategicAgent(seed=43)

final_state = simulate_game(config, agent1, agent2, seed=100)
print(f"Winner: {final_state.winner}")
```

### Run Tournament

```bash
python run_tournament.py
```

## Creating Custom Agents

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
        pass

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        # Place initial stone in setup zone
        ...
        return SetupAction(player=player, position=chosen_position)

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        actions = []
        for pos in state.board.positions_owned_by(player):
            action = self._choose_action_for_territory(pos, state, player, config)
            actions.append(action)
        return PlayerTurnActions(player=player, actions=tuple(actions))
```

## Key Tournament Findings

1. **Search beats heuristics**: OptMinimax(d=1) defeats GreedyStrategic 10-0
2. **Shallow beats deep**: depth-1 beats depth-2 (10-0) due to time constraints
3. **MCTS underperforms**: Random rollout MCTS only achieves 42.9%
4. **Heuristic rollouts broken**: MCTS with heuristic guidance loses to Random

## Removed Agents

The following agents were removed after comprehensive testing showed they underperform:

- DefensiveAgent (35.7% win rate, loses to GreedyStrategic 10-0)
- IntuitionAgent (21.4% win rate)
- AggressiveAgent (weak performance)
- MinimaxAgent (superseded by OptimizedMinimax)
- MCTS variants with heuristic evaluation (broken - lose to Random)
