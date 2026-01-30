"""Simulation framework for Strategic Influence.

This module provides tools for running batch simulations,
parameter sweeps, and statistical analysis.
"""

from .runner import run_simulation, run_single_game, SimulationResult, GameResult
from .sweep import run_parameter_sweep, ParameterSweep, SweepResult
from .statistics import (
    calculate_win_rates,
    wilson_score_interval,
    territory_statistics,
)

__all__ = [
    "run_simulation",
    "run_single_game",
    "SimulationResult",
    "GameResult",
    "run_parameter_sweep",
    "ParameterSweep",
    "SweepResult",
    "calculate_win_rates",
    "wilson_score_interval",
    "territory_statistics",
]
