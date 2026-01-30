"""Tests for core types module.

V3: Stone-count with split movement support.
"""

import pytest

from strategic_influence.types import (
    Owner,
    Position,
    Territory,
    TerritoryBoard,
    TerritoryAction,
    StoneMovement,
    PlayerTurnActions,
    create_empty_board,
    create_territory,
    create_neutral_territory,
    create_grow_action,
    create_simple_move_action,
    create_move_action,
)


class TestOwner:
    """Tests for Owner enum."""

    def test_opponent_of_player1(self):
        assert Owner.PLAYER_1.opponent() == Owner.PLAYER_2

    def test_opponent_of_player2(self):
        assert Owner.PLAYER_2.opponent() == Owner.PLAYER_1

    def test_opponent_of_neutral(self):
        assert Owner.NEUTRAL.opponent() == Owner.NEUTRAL

    def test_str_player1(self):
        assert str(Owner.PLAYER_1) == "White"

    def test_str_player2(self):
        assert str(Owner.PLAYER_2) == "Black"


class TestPosition:
    """Tests for Position dataclass."""

    def test_neighbors_center(self):
        """Center position has 4 neighbors."""
        pos = Position(2, 2)
        neighbors = pos.neighbors(5)
        expected = frozenset({
            Position(1, 2),  # Down
            Position(3, 2),  # Up
            Position(2, 1),  # Left
            Position(2, 3),  # Right
        })
        assert neighbors == expected

    def test_neighbors_corner(self):
        """Corner position has 2 neighbors."""
        pos = Position(0, 0)
        neighbors = pos.neighbors(5)
        expected = frozenset({
            Position(1, 0),  # Up
            Position(0, 1),  # Right
        })
        assert neighbors == expected

    def test_neighbors_edge(self):
        """Edge position (non-corner) has 3 neighbors."""
        pos = Position(0, 2)
        neighbors = pos.neighbors(5)
        expected = frozenset({
            Position(0, 1),  # Left
            Position(0, 3),  # Right
            Position(1, 2),  # Up
        })
        assert neighbors == expected

    def test_is_valid(self):
        """Test position validation."""
        assert Position(0, 0).is_valid(5) is True
        assert Position(4, 4).is_valid(5) is True
        assert Position(-1, 0).is_valid(5) is False
        assert Position(5, 0).is_valid(5) is False

    def test_is_in_setup_zone_p1(self):
        """Player 1 setup zone is cols 0-1 + bottom of middle col."""
        # Left two columns
        assert Position(0, 0).is_in_setup_zone(5, Owner.PLAYER_1) is True
        assert Position(2, 0).is_in_setup_zone(5, Owner.PLAYER_1) is True
        assert Position(0, 1).is_in_setup_zone(5, Owner.PLAYER_1) is True
        # Bottom of middle column (rows 0, 1)
        assert Position(0, 2).is_in_setup_zone(5, Owner.PLAYER_1) is True
        assert Position(1, 2).is_in_setup_zone(5, Owner.PLAYER_1) is True
        # Center and beyond excluded
        assert Position(2, 2).is_in_setup_zone(5, Owner.PLAYER_1) is False  # center
        assert Position(0, 3).is_in_setup_zone(5, Owner.PLAYER_1) is False

    def test_is_in_setup_zone_p2(self):
        """Player 2 setup zone is cols 3-4 + top of middle col."""
        # Right two columns
        assert Position(0, 4).is_in_setup_zone(5, Owner.PLAYER_2) is True
        assert Position(2, 4).is_in_setup_zone(5, Owner.PLAYER_2) is True
        assert Position(0, 3).is_in_setup_zone(5, Owner.PLAYER_2) is True
        # Top of middle column (rows 3, 4)
        assert Position(3, 2).is_in_setup_zone(5, Owner.PLAYER_2) is True
        assert Position(4, 2).is_in_setup_zone(5, Owner.PLAYER_2) is True
        # Center and beyond excluded
        assert Position(2, 2).is_in_setup_zone(5, Owner.PLAYER_2) is False  # center
        assert Position(0, 1).is_in_setup_zone(5, Owner.PLAYER_2) is False


class TestTerritory:
    """Tests for Territory dataclass."""

    def test_neutral_territory(self):
        """Neutral territory has 0 stones."""
        territory = create_neutral_territory()
        assert territory.owner == Owner.NEUTRAL
        assert territory.stones == 0

    def test_owned_territory(self):
        """Owned territory has at least 1 stone."""
        territory = create_territory(Owner.PLAYER_1, 3)
        assert territory.owner == Owner.PLAYER_1
        assert territory.stones == 3

    def test_negative_stones_raises(self):
        """Negative stones should raise error."""
        with pytest.raises(ValueError):
            Territory(owner=Owner.PLAYER_1, stones=-1)

    def test_owned_with_zero_stones_raises(self):
        """Owned territory with 0 stones should raise error."""
        with pytest.raises(ValueError):
            Territory(owner=Owner.PLAYER_1, stones=0)

    def test_neutral_with_stones_raises(self):
        """Neutral territory with stones should raise error."""
        with pytest.raises(ValueError):
            Territory(owner=Owner.NEUTRAL, stones=1)


class TestTerritoryBoard:
    """Tests for TerritoryBoard dataclass."""

    def test_empty_board_all_neutral(self):
        """Empty board has all neutral cells."""
        board = create_empty_board(5)
        for r in range(5):
            for c in range(5):
                territory = board.get(Position(r, c))
                assert territory.owner == Owner.NEUTRAL
                assert territory.stones == 0

    def test_with_stones_creates_new_board(self):
        """with_stones returns a new board, doesn't mutate."""
        board1 = create_empty_board(5)
        pos = Position(2, 2)

        board2 = board1.with_stones(pos, Owner.PLAYER_1, 3)

        assert board1.get_owner(pos) == Owner.NEUTRAL
        assert board2.get_owner(pos) == Owner.PLAYER_1
        assert board2.get_stones(pos) == 3

    def test_positions_owned_by(self):
        """Test getting positions owned by a player."""
        board = create_empty_board(5)
        board = board.with_stones(Position(0, 0), Owner.PLAYER_1, 1)
        board = board.with_stones(Position(1, 1), Owner.PLAYER_1, 2)
        board = board.with_stones(Position(2, 2), Owner.PLAYER_2, 1)

        p1_positions = board.positions_owned_by(Owner.PLAYER_1)
        assert p1_positions == frozenset({Position(0, 0), Position(1, 1)})

        p2_positions = board.positions_owned_by(Owner.PLAYER_2)
        assert p2_positions == frozenset({Position(2, 2)})

    def test_count_territories(self):
        """Test territory counting."""
        board = create_empty_board(5)
        board = board.with_stones(Position(0, 0), Owner.PLAYER_1, 1)
        board = board.with_stones(Position(1, 1), Owner.PLAYER_1, 2)
        board = board.with_stones(Position(2, 2), Owner.PLAYER_2, 1)

        counts = board.count_territories()
        assert counts[Owner.PLAYER_1] == 2
        assert counts[Owner.PLAYER_2] == 1
        assert counts[Owner.NEUTRAL] == 22  # 25 - 3

    def test_total_stones(self):
        """Test total stone counting."""
        board = create_empty_board(5)
        board = board.with_stones(Position(0, 0), Owner.PLAYER_1, 1)
        board = board.with_stones(Position(1, 1), Owner.PLAYER_1, 3)
        board = board.with_stones(Position(2, 2), Owner.PLAYER_2, 5)

        assert board.total_stones(Owner.PLAYER_1) == 4
        assert board.total_stones(Owner.PLAYER_2) == 5
        assert board.total_stones(Owner.NEUTRAL) == 0

    def test_all_positions(self):
        """Test getting all positions."""
        board = create_empty_board(3)
        positions = board.all_positions()
        assert len(positions) == 9
        assert Position(0, 0) in positions
        assert Position(2, 2) in positions


class TestTerritoryAction:
    """Tests for TerritoryAction with split movements."""

    def test_grow_action(self):
        """Grow action has no movements."""
        action = create_grow_action(Position(2, 2))
        assert action.is_grow is True
        assert action.is_move is False
        assert action.total_stones_moving == 0

    def test_simple_move_action(self):
        """Simple move has one movement."""
        action = create_simple_move_action(Position(2, 2), Position(2, 3), 3)
        assert action.is_grow is False
        assert action.is_move is True
        assert action.total_stones_moving == 3
        assert len(action.movements) == 1

    def test_split_move_action(self):
        """Split move has multiple movements."""
        movements = [
            (Position(2, 3), 2),
            (Position(3, 2), 1),
        ]
        action = create_move_action(Position(2, 2), movements)
        assert action.is_grow is False
        assert action.is_move is True
        assert action.total_stones_moving == 3
        assert len(action.movements) == 2


class TestPlayerTurnActions:
    """Tests for PlayerTurnActions."""

    def test_get_all_movements(self):
        """Test getting all movements from all actions."""
        action1 = create_grow_action(Position(0, 0))
        action2 = create_simple_move_action(Position(1, 1), Position(1, 2), 2)
        action3 = create_move_action(Position(2, 2), [
            (Position(2, 3), 1),
            (Position(3, 2), 1),
        ])

        actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(action1, action2, action3),
        )

        all_movements = actions.get_all_movements()
        assert len(all_movements) == 3  # 0 + 1 + 2 = 3

    def test_get_action_for(self):
        """Test getting action for specific position."""
        action1 = create_grow_action(Position(0, 0))
        action2 = create_simple_move_action(Position(1, 1), Position(1, 2), 2)

        actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(action1, action2),
        )

        assert actions.get_action_for(Position(0, 0)) == action1
        assert actions.get_action_for(Position(1, 1)) == action2
        assert actions.get_action_for(Position(2, 2)) is None
