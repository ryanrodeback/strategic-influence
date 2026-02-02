"""March of Empires - A hex-based strategy game.

A two-player strategy game of territorial expansion and tactical maneuvering.
Players build settlements, command armies, and contest hexagonal terrain under
fog of war. Victory belongs to the player who controls the most territory
after 25 turns.
"""

from .types import (
    Player,
    GamePhase,
    HexCoord,
    CornerCoord,
    CornerDirection,
    Position,
    Army,
    Settlement,
    GameBoard,
    GameState,
    VisibleState,
    Action,
    MoveAction,
    SettleAction,
    PassAction,
    TurnActions,
    TurnResult,
    CombatResult,
    CaptureResult,
    SpawnResult,
    create_empty_board,
    generate_hex_board,
    generate_all_corners,
)

from .config import (
    GameConfig,
    GameRulesConfig,
    MovementConfig,
    CaptureConfig,
    create_default_config,
)

from .engine import (
    create_game,
    apply_setup,
    apply_turn,
    calculate_score,
    determine_winner,
    create_visible_state,
    get_setup_zone,
    get_reachable_positions,
    can_settle,
)

from .agents import (
    Agent,
    RandomAgent,
    ExpansionAgent,
    AggressiveAgent,
    DefensiveAgent,
    BalancedHeuristicAgent,
    MCTSAgent,
)

__all__ = [
    # Types
    "Player",
    "GamePhase",
    "HexCoord",
    "CornerCoord",
    "CornerDirection",
    "Position",
    "Army",
    "Settlement",
    "GameBoard",
    "GameState",
    "VisibleState",
    "Action",
    "MoveAction",
    "SettleAction",
    "PassAction",
    "TurnActions",
    "TurnResult",
    "CombatResult",
    "CaptureResult",
    "SpawnResult",
    "create_empty_board",
    "generate_hex_board",
    "generate_all_corners",
    # Config
    "GameConfig",
    "GameRulesConfig",
    "MovementConfig",
    "CaptureConfig",
    "create_default_config",
    # Engine
    "create_game",
    "apply_setup",
    "apply_turn",
    "calculate_score",
    "determine_winner",
    "create_visible_state",
    "get_setup_zone",
    "get_reachable_positions",
    "can_settle",
    # Agents
    "Agent",
    "RandomAgent",
    "ExpansionAgent",
    "AggressiveAgent",
    "DefensiveAgent",
    "BalancedHeuristicAgent",
    "MCTSAgent",
]
