#!/usr/bin/env python3
"""Extended tournament with more rounds and detailed statistics.

Run with: python extended_tournament.py
"""

import sys
import time
from pathlib import Path
from collections import defaultdict

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


def run_tournament_extended(config, agents, rounds=3):
    """Run extended tournament with detailed statistics."""
    print(f"\nExtended Tournament: {len(agents)} agents × {rounds} round(s)")
    print("="*100)

    results = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "territories": [], "times": []})
    match_count = 0
    total_matches = len(agents) * (len(agents) - 1) * rounds // 2

    for round_num in range(rounds):
        print(f"\nRound {round_num + 1}:")
        for i, (agent1_name, agent1) in enumerate(agents):
            for j, (agent2_name, agent2) in enumerate(agents):
                if i >= j:
                    continue

                match_count += 1
                print(f"  [{match_count:2}/{total_matches}] {agent1_name:25} vs {agent2_name:25} ", end="", flush=True)

                agent1.reset()
                agent2.reset()

                try:
                    start_time = time.time()
                    final_state = simulate_game(config, agent1, agent2, seed=None)
                    elapsed = time.time() - start_time

                    winner = final_state.winner
                    p1_territories = len(list(final_state.board.positions_owned_by(Owner.PLAYER_1)))
                    p2_territories = len(list(final_state.board.positions_owned_by(Owner.PLAYER_2)))

                    results[agent1_name]["territories"].append(p1_territories)
                    results[agent2_name]["territories"].append(p2_territories)
                    results[agent1_name]["times"].append(elapsed)
                    results[agent2_name]["times"].append(elapsed)

                    if winner == Owner.PLAYER_1:
                        results[agent1_name]["wins"] += 1
                        results[agent2_name]["losses"] += 1
                        print(f"✓ {agent1_name} wins ({p1_territories}-{p2_territories} territories)")
                    elif winner == Owner.PLAYER_2:
                        results[agent2_name]["wins"] += 1
                        results[agent1_name]["losses"] += 1
                        print(f"✗ {agent2_name} wins ({p2_territories}-{p1_territories} territories)")
                    else:
                        results[agent1_name]["draws"] += 1
                        results[agent2_name]["draws"] += 1
                        print(f"= Draw ({p1_territories}-{p2_territories} territories)")

                except Exception as e:
                    print(f"ERROR: {e}")

    # Print final results
    print("\n" + "="*100)
    print("FINAL RESULTS")
    print("="*100)

    rankings = sorted(
        [(name, data) for name, data in results.items()],
        key=lambda x: (x[1]["wins"], -x[1]["losses"]),
        reverse=True,
    )

    print(f"\n{'Rank':<5} {'Agent':<30} {'Record':<20} {'Win %':<10} {'Avg Terr':<12} {'Avg Time':<12}")
    print("-"*100)

    for rank, (name, data) in enumerate(rankings, 1):
        total = data["wins"] + data["losses"] + data["draws"]
        record = f"{data['wins']}W-{data['losses']}L-{data['draws']}D"
        wr = data["wins"] / total if total > 0 else 0
        avg_terr = sum(data["territories"]) / len(data["territories"]) if data["territories"] else 0
        avg_time = sum(data["times"]) / len(data["times"]) if data["times"] else 0
        print(f"{rank:<5} {name:<30} {record:<20} {wr:>8.1%}  {avg_terr:>10.2f}  {avg_time:>10.2f}s")

    print("\n" + "="*100)

    return results


def main():
    """Run extended benchmark."""
    print("\nStrategic Influence - Extended AI Tournament")
    print("="*100)

    config = create_default_config()

    print(f"Board size: {config.board_size}x{config.board_size}")
    print(f"Game duration: {config.num_turns} turns")

    # Build diverse agent list
    agents = [
        ("Random", RandomAgent()),
        ("GreedyHeuristic", GreedyStrategicAgent()),
        ("OptimizedMinimax(d=1)", OptimizedMinimaxAgent(max_depth=1, max_moves=8)),
        ("MCTS-Random(100)", ImprovedMCTSAgent(num_simulations=100, rollout_smartness=0.0)),
        ("MCTS-Heuristic(100)", ImprovedMCTSAgent(num_simulations=100, rollout_smartness=0.7)),
        ("MCTS-Heuristic(50)", ImprovedMCTSAgent(num_simulations=50, rollout_smartness=0.7)),
    ]

    start_time = time.time()
    results = run_tournament_extended(config, agents, rounds=2)
    total_time = time.time() - start_time

    print(f"\nTotal benchmark time: {total_time:.1f}s")
    print("Recommendation: Use OptimizedMinimax(d=1) for strong competitive play")


if __name__ == "__main__":
    main()
