"""Random agent for March of Empires - baseline agent."""

from __future__ import annotations

import random
from typing import Sequence

from ..types import (
    Player,
    HexCoord,
    CornerCoord,
    Position,
    Army,
    GameState,
    TurnActions,
    Action,
    MoveAction,
    SettleAction,
    PassAction,
)
from ..config import GameConfig
from ..engine import (
    get_setup_zone,
    get_reachable_positions,
    can_settle,
)


class RandomAgent:
    """Random baseline agent.

    Makes random valid moves. Useful as a baseline for measuring
    other agents' performance.
    """

    def __init__(self, seed: int | None = None):
        self._name = "Random"
        self._rng = random.Random(seed)

    @property
    def name(self) -> str:
        return self._name

    def reset(self) -> None:
        pass  # No state to reset

    def choose_setup(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> CornerCoord:
        """Choose a random valid corner for initial settlement."""
        valid_zone = get_setup_zone(player, config.board_radius)
        return self._rng.choice(list(valid_zone))

    def choose_actions(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> TurnActions:
        """Choose random actions for each army."""
        actions: list[Action] = []
        board = state.board

        # Track which armies started on corners
        armies_on_corners: set[int] = set()
        for army in board.armies_of(player):
            if isinstance(army.position, CornerCoord):
                armies_on_corners.add(army.id)

        # Process each army
        for army in board.armies_of(player):
            army_actions = self._choose_army_actions(
                army, board, player, config, army.id in armies_on_corners
            )
            actions.extend(army_actions)

            # Update board state for subsequent armies
            for action in army_actions:
                if isinstance(action, MoveAction):
                    cost = self._get_move_cost(army, action.to_position, board, player, config)
                    board = board.with_army_moved(action.army_id, action.to_position, cost)
                    army = board.army_by_id(action.army_id)
                elif isinstance(action, SettleAction):
                    board = board.with_army_moved(
                        action.army_id, army.position, config.movement.settle_cost
                    )
                    board, _ = board.with_settlement(army.position, player)

        return TurnActions(player=player, actions=tuple(actions))

    def _choose_army_actions(
        self,
        army: Army,
        board,
        player: Player,
        config: GameConfig,
        started_on_corner: bool,
    ) -> list[Action]:
        """Choose actions for a single army."""
        actions: list[Action] = []
        current_army = army
        current_board = board

        # Decide: settle, move, or pass
        choices = ["move", "pass"]

        # Can only settle if started on corner and corner is empty
        if started_on_corner and can_settle(current_army, current_board, config, True):
            choices.append("settle")

        choice = self._rng.choice(choices)

        if choice == "settle":
            actions.append(SettleAction(army_id=army.id))
        elif choice == "move":
            # Make random moves until out of movement
            while current_army.movement_remaining > 0:
                reachable = get_reachable_positions(current_army, current_board, config)
                # Filter to adjacent positions we can actually reach
                valid_moves = [
                    pos for pos, mp in reachable.items()
                    if pos != current_army.position and mp < current_army.movement_remaining
                ]

                if not valid_moves:
                    break

                target = self._rng.choice(valid_moves)
                cost = self._get_move_cost(current_army, target, current_board, player, config)

                if cost is None or cost > current_army.movement_remaining:
                    break

                actions.append(MoveAction(army_id=army.id, to_position=target))
                current_board = current_board.with_army_moved(army.id, target, cost)
                current_army = current_board.army_by_id(army.id)

                # Random chance to stop moving
                if self._rng.random() < 0.3:
                    break
        else:
            actions.append(PassAction(army_id=army.id))

        return actions

    def _get_move_cost(
        self,
        army: Army,
        target: Position,
        board,
        player: Player,
        config: GameConfig,
    ) -> int | None:
        """Calculate movement cost."""
        from ..engine import calculate_movement_cost
        return calculate_movement_cost(army.position, target, player, board, config)
