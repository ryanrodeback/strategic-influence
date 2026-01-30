#!/usr/bin/env python3
"""Test optimized Minimax with simplified move generation.

Tests:
1. Speed at each depth
2. Pruning efficacy
3. Tournament against IntuitionBot
"""
import sys
import time
sys.path.insert(0, "src")

from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.types import Owner
from strategic_influence.agents import MinimaxAgent, IntuitionAgent, DefensiveAgent
from strategic_influence.evaluation import TERRITORY_ONLY_WEIGHTS, BALANCED_WEIGHTS


def run_match(agent1, agent2, config, seed: int):
    """Run a single match, return winner."""
    final_state = simulate_game(config, agent1, agent2, seed)
    return final_state.winner


def main():
    print("=" * 60)
    print("OPTIMIZED MINIMAX TEST")
    print("Testing simplified move generation")
    print("=" * 60)

    config = create_default_config()

    # Test 1: Speed at each depth
    print("\n" + "=" * 60)
    print("Test 1: SPEED (time per game)")
    print("-" * 60)

    for depth in [1, 2, 3]:
        agent1 = MinimaxAgent(seed=42, max_depth=depth, weights=BALANCED_WEIGHTS, max_moves=50, verbose=True)
        agent2 = IntuitionAgent(seed=42)

        print(f"\nDepth {depth}:")
        start = time.time()
        run_match(agent1, agent2, config, seed=42)
        elapsed = time.time() - start
        print(f"  Time: {elapsed:.1f}s")

        # Get stats from last search
        stats = agent1.get_stats()
        print(f"  Nodes searched: {stats['nodes_searched']}")
        print(f"  Nodes pruned: {stats['nodes_pruned']}")
        print(f"  Prune rate: {stats['prune_rate']:.1%}")

    # Test 2: Depth comparison (does depth still help?)
    print("\n" + "=" * 60)
    print("Test 2: DEPTH COMPARISON (d1 vs d2)")
    print("-" * 60)

    wins_d1 = wins_d2 = draws = 0
    for i in range(4):
        if i % 2 == 0:
            agent1 = MinimaxAgent(seed=42+i, max_depth=1, weights=BALANCED_WEIGHTS, max_moves=50)
            agent2 = MinimaxAgent(seed=42+i, max_depth=2, weights=BALANCED_WEIGHTS, max_moves=50)
            d1_is_p1 = True
        else:
            agent1 = MinimaxAgent(seed=42+i, max_depth=2, weights=BALANCED_WEIGHTS, max_moves=50)
            agent2 = MinimaxAgent(seed=42+i, max_depth=1, weights=BALANCED_WEIGHTS, max_moves=50)
            d1_is_p1 = False

        winner = run_match(agent1, agent2, config, 42 + i)
        if winner == Owner.PLAYER_1:
            if d1_is_p1:
                wins_d1 += 1
            else:
                wins_d2 += 1
        elif winner == Owner.PLAYER_2:
            if d1_is_p1:
                wins_d2 += 1
            else:
                wins_d1 += 1
        else:
            draws += 1

    print(f"Depth-1 vs Depth-2: {wins_d1}-{wins_d2}-{draws}")

    # Test 3: Tournament against heuristic bots
    print("\n" + "=" * 60)
    print("Test 3: TOURNAMENT vs IntuitionBot")
    print("-" * 60)

    # Test depth-2 vs IntuitionBot
    print("\nMinimax depth-2 vs IntuitionBot (6 games):")
    wins_mm = wins_int = draws_t = 0

    for i in range(6):
        if i % 2 == 0:
            agent1 = MinimaxAgent(seed=42+i, max_depth=2, weights=BALANCED_WEIGHTS, max_moves=50)
            agent2 = IntuitionAgent(seed=42+i)
            mm_is_p1 = True
        else:
            agent1 = IntuitionAgent(seed=42+i)
            agent2 = MinimaxAgent(seed=42+i, max_depth=2, weights=BALANCED_WEIGHTS, max_moves=50)
            mm_is_p1 = False

        print(f"  Game {i+1} (Minimax as P{'1' if mm_is_p1 else '2'})...", end=" ", flush=True)
        start = time.time()
        winner = run_match(agent1, agent2, config, 42 + i)
        elapsed = time.time() - start

        if winner == Owner.PLAYER_1:
            if mm_is_p1:
                wins_mm += 1
                print(f"MM wins ({elapsed:.0f}s)")
            else:
                wins_int += 1
                print(f"Int wins ({elapsed:.0f}s)")
        elif winner == Owner.PLAYER_2:
            if mm_is_p1:
                wins_int += 1
                print(f"Int wins ({elapsed:.0f}s)")
            else:
                wins_mm += 1
                print(f"MM wins ({elapsed:.0f}s)")
        else:
            draws_t += 1
            print(f"draw ({elapsed:.0f}s)")

    print(f"\nResult: Minimax-d2 {wins_mm}-{wins_int}-{draws_t} IntuitionBot")

    # Test 4: Can we run depth-3 now?
    print("\n" + "=" * 60)
    print("Test 4: DEPTH-3 FEASIBILITY")
    print("-" * 60)

    print("\nTrying depth-3 vs IntuitionBot (2 games):")
    wins_d3 = wins_int_3 = draws_3 = 0

    for i in range(2):
        if i % 2 == 0:
            agent1 = MinimaxAgent(seed=42+i, max_depth=3, weights=BALANCED_WEIGHTS, max_moves=50)
            agent2 = IntuitionAgent(seed=42+i)
            d3_is_p1 = True
        else:
            agent1 = IntuitionAgent(seed=42+i)
            agent2 = MinimaxAgent(seed=42+i, max_depth=3, weights=BALANCED_WEIGHTS, max_moves=50)
            d3_is_p1 = False

        print(f"  Game {i+1} (depth-3 as P{'1' if d3_is_p1 else '2'})...", end=" ", flush=True)
        start = time.time()
        winner = run_match(agent1, agent2, config, 100 + i)
        elapsed = time.time() - start

        if winner == Owner.PLAYER_1:
            if d3_is_p1:
                wins_d3 += 1
                print(f"d3 wins ({elapsed:.0f}s)")
            else:
                wins_int_3 += 1
                print(f"Int wins ({elapsed:.0f}s)")
        elif winner == Owner.PLAYER_2:
            if d3_is_p1:
                wins_int_3 += 1
                print(f"Int wins ({elapsed:.0f}s)")
            else:
                wins_d3 += 1
                print(f"d3 wins ({elapsed:.0f}s)")
        else:
            draws_3 += 1
            print(f"draw ({elapsed:.0f}s)")

    print(f"\nResult: Depth-3 {wins_d3}-{wins_int_3}-{draws_3} IntuitionBot")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)


if __name__ == "__main__":
    main()
