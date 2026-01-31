"""Common utilities shared across agent implementations."""

from random import Random

from ..types import Owner, Position, GameState, SetupAction
from ..config import GameConfig


def find_valid_setup_positions(
    state: GameState,
    player: Owner,
    config: GameConfig,
) -> list[Position]:
    """Find all valid setup positions for a player.

    Args:
        state: Current game state
        player: Player looking for setup positions
        config: Game configuration

    Returns:
        List of valid setup positions (unoccupied, in player's zone)
    """
    board_size = config.board_size
    return [
        Position(r, c)
        for r in range(board_size)
        for c in range(board_size)
        if Position(r, c).is_in_setup_zone(board_size, player)
        and state.board.get_owner(Position(r, c)) == Owner.NEUTRAL
    ]


def random_setup(
    state: GameState,
    player: Owner,
    config: GameConfig,
    rng: Random,
) -> SetupAction:
    """Choose setup position randomly.

    Args:
        state: Current game state
        player: Player choosing setup
        config: Game configuration
        rng: Random number generator

    Returns:
        Random setup action
    """
    valid_positions = find_valid_setup_positions(state, player, config)
    if not valid_positions:
        raise ValueError(f"No valid setup positions for {player}")
    chosen = rng.choice(valid_positions)
    return SetupAction(player=player, position=chosen)


def center_distance(pos: Position, board_size: int) -> float:
    """Calculate Manhattan distance from board center.

    Args:
        pos: Position to evaluate
        board_size: Size of board

    Returns:
        Distance from center
    """
    mid = board_size // 2
    return abs(pos.row - mid) + abs(pos.col - mid)


def center_aware_setup(
    state: GameState,
    player: Owner,
    config: GameConfig,
) -> SetupAction:
    """Choose setup position closest to center.

    Args:
        state: Current game state
        player: Player choosing setup
        config: Game configuration

    Returns:
        Setup action for center-closest position
    """
    valid_positions = find_valid_setup_positions(state, player, config)
    if not valid_positions:
        raise ValueError(f"No valid setup positions for {player}")

    valid_positions.sort(key=lambda p: center_distance(p, config.board_size))
    return SetupAction(player=player, position=valid_positions[0])
