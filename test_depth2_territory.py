#!/usr/bin/env python3
"""Test territory-only weights at depth-2.

Key question: At depth-2 (can see opponent response),
does territory_count alone work?
"""
import sys
sys.path.insert(0, "src")

from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.types import Owner
from strategic_influence.agents import MinimaxAgent, IntuitionAgent
from strategic_influence.evaluation import (
    TERRITORY_ONLY_WEIGHTS,
    TERRITORY_SAFETY_WEIGHTS,
)


def run_match(agent1, agent2, config, seed: int):
    """Run a single match, return winner."""
    final_state = simulate_game(config, agent1, agent2, seed)
    return final_state.winner


def main():
    print("=" * 60)
    print("DEPTH-2 TERRITORY TEST")
    print("Does Minimax's lookahead handle threats naturally?")
    print("=" * 60)

    config = create_default_config()

    # Focused comparison: TerritoryOnly-d2 vs IntuitionBot
    # This tests: Can depth-2 with just territory_count beat the best heuristic?

    print("\nTest 1: TerritoryOnly-d2 vs IntuitionBot (6 games)")
    print("-" * 50)

    wins_territory = 0
    wins_intuition = 0
    draws = 0

    for i in range(6):
        # Alternate who is P1
        if i % 2 == 0:
            agent1 = MinimaxAgent(seed=42+i, max_depth=2, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15)
            agent2 = IntuitionAgent(seed=42+i)
            territory_is_p1 = True
        else:
            agent1 = IntuitionAgent(seed=42+i)
            agent2 = MinimaxAgent(seed=42+i, max_depth=2, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15)
            territory_is_p1 = False

        print(f"  Game {i+1} (TerritoryOnly as P{'1' if territory_is_p1 else '2'})...", end=" ", flush=True)
        winner = run_match(agent1, agent2, config, 42 + i)

        if winner == Owner.PLAYER_1:
            if territory_is_p1:
                wins_territory += 1
                print("T wins")
            else:
                wins_intuition += 1
                print("I wins")
        elif winner == Owner.PLAYER_2:
            if territory_is_p1:
                wins_intuition += 1
                print("I wins")
            else:
                wins_territory += 1
                print("T wins")
        else:
            draws += 1
            print("draw")

    print(f"\nResult: TerritoryOnly-d2 {wins_territory}-{wins_intuition}-{draws} IntuitionBot")

    # Test 2: Does adding threatened_penalty help at depth-2?
    print("\n" + "=" * 60)
    print("Test 2: TerritoryOnly-d2 vs Territory+Safety-d2 (6 games)")
    print("-" * 50)

    wins_only = 0
    wins_safety = 0
    draws2 = 0

    for i in range(6):
        if i % 2 == 0:
            agent1 = MinimaxAgent(seed=42+i, max_depth=2, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15)
            agent2 = MinimaxAgent(seed=42+i, max_depth=2, weights=TERRITORY_SAFETY_WEIGHTS, max_moves=15)
            only_is_p1 = True
        else:
            agent1 = MinimaxAgent(seed=42+i, max_depth=2, weights=TERRITORY_SAFETY_WEIGHTS, max_moves=15)
            agent2 = MinimaxAgent(seed=42+i, max_depth=2, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15)
            only_is_p1 = False

        print(f"  Game {i+1} (TerritoryOnly as P{'1' if only_is_p1 else '2'})...", end=" ", flush=True)
        winner = run_match(agent1, agent2, config, 100 + i)

        if winner == Owner.PLAYER_1:
            if only_is_p1:
                wins_only += 1
                print("O wins")
            else:
                wins_safety += 1
                print("S wins")
        elif winner == Owner.PLAYER_2:
            if only_is_p1:
                wins_safety += 1
                print("S wins")
            else:
                wins_only += 1
                print("O wins")
        else:
            draws2 += 1
            print("draw")

    print(f"\nResult: TerritoryOnly {wins_only}-{wins_safety}-{draws2} Territory+Safety")

    print("\n" + "=" * 60)
    print("INTERPRETATION:")
    print("- If TerritoryOnly-d2 beats IntuitionBot: Simple metric + search works!")
    print("- If TerritoryOnly == Territory+Safety: Depth-2 handles threats")
    print("- If Territory+Safety wins: Need explicit threat evaluation")
    print("=" * 60)


if __name__ == "__main__":
    main()
