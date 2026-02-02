"""Tournament system for March of Empires."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

from .types import Player
from .config import GameConfig, create_default_config
from .game import run_game, GameResult
from .agents.protocol import Agent


@dataclass
class MatchResult:
    """Result of a single match between two agents."""

    agent1_name: str
    agent2_name: str
    winner_name: str | None
    agent1_score: int
    agent2_score: int
    turns: int


@dataclass
class HeadToHeadStats:
    """Statistics for matches between two specific agents."""

    agent1_name: str
    agent2_name: str
    agent1_wins: int = 0
    agent2_wins: int = 0
    draws: int = 0
    agent1_total_score: int = 0
    agent2_total_score: int = 0

    @property
    def total_games(self) -> int:
        return self.agent1_wins + self.agent2_wins + self.draws

    @property
    def agent1_win_rate(self) -> float:
        if self.total_games == 0:
            return 0.0
        return self.agent1_wins / self.total_games

    @property
    def agent2_win_rate(self) -> float:
        if self.total_games == 0:
            return 0.0
        return self.agent2_wins / self.total_games


@dataclass
class AgentStats:
    """Overall tournament statistics for an agent."""

    name: str
    wins: int = 0
    losses: int = 0
    draws: int = 0
    total_score: int = 0
    games_played: int = 0

    @property
    def win_rate(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.wins / self.games_played

    @property
    def avg_score(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.total_score / self.games_played

    @property
    def points(self) -> float:
        """Tournament points (win=1, draw=0.5, loss=0)."""
        return self.wins + self.draws * 0.5


@dataclass
class TournamentResult:
    """Complete tournament results."""

    agent_stats: dict[str, AgentStats]
    head_to_head: dict[tuple[str, str], HeadToHeadStats]
    match_results: list[MatchResult]
    total_games: int
    duration_seconds: float

    def get_rankings(self) -> list[tuple[str, AgentStats]]:
        """Get agents ranked by tournament points, then win rate."""
        return sorted(
            self.agent_stats.items(),
            key=lambda x: (x[1].points, x[1].win_rate, x[1].avg_score),
            reverse=True,
        )

    def print_summary(self) -> None:
        """Print tournament summary."""
        print("\n" + "=" * 60)
        print("TOURNAMENT RESULTS")
        print("=" * 60)

        rankings = self.get_rankings()

        print(f"\nTotal games played: {self.total_games}")
        print(f"Duration: {self.duration_seconds:.1f} seconds")

        print("\n--- Rankings ---")
        print(f"{'Rank':<5} {'Agent':<20} {'W-L-D':<12} {'Win%':<8} {'Pts':<6} {'AvgScore':<8}")
        print("-" * 60)

        for i, (name, stats) in enumerate(rankings, 1):
            record = f"{stats.wins}-{stats.losses}-{stats.draws}"
            print(
                f"{i:<5} {name:<20} {record:<12} {stats.win_rate*100:>5.1f}%  "
                f"{stats.points:<6.1f} {stats.avg_score:>7.1f}"
            )

        print("\n--- Head-to-Head ---")
        for (a1, a2), h2h in sorted(self.head_to_head.items()):
            print(f"{a1} vs {a2}: {h2h.agent1_wins}-{h2h.agent2_wins}-{h2h.draws}")


def run_tournament(
    agents: Sequence[Agent],
    games_per_matchup: int = 10,
    config: GameConfig | None = None,
    verbose: bool = True,
) -> TournamentResult:
    """Run a round-robin tournament between agents.

    Each pair of agents plays games_per_matchup games (half as each side).

    Args:
        agents: List of agents to compete.
        games_per_matchup: Games per agent pair.
        config: Game configuration.
        verbose: Print progress if True.

    Returns:
        TournamentResult with all statistics.
    """
    if config is None:
        config = create_default_config()

    start_time = time.time()

    # Initialize stats
    agent_stats: dict[str, AgentStats] = {
        agent.name: AgentStats(name=agent.name) for agent in agents
    }
    head_to_head: dict[tuple[str, str], HeadToHeadStats] = {}
    match_results: list[MatchResult] = []

    # Create agent lookup
    agent_by_name = {agent.name: agent for agent in agents}

    # Generate all matchups
    matchups: list[tuple[Agent, Agent]] = []
    for i, agent1 in enumerate(agents):
        for agent2 in agents[i + 1:]:
            matchups.append((agent1, agent2))

    total_games = len(matchups) * games_per_matchup

    if verbose:
        print(f"Running tournament with {len(agents)} agents")
        print(f"Total matchups: {len(matchups)}, Games per matchup: {games_per_matchup}")
        print(f"Total games: {total_games}")
        print()

    game_count = 0
    for agent1, agent2 in matchups:
        key = (agent1.name, agent2.name)
        h2h = HeadToHeadStats(agent1_name=agent1.name, agent2_name=agent2.name)

        # Play half as each side
        games_as_p1 = games_per_matchup // 2
        games_as_p2 = games_per_matchup - games_as_p1

        # Agent1 as Player 1
        for _ in range(games_as_p1):
            result = run_game(agent1, agent2, config, verbose=False)
            game_count += 1

            _record_result(
                result, agent1.name, agent2.name,
                agent_stats, h2h, match_results, as_p1=True
            )

            if verbose and game_count % 10 == 0:
                print(f"  Games completed: {game_count}/{total_games}")

        # Agent1 as Player 2
        for _ in range(games_as_p2):
            result = run_game(agent2, agent1, config, verbose=False)
            game_count += 1

            _record_result(
                result, agent1.name, agent2.name,
                agent_stats, h2h, match_results, as_p1=False
            )

            if verbose and game_count % 10 == 0:
                print(f"  Games completed: {game_count}/{total_games}")

        head_to_head[key] = h2h

    duration = time.time() - start_time

    tournament_result = TournamentResult(
        agent_stats=agent_stats,
        head_to_head=head_to_head,
        match_results=match_results,
        total_games=total_games,
        duration_seconds=duration,
    )

    if verbose:
        tournament_result.print_summary()

    return tournament_result


def _record_result(
    result: GameResult,
    agent1_name: str,
    agent2_name: str,
    agent_stats: dict[str, AgentStats],
    h2h: HeadToHeadStats,
    match_results: list[MatchResult],
    as_p1: bool,
) -> None:
    """Record a game result in all statistics."""
    # Determine actual scores and winner from agent1's perspective
    if as_p1:
        agent1_score = result.p1_score
        agent2_score = result.p2_score
        if result.winner == Player.PLAYER_1:
            winner_name = agent1_name
        elif result.winner == Player.PLAYER_2:
            winner_name = agent2_name
        else:
            winner_name = None
    else:
        agent1_score = result.p2_score
        agent2_score = result.p1_score
        if result.winner == Player.PLAYER_2:
            winner_name = agent1_name
        elif result.winner == Player.PLAYER_1:
            winner_name = agent2_name
        else:
            winner_name = None

    # Update agent stats
    agent_stats[agent1_name].games_played += 1
    agent_stats[agent1_name].total_score += agent1_score
    agent_stats[agent2_name].games_played += 1
    agent_stats[agent2_name].total_score += agent2_score

    if winner_name == agent1_name:
        agent_stats[agent1_name].wins += 1
        agent_stats[agent2_name].losses += 1
        h2h.agent1_wins += 1
    elif winner_name == agent2_name:
        agent_stats[agent2_name].wins += 1
        agent_stats[agent1_name].losses += 1
        h2h.agent2_wins += 1
    else:
        agent_stats[agent1_name].draws += 1
        agent_stats[agent2_name].draws += 1
        h2h.draws += 1

    h2h.agent1_total_score += agent1_score
    h2h.agent2_total_score += agent2_score

    # Record match result
    match_results.append(MatchResult(
        agent1_name=agent1_name,
        agent2_name=agent2_name,
        winner_name=winner_name,
        agent1_score=agent1_score,
        agent2_score=agent2_score,
        turns=result.total_turns,
    ))
