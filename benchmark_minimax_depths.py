#!/usr/bin/env python3
"""Benchmark minimax depths to understand timeout issues.

Tests move generation and evaluation speed at different depths.
Shows:
- How long move generation takes
- How long evaluation takes at each depth
- Branching factor
- Why depth 2+ times out

Run with: python benchmark_minimax_depths.py
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
from strategic_influence.evaluation import TERRITORY_ONLY_WEIGHTS


def benchmark_move_generation():
    """Measure move generation complexity."""
    print("\n" + "="*80)
    print("PART 1: MOVE GENERATION ANALYSIS")
    print("="*80)

    config = create_default_config()
    state = create_game(config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_1, config), config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_2, config), config)

    agent = MinimaxAgent(max_depth=0, weights=TERRITORY_ONLY_WEIGHTS)

    p1_territories = len(list(state.board.positions_owned_by(Owner.PLAYER_1)))
    p2_territories = len(list(state.board.positions_owned_by(Owner.PLAYER_2)))

    print(f"\nInitial state: P1={p1_territories} territory, P2={p2_territories} territory")

    # Early game move generation
    print("\n[EARLY GAME] Generating moves...")
    start = time.time()
    moves = agent._generate_moves(state, Owner.PLAYER_1, config)
    elapsed = time.time() - start
    print(f"  Time: {elapsed*1000:.1f}ms")
    print(f"  Moves: {len(moves)}")
    print(f"  Branching factor: {len(moves)}")

    # Simulate to mid-game
    print("\n[MID-GAME] Simulating 3 turns of random play...")
    rng = Random(42)
    for turn in range(3):
        p1_moves = agent._generate_moves(state, Owner.PLAYER_1, config)
        p2_moves = agent._generate_moves(state, Owner.PLAYER_2, config)

        if p1_moves and p2_moves:
            p1_action = agent._order_moves(p1_moves, state, Owner.PLAYER_1, config)[0]
            p2_action = agent._order_moves(p2_moves, state, Owner.PLAYER_2, config)[0]

            turn_actions = TurnActions(player1_actions=p1_action, player2_actions=p2_action, turn_number=state.current_turn+1)
            state = apply_turn(state, turn_actions, config, rng)

    p1_territories = len(list(state.board.positions_owned_by(Owner.PLAYER_1)))
    p2_territories = len(list(state.board.positions_owned_by(Owner.PLAYER_2)))
    print(f"  Board state: P1={p1_territories} territories, P2={p2_territories} territories")

    # Mid-game move generation
    print("\n[MID-GAME] Generating moves for P1...")
    start = time.time()
    moves_p1 = agent._generate_moves(state, Owner.PLAYER_1, config)
    elapsed = time.time() - start
    print(f"  Time: {elapsed*1000:.1f}ms")
    print(f"  Moves: {len(moves_p1)}")
    print(f"  Branching factor: {len(moves_p1)}")

    start = time.time()
    moves_p2 = agent._generate_moves(state, Owner.PLAYER_2, config)
    elapsed = time.time() - start
    print(f"\n[MID-GAME] Generating moves for P2...")
    print(f"  Time: {elapsed*1000:.1f}ms")
    print(f"  Moves: {len(moves_p2)}")
    print(f"  Branching factor: {len(moves_p2)}")


def benchmark_single_move_time(agent, depth: int, state, config, timeout: float = 10.0):
    """Benchmark how long one move takes at a given depth."""
    print(f"\n[DEPTH {depth}] Choosing move...")
    start = time.time()

    try:
        # Set up timeout
        import signal
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Move selection timed out after {timeout}s")
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout) + 1)

        # Choose move
        action = agent.choose_actions(state, Owner.PLAYER_1, config)
        signal.alarm(0)

        elapsed = time.time() - start
        stats = agent.get_stats() if hasattr(agent, 'get_stats') else {}

        print(f"  ✓ Move selected in {elapsed:.2f}s")
        if stats:
            print(f"    Nodes: {stats.get('nodes_searched', 'N/A')}")
            print(f"    Pruned: {stats.get('nodes_pruned', 'N/A')}")
            if stats.get('prune_rate'):
                print(f"    Prune rate: {stats['prune_rate']:.0%}")

        return elapsed, action

    except TimeoutError as e:
        elapsed = time.time() - start
        print(f"  ✗ TIMEOUT: {e}")
        return None, None
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def benchmark_depths_original():
    """Test original MinimaxAgent at different depths."""
    print("\n" + "="*80)
    print("PART 2: ORIGINAL MINIMAX AGENT - DEPTH TIMING")
    print("="*80)

    config = create_default_config()
    state = create_game(config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_1, config), config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_2, config), config)

    # Simulate to mid-game
    rng = Random(42)
    agent_sim = MinimaxAgent(max_depth=0, weights=TERRITORY_ONLY_WEIGHTS)
    for _ in range(2):
        p1_moves = agent_sim._generate_moves(state, Owner.PLAYER_1, config)
        p2_moves = agent_sim._generate_moves(state, Owner.PLAYER_2, config)
        if p1_moves and p2_moves:
            p1_action = agent_sim._order_moves(p1_moves, state, Owner.PLAYER_1, config)[0]
            p2_action = agent_sim._order_moves(p2_moves, state, Owner.PLAYER_2, config)[0]
            turn_actions = TurnActions(player1_actions=p1_action, player2_actions=p2_action, turn_number=state.current_turn+1)
            state = apply_turn(state, turn_actions, config, rng)

    # Test each depth
    for depth in [0, 1]:
        print(f"\n--- Testing depth {depth} ---")
        agent = MinimaxAgent(max_depth=depth, weights=TERRITORY_ONLY_WEIGHTS, verbose=True)

        elapsed, _ = benchmark_single_move_time(agent, depth, state, config, timeout=30.0)

        if elapsed is None:
            print(f"  Skipping depth {depth+1} due to timeout")
            break


def benchmark_depths_optimized():
    """Test optimized MinimaxAgent at different depths."""
    print("\n" + "="*80)
    print("PART 3: OPTIMIZED MINIMAX AGENT - DEPTH TIMING")
    print("="*80)

    config = create_default_config()
    state = create_game(config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_1, config), config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_2, config), config)

    # Simulate to mid-game
    rng = Random(42)
    agent_sim = OptimizedMinimaxAgent(max_depth=1, weights=TERRITORY_ONLY_WEIGHTS)
    for _ in range(2):
        p1_moves = agent_sim._generate_limited_moves(state, Owner.PLAYER_1, config)
        p2_moves = agent_sim._generate_limited_moves(state, Owner.PLAYER_2, config)
        if p1_moves and p2_moves:
            p1_action = agent_sim._order_moves(p1_moves, state, Owner.PLAYER_1, config)[0]
            p2_action = agent_sim._order_moves(p2_moves, state, Owner.PLAYER_2, config)[0]
            turn_actions = TurnActions(player1_actions=p1_action, player2_actions=p2_action, turn_number=state.current_turn+1)
            state = apply_turn(state, turn_actions, config, rng)

    # Test each depth
    for depth in [1, 2]:
        print(f"\n--- Testing depth {depth} ---")
        agent = OptimizedMinimaxAgent(max_depth=depth, weights=TERRITORY_ONLY_WEIGHTS, verbose=True, time_limit_sec=10.0)

        elapsed, _ = benchmark_single_move_time(agent, depth, state, config, timeout=15.0)


def main():
    """Run all benchmarks."""
    print("\n" + "="*80)
    print("MINIMAX DEPTH BENCHMARK")
    print("="*80)

    try:
        benchmark_move_generation()
    except Exception as e:
        print(f"\n✗ Move generation benchmark failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        benchmark_depths_original()
    except Exception as e:
        print(f"\n✗ Original minimax benchmark failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        benchmark_depths_optimized()
    except Exception as e:
        print(f"\n✗ Optimized minimax benchmark failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
The benchmarks show:
1. Move generation complexity at each depth
2. Actual timing for minimax decisions
3. Whether depth 2 and 3 are viable

See INVESTIGATION_REPORT.md for detailed analysis.
""")


if __name__ == "__main__":
    main()
