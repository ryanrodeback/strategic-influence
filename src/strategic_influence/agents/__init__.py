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

MCTS Variants (improved evaluation strategies):
- MCTSHeuristicEval: MCTS with heuristic evaluation at leaf nodes
- MCTSMinimaxEval: MCTS with depth-1 minimax evaluation at leaf nodes
- MCTSHeuristicRollout: MCTS with pure greedy heuristic rollouts

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
from .heuristic_minimax_agent import HeuristicMinimaxAgent
from .mcts_variants import (
    MCTSHeuristicEval,
    MCTSMinimaxEval,
    MCTSHeuristicRollout,
)
from .expectimax_agent import ExpectimaxAgent

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
    "HeuristicMinimaxAgent",
    "MCTSHeuristicEval",
    "MCTSMinimaxEval",
    "MCTSHeuristicRollout",
    "ExpectimaxAgent",
]
