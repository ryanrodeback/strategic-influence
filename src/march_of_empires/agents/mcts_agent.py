"""Monte Carlo Tree Search agent for March of Empires."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
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


@dataclass
class MCTSNode:
    """Node in the MCTS search tree."""

    board: GameBoard
    player: Player  # Player who just moved (parent's active player)
    parent: MCTSNode | None = None
    action: Action | None = None  # Action that led to this state
    children: list[MCTSNode] = field(default_factory=list)
    visits: int = 0
    wins: float = 0.0
    untried_actions: list[Action] | None = None

    def ucb_value(self, exploration_c: float, parent_visits: int) -> float:
        """Calculate UCB1 value for node selection."""
        if self.visits == 0:
            return float('inf')
        exploitation = self.wins / self.visits
        exploration = exploration_c * math.sqrt(math.log(parent_visits) / self.visits)
        return exploitation + exploration


class MCTSAgent:
    """Monte Carlo Tree Search agent.

    Uses MCTS with heuristic rollouts for move selection.
    Adapts well to complex positions where simple heuristics fail.
    """

    def __init__(
        self,
        seed: int | None = None,
        num_simulations: int = 50,
        exploration_c: float = 1.414,
        rollout_depth: int = 10,
    ):
        self._name = "MCTS"
        self._rng = random.Random(seed)
        self._num_simulations = num_simulations
        self._exploration_c = exploration_c
        self._rollout_depth = rollout_depth

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
        """Use MCTS to choose actions."""
        board = state.board

        # Track which armies started on corners
        armies_on_corners: set[int] = set()
        for army in board.armies_of(player):
            if isinstance(army.position, CornerCoord):
                armies_on_corners.add(army.id)

        # Run MCTS to find best action sequence
        best_actions = self._mcts_search(
            board, player, config, armies_on_corners
        )

        return TurnActions(player=player, actions=tuple(best_actions))

    def _mcts_search(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        armies_on_corners: set[int],
    ) -> list[Action]:
        """Run MCTS search and return best actions."""
        root = MCTSNode(board=board, player=player.opponent())  # Parent was opponent

        # Generate initial actions for root
        root.untried_actions = self._generate_all_actions(
            board, player, config, armies_on_corners
        )

        for _ in range(self._num_simulations):
            node = root
            current_board = board
            current_player = player

            # 1. Selection: Traverse tree using UCB1
            while node.untried_actions is not None and len(node.untried_actions) == 0 and node.children:
                node = max(
                    node.children,
                    key=lambda n: n.ucb_value(self._exploration_c, node.visits)
                )
                if node.action:
                    current_board = self._apply_action(
                        current_board, current_player, node.action, config
                    )

            # 2. Expansion: Add one new child
            if node.untried_actions and len(node.untried_actions) > 0:
                action = self._rng.choice(node.untried_actions)
                node.untried_actions.remove(action)

                new_board = self._apply_action(current_board, current_player, action, config)
                child = MCTSNode(
                    board=new_board,
                    player=current_player,
                    parent=node,
                    action=action,
                )
                # Generate actions for child (opponent's turn after our actions)
                child.untried_actions = self._generate_all_actions(
                    new_board, current_player.opponent(), config, set()
                )
                node.children.append(child)
                node = child
                current_board = new_board

            # 3. Simulation: Heuristic rollout
            result = self._rollout(current_board, player, config)

            # 4. Backpropagation
            while node is not None:
                node.visits += 1
                if result == player:
                    node.wins += 1.0
                elif result is None:
                    node.wins += 0.5
                node = node.parent

        # Select best action (most visited child)
        if not root.children:
            # Fallback: use greedy action
            return self._greedy_actions(board, player, config, armies_on_corners)

        best_child = max(root.children, key=lambda c: c.visits)
        if best_child.action:
            return [best_child.action]

        return self._greedy_actions(board, player, config, armies_on_corners)

    def _generate_all_actions(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        armies_on_corners: set[int],
    ) -> list[Action]:
        """Generate all possible actions for a player."""
        actions: list[Action] = []

        for army in board.armies_of(player):
            started_on_corner = army.id in armies_on_corners

            # Can settle?
            if started_on_corner and can_settle(army, board, config, True):
                actions.append(SettleAction(army_id=army.id))

            # Can move? Only to ADJACENT positions (single step moves)
            adjacent = self._get_adjacent_positions(army.position, board)
            for pos in adjacent:
                cost = calculate_movement_cost(army.position, pos, player, board, config)
                if cost is not None and cost <= army.movement_remaining:
                    actions.append(MoveAction(army_id=army.id, to_position=pos))

            # Can pass
            actions.append(PassAction(army_id=army.id))

        return actions if actions else [PassAction(army_id=-1)]  # Dummy pass if no armies

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

    def _rollout(
        self,
        board: GameBoard,
        perspective_player: Player,
        config: GameConfig,
    ) -> Player | None:
        """Simulate game to completion using heuristic policy."""
        current_board = board
        current_player = perspective_player

        for _ in range(self._rollout_depth):
            # Quick heuristic move
            action = self._rollout_policy(current_board, current_player, config)
            current_board = self._apply_action(current_board, current_player, action, config)
            current_player = current_player.opponent()

        # Evaluate final position
        p1_score = calculate_score(current_board, Player.PLAYER_1)
        p2_score = calculate_score(current_board, Player.PLAYER_2)

        if p1_score > p2_score:
            return Player.PLAYER_1
        elif p2_score > p1_score:
            return Player.PLAYER_2
        return None

    def _rollout_policy(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> Action:
        """Quick heuristic for rollout move selection - expansion focused."""
        armies = list(board.armies_of(player))
        if not armies:
            return PassAction(army_id=-1)

        army = self._rng.choice(armies)

        # PRIORITIZE SETTLING - this is the key to winning
        if isinstance(army.position, CornerCoord):
            if can_settle(army, board, config, True):
                # Check if settling gains territory
                my_hexes = board.friendly_hexes(player)
                adjacent = army.position.valid_adjacent_hexes(config.board_radius)
                new_hexes = len([h for h in adjacent if h not in my_hexes])
                if new_hexes >= 1:
                    return SettleAction(army_id=army.id)

        # 20% random for exploration
        if self._rng.random() < 0.2:
            return self._random_action(army, board, player, config)

        # Move toward nearest unsettled corner for expansion
        best_corner = self._find_nearest_unsettled_corner(army, board, player, config)
        if best_corner:
            move = self._move_toward(army, best_corner, board, player, config)
            if move:
                return move

        return self._random_action(army, board, player, config)

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

            # Score by new hexes - distance
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

    def _random_action(
        self,
        army: Army,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> Action:
        """Generate a random valid action."""
        reachable = get_reachable_positions(army, board, config)
        moves = [pos for pos in reachable if pos != army.position]

        if moves and self._rng.random() < 0.7:
            return MoveAction(army_id=army.id, to_position=self._rng.choice(moves))

        return PassAction(army_id=army.id)

    def _can_reach(
        self,
        army: Army,
        target: Position,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> bool:
        """Check if army can reach target in one turn."""
        reachable = get_reachable_positions(army, board, config)
        return target in reachable

    def _move_toward(
        self,
        army: Army,
        target: CornerCoord,
        board: GameBoard,
        player: Player,
        config: GameConfig,
    ) -> Action | None:
        """Generate move toward target."""
        reachable = get_reachable_positions(army, board, config)

        best_pos = None
        best_dist = self._distance_to_corner(army.position, target, config)

        for pos in reachable:
            if pos == army.position:
                continue
            dist = self._distance_to_corner(pos, target, config)
            if dist < best_dist:
                best_dist = dist
                best_pos = pos

        if best_pos:
            return MoveAction(army_id=army.id, to_position=best_pos)
        return None

    def _greedy_actions(
        self,
        board: GameBoard,
        player: Player,
        config: GameConfig,
        armies_on_corners: set[int],
    ) -> list[Action]:
        """Fallback greedy action selection - expansion focused."""
        actions: list[Action] = []

        for army in board.armies_of(player):
            started_on_corner = army.id in armies_on_corners

            # Try settling first - this is the key to winning
            if started_on_corner and can_settle(army, board, config, True):
                if isinstance(army.position, CornerCoord):
                    my_hexes = board.friendly_hexes(player)
                    adjacent = army.position.valid_adjacent_hexes(config.board_radius)
                    new_hexes = len([h for h in adjacent if h not in my_hexes])
                    if new_hexes >= 1:
                        actions.append(SettleAction(army_id=army.id))
                        continue

            # Move toward best unsettled corner for expansion
            best_corner = self._find_nearest_unsettled_corner(army, board, player, config)
            if best_corner:
                move = self._move_toward(army, best_corner, board, player, config)
                if move:
                    actions.append(move)
                    continue

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
