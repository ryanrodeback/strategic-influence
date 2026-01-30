#!/usr/bin/env python3
"""Test GreedyStrategicAgent - does our Minimax strategy work without search?"""
import sys
import time
sys.path.insert(0, "src")

from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.types import Owner
from strategic_influence.agents import (
    MinimaxAgent, IntuitionAgent, GreedyStrategicAgent, DefensiveAgent
)
from strategic_influence.evaluation import BALANCED_WEIGHTS


def run_match(agent1, agent2, config, seed: int):
    """Run a single match, return winner."""
    start = time.time()
    final_state = simulate_game(config, agent1, agent2, seed)
    elapsed = time.time() - start
    return final_state.winner, elapsed


def compare(name1, factory1, name2, factory2, config, num_games=10):
    """Compare two agents."""
    wins1 = wins2 = draws = 0
    total_time = 0

    for i in range(num_games):
        # Alternate who is P1
        if i % 2 == 0:
            a1, a2 = factory1(), factory2()
            p1_is_1 = True
        else:
            a1, a2 = factory2(), factory1()
            p1_is_1 = False

        winner, elapsed = run_match(a1, a2, config, 42 + i)
        total_time += elapsed

        if winner == Owner.PLAYER_1:
            if p1_is_1:
                wins1 += 1
            else:
                wins2 += 1
        elif winner == Owner.PLAYER_2:
            if p1_is_1:
                wins2 += 1
            else:
                wins1 += 1
        else:
            draws += 1

    avg_time = total_time / num_games
    print(f"  {name1} vs {name2}: {wins1}-{wins2}-{draws} ({avg_time:.2f}s/game avg)")
    return wins1, wins2, draws


def main():
    print("=" * 60)
    print("GREEDY STRATEGIC AGENT TEST")
    print("Does our Minimax strategy work without search?")
    print("=" * 60)

    config = create_default_config()

    agents = {
        "GreedyStrategic": lambda: GreedyStrategicAgent(seed=42),
        "IntuitionBot": lambda: IntuitionAgent(seed=42),
        "DefensiveBot": lambda: DefensiveAgent(seed=42),
        "Minimax-d2": lambda: MinimaxAgent(seed=42, max_depth=2, weights=BALANCED_WEIGHTS, max_moves=50),
    }

    print("\n--- Speed Test (single game) ---")
    for name, factory in agents.items():
        agent = factory()
        other = IntuitionAgent(seed=99)
        _, elapsed = run_match(agent, other, config, 42)
        print(f"  {name}: {elapsed:.2f}s/game")

    print("\n--- Head-to-Head Comparisons (10 games each) ---")

    # GreedyStrategic vs IntuitionBot
    compare("GreedyStrategic", agents["GreedyStrategic"],
            "IntuitionBot", agents["IntuitionBot"], config)

    # GreedyStrategic vs DefensiveBot
    compare("GreedyStrategic", agents["GreedyStrategic"],
            "DefensiveBot", agents["DefensiveBot"], config)

    # GreedyStrategic vs Minimax (the big question!)
    compare("GreedyStrategic", agents["GreedyStrategic"],
            "Minimax-d2", agents["Minimax-d2"], config)

    # For reference: Minimax vs IntuitionBot
    compare("Minimax-d2", agents["Minimax-d2"],
            "IntuitionBot", agents["IntuitionBot"], config)

    print("\n" + "=" * 60)
    print("KEY QUESTIONS:")
    print("1. Does GreedyStrategic beat IntuitionBot? (strategy knowledge)")
    print("2. How close is GreedyStrategic to Minimax? (value of search)")
    print("=" * 60)


if __name__ == "__main__":
    main()
