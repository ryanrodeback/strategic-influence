# Strategic Influence - Tournaments Documentation

## Tournament System Overview

The tournament system runs multiple games between agents and collects comprehensive statistics to compare performance.

**Key concepts**:
- **Round-robin**: Every agent plays every other agent
- **Match result**: Win/loss/draw between two specific agents
- **Head-to-head stats**: Statistics for pair of agents
- **Agent stats**: Overall statistics across all matches

## Running Tournaments

### Quick Tournament

```bash
# Watch two agents play one game
strategic-influence watch --p1 greedy --p2 defensive

# Run 5 games between two agents
python run_tournament.py --agent1 greedy --agent2 defensive --games 5

# Display results with ASCII table
python run_tournament.py --agent1 greedy --agent2 defensive --games 10 --verbose
```

### Extended Tournament

```bash
# Round-robin: All agents vs all other agents (10 games each matchup)
python extended_tournament.py --agents greedy defensive aggressive random --games 10

# Save results to file
python extended_tournament.py --agents greedy defensive --games 5 --output results.json

# Compare specific agents intensively
python extended_tournament.py --agents greedy minimax --games 20 --output head_to_head.json
```

### Tournament with Custom Configuration

```bash
# Use custom board size or turn count
python run_tournament.py --agent1 greedy --agent2 defensive \
    --games 10 \
    --board-size 5 \
    --turns 20
```

## Tournament Code

### Running a Tournament Programmatically

```python
from strategic_influence.tournament import run_tournament
from strategic_influence.agents import GreedyStrategicAgent, DefensiveAgent
from strategic_influence.config import create_default_config

config = create_default_config()
agent1 = GreedyStrategicAgent(seed=42)
agent2 = DefensiveAgent(seed=43)

results = run_tournament(
    config=config,
    agents=[agent1, agent2],
    num_games_per_matchup=10,
    seed=100,
)

# Access results
print(results.get_rankings())
print(results.format_report())
```

### Understanding Tournament Results

```python
# Results structure
TournamentResults:
  agent_stats: dict[agent_name -> AgentStats]
  head_to_head: dict[(agent1, agent2) -> HeadToHeadStats]
  matches: list[MatchResult]

# Agent stats
AgentStats:
  name: str
  wins: int
  losses: int
  draws: int
  total_territories: int
  total_stones: int
  games_played: int

  win_rate: float  # wins / games_played
  avg_territories: float
  avg_stones: float

# Head-to-head stats
HeadToHeadStats:
  agent1_name: str
  agent2_name: str
  agent1_wins: int
  agent2_wins: int
  draws: int

  agent1_win_rate: float
  agent2_win_rate: float
```

## Tournament Examples

### Example 1: Head-to-Head Comparison

```python
# Test if GreedyStrategic is stronger than Defensive

results = run_tournament(
    config=config,
    agents=[GreedyStrategicAgent(seed=42), DefensiveAgent(seed=43)],
    num_games_per_matchup=20,
    seed=100,
)

# Extract head-to-head stats
h2h = results.head_to_head[("GreedyStrategic", "Defensive")]
print(f"GreedyStrategic win rate: {h2h.agent1_win_rate:.1%}")
print(f"Defensive win rate: {h2h.agent2_win_rate:.1%}")

# Get overall rankings
rankings = results.get_rankings()
for name, stats in rankings:
    print(f"{name}: {stats.win_rate:.1%} ({stats.wins}-{stats.losses}-{stats.draws})")
```

### Example 2: Multi-Agent Tournament

```python
from strategic_influence.agents import (
    RandomAgent,
    GreedyStrategicAgent,
    MinimaxAgent,
    DefensiveAgent,
)

agents = [
    RandomAgent(seed=1),
    GreedyStrategicAgent(seed=2),
    DefensiveAgent(seed=3),
    MinimaxAgent(max_depth=1, seed=4),  # Reduced depth for speed
]

results = run_tournament(
    config=config,
    agents=agents,
    num_games_per_matchup=5,  # 5 games per matchup
    seed=100,
)

print(results.format_report())
```

### Example 3: Configuration Sensitivity

Test how agents perform under different rules:

```python
# Test with different turn counts
configs = [
    GameConfig(..., num_turns=10),
    GameConfig(..., num_turns=20),
    GameConfig(..., num_turns=30),
]

agents = [GreedyStrategicAgent(seed=42), DefensiveAgent(seed=43)]

for config in configs:
    results = run_tournament(config, agents, num_games_per_matchup=5, seed=100)
    print(f"\nWith {config.num_turns} turns:")
    print(results.format_report())
```

## Tournament Interpretation

### Win Rate

```
Win rate = wins / (wins + losses + draws)

Example:
  Agent A: 8 wins, 1 loss, 1 draw out of 10 games
  Win rate = 8/10 = 80%

Interpretation:
  - 50%: Evenly matched
  - 60%+: Clear advantage
  - 70%+: Strong advantage
  - 80%+: Dominant
```

### Territory Differential

```
Avg territories for Agent A: 13.2
Avg territories for Agent B: 11.8
Difference: 1.4 territories

Interpretation:
  - Agent A controls ~1 more territory on average
  - Small difference (<1) = well matched
  - Large difference (>2) = significant advantage
```

### Statistical Significance

```
With N games per matchup:
  N=5: Weak signal (could be luck)
  N=10: Moderate signal (likely real)
  N=20: Strong signal (probably real)
  N=50+: Very strong signal (definitely real)

Chi-square test can determine if result is significant.
```

## Extended Tournament System

### Multiple Agents

```python
from strategic_influence.tournament_extended import run_extended_tournament

agents = [
    GreedyStrategicAgent(seed=1),
    DefensiveAgent(seed=2),
    AggressiveAgent(seed=3),
    RandomAgent(seed=4),
    MinimaxAgent(max_depth=1, seed=5),
]

results = run_extended_tournament(
    config=config,
    agents=agents,
    num_games_per_matchup=5,
    seed=100,
)

# Results include
results.format_rankings()           # Table of final rankings
results.format_head_to_head()      # All pairwise comparisons
results.export_json("results.json") # Export for analysis
```

### Tournament Report Generation

```python
# Automatic report generation
report = results.format_report()
print(report)

# Output example:
"""
TOURNAMENT RESULTS
==================

Rankings (by win rate):
1. GreedyStrategic: 85.0% (17-3-0) - 13.4 territories
2. MinimaxBot: 75.0% (15-5-0) - 13.1 territories
3. Defensive: 55.0% (11-9-0) - 12.6 territories
4. Aggressive: 50.0% (10-10-0) - 12.2 territories
5. Random: 20.0% (4-16-0) - 9.8 territories

Head-to-Head:
GreedyStrategic vs MinimaxBot: 10-10 (50%-50%)
GreedyStrategic vs Defensive: 18-2 (90%-10%)
...
"""
```

## Benchmarking

### Performance Benchmarks

Compare agent speed and effectiveness:

```python
import time
from strategic_influence.engine import simulate_game

agents = [
    (GreedyStrategicAgent(), "Greedy"),
    (MinimaxAgent(max_depth=1), "Minimax-1"),
    (MinimaxAgent(max_depth=2), "Minimax-2"),
]

for agent, name in agents:
    start = time.time()
    for _ in range(5):
        simulate_game(config, RandomAgent(), agent, seed=100)
    elapsed = time.time() - start
    avg_time = elapsed / 5
    print(f"{name}: {avg_time:.2f}s per game")
```

### Throughput Benchmarking

```bash
# How many games can we run per second?
python quick_benchmark.py --agent1 greedy --agent2 defensive --games 100
```

## Advanced Tournament Features

### Seeding and Reproducibility

```python
# Same seed = same sequence of games
results1 = run_tournament(..., seed=42)
results2 = run_tournament(..., seed=42)

# Results are identical
assert results1.matches == results2.matches
```

### Custom Matchup Weighting

```python
# Play Agent1 vs Agent2 uneven number of times
results = run_extended_tournament(
    agents=agents,
    num_games_per_matchup=5,
    # Each agent plays as both colors
    # Total: 5*2 = 10 games
)
```

### Color Balance

The tournament system alternates player colors:
- Agent A as Player 1, Agent B as Player 2
- Agent B as Player 1, Agent A as Player 2

This ensures color bias is detected.

### Parallel Execution

```python
# Run multiple games in parallel (if implemented)
from strategic_influence.simulation import run_parallel_games

results = run_parallel_games(
    config=config,
    agent1=GreedyStrategicAgent(),
    agent2=DefensiveAgent(),
    num_games=20,
    num_workers=4,  # Use 4 processes
)
```

## Tournament Files

### run_tournament.py

Simple script to run tournament between two agents:

```bash
python run_tournament.py --agent1 greedy --agent2 defensive --games 10
```

Usage:
```
--agent1 AGENT        First agent (random, greedy, defensive, etc.)
--agent2 AGENT        Second agent
--games N             Number of games per matchup
--config FILE         Config file path
--seed SEED           Random seed
--verbose             Print full output
```

### extended_tournament.py

Full round-robin tournament:

```bash
python extended_tournament.py --agents greedy defensive random minimax --games 5
```

Usage:
```
--agents AGENTS...    List of agents to include
--games N             Games per matchup
--output FILE         JSON output file
--verbose             Print full output
--parallel N          Use N processes
```

## Analytics and Reporting

### Computing Statistics

```python
# Win rate confidence interval
from scipy.stats import binom

games = 10
wins = 7

# 95% confidence interval
ci = binom.interval(0.95, games, 0.5)
print(f"95% CI for win rate: {ci[0]/games:.1%} - {ci[1]/games:.1%}")
```

### Head-to-Head Charts

```
GreedyStrategic vs Defensive
[████████░░] 80% (8-2 in 10 games)

GreedyStrategic vs MinimaxBot
[██████░░░░] 60% (6-4 in 10 games)
```

### Strength Ranking

```python
# Rank agents by strength
rankings = results.get_rankings()
for i, (name, stats) in enumerate(rankings, 1):
    print(f"{i}. {name}: {stats.win_rate:.1%}")
    print(f"   {stats.wins}W-{stats.losses}L-{stats.draws}D")
    print(f"   Avg {stats.avg_territories:.1f} territories")
```

## Troubleshooting

### Issue: Tournament Takes Too Long
**Solution**: Reduce num_games_per_matchup, use faster agents, use multiprocessing

### Issue: Results Seem Unreliable (high variance)
**Solution**: Increase num_games_per_matchup to 20+, check random seeds

### Issue: One Agent Always Wins
**Solution**: Compare win rates carefully (may be real advantage), try different seeds, check for bugs

## Tournament Strategy

### Quick Evaluation (< 1 minute)
- Use 3-5 games per matchup
- Use fast agents (Greedy, Random, Defensive)
- Focus on 2-3 agent comparison

### Serious Comparison (< 10 minutes)
- Use 10-20 games per matchup
- Include 4-6 agents
- Use reasonable agents (Minimax depth 1, MCTS)

### Deep Analysis (minutes to hours)
- Use 50+ games per matchup
- Include all agents
- Use slow agents (Minimax depth 2, MCTS with 10k+ iterations)
- Compute statistical significance

## Best Practices

1. **Always use seeds**: Reproducible results
2. **Use odd number of games**: Avoid ties in overall tournament
3. **Alternate colors**: Run Agent1 as both Player 1 and Player 2
4. **Run sufficient games**: 10+ per matchup for reliable results
5. **Check for color bias**: Some agents may play different as Player 1 vs Player 2
6. **Save results**: Export tournament results for later analysis
7. **Document configuration**: Record game config used in tournament

## Example Tournament Report

```
=== TOURNAMENT RESULTS ===
Agents: Greedy, Defensive, Random, Minimax (depth 1)
Games per matchup: 5
Total games: 30

RANKINGS
--------
1. Greedy: 80% (8-2-0) avg 13.4 territories
2. Minimax: 70% (7-3-0) avg 13.1 territories
3. Defensive: 40% (4-6-0) avg 12.2 territories
4. Random: 10% (1-9-0) avg 10.1 territories

HEAD-TO-HEAD
------------
Greedy vs Defensive: 9-1 (90%-10%)
Greedy vs Minimax: 5-5 (50%-50%)
Greedy vs Random: 10-0 (100%-0%)
Defensive vs Minimax: 4-6 (40%-60%)
Defensive vs Random: 10-0 (100%-0%)
Minimax vs Random: 10-0 (100%-0%)

NOTES
-----
- Greedy shows clear advantage over Defensive
- Greedy and Minimax are evenly matched
- Random is consistently weak
- Color bias: Check if agents play differently as P1 vs P2
```

## Future Enhancements

Potential tournament improvements:
1. **Swiss system**: Reduce number of games while maintaining accuracy
2. **Dynamic weighting**: Give harder matches higher value
3. **Strength rating**: Calculate Elo or Glicko ratings
4. **Meta analysis**: Detect which strategies are strong against what
5. **Visualization**: Charts and graphs of tournament progress
6. **Web interface**: Run tournaments and view results in browser
