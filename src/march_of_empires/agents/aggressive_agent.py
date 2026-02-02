"""Aggressive agent for March of Empires - focuses on attacking."""

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
    get_reachable_positions,
    can_settle,
    calculate_movement_cost,
)


class AggressiveAgent:
    """Aggressive agent that prioritizes attacking enemy settlements.

    Strategy:
    1. Coordinate armies to capture enemy settlements
    2. Move armies toward enemy territory
    3. Only settle when safe and advantageous
    4. Trade armies favorably (more settlements = faster respawn)
    """

    def __init__(self, seed: int | None = None):
        self._name = "Aggressive"
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
        """Choose corner toward the center/enemy side for aggression."""
        valid_zone = get_setup_zone(player, config.board_radius)
        center = HexCoord(0, 0)

        def corner_score(corner: CornerCoord) -> float:
            adjacent_hexes = corner.valid_adjacent_hexes(config.board_radius)
            # Prioritize corners close to center (and thus enemy)
            centrality = sum(
                1.0 / (1 + h.distance_to(center)) for h in adjacent_hexes
            )
            return centrality

        best = max(valid_zone, key=corner_score)
        return best

    def choose_actions(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> TurnActions:
        """Choose actions prioritizing attack."""
        actions: list[Action] = []
        board = state.board

        # Track which armies started on corners
        armies_on_corners: set[int] = set()
        for army in board.armies_of(player):
            if isinstance(army.position, CornerCoord):
                armies_on_corners.add(army.id)

        # Find attack targets
        attack_targets = self._find_attack_targets(board, player, config)

        # Assign armies to targets
        armies = list(board.armies_of(player))
        army_assignments: dict[int, CornerCoord | None] = {}

        for target, priority in attack_targets:
            # Find armies that can reach this target
            reachable_armies = []
            for army in armies:
                if army.id in army_assignments:
                    continue
                dist = self._distance_to_corner(army.position, target, config)
                if dist <= 4:  # Within reasonable range
                    reachable_armies.append((army, dist))

            reachable_armies.sort(key=lambda x: x[1])

            # Assign closest armies
            settlement = board.settlement_at(target)
            needed = config.capture.defended_armies_required if self._is_defended(board, target) else config.capture.undefended_armies_required

            for army, dist in reachable_armies[:needed + 1]:  # +1 for buffer
                army_assignments[army.id] = target

        # Process each army
        for army in armies:
            started_on_corner = army.id in armies_on_corners
            target = army_assignments.get(army.id)

            if target:
                army_actions = self._attack_target(
                    army, target, board, player, config, started_on_corner
                )
            else:
                army_actions = self._default_actions(
                    army, board, player, config, started_on_corner
                )

            actions.extend(army_actions)

            # Update board state
            for action in army_actions:
                if isinstance(action, MoveAction):
                    cost = calculate_movement_cost(
                        army.position, action.to_position, player, board, config
                    )
                    if cost:
                        board = board.with_army_moved(action.army_id, action.to_position, cost)
                        army = board.army_by_id(action.army_id)
                elif isinstance(action, SettleAction):
                    board = board.with_army_moved(
                        action.army_id, army.position, config.movement.settle_cost
                    )
                    board, _ = board.with_settlement(army.position, player)

        return TurnActions(player=player, actions=tuple(actions))

    def _find_attack_targets(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> list[tuple[CornerCoord, float]]:
        """Find enemy settlements to attack, ranked by priority."""
        enemy = player.opponent()
        targets: list[tuple[CornerCoord, float]] = []

        for settlement in board.settlements_of(enemy):
            corner = settlement.position

            # Count nearby friendly armies
            nearby_armies = 0
            for army in board.armies_of(player):
                dist = self._distance_to_corner(army.position, corner, config)
                if dist <= 3:
                    nearby_armies += 1

            # Check if defended
            is_defended = self._is_defended(board, corner)
            needed = config.capture.defended_armies_required if is_defended else config.capture.undefended_armies_required

            # Priority: higher if we have enough armies, lower if defended
            priority = nearby_armies - needed
            if not is_defended:
                priority += 2  # Bonus for undefended

            # Centrality bonus
            center = HexCoord(0, 0)
            adjacent_hexes = corner.valid_adjacent_hexes(config.board_radius)
            avg_dist = sum(h.distance_to(center) for h in adjacent_hexes) / max(len(adjacent_hexes), 1)
            priority += (config.board_radius - avg_dist) * 0.3

            targets.append((corner, priority))

        targets.sort(key=lambda x: x[1], reverse=True)
        return targets

    def _is_defended(self, board: GameBoard, corner: CornerCoord) -> bool:
        """Check if a settlement is defended."""
        settlement = board.settlement_at(corner)
        if not settlement:
            return False
        armies = board.armies_at(corner)
        return any(a.owner == settlement.owner for a in armies)

    def _attack_target(
        self,
        army: Army,
        target: CornerCoord,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        started_on_corner: bool,
    ) -> list[Action]:
        """Move army toward attack target using step-by-step adjacent moves."""
        actions: list[Action] = []
        current_army = army
        current_board = board

        while current_army.movement_remaining > 0:
            # If at target, stop
            if current_army.position == target:
                break

            # Get only ADJACENT positions (single step)
            adjacent = self._get_adjacent_positions(current_army.position, current_board)

            # Find adjacent position closest to target
            best_pos = None
            best_dist = float('inf')

            for pos in adjacent:
                cost = calculate_movement_cost(
                    current_army.position, pos, player, current_board, config
                )
                if cost is None or cost > current_army.movement_remaining:
                    continue

                dist = self._distance_to_corner(pos, target, config)

                if dist < best_dist:
                    best_dist = dist
                    best_pos = pos

            if best_pos is None:
                break

            # Check if making progress
            current_dist = self._distance_to_corner(current_army.position, target, config)
            if best_dist >= current_dist and best_pos != target:
                break

            cost = calculate_movement_cost(
                current_army.position, best_pos, player, current_board, config
            )
            if cost is None or cost > current_army.movement_remaining:
                break

            actions.append(MoveAction(army_id=army.id, to_position=best_pos))
            current_board = current_board.with_army_moved(army.id, best_pos, cost)
            current_army = current_board.army_by_id(army.id)

        if not actions:
            actions.append(PassAction(army_id=army.id))

        return actions

    def _default_actions(
        self,
        army: Army,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        started_on_corner: bool,
    ) -> list[Action]:
        """Default behavior when no attack target assigned."""
        # If on good corner and can settle, do it
        if started_on_corner and can_settle(army, board, config, True):
            if isinstance(army.position, CornerCoord):
                # Check if worth settling
                my_hexes = board.friendly_hexes(player)
                adjacent = army.position.valid_adjacent_hexes(config.board_radius)
                new_hexes = len([h for h in adjacent if h not in my_hexes])
                if new_hexes >= 2:
                    return [SettleAction(army_id=army.id)]

        # Move toward enemy territory
        enemy = player.opponent()
        enemy_settlements = list(board.settlements_of(enemy))

        if enemy_settlements:
            # Move toward closest enemy settlement
            closest = min(
                enemy_settlements,
                key=lambda s: self._distance_to_corner(army.position, s.position, config)
            )
            return self._attack_target(
                army, closest.position, board, player, config, started_on_corner
            )

        return [PassAction(army_id=army.id)]

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
