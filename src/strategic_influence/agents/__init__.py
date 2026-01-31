"""Agent implementations for Strategic Influence.

Tournament-proven agents (recommended):
- OptimizedMinimaxAgent: Best AI with 100% win rate (use depth=1)
- GreedyStrategicAgent: Fast heuristic with 78.6% win rate
- ImprovedMCTSAgent: MCTS with random rollouts (research use)

Utility agents:
- RandomAgent: Random baseline for testing
- HumanAgent: Interactive human player
"""

from .protocol import Agent
from .random_agent import RandomAgent
from .human import HumanAgent
from .greedy_strategic_agent import GreedyStrategicAgent
from .optimized_minimax_agent import OptimizedMinimaxAgent
from .improved_mcts_agent import ImprovedMCTSAgent

__all__ = [
    "Agent",
    "RandomAgent",
    "HumanAgent",
    "GreedyStrategicAgent",
    "OptimizedMinimaxAgent",
    "ImprovedMCTSAgent",
]
