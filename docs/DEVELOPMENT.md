# Strategic Influence - Development Guide

## Project Setup

### Prerequisites
- Python 3.10+
- pip or poetry
- git

### Installation

```bash
# Clone repository
git clone <repository-url>
cd strategic-influence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt
```

### Verify Installation

```bash
# Run a quick test game
python -c "
from strategic_influence.engine import simulate_game
from strategic_influence.agents import RandomAgent
from strategic_influence.config import create_default_config

config = create_default_config()
state = simulate_game(config, RandomAgent(), RandomAgent(), seed=42)
print(f'Game complete. Winner: {state.winner}')
"

# Run tests
pytest -q

# Run CLI
strategic-influence watch --p1 random --p2 random
```

## Project Structure

```
strategic-influence/
├── docs/                          # Documentation
│   ├── GAME_MANUAL.md
│   ├── ARCHITECTURE.md
│   ├── AGENTS.md
│   ├── TESTING.md
│   ├── TOURNAMENTS.md
│   └── DEVELOPMENT.md (this file)
│
├── src/strategic_influence/       # Main package
│   ├── types.py                   # Core data types
│   ├── engine.py                  # Game flow
│   ├── resolution.py              # Turn resolution
│   ├── combat.py                  # Combat mechanics
│   ├── evaluation.py              # Position evaluation
│   ├── config.py                  # Configuration
│   ├── tournament.py              # Tournament runner
│   ├── tournament_extended.py     # Extended tournaments
│   │
│   ├── agents/                    # AI agents
│   │   ├── protocol.py            # Agent interface
│   │   ├── random_agent.py
│   │   ├── greedy_strategic_agent.py
│   │   ├── minimax_agent.py
│   │   ├── defensive_agent.py
│   │   ├── aggressive_agent.py
│   │   ├── intuition_agent.py
│   │   └── ... (other agents)
│   │
│   ├── cli/                       # Command-line interface
│   │   ├── app.py                 # Main CLI
│   │   └── renderer.py            # Text rendering
│   │
│   ├── simulation/                # Batch simulation
│   │   ├── runner.py
│   │   └── statistics.py
│   │
│   └── visualizer/                # Game visualization
│       └── ... (visualization code)
│
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Full game tests
│   ├── scenarios/                 # Scenario tests
│   ├── benchmarks/                # Performance tests
│   └── conftest.py                # Shared fixtures
│
├── config/                        # Game configuration files
│   └── game_config.yaml
│
├── pyproject.toml                 # Project metadata
├── requirements.txt               # Dependencies
├── requirements-dev.txt           # Dev dependencies
├── pytest.ini                     # Pytest config
└── README.md
```

## Development Workflow

### Making Changes

1. **Create a feature branch**:
```bash
git checkout -b feature/my-feature
```

2. **Make changes** and test:
```bash
pytest tests/unit/test_engine.py -v
```

3. **Run full test suite**:
```bash
pytest
```

4. **Check code quality**:
```bash
# Format code
black src/ tests/

# Check types
mypy src/

# Lint
pylint src/
```

5. **Commit and push**:
```bash
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

6. **Create pull request** on GitHub

### Code Style

The project follows PEP 8 with the following conventions:

**Imports**:
```python
# Standard library
import sys
from dataclasses import dataclass

# Third party
import pytest
import typer

# Local
from .types import Owner, Position
from .config import GameConfig
```

**Naming**:
- `Classes`: PascalCase (GameState, GreedyStrategicAgent)
- `functions`: snake_case (apply_turn, create_game)
- `constants`: UPPER_CASE (BALANCED_WEIGHTS)
- `private`: _snake_case (_nodes_searched)

**Docstrings**:
```python
def apply_turn(
    state: GameState,
    actions: TurnActions,
    config: GameConfig,
    rng: Random,
) -> GameState:
    """Apply a turn to the game state.

    Validates actions, resolves movements and combat, applies growth.

    Args:
        state: Current game state.
        actions: Both players' actions.
        config: Game configuration.
        rng: Random number generator.

    Returns:
        New GameState after the turn.

    Raises:
        ValueError: If actions are invalid or game is not in PLAYING phase.
    """
```

**Type hints**:
```python
# Always use type hints
def choose_actions(
    self,
    state: GameState,
    player: Owner,
    config: GameConfig,
) -> PlayerTurnActions:
    # ...
```

### Testing Your Changes

```bash
# Test single file
pytest tests/unit/test_engine.py -v

# Test single function
pytest tests/unit/test_engine.py::test_apply_setup_valid -v

# Test with coverage
pytest --cov=src/strategic_influence tests/unit/

# Run benchmarks
pytest tests/benchmarks/ -v
```

## Configuration System

### Game Configuration File

Default: `config/game_config.yaml`

```yaml
game:
  board_size: 5
  num_turns: 20
  combat:
    hit_chance: 0.5
  growth:
    stones_per_turn: 1
    max_stones: 10
  setup:
    stones_per_placement: 3
  expansion_success_rate: 1.0

simulation:
  default_num_games: 10
  parallel_workers: 4
  random_seed: null

display:
  symbols:
    player1: "W"
    player2: "B"
    neutral: "+"
  board:
    cell_width: 3
    show_coordinates: true
  verbosity:
    show_combat_rolls: true
    show_movements: true
    show_growth: true
```

### Loading Configuration

```python
from strategic_influence.config import load_config, create_default_config
from pathlib import Path

# From file
config = load_config(Path("config/game_config.yaml"))

# Default
config = create_default_config()

# Modify
from dataclasses import replace
modified_config = replace(config, num_turns=30)
```

### Modifying Game Rules

To change a rule (e.g., expansion success rate):

1. **Update config file**:
```yaml
expansion_success_rate: 0.75  # Changed from 1.0
```

2. **Update tests**:
```python
def test_expansion_with_different_rate():
    config = create_default_config()
    config = replace(config, game=replace(
        config.game,
        expansion_success_rate=0.75
    ))
    # ... test with new rate ...
```

3. **Update documentation**: Add note to GAME_MANUAL.md

## Adding New Features

### Adding a New Agent

1. **Create agent file** (`src/strategic_influence/agents/my_agent.py`):

```python
from ..types import Owner, GameState, SetupAction, PlayerTurnActions
from ..config import GameConfig

class MyCustomAgent:
    def __init__(self, seed: int | None = None):
        self._initial_seed = seed

    @property
    def name(self) -> str:
        return "MyCustom"

    def reset(self) -> None:
        pass

    def choose_setup(self, state, player, config) -> SetupAction:
        # Implementation
        pass

    def choose_actions(self, state, player, config) -> PlayerTurnActions:
        # Implementation
        pass
```

2. **Add to agents/__init__.py**:
```python
from .my_agent import MyCustomAgent

__all__ = [..., "MyCustomAgent"]
```

3. **Add to CLI** (`src/strategic_influence/cli/app.py`):
```python
def get_agent(agent_type: str, seed: int | None = None) -> Agent:
    # ...
    elif agent_type == "mycustom":
        return MyCustomAgent(seed=seed)
    # ...
```

4. **Add tests** (`tests/unit/test_agents.py`):
```python
def test_my_custom_agent_chooses_actions():
    agent = MyCustomAgent(seed=42)
    state = create_initial_game_state()
    actions = agent.choose_actions(state, Owner.PLAYER_1, default_config)
    assert len(actions.actions) > 0
```

### Adding a New Rule

1. **Modify the rule** in relevant module:
   - Core rule? → `types.py` or `engine.py`
   - Resolution? → `resolution.py` or `combat.py`
   - Config? → `config.py`

2. **Add tests** that verify the new behavior:
```python
def test_new_rule():
    # Test the new mechanic
    pass
```

3. **Update documentation**:
   - GAME_MANUAL.md: Add description of new rule
   - ARCHITECTURE.md: Explain design decision
   - Config defaults if needed

### Adding Evaluation Metrics

1. **Add metric function** in `evaluation.py`:
```python
def compute_my_metric(board: TerritoryBoard, player: Owner, config: GameConfig) -> float:
    """Compute some strategic metric."""
    # ...
    return score
```

2. **Add to EvaluationWeights**:
```python
@dataclass
class EvaluationWeights:
    # ... existing weights ...
    my_metric: float = 1.5  # Default weight
```

3. **Use in evaluation**:
```python
def evaluate_board(...):
    # ... compute existing metrics ...
    my_metric_score = compute_my_metric(board, player, config)
    # ... add to final score using weight ...
```

4. **Create weight preset**:
```python
MY_METRIC_WEIGHTS = EvaluationWeights(
    my_metric=5.0,  # High value for this preset
    # ... other weights ...
)
```

## Debugging

### Print Debugging

```python
def apply_turn(...):
    # ...
    if debug:
        print(f"Board state: {board}")
        print(f"Movements: {movements}")
```

### Interactive Debugging

```python
# In code, add breakpoint:
breakpoint()  # or pdb.set_trace()

# Run with:
pytest -s tests/unit/test_file.py::test_function
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def apply_turn(...):
    logger.debug(f"Applying turn with {len(actions)} actions")
    # ...
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile a function
profiler = cProfile.Profile()
profiler.enable()

# Run code to profile
result = agent.choose_actions(state, player, config)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

### Common Bottlenecks

1. **Agent lookahead**: Minimax is slow, consider move limiting
2. **Board copying**: Immutability has cost, consider pooling
3. **Move generation**: Can be optimized with caching
4. **Evaluation function**: Called many times, should be fast

### Optimization Tips

1. **Cache position evaluation results** (memoization)
2. **Limit branching factor** (fewer moves to consider)
3. **Use iterative deepening** (time-bounded search)
4. **Pre-compute heuristics** (e.g., center control bonus)

## Release Process

### Version Numbering

Uses semantic versioning: MAJOR.MINOR.PATCH

- MAJOR: Breaking changes to game/API
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Checklist

- [ ] Update CHANGELOG.md
- [ ] Update version in `pyproject.toml`
- [ ] Run full test suite (`pytest`)
- [ ] Check coverage (`pytest --cov`)
- [ ] Update documentation if needed
- [ ] Tag release (`git tag v1.2.3`)
- [ ] Create GitHub release notes

## CI/CD Pipeline

### Local Checks (before committing)

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
pylint src/

# Tests
pytest

# Coverage
pytest --cov=src/strategic_influence --cov-report=term-missing
```

### GitHub Actions

(If configured) Automatically runs:
- Full test suite
- Coverage check
- Code quality checks
- Build documentation

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def simulate_game(
    config: GameConfig,
    player1: Agent,
    player2: Agent,
    seed: int | None = None,
) -> GameState:
    """Run a complete game between two players.

    Simulates a full game from setup through 20 turns, with both players
    choosing actions and the engine resolving all movements and combat.

    Args:
        config: Game configuration (board size, num turns, etc.)
        player1: First player (White)
        player2: Second player (Black)
        seed: Random seed for reproducibility (default: system random)

    Returns:
        Final GameState with completed game

    Raises:
        ValueError: If config is invalid

    Examples:
        >>> config = create_default_config()
        >>> agent1 = GreedyStrategicAgent(seed=42)
        >>> agent2 = DefensiveAgent(seed=43)
        >>> result = simulate_game(config, agent1, agent2, seed=100)
        >>> result.is_complete
        True
    """
```

### Updating Documentation

1. **Game rules changed?** → Update GAME_MANUAL.md
2. **Architecture changed?** → Update ARCHITECTURE.md
3. **New agent?** → Update AGENTS.md with description and strategy
4. **New test pattern?** → Update TESTING.md
5. **New tournament feature?** → Update TOURNAMENTS.md

## Common Tasks

### Running a Quick Game

```python
from strategic_influence.engine import simulate_game
from strategic_influence.agents import GreedyStrategicAgent, DefensiveAgent
from strategic_influence.config import create_default_config

config = create_default_config()
state = simulate_game(config, GreedyStrategicAgent(), DefensiveAgent(), seed=42)
print(state.board)
```

### Benchmarking Agents

```bash
python benchmark_agents.py --agents greedy defensive minimax --games 10
```

### Running Tests for a Component

```bash
# Test resolution system
pytest tests/unit/test_resolution.py -v

# Test agent performance
pytest tests/unit/test_agents.py -v
```

### Inspecting Game History

```python
state = simulate_game(...)

# Check turn-by-turn results
for turn_result in state.turn_history:
    print(f"Turn {turn_result.turn_number}:")
    print(f"  Movements: {len(turn_result.movements)}")
    print(f"  Combats: {len(turn_result.combats)}")
    print(f"  Territories grown: {turn_result.territories_grown}")
```

## Troubleshooting Development Issues

### Issue: Import errors
**Solution**: Make sure you've installed the package in editable mode (`pip install -e .`)

### Issue: Tests fail locally but pass in CI
**Solution**: Check Python version, check for non-determinism (use seeding), check file paths

### Issue: Slow tests
**Solution**: Use `pytest -m "not slow"` to skip slow tests, profile with cProfile

### Issue: Agent makes invalid moves
**Solution**: Check agent.choose_actions() is returning valid territories, verify validation

## Getting Help

1. **Check ARCHITECTURE.md** for system design
2. **Check TESTING.md** for testing patterns
3. **Look at similar code** for examples
4. **Run tests** to verify changes
5. **Ask questions** in issues/discussions

## Resources

- **Game Manual**: GAME_MANUAL.md
- **Architecture**: ARCHITECTURE.md
- **Agents**: AGENTS.md
- **Testing**: TESTING.md
- **Tournaments**: TOURNAMENTS.md
- **Code Examples**: Look at existing agents
- **Test Examples**: Look at test files

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes and test
4. Update documentation
5. Create pull request

See the main README for contribution guidelines.
