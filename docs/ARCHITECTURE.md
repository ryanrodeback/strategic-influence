# Strategic Influence - Architecture Documentation

## System Overview

The Strategic Influence project is structured as a modular game engine with clear separation of concerns:

```
strategic_influence/
├── types.py              # Core game data types (immutable)
├── engine.py             # Game flow (setup, turns, win condition)
├── resolution.py         # Turn resolution (movement, combat, growth)
├── combat.py             # Combat mechanics
├── evaluation.py         # Position evaluation for AI
├── config.py             # Game configuration (YAML loading)
├── tournament.py         # Tournament runners
├── tournament_extended.py # Advanced tournament features
├── agents/               # AI agent implementations
├── cli/                  # Command-line interface
├── simulation/           # Batch simulation runners
├── visualizer/           # Game visualization tools
```

## Architectural Principles

### 1. Immutability First

All game state is represented as **frozen dataclasses**:

```python
@dataclass(frozen=True)
class GameState:
    board: TerritoryBoard
    phase: GamePhase
    current_turn: int
    turn_history: tuple[TurnResult, ...]
    setup_complete: tuple[Owner, ...]
    winner: Owner | None
```

**Why**:
- **Pure functions**: All game operations return new state, never mutate
- **Reproducibility**: Same seed produces identical game sequence
- **Parallel safety**: Multiple simulations can run without race conditions
- **Debuggability**: Can inspect historical states in turn_history

**Cost**: Slightly higher memory usage, but worth it for correctness.

### 2. Separation of Concerns

**Clear module boundaries**:

| Module | Responsibility |
|--------|---|
| `types.py` | Define all data structures (Position, Territory, GameState, etc.) |
| `engine.py` | High-level game flow (setup, turns, winning) |
| `resolution.py` | Turn resolution mechanics (movement, combat, growth) |
| `combat.py` | Combat rolling and outcome calculation |
| `evaluation.py` | Position assessment for AI agents |
| `config.py` | Configuration loading and defaults |

This separation means:
- Each module can be tested independently
- Game rules can be modified in one place
- AI agents only depend on types and config

### 3. Pure Functions

Game operations are pure functions:

```python
def apply_turn(
    state: GameState,
    actions: TurnActions,
    config: GameConfig,
    rng: Random,
) -> GameState:
    """Takes state, returns new state. No side effects."""
```

**Benefits**:
- Easy to test (input -> output)
- Easy to parallelize (no shared state)
- Easy to debug (can replay with exact seed)

**Convention**:
- Functions that transform state are named `apply_*` or `resolve_*`
- Query functions are named `get_*` or `count_*`

### 4. Explicit RNG Handling

Random number generation is **explicit and parameterized**:

```python
def resolve_expansion(
    position: Position,
    expander: Owner,
    stones: int,
    success_rate: float,
    rng: Random,  # <-- Passed in explicitly
) -> ExpansionResult:
```

**Why**:
- Reproducible with seeding
- Testable (can inject mock RNG)
- Clear which functions are non-deterministic
- Parallel simulation safe

## Core Game Flow

### Setup Phase
```
1. create_game(config) -> GameState (SETUP phase, empty board)
2. player1.choose_setup(...) -> SetupAction
3. apply_setup(state, action, config) -> GameState
4. player2.choose_setup(...) -> SetupAction
5. apply_setup(state, action, config) -> GameState (now PLAYING phase)
```

### Main Game Loop
```
WHILE not state.is_complete:
    1. player1.choose_actions(state, ...) -> PlayerTurnActions
    2. player2.choose_actions(state, ...) -> PlayerTurnActions
    3. apply_turn(state, combined_actions, config, rng) -> GameState
```

### Game End
```
After num_turns:
    determine_winner(board) -> Owner | None
    state.phase = COMPLETE
```

## Key Components

### 1. Data Types (`types.py`)

**Board representation**:
- `Position`: (row, col) coordinate with bounds checking
- `Territory`: Owner + stone count at one intersection
- `TerritoryBoard`: Full board state (5x5 grid of territories)

**Actions**:
- `TerritoryAction`: One position's action (GROW or MOVE)
- `StoneMovement`: Individual stone movement (source, dest, count)
- `PlayerTurnActions`: All actions for one player
- `TurnActions`: Both players' actions for one turn

**Results**:
- `MovementResult`: Outcome of one stone movement (may involve combat/expansion)
- `CombatResult`: Complete combat at one position
- `ExpansionResult`: Expansion attempt result
- `TurnResult`: Full turn outcome with all movements

**Helper Functions**:
- `create_grow_action()`: Simple GROW action
- `create_simple_move_action()`: Single-direction movement
- `create_move_action()`: Multi-direction split movement
- `get_valid_actions()`: All legal moves for a position

### 2. Game Engine (`engine.py`)

**Core functions**:

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `create_game()` | GameConfig | GameState | Initialize empty game |
| `apply_setup()` | GameState, SetupAction | GameState | Apply one setup placement |
| `apply_turn()` | GameState, TurnActions, RNG | GameState | Execute one full turn |
| `determine_winner()` | TerritoryBoard | Owner \| None | Calculate winner |
| `simulate_game()` | GameConfig, 2 Agents | GameState | Run complete game |

**Validation**:
- `validate_setup_action()`: Check setup position is legal
- `validate_turn_actions()`: Check all actions are valid

### 3. Turn Resolution (`resolution.py`)

The heart of the game: **how movements are resolved**.

**Key insight**: Simultaneous movement requires careful ordering:

```
1. All Departures (remove stones from source territories)
2. Reinforcements (add stones to friendly territories)
3. Expansions (roll for neutral territories)
4. Attacks (combat against enemy territories)
5. Growth (add +1 stones to territories that grew)
```

**Why this order**:
- Simultaneous departures ensure true simultaneity
- Reinforcements can't fail (safe)
- Expansions are independent (no interaction)
- Combat happens with known board state
- Growth happens after combat resolves

**Functions**:

| Function | Purpose |
|----------|---------|
| `_apply_all_departures()` | Remove all moving stones (step 1) |
| `_apply_reinforcements()` | Add friendly movements (step 2) |
| `resolve_expansion()` | Roll for neutral territory |
| `_resolve_expansions()` | Handle all expansions (step 3) |
| `_resolve_attacks()` | Handle all combat (step 4) |
| `_apply_growth()` | Add growth stones (step 5) |
| `resolve_turn()` | Orchestrate all steps |

### 4. Combat (`combat.py`)

**Combat mechanics**:
- Defender rolls first (50% hit chance)
- Attacker rolls (50% hit chance)
- Alternate until one side eliminated
- Both rolls are independent

**Function**: `resolve_combat(attacker_stones, defender_stones, rng)`

Returns `CombatResult` with:
- Initial stone counts
- Final stone counts
- All individual rolls
- Combat outcome (ATTACKER_WINS, DEFENDER_HOLDS, MUTUAL_DESTRUCTION)

### 5. Evaluation (`evaluation.py`)

Position evaluation for AI agents to score board states.

**Key metrics**:
- `territory_count`: Number of territories you control
- `stone_advantage`: Your stones vs opponent stones
- `growth_potential`: How many stones you can gain next turn
- `expansion_opportunity`: How many safe expansion targets exist
- `center_control`: Control of center positions
- `attack_opportunity`: How many enemy territories you can attack
- `threatened_penalty`: How many of your territories are threatened
- `connectivity`: How connected your territories are
- `merge_potential`: Ability to merge forces back together

**Preset weights**:
- `BALANCED_WEIGHTS`: Default, balanced evaluation
- `AGGRESSIVE_WEIGHTS`: Prioritize territory/attack
- `DEFENSIVE_WEIGHTS`: Prioritize safety/growth
- `INTUITION_WEIGHTS`: Growth-first strategy
- `GROWTH_FIRST_MODERATE`: Experimental growth focus

**Key functions**:
```python
def evaluate_board(board: TerritoryBoard, player: Owner, weights: EvaluationWeights) -> float:
    """Score board from player's perspective (higher = better for player)."""
```

## Agent Architecture

### Agent Protocol

All AI agents implement this interface:

```python
class Agent(Protocol):
    @property
    def name(self) -> str:
        """Display name for agent."""

    def reset(self) -> None:
        """Reset for new game."""

    def choose_setup(state: GameState, player: Owner, config: GameConfig) -> SetupAction:
        """Choose where to place initial stone."""

    def choose_actions(state: GameState, player: Owner, config: GameConfig) -> PlayerTurnActions:
        """Choose action for each owned territory."""
```

### Agent Implementations

See `AGENTS.md` for detailed descriptions. Quick overview:

| Agent | Strategy | Speed | Strength |
|-------|----------|-------|----------|
| `RandomAgent` | Random moves | Fast | Baseline |
| `GreedyStrategicAgent` | Heuristic scoring | Very Fast | Strong |
| `MinimaxAgent` | Game tree search + alpha-beta | Slow | Strongest |
| `OptimizedMinimaxAgent` | Faster minimax variant | Medium | Strong |
| `ImprovedMCTSAgent` | Monte Carlo tree search | Medium | Strong |
| `DefensiveAgent` | Defense-first heuristic | Very Fast | Moderate |
| `AggressiveAgent` | Attack-first heuristic | Very Fast | Moderate |
| `IntuitionAgent` | Growth-first heuristic | Very Fast | Moderate |

## Configuration System

### GameConfig Structure

```python
@dataclass(frozen=True)
class GameConfig:
    board_size: int              # 5x5 board
    num_turns: int               # Number of turns
    game: GameRulesConfig        # Core rules
    display: DisplayConfig       # UI settings
    simulation: SimulationConfig # Runner settings
```

### Loading Configuration

```python
# From file
config = load_config(Path("config/game_config.yaml"))

# Default
config = create_default_config()
```

### Key Configurable Values

| Setting | Default | Impact |
|---------|---------|--------|
| `board_size` | 5 | Game complexity |
| `num_turns` | 20 | Game length |
| `combat.hit_chance` | 0.5 | Combat mechanics |
| `growth.stones_per_turn` | 1 | Growth rate |
| `growth.max_stones` | 10 | Stone cap |
| `expansion_success_rate` | 1.0 | Expansion risk |

## Testing Architecture

### Test Organization

```
tests/
├── unit/                # Component tests
│   ├── test_types.py
│   ├── test_engine.py
│   ├── test_resolution.py
│   └── test_agents.py
├── integration/        # Full game tests
├── scenarios/          # Specific game situations
├── benchmarks/         # Performance tests
└── conftest.py         # Shared fixtures
```

### Fixture System

Shared test utilities in `conftest.py`:

```python
@pytest.fixture
def empty_board(default_config):
    """Empty 5x5 board."""

@pytest.fixture
def seeded_rng():
    """Reproducible RNG."""

def create_test_board(size, territories):
    """Create board with specific territories."""

def create_test_actions(player, actions):
    """Create actions from list of dicts."""
```

### Testing Patterns

**Unit tests**:
- Test single function in isolation
- Use seeded RNG for reproducibility
- Verify error handling

**Integration tests**:
- Run complete games
- Verify final state is correct
- Check win condition logic

**Benchmark tests**:
- Measure agent performance
- Compare different strategies
- Track regressions

## Performance Considerations

### Bottlenecks

1. **Agent decision making** (~90% of time in long games)
   - Minimax depth-2: ~20s per territory (2-3 territories = too slow)
   - Greedy heuristic: ~1ms per move
   - MCTS: ~2-5s per move (good balance)

2. **Board state copying**
   - Creating new board each turn (immutability cost)
   - Noticeable at 1000+ simulations

3. **Movement resolution**
   - Iterating all movements is fast
   - Combat/expansion rolling is minor

### Optimization Strategies

1. **Limit lookahead depth**
   - Minimax: depth 2 is practical, depth 3+ needs move limiting

2. **Move sampling**
   - Instead of exploring all moves, sample promising ones
   - Reduces branching factor

3. **Batch simulation**
   - Run multiple games in parallel
   - Use Python multiprocessing

4. **Memoization**
   - Cache evaluation results
   - Cache movement possibilities

## Extensibility Points

### Adding New Agents

1. Implement Agent protocol
2. Add to `agents/__init__.py`
3. Add to CLI `get_agent()` function
4. Add tests in `tests/unit/test_agents.py`

### Changing Game Rules

1. Modify constants in `config.py`
2. Update validation in `engine.py` if needed
3. Update resolution in `resolution.py` if needed
4. Add tests to verify change

### Custom Board Sizes

1. Update `board_size` in config
2. Setup zones automatically scale
3. Test with benchmarks to ensure no regressions

### New Evaluation Metrics

1. Add metric function in `evaluation.py`
2. Add weight to `EvaluationWeights`
3. Use in agent evaluation
4. Compare agent performance

## Design Decisions

### Why Stone Count vs. Territory Count?

**Territory Count** was chosen for winning condition because:
- More interesting strategically (not just "pile more stones")
- Rewards actual control, not just accumulation
- Prevents "turtle" strategy (infinite stacking)
- Matches Go-like territory control theme

### Why Simultaneous Movement with Fixed Order?

**True simultaneity** (all depart at once) was chosen because:
- More fair than sequential (no turn order advantage)
- More interesting tactics (can't react mid-turn)
- Mirrors real-time strategy gameplay

**Fixed resolution order** ensures:
- Deterministic outcomes
- Clear cause-and-effect
- Easier to reason about

### Why Immutability?

Immutable state was chosen because:
- Essential for agent lookahead (simulation)
- Enables parallel game execution
- Guarantees reproducibility
- Makes testing cleaner

Cost is acceptable (Python immutability is fast enough).

### Why Explicit RNG Passing?

Explicit RNG parameters enable:
- Deterministic replay
- Parallel simulation (each gets own RNG)
- Testing without mocking
- Clear which functions are non-deterministic

### Why Expansion Risk (50% per stone)?

Risk creates interesting decisions:
- Rush (single-stone expansions are risky)
- Patience (grow first, then expand safely)
- Without risk, optimal play is boring

The 50% rate makes it solvable by heuristics.

## Future Architecture Notes

### Potential Improvements

1. **Visualization improvement**: Current visualizer is simple; could add animated movement
2. **Better MCTS**: Current implementation is basic; could add UCT improvements
3. **Network play**: Add multiplayer via network (requires rewriting CLI)
4. **Replay system**: Store and replay games with UI
5. **Analytics**: Better statistics collection and analysis
6. **Distributed tournaments**: Run tournaments across multiple machines

### Stability Notes

- Core engine is stable (immutable, well-tested)
- Agent APIs are stable (Protocol-based)
- Config system is stable (frozen dataclasses)
- Tournament system may evolve (good place to experiment)
