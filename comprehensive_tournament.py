#!/usr/bin/env python3
"""Comprehensive tournament comparing all available AI agents.

Tests all agents against each other with:
- 20+ games per matchup
- Timeout handling (counts as loss)
- Detailed statistics tracking
- Head-to-head matrix generation
"""

import time
from dataclasses import dataclass, field
from typing import Callable
from random import Random
from collections import defaultdict

from src.strategic_influence.types import Owner
from src.strategic_influence.config import create_default_config
from src.strategic_influence.engine import simulate_game
from src.strategic_influence.agents import (
    RandomAgent,
    AggressiveAgent,
    DefensiveAgent,
    IntuitionAgent,
    MinimaxAgent,
    ImprovedMCTSAgent,
    GreedyStrategicAgent,
    HeuristicMinimaxAgent,
)
from src.strategic_influence.agents.optimized_minimax_agent import OptimizedMinimaxAgent
from src.strategic_influence.agents.mcts_variants import (
    MCTSHeuristicEval,
    MCTSMinimaxEval,
    MCTSHeuristicRollout,
)


@dataclass
class GameStats:
    """Statistics for a single game."""
    p1_name: str
    p2_name: str
    winner: Owner | None
    p1_territories: int
    p2_territories: int
    p1_stones: int
    p2_stones: int
    game_length: int
    timeout: bool = False


@dataclass
class AgentStats:
    """Cumulative statistics for an agent."""
    name: str
    wins: int = 0
    losses: int = 0
    draws: int = 0
    timeouts: int = 0
    total_territories: int = 0
    total_stones: int = 0
    total_game_length: int = 0
    games_played: int = 0

    @property
    def win_rate(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.wins / self.games_played

    @property
    def avg_territories(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.total_territories / self.games_played

    @property
    def avg_stones(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.total_stones / self.games_played

    @property
    def avg_game_length(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.total_game_length / self.games_played


class ComprehensiveTournament:
    """Run comprehensive tournament between multiple agents."""

    def __init__(self, games_per_matchup: int = 20, timeout_sec: float = 30.0):
        self.games_per_matchup = games_per_matchup
        self.timeout_sec = timeout_sec
        self.results: list[GameStats] = []
        self.agent_stats: dict[str, AgentStats] = {}
        self.head_to_head: dict[tuple[str, str], dict] = defaultdict(
            lambda: {"agent1_wins": 0, "agent2_wins": 0, "draws": 0, "timeouts": 0}
        )

    def create_all_agents(self) -> list[tuple[str, Callable]]:
        """Create all available agents."""
        agents = [
            # Baselines
            ("RandomBot", lambda: RandomAgent()),

            # Pure heuristics
            ("GreedyStrategic", lambda: GreedyStrategicAgent()),
            ("DefensiveBot", lambda: DefensiveAgent()),
            ("AggressiveBot", lambda: AggressiveAgent()),
            ("IntuitionBot", lambda: IntuitionAgent()),
            ("HeuristicMinimax", lambda: HeuristicMinimaxAgent()),

            # Minimax variant (depth 0 only for speed)
            ("MinimaxBot(d=0)", lambda: MinimaxAgent(max_depth=0, max_moves=20)),

            # MCTS variant (50 simulations for speed)
            ("ImprovedMCTS(50)", lambda: ImprovedMCTSAgent(num_simulations=50)),
        ]
        return agents

    def run_tournament(self):
        """Run comprehensive tournament."""
        agents = self.create_all_agents()
        config = create_default_config()

        print("=" * 80)
        print("COMPREHENSIVE TOURNAMENT")
        print("=" * 80)
        print(f"Agents: {len(agents)}")
        print(f"Games per matchup: {self.games_per_matchup}")
        print(f"Timeout per game: {self.timeout_sec}s")
        print()

        # Initialize agent stats
        for name, _ in agents:
            self.agent_stats[name] = AgentStats(name=name)

        # Run all matchups
        total_matchups = len(agents) * (len(agents) - 1) // 2
        current_matchup = 0

        for i, (name1, agent1_factory) in enumerate(agents):
            for j, (name2, agent2_factory) in enumerate(agents[i + 1 :], start=i + 1):
                current_matchup += 1
                print(f"[{current_matchup}/{total_matchups}] {name1} vs {name2}")

                # Run games
                for game_num in range(self.games_per_matchup):
                    # Alternate who goes first
                    if game_num % 2 == 0:
                        agent1 = agent1_factory()
                        agent2 = agent2_factory()
                        result = self._play_game(
                            name1, agent1, name2, agent2, config, game_num
                        )
                    else:
                        agent2 = agent2_factory()
                        agent1 = agent1_factory()
                        result = self._play_game(
                            name2, agent2, name1, agent1, config, game_num
                        )

                    self.results.append(result)
                    self._update_stats(result)

                # Print interim results
                stats1 = self.agent_stats[name1]
                stats2 = self.agent_stats[name2]
                h2h = self.head_to_head[(name1, name2)]
                print(
                    f"  {name1}: {stats1.win_rate:.1%} ({stats1.wins}W-{stats1.losses}L-{stats1.draws}D) | "
                    f"{name2}: {stats2.win_rate:.1%} ({stats2.wins}W-{stats2.losses}L-{stats2.draws}D)"
                )
                print(
                    f"  H2H: {name1} {h2h['agent1_wins']}W-{h2h['agent2_wins']}L-{h2h['draws']}D "
                    f"(timeouts: {h2h['timeouts']})"
                )
                print()

        print("=" * 80)
        print("TOURNAMENT COMPLETE")
        print("=" * 80)

    def _play_game(
        self,
        p1_name: str,
        agent1,
        p2_name: str,
        agent2,
        config,
        game_num: int,
    ) -> GameStats:
        """Play a single game with timeout handling."""
        try:
            start_time = time.time()

            # Run game with timeout
            final_state = simulate_game(
                config, agent1, agent2, seed=game_num
            )

            elapsed = time.time() - start_time

            if elapsed > self.timeout_sec:
                # Game timed out
                return GameStats(
                    p1_name=p1_name,
                    p2_name=p2_name,
                    winner=None,
                    p1_territories=0,
                    p2_territories=0,
                    p1_stones=0,
                    p2_stones=0,
                    game_length=final_state.current_turn,
                    timeout=True,
                )

            # Extract final stats
            p1_territories = len(
                list(final_state.board.positions_owned_by(Owner.PLAYER_1))
            )
            p2_territories = len(
                list(final_state.board.positions_owned_by(Owner.PLAYER_2))
            )
            p1_stones = final_state.board.total_stones(Owner.PLAYER_1)
            p2_stones = final_state.board.total_stones(Owner.PLAYER_2)

            return GameStats(
                p1_name=p1_name,
                p2_name=p2_name,
                winner=final_state.winner,
                p1_territories=p1_territories,
                p2_territories=p2_territories,
                p1_stones=p1_stones,
                p2_stones=p2_stones,
                game_length=final_state.current_turn,
                timeout=False,
            )

        except Exception as e:
            print(f"    ERROR in game: {e}")
            return GameStats(
                p1_name=p1_name,
                p2_name=p2_name,
                winner=None,
                p1_territories=0,
                p2_territories=0,
                p1_stones=0,
                p2_stones=0,
                game_length=0,
                timeout=True,
            )

    def _update_stats(self, result: GameStats):
        """Update statistics based on game result."""
        # Update agent stats
        if result.timeout:
            # Timeout counts as loss for both
            self.agent_stats[result.p1_name].timeouts += 1
            self.agent_stats[result.p2_name].timeouts += 1
            self.agent_stats[result.p1_name].losses += 1
            self.agent_stats[result.p2_name].losses += 1
            self.agent_stats[result.p1_name].games_played += 1
            self.agent_stats[result.p2_name].games_played += 1
            self.agent_stats[result.p1_name].total_territories += result.p1_territories
            self.agent_stats[result.p2_name].total_territories += result.p2_territories
            self.agent_stats[result.p1_name].total_stones += result.p1_stones
            self.agent_stats[result.p2_name].total_stones += result.p2_stones
            self.agent_stats[result.p1_name].total_game_length += result.game_length
            self.agent_stats[result.p2_name].total_game_length += result.game_length
        else:
            # Update win/loss
            if result.winner == Owner.PLAYER_1:
                self.agent_stats[result.p1_name].wins += 1
                self.agent_stats[result.p2_name].losses += 1
            elif result.winner == Owner.PLAYER_2:
                self.agent_stats[result.p2_name].wins += 1
                self.agent_stats[result.p1_name].losses += 1
            else:
                self.agent_stats[result.p1_name].draws += 1
                self.agent_stats[result.p2_name].draws += 1

            # Update games played
            self.agent_stats[result.p1_name].games_played += 1
            self.agent_stats[result.p2_name].games_played += 1

            # Update territorial stats
            self.agent_stats[result.p1_name].total_territories += result.p1_territories
            self.agent_stats[result.p2_name].total_territories += result.p2_territories
            self.agent_stats[result.p1_name].total_stones += result.p1_stones
            self.agent_stats[result.p2_name].total_stones += result.p2_stones
            self.agent_stats[result.p1_name].total_game_length += result.game_length
            self.agent_stats[result.p2_name].total_game_length += result.game_length

        # Update head-to-head
        key = (result.p1_name, result.p2_name)
        if result.timeout:
            self.head_to_head[key]["timeouts"] += 1
        elif result.winner == Owner.PLAYER_1:
            self.head_to_head[key]["agent1_wins"] += 1
        elif result.winner == Owner.PLAYER_2:
            self.head_to_head[key]["agent2_wins"] += 1
        else:
            self.head_to_head[key]["draws"] += 1

    def print_results(self):
        """Print tournament results."""
        print("\n" + "=" * 80)
        print("RESULTS SUMMARY")
        print("=" * 80)

        # Sort by win rate
        sorted_agents = sorted(
            self.agent_stats.values(),
            key=lambda x: (x.win_rate, x.avg_territories),
            reverse=True,
        )

        print("\nOVERALL RANKINGS (by win rate):")
        print("-" * 80)
        print(
            f"{'Rank':<5} {'Agent':<25} {'W-L-D':<15} {'Win%':<10} {'Terr':<8} {'Stones':<8}"
        )
        print("-" * 80)

        for rank, stats in enumerate(sorted_agents, 1):
            print(
                f"{rank:<5} {stats.name:<25} "
                f"{stats.wins}-{stats.losses}-{stats.draws:<8} "
                f"{stats.win_rate:>8.1%}  "
                f"{stats.avg_territories:>7.1f} "
                f"{stats.avg_stones:>7.1f}"
            )

        # Head-to-head matrix
        print("\n" + "=" * 80)
        print("HEAD-TO-HEAD MATRIX")
        print("=" * 80)
        print("\nWin rates (A beats B):")
        print()

        agent_names = sorted(self.agent_stats.keys())
        print(f"{'vs':<25}", end="")
        for name in agent_names:
            print(f"{name[:12]:<13}", end="")
        print()
        print("-" * (25 + len(agent_names) * 13))

        for name1 in agent_names:
            print(f"{name1:<25}", end="")
            for name2 in agent_names:
                if name1 == name2:
                    print(f"{'—':<13}", end="")
                else:
                    key = (name1, name2) if (name1, name2) in self.head_to_head else (name2, name1)
                    if key in self.head_to_head:
                        h2h = self.head_to_head[key]
                        if (name1, name2) in self.head_to_head:
                            wins = h2h["agent1_wins"]
                            total = h2h["agent1_wins"] + h2h["agent2_wins"] + h2h["draws"]
                        else:
                            wins = h2h["agent2_wins"]
                            total = h2h["agent1_wins"] + h2h["agent2_wins"] + h2h["draws"]

                        if total > 0:
                            wr = wins / total
                            print(f"{wr:>6.1%}({wins}-{total-wins}){'':<2}", end="")
                        else:
                            print(f"{'—':<13}", end="")
                    else:
                        print(f"{'—':<13}", end="")
            print()

        # Detailed statistics
        print("\n" + "=" * 80)
        print("DETAILED STATISTICS")
        print("=" * 80)

        for stats in sorted_agents:
            print(f"\n{stats.name}")
            print(f"  Record: {stats.wins}W-{stats.losses}L-{stats.draws}D (win rate: {stats.win_rate:.1%})")
            print(f"  Avg territories: {stats.avg_territories:.1f}")
            print(f"  Avg stones: {stats.avg_stones:.1f}")
            print(f"  Avg game length: {stats.avg_game_length:.1f} turns")
            print(f"  Timeouts: {stats.timeouts}")


def main():
    """Run tournament."""
    import sys

    # Control parameters
    games_per_matchup = 20
    timeout_sec = 30.0

    if len(sys.argv) > 1:
        games_per_matchup = int(sys.argv[1])

    tournament = ComprehensiveTournament(
        games_per_matchup=games_per_matchup, timeout_sec=timeout_sec
    )

    print(f"Starting tournament with {games_per_matchup} games per matchup...")
    print()

    start_time = time.time()
    tournament.run_tournament()
    elapsed = time.time() - start_time

    tournament.print_results()

    print("\n" + "=" * 80)
    print(f"Total time: {elapsed:.1f}s ({elapsed/60:.1f}m)")
    print("=" * 80)


if __name__ == "__main__":
    main()
