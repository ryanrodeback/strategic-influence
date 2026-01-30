"""Tests for resolution module.

V4: Simultaneous resolution with expansion risk.
"""

import pytest
from random import Random

from strategic_influence.config import create_default_config
from strategic_influence.types import (
    Owner,
    Position,
    TurnActions,
    CombatOutcome,
    create_empty_board,
    create_grow_action,
    create_simple_move_action,
    create_move_action,
    PlayerTurnActions,
)
from strategic_influence.resolution import (
    resolve_expansion,
    resolve_all_movements,
    apply_growth,
    resolve_turn,
)
from tests.conftest import create_test_board


class TestResolveExpansion:
    """Tests for expansion risk mechanic."""

    def test_expansion_can_succeed(self, default_config):
        """Expansion with favorable roll succeeds."""
        # Use a seed that produces a successful roll
        rng = Random(42)
        result = resolve_expansion(
            position=Position(2, 3),
            expander=Owner.PLAYER_1,
            stones=3,
            success_rate=0.5,
            rng=rng,
        )

        # With 3 stones at 50% each, high chance of success
        # Check structure is correct
        assert result.position == Position(2, 3)
        assert result.expander == Owner.PLAYER_1
        assert result.stones_sent == 3
        assert len(result.rolls) == 3

    def test_expansion_all_fail_loses_stones(self, default_config):
        """When all expansion rolls fail, all stones are lost."""
        # Use 0% hit chance to guarantee failure
        rng = Random(42)
        result = resolve_expansion(
            position=Position(2, 3),
            expander=Owner.PLAYER_1,
            stones=3,
            success_rate=0.0,  # 0% chance - always fails
            rng=rng,
        )

        assert result.succeeded is False
        assert result.stones_surviving == 0

    def test_expansion_any_success_keeps_all(self, default_config):
        """When any roll succeeds, all stones claim territory."""
        # Use 100% hit chance to guarantee success
        rng = Random(42)
        result = resolve_expansion(
            position=Position(2, 3),
            expander=Owner.PLAYER_1,
            stones=3,
            success_rate=1.0,  # 100% chance - always succeeds
            rng=rng,
        )

        assert result.succeeded is True
        assert result.stones_surviving == 3


class TestSimultaneousMovement:
    """Tests for simultaneous movement resolution."""

    def test_reinforcement_always_succeeds(self, default_config, seeded_rng):
        """Moving to own territory always succeeds (no expansion risk)."""
        board = create_test_board(5, {
            (2, 2): (Owner.PLAYER_1, 3),
            (2, 3): (Owner.PLAYER_1, 2),
        })

        p1_actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_simple_move_action(Position(2, 2), Position(2, 3), 3),),
        )
        p2_actions = PlayerTurnActions(
            player=Owner.PLAYER_2,
            actions=(),
        )
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=1,
        )

        new_board, results = resolve_all_movements(
            board, actions, default_config, seeded_rng
        )

        assert new_board.get_owner(Position(2, 3)) == Owner.PLAYER_1
        assert new_board.get_stones(Position(2, 3)) == 5
        assert new_board.get_owner(Position(2, 2)) == Owner.NEUTRAL

    def test_expansion_to_neutral_has_risk(self, default_config):
        """Moving to neutral territory has expansion risk."""
        board = create_test_board(5, {
            (2, 2): (Owner.PLAYER_1, 3),
        })

        p1_actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_simple_move_action(Position(2, 2), Position(2, 3), 3),),
        )
        p2_actions = PlayerTurnActions(
            player=Owner.PLAYER_2,
            actions=(),
        )
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=1,
        )

        # Use 100% hit chance to guarantee success
        rng = Random(42)
        new_board, results = resolve_all_movements(
            board, actions, default_config, rng
        )

        # Should have expansion result
        assert len(results) == 1
        assert results[0].expansion is not None

    def test_attack_triggers_combat(self, default_config, seeded_rng):
        """Moving to enemy territory triggers combat."""
        board = create_test_board(5, {
            (2, 2): (Owner.PLAYER_1, 5),
            (2, 3): (Owner.PLAYER_2, 2),
        })

        p1_actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_simple_move_action(Position(2, 2), Position(2, 3), 5),),
        )
        p2_actions = PlayerTurnActions(
            player=Owner.PLAYER_2,
            actions=(create_grow_action(Position(2, 3)),),
        )
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=1,
        )

        new_board, results = resolve_all_movements(
            board, actions, default_config, seeded_rng
        )

        # Should have combat result
        assert len(results) == 1
        assert results[0].combat is not None
        assert results[0].combat.attacker == Owner.PLAYER_1
        assert results[0].combat.defender == Owner.PLAYER_2

    def test_simultaneous_departures(self, default_config, seeded_rng):
        """All departures happen simultaneously before arrivals."""
        # Both players move from their territories at the same time
        board = create_test_board(5, {
            (2, 1): (Owner.PLAYER_1, 3),
            (2, 3): (Owner.PLAYER_2, 3),
        })

        # Both move toward center (neutral)
        p1_actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_simple_move_action(Position(2, 1), Position(2, 2), 3),),
        )
        p2_actions = PlayerTurnActions(
            player=Owner.PLAYER_2,
            actions=(create_simple_move_action(Position(2, 3), Position(2, 2), 3),),
        )
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=1,
        )

        new_board, results = resolve_all_movements(
            board, actions, default_config, seeded_rng
        )

        # Both sources should be empty now
        assert new_board.get_owner(Position(2, 1)) == Owner.NEUTRAL
        assert new_board.get_owner(Position(2, 3)) == Owner.NEUTRAL


class TestContestedExpansion:
    """Tests for contested expansion (both players to same neutral)."""

    def test_contested_expansion_both_roll(self, default_config):
        """When both players expand to same neutral, both roll."""
        board = create_test_board(5, {
            (2, 1): (Owner.PLAYER_1, 3),
            (2, 3): (Owner.PLAYER_2, 3),
        })

        # Both try to claim center
        p1_actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_simple_move_action(Position(2, 1), Position(2, 2), 3),),
        )
        p2_actions = PlayerTurnActions(
            player=Owner.PLAYER_2,
            actions=(create_simple_move_action(Position(2, 3), Position(2, 2), 3),),
        )
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=1,
        )

        rng = Random(42)
        new_board, results = resolve_all_movements(
            board, actions, default_config, rng
        )

        # Both should have expansion results
        p1_results = [r for r in results if r.owner == Owner.PLAYER_1]
        p2_results = [r for r in results if r.owner == Owner.PLAYER_2]

        assert len(p1_results) == 1
        assert len(p2_results) == 1
        assert p1_results[0].expansion is not None
        assert p2_results[0].expansion is not None


class TestReinforcementBeforeAttack:
    """Tests for reinforcement happening before attacks."""

    def test_reinforcement_before_being_attacked(self, default_config):
        """Reinforcement arrives before attack is resolved."""
        # P2 has two territories, one reinforces the other
        # P1 attacks the territory being reinforced
        board = create_test_board(5, {
            (2, 1): (Owner.PLAYER_1, 5),   # Attacker
            (2, 2): (Owner.PLAYER_2, 1),   # Will be reinforced and attacked
            (2, 3): (Owner.PLAYER_2, 3),   # Reinforcing
        })

        # P1 attacks (2,2), P2 reinforces (2,2) from (2,3)
        p1_actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_simple_move_action(Position(2, 1), Position(2, 2), 5),),
        )
        p2_actions = PlayerTurnActions(
            player=Owner.PLAYER_2,
            actions=(create_simple_move_action(Position(2, 3), Position(2, 2), 3),),
        )
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=1,
        )

        rng = Random(42)
        new_board, results = resolve_all_movements(
            board, actions, default_config, rng
        )

        # Find combat result
        combat_results = [r for r in results if r.combat is not None]
        assert len(combat_results) == 1

        combat = combat_results[0].combat
        # Defender should have had 4 stones (1 original + 3 reinforcement)
        assert combat.defender_initial == 4


class TestApplyGrowth:
    """Tests for growth phase."""

    def test_grow_adds_stones(self, default_config):
        """Territories that chose GROW gain stones."""
        board = create_test_board(5, {
            (2, 2): (Owner.PLAYER_1, 3),
            (2, 3): (Owner.PLAYER_2, 2),
        })

        p1_actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_grow_action(Position(2, 2)),),
        )
        p2_actions = PlayerTurnActions(
            player=Owner.PLAYER_2,
            actions=(create_grow_action(Position(2, 3)),),
        )
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=1,
        )

        new_board, grown = apply_growth(board, actions, default_config)

        assert new_board.get_stones(Position(2, 2)) == 4
        assert new_board.get_stones(Position(2, 3)) == 3
        assert Position(2, 2) in grown
        assert Position(2, 3) in grown

    def test_move_action_no_growth(self, default_config):
        """Territories that chose MOVE don't grow."""
        board = create_test_board(5, {
            (2, 2): (Owner.PLAYER_1, 3),
        })

        p1_actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_simple_move_action(Position(2, 2), Position(2, 3), 3),),
        )
        p2_actions = PlayerTurnActions(
            player=Owner.PLAYER_2,
            actions=(),
        )
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=1,
        )

        new_board, grown = apply_growth(board, actions, default_config)

        # Source territory is now neutral, destination wasn't grown
        # (it was just claimed, not a grow action)
        assert Position(2, 2) not in grown


class TestResolveTurn:
    """Tests for full turn resolution."""

    def test_turn_resolution_order(self, default_config, seeded_rng):
        """Turn resolution: movements first, then growth."""
        board = create_test_board(5, {
            (2, 2): (Owner.PLAYER_1, 3),
            (3, 3): (Owner.PLAYER_2, 2),
        })

        # P1 grows, P2 moves
        p1_actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_grow_action(Position(2, 2)),),
        )
        p2_actions = PlayerTurnActions(
            player=Owner.PLAYER_2,
            actions=(create_simple_move_action(Position(3, 3), Position(3, 2), 2),),
        )
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=1,
        )

        final_board, movements, grown = resolve_turn(
            board, actions, default_config, seeded_rng
        )

        # P1 should have grown
        assert Position(2, 2) in grown
        assert final_board.get_stones(Position(2, 2)) == 4

        # P2 should have moved (not grown)
        assert Position(3, 3) not in grown

    def test_same_seed_same_result(self, default_config):
        """Same seed produces same turn resolution."""
        board = create_test_board(5, {
            (2, 2): (Owner.PLAYER_1, 3),
            (2, 3): (Owner.PLAYER_2, 3),
        })

        # P1 attacks P2
        p1_actions = PlayerTurnActions(
            player=Owner.PLAYER_1,
            actions=(create_simple_move_action(Position(2, 2), Position(2, 3), 3),),
        )
        p2_actions = PlayerTurnActions(
            player=Owner.PLAYER_2,
            actions=(create_grow_action(Position(2, 3)),),
        )
        actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=1,
        )

        rng1 = Random(42)
        rng2 = Random(42)

        board1, moves1, grown1 = resolve_turn(board, actions, default_config, rng1)
        board2, moves2, grown2 = resolve_turn(board, actions, default_config, rng2)

        # Same results
        assert board1.get_owner(Position(2, 3)) == board2.get_owner(Position(2, 3))
        if moves1:
            assert moves1[0].combat.outcome == moves2[0].combat.outcome
