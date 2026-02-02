"""Game engine for March of Empires.

This module handles:
- Game creation and setup
- Turn execution
- Victory determination
"""

from __future__ import annotations

from typing import Sequence

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
)
from .config import GameConfig, create_default_config


# =============================================================================
# Game Creation
# =============================================================================


def create_game(config: GameConfig | None = None) -> GameState:
    """Create a new game in setup phase."""
    if config is None:
        config = create_default_config()

    board = create_empty_board(config.board_radius)
    return GameState(
        board=board,
        phase=GamePhase.SETUP,
        current_turn=0,
        active_player=Player.PLAYER_1,
        turn_history=(),
        setup_complete=frozenset(),
        winner=None,
    )


# =============================================================================
# Setup Phase
# =============================================================================


def get_setup_zone(player: Player, board_radius: int) -> frozenset[CornerCoord]:
    """Return valid corner positions for player's starting settlement.

    Player 1: Bottom half of board (positive r values, which is "south")
    Player 2: Top half of board (negative r values, which is "north")

    The zones are exclusive (r=0 corners split by direction to avoid overlap).
    """
    from .types import generate_all_corners

    all_corners = generate_all_corners(board_radius)

    if player == Player.PLAYER_1:
        # Player 1 gets southern half: r > 0, OR r = 0 with SOUTH direction
        return frozenset(
            c for c in all_corners
            if c.r > 0 or (c.r == 0 and c.direction == CornerDirection.SOUTH)
        )
    else:
        # Player 2 gets northern half: r < 0, OR r = 0 with NORTH direction
        return frozenset(
            c for c in all_corners
            if c.r < 0 or (c.r == 0 and c.direction == CornerDirection.NORTH)
        )


def validate_setup_action(
    corner: CornerCoord,
    state: GameState,
    player: Player,
    config: GameConfig,
) -> tuple[bool, str | None]:
    """Validate a setup placement."""
    if player in state.setup_complete:
        return False, f"{player} has already completed setup"

    if state.active_player != player:
        return False, f"Not {player}'s turn to set up"

    valid_zone = get_setup_zone(player, config.board_radius)
    if corner not in valid_zone:
        return False, f"Corner {corner} is not in {player}'s setup zone"

    if state.board.settlement_at(corner) is not None:
        return False, f"Corner {corner} is already occupied"

    if not corner.is_valid(config.board_radius):
        return False, f"Corner {corner} is not on the board"

    return True, None


def apply_setup(
    state: GameState,
    corner: CornerCoord,
    player: Player,
    config: GameConfig | None = None,
) -> GameState:
    """Apply a setup placement.

    Creates:
    - Settlement at the corner
    - One army at the corner
    """
    if config is None:
        config = create_default_config()

    valid, error = validate_setup_action(corner, state, player, config)
    if not valid:
        raise ValueError(f"Invalid setup: {error}")

    # Create settlement
    board, settlement = state.board.with_settlement(corner, player)

    # Create initial army at the settlement
    board, army = board.with_army(corner, player, config.movement.points_per_turn)

    # Update setup tracking
    new_setup_complete = state.setup_complete | {player}

    # Check if setup is complete
    if Player.PLAYER_1 in new_setup_complete and Player.PLAYER_2 in new_setup_complete:
        new_phase = GamePhase.PLAYING
        next_player = Player.PLAYER_1  # P1 goes first
        current_turn = 1
    else:
        new_phase = GamePhase.SETUP
        next_player = player.opponent()
        current_turn = 0

    return GameState(
        board=board,
        phase=new_phase,
        current_turn=current_turn,
        active_player=next_player,
        turn_history=state.turn_history,
        setup_complete=new_setup_complete,
        winner=None,
    )


# =============================================================================
# Movement Helpers
# =============================================================================


def calculate_movement_cost(
    from_pos: Position,
    to_pos: Position,
    player: Player,
    board: GameBoard,
    config: GameConfig,
) -> int | None:
    """Calculate movement cost between adjacent positions.

    Returns None if positions are not adjacent.

    Rules:
    - Hex <-> Corner: 1 point
    - Hex -> Friendly Hex: 1 point
    - Hex -> Neutral/Enemy Hex: 2 points
    """
    mc = config.movement

    # Hex to Hex
    if isinstance(from_pos, HexCoord) and isinstance(to_pos, HexCoord):
        if to_pos not in from_pos.neighbors():
            return None
        if board.is_hex_friendly(to_pos, player):
            return mc.friendly_hex_cost
        return mc.neutral_hex_cost

    # Hex to Corner
    if isinstance(from_pos, HexCoord) and isinstance(to_pos, CornerCoord):
        if from_pos not in to_pos.adjacent_hexes():
            return None
        return mc.hex_corner_transition

    # Corner to Hex
    if isinstance(from_pos, CornerCoord) and isinstance(to_pos, HexCoord):
        if to_pos not in from_pos.adjacent_hexes():
            return None
        # When entering a hex from a corner, we just pay the corner-hex cost
        # The hex ownership doesn't affect corner-to-hex transition
        return mc.hex_corner_transition

    # Corner to Corner (through adjacent corner)
    if isinstance(from_pos, CornerCoord) and isinstance(to_pos, CornerCoord):
        if to_pos not in from_pos.adjacent_corners():
            return None
        return mc.hex_corner_transition

    return None


def is_adjacent(from_pos: Position, to_pos: Position, radius: int) -> bool:
    """Check if two positions are adjacent."""
    if isinstance(from_pos, HexCoord) and isinstance(to_pos, HexCoord):
        return to_pos in from_pos.valid_neighbors(radius)

    if isinstance(from_pos, HexCoord) and isinstance(to_pos, CornerCoord):
        return from_pos in to_pos.valid_adjacent_hexes(radius)

    if isinstance(from_pos, CornerCoord) and isinstance(to_pos, HexCoord):
        return to_pos in from_pos.valid_adjacent_hexes(radius)

    if isinstance(from_pos, CornerCoord) and isinstance(to_pos, CornerCoord):
        return to_pos in from_pos.valid_adjacent_corners(radius)

    return False


def get_reachable_positions(
    army: Army,
    board: GameBoard,
    config: GameConfig,
) -> dict[Position, int]:
    """Get all positions reachable by an army with remaining movement.

    Returns dict mapping position -> remaining_mp after reaching it.
    Uses BFS to find all reachable positions.
    """
    reachable: dict[Position, int] = {army.position: army.movement_remaining}
    to_explore: list[tuple[Position, int]] = [(army.position, army.movement_remaining)]

    while to_explore:
        current_pos, remaining_mp = to_explore.pop(0)

        if remaining_mp <= 0:
            continue

        # Get adjacent positions
        adjacent: list[Position] = []
        if isinstance(current_pos, HexCoord):
            adjacent.extend(current_pos.valid_neighbors(board.radius))
            adjacent.extend(current_pos.valid_corners(board.radius))
        else:  # CornerCoord
            adjacent.extend(current_pos.valid_adjacent_hexes(board.radius))
            adjacent.extend(current_pos.valid_adjacent_corners(board.radius))

        for next_pos in adjacent:
            cost = calculate_movement_cost(
                current_pos, next_pos, army.owner, board, config
            )
            if cost is None or cost > remaining_mp:
                continue

            new_remaining = remaining_mp - cost
            # Only add if we found a better path or haven't visited
            if next_pos not in reachable or new_remaining > reachable[next_pos]:
                reachable[next_pos] = new_remaining
                to_explore.append((next_pos, new_remaining))

    return reachable


# =============================================================================
# Action Validation
# =============================================================================


def validate_move_action(
    action: MoveAction,
    board: GameBoard,
    player: Player,
    config: GameConfig,
) -> tuple[bool, str | None]:
    """Validate a move action."""
    army = board.army_by_id(action.army_id)
    if army is None:
        return False, f"Army {action.army_id} not found"

    if army.owner != player:
        return False, f"Army {action.army_id} belongs to {army.owner}, not {player}"

    # Check adjacency and calculate cost
    cost = calculate_movement_cost(army.position, action.to_position, player, board, config)
    if cost is None:
        return False, f"Cannot move from {army.position} to {action.to_position} (not adjacent)"

    if army.movement_remaining < cost:
        return False, f"Army has {army.movement_remaining} MP, needs {cost}"

    return True, None


def validate_settle_action(
    action: SettleAction,
    board: GameBoard,
    player: Player,
    config: GameConfig,
    started_on_corner: bool,
) -> tuple[bool, str | None]:
    """Validate a settle action."""
    army = board.army_by_id(action.army_id)
    if army is None:
        return False, f"Army {action.army_id} not found"

    if army.owner != player:
        return False, f"Army {action.army_id} belongs to {army.owner}, not {player}"

    if not isinstance(army.position, CornerCoord):
        return False, "Army must be on a corner to settle"

    if not started_on_corner:
        return False, "Army must START the turn on a corner to settle"

    if army.movement_remaining < config.movement.settle_cost:
        return False, f"Army has {army.movement_remaining} MP, needs {config.movement.settle_cost} to settle"

    if board.settlement_at(army.position) is not None:
        return False, "Corner already has a settlement"

    return True, None


# =============================================================================
# Turn Execution
# =============================================================================


def resolve_spawns(
    board: GameBoard,
    player: Player,
    pending_settlements: frozenset[CornerCoord],
    config: GameConfig,
) -> tuple[GameBoard, tuple[SpawnResult, ...]]:
    """Resolve army spawning at start of player's turn.

    Spawns happen for:
    1. Armies destroyed since last turn (respawn at most central settlement)
    """
    spawns: list[SpawnResult] = []
    current_board = board

    army_cap = current_board.army_cap(player)
    current_armies = current_board.army_count(player)
    armies_to_spawn = army_cap - current_armies

    if armies_to_spawn <= 0:
        return current_board, ()

    # Find most central settlement for respawns
    settlements = list(current_board.settlements_of(player))
    if not settlements:
        return current_board, ()

    center = HexCoord(0, 0)

    def settlement_centrality(s: Settlement) -> float:
        adjacent = s.position.valid_adjacent_hexes(current_board.radius)
        if not adjacent:
            return float("inf")
        return min(h.distance_to(center) for h in adjacent)

    settlements.sort(key=settlement_centrality)
    central_settlement = settlements[0]

    # Spawn armies at central settlement
    for _ in range(armies_to_spawn):
        current_board, army = current_board.with_army(
            central_settlement.position,
            player,
            config.movement.points_per_turn,
        )
        spawns.append(
            SpawnResult(army=army, settlement=central_settlement, reason="respawn")
        )

    return current_board, tuple(spawns)


def resolve_combat(board: GameBoard) -> tuple[GameBoard, tuple[CombatResult, ...]]:
    """Resolve all combat situations on the board.

    Combat happens when armies of different players occupy the same position.
    Combat is mutual destruction: armies destroy each other 1:1.
    """
    combats: list[CombatResult] = []
    current_board = board

    # Find all contested positions
    positions_with_armies: dict[Position, list[Army]] = {}
    for army in current_board.armies:
        if army.position not in positions_with_armies:
            positions_with_armies[army.position] = []
        positions_with_armies[army.position].append(army)

    for pos, armies in positions_with_armies.items():
        p1_armies = [a for a in armies if a.owner == Player.PLAYER_1]
        p2_armies = [a for a in armies if a.owner == Player.PLAYER_2]

        if not p1_armies or not p2_armies:
            continue

        # Mutual destruction
        p1_count = len(p1_armies)
        p2_count = len(p2_armies)
        destroyed = min(p1_count, p2_count)

        p1_destroyed = p1_armies[:destroyed]
        p2_destroyed = p2_armies[:destroyed]

        # Remove destroyed armies
        for army in p1_destroyed:
            current_board = current_board.without_army(army.id)
        for army in p2_destroyed:
            current_board = current_board.without_army(army.id)

        combats.append(
            CombatResult(
                position=pos,
                attacker_armies=tuple(p1_armies),
                defender_armies=tuple(p2_armies),
                attacker_survivors=p1_count - destroyed,
                defender_survivors=p2_count - destroyed,
                attacker_destroyed=tuple(a.id for a in p1_destroyed),
                defender_destroyed=tuple(a.id for a in p2_destroyed),
            )
        )

    return current_board, tuple(combats)


def resolve_captures(
    board: GameBoard,
    acting_player: Player,
    config: GameConfig,
) -> tuple[GameBoard, tuple[CaptureResult, ...]]:
    """Resolve settlement capture attempts at end of turn."""
    captures: list[CaptureResult] = []
    current_board = board
    opponent = acting_player.opponent()

    # Check all enemy settlements
    for settlement in list(current_board.settlements_of(opponent)):
        corner = settlement.position
        armies_here = current_board.armies_at(corner)

        attacker_armies = [a for a in armies_here if a.owner == acting_player]
        defender_armies = [a for a in armies_here if a.owner == opponent]

        is_defended = len(defender_armies) > 0
        required = (
            config.capture.defended_armies_required
            if is_defended
            else config.capture.undefended_armies_required
        )

        if len(attacker_armies) >= required:
            # Capture succeeds!
            defender_destroyed = None

            # Remove defending army if present
            for army in defender_armies:
                current_board = current_board.without_army(army.id)
                defender_destroyed = army.id

            # Transfer settlement ownership
            current_board = current_board.with_settlement_captured(
                settlement.id, acting_player
            )

            captures.append(
                CaptureResult(
                    settlement_id=settlement.id,
                    corner=corner,
                    capturing_player=acting_player,
                    previous_owner=opponent,
                    defender_destroyed=defender_destroyed,
                )
            )

    return current_board, tuple(captures)


def apply_turn(
    state: GameState,
    actions: TurnActions,
    config: GameConfig | None = None,
) -> GameState:
    """Apply a complete player turn.

    Turn phases:
    1. START OF TURN: Spawn armies (respawns for destroyed armies)
    2. EXECUTE ACTIONS: Process all moves and settlements
    3. COMBAT: Resolve army-vs-army combat
    4. CAPTURES: Resolve settlement captures
    5. ADVANCE: Check game end or advance turn
    """
    if config is None:
        config = create_default_config()

    if state.phase != GamePhase.PLAYING:
        raise ValueError(f"Cannot apply turn in {state.phase} phase")

    if actions.player != state.active_player:
        raise ValueError(
            f"Expected {state.active_player}'s turn, got {actions.player}"
        )

    player = actions.player
    board = state.board
    board_before = board

    # Phase 1: Spawns (armies respawn if under cap)
    board, spawns = resolve_spawns(board, player, frozenset(), config)

    # Track which armies started on corners (for settle validation)
    armies_starting_on_corners: set[int] = set()
    for army in board.armies_of(player):
        if isinstance(army.position, CornerCoord):
            armies_starting_on_corners.add(army.id)

    # Phase 2: Execute actions
    new_settlements: list[Settlement] = []

    for action in actions.actions:
        if isinstance(action, MoveAction):
            valid, error = validate_move_action(action, board, player, config)
            if not valid:
                raise ValueError(f"Invalid move: {error}")

            army = board.army_by_id(action.army_id)
            cost = calculate_movement_cost(
                army.position, action.to_position, player, board, config
            )
            board = board.with_army_moved(action.army_id, action.to_position, cost)

        elif isinstance(action, SettleAction):
            started_on_corner = action.army_id in armies_starting_on_corners
            valid, error = validate_settle_action(
                action, board, player, config, started_on_corner
            )
            if not valid:
                raise ValueError(f"Invalid settle: {error}")

            army = board.army_by_id(action.army_id)
            # Deduct movement points
            board = board.with_army_moved(
                action.army_id, army.position, config.movement.settle_cost
            )
            # Create settlement
            board, settlement = board.with_settlement(army.position, player)
            new_settlements.append(settlement)

        elif isinstance(action, PassAction):
            # Do nothing, army keeps position but loses remaining MP
            army = board.army_by_id(action.army_id)
            if army is not None and army.owner == player:
                board = board.with_army_moved(
                    action.army_id, army.position, army.movement_remaining
                )

    # Phase 3: Combat resolution
    board, combats = resolve_combat(board)

    # Phase 4: Capture resolution
    board, captures = resolve_captures(board, player, config)

    # Reset movement for all of opponent's armies (they go next)
    opponent = player.opponent()
    for army in board.armies_of(opponent):
        board = board.with_army_movement_reset(army.id, config.movement.points_per_turn)

    # Create turn result
    turn_result = TurnResult(
        turn_number=state.current_turn,
        player=player,
        actions=actions,
        spawns=spawns,
        combats=combats,
        captures=captures,
        new_settlements=tuple(new_settlements),
        board_before=board_before,
        board_after=board,
    )

    # Determine next state
    # In alternating turns, each "turn number" represents one player's turn
    # After 25 turns each (50 total actions), the game ends
    new_turn = state.current_turn
    if player == Player.PLAYER_2:
        new_turn += 1  # Increment turn after P2 goes

    is_complete = new_turn > config.num_turns

    if is_complete:
        winner = determine_winner(board)
        new_phase = GamePhase.COMPLETE
    else:
        winner = None
        new_phase = GamePhase.PLAYING

    return GameState(
        board=board,
        phase=new_phase,
        current_turn=new_turn if not is_complete else state.current_turn,
        active_player=opponent,
        turn_history=state.turn_history + (turn_result,),
        setup_complete=state.setup_complete,
        winner=winner,
    )


# =============================================================================
# Victory
# =============================================================================


def calculate_score(board: GameBoard, player: Player) -> int:
    """Calculate the number of friendly hexes for a player.

    Victory is determined by who controls more hexes.
    """
    return len(board.friendly_hexes(player))


def determine_winner(board: GameBoard) -> Player | None:
    """Determine the winner based on hex count.

    Returns None if tied.
    """
    p1_score = calculate_score(board, Player.PLAYER_1)
    p2_score = calculate_score(board, Player.PLAYER_2)

    if p1_score > p2_score:
        return Player.PLAYER_1
    elif p2_score > p1_score:
        return Player.PLAYER_2
    return None


# =============================================================================
# Visibility / Fog of War
# =============================================================================


def calculate_visibility(board: GameBoard, player: Player) -> frozenset[HexCoord]:
    """Calculate which hexes a player can see.

    Visibility rules:
    - Hexes adjacent to owned settlements
    - Hexes containing owned armies
    - From corners: all 3 adjacent hexes
    """
    visible: set[HexCoord] = set()

    # From settlements
    for settlement in board.settlements_of(player):
        visible.update(settlement.friendly_hexes(board.radius))

    # From armies
    for army in board.armies_of(player):
        if isinstance(army.position, HexCoord):
            visible.add(army.position)
            visible.update(army.position.valid_neighbors(board.radius))
        else:  # On corner
            visible.update(army.position.valid_adjacent_hexes(board.radius))

    return frozenset(visible)


def create_visible_state(state: GameState, player: Player) -> VisibleState:
    """Create fog-of-war filtered view for a player."""
    visible_hexes = calculate_visibility(state.board, player)

    # Calculate visible corners
    visible_corners: set[CornerCoord] = set()
    for hex_coord in visible_hexes:
        visible_corners.update(hex_coord.valid_corners(state.board.radius))

    return VisibleState(
        viewer=player,
        visible_hexes=visible_hexes,
        visible_corners=frozenset(visible_corners),
        board=state.board,
        phase=state.phase,
        current_turn=state.current_turn,
        active_player=state.active_player,
    )


# =============================================================================
# Utility Functions
# =============================================================================


def get_valid_moves(
    army: Army,
    board: GameBoard,
    config: GameConfig,
) -> list[MoveAction]:
    """Get all valid single-step move actions for an army.

    Only returns moves to ADJACENT positions (one step).
    """
    moves: list[MoveAction] = []

    # Get adjacent positions based on current position type
    adjacent: list[Position] = []
    if isinstance(army.position, HexCoord):
        adjacent.extend(army.position.valid_neighbors(board.radius))
        adjacent.extend(army.position.valid_corners(board.radius))
    else:  # CornerCoord
        adjacent.extend(army.position.valid_adjacent_hexes(board.radius))
        adjacent.extend(army.position.valid_adjacent_corners(board.radius))

    for pos in adjacent:
        cost = calculate_movement_cost(army.position, pos, army.owner, board, config)
        if cost is not None and cost <= army.movement_remaining:
            moves.append(MoveAction(army_id=army.id, to_position=pos))

    return moves


def get_adjacent_positions(
    position: Position,
    board: GameBoard,
) -> list[Position]:
    """Get all adjacent positions from a given position."""
    adjacent: list[Position] = []
    if isinstance(position, HexCoord):
        adjacent.extend(position.valid_neighbors(board.radius))
        adjacent.extend(position.valid_corners(board.radius))
    else:  # CornerCoord
        adjacent.extend(position.valid_adjacent_hexes(board.radius))
        adjacent.extend(position.valid_adjacent_corners(board.radius))
    return adjacent


def can_settle(
    army: Army,
    board: GameBoard,
    config: GameConfig,
    started_on_corner: bool,
) -> bool:
    """Check if an army can settle at its current position."""
    if not isinstance(army.position, CornerCoord):
        return False
    if not started_on_corner:
        return False
    if army.movement_remaining < config.movement.settle_cost:
        return False
    if board.settlement_at(army.position) is not None:
        return False
    return True
