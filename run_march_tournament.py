#!/usr/bin/env python3
"""Run a tournament between March of Empires agents.

This script runs a round-robin tournament between all implemented agents
and provides comprehensive analysis of the results.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from march_of_empires import (
    GameConfig,
    create_default_config,
    Player,
)
from march_of_empires.agents import (
    RandomAgent,
    ExpansionAgent,
    AggressiveAgent,
    DefensiveAgent,
    BalancedHeuristicAgent,
    MCTSAgent,
)
from march_of_empires.tournament import run_tournament
from march_of_empires.game import run_game
from march_of_empires.cli.renderer import render_game_state


def create_agents():
    """Create all agents for the tournament."""
    return [
        RandomAgent(seed=42),
        ExpansionAgent(seed=42),
        AggressiveAgent(seed=42),
        DefensiveAgent(seed=42),
        BalancedHeuristicAgent(seed=42),
        MCTSAgent(seed=42, num_simulations=50),  # Reduced for speed
    ]


def analyze_strategies(tournament_result):
    """Analyze and print strategy insights from tournament results."""
    print("\n" + "=" * 60)
    print("STRATEGY ANALYSIS")
    print("=" * 60)

    rankings = tournament_result.get_rankings()

    # Win rate analysis
    print("\n--- Win Rate by Strategy Type ---")
    strategy_types = {
        "Random": ["Random"],
        "Growth-focused": ["Expansion"],
        "Combat-focused": ["Aggressive"],
        "Safety-focused": ["Defensive"],
        "Multi-factor": ["Balanced"],
        "Search-based": ["MCTS"],
    }

    for strategy_type, agent_names in strategy_types.items():
        total_wins = sum(
            tournament_result.agent_stats[name].wins
            for name in agent_names
            if name in tournament_result.agent_stats
        )
        total_games = sum(
            tournament_result.agent_stats[name].games_played
            for name in agent_names
            if name in tournament_result.agent_stats
        )
        if total_games > 0:
            win_rate = total_wins / total_games * 100
            print(f"  {strategy_type}: {win_rate:.1f}% win rate")

    # Head-to-head insights
    print("\n--- Key Matchup Insights ---")

    # Find biggest mismatches
    mismatches = []
    for (a1, a2), h2h in tournament_result.head_to_head.items():
        if h2h.total_games > 0:
            diff = abs(h2h.agent1_wins - h2h.agent2_wins)
            dominant = a1 if h2h.agent1_wins > h2h.agent2_wins else a2
            dominated = a2 if h2h.agent1_wins > h2h.agent2_wins else a1
            wins = max(h2h.agent1_wins, h2h.agent2_wins)
            mismatches.append((diff, dominant, dominated, wins, h2h.total_games))

    mismatches.sort(reverse=True)
    for diff, dominant, dominated, wins, total in mismatches[:5]:
        print(f"  {dominant} dominates {dominated}: {wins}/{total} wins")

    # Score analysis
    print("\n--- Average Score Analysis ---")
    for name, stats in rankings[:3]:
        print(f"  {name}: avg {stats.avg_score:.1f} hexes per game")

    # Strategy observations
    print("\n--- Strategy Observations ---")

    top_agent = rankings[0][0]
    bottom_agent = rankings[-1][0]

    print(f"  Best performing: {top_agent}")
    print(f"  Worst performing: {bottom_agent}")

    # Check if expansion beats aggressive (territory > combat early)
    exp_vs_agg = tournament_result.head_to_head.get(("Aggressive", "Expansion"))
    if exp_vs_agg is None:
        exp_vs_agg = tournament_result.head_to_head.get(("Expansion", "Aggressive"))
        if exp_vs_agg:
            if exp_vs_agg.agent1_wins > exp_vs_agg.agent2_wins:
                print("  Expansion-focused strategy beats aggressive approach")
            else:
                print("  Aggressive approach beats expansion-focused strategy")

    # Check balanced vs specialists
    balanced_stats = tournament_result.agent_stats.get("Balanced")
    if balanced_stats:
        specialist_avg = sum(
            s.win_rate for name, s in tournament_result.agent_stats.items()
            if name in ["Expansion", "Aggressive", "Defensive"]
        ) / 3
        if balanced_stats.win_rate > specialist_avg:
            print("  Multi-factor evaluation outperforms single-strategy specialists")


def run_sample_game(verbose=True):
    """Run a sample game to demonstrate gameplay."""
    print("\n" + "=" * 60)
    print("SAMPLE GAME: Balanced vs Expansion")
    print("=" * 60)

    config = create_default_config()
    agent1 = BalancedHeuristicAgent(seed=123)
    agent2 = ExpansionAgent(seed=456)

    result = run_game(agent1, agent2, config, verbose=verbose)

    print(f"\nFinal Result:")
    print(f"  {agent1.name} (P1): {result.p1_score} hexes")
    print(f"  {agent2.name} (P2): {result.p2_score} hexes")
    print(f"  Winner: {result.winner if result.winner else 'Draw'}")
    print(f"  Total turns: {result.total_turns}")

    # Show final state
    print("\n" + render_game_state(result.final_state, config))

    return result


def main():
    """Run the tournament and analysis."""
    print("=" * 60)
    print("MARCH OF EMPIRES - AI TOURNAMENT")
    print("=" * 60)
    print()

    # Create agents
    agents = create_agents()
    print(f"Agents participating: {[a.name for a in agents]}")
    print()

    # Run tournament
    print("Running tournament...")
    config = create_default_config()

    # Run fewer games for faster results
    tournament_result = run_tournament(
        agents=agents,
        games_per_matchup=20,  # 10 games each side
        config=config,
        verbose=True,
    )

    # Analyze strategies
    analyze_strategies(tournament_result)

    # Run a sample game with visualization
    run_sample_game(verbose=True)

    print("\n" + "=" * 60)
    print("TOURNAMENT COMPLETE")
    print("=" * 60)

    return tournament_result


if __name__ == "__main__":
    main()
