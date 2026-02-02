"""Expansion-focused agent for March of Empires."""

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


class ExpansionAgent:
    """Expansion-focused agent.

    Prioritizes founding new settlements to maximize territory.
    Strategy:
    1. Settle whenever possible on corners that maximize new hex coverage
    2. Move armies toward good settlement sites
    3. Spread settlements to avoid overlap
    """

    def __init__(self, seed: int | None = None):
        self._name = "Expansion"
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
        """Choose corner closest to center for maximum expansion potential."""
        valid_zone = get_setup_zone(player, config.board_radius)
        center = HexCoord(0, 0)

        def corner_score(corner: CornerCoord) -> float:
            # Score based on centrality and expansion potential
            adjacent_hexes = corner.valid_adjacent_hexes(config.board_radius)
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
        """Choose actions prioritizing expansion."""
        actions: list[Action] = []
        board = state.board

        # Track which armies started on corners
        armies_on_corners: set[int] = set()
        for army in board.armies_of(player):
            if isinstance(army.position, CornerCoord):
                armies_on_corners.add(army.id)

        # Process each army
        armies = list(board.armies_of(player))
        settled_corners: set[CornerCoord] = set()

        for army in armies:
            started_on_corner = army.id in armies_on_corners
            army_actions = self._choose_army_actions(
                army, board, player, config, started_on_corner,
                settled_corners
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
                    if isinstance(army.position, CornerCoord):
                        settled_corners.add(army.position)

        return TurnActions(player=player, actions=tuple(actions))

    def _rank_settlement_sites(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        army_position: Position | None = None,
    ) -> list[tuple[CornerCoord, float]]:
        """Rank potential settlement sites by value.

        If army_position is provided, factor in distance (prefer closer sites).
        """
        my_hexes = board.friendly_hexes(player)
        enemy_hexes = board.friendly_hexes(player.opponent())
        all_corners = board.all_corners()

        sites: list[tuple[CornerCoord, float]] = []

        for corner in all_corners:
            if board.settlement_at(corner) is not None:
                continue

            # Calculate value: new hexes claimed
            adjacent_hexes = corner.valid_adjacent_hexes(config.board_radius)
            new_hexes = len([h for h in adjacent_hexes if h not in my_hexes])
            contested_hexes = len([h for h in adjacent_hexes if h in enemy_hexes])

            # Score: prioritize new hexes, bonus for contesting enemy
            score = new_hexes * 3.0 + contested_hexes * 1.0

            # Centrality bonus
            center = HexCoord(0, 0)
            avg_dist = sum(h.distance_to(center) for h in adjacent_hexes) / max(len(adjacent_hexes), 1)
            score += (config.board_radius - avg_dist) * 0.5

            # Distance penalty: prefer closer sites
            if army_position is not None:
                dist = self._distance_to_corner(army_position, corner, config)
                # Heavily penalize far sites - we want to settle soon
                score -= dist * 2.0

            sites.append((corner, score))

        sites.sort(key=lambda x: x[1], reverse=True)
        return sites

    def _choose_army_actions(
        self,
        army: Army,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        started_on_corner: bool,
        settled_this_turn: set[CornerCoord],
    ) -> list[Action]:
        """Choose actions for a single army."""
        actions: list[Action] = []
        current_army = army
        current_board = board

        # If on a good corner and can settle, do it
        if started_on_corner and can_settle(current_army, current_board, config, True):
            if isinstance(current_army.position, CornerCoord):
                corner = current_army.position
                # Check if this corner has good value
                my_hexes = current_board.friendly_hexes(player)
                adjacent = corner.valid_adjacent_hexes(config.board_radius)
                new_hexes = len([h for h in adjacent if h not in my_hexes])
                if new_hexes >= 1:  # Worth settling if we gain at least 1 hex
                    actions.append(SettleAction(army_id=army.id))
                    return actions

        # Get settlement sites ranked by distance from this army
        settlement_sites = self._rank_settlement_sites(
            current_board, player, config, current_army.position
        )

        # Otherwise, move toward best settlement site
        best_target = self._find_best_target(
            current_army, current_board, player, config,
            settlement_sites, settled_this_turn
        )

        if best_target:
            move_actions = self._move_toward(
                current_army, best_target, current_board, player, config
            )
            actions.extend(move_actions)

        if not actions:
            actions.append(PassAction(army_id=army.id))

        return actions

    def _find_best_target(
        self,
        army: Army,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        settlement_sites: list[tuple[CornerCoord, float]],
        settled_this_turn: set[CornerCoord],
    ) -> CornerCoord | None:
        """Find the best corner to move toward."""
        for corner, score in settlement_sites:
            if corner in settled_this_turn:
                continue
            if board.settlement_at(corner) is not None:
                continue
            return corner
        return None

    def _move_toward(
        self,
        army: Army,
        target: CornerCoord,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> list[Action]:
        """Generate move actions to approach target.

        IMPORTANT: Try to end on a corner so we can settle next turn.
        """
        actions: list[Action] = []
        current_army = army
        current_board = board

        while current_army.movement_remaining > 0:
            # Get ADJACENT positions only (not all reachable)
            adjacent: list[Position] = []
            if isinstance(current_army.position, HexCoord):
                adjacent.extend(current_army.position.valid_neighbors(config.board_radius))
                adjacent.extend(current_army.position.valid_corners(config.board_radius))
            else:
                adjacent.extend(current_army.position.valid_adjacent_hexes(config.board_radius))
                adjacent.extend(current_army.position.valid_adjacent_corners(config.board_radius))

            # Find best adjacent position (closest to target)
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

                # Calculate distance to target
                if isinstance(pos, HexCoord):
                    target_hexes = [h for h in target.adjacent_hexes() if h.is_valid(config.board_radius)]
                    dist = min(pos.distance_to(h) for h in target_hexes) if target_hexes else 999
                    is_corner = False
                else:
                    if pos == target:
                        dist = 0
                    else:
                        # Check if this corner shares hexes with target
                        shared = pos.valid_adjacent_hexes(config.board_radius) & target.adjacent_hexes()
                        if shared:
                            dist = 1
                        else:
                            pos_hexes = pos.valid_adjacent_hexes(config.board_radius)
                            target_hexes = [h for h in target.adjacent_hexes() if h.is_valid(config.board_radius)]
                            dist = min(
                                ph.distance_to(th) + 1
                                for ph in pos_hexes
                                for th in target_hexes
                            ) if pos_hexes and target_hexes else 999
                    is_corner = True

                # Prefer corners when distance is equal
                if dist < best_dist or (dist == best_dist and is_corner and not best_is_corner):
                    best_dist = dist
                    best_pos = pos
                    best_is_corner = is_corner
                    best_cost = cost

            if best_pos is None:
                break

            # Check if this move makes progress
            current_dist = self._distance_to_corner(current_army.position, target, config)
            if best_dist >= current_dist and best_pos != target:
                # No progress toward target, but try to end on a corner
                if isinstance(current_army.position, CornerCoord):
                    # Already on corner, stop here
                    break
                else:
                    # On hex, try to move to any valid settlement corner
                    found_corner = False
                    for pos in adjacent:
                        if isinstance(pos, CornerCoord):
                            cost = calculate_movement_cost(
                                current_army.position, pos, player, current_board, config
                            )
                            if cost and cost <= current_army.movement_remaining:
                                if current_board.settlement_at(pos) is None:
                                    best_pos = pos
                                    best_cost = cost
                                    found_corner = True
                                    break
                    if not found_corner:
                        break

            # Make the move
            actions.append(MoveAction(army_id=army.id, to_position=best_pos))
            current_board = current_board.with_army_moved(army.id, best_pos, best_cost)
            current_army = current_board.army_by_id(army.id)

            # Stop if we reached the target
            if best_pos == target:
                break
            # If we're on a corner and it's a valid settlement site, stop here
            if isinstance(best_pos, CornerCoord) and current_board.settlement_at(best_pos) is None:
                break

        return actions

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
            # Corner to corner via adjacent hexes
            pos_hexes = pos.valid_adjacent_hexes(config.board_radius)
            shared = pos_hexes & target_hexes
            if shared:
                return 1
            return 2
