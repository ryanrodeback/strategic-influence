"""Agent implementations for Strategic Influence.

Core tournament agents:
- DefensiveBot: Safety-first positional strategy
- IntuitionBot: Safe-division hypothesis with threat awareness
- MinimaxBot: Game tree search with alpha-beta pruning (tunable depth)
- ImprovedMCTSBot: Monte Carlo tree search with heuristic rollouts

Baseline agents:
- RandomBot: Random baseline for sanity checks
- AggressiveBot: Attack-focused heuristic strategy
- GreedyStrategic: Fast greedy strategy (Minimax insights without search)

Utility agents:
- HumanAgent: Interactive human player
"""

from .protocol import Agent
from .random_agent import RandomAgent
from .aggressive_agent import AggressiveAgent
from .defensive_agent import DefensiveAgent
from .human import HumanAgent
from .intuition_agent import IntuitionAgent
from .minimax_agent import MinimaxAgent
from .improved_mcts_agent import ImprovedMCTSAgent
from .greedy_strategic_agent import GreedyStrategicAgent

__all__ = [
    "Agent",
    "RandomAgent",
    "AggressiveAgent",
    "DefensiveAgent",
    "HumanAgent",
    "IntuitionAgent",
    "MinimaxAgent",
    "ImprovedMCTSAgent",
    "GreedyStrategicAgent",
]
