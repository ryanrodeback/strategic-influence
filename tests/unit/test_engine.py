"""Tests for game engine module.

V3: Stone-count with split movement support.
"""

import pytest
from random import Random

from strategic_influence.config import create_default_config
from strategic_influence.types import (
    Owner,
    Position,
    GamePhase,
    PlayerTurnActions,
    TurnActions,
    SetupAction,
    create_empty_board,
    create_grow_action,
    create_simple_move_action,
)
from strategic_influence.engine import (
    create_game,
    apply_setup,
    apply_turn,
    validate_setup_action,
    validate_turn_actions,
    determine_winner,
    simulate_game,
)
from strategic_influence.agents import RandomAgent
from tests.conftest import create_test_board


class TestCreateGame:
    """Tests for game creation."""

    def test_creates_empty_board(self, default_config):
        """New game has empty board in setup phase."""
        state = create_game(default_config)

        assert state.current_turn == 0
        assert state.phase == GamePhase.SETUP
        assert state.is_complete is False
        assert state.winner is None
        assert len(state.turn_history) == 0

        # All cells neutral
        for pos in state.board.all_positions():
            assert state.board.get_owner(pos) == Owner.NEUTRAL


class TestValidateSetupAction:
    """Tests for setup action validation."""

    def test_valid_p1_setup(self, default_config):
        """Valid P1 setup action in left column."""
        state = create_game(default_config)
        action = SetupAction(player=Owner.PLAYER_1, position=Position(2, 0))

        is_valid, error = validate_setup_action(action, state, default_config)

        assert is_valid is True
        assert error is None

    def test_invalid_position_wrong_column(self, default_config):
        """Setup in wrong column fails."""
        state = create_game(default_config)
        # P1 must place in column 0, not column 2
        action = SetupAction(player=Owner.PLAYER_1, position=Position(2, 2))

        is_valid, error = validate_setup_action(action, state, default_config)

        assert is_valid is False
        assert "setup zone" in error.lower()


class TestApplySetup:
    """Tests for setup phase."""

    def test_apply_p1_setup(self, default_config):
        """P1 setup places stone correctly."""
        state = create_game(default_config)
        action = SetupAction(player=Owner.PLAYER_1, position=Position(2, 0))

        new_state = apply_setup(state, action, default_config)

        assert new_state.board.get_owner(Position(2, 0)) == Owner.PLAYER_1
        # Default config now places 3 stones
        assert new_state.board.get_stones(Position(2, 0)) == default_config.game.setup.stones_per_placement
        assert Owner.PLAYER_1 in new_state.setup_complete
        assert new_state.phase == GamePhase.SETUP  # P2 still needs to place

    def test_both_players_complete_setup(self, default_config):
        """After both players setup, phase changes to PLAYING."""
        state = create_game(default_config)

        # P1 setup
        state = apply_setup(state, SetupAction(Owner.PLAYER_1, Position(2, 0)), default_config)
        assert state.phase == GamePhase.SETUP

        # P2 setup
        state = apply_setup(state, SetupAction(Owner.PLAYER_2, Position(2, 4)), default_config)
        assert state.phase == GamePhase.PLAYING


class TestValidateTurnActions:
    """Tests for turn action validation."""

    def test_valid_grow_action(self, default_config):
        """Valid grow action passes."""
        board = create_test_board(5, {(2, 2): (Owner.PLAYER_1, 3)})
        state = create_game(default_config)
        state = state.__class__(
            board=board,
            phase=GamePhase.PLAYING,
            current_turn=1,
            turn_history=(),
            setup_complete=(Owner.PLAYER_1, Owner.PLAYER_2),
            winner=None,
        )

        actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_grow_action(Position(2, 2)),),
        )

        is_valid, error = validate_turn_actions(actions, state, default_config)
        assert is_valid is True

    def test_valid_move_action(self, default_config):
        """Valid move action passes."""
        board = create_test_board(5, {(2, 2): (Owner.PLAYER_1, 3)})
        state = create_game(default_config)
        state = state.__class__(
            board=board,
            phase=GamePhase.PLAYING,
            current_turn=1,
            turn_history=(),
            setup_complete=(Owner.PLAYER_1, Owner.PLAYER_2),
            winner=None,
        )

        actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_simple_move_action(Position(2, 2), Position(2, 3), 3),),
        )

        is_valid, error = validate_turn_actions(actions, state, default_config)
        assert is_valid is True

    def test_missing_action_fails(self, default_config):
        """Missing action for owned territory fails."""
        board = create_test_board(5, {
            (2, 2): (Owner.PLAYER_1, 3),
            (2, 3): (Owner.PLAYER_1, 2),
        })
        state = create_game(default_config)
        state = state.__class__(
            board=board,
            phase=GamePhase.PLAYING,
            current_turn=1,
            turn_history=(),
            setup_complete=(Owner.PLAYER_1, Owner.PLAYER_2),
            winner=None,
        )

        # Only provide action for one territory
        actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_grow_action(Position(2, 2)),),
        )

        is_valid, error = validate_turn_actions(actions, state, default_config)
        assert is_valid is False
        assert "missing" in error.lower()


class TestApplyTurn:
    """Tests for applying turns."""

    def test_game_completes_after_n_turns(self, default_config):
        """Game completes after num_turns."""
        agent1 = RandomAgent(seed=42)
        agent2 = RandomAgent(seed=43)

        state = create_game(default_config)
        state = apply_setup(state, agent1.choose_setup(state, Owner.PLAYER_1, default_config), default_config)
        state = apply_setup(state, agent2.choose_setup(state, Owner.PLAYER_2, default_config), default_config)

        rng = Random(42)
        for turn in range(default_config.num_turns):
            p1_actions = agent1.choose_actions(state, Owner.PLAYER_1, default_config)
            p2_actions = agent2.choose_actions(state, Owner.PLAYER_2, default_config)
            actions = TurnActions(
                player1_actions=p1_actions,
                player2_actions=p2_actions,
                turn_number=state.current_turn + 1,
            )
            state = apply_turn(state, actions, default_config, rng)

        assert state.is_complete is True
        assert state.current_turn == default_config.num_turns

    def test_cannot_apply_to_complete_game(self, default_config):
        """Cannot apply turn to completed game."""
        agent1 = RandomAgent(seed=42)
        agent2 = RandomAgent(seed=43)

        state = simulate_game(default_config, agent1, agent2, seed=42)

        # Try to apply another turn
        p1_actions = PlayerTurnActions(player=Owner.PLAYER_1, actions=())
        p2_actions = PlayerTurnActions(player=Owner.PLAYER_2, actions=())
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=state.current_turn + 1,
        )

        with pytest.raises(ValueError, match="PLAYING"):
            apply_turn(state, actions, default_config, Random(42))


class TestDetermineWinner:
    """Tests for winner determination."""

    def test_p1_wins_with_more_territory(self):
        """Player 1 wins with more territory."""
        board = create_test_board(5, {
            (0, 0): (Owner.PLAYER_1, 1),
            (0, 1): (Owner.PLAYER_1, 1),
            (0, 2): (Owner.PLAYER_2, 1),
        })

        winner = determine_winner(board)
        assert winner == Owner.PLAYER_1

    def test_p2_wins_with_more_territory(self):
        """Player 2 wins with more territory."""
        board = create_test_board(5, {
            (0, 0): (Owner.PLAYER_1, 1),
            (0, 1): (Owner.PLAYER_2, 1),
            (0, 2): (Owner.PLAYER_2, 1),
        })

        winner = determine_winner(board)
        assert winner == Owner.PLAYER_2

    def test_draw_with_equal_territory(self):
        """Draw when territories are equal."""
        board = create_test_board(5, {
            (0, 0): (Owner.PLAYER_1, 1),
            (0, 1): (Owner.PLAYER_2, 1),
        })

        winner = determine_winner(board)
        assert winner is None


class TestSimulateGame:
    """Tests for full game simulation."""

    def test_simulate_game_completes(self, default_config):
        """simulate_game runs a full game."""
        agent1 = RandomAgent(seed=42)
        agent2 = RandomAgent(seed=43)

        final_state = simulate_game(default_config, agent1, agent2, seed=42)

        assert final_state.is_complete is True
        assert final_state.current_turn == default_config.num_turns

    def test_same_seed_same_result(self, default_config):
        """Same seed produces same game result."""
        agent1 = RandomAgent(seed=42)
        agent2 = RandomAgent(seed=43)

        state1 = simulate_game(default_config, agent1, agent2, seed=100)

        agent1.reset()
        agent2.reset()

        state2 = simulate_game(default_config, agent1, agent2, seed=100)

        assert state1.winner == state2.winner
        counts1 = state1.board.count_territories()
        counts2 = state2.board.count_territories()
        assert counts1 == counts2
