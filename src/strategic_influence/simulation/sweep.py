"""Parameter sweep framework for experiments.

This module provides tools for systematically varying game parameters
and measuring the effects on game outcomes.
"""

from dataclasses import dataclass
from typing import Any, Callable, Sequence
import itertools

from ..config import GameConfig, with_override
from ..agents.protocol import Agent
from .runner import run_simulation, SimulationResult


@dataclass
class ParameterSweep:
    """Definition of a parameter sweep.

    Attributes:
        path: Dot-notation path to the parameter (e.g., "influence.k_value").
        values: Sequence of values to test.
        name: Optional display name for the parameter.
    """
    path: str
    values: Sequence[Any]
    name: str | None = None

    @property
    def display_name(self) -> str:
        return self.name or self.path


@dataclass
class SweepResult:
    """Results from a parameter sweep."""
    sweep: ParameterSweep
    results_by_value: dict[Any, SimulationResult]
    base_config: GameConfig

    def summary_table(self) -> str:
        """Generate a summary table of results."""
        lines = [
            f"Parameter Sweep: {self.sweep.display_name}",
            "=" * 60,
            f"{'Value':<15} {'P1 Wins':<10} {'P2 Wins':<10} {'Draws':<10} {'P1 Rate':<10}",
            "-" * 60,
        ]

        for value in self.sweep.values:
            result = self.results_by_value.get(value)
            if result:
                lines.append(
                    f"{str(value):<15} "
                    f"{result.player1_wins:<10} "
                    f"{result.player2_wins:<10} "
                    f"{result.draws:<10} "
                    f"{result.player1_win_rate:.1%}"
                )

        return "\n".join(lines)

    def to_csv(self) -> str:
        """Export results as CSV."""
        lines = ["value,p1_wins,p2_wins,draws,p1_win_rate,p2_win_rate"]

        for value in self.sweep.values:
            result = self.results_by_value.get(value)
            if result:
                lines.append(
                    f"{value},{result.player1_wins},{result.player2_wins},"
                    f"{result.draws},{result.player1_win_rate:.4f},{result.player2_win_rate:.4f}"
                )

        return "\n".join(lines)


def run_parameter_sweep(
    base_config: GameConfig,
    sweep: ParameterSweep,
    player1_factory: Callable[[], Agent],
    player2_factory: Callable[[], Agent],
    runs_per_value: int = 100,
    base_seed: int = 42,
    progress_callback: Callable[[str, int, int], None] | None = None,
) -> SweepResult:
    """Run a parameter sweep experiment.

    Args:
        base_config: Base configuration to modify.
        sweep: Parameter sweep definition.
        player1_factory: Factory for Player 1 agents.
        player2_factory: Factory for Player 2 agents.
        runs_per_value: Number of games per parameter value.
        base_seed: Base seed for reproducibility.
        progress_callback: Optional callback(param_value, completed, total).

    Returns:
        SweepResult with results for each parameter value.
    """
    results_by_value: dict[Any, SimulationResult] = {}

    for i, value in enumerate(sweep.values):
        # Create modified config
        modified_config = with_override(base_config, sweep.path, value)

        # Run simulation with this config
        # Use different seed offset for each value to avoid correlations
        seed = base_seed + i * 10000 if base_seed is not None else None

        result = run_simulation(
            config=modified_config,
            player1_factory=player1_factory,
            player2_factory=player2_factory,
            num_games=runs_per_value,
            base_seed=seed,
            parallel_workers=1,  # Sequential for now
        )

        results_by_value[value] = result

        if progress_callback:
            progress_callback(str(value), i + 1, len(sweep.values))

    return SweepResult(
        sweep=sweep,
        results_by_value=results_by_value,
        base_config=base_config,
    )


@dataclass
class GridSweepResult:
    """Results from a grid sweep over multiple parameters."""
    sweeps: list[ParameterSweep]
    results: dict[tuple, SimulationResult]  # (value1, value2, ...) -> result
    base_config: GameConfig

    def summary(self) -> str:
        """Generate summary of grid sweep."""
        lines = [
            "Grid Sweep Results",
            "=" * 60,
            f"Parameters: {', '.join(s.display_name for s in self.sweeps)}",
            f"Total combinations: {len(self.results)}",
            "-" * 60,
        ]

        for combo, result in sorted(self.results.items()):
            combo_str = ", ".join(f"{s.display_name}={v}" for s, v in zip(self.sweeps, combo))
            lines.append(f"{combo_str}: P1={result.player1_win_rate:.1%}")

        return "\n".join(lines)


def run_grid_sweep(
    base_config: GameConfig,
    sweeps: list[ParameterSweep],
    player1_factory: Callable[[], Agent],
    player2_factory: Callable[[], Agent],
    runs_per_combination: int = 50,
    base_seed: int = 42,
) -> GridSweepResult:
    """Run a grid sweep over multiple parameters.

    Tests all combinations of parameter values.

    Args:
        base_config: Base configuration.
        sweeps: List of parameter sweeps.
        player1_factory: Factory for Player 1.
        player2_factory: Factory for Player 2.
        runs_per_combination: Games per combination.
        base_seed: Random seed.

    Returns:
        GridSweepResult with results for all combinations.
    """
    results: dict[tuple, SimulationResult] = {}

    # Generate all combinations
    value_lists = [sweep.values for sweep in sweeps]
    paths = [sweep.path for sweep in sweeps]

    for i, combo in enumerate(itertools.product(*value_lists)):
        # Create config with all parameter values
        modified_config = base_config
        for path, value in zip(paths, combo):
            modified_config = with_override(modified_config, path, value)

        # Run simulation
        seed = base_seed + i * 10000 if base_seed is not None else None

        result = run_simulation(
            config=modified_config,
            player1_factory=player1_factory,
            player2_factory=player2_factory,
            num_games=runs_per_combination,
            base_seed=seed,
            parallel_workers=1,
        )

        results[combo] = result

    return GridSweepResult(
        sweeps=sweeps,
        results=results,
        base_config=base_config,
    )
