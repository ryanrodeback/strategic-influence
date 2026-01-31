#!/usr/bin/env python3
"""Test ultra-minimal weight configurations.

Tests the hypothesis: Is territory_count alone sufficient?
Or does Minimax need explicit threat evaluation?
"""
import sys
sys.path.insert(0, "src")

from random import Random
from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.types import Owner
from strategic_influence.agents import MinimaxAgent, IntuitionAgent, DefensiveAgent
from strategic_influence.evaluation import (
    TERRITORY_ONLY_WEIGHTS,
    TERRITORY_SAFETY_WEIGHTS,
    BALANCED_WEIGHTS,
)


def run_match(agent1, agent2, config, seed: int):
    """Run a single match, return winner."""
    final_state = simulate_game(config, agent1, agent2, seed)
    return final_state.winner


def compare_agents(config, factory1, factory2, num_games: int, base_seed: int):
    """Run comparison with both orderings."""
    half = num_games // 2
    wins1 = wins2 = draws = 0

    # Agent 1 as Player 1
    for i in range(half):
        agent1 = factory1()
        agent2 = factory2()
        winner = run_match(agent1, agent2, config, base_seed + i)
        if winner == Owner.PLAYER_1:
            wins1 += 1
        elif winner == Owner.PLAYER_2:
            wins2 += 1
        else:
            draws += 1

    # Agent 1 as Player 2
    for i in range(half):
        agent1 = factory2()
        agent2 = factory1()
        winner = run_match(agent1, agent2, config, base_seed + 1000 + i)
        if winner == Owner.PLAYER_1:
            wins2 += 1
        elif winner == Owner.PLAYER_2:
            wins1 += 1
        else:
            draws += 1

    return {"wins1": wins1, "wins2": wins2, "draws": draws}


def main():
    print("=" * 60)
    print("ULTRA-MINIMAL WEIGHTS TOURNAMENT (Fast version)")
    print("Testing: Is territory_count alone sufficient?")
    print("=" * 60)

    config = create_default_config()
    num_games = 10  # 5 each direction - faster

    # Use depth=1 for Minimax (much faster, still tests hypothesis)
    # The key question is: does territory_count alone capture what matters?
    agents = {
        "TerritoryOnly-d1": lambda: MinimaxAgent(
            seed=42, max_depth=1, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15
        ),
        "Territory+Safety-d1": lambda: MinimaxAgent(
            seed=42, max_depth=1, weights=TERRITORY_SAFETY_WEIGHTS, max_moves=15
        ),
        "Balanced-d1": lambda: MinimaxAgent(
            seed=42, max_depth=1, weights=BALANCED_WEIGHTS, max_moves=15
        ),
        "IntuitionBot": lambda: IntuitionAgent(seed=42),
        "DefensiveBot": lambda: DefensiveAgent(seed=42),
    }

    print(f"\nAgents: {list(agents.keys())}")
    print(f"Games per pair: {num_games} ({num_games//2} as P1, {num_games//2} as P2)")
    print(f"Config: {config.board_size}x{config.board_size}, {config.num_turns} turns")
    print(f"NOTE: Using depth=1 for Minimax (faster iteration)")

    # Track results
    results = {name: {"wins": 0, "losses": 0, "draws": 0} for name in agents}

    agent_names = list(agents.keys())

    for i, name1 in enumerate(agent_names):
        for name2 in agent_names[i+1:]:
            print(f"\n{name1} vs {name2}...", end=" ", flush=True)

            comparison = compare_agents(
                config=config,
                factory1=agents[name1],
                factory2=agents[name2],
                num_games=num_games,
                base_seed=42 + i * 100,
            )

            results[name1]["wins"] += comparison["wins1"]
            results[name1]["losses"] += comparison["wins2"]
            results[name1]["draws"] += comparison["draws"]

            results[name2]["wins"] += comparison["wins2"]
            results[name2]["losses"] += comparison["wins1"]
            results[name2]["draws"] += comparison["draws"]

            print(f"{comparison['wins1']}-{comparison['wins2']}-{comparison['draws']}")

    # Print results
    print("\n\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    # Calculate win rates
    sorted_results = []
    for name, stats in results.items():
        total = stats["wins"] + stats["losses"] + stats["draws"]
        win_rate = (stats["wins"] + 0.5 * stats["draws"]) / total if total > 0 else 0
        sorted_results.append((name, stats, win_rate))

    sorted_results.sort(key=lambda x: x[2], reverse=True)

    print(f"\n{'Agent':<25} {'W':>4} {'L':>4} {'D':>4} {'Win%':>8}")
    print("-" * 49)
    for name, stats, win_rate in sorted_results:
        print(f"{name:<25} {stats['wins']:>4} {stats['losses']:>4} {stats['draws']:>4} {win_rate:>7.1%}")

    # Key comparison
    print("\n" + "=" * 60)
    print("KEY INSIGHTS:")
    print("1. TerritoryOnly vs Territory+Safety: If similar, depth-1 sees threats")
    print("2. Territory-based vs IntuitionBot: Tests if simple metric works")
    print("3. Territory-based vs DefensiveBot: Compare to strongest heuristic")
    print("=" * 60)


if __name__ == "__main__":
    main()
