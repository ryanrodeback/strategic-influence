"""Simulation runner for batch game execution.

This module provides functions for running single games or batches of games,
with support for parallel execution and reproducibility.
"""

from dataclasses import dataclass
from random import Random
from typing import Callable
from concurrent.futures import ProcessPoolExecutor, as_completed

from ..types import Owner, GameState
from ..config import GameConfig
from ..engine import simulate_game
from ..agents.protocol import Agent


@dataclass
class GameResult:
    """Result of a single game."""
    game_id: int
    winner: Owner | None  # None = draw
    player1_territories: int
    player2_territories: int
    neutral_territories: int
    seed: int
    num_turns: int

    @property
    def is_draw(self) -> bool:
        return self.winner is None

    @property
    def player1_won(self) -> bool:
        return self.winner == Owner.PLAYER_1

    @property
    def player2_won(self) -> bool:
        return self.winner == Owner.PLAYER_2


@dataclass
class SimulationResult:
    """Aggregated results from a batch simulation."""
    config: GameConfig
    results: list[GameResult]
    player1_name: str
    player2_name: str

    @property
    def num_games(self) -> int:
        return len(self.results)

    @property
    def player1_wins(self) -> int:
        return sum(1 for r in self.results if r.player1_won)

    @property
    def player2_wins(self) -> int:
        return sum(1 for r in self.results if r.player2_won)

    @property
    def draws(self) -> int:
        return sum(1 for r in self.results if r.is_draw)

    @property
    def player1_win_rate(self) -> float:
        if self.num_games == 0:
            return 0.0
        return self.player1_wins / self.num_games

    @property
    def player2_win_rate(self) -> float:
        if self.num_games == 0:
            return 0.0
        return self.player2_wins / self.num_games

    @property
    def draw_rate(self) -> float:
        if self.num_games == 0:
            return 0.0
        return self.draws / self.num_games

    def summary(self) -> str:
        """Generate a text summary of results."""
        lines = [
            f"Simulation Results ({self.num_games} games)",
            "=" * 40,
            f"Player 1 ({self.player1_name}): {self.player1_wins} wins ({self.player1_win_rate:.1%})",
            f"Player 2 ({self.player2_name}): {self.player2_wins} wins ({self.player2_win_rate:.1%})",
            f"Draws: {self.draws} ({self.draw_rate:.1%})",
        ]
        return "\n".join(lines)


def run_single_game(
    config: GameConfig,
    player1: Agent,
    player2: Agent,
    seed: int,
    game_id: int = 0,
) -> GameResult:
    """Run a single game and return the result.

    Args:
        config: Game configuration.
        player1: Player 1 agent.
        player2: Player 2 agent.
        seed: Random seed for this game.
        game_id: Identifier for this game.

    Returns:
        GameResult with outcome data.
    """
    final_state = simulate_game(config, player1, player2, seed)

    counts = final_state.board.count_territories()

    return GameResult(
        game_id=game_id,
        winner=final_state.winner,
        player1_territories=counts[Owner.PLAYER_1],
        player2_territories=counts[Owner.PLAYER_2],
        neutral_territories=counts[Owner.NEUTRAL],
        seed=seed,
        num_turns=final_state.current_turn,
    )


def _generate_seeds(num_games: int, base_seed: int | None) -> list[int]:
    """Generate deterministic or random seeds for games."""
    if base_seed is not None:
        rng = Random(base_seed)
        return [rng.randint(0, 2**31 - 1) for _ in range(num_games)]
    else:
        rng = Random()
        return [rng.randint(0, 2**31 - 1) for _ in range(num_games)]


def run_simulation(
    config: GameConfig,
    player1_factory: Callable[[], Agent],
    player2_factory: Callable[[], Agent],
    num_games: int | None = None,
    base_seed: int | None = None,
    parallel_workers: int | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> SimulationResult:
    """Run a batch of games between two player types.

    Args:
        config: Game configuration.
        player1_factory: Factory function that creates Player 1 agents.
        player2_factory: Factory function that creates Player 2 agents.
        num_games: Number of games to run. Defaults to config value.
        base_seed: Base seed for reproducibility. None for random.
        parallel_workers: Number of parallel workers. 1 for sequential.
        progress_callback: Optional callback(completed, total) for progress.

    Returns:
        SimulationResult with all game outcomes.
    """
    if num_games is None:
        num_games = config.simulation.default_num_games

    if parallel_workers is None:
        parallel_workers = config.simulation.parallel_workers

    if base_seed is None:
        base_seed = config.simulation.random_seed

    seeds = _generate_seeds(num_games, base_seed)

    # Get agent names from a sample
    sample_p1 = player1_factory()
    sample_p2 = player2_factory()
    p1_name = sample_p1.name
    p2_name = sample_p2.name

    results: list[GameResult] = []

    if parallel_workers <= 1:
        # Sequential execution
        for i, seed in enumerate(seeds):
            p1 = player1_factory()
            p2 = player2_factory()
            result = run_single_game(config, p1, p2, seed, game_id=i)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, num_games)
    else:
        # Parallel execution
        # Note: For true parallelism, we'd need to ensure agents are picklable
        # For now, we use sequential in a way that could be parallelized
        for i, seed in enumerate(seeds):
            p1 = player1_factory()
            p2 = player2_factory()
            result = run_single_game(config, p1, p2, seed, game_id=i)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, num_games)

    return SimulationResult(
        config=config,
        results=results,
        player1_name=p1_name,
        player2_name=p2_name,
    )


def compare_agents(
    config: GameConfig,
    agent1_factory: Callable[[], Agent],
    agent2_factory: Callable[[], Agent],
    num_games: int = 100,
    base_seed: int | None = 42,
) -> dict:
    """Compare two agents head-to-head.

    Runs games with both orderings to control for first-player advantage.

    Args:
        config: Game configuration.
        agent1_factory: Factory for first agent type.
        agent2_factory: Factory for second agent type.
        num_games: Total games (split evenly between orderings).
        base_seed: Random seed for reproducibility.

    Returns:
        Dictionary with comparison statistics.
    """
    half = num_games // 2

    # Agent 1 as Player 1
    result_1_first = run_simulation(
        config, agent1_factory, agent2_factory,
        num_games=half, base_seed=base_seed
    )

    # Agent 1 as Player 2
    result_1_second = run_simulation(
        config, agent2_factory, agent1_factory,
        num_games=half, base_seed=(base_seed + 1000 if base_seed else None)
    )

    # Calculate aggregate stats
    agent1_wins = result_1_first.player1_wins + result_1_second.player2_wins
    agent2_wins = result_1_first.player2_wins + result_1_second.player1_wins
    draws = result_1_first.draws + result_1_second.draws

    total = agent1_wins + agent2_wins + draws

    return {
        "agent1_name": result_1_first.player1_name,
        "agent2_name": result_1_first.player2_name,
        "agent1_wins": agent1_wins,
        "agent2_wins": agent2_wins,
        "draws": draws,
        "total_games": total,
        "agent1_win_rate": agent1_wins / total if total > 0 else 0,
        "agent2_win_rate": agent2_wins / total if total > 0 else 0,
    }
