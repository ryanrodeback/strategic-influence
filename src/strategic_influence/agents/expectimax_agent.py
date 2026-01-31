#!/usr/bin/env python3
"""ExpectimaxAgent: Proper handling of stochastic combat.

This agent fixes the critical bug in MinimaxAgent where stochastic combat
was evaluated with a fixed seed, causing deeper search to perform worse.

The key insight: In games with chance elements (like combat with dice rolls),
we must compute the EXPECTED VALUE over possible outcomes, not assume a
single deterministic outcome.

Methods:
1. Monte Carlo Sampling: Sample N different random seeds, average results
2. Analytical: Pre-compute expected combat outcomes (future enhancement)

This implementation uses Monte Carlo sampling for simplicity and correctness.
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


class ExpectimaxAgent:
    """Expectimax agent with proper stochastic combat handling.

    Unlike standard minimax which uses a fixed seed (causing bias),
    this agent samples multiple random outcomes and averages them
    to get the expected value.

    Parameters:
    - max_depth: Search depth (1-3 recommended)
    - num_samples: Number of random samples for chance nodes (5-20)
    - max_moves: Maximum moves to consider per position
    - max_candidates_per_territory: Max options per territory
    - time_limit_sec: Hard time limit per move
    """

    def __init__(
        self,
        seed: int | None = None,
        max_depth: int = 2,
        num_samples: int = 8,  # Number of samples for chance nodes
        weights: EvaluationWeights | None = None,
        max_moves: int = 8,
        max_candidates_per_territory: int = 4,
        time_limit_sec: float = 10.0,
        verbose: bool = False,
    ):
        self._initial_seed = seed
        self._rng = Random(seed)
        self._max_depth = max_depth
        self._num_samples = num_samples
        self._weights = weights or BALANCED_WEIGHTS
        self._max_moves = max_moves
        self._max_candidates_per_territory = max_candidates_per_territory
        self._time_limit_sec = time_limit_sec
        self._verbose = verbose

        self._nodes_searched = 0
        self._samples_taken = 0
        self._last_search_time = 0.0
        self._start_time = 0.0

    @property
    def name(self) -> str:
        return f"Expectimax(d={self._max_depth},s={self._num_samples})"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)
        self._nodes_searched = 0
        self._samples_taken = 0

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
        """Choose best move using expectimax with Monte Carlo sampling."""
        self._start_time = time.time()
        self._nodes_searched = 0
        self._samples_taken = 0

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
            print(f"  Expectimax: {len(moves)} moves, depth {self._max_depth}, {self._num_samples} samples")

        best_move = moves[0]
        best_value = float("-inf")

        for move in moves:
            if time.time() - self._start_time > self._time_limit_sec:
                if self._verbose:
                    print(f"  Time limit exceeded, using current best move")
                break

            # Use expectimax: average over opponent responses AND random outcomes
            value = self._expectimax_value(state, player, move, self._max_depth, config)

            if value > best_value:
                best_value = value
                best_move = move

        self._last_search_time = time.time() - self._start_time

        if self._verbose:
            print(f"  Expectimax: {self._nodes_searched} nodes, {self._samples_taken} samples, {self._last_search_time:.2f}s")

        return best_move

    def get_stats(self) -> dict:
        """Get statistics from last search."""
        return {
            "nodes_searched": self._nodes_searched,
            "samples_taken": self._samples_taken,
            "search_time": self._last_search_time,
        }

    def _expectimax_value(
        self,
        state: GameState,
        player: Owner,
        my_move: PlayerTurnActions,
        depth: int,
        config: GameConfig,
    ) -> float:
        """Compute expected value for a move, averaging over random outcomes.

        This is the key fix: instead of using Random(42) and getting one
        deterministic outcome, we sample multiple random outcomes and average.
        """
        opponent = player.opponent()

        # Generate opponent moves
        opp_moves = self._generate_limited_moves(state, opponent, config)
        if not opp_moves:
            # Opponent has no moves - evaluate with sampling
            return self._sample_expected_value(state, my_move, opponent, None, player, depth, config)

        opp_moves = self._order_moves(opp_moves, state, opponent, config)
        if len(opp_moves) > self._max_moves:
            opp_moves = opp_moves[: self._max_moves]

        # Opponent minimizes our value
        min_value = float("inf")

        for opp_move in opp_moves:
            # Sample expected value over random outcomes
            expected_value = self._sample_expected_value(
                state, my_move, opponent, opp_move, player, depth, config
            )
            min_value = min(min_value, expected_value)

        return min_value

    def _sample_expected_value(
        self,
        state: GameState,
        my_move: PlayerTurnActions,
        opponent: Owner,
        opp_move: PlayerTurnActions | None,
        player: Owner,
        depth: int,
        config: GameConfig,
    ) -> float:
        """Sample multiple random outcomes and average.

        This handles the stochastic combat properly by not assuming
        a fixed dice roll sequence.
        """
        total_value = 0.0

        for i in range(self._num_samples):
            self._samples_taken += 1

            # Use a fresh random seed for each sample
            sample_rng = Random(self._rng.randint(0, 2**31 - 1))

            # Apply turn with this random outcome
            next_state = self._apply_turn_sampled(
                state, my_move, opp_move, player, config, sample_rng
            )

            # Recursively evaluate or use heuristic
            if depth <= 1 or next_state.is_complete:
                self._nodes_searched += 1
                value = evaluate_board(
                    next_state.board, player, config, next_state.current_turn, self._weights
                )
            else:
                # Recursive expectimax
                value = self._max_player_value(next_state, player, depth - 1, config)

            total_value += value

        return total_value / self._num_samples

    def _max_player_value(
        self,
        state: GameState,
        player: Owner,
        depth: int,
        config: GameConfig,
    ) -> float:
        """Maximizing player's expected value."""
        self._nodes_searched += 1

        if time.time() - self._start_time > self._time_limit_sec:
            return evaluate_board(state.board, player, config, state.current_turn, self._weights)

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
            value = self._expectimax_value(state, player, move, depth, config)
            best_value = max(best_value, value)

        return best_value

    def _apply_turn_sampled(
        self,
        state: GameState,
        my_move: PlayerTurnActions,
        opp_move: PlayerTurnActions | None,
        player: Owner,
        config: GameConfig,
        rng: Random,
    ) -> GameState:
        """Apply turn with a specific random generator (for sampling)."""
        opponent = player.opponent()

        if opp_move is None:
            opp_move = PlayerTurnActions(player=opponent, actions=())

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

        return apply_turn(state, turn_actions, config, rng)

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

        territory_options: list[list[TerritoryAction]] = []

        for pos in territories:
            options = self._get_limited_options(pos, state.board, config)
            if not options:
                options = [create_grow_action(pos)]
            territory_options.append(options)

        total_combos = 1
        for opts in territory_options:
            total_combos *= len(opts)

        if total_combos > 200:
            return self._sample_moves(state, player, config, 30)

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
        """Get limited options for a territory."""
        territory = board.get(pos)
        stones = territory.stones
        player = territory.owner
        opponent = player.opponent()

        if stones <= 1:
            return [create_grow_action(pos)]

        options = [create_grow_action(pos)]
        half_stones = calculate_half(stones)
        neighbors = list(pos.neighbors(config.board_size))

        if not neighbors:
            return options

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

            if owner == Owner.NEUTRAL:
                neutral_count = sum(
                    1 for nn in neighbor.neighbors(config.board_size)
                    if board.get_owner(nn) == Owner.NEUTRAL
                )
                score = 100 + neutral_count
            elif owner == opponent:
                score = 50
            else:
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

        all_stay = tuple(create_grow_action(p) for p in territories)
        moves.append(PlayerTurnActions(player=player, actions=all_stay))

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
        """Order moves for better search."""
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

    def _all_stay(
        self,
        state: GameState,
        player: Owner,
    ) -> PlayerTurnActions:
        """Create all-stay actions."""
        actions = [create_grow_action(pos) for pos in state.board.positions_owned_by(player)]
        return PlayerTurnActions(player=player, actions=tuple(actions))
