"""Greedy Settler agent for March of Empires - simple but effective expansion."""

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
    GameBoard,
    TurnActions,
    Action,
    MoveAction,
    SettleAction,
    PassAction,
)
from ..config import GameConfig
from ..engine import (
    get_setup_zone,
    can_settle,
    calculate_movement_cost,
)


class GreedySettlerAgent:
    """Simple greedy expansion agent.

    Strategy is dead simple:
    1. If on a corner with no settlement -> SETTLE
    2. Otherwise -> Move toward corner that gains most hexes per move
    3. Always try to end turn on a corner

    No combat logic, no defense - pure greedy expansion.
    """

    def __init__(self, seed: int | None = None):
        self._name = "GreedySettler"
        self._rng = random.Random(seed)

    @property
    def name(self) -> str:
        return self._name

    def reset(self) -> None:
        pass

    def choose_setup(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> CornerCoord:
        """Choose corner with max hex coverage."""
        valid_zone = get_setup_zone(player, config.board_radius)

        def corner_score(corner: CornerCoord) -> float:
            return len(corner.valid_adjacent_hexes(config.board_radius))

        return max(valid_zone, key=corner_score)

    def choose_actions(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> TurnActions:
        """Greedy expansion: settle or move to corner."""
        actions: list[Action] = []
        board = state.board

        # Track which armies started on corners
        armies_on_corners: set[int] = set()
        for army in board.armies_of(player):
            if isinstance(army.position, CornerCoord):
                armies_on_corners.add(army.id)

        # Assign each army to a different corner
        taken_corners: set[CornerCoord] = set()

        for army in board.armies_of(player):
            started_on_corner = army.id in armies_on_corners

            # Step 1: Settle if possible
            if started_on_corner and can_settle(army, board, config, True):
                if isinstance(army.position, CornerCoord):
                    my_hexes = board.friendly_hexes(player)
                    adjacent = army.position.valid_adjacent_hexes(config.board_radius)
                    new_hexes = len([h for h in adjacent if h not in my_hexes])
                    if new_hexes >= 1:
                        actions.append(SettleAction(army_id=army.id))
                        board = board.with_army_moved(
                            army.id, army.position, config.movement.settle_cost
                        )
                        board, _ = board.with_settlement(army.position, player)
                        continue

            # Step 2: Find best corner and move toward it
            best_corner = self._greedy_corner(army, board, player, config, taken_corners)

            if best_corner:
                taken_corners.add(best_corner)
                move_actions = self._move_to_corner(army, best_corner, board, player, config)
                actions.extend(move_actions)

                for action in move_actions:
                    if isinstance(action, MoveAction):
                        cost = calculate_movement_cost(
                            army.position, action.to_position, player, board, config
                        )
                        if cost:
                            board = board.with_army_moved(army.id, action.to_position, cost)
                            army = board.army_by_id(army.id)
            else:
                actions.append(PassAction(army_id=army.id))

        return TurnActions(player=player, actions=tuple(actions))

    def _greedy_corner(
        self,
        army: Army,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        excluded: set[CornerCoord],
    ) -> CornerCoord | None:
        """Find corner with best (new hexes) / distance ratio."""
        my_hexes = board.friendly_hexes(player)
        best_corner = None
        best_ratio = 0.0

        for corner in board.all_corners():
            if board.settlement_at(corner) is not None:
                continue
            if corner in excluded:
                continue

            adjacent = corner.valid_adjacent_hexes(config.board_radius)
            new_hexes = len([h for h in adjacent if h not in my_hexes])

            if new_hexes < 1:
                continue

            dist = self._distance_to_corner(army.position, corner, config)
            ratio = new_hexes / (dist + 0.5)  # +0.5 to avoid div by zero and favor close

            if ratio > best_ratio:
                best_ratio = ratio
                best_corner = corner

        return best_corner

    def _move_to_corner(
        self,
        army: Army,
        target: CornerCoord,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> list[Action]:
        """Move toward target, ending on a corner if possible."""
        actions: list[Action] = []
        current_army = army
        current_board = board

        while current_army.movement_remaining > 0:
            if current_army.position == target:
                break

            adjacent = self._get_adjacent_positions(current_army.position, current_board)

            # Find move that gets us closest to target
            best_pos = None
            best_dist = float('inf')
            best_is_corner = False
            best_cost = 0

            for pos in adjacent:
                cost = calculate_movement_cost(
                    current_army.position, pos, player, current_board, config
                )
                if cost is None or cost > current_army.movement_remaining:
                    continue

                dist = self._distance_to_corner(pos, target, config)
                is_corner = isinstance(pos, CornerCoord)

                # Prefer corners (same distance or closer)
                if dist < best_dist or (dist == best_dist and is_corner):
                    best_dist = dist
                    best_pos = pos
                    best_is_corner = is_corner
                    best_cost = cost

            if best_pos is None:
                break

            actions.append(MoveAction(army_id=army.id, to_position=best_pos))
            current_board = current_board.with_army_moved(army.id, best_pos, best_cost)
            current_army = current_board.army_by_id(army.id)

            # Stop on any corner (can settle next turn)
            if isinstance(best_pos, CornerCoord):
                break

        if not actions:
            actions.append(PassAction(army_id=army.id))

        return actions

    def _get_adjacent_positions(
        self,
        position: Position,
        board: GameBoard,
    ) -> list[Position]:
        """Get all adjacent positions."""
        adjacent: list[Position] = []
        if isinstance(position, HexCoord):
            adjacent.extend(position.valid_neighbors(board.radius))
            adjacent.extend(position.valid_corners(board.radius))
        else:
            adjacent.extend(position.valid_adjacent_hexes(board.radius))
            adjacent.extend(position.valid_adjacent_corners(board.radius))
        return adjacent

    def _distance_to_corner(
        self,
        pos: Position,
        target: CornerCoord,
        config: GameConfig,
    ) -> int:
        """Distance from position to corner."""
        target_hexes = target.valid_adjacent_hexes(config.board_radius)

        if isinstance(pos, HexCoord):
            return min(pos.distance_to(h) for h in target_hexes) if target_hexes else 999
        else:
            if pos == target:
                return 0
            pos_hexes = pos.valid_adjacent_hexes(config.board_radius)
            shared = pos_hexes & target_hexes
            return 1 if shared else 2
