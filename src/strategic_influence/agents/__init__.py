"""Agent implementations for Strategic Influence.

V3: Enhanced AI agents with minimax, improved MCTS, and strategic hypotheses.

This module provides various AI and human player implementations.

Core agents for tournaments:
- DefensiveBot: Safety-first, currently top performer
- IntuitionBot: User's safe-division hypothesis
- StrategicBot: Balanced phase-aware play
- MinimaxBot: Game tree search (tunable depth)
- ImprovedMCTS: Monte Carlo simulation (tunable)

Baseline/utility agents:
- RandomBot: Sanity check baseline
- AggressiveBot: Attack-focused (for comparison)
"""

from .protocol import Agent
from .random_agent import RandomAgent
from .aggressive_agent import AggressiveAgent
from .defensive_agent import DefensiveAgent
from .rush_agent import RushAgent
from .strategic_agent import StrategicAgent
from .human import HumanAgent
from .monte_carlo_agent import MonteCarloAgent
from .intuition_agent import IntuitionAgent
from .minimax_agent import MinimaxAgent
from .improved_mcts_agent import ImprovedMCTSAgent
from .greedy_strategic_agent import GreedyStrategicAgent

__all__ = [
    "Agent",
    "RandomAgent",
    "AggressiveAgent",
    "DefensiveAgent",
    "RushAgent",
    "StrategicAgent",
    "HumanAgent",
    "MonteCarloAgent",
    "IntuitionAgent",
    "MinimaxAgent",
    "ImprovedMCTSAgent",
    "GreedyStrategicAgent",
]
