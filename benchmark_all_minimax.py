#!/usr/bin/env python3
"""Comprehensive benchmark comparing all minimax implementations.

Compares:
1. Original MinimaxAgent (buggy - times out)
2. OptimizedMinimaxAgent (works with time limits)
3. FixedMinimaxAgent (fixes the depth bug)

Shows how the fix and optimizations improve performance.

Run with: python benchmark_all_minimax.py
"""

import sys
import time
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.engine import create_game, apply_setup, apply_turn
from strategic_influence.types import Owner, TurnActions
from strategic_influence.agents.random_agent import RandomAgent
from strategic_influence.agents.minimax_agent import MinimaxAgent
from strategic_influence.agents.optimized_minimax_agent import OptimizedMinimaxAgent
from strategic_influence.agents.fixed_minimax_agent import FixedMinimaxAgent
from strategic_influence.evaluation import TERRITORY_ONLY_WEIGHTS


def setup_mid_game_state():
    """Create a game state after a few turns."""
    config = create_default_config()
    state = create_game(config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_1, config), config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_2, config), config)

    # Simulate a few turns
    rng = Random(42)
    agent_sim = FixedMinimaxAgent(max_depth=1, weights=TERRITORY_ONLY_WEIGHTS)
    for _ in range(2):
        p1_moves = agent_sim._generate_limited_moves(state, Owner.PLAYER_1, config)
        p2_moves = agent_sim._generate_limited_moves(state, Owner.PLAYER_2, config)

        if p1_moves and p2_moves:
            p1_action = agent_sim._order_moves(p1_moves, state, Owner.PLAYER_1, config)[0]
            p2_action = agent_sim._order_moves(p2_moves, state, Owner.PLAYER_2, config)[0]
            turn_actions = TurnActions(
                player1_actions=p1_action,
                player2_actions=p2_action,
                turn_number=state.current_turn + 1
            )
            state = apply_turn(state, turn_actions, config, rng)

    return config, state


def test_agent(agent_class, agent_name: str, depth: int, config, state, timeout: float = 10.0):
    """Test a single agent at a given depth."""
    print(f"\n  {agent_name} (depth={depth}):")
    sys.stdout.flush()

    # Create agent with appropriate parameters
    if agent_class == MinimaxAgent:
        agent = agent_class(
            seed=42,
            max_depth=depth,
            weights=TERRITORY_ONLY_WEIGHTS,
            verbose=False
        )
    else:
        agent = agent_class(
            seed=42,
            max_depth=depth,
            weights=TERRITORY_ONLY_WEIGHTS,
            time_limit_sec=timeout,
            verbose=False
        )

    start = time.time()

    try:
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Timed out after {timeout}s")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout) + 2)

        action = agent.choose_actions(state, Owner.PLAYER_1, config)
        signal.alarm(0)
        elapsed = time.time() - start

        stats = agent.get_stats() if hasattr(agent, 'get_stats') else {}

        print(f"    ✓ {elapsed:.3f}s", end="")
        if stats:
            print(f" ({stats.get('nodes_searched', '?')} nodes", end="")
            if stats.get('prune_rate'):
                print(f", {stats['prune_rate']:.0%} pruned", end="")
            print(")", end="")
        print()

        return elapsed

    except TimeoutError:
        elapsed = time.time() - start
        print(f"    ✗ TIMEOUT after {elapsed:.1f}s")
        return None
    except Exception as e:
        elapsed = time.time() - start
        print(f"    ✗ ERROR after {elapsed:.1f}s: {type(e).__name__}")
        return None


def main():
    """Run comprehensive benchmark."""
    print("="*80)
    print("MINIMAX AGENT COMPARISON BENCHMARK")
    print("="*80)
    print("\nComparing three implementations:")
    print("1. Original MinimaxAgent (has depth bug)")
    print("2. OptimizedMinimaxAgent (works with time limits)")
    print("3. FixedMinimaxAgent (fixes the bug)")

    # Setup game state
    print("\nSetting up mid-game state...", end=" ", flush=True)
    config, state = setup_mid_game_state()
    p1_count = len(list(state.board.positions_owned_by(Owner.PLAYER_1)))
    p2_count = len(list(state.board.positions_owned_by(Owner.PLAYER_2)))
    print(f"✓ (P1={p1_count}, P2={p2_count} territories)")

    # Test each depth
    print("\n" + "-"*80)
    print("DEPTH 1 (one ply: our move + opponent response)")
    print("-"*80)

    results_d1 = {
        "Original": test_agent(MinimaxAgent, "Original MinimaxAgent", 1, config, state, timeout=10.0),
        "Optimized": test_agent(OptimizedMinimaxAgent, "OptimizedMinimaxAgent", 1, config, state, timeout=10.0),
        "Fixed": test_agent(FixedMinimaxAgent, "FixedMinimaxAgent", 1, config, state, timeout=10.0),
    }

    print("\n" + "-"*80)
    print("DEPTH 2 (two plies: our move + opponent + our response)")
    print("-"*80)

    results_d2 = {
        "Original": test_agent(MinimaxAgent, "Original MinimaxAgent", 2, config, state, timeout=10.0),
        "Optimized": test_agent(OptimizedMinimaxAgent, "OptimizedMinimaxAgent", 2, config, state, timeout=10.0),
        "Fixed": test_agent(FixedMinimaxAgent, "FixedMinimaxAgent", 2, config, state, timeout=10.0),
    }

    print("\n" + "-"*80)
    print("DEPTH 3 (three plies)")
    print("-"*80)

    results_d3 = {
        "Original": test_agent(MinimaxAgent, "Original MinimaxAgent", 3, config, state, timeout=10.0),
        "Optimized": test_agent(OptimizedMinimaxAgent, "OptimizedMinimaxAgent", 3, config, state, timeout=10.0),
        "Fixed": test_agent(FixedMinimaxAgent, "FixedMinimaxAgent", 3, config, state, timeout=10.0),
    }

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    print("\n[DEPTH 1]")
    for name, time_taken in results_d1.items():
        if time_taken is not None:
            print(f"  {name:20s}: {time_taken:.3f}s ✓")
        else:
            print(f"  {name:20s}: TIMEOUT ✗")

    print("\n[DEPTH 2]")
    for name, time_taken in results_d2.items():
        if time_taken is not None:
            print(f"  {name:20s}: {time_taken:.3f}s ✓")
        else:
            print(f"  {name:20s}: TIMEOUT ✗")

    print("\n[DEPTH 3]")
    for name, time_taken in results_d3.items():
        if time_taken is not None:
            print(f"  {name:20s}: {time_taken:.3f}s ✓")
        else:
            print(f"  {name:20s}: TIMEOUT ✗")

    # Analysis
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)

    if results_d1["Original"] is None:
        print("\n❌ ORIGINAL MINIMAX: Fails even at depth 1")
        print("   Reason: Infinite recursion due to depth tracking bug")
        print("   See INVESTIGATION_REPORT.md for details")

    if results_d2["Original"] is None:
        print("   Cannot test depth 2 due to depth 1 failure")

    if results_d2["Fixed"] is not None and results_d2["Fixed"] < 1.0:
        print("\n✅ FIXED MINIMAX: Works at depth 2")
        print(f"   Time: {results_d2['Fixed']:.3f}s")
        print("   The fix (adding depth-1 to _max_player) enables correct recursion")

    if results_d3["Fixed"] is not None:
        print("\n✅ FIXED MINIMAX: Also works at depth 3")
        print(f"   Time: {results_d3['Fixed']:.3f}s")
        print("   With time limits, depth 3 is viable for strategic play")

    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("""
The investigation reveals:

1. ORIGINAL MINIMAX is broken due to a depth tracking bug in line 391.
   When _max_player calls _min_opponent, it should pass (depth-1) not depth.
   This causes infinite recursion leading to timeouts.

2. OPTIMIZED MINIMAX works despite using similar code, because:
   - Time limits prevent infinite recursion from hanging
   - Limited move generation reduces branching
   - Still inefficient but avoids user-visible timeouts

3. FIXED MINIMAX properly corrects the depth bug and adds optimizations:
   - One-line fix to line 391: depth → depth-1
   - Time limits for safety
   - Move generation limiting
   - Transposition table support

RECOMMENDATION:
- Apply the one-line fix to MinimaxAgent line 391
- Add time limits (5-10 seconds per move)
- Use max_moves=20 and max_candidates_per_territory=4 to limit branching
- Test depth 2 for reliable fast play (< 1 second per move)
- Use depth 3 with time limits for deeper strategic play (< 10 seconds)
""")


if __name__ == "__main__":
    main()
