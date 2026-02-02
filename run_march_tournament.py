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
    MCTSAgent,
    MinimaxAgent,
    TerritoryRushAgent,
    GreedySettlerAgent,
)
from march_of_empires.tournament import run_tournament
from march_of_empires.game import run_game
from march_of_empires.cli.renderer import render_game_state


def create_agents():
    """Create all agents for the tournament.

    Includes the improved agents:
    - Random: Baseline
    - Expansion: Original best agent
    - MCTS: Improved with expansion-focused rollouts
    - Minimax: Alpha-beta search with position evaluation
    - TerritoryRush: Ultra-aggressive expansion
    - GreedySettler: Simple but effective greedy expansion
    """
    return [
        RandomAgent(seed=42),
        ExpansionAgent(seed=42),
        MCTSAgent(seed=42, num_simulations=100),  # Balanced for speed
        MinimaxAgent(seed=42, max_depth=2),  # Reduced for speed
        TerritoryRushAgent(seed=42),
        GreedySettlerAgent(seed=42),
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
        "Growth-focused": ["Expansion", "TerritoryRush", "GreedySettler"],
        "Search-based": ["MCTS", "Minimax"],
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

    # Check if search-based beats heuristic
    mcts_stats = tournament_result.agent_stats.get("MCTS")
    exp_stats = tournament_result.agent_stats.get("Expansion")
    if mcts_stats and exp_stats:
        if mcts_stats.win_rate > exp_stats.win_rate:
            print("  Search-based (MCTS) outperforms heuristic expansion")
        else:
            print("  Heuristic expansion competitive with search-based agents")

    # Check minimax vs others
    minimax_stats = tournament_result.agent_stats.get("Minimax")
    if minimax_stats:
        print(f"  Minimax agent: {minimax_stats.win_rate:.1f}% win rate")


def run_sample_game(verbose=True):
    """Run a sample game to demonstrate gameplay."""
    print("\n" + "=" * 60)
    print("SAMPLE GAME: TerritoryRush vs Expansion")
    print("=" * 60)

    config = create_default_config()
    agent1 = TerritoryRushAgent(seed=123)
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
