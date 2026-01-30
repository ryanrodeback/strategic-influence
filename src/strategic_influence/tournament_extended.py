"""Extended tournament runner with Elo ratings and iteration support.

Provides:
- Elo rating system
- Confidence intervals
- Overfitting detection
- Stop condition checking
- Automated iteration loop
"""

import math
import statistics
from dataclasses import dataclass, field
from random import Random
from typing import Callable

from .types import Owner
from .config import GameConfig, create_default_config
from .engine import simulate_game
from .agents.protocol import Agent
from .tournament import MatchResult, HeadToHeadStats, AgentStats, run_match


@dataclass
class EloRating:
    """Elo rating with history tracking."""
    rating: float = 1500.0
    games_played: int = 0
    rating_history: list[float] = field(default_factory=list)

    @property
    def k_factor(self) -> float:
        """K-factor decreases as games increase (stabilization)."""
        if self.games_played < 30:
            return 40  # Provisional
        elif self.games_played < 100:
            return 20  # Established
        else:
            return 10  # Stable


@dataclass
class EloSystem:
    """Manages Elo ratings for all agents."""
    ratings: dict[str, EloRating] = field(default_factory=dict)

    def get_rating(self, name: str) -> EloRating:
        """Get or create rating for an agent."""
        if name not in self.ratings:
            self.ratings[name] = EloRating()
        return self.ratings[name]

    def update_win(self, winner_name: str, loser_name: str) -> None:
        """Update ratings after a decisive match."""
        winner = self.get_rating(winner_name)
        loser = self.get_rating(loser_name)

        expected_winner = 1 / (1 + 10 ** ((loser.rating - winner.rating) / 400))

        winner.rating += winner.k_factor * (1 - expected_winner)
        loser.rating += loser.k_factor * (0 - (1 - expected_winner))

        winner.games_played += 1
        loser.games_played += 1
        winner.rating_history.append(winner.rating)
        loser.rating_history.append(loser.rating)

    def update_draw(self, name1: str, name2: str) -> None:
        """Handle draws with 0.5 score."""
        p1 = self.get_rating(name1)
        p2 = self.get_rating(name2)

        expected_p1 = 1 / (1 + 10 ** ((p2.rating - p1.rating) / 400))

        p1.rating += p1.k_factor * (0.5 - expected_p1)
        p2.rating += p2.k_factor * (0.5 - (1 - expected_p1))

        p1.games_played += 1
        p2.games_played += 1
        p1.rating_history.append(p1.rating)
        p2.rating_history.append(p2.rating)

    def get_rankings(self) -> list[tuple[str, float]]:
        """Get agents ranked by Elo."""
        return sorted(
            [(name, r.rating) for name, r in self.ratings.items()],
            key=lambda x: x[1],
            reverse=True,
        )


def wilson_score_interval(
    successes: int,
    total: int,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Calculate Wilson score confidence interval for a proportion."""
    if total == 0:
        return (0.0, 1.0)

    z = 1.96 if confidence == 0.95 else 1.645  # 95% or 90%
    p = successes / total

    denominator = 1 + z * z / total
    center = p + z * z / (2 * total)
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total)

    lower = (center - spread) / denominator
    upper = (center + spread) / denominator

    return (max(0, lower), min(1, upper))


def is_elo_stable(
    elo: EloRating,
    window: int = 50,
    threshold: float = 25,
) -> bool:
    """Check if Elo rating has stabilized."""
    if len(elo.rating_history) < window:
        return False
    recent = elo.rating_history[-window:]
    return statistics.stdev(recent) < threshold


def detect_overfitting(
    head_to_head: dict[tuple[str, str], HeadToHeadStats],
    agent_name: str,
) -> dict:
    """Detect if agent is overfit to specific opponents."""
    win_rates: dict[str, float] = {}

    for (a1, a2), h2h in head_to_head.items():
        if a1 == agent_name:
            if h2h.total_games > 0:
                win_rates[a2] = h2h.agent1_win_rate
        elif a2 == agent_name:
            if h2h.total_games > 0:
                win_rates[a1] = h2h.agent2_win_rate

    if len(win_rates) < 2:
        return {"is_overfit": False, "coefficient_of_variation": 0.0, "win_rates": win_rates}

    rates = list(win_rates.values())
    mean_rate = statistics.mean(rates)
    std_rate = statistics.stdev(rates)

    # Coefficient of variation - high means inconsistent performance
    cv = std_rate / mean_rate if mean_rate > 0 else 0

    return {
        "is_overfit": cv > 0.3,  # High variance = overfitting
        "coefficient_of_variation": cv,
        "win_rates": win_rates,
    }


@dataclass
class CompetitivenessThresholds:
    """Thresholds for declaring an agent competitive."""
    min_games_per_opponent: int = 30
    min_total_games: int = 100
    vs_random_target: float = 0.65
    vs_heuristic_target: float = 0.55
    min_elo: float = 1550
    elo_stability_window: int = 50
    elo_stability_std: float = 25


def check_competitiveness(
    agent_name: str,
    agent_stats: dict[str, AgentStats],
    head_to_head: dict[tuple[str, str], HeadToHeadStats],
    elo_system: EloSystem,
    thresholds: CompetitivenessThresholds | None = None,
) -> dict:
    """Check if agent meets competitiveness criteria."""
    if thresholds is None:
        thresholds = CompetitivenessThresholds()

    stats = agent_stats.get(agent_name)
    elo = elo_system.get_rating(agent_name)

    if stats is None:
        return {"is_competitive": False, "reason": "No stats found"}

    checks = {
        "sufficient_games": stats.games_played >= thresholds.min_total_games,
        "beats_random": False,
        "beats_heuristics": True,  # Start true, set false if any fails
        "elo_sufficient": elo.rating >= thresholds.min_elo,
        "elo_stable": is_elo_stable(
            elo, thresholds.elo_stability_window, thresholds.elo_stability_std
        ),
    }

    # Check head-to-head rates
    heuristic_agents = ["AggressiveBot", "DefensiveBot", "RushBot", "StrategicBot"]

    for (a1, a2), h2h in head_to_head.items():
        opponent = None
        rate = 0.0

        if a1 == agent_name:
            opponent = a2
            rate = h2h.agent1_win_rate
        elif a2 == agent_name:
            opponent = a1
            rate = h2h.agent2_win_rate

        if opponent is None:
            continue

        if opponent == "RandomBot":
            checks["beats_random"] = rate >= thresholds.vs_random_target
        elif opponent in heuristic_agents:
            if rate < thresholds.vs_heuristic_target:
                checks["beats_heuristics"] = False

    checks["is_competitive"] = (
        checks["sufficient_games"] and
        checks["beats_random"] and
        checks["elo_sufficient"]
    )

    checks["is_strong"] = checks["is_competitive"] and checks["beats_heuristics"]
    checks["is_stable"] = checks["is_strong"] and checks["elo_stable"]

    return checks


@dataclass
class ExtendedTournamentResults:
    """Complete tournament results with Elo ratings."""
    agent_stats: dict[str, AgentStats]
    head_to_head: dict[tuple[str, str], HeadToHeadStats]
    matches: list[MatchResult]
    elo_system: EloSystem

    def get_rankings(self) -> list[tuple[str, AgentStats]]:
        """Get agents ranked by win rate."""
        return sorted(
            self.agent_stats.items(),
            key=lambda x: (x[1].win_rate, x[1].avg_territories),
            reverse=True,
        )

    def get_elo_rankings(self) -> list[tuple[str, float]]:
        """Get agents ranked by Elo."""
        return self.elo_system.get_rankings()

    def format_report(self) -> str:
        """Generate a formatted tournament report with Elo."""
        lines = []
        lines.append("=" * 70)
        lines.append("EXTENDED TOURNAMENT RESULTS")
        lines.append("=" * 70)
        lines.append("")

        # Elo rankings
        lines.append("ELO RANKINGS")
        lines.append("-" * 70)
        for i, (name, rating) in enumerate(self.get_elo_rankings(), 1):
            elo_obj = self.elo_system.ratings[name]
            stability = "stable" if is_elo_stable(elo_obj) else "unstable"
            lines.append(
                f"{i}. {name:20s} | Elo: {rating:7.1f} | "
                f"Games: {elo_obj.games_played:3d} | {stability}"
            )
        lines.append("")

        # Win rate rankings
        lines.append("WIN RATE RANKINGS")
        lines.append("-" * 70)
        for i, (name, stats) in enumerate(self.get_rankings(), 1):
            ci_low, ci_high = wilson_score_interval(stats.wins, stats.games_played)
            lines.append(
                f"{i}. {name:20s} | "
                f"Win: {stats.win_rate:5.1%} ({ci_low:.1%}-{ci_high:.1%}) | "
                f"W-L-D: {stats.wins:2d}-{stats.losses:2d}-{stats.draws:2d}"
            )
        lines.append("")

        # Competitiveness check
        lines.append("COMPETITIVENESS STATUS")
        lines.append("-" * 70)
        for name in self.agent_stats.keys():
            status = check_competitiveness(
                name, self.agent_stats, self.head_to_head, self.elo_system
            )
            level = "STABLE" if status.get("is_stable") else \
                    "STRONG" if status.get("is_strong") else \
                    "COMPETITIVE" if status.get("is_competitive") else \
                    "developing"
            lines.append(f"  {name:20s}: {level}")

        lines.append("")
        lines.append(f"Total matches played: {len(self.matches)}")

        return "\n".join(lines)


def run_extended_tournament(
    agents: list[Agent],
    games_per_matchup: int = 30,
    config: GameConfig | None = None,
    base_seed: int = 42,
    verbose: bool = True,
) -> ExtendedTournamentResults:
    """Run tournament with Elo tracking."""
    if config is None:
        config = create_default_config()

    # Initialize
    agent_stats: dict[str, AgentStats] = {
        agent.name: AgentStats(name=agent.name) for agent in agents
    }
    head_to_head: dict[tuple[str, str], HeadToHeadStats] = {}
    matches: list[MatchResult] = []
    elo_system = EloSystem()

    rng = Random(base_seed)
    games_per_side = games_per_matchup // 2

    total_matchups = len(agents) * (len(agents) - 1) // 2
    matchup_num = 0

    for i, agent1 in enumerate(agents):
        for agent2 in agents[i + 1:]:
            matchup_num += 1
            if verbose:
                print(f"Matchup {matchup_num}/{total_matchups}: {agent1.name} vs {agent2.name}")

            h2h = HeadToHeadStats(agent1.name, agent2.name)

            # Play games with agent1 as P1
            for _ in range(games_per_side):
                seed = rng.randint(0, 2**31)
                result = run_match(agent1, agent2, config, seed)
                matches.append(result)

                # Update head-to-head
                if result.winner == Owner.PLAYER_1:
                    h2h.agent1_wins += 1
                    elo_system.update_win(agent1.name, agent2.name)
                elif result.winner == Owner.PLAYER_2:
                    h2h.agent2_wins += 1
                    elo_system.update_win(agent2.name, agent1.name)
                else:
                    h2h.draws += 1
                    elo_system.update_draw(agent1.name, agent2.name)

                _update_agent_stats(agent_stats[agent1.name], result, is_player1=True)
                _update_agent_stats(agent_stats[agent2.name], result, is_player1=False)

            # Play games with agent2 as P1
            for _ in range(games_per_side):
                seed = rng.randint(0, 2**31)
                result = run_match(agent2, agent1, config, seed)
                matches.append(result)

                if result.winner == Owner.PLAYER_1:
                    h2h.agent2_wins += 1
                    elo_system.update_win(agent2.name, agent1.name)
                elif result.winner == Owner.PLAYER_2:
                    h2h.agent1_wins += 1
                    elo_system.update_win(agent1.name, agent2.name)
                else:
                    h2h.draws += 1
                    elo_system.update_draw(agent1.name, agent2.name)

                _update_agent_stats(agent_stats[agent2.name], result, is_player1=True)
                _update_agent_stats(agent_stats[agent1.name], result, is_player1=False)

            head_to_head[(agent1.name, agent2.name)] = h2h

            if verbose:
                print(f"  Result: {agent1.name} {h2h.agent1_wins}-{h2h.draws}-{h2h.agent2_wins} {agent2.name}")

    return ExtendedTournamentResults(
        agent_stats=agent_stats,
        head_to_head=head_to_head,
        matches=matches,
        elo_system=elo_system,
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


def run_iteration_loop(
    agents: list[Agent],
    games_per_matchup: int = 30,
    max_iterations: int = 10,
    config: GameConfig | None = None,
    verbose: bool = True,
) -> list[ExtendedTournamentResults]:
    """Run iterative tournament until agents stabilize or max iterations reached.

    Returns list of results from each iteration.
    """
    results_history: list[ExtendedTournamentResults] = []

    for iteration in range(max_iterations):
        if verbose:
            print(f"\n{'='*70}")
            print(f"ITERATION {iteration + 1}/{max_iterations}")
            print(f"{'='*70}\n")

        # Reset agents
        for agent in agents:
            agent.reset()

        # Run tournament
        results = run_extended_tournament(
            agents, games_per_matchup, config, base_seed=42 + iteration * 1000, verbose=verbose
        )
        results_history.append(results)

        if verbose:
            print("\n" + results.format_report())

        # Check stopping conditions
        all_stable = True
        for name in results.agent_stats.keys():
            status = check_competitiveness(
                name, results.agent_stats, results.head_to_head, results.elo_system
            )
            if not status.get("elo_stable", False):
                all_stable = False

        if all_stable and iteration >= 2:
            if verbose:
                print("\nAll agents have stable Elo ratings. Stopping.")
            break

    return results_history


def main():
    """Run extended tournament with all agents."""
    from .agents import (
        RandomAgent, AggressiveAgent, DefensiveAgent, RushAgent,
        StrategicAgent, MonteCarloAgent, IntuitionAgent, MinimaxAgent,
        ImprovedMCTSAgent, ContraryAgent,
    )

    agents = [
        RandomAgent(seed=42),
        AggressiveAgent(seed=42),
        DefensiveAgent(seed=42),
        RushAgent(seed=42),
        StrategicAgent(seed=42),
        MonteCarloAgent(seed=42, num_simulations=30),
        IntuitionAgent(seed=42),
        MinimaxAgent(seed=42, max_depth=3),
        ImprovedMCTSAgent(seed=42, num_simulations=50),
        ContraryAgent(seed=42),
    ]

    print(f"Running extended tournament with {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent.name}")
    print()

    results = run_extended_tournament(agents, games_per_matchup=30, verbose=True)
    print("\n" + results.format_report())


if __name__ == "__main__":
    main()
