#!/usr/bin/env python3
"""Quick benchmark of agent move times.

Run with: python benchmark_move_time.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.engine import create_game, apply_setup
from strategic_influence.types import Owner
from strategic_influence.agents.minimax_agent import MinimaxAgent
from strategic_influence.agents.greedy_strategic_agent import GreedyStrategicAgent
from strategic_influence.agents.improved_mcts_agent import ImprovedMCTSAgent
from strategic_influence.agents.random_agent import RandomAgent
from strategic_influence.evaluation import TERRITORY_ONLY_WEIGHTS


def benchmark_agent_move(agent_name, agent, state, owner, config):
    """Benchmark a single move."""
    try:
        start = time.time()
        agent.choose_actions(state, owner, config)
        elapsed = time.time() - start
        return elapsed
    except Exception as e:
        print(f"ERROR {agent_name}: {e}")
        return None


def main():
    """Run benchmarks."""
    print("AI Agent Move Time Benchmark")
    print("="*80)

    config = create_default_config()

    # Create game state
    state = create_game(config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_1, config), config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_2, config), config)

    print(f"\nBoard size: {config.board_size}x{config.board_size}")
    print(f"Initial setup: P1={len(list(state.board.positions_owned_by(Owner.PLAYER_1)))}, "
          f"P2={len(list(state.board.positions_owned_by(Owner.PLAYER_2)))}")
    print("\nBenchmarking move times (5 samples each):")
    print(f"{'Agent':<30} {'Time (ms)':<15} {'Status':<15}")
    print("-" * 80)

    # Test different agents
    agents = [
        ("Random", RandomAgent()),
        ("Greedy-Heuristic", GreedyStrategicAgent()),
        ("Minimax(d=0)", MinimaxAgent(max_depth=0, weights=TERRITORY_ONLY_WEIGHTS)),
        ("Minimax(d=1)", MinimaxAgent(max_depth=1, weights=TERRITORY_ONLY_WEIGHTS)),
        ("Minimax(d=2)", MinimaxAgent(max_depth=2, weights=TERRITORY_ONLY_WEIGHTS, max_moves=10)),
        ("MCTS(100,0.0)", ImprovedMCTSAgent(num_simulations=100, rollout_smartness=0.0)),
        ("MCTS(100,0.7)", ImprovedMCTSAgent(num_simulations=100, rollout_smartness=0.7)),
        ("MCTS(50,0.7)", ImprovedMCTSAgent(num_simulations=50, rollout_smartness=0.7)),
    ]

    for agent_name, agent in agents:
        times = []
        for i in range(5):
            elapsed = benchmark_agent_move(agent_name, agent, state, Owner.PLAYER_1, config)
            if elapsed is None:
                break
            times.append(elapsed * 1000)  # Convert to ms

        if times:
            avg_ms = sum(times) / len(times)
            max_ms = max(times)

            if avg_ms > 30000:  # > 30 seconds
                status = "TOO SLOW"
            elif avg_ms > 5000:  # > 5 seconds
                status = "SLOW"
            elif avg_ms > 1000:  # > 1 second
                status = "MODERATE"
            else:
                status = "FAST"

            print(f"{agent_name:<30} {avg_ms:>10.1f} (max {max_ms:>10.1f})  {status:<15}")
        else:
            print(f"{agent_name:<30} ERROR")

    print("\n" + "="*80)
    print("Legend: FAST (<1s), MODERATE (1-5s), SLOW (5-30s), TOO SLOW (>30s)")


if __name__ == "__main__":
    main()
