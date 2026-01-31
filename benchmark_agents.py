#!/usr/bin/env python3
"""Comprehensive AI agent benchmarking and comparison.

This script tests:
1. Minimax depth variations (0, 1, 2, 3)
2. Pure heuristic agents
3. MCTS variations (random, heuristic, minimax-based)
4. Tournament comparisons

Run with: PYTHONPATH=src python benchmark_agents.py
"""

import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.engine import simulate_game
from strategic_influence.types import Owner
from strategic_influence.agents.minimax_agent import MinimaxAgent
from strategic_influence.agents.improved_mcts_agent import ImprovedMCTSAgent
from strategic_influence.agents.greedy_strategic_agent import GreedyStrategicAgent
from strategic_influence.agents.random_agent import RandomAgent
from strategic_influence.evaluation import BALANCED_WEIGHTS, TERRITORY_ONLY_WEIGHTS


@dataclass
class MatchResult:
    """Result of a single match."""
    agent1_name: str
    agent2_name: str
    winner: Owner | None
    p1_territories: int
    p2_territories: int
    duration: float
    p1_avg_move_time: float
    p2_avg_move_time: float


@dataclass
class AgentStats:
    """Statistics for an agent."""
    name: str
    wins: int = 0
    losses: int = 0
    draws: int = 0
    total_duration: float = 0.0
    total_avg_move_time: float = 0.0
    matches: int = 0

    @property
    def win_rate(self) -> float:
        if self.matches == 0:
            return 0.0
        return self.wins / self.matches

    @property
    def avg_game_duration(self) -> float:
        if self.matches == 0:
            return 0.0
        return self.total_duration / self.matches

    @property
    def avg_move_time(self) -> float:
        if self.matches == 0:
            return 0.0
        return self.total_avg_move_time / self.matches


class AgentBenchmark:
    """Run benchmarks and tournaments."""

    def __init__(self, config=None):
        self.config = config or create_default_config()
        self.results: list[MatchResult] = []
        self.agent_stats: dict[str, AgentStats] = {}

    def create_minimax_agents(self) -> list[tuple[str, MinimaxAgent]]:
        """Create minimax agents with different depths."""
        agents = []
        for depth in [0, 1, 2]:
            agent = MinimaxAgent(max_depth=depth, weights=TERRITORY_ONLY_WEIGHTS)
            agents.append((f"Minimax(d={depth})", agent))
        return agents

    def create_mcts_agents(self) -> list[tuple[str, ImprovedMCTSAgent]]:
        """Create MCTS variants."""
        agents = []

        # Random rollouts (baseline)
        mcts_random = ImprovedMCTSAgent(
            num_simulations=100,
            rollout_smartness=0.0,
        )
        agents.append(("MCTS-Random", mcts_random))

        # Heuristic rollouts (standard)
        mcts_heuristic = ImprovedMCTSAgent(
            num_simulations=100,
            rollout_smartness=0.7,
        )
        agents.append(("MCTS-Heuristic", mcts_heuristic))

        # More simulations, smart rollouts
        mcts_heavy = ImprovedMCTSAgent(
            num_simulations=200,
            rollout_smartness=0.9,
        )
        agents.append(("MCTS-Heavy", mcts_heavy))

        return agents

    def create_heuristic_agents(self) -> list[tuple[str, GreedyStrategicAgent]]:
        """Create pure heuristic agents."""
        return [
            ("Greedy-Heuristic", GreedyStrategicAgent()),
        ]

    def create_baseline_agent(self) -> tuple[str, RandomAgent]:
        """Create baseline random agent."""
        return ("Random", RandomAgent())

    def run_match(
        self,
        agent1_name: str,
        agent1,
        agent2_name: str,
        agent2,
        verbose: bool = False,
    ) -> MatchResult:
        """Run a single match between two agents."""
        if verbose:
            print(f"  {agent1_name} vs {agent2_name}...", end=" ", flush=True)

        start_time = time.time()
        try:
            result = simulate_game(
                agent1, agent2, self.config,
                seed=None,  # Let it randomize
                verbose=False,
            )
            duration = time.time() - start_time

            # Extract stats (this is a simplification - in real code we'd track move times)
            winner = result.winner
            p1_territories = len(list(result.board.positions_owned_by(Owner.PLAYER_1)))
            p2_territories = len(list(result.board.positions_owned_by(Owner.PLAYER_2)))

            match_result = MatchResult(
                agent1_name=agent1_name,
                agent2_name=agent2_name,
                winner=winner,
                p1_territories=p1_territories,
                p2_territories=p2_territories,
                duration=duration,
                p1_avg_move_time=0.0,  # Would need to track in engine
                p2_avg_move_time=0.0,
            )

            if verbose:
                if winner == Owner.PLAYER_1:
                    print(f"✓ {agent1_name} wins ({p1_territories}-{p2_territories} territories)")
                elif winner == Owner.PLAYER_2:
                    print(f"✗ {agent2_name} wins ({p2_territories}-{p1_territories} territories)")
                else:
                    print(f"= Draw ({p1_territories}-{p2_territories} territories)")

            return match_result

        except Exception as e:
            if verbose:
                print(f"ERROR: {e}")
            raise

    def run_tournament(
        self,
        agents: list[tuple[str, any]],
        rounds: int = 2,
        verbose: bool = True,
    ) -> dict[str, AgentStats]:
        """Run round-robin tournament."""
        self.results = []
        self.agent_stats = {name: AgentStats(name=name) for name, _ in agents}

        total_matches = len(agents) * (len(agents) - 1) * rounds
        match_count = 0

        if verbose:
            print(f"\nRunning tournament: {len(agents)} agents × {rounds} rounds = {total_matches} matches\n")

        for _ in range(rounds):
            for i, (agent1_name, agent1) in enumerate(agents):
                for j, (agent2_name, agent2) in enumerate(agents):
                    if i >= j:  # Skip self-matches and duplicates
                        continue

                    match_count += 1
                    if verbose:
                        print(f"[{match_count}/{total_matches}]", end=" ")

                    # Player 1 vs Player 2
                    agent1.reset()
                    agent2.reset()
                    result = self.run_match(agent1_name, agent1, agent2_name, agent2, verbose=True)
                    self.results.append(result)

                    # Update stats
                    self.agent_stats[agent1_name].matches += 1
                    self.agent_stats[agent2_name].matches += 1
                    self.agent_stats[agent1_name].total_duration += result.duration
                    self.agent_stats[agent2_name].total_duration += result.duration

                    if result.winner == Owner.PLAYER_1:
                        self.agent_stats[agent1_name].wins += 1
                        self.agent_stats[agent2_name].losses += 1
                    elif result.winner == Owner.PLAYER_2:
                        self.agent_stats[agent2_name].wins += 1
                        self.agent_stats[agent1_name].losses += 1
                    else:
                        self.agent_stats[agent1_name].draws += 1
                        self.agent_stats[agent2_name].draws += 1

        return self.agent_stats

    def print_results(self):
        """Print tournament results."""
        if not self.agent_stats:
            print("No results to print")
            return

        print("\n" + "="*80)
        print("TOURNAMENT RESULTS")
        print("="*80)

        # Rankings
        rankings = sorted(
            self.agent_stats.values(),
            key=lambda x: (x.win_rate, x.matches),
            reverse=True,
        )

        print("\nRankings:")
        print(f"{'Rank':<5} {'Agent':<25} {'Record':<15} {'Win Rate':<12} {'Avg Duration':<15}")
        print("-" * 80)

        for rank, stats in enumerate(rankings, 1):
            record = f"{stats.wins}W-{stats.losses}L-{stats.draws}D"
            print(
                f"{rank:<5} {stats.name:<25} {record:<15} "
                f"{stats.win_rate:>10.1%}  {stats.avg_game_duration:>13.2f}s"
            )

        # Head-to-head details
        print("\n" + "="*80)
        print("DETAILED MATCH RESULTS")
        print("="*80)
        for result in self.results:
            if result.winner == Owner.PLAYER_1:
                outcome = f"{result.agent1_name} wins"
            elif result.winner == Owner.PLAYER_2:
                outcome = f"{result.agent2_name} wins"
            else:
                outcome = "Draw"

            print(
                f"{result.agent1_name:<25} vs {result.agent2_name:<25} | "
                f"{outcome:<30} | {result.duration:>6.2f}s"
            )


def main():
    """Run the benchmark suite."""
    print("Strategic Influence - AI Benchmarking Suite")
    print("=" * 80)

    config = create_default_config()
    benchmark = AgentBenchmark(config)

    # Test A: Minimax depth comparison (quick test with fewer rounds)
    print("\n--- TEST A: MINIMAX DEPTH COMPARISON ---")
    minimax_agents = benchmark.create_minimax_agents()
    benchmark.run_tournament(minimax_agents, rounds=2, verbose=True)
    benchmark.print_results()

    # Test B: MCTS variations
    print("\n--- TEST B: MCTS VARIATIONS ---")
    benchmark = AgentBenchmark(config)
    mcts_agents = benchmark.create_mcts_agents()
    benchmark.run_tournament(mcts_agents, rounds=2, verbose=True)
    benchmark.print_results()

    # Test C: Heuristic vs Minimax vs MCTS (comprehensive)
    print("\n--- TEST C: COMPREHENSIVE TOURNAMENT ---")
    benchmark = AgentBenchmark(config)
    all_agents = (
        [("Baseline-Random", RandomAgent())] +
        minimax_agents +
        [("Greedy-Heuristic", GreedyStrategicAgent())] +
        [(name, agent) for name, agent in mcts_agents[:2]]  # Top 2 MCTS variants
    )
    benchmark.run_tournament(all_agents, rounds=1, verbose=True)
    benchmark.print_results()

    print("\n" + "="*80)
    print("Benchmarking complete!")


if __name__ == "__main__":
    main()
