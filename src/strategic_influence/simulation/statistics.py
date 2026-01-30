"""Statistical analysis utilities for simulation results.

This module provides functions for calculating win rates, confidence intervals,
and other statistics from simulation results.
"""

import math
from typing import Sequence

from ..types import Owner
from .runner import SimulationResult, GameResult


def calculate_win_rates(results: SimulationResult) -> dict[str, float]:
    """Calculate win rates from simulation results.

    Args:
        results: Simulation results to analyze.

    Returns:
        Dictionary with win rates for each outcome.
    """
    total = results.num_games
    if total == 0:
        return {
            "player1": 0.0,
            "player2": 0.0,
            "draw": 0.0,
        }

    return {
        "player1": results.player1_wins / total,
        "player2": results.player2_wins / total,
        "draw": results.draws / total,
    }


def wilson_score_interval(
    successes: int,
    total: int,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Calculate Wilson score confidence interval for a proportion.

    The Wilson score interval is more accurate than the normal approximation,
    especially for proportions near 0 or 1 or with small sample sizes.

    Args:
        successes: Number of successes (e.g., wins).
        total: Total number of trials (e.g., games).
        confidence: Confidence level (default 0.95 for 95% CI).

    Returns:
        Tuple of (lower_bound, upper_bound).
    """
    if total == 0:
        return (0.0, 1.0)

    # Z-score for confidence level (approximate)
    # For 95% confidence, z ≈ 1.96
    z_scores = {
        0.90: 1.645,
        0.95: 1.960,
        0.99: 2.576,
    }
    z = z_scores.get(confidence, 1.960)

    p_hat = successes / total
    n = total

    denominator = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denominator
    margin = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n) / denominator

    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)

    return (lower, upper)


def territory_statistics(results: SimulationResult) -> dict[str, float]:
    """Calculate territory count statistics.

    Args:
        results: Simulation results.

    Returns:
        Dictionary with mean and std for each player's territories.
    """
    if not results.results:
        return {
            "player1_mean": 0.0,
            "player1_std": 0.0,
            "player2_mean": 0.0,
            "player2_std": 0.0,
            "neutral_mean": 0.0,
            "margin_mean": 0.0,
        }

    p1_territories = [r.player1_territories for r in results.results]
    p2_territories = [r.player2_territories for r in results.results]
    neutral_territories = [r.neutral_territories for r in results.results]

    p1_mean = sum(p1_territories) / len(p1_territories)
    p2_mean = sum(p2_territories) / len(p2_territories)
    neutral_mean = sum(neutral_territories) / len(neutral_territories)

    p1_std = _std(p1_territories)
    p2_std = _std(p2_territories)

    margins = [p1 - p2 for p1, p2 in zip(p1_territories, p2_territories)]
    margin_mean = sum(margins) / len(margins)

    return {
        "player1_mean": p1_mean,
        "player1_std": p1_std,
        "player2_mean": p2_mean,
        "player2_std": p2_std,
        "neutral_mean": neutral_mean,
        "margin_mean": margin_mean,
    }


def _std(values: Sequence[float]) -> float:
    """Calculate standard deviation."""
    if len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def significance_test(
    results1: SimulationResult,
    results2: SimulationResult,
) -> dict:
    """Test if win rates differ significantly between two simulations.

    Uses a two-proportion z-test.

    Args:
        results1: First simulation results.
        results2: Second simulation results.

    Returns:
        Dictionary with test statistics and p-value.
    """
    n1 = results1.num_games
    n2 = results2.num_games
    p1 = results1.player1_win_rate
    p2 = results2.player1_win_rate

    if n1 == 0 or n2 == 0:
        return {
            "z_statistic": 0.0,
            "p_value": 1.0,
            "significant_at_05": False,
            "difference": 0.0,
        }

    # Pooled proportion
    pooled_successes = results1.player1_wins + results2.player1_wins
    pooled_total = n1 + n2
    p_pooled = pooled_successes / pooled_total

    # Standard error
    se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))

    if se == 0:
        return {
            "z_statistic": 0.0,
            "p_value": 1.0,
            "significant_at_05": False,
            "difference": p1 - p2,
        }

    z = (p1 - p2) / se

    # Two-tailed p-value (approximate using normal distribution)
    # For |z| > 1.96, p < 0.05
    # For |z| > 2.576, p < 0.01
    abs_z = abs(z)
    if abs_z > 3.5:
        p_value = 0.0005
    elif abs_z > 2.576:
        p_value = 0.01
    elif abs_z > 1.96:
        p_value = 0.05
    elif abs_z > 1.645:
        p_value = 0.10
    else:
        p_value = 0.5  # Rough approximation

    return {
        "z_statistic": z,
        "p_value": p_value,
        "significant_at_05": p_value < 0.05,
        "difference": p1 - p2,
    }


def analysis_report(results: SimulationResult) -> str:
    """Generate a comprehensive analysis report.

    Args:
        results: Simulation results to analyze.

    Returns:
        Multi-line string with analysis.
    """
    win_rates = calculate_win_rates(results)
    p1_ci = wilson_score_interval(results.player1_wins, results.num_games)
    p2_ci = wilson_score_interval(results.player2_wins, results.num_games)
    territory_stats = territory_statistics(results)

    lines = [
        "=" * 60,
        "SIMULATION ANALYSIS REPORT",
        "=" * 60,
        "",
        f"Games Played: {results.num_games}",
        f"Player 1: {results.player1_name}",
        f"Player 2: {results.player2_name}",
        "",
        "WIN RATES",
        "-" * 40,
        f"Player 1: {win_rates['player1']:.1%} (95% CI: {p1_ci[0]:.1%} - {p1_ci[1]:.1%})",
        f"Player 2: {win_rates['player2']:.1%} (95% CI: {p2_ci[0]:.1%} - {p2_ci[1]:.1%})",
        f"Draws:    {win_rates['draw']:.1%}",
        "",
        "TERRITORY STATISTICS",
        "-" * 40,
        f"Player 1 avg territories: {territory_stats['player1_mean']:.1f} (std: {territory_stats['player1_std']:.1f})",
        f"Player 2 avg territories: {territory_stats['player2_mean']:.1f} (std: {territory_stats['player2_std']:.1f})",
        f"Neutral avg territories:  {territory_stats['neutral_mean']:.1f}",
        f"Average margin (P1-P2):   {territory_stats['margin_mean']:.1f}",
        "",
        "=" * 60,
    ]

    return "\n".join(lines)
