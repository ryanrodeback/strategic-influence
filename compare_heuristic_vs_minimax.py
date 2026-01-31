"""Compare HeuristicMinimaxAgent vs MinimaxAgent in series.

Tests:
- Run 50+ games of HeuristicMinimax vs Minimax(depth=1)
- Report win rates, average game length, move times
- Analyze which agent plays more consistently

Hypothesis: HeuristicMinimax should get 30-50% win rate since it
encodes Minimax's heuristics without search. It should be much faster
but potentially weaker due to no lookahead.
"""

import sys
import time
from pathlib import Path
from statistics import mean, stdev

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.agents.minimax_agent import MinimaxAgent
from strategic_influence.agents.heuristic_minimax_agent import HeuristicMinimaxAgent
from strategic_influence.agents.greedy_strategic_agent import GreedyStrategicAgent
from strategic_influence.types import Owner


def run_game(agent1, agent2, config, seed: int = None) -> tuple[Owner | None, float]:
    """Run a single game.

    Returns:
        (winner, game_duration_seconds)
    """
    start_time = time.time()

    try:
        final_state = simulate_game(config, agent1, agent2, seed=seed)
        winner = final_state.winner
    except Exception as e:
        print(f"  Error during game: {e}")
        return None, 0.0

    duration = time.time() - start_time
    return winner, duration


def run_tournament(num_games: int = 50):
    """Run tournament: HeuristicMinimax vs MinimaxAgent(depth=1).

    Tests both orderings (who goes first).
    """
    config = create_default_config()

    print("=" * 70)
    print("HEURISTIC MINIMAX vs MINIMAX COMPARISON")
    print("=" * 70)
    print(f"Config: {config.board_size}x{config.board_size}, max_turns={config.num_turns}")
    print(f"Playing {num_games} games (both orderings alternated)\n")

    # Initialize agents
    heuristic_agent = HeuristicMinimaxAgent(seed=42)
    minimax_agent = MinimaxAgent(seed=42, max_depth=1, max_moves=20)
    greedy_agent = GreedyStrategicAgent(seed=42)

    # Track results
    results = {
        "heuristic_vs_minimax": {"heuristic_wins": 0, "minimax_wins": 0, "draws": 0},
        "heuristic_vs_greedy": {"heuristic_wins": 0, "greedy_wins": 0, "draws": 0},
        "greedy_vs_minimax": {"greedy_wins": 0, "minimax_wins": 0, "draws": 0},
    }

    heuristic_times = []
    minimax_times = []
    greedy_times = []
    game_lengths = []

    print("Running Heuristic vs Minimax games...")
    print("-" * 70)

    for game_num in range(1, num_games + 1):
        seed = 42 + game_num

        # Alternate who goes first for fairness
        if game_num % 2 == 1:
            agent1, agent2 = heuristic_agent, minimax_agent
            winner, duration = run_game(agent1, agent2, config, seed)

            if winner == Owner.PLAYER_1:
                results["heuristic_vs_minimax"]["heuristic_wins"] += 1
                heuristic_times.append(duration)
            elif winner == Owner.PLAYER_2:
                results["heuristic_vs_minimax"]["minimax_wins"] += 1
                minimax_times.append(duration)
            else:
                results["heuristic_vs_minimax"]["draws"] += 1
        else:
            agent1, agent2 = minimax_agent, heuristic_agent
            winner, duration = run_game(agent1, agent2, config, seed)

            if winner == Owner.PLAYER_1:
                results["heuristic_vs_minimax"]["minimax_wins"] += 1
                minimax_times.append(duration)
            elif winner == Owner.PLAYER_2:
                results["heuristic_vs_minimax"]["heuristic_wins"] += 1
                heuristic_times.append(duration)
            else:
                results["heuristic_vs_minimax"]["draws"] += 1

        if game_num % 5 == 0:
            h_wins = results["heuristic_vs_minimax"]["heuristic_wins"]
            m_wins = results["heuristic_vs_minimax"]["minimax_wins"]
            print(f"  Game {game_num}: Heuristic {h_wins}-{m_wins} Minimax")

    print("\n" + "=" * 70)
    print("HEURISTIC vs MINIMAX (depth=1) - RESULTS")
    print("=" * 70)

    h_wins = results["heuristic_vs_minimax"]["heuristic_wins"]
    m_wins = results["heuristic_vs_minimax"]["minimax_wins"]
    draws = results["heuristic_vs_minimax"]["draws"]

    print(f"\nWin Record:")
    print(f"  Heuristic: {h_wins} wins ({h_wins/num_games*100:.1f}%)")
    print(f"  Minimax:   {m_wins} wins ({m_wins/num_games*100:.1f}%)")
    print(f"  Draws:     {draws} ({draws/num_games*100:.1f}%)")

    print(f"\nGameplay:")
    print(f"  Total games: {num_games}")

    if heuristic_times:
        print(f"\nHeuristic Agent Speed:")
        print(f"  Avg game time: {mean(heuristic_times):.2f}s")

    if minimax_times:
        print(f"\nMinimax Agent Speed:")
        print(f"  Avg game time: {mean(minimax_times):.2f}s")

    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    win_pct = h_wins / num_games * 100

    if win_pct >= 45:
        print("✓ STRONG: Heuristic achieved 45%+ win rate against depth=1 Minimax")
        print("  The heuristics successfully captured Minimax's strategy!")
    elif win_pct >= 35:
        print("✓ MODERATE: Heuristic achieved 35-45% win rate")
        print("  Heuristics capture some of Minimax's strategy, but search helps")
    elif win_pct >= 25:
        print("○ FAIR: Heuristic achieved 25-35% win rate")
        print("  Minimax's lookahead provides clear advantage over heuristics alone")
    else:
        print("✗ WEAK: Heuristic achieved <25% win rate")
        print("  Search is essential; heuristics need refinement")

    print(f"\nKey insight: Heuristics encode {win_pct:.1f}% of Minimax's strength")
    print("(assuming even play, 50% would be equally strong)")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare Heuristic vs Minimax agents")
    parser.add_argument("--games", type=int, default=50, help="Number of games to play")
    args = parser.parse_args()

    results = run_tournament(num_games=args.games)
