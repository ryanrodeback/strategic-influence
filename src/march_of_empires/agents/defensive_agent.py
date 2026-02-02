"""Defensive agent for March of Empires - focuses on protection."""

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


class DefensiveAgent:
    """Defensive agent that prioritizes protecting settlements.

    Strategy:
    1. Keep armies near settlements for defense
    2. Intercept threats before they reach settlements
    3. Expand cautiously only when safe
    4. Maintain garrison at each settlement
    """

    def __init__(self, seed: int | None = None):
        self._name = "Defensive"
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
        """Choose a defensible corner away from center."""
        valid_zone = get_setup_zone(player, config.board_radius)

        def corner_score(corner: CornerCoord) -> float:
            # Prefer corners with good hex coverage but not too central
            adjacent_hexes = corner.valid_adjacent_hexes(config.board_radius)
            hex_count = len(adjacent_hexes)

            # Slight preference for being away from center (safer)
            center = HexCoord(0, 0)
            centrality = sum(h.distance_to(center) for h in adjacent_hexes) / max(hex_count, 1)

            return hex_count * 2 + centrality * 0.5

        best = max(valid_zone, key=corner_score)
        return best

    def choose_actions(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> TurnActions:
        """Choose actions prioritizing defense."""
        actions: list[Action] = []
        board = state.board

        # Track which armies started on corners
        armies_on_corners: set[int] = set()
        for army in board.armies_of(player):
            if isinstance(army.position, CornerCoord):
                armies_on_corners.add(army.id)

        # Assess threats to each settlement
        threats = self._assess_threats(board, player, config)

        # Assign defenders
        armies = list(board.armies_of(player))
        army_assignments: dict[int, CornerCoord | None] = {}

        # First, assign armies to threatened settlements
        for settlement_corner, threat_level in threats:
            if threat_level <= 0:
                continue

            # Count current defenders
            current_defenders = sum(
                1 for a in board.armies_at(settlement_corner)
                if a.owner == player
            )

            # Find nearby armies to assign as defenders
            needed = max(0, threat_level - current_defenders + 1)
            available_armies = [
                (a, self._distance_to_corner(a.position, settlement_corner, config))
                for a in armies
                if a.id not in army_assignments
            ]
            available_armies.sort(key=lambda x: x[1])

            for army, dist in available_armies[:needed]:
                army_assignments[army.id] = settlement_corner

        # Process each army
        for army in armies:
            started_on_corner = army.id in armies_on_corners
            defense_target = army_assignments.get(army.id)

            if defense_target:
                army_actions = self._defend_settlement(
                    army, defense_target, board, player, config
                )
            else:
                army_actions = self._safe_expansion(
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

    def _assess_threats(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> list[tuple[CornerCoord, int]]:
        """Assess threat level to each settlement.

        Returns list of (corner, threat_level) sorted by threat.
        Threat level = enemy armies nearby - our defenders.
        """
        enemy = player.opponent()
        threats: list[tuple[CornerCoord, int]] = []

        for settlement in board.settlements_of(player):
            corner = settlement.position

            # Count enemy armies within range
            enemy_threat = 0
            for army in board.armies_of(enemy):
                dist = self._distance_to_corner(army.position, corner, config)
                if dist == 0:
                    enemy_threat += 3  # On the settlement
                elif dist == 1:
                    enemy_threat += 2  # Adjacent
                elif dist <= 3:
                    enemy_threat += 1  # Nearby

            # Count our defenders
            defenders = sum(
                1 for a in board.armies_at(corner) if a.owner == player
            )

            threat_level = enemy_threat - defenders
            threats.append((corner, threat_level))

        threats.sort(key=lambda x: x[1], reverse=True)
        return threats

    def _defend_settlement(
        self,
        army: Army,
        target: CornerCoord,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> list[Action]:
        """Move army to defend a settlement using step-by-step adjacent moves."""
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

    def _safe_expansion(
        self,
        army: Army,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        started_on_corner: bool,
    ) -> list[Action]:
        """Expand only when safe (no nearby enemies)."""
        enemy = player.opponent()

        # Check if any enemies are near this army
        for enemy_army in board.armies_of(enemy):
            dist = self._army_distance(army, enemy_army, config)
            if dist <= 3:
                # Too dangerous to expand, stay defensive
                # Move back toward nearest friendly settlement
                nearest_settlement = self._find_nearest_settlement(
                    army, board, player, config
                )
                if nearest_settlement:
                    return self._defend_settlement(
                        army, nearest_settlement.position, board, player, config
                    )
                return [PassAction(army_id=army.id)]

        # Safe to expand - settle if on good corner
        if started_on_corner and can_settle(army, board, config, True):
            if isinstance(army.position, CornerCoord):
                my_hexes = board.friendly_hexes(player)
                adjacent = army.position.valid_adjacent_hexes(config.board_radius)
                new_hexes = len([h for h in adjacent if h not in my_hexes])
                if new_hexes >= 1:
                    return [SettleAction(army_id=army.id)]

        # Find safe expansion target
        safe_corners = self._find_safe_corners(board, player, config)
        if safe_corners:
            target = safe_corners[0]
            return self._move_toward_corner(army, target, board, player, config)

        return [PassAction(army_id=army.id)]

    def _find_safe_corners(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> list[CornerCoord]:
        """Find corners that are safe to settle (far from enemies)."""
        enemy = player.opponent()
        my_hexes = board.friendly_hexes(player)
        safe_corners: list[tuple[CornerCoord, float]] = []

        for corner in board.all_corners():
            if board.settlement_at(corner) is not None:
                continue

            # Check distance to nearest enemy
            min_enemy_dist = float('inf')
            for enemy_army in board.armies_of(enemy):
                dist = self._distance_to_corner(enemy_army.position, corner, config)
                min_enemy_dist = min(min_enemy_dist, dist)

            if min_enemy_dist < 4:
                continue  # Too close to enemy

            # Score by new hexes gained
            adjacent = corner.valid_adjacent_hexes(config.board_radius)
            new_hexes = len([h for h in adjacent if h not in my_hexes])

            if new_hexes > 0:
                safe_corners.append((corner, new_hexes + min_enemy_dist * 0.1))

        safe_corners.sort(key=lambda x: x[1], reverse=True)
        return [c for c, _ in safe_corners]

    def _find_nearest_settlement(
        self,
        army: Army,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> Settlement | None:
        """Find the nearest friendly settlement."""
        settlements = list(board.settlements_of(player))
        if not settlements:
            return None

        return min(
            settlements,
            key=lambda s: self._distance_to_corner(army.position, s.position, config)
        )

    def _move_toward_corner(
        self,
        army: Army,
        target: CornerCoord,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> list[Action]:
        """Move army toward a corner using step-by-step adjacent moves."""
        actions: list[Action] = []
        current_army = army
        current_board = board

        while current_army.movement_remaining > 0:
            if current_army.position == target:
                break

            # Get only ADJACENT positions (single step)
            adjacent = self._get_adjacent_positions(current_army.position, current_board)

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

    def _army_distance(
        self,
        army1: Army,
        army2: Army,
        config: GameConfig,
    ) -> int:
        """Distance between two armies."""
        if isinstance(army1.position, HexCoord) and isinstance(army2.position, HexCoord):
            return army1.position.distance_to(army2.position)
        elif isinstance(army1.position, HexCoord) and isinstance(army2.position, CornerCoord):
            return self._distance_to_corner(army1.position, army2.position, config)
        elif isinstance(army1.position, CornerCoord) and isinstance(army2.position, HexCoord):
            return self._distance_to_corner(army2.position, army1.position, config)
        else:
            # Both corners
            if army1.position == army2.position:
                return 0
            shared = army1.position.valid_adjacent_hexes(config.board_radius) & army2.position.valid_adjacent_hexes(config.board_radius)
            return 1 if shared else 2
