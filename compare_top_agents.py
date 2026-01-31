#!/usr/bin/env python3
"""Comprehensive tournament comparing ALL top agents fairly.

This script runs a definitive head-to-head comparison of:
- Best heuristic agents: GreedyStrategic, Defensive, Intuition
- Best minimax agents: OptimizedMinimax at depths 1 and 2
- Best MCTS agents: Random rollouts only (heuristic variants are broken)

Each matchup is played 10 times (5 as P1, 5 as P2) for statistical significance.
"""

import sys
import time
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.types import Owner

# Import all agents
from strategic_influence.agents.random_agent import RandomAgent
from strategic_influence.agents.greedy_strategic_agent import GreedyStrategicAgent
from strategic_influence.agents.defensive_agent import DefensiveAgent
from strategic_influence.agents.intuition_agent import IntuitionAgent
from strategic_influence.agents.optimized_minimax_agent import OptimizedMinimaxAgent
from strategic_influence.agents.improved_mcts_agent import ImprovedMCTSAgent


def run_matchup(config, agent1_name, agent1, agent2_name, agent2, games_per_side=5):
    """Run a matchup between two agents, alternating sides."""
    results = {"agent1_wins": 0, "agent2_wins": 0, "draws": 0, "total_time": 0}

    for game_num in range(games_per_side * 2):
        # Alternate who plays first
        if game_num < games_per_side:
            p1, p2 = agent1, agent2
            p1_is_agent1 = True
        else:
            p1, p2 = agent2, agent1
            p1_is_agent1 = False

        agent1.reset()
        agent2.reset()

        start_time = time.time()
        try:
            final_state = simulate_game(config, p1, p2, seed=game_num)
            elapsed = time.time() - start_time
            results["total_time"] += elapsed

            winner = final_state.winner
            if winner == Owner.PLAYER_1:
                if p1_is_agent1:
                    results["agent1_wins"] += 1
                else:
                    results["agent2_wins"] += 1
            elif winner == Owner.PLAYER_2:
                if p1_is_agent1:
                    results["agent2_wins"] += 1
                else:
                    results["agent1_wins"] += 1
            else:
                results["draws"] += 1

        except Exception as e:
            print(f"  ERROR in {agent1_name} vs {agent2_name}: {e}")
            results["draws"] += 1

    return results


def run_full_tournament(config, agents, games_per_side=5):
    """Run round-robin tournament with detailed head-to-head tracking."""
    agent_stats = {name: {"wins": 0, "losses": 0, "draws": 0, "time": 0} for name, _ in agents}
    head_to_head = defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0}))

    total_matchups = len(agents) * (len(agents) - 1) // 2
    matchup_num = 0

    print(f"\nRunning tournament: {len(agents)} agents, {total_matchups} matchups")
    print(f"Games per matchup: {games_per_side * 2} ({games_per_side} per side)")
    print("=" * 80)

    for i, (name1, agent1) in enumerate(agents):
        for j, (name2, agent2) in enumerate(agents):
            if i >= j:
                continue

            matchup_num += 1
            print(f"[{matchup_num:2}/{total_matchups}] {name1:25} vs {name2:25} ", end="", flush=True)

            results = run_matchup(config, name1, agent1, name2, agent2, games_per_side)

            # Record head-to-head
            head_to_head[name1][name2]["wins"] = results["agent1_wins"]
            head_to_head[name1][name2]["losses"] = results["agent2_wins"]
            head_to_head[name1][name2]["draws"] = results["draws"]
            head_to_head[name2][name1]["wins"] = results["agent2_wins"]
            head_to_head[name2][name1]["losses"] = results["agent1_wins"]
            head_to_head[name2][name1]["draws"] = results["draws"]

            # Update totals
            agent_stats[name1]["wins"] += results["agent1_wins"]
            agent_stats[name1]["losses"] += results["agent2_wins"]
            agent_stats[name1]["draws"] += results["draws"]
            agent_stats[name1]["time"] += results["total_time"] / 2

            agent_stats[name2]["wins"] += results["agent2_wins"]
            agent_stats[name2]["losses"] += results["agent1_wins"]
            agent_stats[name2]["draws"] += results["draws"]
            agent_stats[name2]["time"] += results["total_time"] / 2

            print(f"{results['agent1_wins']}-{results['agent2_wins']}-{results['draws']} ({results['total_time']:.1f}s)")

    return agent_stats, head_to_head


def print_rankings(agent_stats, head_to_head, agents):
    """Print tournament rankings and analysis."""
    print("\n" + "=" * 80)
    print("TOURNAMENT RESULTS")
    print("=" * 80)

    # Calculate win rates and sort
    rankings = []
    for name, stats in agent_stats.items():
        total = stats["wins"] + stats["losses"] + stats["draws"]
        win_rate = stats["wins"] / total if total > 0 else 0
        rankings.append((name, stats, win_rate, total))

    rankings.sort(key=lambda x: (x[2], -x[1]["losses"]), reverse=True)

    print(f"\n{'Rank':<5} {'Agent':<30} {'W-L-D':<15} {'Win Rate':<12} {'Avg Time':<10}")
    print("-" * 75)

    for rank, (name, stats, win_rate, total) in enumerate(rankings, 1):
        record = f"{stats['wins']}-{stats['losses']}-{stats['draws']}"
        avg_time = stats["time"] / total if total > 0 else 0
        print(f"{rank:<5} {name:<30} {record:<15} {win_rate:>10.1%} {avg_time:>8.2f}s")

    # Head-to-head matrix
    print("\n" + "=" * 80)
    print("HEAD-TO-HEAD MATRIX (Row vs Column: W-L-D)")
    print("=" * 80)

    agent_names = [name for name, _ in agents]

    # Print header
    print(f"\n{'':20}", end="")
    for name in agent_names:
        short = name[:9]
        print(f"{short:>12}", end="")
    print()
    print("-" * (20 + 12 * len(agent_names)))

    for name1 in agent_names:
        print(f"{name1:20}", end="")
        for name2 in agent_names:
            if name1 == name2:
                print(f"{'---':>12}", end="")
            else:
                h2h = head_to_head[name1][name2]
                result = f"{h2h['wins']}-{h2h['losses']}-{h2h['draws']}"
                print(f"{result:>12}", end="")
        print()

    return rankings


def analyze_by_category(rankings, agents):
    """Analyze best agents by category."""
    print("\n" + "=" * 80)
    print("ANALYSIS BY CATEGORY")
    print("=" * 80)

    # Categorize agents
    categories = {
        "Heuristic": ["GreedyStrategic", "Defensive", "Intuition"],
        "Minimax": ["OptMinimax(d=1)", "OptMinimax(d=2)"],
        "MCTS": ["MCTS-Random(100)", "MCTS-Random(200)"],
        "Baseline": ["Random"],
    }

    ranking_dict = {name: (rank, stats, wr) for rank, (name, stats, wr, _) in enumerate(rankings, 1)}

    for category, agent_names in categories.items():
        print(f"\n{category} Agents:")
        print("-" * 50)

        cat_agents = []
        for name in agent_names:
            if name in ranking_dict:
                rank, stats, wr = ranking_dict[name]
                cat_agents.append((name, rank, stats, wr))

        cat_agents.sort(key=lambda x: x[1])  # Sort by overall rank

        for name, rank, stats, wr in cat_agents:
            print(f"  #{rank:<3} {name:<25} {wr:.1%} ({stats['wins']}-{stats['losses']}-{stats['draws']})")

        if cat_agents:
            best = cat_agents[0]
            print(f"  >> BEST: {best[0]} (Rank #{best[1]}, {best[3]:.1%})")


def main():
    """Run the comprehensive tournament."""
    print("\n" + "=" * 80)
    print("STRATEGIC INFLUENCE - COMPREHENSIVE AGENT COMPARISON")
    print("=" * 80)

    config = create_default_config()
    print(f"\nGame: {config.board_size}x{config.board_size} board, {config.num_turns} turns")

    # Build comprehensive agent list (excluding broken OptMinimax d=0 and MCTS variants)
    agents = [
        # Baseline
        ("Random", RandomAgent(seed=42)),

        # Heuristic agents
        ("GreedyStrategic", GreedyStrategicAgent(seed=42)),
        ("Defensive", DefensiveAgent(seed=42)),
        ("Intuition", IntuitionAgent(seed=42)),

        # Minimax agents at different depths
        ("OptMinimax(d=1)", OptimizedMinimaxAgent(seed=42, max_depth=1)),
        ("OptMinimax(d=2)", OptimizedMinimaxAgent(seed=42, max_depth=2, time_limit_sec=10.0)),

        # MCTS with random rollouts (the only working variant)
        ("MCTS-Random(100)", ImprovedMCTSAgent(seed=42, num_simulations=100, rollout_smartness=0.0)),
        ("MCTS-Random(200)", ImprovedMCTSAgent(seed=42, num_simulations=200, rollout_smartness=0.0)),
    ]

    print(f"\nAgents in tournament: {len(agents)}")
    for name, _ in agents:
        print(f"  - {name}")

    # Run tournament
    start_time = time.time()
    agent_stats, head_to_head = run_full_tournament(config, agents, games_per_side=5)
    total_time = time.time() - start_time

    # Print results
    rankings = print_rankings(agent_stats, head_to_head, agents)

    # Analyze by category
    analyze_by_category(rankings, agents)

    print(f"\n{'=' * 80}")
    print(f"Tournament complete in {total_time:.1f}s")
    print(f"Total games played: {len(agents) * (len(agents) - 1) // 2 * 10}")

    # Print key findings
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)

    ranking_dict = {name: (rank, stats, wr) for rank, (name, stats, wr, _) in enumerate(rankings, 1)}

    # Find winners in each category
    for cat, names in [("Heuristic", ["GreedyStrategic", "Defensive", "Intuition"]),
                        ("Minimax", ["OptMinimax(d=1)", "OptMinimax(d=2)"]),
                        ("MCTS", ["MCTS-Random(100)", "MCTS-Random(200)"])]:
        best = min([(ranking_dict[n][0], n, ranking_dict[n][2]) for n in names if n in ranking_dict])
        print(f"\nBest {cat}: {best[1]} (Rank #{best[0]}, {best[2]:.1%} win rate)")

    return rankings, head_to_head


if __name__ == "__main__":
    rankings, h2h = main()
