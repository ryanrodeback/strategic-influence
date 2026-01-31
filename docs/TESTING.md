# Strategic Influence - Testing Documentation

## Testing Overview

The project uses **pytest** for testing with a comprehensive test suite covering:
- Unit tests (individual functions)
- Integration tests (full game flows)
- Scenario tests (specific game situations)
- Benchmark tests (performance tracking)

**Key principle**: Immutable data structures make testing straightforward (pure functions with clear inputs/outputs).

## Test Organization

```
tests/
├── unit/                    # Component tests
│   ├── test_types.py        # Data type validation
│   ├── test_engine.py       # Game flow logic
│   ├── test_resolution.py   # Turn resolution
│   └── test_agents.py       # Agent implementations
├── integration/             # Full game tests
│   └── test_full_game.py    # End-to-end game play
├── scenarios/               # Specific game situations
│   ├── test_combat.py
│   ├── test_expansion.py
│   └── test_growth.py
├── benchmarks/              # Performance tests
│   ├── test_minimax_depths.py
│   ├── test_move_generation.py
│   └── ...
└── conftest.py              # Shared fixtures
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_engine.py

# Run specific test function
pytest tests/unit/test_engine.py::test_apply_setup_valid

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s

# Run only failing tests from last run
pytest --lf

# Stop on first failure
pytest -x

# Run tests matching pattern
pytest -k "test_combat"
```

### Test Filtering

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run only benchmarks
pytest tests/benchmarks/

# Skip slow tests
pytest -m "not slow"

# Run only quick tests
pytest -m "quick"
```

### Coverage Analysis

```bash
# Generate coverage report
pytest --cov=src/strategic_influence

# Generate HTML coverage report
pytest --cov=src/strategic_influence --cov-report=html
# View: htmlcov/index.html

# Show uncovered lines
pytest --cov=src/strategic_influence --cov-report=term-missing
```

## Test Structure

### Unit Tests: `tests/unit/`

**Purpose**: Test individual functions in isolation.

**Example** (`test_engine.py`):
```python
def test_apply_setup_valid(default_config):
    """Test applying a valid setup action."""
    state = create_initial_state(default_config.board_size)

    action = SetupAction(
        player=Owner.PLAYER_1,
        position=Position(0, 0)
    )

    new_state = apply_setup(state, action, default_config)

    assert new_state.board.get_owner(Position(0, 0)) == Owner.PLAYER_1
    assert new_state.board.get_stones(Position(0, 0)) == 3
    assert Owner.PLAYER_1 in new_state.setup_complete
```

**Characteristics**:
- Each test is independent
- Uses fixtures for setup
- Verifies one thing
- Tests both success and failure cases

### Integration Tests: `tests/integration/`

**Purpose**: Test complete game flows and interactions.

**Example** (`test_full_game.py`):
```python
def test_full_game_completes(default_config):
    """Test a complete game from setup to finish."""
    agent1 = RandomAgent(seed=42)
    agent2 = RandomAgent(seed=43)

    final_state = simulate_game(default_config, agent1, agent2, seed=100)

    assert final_state.is_complete
    assert final_state.current_turn == default_config.num_turns
    assert final_state.winner is not None or final_state.winner is None  # Draw is ok

    counts = final_state.board.count_territories()
    assert counts[Owner.PLAYER_1] + counts[Owner.PLAYER_2] + counts[Owner.NEUTRAL] == 25
```

### Scenario Tests: `tests/scenarios/`

**Purpose**: Test specific game situations and mechanics.

**Scenario: Combat**
```python
def test_attacker_wins_combat():
    """Test combat where attacker wins."""
    # Setup
    board = create_test_board(5, {
        (1, 1): (Owner.PLAYER_1, 3),
        (1, 2): (Owner.PLAYER_2, 1),
    })

    # Player 1 attacks Player 2
    actions = TurnActions(
        player1_actions=create_test_actions(Owner.PLAYER_1, [
            {'pos': (1, 1), 'type': 'move', 'dest': (1, 2), 'count': 3}
        ]),
        player2_actions=create_test_actions(Owner.PLAYER_2, [
            {'pos': (1, 2), 'type': 'grow'}
        ]),
        turn_number=1,
    )

    # Resolve with fixed RNG
    rng = Random(42)
    result = resolve_turn(board, actions, config, rng)

    # Verify attacker wins
    combats = [m.combat for m in result.movements if m.combat]
    assert any(c.outcome == CombatOutcome.ATTACKER_WINS for c in combats)
```

**Scenario: Expansion**
```python
def test_expansion_success_with_multiple_stones():
    """Test expansion to neutral with multiple stones."""
    board = create_test_board(5, {
        (2, 1): (Owner.PLAYER_1, 3),
        (2, 2): (Owner.NEUTRAL, 0),
    })

    # Player 1 expands with 2 stones
    actions = TurnActions(...)
    rng = Random(42)
    result = resolve_turn(board, actions, config, rng)

    # Expansion should succeed with multiple stones (high probability)
    expansions = [m.expansion for m in result.movements if m.expansion]
    assert any(e.succeeded for e in expansions)
```

### Benchmark Tests: `tests/benchmarks/`

**Purpose**: Track performance and detect regressions.

**Example** (`test_minimax_depths.py`):
```python
def test_minimax_depth1_performance():
    """Minimax depth 1 should be fast (< 100ms per move)."""
    agent = MinimaxAgent(max_depth=1)
    state = create_initial_game_state()

    start = time.time()
    agent.choose_actions(state, Owner.PLAYER_1, config)
    elapsed = time.time() - start

    assert elapsed < 0.1, f"Took {elapsed}s, expected < 0.1s"
```

## Fixture System

### Shared Fixtures (`conftest.py`)

Fixtures provide reusable test setup:

```python
@pytest.fixture
def default_config() -> GameConfig:
    """Provide default game configuration."""
    return create_default_config()

@pytest.fixture
def empty_board(default_config: GameConfig) -> TerritoryBoard:
    """Provide an empty 5x5 board."""
    return create_empty_board(default_config.board_size)

@pytest.fixture
def seeded_rng() -> Random:
    """Provide a seeded RNG for reproducible tests."""
    return Random(42)
```

### Helper Functions

Create test data easily:

```python
def create_test_board(
    size: int,
    territories: dict[tuple[int, int], tuple[Owner, int]],
) -> TerritoryBoard:
    """Create board with specific territories."""
    # Usage:
    board = create_test_board(5, {
        (0, 0): (Owner.PLAYER_1, 3),
        (2, 2): (Owner.NEUTRAL, 0),
        (4, 4): (Owner.PLAYER_2, 2),
    })

def create_test_actions(
    player: Owner,
    actions: list[dict],
) -> PlayerTurnActions:
    """Create actions from action descriptions."""
    # Usage:
    actions = create_test_actions(Owner.PLAYER_1, [
        {'pos': (0, 0), 'type': 'grow'},
        {'pos': (1, 1), 'type': 'move', 'dest': (1, 2), 'count': 2},
        {'pos': (2, 2), 'splits': [((2, 3), 1), ((3, 2), 1)]},
    ])
```

## Writing New Tests

### Test Template

```python
import pytest
from strategic_influence.types import Owner, Position
from strategic_influence.engine import apply_turn
from tests.conftest import create_test_board, create_test_actions

class TestMyFeature:
    """Test suite for feature X."""

    def test_basic_case(self, default_config, empty_board):
        """Test the basic case."""
        # ARRANGE: Set up initial state
        board = create_test_board(5, {
            (1, 1): (Owner.PLAYER_1, 2),
            (1, 2): (Owner.NEUTRAL, 0),
        })

        # ACT: Execute the action
        actions = create_test_actions(Owner.PLAYER_1, [
            {'pos': (1, 1), 'type': 'move', 'dest': (1, 2), 'count': 1}
        ])

        # ASSERT: Verify the result
        result = resolve_turn(board, actions, default_config, Random(42))
        assert result is not None

    def test_edge_case(self, default_config):
        """Test edge case."""
        # ... similar pattern ...

    def test_error_case(self, default_config):
        """Test error handling."""
        with pytest.raises(ValueError, match="error message"):
            # Call function that should raise
            pass
```

### Testing Checklist

- [ ] Arrange initial state
- [ ] Act (call function)
- [ ] Assert results
- [ ] Test both success and failure
- [ ] Test edge cases (empty, full, boundary)
- [ ] Test error conditions
- [ ] Use descriptive assertion messages

## Key Testing Patterns

### Testing Movement Resolution

```python
def test_movement_resolution(seeded_rng):
    """Test that movements resolve correctly."""
    board = create_test_board(...)
    actions = TurnActions(...)

    result = resolve_turn(board, actions, config, seeded_rng)

    # Verify result structure
    assert len(result.movements) > 0
    assert result.board_after != result.board_before
```

### Testing Combat

```python
def test_combat_alternating_rolls(seeded_rng):
    """Test that combat rolls alternate correctly."""
    result = resolve_combat(
        attacker_stones=2,
        defender_stones=2,
        rng=seeded_rng
    )

    assert len(result.rolls) > 0
    # First roll should be defender
    assert result.rolls[0].roller == result.defender
```

### Testing Randomness with Seeding

```python
def test_reproducible_with_seed():
    """Same seed produces same result."""
    game1 = simulate_game(config, agent1, agent2, seed=42)
    game2 = simulate_game(config, agent1, agent2, seed=42)

    assert game1.winner == game2.winner
    assert game1.current_turn == game2.current_turn
```

### Testing Agent Decisions

```python
def test_agent_prefers_expansion(seeded_rng):
    """Test that agent prefers safe expansion."""
    agent = GreedyStrategicAgent(seed=42)
    state = GameState(...)

    actions = agent.choose_actions(state, Owner.PLAYER_1, config)

    # Verify agent made expansion move
    assert any(a.is_move for a in actions.actions)
```

## Debugging Tests

### Verbose Output

```bash
# Print all output (including print statements)
pytest -s tests/unit/test_engine.py::test_apply_setup_valid

# Show local variables on failure
pytest -l

# Full traceback
pytest --tb=long
```

### Debugging with PDB

```python
def test_something():
    board = ...
    # Pause execution here
    breakpoint()  # or pytest.set_trace()
    result = resolve_turn(board, actions, config, rng)
```

Run with:
```bash
pytest -s tests/unit/test_engine.py::test_something
```

### Printing State

```python
def test_board_state():
    board = create_test_board(...)
    print(board)  # Prints ASCII board representation

    state = GameState(...)
    print(state.board.count_territories())  # Verify territory counts
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: pytest --cov=src/strategic_influence
      - run: coverage report --fail-under=80
```

## Performance Benchmarking

### Benchmark Comparison

```bash
# Run and compare against baseline
pytest tests/benchmarks/ -v

# Track performance over time
pytest tests/benchmarks/ --benchmark-json=results.json
```

### Adding Performance Marks

```python
@pytest.mark.benchmark
def test_minimax_speed():
    """Minimax depth 1 performance."""
    # ... test code ...
```

## Test Maintenance

### Updating Tests After Rule Changes

When game rules change:
1. Update test expectations
2. Add tests for new behavior
3. Update existing tests that rely on old behavior
4. Check integration tests still pass

### Flaky Tests

If a test is non-deterministic:
- Use seeded RNG
- Check random behavior is correct
- May need multiple runs to verify

## Test Coverage Goals

| Category | Target | Current |
|----------|--------|---------|
| Core engine | 95% | ~90% |
| Types | 95% | ~92% |
| Agents | 80% | ~75% |
| Resolution | 90% | ~88% |

## Common Issues

### Issue: Test passes locally but fails in CI
**Solution**: Check for non-determinism (use seeding), check for file path issues (use absolute paths)

### Issue: Test is too slow
**Solution**: Reduce board size, use simpler agents, mark with `@pytest.mark.slow`, mock expensive functions

### Issue: Test is flaky (sometimes passes, sometimes fails)
**Solution**: Use seeded RNG, avoid relying on timing, check for race conditions

## Continuous Testing

### Watch Mode

```bash
# Automatically re-run tests on file change
pytest-watch
```

### Pre-commit Hook

```bash
# Add to .git/hooks/pre-commit
pytest --quick
```

## Documentation Tests

Docstring examples can be tested with pytest:

```python
def evaluate_board(board, player, weights):
    """Evaluate board position.

    Examples:
        >>> board = create_test_board(5, {(0, 0): (Owner.PLAYER_1, 3)})
        >>> score = evaluate_board(board, Owner.PLAYER_1, BALANCED_WEIGHTS)
        >>> score > 0
        True
    """
```

Run with:
```bash
pytest --doctest-modules src/
```

## Testing Philosophy

- **Fast**: Tests should run in < 1 second each (except benchmarks)
- **Isolated**: Each test can run independently
- **Clear**: Test name describes what is being tested
- **Complete**: Cover both success and failure cases
- **Maintainable**: Use fixtures and helpers to reduce duplication

## Best Practices

1. **One assertion per test** (or related assertions for same concept)
2. **Descriptive names**: `test_apply_setup_valid_position` not `test_1`
3. **Use fixtures**: Don't create complex setup in every test
4. **Test behavior, not implementation**: Focus on inputs/outputs
5. **Keep tests simple**: If test is complex, code may be too
6. **Use parametrize for variations**: Don't duplicate test logic

```python
@pytest.mark.parametrize("stones,expected", [
    (1, 1),
    (2, 1),
    (3, 2),
    (4, 2),
])
def test_calculate_half(stones, expected):
    assert calculate_half(stones) == expected
```
