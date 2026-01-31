#!/usr/bin/env python3
"""Test minimax agent at different depths to understand performance and timeout issues.

Tests:
- Depth 0: Simple evaluation (should be very fast)
- Depth 1: One full turn ahead (should be fast)
- Depth 2: Two full turns ahead (currently used)
- Depth 3: Three full turns ahead (known to timeout)

Run with: PYTHONPATH=src python test_minimax_depths.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.types import Owner, TurnActions
from strategic_influence.agents.minimax_agent import MinimaxAgent
from strategic_influence.agents.greedy_strategic_agent import GreedyStrategicAgent
from strategic_influence.evaluation import TERRITORY_ONLY_WEIGHTS
from strategic_influence.engine import create_game, apply_setup, apply_turn
from random import Random


def test_minimax_move_time(depth: int, num_moves: int = 5, timeout: float = 30.0):
    """Test how long minimax takes to make moves at a given depth."""
    print(f"\n{'='*80}")
    print(f"Testing Minimax at depth {depth}")
    print(f"{'='*80}")

    config = create_default_config()
    agent = MinimaxAgent(max_depth=depth, weights=TERRITORY_ONLY_WEIGHTS, verbose=True)
    opponent = GreedyStrategicAgent()

    # Start a game and measure move times
    state = create_game(config)

    # Setup phase
    print("\nSetup phase...")
    p1_setup = agent.choose_setup(state, Owner.PLAYER_1, config)
    state = apply_setup(state, p1_setup, config)
    p2_setup = opponent.choose_setup(state, Owner.PLAYER_2, config)
    state = apply_setup(state, p2_setup, config)

    print(f"✓ Setup complete. Board: {len(list(state.board.positions_owned_by(Owner.PLAYER_1)))} vs {len(list(state.board.positions_owned_by(Owner.PLAYER_2)))} territories")

    # Measure move times
    move_times = []
    print(f"\nMeasuring {num_moves} moves...")

    for move_num in range(num_moves):
        if state.is_complete:
            print(f"Game ended after {move_num} moves")
            break

        print(f"\n  Move {move_num + 1}:")

        # Player 1's turn (our agent)
        try:
            print(f"    P1 thinking (depth={depth})...", end=" ", flush=True)
            start = time.time()
            p1_actions = agent.choose_actions(state, Owner.PLAYER_1, config)
            p1_time = time.time() - start
            move_times.append(p1_time)
            stats = agent.get_stats()

            print(f"✓ {p1_time:.2f}s ({stats['nodes_searched']} nodes, {stats['prune_rate']:.0%} pruned)")

            if p1_time > timeout:
                print(f"    ⚠ TIMEOUT ALERT: Move took {p1_time:.2f}s (limit: {timeout}s)")
                return False

        except Exception as e:
            print(f"✗ ERROR: {e}")
            return False

        # Player 2's turn (opponent)
        print(f"    P2 thinking...", end=" ", flush=True)
        start = time.time()
        p2_actions = opponent.choose_actions(state, Owner.PLAYER_2, config)
        p2_time = time.time() - start
        print(f"✓ {p2_time:.2f}s")

        # Apply both moves
        turn_actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=state.current_turn + 1,
        )
        state = apply_turn(state, turn_actions, config, Random(42))

        p1_count = len(list(state.board.positions_owned_by(Owner.PLAYER_1)))
        p2_count = len(list(state.board.positions_owned_by(Owner.PLAYER_2)))
        print(f"    Board: P1={p1_count} vs P2={p2_count}")

    if not move_times:
        print("No moves were made")
        return False

    avg_time = sum(move_times) / len(move_times)
    max_time = max(move_times)
    print(f"\nResults for depth {depth}:")
    print(f"  Average move time: {avg_time:.2f}s")
    print(f"  Max move time: {max_time:.2f}s")
    print(f"  Total moves: {len(move_times)}")

    if max_time > timeout:
        print(f"  ⚠ TIMEOUT EXCEEDED: Some moves took longer than {timeout}s")
        return False
    else:
        print(f"  ✓ All moves completed within {timeout}s limit")
        return True


def run_depth_comparison():
    """Run minimax at all depths and compare results."""
    print("\nMinimax Depth Performance Comparison")
    print("="*80)

    results = {}
    for depth in [0, 1, 2]:
        print(f"\nTesting depth {depth}...")
        success = test_minimax_move_time(depth, num_moves=3, timeout=30.0)
        results[depth] = success

        if not success:
            print(f"✗ Depth {depth} failed or exceeded timeout")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for depth, success in results.items():
        status = "✓ OK" if success else "✗ FAILED"
        print(f"Depth {depth}: {status}")

    return results


if __name__ == "__main__":
    run_depth_comparison()
