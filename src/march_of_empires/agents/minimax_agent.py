"""Minimax agent with alpha-beta pruning for March of Empires."""

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
    calculate_score,
)


class MinimaxAgent:
    """Minimax agent with alpha-beta pruning.

    Uses depth-limited minimax search with position evaluation
    based on territory control and settlement count.
    """

    def __init__(
        self,
        seed: int | None = None,
        max_depth: int = 3,
    ):
        self._name = "Minimax"
        self._rng = random.Random(seed)
        self._max_depth = max_depth

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
        """Choose setup using evaluation."""
        valid_zone = get_setup_zone(player, config.board_radius)
        center = HexCoord(0, 0)

        def corner_score(corner: CornerCoord) -> float:
            adjacent_hexes = corner.valid_adjacent_hexes(config.board_radius)
            hex_score = len(adjacent_hexes) * 3.0
            centrality = sum(
                1.0 / (1 + h.distance_to(center)) for h in adjacent_hexes
            )
            return hex_score + centrality * 2.0

        best = max(valid_zone, key=corner_score)
        return best

    def choose_actions(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> TurnActions:
        """Use minimax to choose actions."""
        board = state.board

        # Track which armies started on corners
        armies_on_corners: set[int] = set()
        for army in board.armies_of(player):
            if isinstance(army.position, CornerCoord):
                armies_on_corners.add(army.id)

        # Run minimax search
        best_actions = self._minimax_search(
            board, player, config, armies_on_corners
        )

        return TurnActions(player=player, actions=tuple(best_actions))

    def _minimax_search(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        armies_on_corners: set[int],
    ) -> list[Action]:
        """Run minimax search with alpha-beta pruning."""
        best_action = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        # Generate and order actions (settling first for better pruning)
        actions = self._generate_ordered_actions(board, player, config, armies_on_corners)

        for action in actions:
            new_board = self._apply_action(board, player, action, config)

            # Minimax with opponent's perspective
            value = self._minimax(
                new_board,
                player.opponent(),
                player,
                config,
                self._max_depth - 1,
                alpha,
                beta,
                False,
            )

            if value > best_value:
                best_value = value
                best_action = action

            alpha = max(alpha, value)

        if best_action:
            return [best_action]

        # Fallback: settle or move toward best corner
        return self._expansion_actions(board, player, config, armies_on_corners)

    def _minimax(
        self,
        board: GameBoard,
        current_player: Player,
        max_player: Player,
        config: GameConfig,
        depth: int,
        alpha: float,
        beta: float,
        is_max: bool,
    ) -> float:
        """Minimax with alpha-beta pruning."""
        # Terminal condition
        if depth == 0:
            return self._evaluate(board, max_player, config)

        actions = self._generate_actions(board, current_player, config)

        if not actions:
            return self._evaluate(board, max_player, config)

        if is_max:
            max_value = float('-inf')
            for action in actions:
                new_board = self._apply_action(board, current_player, action, config)
                value = self._minimax(
                    new_board,
                    current_player.opponent(),
                    max_player,
                    config,
                    depth - 1,
                    alpha,
                    beta,
                    False,
                )
                max_value = max(max_value, value)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # Prune
            return max_value
        else:
            min_value = float('inf')
            for action in actions:
                new_board = self._apply_action(board, current_player, action, config)
                value = self._minimax(
                    new_board,
                    current_player.opponent(),
                    max_player,
                    config,
                    depth - 1,
                    alpha,
                    beta,
                    True,
                )
                min_value = min(min_value, value)
                beta = min(beta, value)
                if beta <= alpha:
                    break  # Prune
            return min_value

    def _evaluate(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> float:
        """Evaluate board position from player's perspective.

        Heavily weighted toward territory control (hex count).
        """
        my_hexes = len(board.friendly_hexes(player))
        enemy_hexes = len(board.friendly_hexes(player.opponent()))

        my_settlements = len(list(board.settlements_of(player)))
        enemy_settlements = len(list(board.settlements_of(player.opponent())))

        my_armies = len(list(board.armies_of(player)))
        enemy_armies = len(list(board.armies_of(player.opponent())))

        # Territory is most important (direct victory condition)
        hex_score = (my_hexes - enemy_hexes) * 10.0

        # Settlements are crucial (they control hexes and spawn armies)
        settlement_score = (my_settlements - enemy_settlements) * 8.0

        # Armies are useful but less important than territory
        army_score = (my_armies - enemy_armies) * 1.0

        return hex_score + settlement_score + army_score

    def _generate_ordered_actions(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        armies_on_corners: set[int],
    ) -> list[Action]:
        """Generate actions ordered for better pruning (settle first)."""
        settle_actions: list[Action] = []
        move_to_corner_actions: list[Action] = []
        other_actions: list[Action] = []

        for army in board.armies_of(player):
            started_on_corner = army.id in armies_on_corners

            # Settle actions (highest priority)
            if started_on_corner and can_settle(army, board, config, True):
                if isinstance(army.position, CornerCoord):
                    my_hexes = board.friendly_hexes(player)
                    adjacent = army.position.valid_adjacent_hexes(config.board_radius)
                    new_hexes = len([h for h in adjacent if h not in my_hexes])
                    if new_hexes >= 1:
                        settle_actions.append(SettleAction(army_id=army.id))
                        continue

            # Move actions
            adjacent = self._get_adjacent_positions(army.position, board)
            for pos in adjacent:
                cost = calculate_movement_cost(army.position, pos, player, board, config)
                if cost is not None and cost <= army.movement_remaining:
                    action = MoveAction(army_id=army.id, to_position=pos)
                    # Prioritize moves to corners
                    if isinstance(pos, CornerCoord) and board.settlement_at(pos) is None:
                        move_to_corner_actions.append(action)
                    else:
                        other_actions.append(action)

            other_actions.append(PassAction(army_id=army.id))

        # Order: settle > move to corner > other moves
        return settle_actions + move_to_corner_actions + other_actions[:10]  # Limit branching

    def _generate_actions(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> list[Action]:
        """Generate a limited set of actions for minimax - fast version."""
        actions: list[Action] = []
        armies = list(board.armies_of(player))

        # Process only first 2 armies to limit branching
        for army in armies[:2]:
            # Can settle? (highest priority)
            if isinstance(army.position, CornerCoord):
                if can_settle(army, board, config, True):
                    my_hexes = board.friendly_hexes(player)
                    adjacent = army.position.valid_adjacent_hexes(config.board_radius)
                    new_hexes = len([h for h in adjacent if h not in my_hexes])
                    if new_hexes >= 1:
                        actions.append(SettleAction(army_id=army.id))
                        continue

            # Move to corners (limited for performance)
            adjacent = self._get_adjacent_positions(army.position, board)
            corner_moves = []
            for pos in adjacent:
                cost = calculate_movement_cost(army.position, pos, player, board, config)
                if cost is not None and cost <= army.movement_remaining:
                    if isinstance(pos, CornerCoord) and board.settlement_at(pos) is None:
                        corner_moves.append(MoveAction(army_id=army.id, to_position=pos))

            if corner_moves:
                actions.extend(corner_moves[:3])  # Limit branching
            else:
                # Add a few other moves
                for pos in adjacent[:3]:
                    cost = calculate_movement_cost(army.position, pos, player, board, config)
                    if cost is not None and cost <= army.movement_remaining:
                        actions.append(MoveAction(army_id=army.id, to_position=pos))

            if not any(isinstance(a, (SettleAction, MoveAction)) and
                      (not isinstance(a, MoveAction) or a.army_id == army.id)
                      for a in actions[-5:]):
                actions.append(PassAction(army_id=army.id))

        return actions if actions else [PassAction(army_id=-1)]

    def _apply_action(
        self,
        board: GameBoard,
        player: Player,
        action: Action,
        config: GameConfig,
    ) -> GameBoard:
        """Apply a single action to board."""
        if isinstance(action, PassAction):
            return board

        army = board.army_by_id(action.army_id)
        if army is None:
            return board

        if isinstance(action, MoveAction):
            cost = calculate_movement_cost(
                army.position, action.to_position, player, board, config
            )
            if cost and cost <= army.movement_remaining:
                return board.with_army_moved(action.army_id, action.to_position, cost)
        elif isinstance(action, SettleAction):
            if isinstance(army.position, CornerCoord):
                new_board = board.with_army_moved(
                    action.army_id, army.position, config.movement.settle_cost
                )
                new_board, _ = new_board.with_settlement(army.position, player)
                return new_board

        return board

    def _expansion_actions(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        armies_on_corners: set[int],
    ) -> list[Action]:
        """Fallback expansion-focused actions."""
        actions: list[Action] = []

        for army in board.armies_of(player):
            started_on_corner = army.id in armies_on_corners

            # Try settling first
            if started_on_corner and can_settle(army, board, config, True):
                if isinstance(army.position, CornerCoord):
                    my_hexes = board.friendly_hexes(player)
                    adjacent = army.position.valid_adjacent_hexes(config.board_radius)
                    new_hexes = len([h for h in adjacent if h not in my_hexes])
                    if new_hexes >= 1:
                        actions.append(SettleAction(army_id=army.id))
                        continue

            # Move toward nearest unsettled corner
            best_corner = self._find_nearest_unsettled_corner(army, board, player, config)
            if best_corner:
                move = self._move_toward(army, best_corner, board, player, config)
                if move:
                    actions.append(move)
                    continue

            actions.append(PassAction(army_id=army.id))

        return actions

    def _find_nearest_unsettled_corner(
        self,
        army: Army,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> CornerCoord | None:
        """Find the nearest unsettled corner that would gain territory."""
        my_hexes = board.friendly_hexes(player)
        best_corner = None
        best_score = float('-inf')

        for corner in board.all_corners():
            if board.settlement_at(corner) is not None:
                continue

            adjacent = corner.valid_adjacent_hexes(config.board_radius)
            new_hexes = len([h for h in adjacent if h not in my_hexes])
            if new_hexes < 1:
                continue

            dist = self._distance_to_corner(army.position, corner, config)
            score = new_hexes * 3.0 - dist * 2.0

            if score > best_score:
                best_score = score
                best_corner = corner

        return best_corner

    def _move_toward(
        self,
        army: Army,
        target: CornerCoord,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> Action | None:
        """Generate move toward target."""
        adjacent = self._get_adjacent_positions(army.position, board)

        best_pos = None
        best_dist = self._distance_to_corner(army.position, target, config)

        for pos in adjacent:
            cost = calculate_movement_cost(army.position, pos, player, board, config)
            if cost is None or cost > army.movement_remaining:
                continue

            dist = self._distance_to_corner(pos, target, config)
            # Prefer corners when distance is equal
            is_corner = isinstance(pos, CornerCoord)
            if dist < best_dist or (dist == best_dist and is_corner):
                best_dist = dist
                best_pos = pos

        if best_pos:
            return MoveAction(army_id=army.id, to_position=best_pos)
        return None

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
