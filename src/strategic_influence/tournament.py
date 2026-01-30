"""Tournament runner for comparing AI agents.

Runs round-robin tournaments between multiple agents and collects statistics.
"""

from dataclasses import dataclass
from typing import Callable
from random import Random

from .types import Owner
from .config import GameConfig, create_default_config
from .engine import simulate_game
from .agents.protocol import Agent


@dataclass
class MatchResult:
    """Result of a single match."""
    player1_name: str
    player2_name: str
    winner: Owner | None  # None = draw
    p1_territories: int
    p2_territories: int
    p1_stones: int
    p2_stones: int


@dataclass
class HeadToHeadStats:
    """Statistics for matches between two specific agents."""
    agent1_name: str
    agent2_name: str
    agent1_wins: int = 0
    agent2_wins: int = 0
    draws: int = 0

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
    """Overall statistics for an agent across all matches."""
    name: str
    wins: int = 0
    losses: int = 0
    draws: int = 0
    total_territories: int = 0
    total_stones: int = 0
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


@dataclass
class TournamentResults:
    """Complete tournament results."""
    agent_stats: dict[str, AgentStats]
    head_to_head: dict[tuple[str, str], HeadToHeadStats]
    matches: list[MatchResult]

    def get_rankings(self) -> list[tuple[str, AgentStats]]:
        """Get agents ranked by win rate, then by average territories."""
        return sorted(
            self.agent_stats.items(),
            key=lambda x: (x[1].win_rate, x[1].avg_territories),
            reverse=True,
        )

    def format_report(self) -> str:
        """Generate a formatted tournament report."""
        lines = []
        lines.append("=" * 60)
        lines.append("TOURNAMENT RESULTS")
        lines.append("=" * 60)
        lines.append("")

        # Overall rankings
        lines.append("RANKINGS (by win rate)")
        lines.append("-" * 60)
        rankings = self.get_rankings()
        for i, (name, stats) in enumerate(rankings, 1):
            lines.append(
                f"{i}. {name:20s} | "
                f"Win: {stats.win_rate:5.1%} | "
                f"W-L-D: {stats.wins:2d}-{stats.losses:2d}-{stats.draws:2d} | "
                f"Avg Terr: {stats.avg_territories:.1f}"
            )
        lines.append("")

        # Head-to-head matrix
        lines.append("HEAD-TO-HEAD RESULTS")
        lines.append("-" * 60)
        agent_names = list(self.agent_stats.keys())

        # Header row
        header = f"{'':20s} |"
        for name in agent_names:
            header += f" {name[:8]:>8s} |"
        lines.append(header)
        lines.append("-" * len(header))

        # Data rows
        for name1 in agent_names:
            row = f"{name1:20s} |"
            for name2 in agent_names:
                if name1 == name2:
                    row += f" {'---':>8s} |"
                else:
                    key = (name1, name2) if (name1, name2) in self.head_to_head else (name2, name1)
                    if key in self.head_to_head:
                        h2h = self.head_to_head[key]
                        if key[0] == name1:
                            wins = h2h.agent1_wins
                        else:
                            wins = h2h.agent2_wins
                        row += f" {wins:>8d} |"
                    else:
                        row += f" {'?':>8s} |"
            lines.append(row)

        lines.append("")
        lines.append(f"Total matches played: {len(self.matches)}")

        return "\n".join(lines)


def run_match(
    player1: Agent,
    player2: Agent,
    config: GameConfig,
    seed: int,
) -> MatchResult:
    """Run a single match between two agents."""
    final_state = simulate_game(config, player1, player2, seed=seed)

    counts = final_state.board.count_territories()

    return MatchResult(
        player1_name=player1.name,
        player2_name=player2.name,
        winner=final_state.winner,
        p1_territories=counts[Owner.PLAYER_1],
        p2_territories=counts[Owner.PLAYER_2],
        p1_stones=final_state.board.total_stones(Owner.PLAYER_1),
        p2_stones=final_state.board.total_stones(Owner.PLAYER_2),
    )


def run_tournament(
    agents: list[Agent],
    games_per_matchup: int = 10,
    config: GameConfig | None = None,
    base_seed: int = 42,
    verbose: bool = True,
) -> TournamentResults:
    """Run a round-robin tournament between agents.

    Each pair of agents plays games_per_matchup games with each agent
    playing as both Player 1 and Player 2.

    Args:
        agents: List of agents to compete.
        games_per_matchup: Number of games per matchup (split between sides).
        config: Game configuration. Uses default if None.
        base_seed: Base seed for reproducibility.
        verbose: Whether to print progress.

    Returns:
        TournamentResults with all statistics.
    """
    if config is None:
        config = create_default_config()

    # Initialize statistics
    agent_stats: dict[str, AgentStats] = {
        agent.name: AgentStats(name=agent.name) for agent in agents
    }
    head_to_head: dict[tuple[str, str], HeadToHeadStats] = {}
    matches: list[MatchResult] = []

    rng = Random(base_seed)
    games_per_side = games_per_matchup // 2

    total_matchups = len(agents) * (len(agents) - 1) // 2
    matchup_num = 0

    # Round-robin: each pair plays
    for i, agent1 in enumerate(agents):
        for agent2 in agents[i + 1:]:
            matchup_num += 1
            if verbose:
                print(f"Matchup {matchup_num}/{total_matchups}: {agent1.name} vs {agent2.name}")

            h2h = HeadToHeadStats(agent1.name, agent2.name)

            # Play games with agent1 as P1
            for game_num in range(games_per_side):
                seed = rng.randint(0, 2**31)
                result = run_match(agent1, agent2, config, seed)
                matches.append(result)

                # Update head-to-head
                if result.winner == Owner.PLAYER_1:
                    h2h.agent1_wins += 1
                elif result.winner == Owner.PLAYER_2:
                    h2h.agent2_wins += 1
                else:
                    h2h.draws += 1

                # Update agent stats
                _update_agent_stats(agent_stats[agent1.name], result, is_player1=True)
                _update_agent_stats(agent_stats[agent2.name], result, is_player1=False)

            # Play games with agent2 as P1
            for game_num in range(games_per_side):
                seed = rng.randint(0, 2**31)
                result = run_match(agent2, agent1, config, seed)
                matches.append(result)

                # Update head-to-head (note: roles swapped)
                if result.winner == Owner.PLAYER_1:
                    h2h.agent2_wins += 1
                elif result.winner == Owner.PLAYER_2:
                    h2h.agent1_wins += 1
                else:
                    h2h.draws += 1

                # Update agent stats
                _update_agent_stats(agent_stats[agent2.name], result, is_player1=True)
                _update_agent_stats(agent_stats[agent1.name], result, is_player1=False)

            head_to_head[(agent1.name, agent2.name)] = h2h

            if verbose:
                print(f"  Result: {agent1.name} {h2h.agent1_wins}-{h2h.draws}-{h2h.agent2_wins} {agent2.name}")

    return TournamentResults(
        agent_stats=agent_stats,
        head_to_head=head_to_head,
        matches=matches,
    )


def _update_agent_stats(stats: AgentStats, result: MatchResult, is_player1: bool) -> None:
    """Update agent stats based on match result."""
    stats.games_played += 1

    if is_player1:
        stats.total_territories += result.p1_territories
        stats.total_stones += result.p1_stones
        if result.winner == Owner.PLAYER_1:
            stats.wins += 1
        elif result.winner == Owner.PLAYER_2:
            stats.losses += 1
        else:
            stats.draws += 1
    else:
        stats.total_territories += result.p2_territories
        stats.total_stones += result.p2_stones
        if result.winner == Owner.PLAYER_2:
            stats.wins += 1
        elif result.winner == Owner.PLAYER_1:
            stats.losses += 1
        else:
            stats.draws += 1


def main():
    """Run a tournament with all available agents."""
    from .agents import RandomAgent, AggressiveAgent

    # Try to import new agents if they exist
    agents = [
        RandomAgent(seed=42),
        AggressiveAgent(seed=42),
    ]

    # Try importing new agents
    try:
        from .agents import DefensiveAgent
        agents.append(DefensiveAgent(seed=42))
    except ImportError:
        pass

    try:
        from .agents import RushAgent
        agents.append(RushAgent(seed=42))
    except ImportError:
        pass

    try:
        from .agents import StrategicAgent
        agents.append(StrategicAgent(seed=42))
    except ImportError:
        pass

    try:
        from .agents import MonteCarloAgent
        agents.append(MonteCarloAgent(seed=42, num_simulations=30))
    except ImportError:
        pass

    print(f"Running tournament with {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent.name}")
    print()

    results = run_tournament(agents, games_per_matchup=20, verbose=True)
    print()
    print(results.format_report())


if __name__ == "__main__":
    main()
