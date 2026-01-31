# Strategic Influence - Complete Documentation

Welcome to the Strategic Influence documentation! This guide will help you understand the game, architecture, and how to extend the system.

## Quick Navigation

### For Players
- **[GAME_MANUAL.md](GAME_MANUAL.md)** - Learn how to play the game
  - Game overview and rules
  - Movement and combat mechanics
  - Strategic concepts and tips
  - Board layout and scoring

### For Understanding the System
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Understand how the code is organized
  - System overview and architectural principles
  - Module responsibilities
  - Key components and data structures
  - Design decisions and rationale

### For AI Development
- **[AGENTS.md](AGENTS.md)** - Learn about all available AI agents
  - Detailed description of each agent's strategy
  - Strengths, weaknesses, and best use cases
  - How to create custom agents
  - Agent comparison and performance

### For Testing
- **[TESTING.md](TESTING.md)** - How to write and run tests
  - Test organization and structure
  - Running tests and interpreting results
  - Writing new tests and test patterns
  - Fixtures and helpers

### For Tournaments
- **[TOURNAMENTS.md](TOURNAMENTS.md)** - Run tournaments and compare agents
  - Running tournaments between agents
  - Interpreting tournament results
  - Performance benchmarking
  - Advanced tournament features

### For Development
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Set up and extend the system
  - Project setup and installation
  - Development workflow
  - Adding new features and agents
  - Code style and best practices

## Document Structure

```
docs/
├── README.md (this file)
├── GAME_MANUAL.md        (Rules and how to play)
├── ARCHITECTURE.md       (System design)
├── AGENTS.md             (AI agents)
├── TESTING.md            (Testing guide)
├── TOURNAMENTS.md        (Tournaments)
└── DEVELOPMENT.md        (Development setup)
```

## Learning Path

### If you're new to the project:
1. Start with **GAME_MANUAL.md** to understand what the game is
2. Read **ARCHITECTURE.md** to understand how it's structured
3. Look at **AGENTS.md** to see what AI strategies exist
4. Check **DEVELOPMENT.md** to set up your development environment

### If you want to run games:
1. **DEVELOPMENT.md** - Set up
2. **GAME_MANUAL.md** - Understand rules
3. **AGENTS.md** - Learn about available agents
4. **TOURNAMENTS.md** - Run tournaments

### If you want to write code:
1. **DEVELOPMENT.md** - Set up environment
2. **ARCHITECTURE.md** - Understand system
3. **TESTING.md** - Learn testing patterns
4. **AGENTS.md** - See how agents are written

### If you want to do research:
1. **AGENTS.md** - Understand existing agents
2. **ARCHITECTURE.md** - Understand evaluation functions
3. **TOURNAMENTS.md** - Run benchmarks
4. **TESTING.md** - Write new tests for experiments

## Key Concepts

### Game Overview
Strategic Influence is a turn-based territorial strategy game:
- 2 players compete on a 5x5 board
- 20 turns total
- Winner: Player controlling most territories (not stones)
- Stone count is resource (more = stronger in combat/expansion)

### Core Mechanics
- **GROW**: Territory gains +1 stone
- **MOVE**: Send stones to adjacent territories
- **Combat**: Simultaneous rolling, attacker rolls last
- **Expansion**: 50% per stone into neutral territory
- **Reinforcement**: Always succeeds when moving to your territory

### Architecture Principles
- **Immutable state**: All operations return new state
- **Pure functions**: No side effects, easy to test
- **Explicit RNG**: All randomness is parameterized
- **Clear separation**: Each module has single responsibility

### Agent Types
- **Random**: Baseline agent (makes random moves)
- **Heuristic**: Fast decision-making (Greedy, Defensive, Aggressive, Intuition)
- **Search-based**: Game tree exploration (Minimax, MCTS)

## Most Important Files

| File | Purpose | Key Takeaway |
|------|---------|--------------|
| `types.py` | Core data types | Everything is immutable, frozen dataclasses |
| `engine.py` | Game flow | Setup → Playing → Complete |
| `resolution.py` | Turn mechanics | Simultaneous movement in 5 phases |
| `combat.py` | Combat | 50% roll chance, alternate rolls |
| `agents/` | AI implementations | All follow Agent protocol |
| `evaluation.py` | Position scoring | Weighted factors for decision-making |
| `config.py` | Game configuration | YAML-based, mutable via code |

## Common Tasks

### Run a quick game
```bash
strategic-influence watch --p1 greedy --p2 defensive
```

### Run tests
```bash
pytest tests/unit/
pytest tests/unit/test_engine.py -v
```

### Run tournament
```bash
python run_tournament.py --agent1 greedy --agent2 minimax --games 10
```

### Benchmark agents
```bash
python benchmark_agents.py
```

### Add a new agent
See **DEVELOPMENT.md** → "Adding New Features" → "Adding a New Agent"

## Design Philosophy

The project is built with these principles:

1. **Clarity over cleverness**
   - Code should be readable and understandable
   - Comments explain "why", not "what"
   - Names are descriptive

2. **Immutability first**
   - No mutating state (safer, testable, parallelizable)
   - Pure functions (input → output)
   - Functional programming style

3. **Separation of concerns**
   - Each module handles one thing well
   - Clear interfaces between modules
   - Easy to test in isolation

4. **Reproducibility**
   - Seeded RNG ensures same results
   - Game history is preserved
   - Replays are possible

5. **Extensibility**
   - Protocol-based agent interface
   - Easy to add new agents
   - Easy to modify rules

## Key Insights

### Why Stone Count vs Territory Count?
Territory count (winning condition) creates interesting strategy:
- Don't just stack stones (turtle strategy)
- Must control actual land
- Forces expansion and tactical play

### Why Simultaneous Movement?
Simultaneous movement (all depart at once) is fairer:
- No turn order advantage
- More interesting tactics (can't react mid-turn)
- Mirrors real-time strategy gameplay

### Why Expansion Risk?
Expansion has 50% per stone success rate:
- Rush vs Patient strategy tension
- Without risk, optimal play is boring
- Creates interesting decisions

### Why Immutability?
Immutable state is essential for:
- Agent lookahead (simulation)
- Parallel execution
- Reproducibility
- Testing

## Architecture Layers

```
CLI Interface (typer)
    ↓
Game Engine (simulate_game)
    ↓
Turn Resolution (resolve_turn)
    ├→ Movement handling
    ├→ Combat resolution
    ├→ Expansion resolution
    └→ Growth application
    ↓
Core Types (immutable dataclasses)
```

## Agent Architecture

```
Agent Interface (Protocol)
    ├→ RandomAgent (baseline)
    ├→ Heuristic Agents
    │   ├→ GreedyStrategic (fast, strong)
    │   ├→ Defensive (safe)
    │   ├→ Aggressive (pushy)
    │   └→ Intuition (growth-first)
    └→ Search Agents
        ├→ Minimax (depth-limited search)
        ├→ OptimizedMinimax (faster)
        └→ ImprovedMCTS (Monte Carlo)
```

## Testing Pyramid

```
                  /\
                 /  \    E2E Tests
                /____\   (Full games)
               /      \
              /________\  Integration Tests
             /          \ (Game components)
            /____________\ Unit Tests
                         (Functions)
```

## Performance Characteristics

| Agent | Speed | Strength | Best For |
|-------|-------|----------|----------|
| Random | Very Fast | Weak | Baseline |
| Greedy | Very Fast | Strong | Quick games |
| Defensive | Very Fast | Moderate | Safe play |
| Aggressive | Very Fast | Moderate | Pushing |
| Intuition | Very Fast | Moderate | Learning |
| Minimax-1 | Fast | Moderate | 1-ply lookahead |
| Minimax-2 | Slow | Strongest | Optimal play (wait 20s) |
| MCTS | Medium | Strong | Exploration |

## Glossary

- **Territory**: An intersection on the board with an owner and stone count
- **Stone**: Unit of control strength (more stones = stronger)
- **Movement**: Sending stones to adjacent position
- **Combat**: Battle between attacking and defending stones
- **Expansion**: Movement into neutral (unoccupied) territory
- **Reinforcement**: Movement into your own territory
- **GROW**: Action to stay and gain +1 stone
- **MOVE**: Action to send stones to adjacent position
- **Turn**: One round where both players choose actions
- **Setup Zone**: Area where players can place initial stones
- **Paranoid search**: Minimax assuming opponent plays optimal counter

## Common Questions

**Q: How do I understand the code?**
A: Start with types.py, then engine.py, then resolution.py. The flow is: GameState → apply_turn → resolve_turn → new GameState.

**Q: How do I add a new rule?**
A: Identify which module handles it (engine.py for game flow, resolution.py for turn mechanics). Add tests first, then implementation.

**Q: Why is my agent slow?**
A: If using Minimax depth 2+, it's expected to be slow. Try greedy heuristic for speed. Use move limiting or MCTS for good balance.

**Q: How do I know if my tournament results are significant?**
A: Run 10+ games per matchup. With 20 games: 65% win rate has 95% confidence interval of roughly 45%-85%.

**Q: Can I add a new game variant?**
A: Yes, create a new config or subclass GameConfig. Tests will verify behavior.

## Resources

- **Code organization**: See ARCHITECTURE.md
- **Game rules**: See GAME_MANUAL.md
- **Agent strategies**: See AGENTS.md
- **Testing patterns**: See TESTING.md
- **Development setup**: See DEVELOPMENT.md
- **Tournament running**: See TOURNAMENTS.md

## Contributing

1. Read DEVELOPMENT.md for setup
2. Make changes and write tests (see TESTING.md)
3. Run tests: `pytest`
4. Update documentation if needed
5. Create pull request

## Current Status

**Version**: 1.0 (stable)
**Status**: Complete with comprehensive AI agents
**Test coverage**: ~85%
**Documentation**: Complete

## Next Steps

Choose your path:

1. **Want to play?** → See GAME_MANUAL.md
2. **Want to understand the code?** → See ARCHITECTURE.md
3. **Want to build an agent?** → See AGENTS.md + DEVELOPMENT.md
4. **Want to run experiments?** → See TOURNAMENTS.md + TESTING.md
5. **Want to extend the system?** → See DEVELOPMENT.md

---

**Last updated**: January 2026
**Maintainer**: Strategic Influence Team
