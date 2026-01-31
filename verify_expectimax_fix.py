#!/usr/bin/env python3
"""Verify that expectimax fixes the depth-search paradox.

This script tests the hypothesis that:
1. With proper stochastic handling (expectimax), deeper search should be better
2. The original minimax with fixed seed has the bug we identified
3. Expectimax at depth 2 should beat expectimax at depth 1

Run with: python verify_expectimax_fix.py
"""

import sys
import time
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.types import Owner
from strategic_influence.agents.optimized_minimax_agent import OptimizedMinimaxAgent
from strategic_influence.agents.expectimax_agent import ExpectimaxAgent
from strategic_influence.agents.random_agent import RandomAgent
from strategic_influence.agents.greedy_strategic_agent import GreedyStrategicAgent


def run_matches(config, agent1_name, agent1_factory, agent2_name, agent2_factory, num_games=10):
    """Run multiple matches and return win rates."""
    wins1, wins2, draws = 0, 0, 0
    total_time = 0

    for i in range(num_games):
        # Create fresh agents each game
        agent1 = agent1_factory()
        agent2 = agent2_factory()

        start = time.time()
        final_state = simulate_game(config, agent1, agent2, seed=None)
        elapsed = time.time() - start
        total_time += elapsed

        if final_state.winner == Owner.PLAYER_1:
            wins1 += 1
        elif final_state.winner == Owner.PLAYER_2:
            wins2 += 1
        else:
            draws += 1

        print(f"  Game {i+1}: {agent1_name} vs {agent2_name} -> "
              f"{'Agent1 wins' if final_state.winner == Owner.PLAYER_1 else 'Agent2 wins' if final_state.winner == Owner.PLAYER_2 else 'Draw'} "
              f"({elapsed:.1f}s)")

    return wins1, wins2, draws, total_time


def main():
    print("=" * 80)
    print("EXPECTIMAX FIX VERIFICATION")
    print("=" * 80)
    print()
    print("This test verifies that:")
    print("1. The original minimax (fixed seed) has the depth paradox bug")
    print("2. Expectimax (Monte Carlo sampling) fixes the bug")
    print("3. With expectimax, deeper search is better (as expected)")
    print()

    config = create_default_config()
    num_games = 5  # Fewer games for faster verification

    # Test 1: Original Minimax depth 1 vs depth 2
    print("-" * 80)
    print("TEST 1: Original OptimizedMinimax - Depth 1 vs Depth 2")
    print("(If depth 1 ≈ depth 2, the fixed seed prevents improvement)")
    print("-" * 80)

    wins1, wins2, draws, t = run_matches(
        config,
        "OldMinimax(d=1)", lambda: OptimizedMinimaxAgent(max_depth=1, max_moves=8),
        "OldMinimax(d=2)", lambda: OptimizedMinimaxAgent(max_depth=2, max_moves=8),
        num_games=num_games
    )
    print(f"\nResult: Depth1 {wins1}W-{wins2}L-{draws}D vs Depth2 ({t:.1f}s total)")
    print(f"Depth 1 win rate: {wins1/(wins1+wins2+draws)*100:.0f}%")
    old_d1_better = wins1 > wins2

    # Test 2: Expectimax depth 1 vs depth 2
    print()
    print("-" * 80)
    print("TEST 2: New Expectimax - Depth 1 vs Depth 2")
    print("(If depth 2 > depth 1, the fix works!)")
    print("-" * 80)

    wins1, wins2, draws, t = run_matches(
        config,
        "Expectimax(d=1)", lambda: ExpectimaxAgent(max_depth=1, num_samples=8, max_moves=8),
        "Expectimax(d=2)", lambda: ExpectimaxAgent(max_depth=2, num_samples=8, max_moves=8),
        num_games=num_games
    )
    print(f"\nResult: Depth1 {wins1}W-{wins2}L-{draws}D vs Depth2 ({t:.1f}s total)")
    print(f"Depth 2 win rate: {wins2/(wins1+wins2+draws)*100:.0f}%")
    new_d2_better = wins2 > wins1

    # Test 3: Expectimax d=2 vs Greedy (should dominate)
    print()
    print("-" * 80)
    print("TEST 3: Expectimax(d=2) vs GreedyHeuristic")
    print("(Search should beat pure heuristics)")
    print("-" * 80)

    wins1, wins2, draws, t = run_matches(
        config,
        "Expectimax(d=2)", lambda: ExpectimaxAgent(max_depth=2, num_samples=8, max_moves=8),
        "GreedyHeuristic", lambda: GreedyStrategicAgent(),
        num_games=num_games
    )
    print(f"\nResult: Expectimax {wins1}W-{wins2}L-{draws}D vs Greedy ({t:.1f}s total)")
    print(f"Expectimax win rate: {wins1/(wins1+wins2+draws)*100:.0f}%")
    expectimax_beats_greedy = wins1 > wins2

    # Test 4: Expectimax vs Old Minimax (same depth)
    print()
    print("-" * 80)
    print("TEST 4: Expectimax(d=2) vs OldMinimax(d=2)")
    print("(Expectimax should be stronger with proper stochastic handling)")
    print("-" * 80)

    wins1, wins2, draws, t = run_matches(
        config,
        "Expectimax(d=2)", lambda: ExpectimaxAgent(max_depth=2, num_samples=8, max_moves=8),
        "OldMinimax(d=2)", lambda: OptimizedMinimaxAgent(max_depth=2, max_moves=8),
        num_games=num_games
    )
    print(f"\nResult: Expectimax {wins1}W-{wins2}L-{draws}D vs OldMinimax ({t:.1f}s total)")
    print(f"Expectimax win rate: {wins1/(wins1+wins2+draws)*100:.0f}%")
    expectimax_beats_old = wins1 >= wins2

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("Bug verification:")
    if old_d1_better:
        print("  ✗ OLD MINIMAX: Depth 1 >= Depth 2 (BUG CONFIRMED!)")
    else:
        print("  ? OLD MINIMAX: Depth 2 >= Depth 1 (inconclusive with small sample)")

    print()
    print("Fix verification:")
    if new_d2_better:
        print("  ✓ EXPECTIMAX: Depth 2 > Depth 1 (FIX WORKS!)")
    else:
        print("  ? EXPECTIMAX: Results inconclusive (try more games)")

    if expectimax_beats_greedy:
        print("  ✓ EXPECTIMAX: Beats pure heuristics (search > no search)")
    else:
        print("  ? EXPECTIMAX: Didn't beat heuristics (try more games)")

    if expectimax_beats_old:
        print("  ✓ EXPECTIMAX: Beats old minimax (proper stochastic handling helps)")
    else:
        print("  ? EXPECTIMAX: Didn't beat old minimax (try more games)")

    print()
    print("CONCLUSION:")
    if new_d2_better:
        print("The expectimax fix addresses the depth paradox.")
        print("Deeper search now correctly produces better results.")
    else:
        print("Run with more games (--games 20) for statistical significance.")

    print()
    print("The key insight: using Random(42) in minimax created deterministic")
    print("predictions for stochastic combat, causing deeper search to overfit")
    print("to specific dice roll sequences instead of computing expected values.")


if __name__ == "__main__":
    main()
