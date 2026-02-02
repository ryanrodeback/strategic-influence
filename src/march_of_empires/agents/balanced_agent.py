"""Balanced heuristic agent for March of Empires."""

from __future__ import annotations

import random
from dataclasses import dataclass
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
    calculate_score,
)


@dataclass(frozen=True)
class EvaluationWeights:
    """Weights for position evaluation."""

    hex_control: float = 10.0
    settlement_value: float = 5.0
    central_bonus: float = 1.5
    army_advantage: float = 2.0
    army_positioning: float = 0.8
    concentration: float = 1.0
    vulnerability: float = 4.0
    expansion_opportunity: float = 1.5
    attack_opportunity: float = 3.0


# Phase-specific weights
EARLY_WEIGHTS = EvaluationWeights(
    hex_control=5.0,
    settlement_value=8.0,
    central_bonus=3.0,
    army_advantage=1.0,
    army_positioning=0.5,
    concentration=0.5,
    vulnerability=2.0,
    expansion_opportunity=5.0,
    attack_opportunity=1.0,
)

MID_WEIGHTS = EvaluationWeights(
    hex_control=8.0,
    settlement_value=5.0,
    central_bonus=2.0,
    army_advantage=3.0,
    army_positioning=1.5,
    concentration=1.5,
    vulnerability=3.0,
    expansion_opportunity=3.0,
    attack_opportunity=4.0,
)

LATE_WEIGHTS = EvaluationWeights(
    hex_control=15.0,
    settlement_value=3.0,
    central_bonus=1.0,
    army_advantage=2.0,
    army_positioning=2.0,
    concentration=2.0,
    vulnerability=5.0,
    expansion_opportunity=1.0,
    attack_opportunity=5.0,
)


class BalancedHeuristicAgent:
    """Balanced agent using multi-factor position evaluation.

    Uses weighted evaluation of:
    - Hex control (victory condition)
    - Settlement count and quality
    - Army advantage and positioning
    - Defensive vulnerability
    - Expansion and attack opportunities

    Weights adapt based on game phase (early/mid/late).
    """

    def __init__(self, seed: int | None = None):
        self._name = "Balanced"
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
        """Choose corner with best overall evaluation."""
        valid_zone = get_setup_zone(player, config.board_radius)
        center = HexCoord(0, 0)

        def corner_score(corner: CornerCoord) -> float:
            adjacent_hexes = corner.valid_adjacent_hexes(config.board_radius)

            # Hex coverage
            hex_score = len(adjacent_hexes) * 3.0

            # Centrality
            centrality = sum(
                1.0 / (1 + h.distance_to(center)) for h in adjacent_hexes
            )

            # Expansion potential
            expansion = len(adjacent_hexes) * 0.5

            return hex_score + centrality * 2.0 + expansion

        best = max(valid_zone, key=corner_score)
        return best

    def choose_actions(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> TurnActions:
        """Choose actions using position evaluation."""
        board = state.board

        # Determine game phase
        progress = state.current_turn / config.num_turns
        if progress < 0.33:
            weights = EARLY_WEIGHTS
        elif progress < 0.67:
            weights = MID_WEIGHTS
        else:
            weights = LATE_WEIGHTS

        # Track which armies started on corners
        armies_on_corners: set[int] = set()
        for army in board.armies_of(player):
            if isinstance(army.position, CornerCoord):
                armies_on_corners.add(army.id)

        # Generate candidate action sequences and evaluate
        best_actions: list[Action] = []
        best_score = float('-inf')

        # Try multiple action sequences
        for _ in range(20):  # Sample 20 random sequences
            candidate_actions = self._generate_action_sequence(
                board, player, config, armies_on_corners
            )
            simulated_board = self._simulate_actions(
                board, player, candidate_actions, config
            )
            score = self._evaluate_position(
                simulated_board, player, config, weights
            )
            score += self._rng.random() * 0.01  # Tiebreaker

            if score > best_score:
                best_score = score
                best_actions = candidate_actions

        # Also try a greedy approach
        greedy_actions = self._greedy_actions(
            board, player, config, armies_on_corners, weights
        )
        greedy_board = self._simulate_actions(board, player, greedy_actions, config)
        greedy_score = self._evaluate_position(greedy_board, player, config, weights)

        if greedy_score > best_score:
            best_actions = greedy_actions

        return TurnActions(player=player, actions=tuple(best_actions))

    def _evaluate_position(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        weights: EvaluationWeights,
    ) -> float:
        """Evaluate board position for player."""
        score = 0.0
        opponent = player.opponent()
        center = HexCoord(0, 0)

        # 1. Hex control (victory condition)
        my_hexes = len(board.friendly_hexes(player))
        enemy_hexes = len(board.friendly_hexes(opponent))
        score += (my_hexes - enemy_hexes) * weights.hex_control

        # 2. Settlement value
        for settlement in board.settlements_of(player):
            adjacent = settlement.position.valid_adjacent_hexes(config.board_radius)
            my_friendly = board.friendly_hexes(player)
            unique_hexes = len([h for h in adjacent if h not in (my_friendly - set(adjacent))])
            score += unique_hexes * weights.settlement_value

            # Central bonus
            avg_dist = sum(h.distance_to(center) for h in adjacent) / max(len(adjacent), 1)
            score += (config.board_radius - avg_dist) * weights.central_bonus

        # 3. Army advantage
        my_armies = board.army_count(player)
        enemy_armies = board.army_count(opponent)
        score += (my_armies - enemy_armies) * weights.army_advantage

        # 4. Army positioning (pressure on enemy)
        for army in board.armies_of(player):
            for enemy_settlement in board.settlements_of(opponent):
                dist = self._distance_to_corner(army.position, enemy_settlement.position, config)
                if dist <= 4:
                    score += (5 - dist) * weights.army_positioning

        # 5. Concentration (mutual support)
        for army in board.armies_of(player):
            nearby_friends = sum(
                1 for a in board.armies_of(player)
                if a.id != army.id and self._army_distance(army, a, config) <= 2
            )
            score += nearby_friends * weights.concentration

        # 6. Vulnerability
        for settlement in board.settlements_of(player):
            defenders = sum(
                1 for a in board.armies_at(settlement.position)
                if a.owner == player
            )
            nearby_enemies = sum(
                1 for a in board.armies_of(opponent)
                if self._distance_to_corner(a.position, settlement.position, config) <= 3
            )
            if nearby_enemies > defenders:
                score -= (nearby_enemies - defenders) * weights.vulnerability

        # 7. Expansion opportunities
        good_corners = 0
        for corner in board.all_corners():
            if board.settlement_at(corner) is not None:
                continue
            adjacent = corner.valid_adjacent_hexes(config.board_radius)
            my_friendly = board.friendly_hexes(player)
            new_hexes = len([h for h in adjacent if h not in my_friendly])
            if new_hexes >= 2:
                good_corners += 1
        score += good_corners * weights.expansion_opportunity

        # 8. Attack opportunities
        for settlement in board.settlements_of(opponent):
            nearby_armies = sum(
                1 for a in board.armies_of(player)
                if self._distance_to_corner(a.position, settlement.position, config) <= 2
            )
            is_defended = any(
                a.owner == opponent for a in board.armies_at(settlement.position)
            )
            needed = config.capture.defended_armies_required if is_defended else config.capture.undefended_armies_required
            if nearby_armies >= needed:
                score += weights.attack_opportunity

        return score

    def _generate_action_sequence(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        armies_on_corners: set[int],
    ) -> list[Action]:
        """Generate a random but valid action sequence."""
        actions: list[Action] = []
        current_board = board

        for army in list(current_board.armies_of(player)):
            started_on_corner = army.id in armies_on_corners
            current_army = current_board.army_by_id(army.id)
            if current_army is None:
                continue

            # Random choice: settle, move, or pass
            choices = ["move", "pass"]
            if started_on_corner and can_settle(current_army, current_board, config, True):
                choices.append("settle")

            choice = self._rng.choice(choices)

            if choice == "settle":
                actions.append(SettleAction(army_id=army.id))
                current_board = current_board.with_army_moved(
                    army.id, current_army.position, config.movement.settle_cost
                )
                current_board, _ = current_board.with_settlement(current_army.position, player)
            elif choice == "move":
                move_actions = self._random_moves(current_army, current_board, player, config)
                actions.extend(move_actions)
                for action in move_actions:
                    if isinstance(action, MoveAction):
                        cost = calculate_movement_cost(
                            current_army.position, action.to_position, player, current_board, config
                        )
                        if cost:
                            current_board = current_board.with_army_moved(action.army_id, action.to_position, cost)
                            current_army = current_board.army_by_id(action.army_id)
            else:
                actions.append(PassAction(army_id=army.id))

        return actions

    def _random_moves(
        self,
        army: Army,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> list[Action]:
        """Generate random moves for an army."""
        actions: list[Action] = []
        current_army = army
        current_board = board

        while current_army.movement_remaining > 0:
            # Get ADJACENT positions only
            adjacent = self._get_adjacent_positions(current_army.position, current_board)
            valid_moves = []
            for pos in adjacent:
                cost = calculate_movement_cost(
                    current_army.position, pos, player, current_board, config
                )
                if cost is not None and cost <= current_army.movement_remaining:
                    valid_moves.append((pos, cost))

            if not valid_moves:
                break

            target, cost = self._rng.choice(valid_moves)
            actions.append(MoveAction(army_id=army.id, to_position=target))
            current_board = current_board.with_army_moved(army.id, target, cost)
            current_army = current_board.army_by_id(army.id)

            if self._rng.random() < 0.5:  # 50% chance to stop early
                break

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

    def _greedy_actions(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        armies_on_corners: set[int],
        weights: EvaluationWeights,
    ) -> list[Action]:
        """Generate greedy actions (best immediate move for each army)."""
        actions: list[Action] = []
        current_board = board

        for army in list(current_board.armies_of(player)):
            started_on_corner = army.id in armies_on_corners
            current_army = current_board.army_by_id(army.id)
            if current_army is None:
                continue

            best_action: Action = PassAction(army_id=army.id)
            best_score = self._evaluate_position(current_board, player, config, weights)

            # Try settling
            if started_on_corner and can_settle(current_army, current_board, config, True):
                test_board = current_board.with_army_moved(
                    army.id, current_army.position, config.movement.settle_cost
                )
                test_board, _ = test_board.with_settlement(current_army.position, player)
                score = self._evaluate_position(test_board, player, config, weights)
                if score > best_score:
                    best_score = score
                    best_action = SettleAction(army_id=army.id)

            # Try each ADJACENT position only
            adjacent = self._get_adjacent_positions(current_army.position, current_board)
            for pos in adjacent:
                cost = calculate_movement_cost(
                    current_army.position, pos, player, current_board, config
                )
                if cost is None or cost > current_army.movement_remaining:
                    continue

                test_board = current_board.with_army_moved(army.id, pos, cost)
                score = self._evaluate_position(test_board, player, config, weights)

                if score > best_score:
                    best_score = score
                    best_action = MoveAction(army_id=army.id, to_position=pos)

            actions.append(best_action)

            # Update board for next army
            if isinstance(best_action, MoveAction):
                cost = calculate_movement_cost(
                    current_army.position, best_action.to_position, player, current_board, config
                )
                if cost:
                    current_board = current_board.with_army_moved(army.id, best_action.to_position, cost)
            elif isinstance(best_action, SettleAction):
                current_board = current_board.with_army_moved(
                    army.id, current_army.position, config.movement.settle_cost
                )
                current_board, _ = current_board.with_settlement(current_army.position, player)

        return actions

    def _simulate_actions(
        self,
        board: GameBoard,
        player: Player,
        actions: list[Action],
        config: GameConfig,
    ) -> GameBoard:
        """Simulate applying actions to board."""
        current_board = board

        for action in actions:
            army = current_board.army_by_id(action.army_id)
            if army is None:
                continue

            if isinstance(action, MoveAction):
                cost = calculate_movement_cost(
                    army.position, action.to_position, player, current_board, config
                )
                if cost and cost <= army.movement_remaining:
                    current_board = current_board.with_army_moved(
                        action.army_id, action.to_position, cost
                    )
            elif isinstance(action, SettleAction):
                if isinstance(army.position, CornerCoord):
                    current_board = current_board.with_army_moved(
                        action.army_id, army.position, config.movement.settle_cost
                    )
                    current_board, _ = current_board.with_settlement(army.position, player)

        return current_board

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
            if army1.position == army2.position:
                return 0
            shared = army1.position.valid_adjacent_hexes(config.board_radius) & army2.position.valid_adjacent_hexes(config.board_radius)
            return 1 if shared else 2
