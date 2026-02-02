"""Territory Rush agent for March of Empires - ultra-aggressive expansion."""

from __future__ import annotations

import random
from typing import Sequence

from ..types import (
    Player,
    HexCoord,
    CornerCoord,
    Position,
    Army,
    Settlement,
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


class TerritoryRushAgent:
    """Ultra-aggressive expansion agent.

    Strategy:
    1. ALWAYS settle when on a corner (even if it gains only 1 hex)
    2. Move directly to nearest unsettled corner
    3. Prioritize corners that maximize NEW hex gain
    4. Never waste movement - always end on a corner if possible
    """

    def __init__(self, seed: int | None = None):
        self._name = "TerritoryRush"
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
        """Choose most central corner in setup zone."""
        valid_zone = get_setup_zone(player, config.board_radius)
        center = HexCoord(0, 0)

        def corner_score(corner: CornerCoord) -> float:
            adjacent_hexes = corner.valid_adjacent_hexes(config.board_radius)
            # Maximize hexes covered AND centrality
            centrality = sum(
                1.0 / (1 + h.distance_to(center)) for h in adjacent_hexes
            )
            return len(adjacent_hexes) * 2 + centrality

        return max(valid_zone, key=corner_score)

    def choose_actions(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> TurnActions:
        """Choose actions with ultra-aggressive expansion."""
        actions: list[Action] = []
        board = state.board

        # Track which armies started on corners
        armies_on_corners: set[int] = set()
        for army in board.armies_of(player):
            if isinstance(army.position, CornerCoord):
                armies_on_corners.add(army.id)

        # Track corners being targeted this turn
        targeted_corners: set[CornerCoord] = set()

        # Process each army
        for army in board.armies_of(player):
            started_on_corner = army.id in armies_on_corners

            # ALWAYS settle when on a corner (even if just 1 new hex)
            if started_on_corner and can_settle(army, board, config, True):
                if isinstance(army.position, CornerCoord):
                    # Settle if it gains ANY new hexes
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

            # Move toward best corner
            best_corner = self._find_best_corner(
                army, board, player, config, targeted_corners
            )

            if best_corner:
                targeted_corners.add(best_corner)
                move_actions = self._rush_to_corner(
                    army, best_corner, board, player, config
                )
                actions.extend(move_actions)

                # Update board state
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

    def _find_best_corner(
        self,
        army: Army,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        excluded: set[CornerCoord],
    ) -> CornerCoord | None:
        """Find the best corner to rush toward.

        Prioritizes: (new hexes gained) / (distance + 1)
        This balances territory gain with time to settle.
        """
        my_hexes = board.friendly_hexes(player)
        enemy_hexes = board.friendly_hexes(player.opponent())
        best_corner = None
        best_score = float('-inf')

        for corner in board.all_corners():
            if board.settlement_at(corner) is not None:
                continue
            if corner in excluded:
                continue

            adjacent = corner.valid_adjacent_hexes(config.board_radius)
            new_hexes = len([h for h in adjacent if h not in my_hexes])
            contested = len([h for h in adjacent if h in enemy_hexes])

            if new_hexes < 1:
                continue

            dist = self._distance_to_corner(army.position, corner, config)

            # Score: value per turn to reach
            # new_hexes worth 3, contested worth 2 (we're taking from enemy)
            value = new_hexes * 3.0 + contested * 2.0
            # Divide by distance + 1 to prioritize closer corners
            score = value / (dist + 1)

            if score > best_score:
                best_score = score
                best_corner = corner

        return best_corner

    def _rush_to_corner(
        self,
        army: Army,
        target: CornerCoord,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> list[Action]:
        """Rush toward target corner, trying to end on a corner if possible."""
        actions: list[Action] = []
        current_army = army
        current_board = board

        while current_army.movement_remaining > 0:
            # Already at target
            if current_army.position == target:
                break

            adjacent = self._get_adjacent_positions(current_army.position, current_board)

            # Find best move
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

                # Prefer corners when distance is equal or close
                if dist < best_dist or (dist == best_dist and is_corner and not best_is_corner):
                    best_dist = dist
                    best_pos = pos
                    best_is_corner = is_corner
                    best_cost = cost

            if best_pos is None:
                break

            # Make the move
            actions.append(MoveAction(army_id=army.id, to_position=best_pos))
            current_board = current_board.with_army_moved(army.id, best_pos, best_cost)
            current_army = current_board.army_by_id(army.id)

            # Stop if we're on a corner (can settle next turn)
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
        """Get all adjacent positions from a given position."""
        adjacent: list[Position] = []
        if isinstance(position, HexCoord):
            adjacent.extend(position.valid_neighbors(board.radius))
            adjacent.extend(position.valid_corners(board.radius))
        else:  # CornerCoord
            adjacent.extend(position.valid_adjacent_hexes(board.radius))
            adjacent.extend(position.valid_adjacent_corners(board.radius))
        return adjacent

    def _distance_to_corner(
        self,
        pos: Position,
        target: CornerCoord,
        config: GameConfig,
    ) -> int:
        """Estimate distance from position to corner."""
        target_hexes = target.valid_adjacent_hexes(config.board_radius)

        if isinstance(pos, HexCoord):
            return min(pos.distance_to(h) for h in target_hexes) if target_hexes else 999
        else:
            if pos == target:
                return 0
            pos_hexes = pos.valid_adjacent_hexes(config.board_radius)
            shared = pos_hexes & target_hexes
            if shared:
                return 1
            return 2
