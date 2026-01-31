#!/usr/bin/env python3
"""Comprehensive tournament comparing all AI agents.

Run with: python run_tournament.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.types import Owner
from strategic_influence.agents.minimax_agent import MinimaxAgent
from strategic_influence.agents.optimized_minimax_agent import OptimizedMinimaxAgent
from strategic_influence.agents.improved_mcts_agent import ImprovedMCTSAgent
from strategic_influence.agents.greedy_strategic_agent import GreedyStrategicAgent
from strategic_influence.agents.random_agent import RandomAgent
from strategic_influence.evaluation import TERRITORY_ONLY_WEIGHTS


def run_match(config, agent1_name, agent1, agent2_name, agent2, verbose=True):
    """Run a single match."""
    if verbose:
        print(f"  {agent1_name:25} vs {agent2_name:25} ", end="", flush=True)

    start_time = time.time()
    try:
        final_state = simulate_game(config, agent1, agent2, seed=None)
        elapsed = time.time() - start_time

        winner = final_state.winner
        p1_territories = len(list(final_state.board.positions_owned_by(Owner.PLAYER_1)))
        p2_territories = len(list(final_state.board.positions_owned_by(Owner.PLAYER_2)))

        if winner == Owner.PLAYER_1:
            result_str = f"✓ {agent1_name} wins"
        elif winner == Owner.PLAYER_2:
            result_str = f"✗ {agent2_name} wins"
        else:
            result_str = "= Draw"

        if verbose:
            print(f"{result_str:40} ({p1_territories}-{p2_territories} territories, {elapsed:.1f}s)")

        return winner, p1_territories, p2_territories, elapsed

    except Exception as e:
        if verbose:
            print(f"ERROR: {e}")
        return None, 0, 0, 0


def run_tournament(config, agents, rounds=1, verbose=True):
    """Run round-robin tournament."""
    results = {name: {"wins": 0, "losses": 0, "draws": 0} for name, _ in agents}
    total_time = 0
    match_count = 0
    total_matches = len(agents) * (len(agents) - 1) * rounds // 2

    if verbose:
        print(f"\nTournament: {len(agents)} agents × {rounds} round(s) = {total_matches} matches")
        print("="*100)

    for round_num in range(rounds):
        for i, (agent1_name, agent1) in enumerate(agents):
            for j, (agent2_name, agent2) in enumerate(agents):
                if i >= j:
                    continue

                match_count += 1
                if verbose:
                    print(f"[{match_count:2}/{total_matches}]", end=" ")

                agent1.reset()
                agent2.reset()

                winner, p1_terr, p2_terr, elapsed = run_match(
                    config, agent1_name, agent1, agent2_name, agent2, verbose=True
                )
                total_time += elapsed

                if winner == Owner.PLAYER_1:
                    results[agent1_name]["wins"] += 1
                    results[agent2_name]["losses"] += 1
                elif winner == Owner.PLAYER_2:
                    results[agent2_name]["wins"] += 1
                    results[agent1_name]["losses"] += 1
                else:
                    results[agent1_name]["draws"] += 1
                    results[agent2_name]["draws"] += 1

    if verbose:
        print("\n" + "="*100)
        print("TOURNAMENT RESULTS")
        print("="*100)

        # Rankings
        rankings = sorted(
            [(name, stats) for name, stats in results.items()],
            key=lambda x: (x[1]["wins"], -x[1]["losses"]),
            reverse=True,
        )

        print(f"\n{'Rank':<5} {'Agent':<30} {'Record':<20} {'Win Rate':<12}")
        print("-"*70)

        for rank, (name, stats) in enumerate(rankings, 1):
            total = stats["wins"] + stats["losses"] + stats["draws"]
            record = f"{stats['wins']}W-{stats['losses']}L-{stats['draws']}D"
            wr = stats["wins"] / total if total > 0 else 0
            print(f"{rank:<5} {name:<30} {record:<20} {wr:>10.1%}")

        print(f"\nTotal time: {total_time:.1f}s")
        print(f"Average match time: {total_time/match_count:.1f}s")

    return results


def main():
    """Run the full benchmark."""
    print("\nStrategic Influence - AI Tournament")
    print("="*100)

    config = create_default_config()

    print(f"Board size: {config.board_size}x{config.board_size}")
    print(f"Game duration: {config.num_turns} turns")

    # Build agent list
    agents = [
        ("Random", RandomAgent()),
        ("GreedyHeuristic", GreedyStrategicAgent()),
        ("OptimizedMinimax(d=1)", OptimizedMinimaxAgent(max_depth=1, max_moves=8)),
        ("MCTS-Random(100)", ImprovedMCTSAgent(num_simulations=100, rollout_smartness=0.0)),
        ("MCTS-Heuristic(100)", ImprovedMCTSAgent(num_simulations=100, rollout_smartness=0.7)),
        ("MCTS-Heuristic(50)", ImprovedMCTSAgent(num_simulations=50, rollout_smartness=0.7)),
    ]

    # Run tournament
    results = run_tournament(config, agents, rounds=1, verbose=True)

    print("\n" + "="*100)
    print("Benchmark complete!")


if __name__ == "__main__":
    main()
