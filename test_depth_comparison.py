#!/usr/bin/env python3
"""Test if deeper search helps Minimax.

If depth-2 beats depth-1, it confirms:
1. The search is working correctly
2. More lookahead = better play
"""
import sys
import time
sys.path.insert(0, "src")

from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.types import Owner
from strategic_influence.agents import MinimaxAgent, IntuitionAgent
from strategic_influence.evaluation import TERRITORY_ONLY_WEIGHTS


def run_match(agent1, agent2, config, seed: int):
    """Run a single match, return winner."""
    final_state = simulate_game(config, agent1, agent2, seed)
    return final_state.winner


def main():
    print("=" * 60)
    print("DEPTH COMPARISON TEST")
    print("Does looking further ahead help?")
    print("=" * 60)
    print("\nTiming (from previous run):")
    print("  Depth 1: ~0.8s/game")
    print("  Depth 2: ~60s/game")
    print("  Depth 3: ~17min/game (too slow!)")

    config = create_default_config()

    # Test 1: Depth 1 vs Depth 2
    print("\n" + "=" * 60)
    print("Test 1: TerritoryOnly depth-1 vs depth-2 (6 games)")
    print("-" * 50)

    wins_d1 = 0
    wins_d2 = 0
    draws = 0

    for i in range(6):
        if i % 2 == 0:
            agent1 = MinimaxAgent(seed=42+i, max_depth=1, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15)
            agent2 = MinimaxAgent(seed=42+i, max_depth=2, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15)
            d1_is_p1 = True
        else:
            agent1 = MinimaxAgent(seed=42+i, max_depth=2, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15)
            agent2 = MinimaxAgent(seed=42+i, max_depth=1, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15)
            d1_is_p1 = False

        print(f"  Game {i+1} (depth-1 as P{'1' if d1_is_p1 else '2'})...", end=" ", flush=True)
        start = time.time()
        winner = run_match(agent1, agent2, config, 42 + i)
        elapsed = time.time() - start

        if winner == Owner.PLAYER_1:
            if d1_is_p1:
                wins_d1 += 1
                print(f"d1 wins ({elapsed:.0f}s)")
            else:
                wins_d2 += 1
                print(f"d2 wins ({elapsed:.0f}s)")
        elif winner == Owner.PLAYER_2:
            if d1_is_p1:
                wins_d2 += 1
                print(f"d2 wins ({elapsed:.0f}s)")
            else:
                wins_d1 += 1
                print(f"d1 wins ({elapsed:.0f}s)")
        else:
            draws += 1
            print(f"draw ({elapsed:.0f}s)")

    print(f"\nResult: Depth-1 {wins_d1} - {wins_d2} - {draws} Depth-2")

    # Test 2: Depth-2 vs IntuitionBot (we know d2 loses, but let's confirm)
    print("\n" + "=" * 60)
    print("Test 2: TerritoryOnly depth-2 vs IntuitionBot (4 games)")
    print("-" * 50)

    wins_d2_v_int = 0
    wins_int = 0
    draws2 = 0

    for i in range(4):
        if i % 2 == 0:
            agent1 = MinimaxAgent(seed=42+i, max_depth=2, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15)
            agent2 = IntuitionAgent(seed=42+i)
            d2_is_p1 = True
        else:
            agent1 = IntuitionAgent(seed=42+i)
            agent2 = MinimaxAgent(seed=42+i, max_depth=2, weights=TERRITORY_ONLY_WEIGHTS, max_moves=15)
            d2_is_p1 = False

        print(f"  Game {i+1} (depth-2 as P{'1' if d2_is_p1 else '2'})...", end=" ", flush=True)
        start = time.time()
        winner = run_match(agent1, agent2, config, 100 + i)
        elapsed = time.time() - start

        if winner == Owner.PLAYER_1:
            if d2_is_p1:
                wins_d2_v_int += 1
                print(f"d2 wins ({elapsed:.0f}s)")
            else:
                wins_int += 1
                print(f"Int wins ({elapsed:.0f}s)")
        elif winner == Owner.PLAYER_2:
            if d2_is_p1:
                wins_int += 1
                print(f"Int wins ({elapsed:.0f}s)")
            else:
                wins_d2_v_int += 1
                print(f"d2 wins ({elapsed:.0f}s)")
        else:
            draws2 += 1
            print(f"draw ({elapsed:.0f}s)")

    print(f"\nResult: Depth-2 {wins_d2_v_int} - {wins_int} - {draws2} IntuitionBot")

    print("\n" + "=" * 60)
    print("INTERPRETATION:")
    print("- If depth-2 > depth-1: Search is working, more depth helps")
    print("- If depth-2 still loses to IntuitionBot: Need better evaluation, not just depth")
    print("=" * 60)


if __name__ == "__main__":
    main()
