"""Pytest configuration and shared fixtures for Strategic Influence tests.

V3: Stone-count with split movement support.
"""

import pytest
from random import Random

from strategic_influence.config import create_default_config, GameConfig
from strategic_influence.types import (
    TerritoryBoard,
    Owner,
    Position,
    Territory,
    PlayerTurnActions,
    TurnActions,
    TerritoryAction,
    StoneMovement,
    create_empty_board,
    create_initial_state,
    create_territory,
    create_neutral_territory,
    create_grow_action,
    create_simple_move_action,
    create_move_action,
)


@pytest.fixture
def default_config() -> GameConfig:
    """Provide default game configuration."""
    return create_default_config()


@pytest.fixture
def empty_board(default_config: GameConfig) -> TerritoryBoard:
    """Provide an empty 5x5 board."""
    return create_empty_board(default_config.board_size)


@pytest.fixture
def seeded_rng() -> Random:
    """Provide a seeded RNG for reproducible tests."""
    return Random(42)


@pytest.fixture
def center_position() -> Position:
    """The center position of a 5x5 board."""
    return Position(2, 2)


@pytest.fixture
def corner_position() -> Position:
    """A corner position (bottom-left)."""
    return Position(0, 0)


@pytest.fixture
def edge_position() -> Position:
    """An edge position (not corner)."""
    return Position(0, 2)


def create_test_board(
    size: int,
    territories: dict[tuple[int, int], tuple[Owner, int]],
) -> TerritoryBoard:
    """Helper to create a board with specific territories.

    Args:
        size: Board size.
        territories: Dict mapping (row, col) tuples to (owner, stones).

    Returns:
        TerritoryBoard with the specified territories.
    """
    board = create_empty_board(size)
    for (row, col), (owner, stones) in territories.items():
        pos = Position(row, col)
        if owner == Owner.NEUTRAL:
            territory = create_neutral_territory()
        else:
            territory = create_territory(owner, stones)
        board = board.with_territory(pos, territory)
    return board


def create_test_actions(
    player: Owner,
    actions: list[dict],
) -> PlayerTurnActions:
    """Helper to create player actions from a list of action dicts.

    Args:
        player: The player making the moves.
        actions: List of dicts with keys:
            - 'pos': (row, col) tuple
            - 'type': 'grow' or 'move'
            - 'dest': (row, col) tuple (for move)
            - 'count': int (for move, defaults to all stones)
            - 'splits': list of ((row,col), count) for split moves

    Returns:
        PlayerTurnActions with the specified actions.
    """
    territory_actions = []

    for action in actions:
        pos = Position(action['pos'][0], action['pos'][1])

        if action.get('type') == 'grow' or action.get('type') is None:
            territory_actions.append(create_grow_action(pos))
        elif 'splits' in action:
            # Split movement
            movements = [
                (Position(dest[0], dest[1]), count)
                for dest, count in action['splits']
            ]
            territory_actions.append(create_move_action(pos, movements))
        else:
            # Simple movement
            dest = Position(action['dest'][0], action['dest'][1])
            count = action.get('count', 1)
            territory_actions.append(create_simple_move_action(pos, dest, count))

    return PlayerTurnActions(player=player, actions=tuple(territory_actions))


def create_test_turn_actions(
    turn: int,
    p1_actions: list[dict],
    p2_actions: list[dict],
) -> TurnActions:
    """Helper to create TurnActions from action lists.

    Args:
        turn: Turn number.
        p1_actions: Player 1's actions (see create_test_actions).
        p2_actions: Player 2's actions (see create_test_actions).

    Returns:
        TurnActions for both players.
    """
    return TurnActions(
        player1_actions=create_test_actions(Owner.PLAYER_1, p1_actions),
        player2_actions=create_test_actions(Owner.PLAYER_2, p2_actions),
        turn_number=turn,
    )
