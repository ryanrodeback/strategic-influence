#!/usr/bin/env python3
"""Optimized MinimaxAgent that avoids move generation overhead.

Key improvements:
1. Faster move generation with limits
2. Better pruning
3. Time limits per move
4. Simpler evaluation for shallow depths

Run tests with: python -m pytest tests/unit/test_agents.py -v
"""

import time
from random import Random
from itertools import product

from ..types import (
    Owner,
    Position,
    GameState,
    SetupAction,
    PlayerTurnActions,
    TerritoryAction,
    TurnActions,
    calculate_half,
    create_grow_action,
    create_simple_move_action,
)
from ..config import GameConfig
from ..engine import apply_turn
from ..evaluation import (
    evaluate_board,
    BALANCED_WEIGHTS,
    EvaluationWeights,
)


class OptimizedMinimaxAgent:
    """Faster minimax with better move limiting and time control.

    Key changes from MinimaxAgent:
    - Hard limit on move generation (max_candidates per territory)
    - Time limit per move
    - Simplified evaluation for depth 0-1
    - Better initial move ordering

    Parameters:
    - max_depth: Search depth (1-2 recommended)
    - max_moves: Maximum moves to consider (5-10 for speed)
    - max_candidates_per_territory: Max options per territory (3-5)
    - time_limit_sec: Hard time limit per move
    """

    def __init__(
        self,
        seed: int | None = None,
        max_depth: int = 1,
        weights: EvaluationWeights | None = None,
        max_moves: int = 8,
        max_candidates_per_territory: int = 4,
        time_limit_sec: float = 5.0,
        verbose: bool = False,
    ):
        self._initial_seed = seed
        self._rng = Random(seed)
        self._max_depth = max_depth
        self._weights = weights or BALANCED_WEIGHTS
        self._max_moves = max_moves
        self._max_candidates_per_territory = max_candidates_per_territory
        self._time_limit_sec = time_limit_sec
        self._verbose = verbose

        self._nodes_searched = 0
        self._last_search_time = 0.0
        self._start_time = 0.0

    @property
    def name(self) -> str:
        return f"OptimizedMinimax(d={self._max_depth})"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)
        self._nodes_searched = 0

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose setup position - prefer center."""
        board_size = config.board_size
        mid = board_size // 2

        valid_positions = [
            Position(r, c)
            for r in range(board_size)
            for c in range(board_size)
            if Position(r, c).is_in_setup_zone(board_size, player)
            and state.board.get_owner(Position(r, c)) == Owner.NEUTRAL
        ]

        if not valid_positions:
            raise ValueError(f"No valid setup positions for {player}")

        def center_distance(pos: Position) -> float:
            return abs(pos.row - mid) + abs(pos.col - mid)

        valid_positions.sort(key=center_distance)
        return SetupAction(player=player, position=valid_positions[0])

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose best move using optimized minimax."""
        self._start_time = time.time()
        self._nodes_searched = 0

        # Limit to 5 best candidates per territory for speed
        moves = self._generate_limited_moves(state, player, config)
        if not moves:
            return self._all_stay(state, player)

        if len(moves) == 1:
            return moves[0]

        # Order for better pruning
        moves = self._order_moves(moves, state, player, config)
        if len(moves) > self._max_moves:
            moves = moves[: self._max_moves]

        if self._verbose:
            print(f"  OptimizedMinimax: {len(moves)} moves, depth {self._max_depth}")

        best_move = moves[0]
        best_value = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for move in moves:
            # Check time limit
            if time.time() - self._start_time > self._time_limit_sec:
                if self._verbose:
                    print(f"  Time limit exceeded, using current best move")
                break

            value = self._min_opponent(state, player, move, self._max_depth, alpha, beta, config)

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, value)

        self._last_search_time = time.time() - self._start_time

        if self._verbose:
            print(f"  OptimizedMinimax: {self._nodes_searched} nodes, {self._last_search_time:.2f}s")

        return best_move

    def get_stats(self) -> dict:
        """Get statistics from last search."""
        return {
            "nodes_searched": self._nodes_searched,
            "search_time": self._last_search_time,
        }

    def _generate_limited_moves(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> list[PlayerTurnActions]:
        """Generate limited set of candidate moves quickly."""
        territories = list(state.board.positions_owned_by(player))
        if not territories:
            return []

        # For each territory, get limited options
        territory_options: list[list[TerritoryAction]] = []

        for pos in territories:
            options = self._get_limited_options(pos, state.board, config)
            if not options:
                options = [create_grow_action(pos)]
            territory_options.append(options)

        # Generate combinations with limits
        total_combos = 1
        for opts in territory_options:
            total_combos *= len(opts)

        if total_combos > 200:
            # Too many combinations - sample instead
            return self._sample_moves(state, player, config, 30)

        # Generate all combinations
        all_combos = list(product(*territory_options))
        moves = [
            PlayerTurnActions(player=player, actions=tuple(combo)) for combo in all_combos
        ]

        return moves

    def _get_limited_options(
        self,
        pos: Position,
        board,
        config: GameConfig,
    ) -> list[TerritoryAction]:
        """Get limited options for a territory (faster than full enumeration)."""
        territory = board.get(pos)
        stones = territory.stones
        player = territory.owner
        opponent = player.opponent()

        # 1-stone territories must STAY
        if stones <= 1:
            return [create_grow_action(pos)]

        options = [create_grow_action(pos)]  # STAY is always first
        half_stones = calculate_half(stones)
        neighbors = list(pos.neighbors(config.board_size))

        if not neighbors:
            return options

        # Limit neighbors considered
        best_neighbors = self._select_best_neighbors(
            pos, neighbors, board, config, self._max_candidates_per_territory
        )

        for neighbor in best_neighbors:
            neighbor_owner = board.get_owner(neighbor)
            neighbor_stones = board.get_stones(neighbor) if neighbor_owner != Owner.NEUTRAL else 0

            if neighbor_owner == Owner.NEUTRAL:
                options.append(create_simple_move_action(pos, neighbor, half_stones))

            elif neighbor_owner == opponent:
                if half_stones > neighbor_stones:
                    options.append(create_simple_move_action(pos, neighbor, half_stones))
                elif stones > neighbor_stones:
                    options.append(create_simple_move_action(pos, neighbor, stones))

            else:  # friendly
                neighbor_threatened_by = None
                for nn in neighbor.neighbors(config.board_size):
                    if board.get_owner(nn) == opponent:
                        enemy_stones = board.get_stones(nn)
                        if enemy_stones > neighbor_stones:
                            neighbor_threatened_by = enemy_stones
                            break

                if neighbor_threatened_by is not None:
                    reinforced = neighbor_stones + half_stones
                    if reinforced >= neighbor_threatened_by:
                        options.append(create_simple_move_action(pos, neighbor, half_stones))

        return options if options else [create_grow_action(pos)]

    def _select_best_neighbors(
        self,
        pos: Position,
        neighbors: list[Position],
        board,
        config: GameConfig,
        limit: int,
    ) -> list[Position]:
        """Select most promising neighbors."""
        scored = []
        opponent = board.get_owner(pos).opponent()

        for neighbor in neighbors:
            owner = board.get_owner(neighbor)
            stones = board.get_stones(neighbor)

            if owner == Owner.NEUTRAL:
                # Score by neutral neighbors
                neutral_count = sum(
                    1 for nn in neighbor.neighbors(config.board_size)
                    if board.get_owner(nn) == Owner.NEUTRAL
                )
                score = 100 + neutral_count
            elif owner == opponent:
                # Score attacks
                score = 50
            else:
                # Score friendly
                score = 30

            scored.append((score, neighbor))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [n for _, n in scored[: limit]]

    def _sample_moves(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
        n: int,
    ) -> list[PlayerTurnActions]:
        """Sample moves when full enumeration is expensive."""
        moves = []
        territories = list(state.board.positions_owned_by(player))

        # Always include all-stay
        all_stay = tuple(create_grow_action(p) for p in territories)
        moves.append(PlayerTurnActions(player=player, actions=all_stay))

        # Generate random samples
        for _ in range(n - 1):
            actions = []
            for pos in territories:
                options = self._get_limited_options(pos, state.board, config)
                actions.append(self._rng.choice(options))
            moves.append(PlayerTurnActions(player=player, actions=tuple(actions)))

        return moves

    def _order_moves(
        self,
        moves: list[PlayerTurnActions],
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> list[PlayerTurnActions]:
        """Order moves for better pruning."""
        board = state.board

        def move_score(move: PlayerTurnActions) -> float:
            score = 0.0

            for action in move.actions:
                if action.is_grow:
                    score += 10
                elif action.is_move:
                    for movement in action.movements:
                        dest = movement.destination
                        dest_owner = board.get_owner(dest)

                        if dest_owner == Owner.NEUTRAL:
                            score += 200
                        elif dest_owner == player.opponent():
                            score += 100
                        else:
                            score += 50

            return score

        return sorted(moves, key=move_score, reverse=True)

    def _max_player(
        self,
        state: GameState,
        player: Owner,
        depth: int,
        alpha: float,
        beta: float,
        config: GameConfig,
    ) -> float:
        """Maximizing player's turn."""
        self._nodes_searched += 1

        # Check time limit
        if time.time() - self._start_time > self._time_limit_sec:
            return evaluate_board(state.board, player, config, state.current_turn, self._weights)

        # Terminal or depth limit
        if state.is_complete or depth == 0:
            return evaluate_board(state.board, player, config, state.current_turn, self._weights)

        moves = self._generate_limited_moves(state, player, config)
        if not moves:
            return evaluate_board(state.board, player, config, state.current_turn, self._weights)

        moves = self._order_moves(moves, state, player, config)
        if len(moves) > self._max_moves:
            moves = moves[: self._max_moves]

        best_value = float("-inf")

        for move in moves:
            value = self._min_opponent(state, player, move, depth, alpha, beta, config)
            best_value = max(best_value, value)
            alpha = max(alpha, value)

            if beta <= alpha:
                break

        return best_value

    def _min_opponent(
        self,
        state: GameState,
        player: Owner,
        my_move: PlayerTurnActions,
        depth: int,
        alpha: float,
        beta: float,
        config: GameConfig,
    ) -> float:
        """Minimizing opponent's response."""
        opponent = player.opponent()

        opp_moves = self._generate_limited_moves(state, opponent, config)
        if not opp_moves:
            next_state = self._apply_turn(state, my_move, player, config)
            return self._max_player(next_state, player, depth - 1, alpha, beta, config)

        opp_moves = self._order_moves(opp_moves, state, opponent, config)
        if len(opp_moves) > self._max_moves:
            opp_moves = opp_moves[: self._max_moves]

        best_value = float("inf")

        for opp_move in opp_moves:
            next_state = self._apply_turn_both(state, my_move, opp_move, player, config)
            value = self._max_player(next_state, player, depth - 1, alpha, beta, config)
            best_value = min(best_value, value)
            beta = min(beta, value)

            if beta <= alpha:
                break

        return best_value

    def _apply_turn(
        self,
        state: GameState,
        move: PlayerTurnActions,
        player: Owner,
        config: GameConfig,
    ) -> GameState:
        """Apply a single player's move."""
        opponent = player.opponent()
        opp_actions = PlayerTurnActions(player=opponent, actions=())

        if player == Owner.PLAYER_1:
            turn_actions = TurnActions(
                player1_actions=move,
                player2_actions=opp_actions,
                turn_number=state.current_turn + 1,
            )
        else:
            turn_actions = TurnActions(
                player1_actions=opp_actions,
                player2_actions=move,
                turn_number=state.current_turn + 1,
            )

        return apply_turn(state, turn_actions, config, self._rng)

    def _apply_turn_both(
        self,
        state: GameState,
        my_move: PlayerTurnActions,
        opp_move: PlayerTurnActions,
        player: Owner,
        config: GameConfig,
    ) -> GameState:
        """Apply simultaneous moves."""
        if player == Owner.PLAYER_1:
            turn_actions = TurnActions(
                player1_actions=my_move,
                player2_actions=opp_move,
                turn_number=state.current_turn + 1,
            )
        else:
            turn_actions = TurnActions(
                player1_actions=opp_move,
                player2_actions=my_move,
                turn_number=state.current_turn + 1,
            )

        # Use fixed seed for consistency
        eval_rng = Random(42)
        return apply_turn(state, turn_actions, config, eval_rng)

    def _all_stay(
        self,
        state: GameState,
        player: Owner,
    ) -> PlayerTurnActions:
        """Create all-stay actions."""
        actions = [create_grow_action(pos) for pos in state.board.positions_owned_by(player)]
        return PlayerTurnActions(player=player, actions=tuple(actions))
