"""Comprehensive test of HeuristicMinimaxAgent vs other agents.

This tests the hypothesis: can pure heuristics capture Minimax's strength?

Key question: What's the difference between:
1. Picking locally-optimal moves (heuristic)
2. Searching 1-ply to see opponent's response (Minimax depth=1)

Results will show how much of Minimax's strength comes from search vs heuristics.
"""

import sys
import time
from pathlib import Path
from statistics import mean, stdev

sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.agents.minimax_agent import MinimaxAgent
from strategic_influence.agents.heuristic_minimax_agent import HeuristicMinimaxAgent
from strategic_influence.agents.greedy_strategic_agent import GreedyStrategicAgent
from strategic_influence.agents.random_agent import RandomAgent
from strategic_influence.types import Owner


def run_tournament(agent_pairs: list[tuple[str, object, str, object]], num_games: int = 30):
    """Run tournament between agent pairs.

    Args:
        agent_pairs: List of (name1, agent1, name2, agent2) tuples
        num_games: Number of games per pair

    Returns:
        Dict of results
    """
    config = create_default_config()
    results = {}

    for name1, agent1, name2, agent2 in agent_pairs:
        matchup = f"{name1} vs {name2}"
        results[matchup] = {"p1_wins": 0, "p2_wins": 0, "draws": 0, "times": []}

        print(f"\n{matchup}")
        print("-" * 60)

        for game_num in range(1, num_games + 1):
            seed = 100 + game_num

            # Alternate starting positions
            if game_num % 2 == 1:
                a1, a2 = agent1, agent2
                name_a1, name_a2 = name1, name2
            else:
                a1, a2 = agent2, agent1
                name_a1, name_a2 = name2, name1

            start = time.time()
            try:
                a1.reset()
                a2.reset()
                final_state = simulate_game(config, a1, a2, seed=seed)
                elapsed = time.time() - start

                winner = final_state.winner
                if winner == Owner.PLAYER_1:
                    results[matchup]["p1_wins"] += 1
                    if game_num % 2 == 1:
                        print(f"  Game {game_num:2d}: {name_a1:20} wins  ({elapsed:.2f}s)")
                    else:
                        print(f"  Game {game_num:2d}: {name_a2:20} wins  ({elapsed:.2f}s)")
                elif winner == Owner.PLAYER_2:
                    results[matchup]["p2_wins"] += 1
                    if game_num % 2 == 1:
                        print(f"  Game {game_num:2d}: {name_a2:20} wins  ({elapsed:.2f}s)")
                    else:
                        print(f"  Game {game_num:2d}: {name_a1:20} wins  ({elapsed:.2f}s)")
                else:
                    results[matchup]["draws"] += 1
                    print(f"  Game {game_num:2d}: DRAW  ({elapsed:.2f}s)")

                results[matchup]["times"].append(elapsed)

            except Exception as e:
                print(f"  Game {game_num:2d}: ERROR - {e}")

    return results


def print_summary(results):
    """Print tournament summary."""
    print("\n" + "=" * 70)
    print("TOURNAMENT SUMMARY")
    print("=" * 70)

    for matchup, data in results.items():
        p1_wins = data["p1_wins"]
        p2_wins = data["p2_wins"]
        draws = data["draws"]
        total = p1_wins + p2_wins + draws

        print(f"\n{matchup}:")
        print(f"  Player 1 (name1): {p1_wins}/{total} ({p1_wins/total*100:.1f}%)")
        print(f"  Player 2 (name2): {p2_wins}/{total} ({p2_wins/total*100:.1f}%)")
        if draws > 0:
            print(f"  Draws: {draws}/{total}")

        if data["times"]:
            avg_time = mean(data["times"])
            print(f"  Avg game time: {avg_time:.2f}s")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive heuristic vs minimax test")
    parser.add_argument("--games", type=int, default=30, help="Games per matchup")
    args = parser.parse_args()

    config = create_default_config()

    # Create agents
    heuristic = HeuristicMinimaxAgent(seed=42)
    greedy = GreedyStrategicAgent(seed=42)
    minimax_d1 = MinimaxAgent(seed=42, max_depth=1, max_moves=20)
    minimax_d2 = MinimaxAgent(seed=42, max_depth=2, max_moves=20)
    random = RandomAgent(seed=42)

    print("=" * 70)
    print("HEURISTIC VS MINIMAX: COMPREHENSIVE COMPARISON")
    print("=" * 70)
    print(f"\nTesting {args.games} games per matchup\n")

    pairs = [
        ("HeuristicMinimax", heuristic, "Minimax(d=1)", minimax_d1),
        ("HeuristicMinimax", heuristic, "GreedyStrategic", greedy),
        ("GreedyStrategic", greedy, "Minimax(d=1)", minimax_d1),
        ("Minimax(d=1)", minimax_d1, "Minimax(d=2)", minimax_d2),
        ("HeuristicMinimax", heuristic, "Random", random),
    ]

    results = run_tournament(pairs, num_games=args.games)
    print_summary(results)

    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)

    # Analyze
    h_vs_m = results.get("HeuristicMinimax vs Minimax(d=1)", {})
    h_vs_g = results.get("HeuristicMinimax vs GreedyStrategic", {})
    g_vs_m = results.get("GreedyStrategic vs Minimax(d=1)", {})

    if h_vs_m:
        h_winrate = h_vs_m["p1_wins"] / (h_vs_m["p1_wins"] + h_vs_m["p2_wins"] + h_vs_m["draws"]) * 100
        print(f"\n1. Heuristic vs Minimax(d=1): {h_winrate:.1f}% win rate")
        if h_winrate < 20:
            print("   INSIGHT: Search matters more than heuristics")
            print("   Even with 'correct' move selection, 1-ply lookahead wins")
        elif h_winrate < 45:
            print("   INSIGHT: Heuristics capture some but not all of Minimax's wisdom")
        else:
            print("   INSIGHT: Heuristics successfully capture Minimax's strategy!")

    if h_vs_g and h_vs_g["p1_wins"] + h_vs_g["p2_wins"] > 0:
        h_winrate = h_vs_g["p1_wins"] / (h_vs_g["p1_wins"] + h_vs_g["p2_wins"] + h_vs_g["draws"]) * 100
        print(f"\n2. Heuristic vs Greedy: {h_winrate:.1f}% win rate")
        print("   (Should be ~50% - they use nearly identical logic)")

    if g_vs_m and g_vs_m["p1_wins"] + g_vs_m["p2_wins"] > 0:
        g_winrate = g_vs_m["p1_wins"] / (g_vs_m["p1_wins"] + g_vs_m["p2_wins"] + g_vs_m["draws"]) * 100
        print(f"\n3. Greedy vs Minimax(d=1): {g_winrate:.1f}% win rate")
        if g_winrate < 20:
            print("   INSIGHT: Greedy (pure heuristic) loses to search")
