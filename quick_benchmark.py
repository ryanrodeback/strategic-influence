#!/usr/bin/env python3
"""Quick benchmark with timeout protection.

Run with: python quick_benchmark.py
"""

import sys
import time
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.engine import create_game, apply_setup
from strategic_influence.types import Owner, GameState
from strategic_influence.agents.minimax_agent import MinimaxAgent
from strategic_influence.agents.greedy_strategic_agent import GreedyStrategicAgent
from strategic_influence.agents.improved_mcts_agent import ImprovedMCTSAgent
from strategic_influence.agents.random_agent import RandomAgent
from strategic_influence.evaluation import TERRITORY_ONLY_WEIGHTS


def timeout_handler(signum, frame):
    raise TimeoutError("Move exceeded time limit")


def benchmark_agent_move(agent_name, agent, state, owner, config, timeout_sec=10):
    """Benchmark a single move with timeout."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_sec)

    try:
        start = time.time()
        agent.choose_actions(state, owner, config)
        elapsed = time.time() - start
        signal.alarm(0)  # Cancel alarm
        return elapsed
    except TimeoutError:
        return None
    except Exception as e:
        signal.alarm(0)
        print(f"ERROR: {e}")
        return None


def main():
    """Run benchmarks."""
    print("AI Agent Move Time Benchmark (with Timeouts)")
    print("="*80)

    config = create_default_config()

    # Create a simple game state
    state = create_game(config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_1, config), config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_2, config), config)

    print(f"\nBoard size: {config.board_size}x{config.board_size}")
    p1_count = len(list(state.board.positions_owned_by(Owner.PLAYER_1)))
    p2_count = len(list(state.board.positions_owned_by(Owner.PLAYER_2)))
    print(f"Initial setup: P1={p1_count}, P2={p2_count}")
    print("\nBenchmarking move times (1 sample per agent, 10sec timeout):")
    print(f"{'Agent':<30} {'Time (ms)':<15} {'Status':<15}")
    print("-" * 80)

    agents = [
        ("Random", RandomAgent()),
        ("Greedy-Heuristic", GreedyStrategicAgent()),
        ("Minimax(d=0)", MinimaxAgent(max_depth=0, weights=TERRITORY_ONLY_WEIGHTS)),
        ("Minimax(d=1)", MinimaxAgent(max_depth=1, weights=TERRITORY_ONLY_WEIGHTS)),
        ("Minimax(d=2)", MinimaxAgent(max_depth=2, weights=TERRITORY_ONLY_WEIGHTS, max_moves=5)),
        ("MCTS(50,0.7)", ImprovedMCTSAgent(num_simulations=50, rollout_smartness=0.7)),
        ("MCTS(100,0.7)", ImprovedMCTSAgent(num_simulations=100, rollout_smartness=0.7)),
    ]

    for agent_name, agent in agents:
        print(f"{agent_name:<30}", end=" ", flush=True)
        elapsed_ms = benchmark_agent_move(agent_name, agent, state, Owner.PLAYER_1, config, timeout_sec=10)

        if elapsed_ms is None:
            print(f"TIMEOUT (>10s)")
        else:
            elapsed_ms *= 1000

            if elapsed_ms > 5000:
                status = "SLOW"
            elif elapsed_ms > 1000:
                status = "MODERATE"
            else:
                status = "FAST"

            print(f"{elapsed_ms:>10.1f} ms      {status:<15}")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
