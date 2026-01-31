"""MinimaxAgent: True game tree search with alpha-beta pruning.

With the simplified 3-option system, branching factor is manageable:
- Per territory: ~9 options (1 STAY + 4 SEND_HALF + 4 SEND_ALL)
- 1-2 territories: can search 3-4 plies deep
- 3+ territories: reduce depth or sample moves

Handles simultaneous moves using "paranoid search" - assume
opponent plays the worst-case response to our move.

TUNING GUIDE:
- depth: How many turns to look ahead (1=fast, 2=moderate, 3+=slow)
- max_moves: How many moves to consider per position (fewer=faster)
- For debugging, set verbose=True to see search stats
"""

from itertools import product
from random import Random
import time

from ..types import (
    Owner,
    Position,
    GameState,
    SetupAction,
    PlayerTurnActions,
    TerritoryAction,
    TurnActions,
    MoveType,
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
from .common import center_aware_setup


class MinimaxAgent:
    """Minimax agent with alpha-beta pruning.

    Uses paranoid search for simultaneous moves:
    - We choose our move
    - Assume opponent sees it and plays optimal counter
    - Recurse

    Key parameters:
    - max_depth: How far to look ahead (default 2 for speed)
    - max_moves: Limit on moves to consider (default 20)
    - verbose: Print search statistics
    """

    def __init__(
        self,
        seed: int | None = None,
        max_depth: int = 2,  # Conservative default for speed
        weights: EvaluationWeights | None = None,
        max_moves: int = 20,  # Limit branching
        verbose: bool = False,
    ):
        self._initial_seed = seed
        self._rng = Random(seed)
        self._max_depth = max_depth
        self._weights = weights or BALANCED_WEIGHTS
        self._max_moves = max_moves
        self._verbose = verbose

        # Diagnostic counters (reset each move)
        self._nodes_searched = 0
        self._nodes_pruned = 0  # Cut off by alpha-beta
        self._moves_generated = 0
        self._moves_after_limit = 0
        self._last_search_time = 0.0

    @property
    def name(self) -> str:
        return f"MinimaxBot(d={self._max_depth})"

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
        return center_aware_setup(state, player, config)

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose best move using minimax with alpha-beta."""
        start_time = time.time()

        # Reset diagnostic counters
        self._nodes_searched = 0
        self._nodes_pruned = 0
        self._moves_generated = 0
        self._moves_after_limit = 0

        # Use configured depth
        depth = self._max_depth

        # Generate moves
        moves = self._generate_moves(state, player, config)
        if not moves:
            return self._all_stay(state, player)

        if len(moves) == 1:
            return moves[0]

        # Order moves for better pruning
        moves = self._order_moves(moves, state, player, config)

        # Track move limiting
        moves_before_limit = len(moves)
        if len(moves) > self._max_moves:
            moves = moves[:self._max_moves]
        self._moves_generated += moves_before_limit
        self._moves_after_limit += len(moves)

        if self._verbose:
            print(f"  Minimax: {len(moves)} moves (of {moves_before_limit}), depth {depth}")

        best_move = moves[0]
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for move in moves:
            value = self._min_opponent(
                state, player, move, depth, alpha, beta, config
            )

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, value)

        self._last_search_time = time.time() - start_time

        if self._verbose:
            prune_rate = self._nodes_pruned / max(1, self._nodes_searched + self._nodes_pruned)
            print(f"  Minimax: {self._nodes_searched} nodes, {self._nodes_pruned} pruned ({prune_rate:.0%}), {self._last_search_time:.2f}s")

        return best_move

    def get_stats(self) -> dict:
        """Get statistics from last search (for debugging)."""
        total_considered = self._nodes_searched + self._nodes_pruned
        prune_rate = self._nodes_pruned / max(1, total_considered)
        return {
            "nodes_searched": self._nodes_searched,
            "nodes_pruned": self._nodes_pruned,
            "prune_rate": prune_rate,
            "moves_generated": self._moves_generated,
            "moves_after_limit": self._moves_after_limit,
            "search_time": self._last_search_time,
            "nodes_per_second": self._nodes_searched / max(0.001, self._last_search_time),
        }

    def _generate_moves(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> list[PlayerTurnActions]:
        """Generate all legal moves for player."""
        territories = list(state.board.positions_owned_by(player))
        if not territories:
            return []

        # Generate options for each territory
        territory_options: list[list[TerritoryAction]] = []

        for pos in territories:
            options = self._get_territory_options(pos, state.board, config)
            territory_options.append(options)

        # Generate combinations (but limit to avoid explosion)
        total_combos = 1
        for opts in territory_options:
            total_combos *= len(opts)

        if total_combos > 1000:
            # Too many - use sampling
            return self._sample_moves(state, player, config, 100)

        # Generate all combinations
        all_combos = list(product(*territory_options))

        moves = []
        for combo in all_combos:
            moves.append(PlayerTurnActions(player=player, actions=tuple(combo)))

        return moves

    def _get_territory_options(
        self,
        pos: Position,
        board,
        config: GameConfig,
    ) -> list[TerritoryAction]:
        """Get options for a single territory.

        Simplified move generation (user hypotheses):
        - 1-stone territories must STAY
        - Eliminate SEND_ALL to neutral (abandons source)
        - Eliminate attacks without advantage
        - SEND_ALL to enemy only if SEND_HALF wouldn't win
        - Eliminate SEND_ALL to friendly (merge)
        - Eliminate reinforce that doesn't resolve threat
        """
        territory = board.get(pos)
        stones = territory.stones
        player = territory.owner
        opponent = player.opponent()

        # 1-stone territories must STAY
        if stones <= 1:
            return [create_grow_action(pos)]

        options = [create_grow_action(pos)]  # STAY is always an option
        half_stones = calculate_half(stones)
        neighbors = list(pos.neighbors(config.board_size))

        for neighbor in neighbors:
            neighbor_owner = board.get_owner(neighbor)
            neighbor_stones = board.get_stones(neighbor) if neighbor_owner != Owner.NEUTRAL else 0

            if neighbor_owner == Owner.NEUTRAL:
                # SEND_HALF to neutral only (SEND_ALL eliminated)
                options.append(create_simple_move_action(pos, neighbor, half_stones))

            elif neighbor_owner == opponent:
                # Attack only with advantage
                if half_stones > neighbor_stones:
                    # SEND_HALF wins - use it (keeps our territory)
                    options.append(create_simple_move_action(pos, neighbor, half_stones))
                elif stones > neighbor_stones:
                    # Only SEND_ALL wins - include it
                    options.append(create_simple_move_action(pos, neighbor, stones))
                # else: no advantage, don't include attack

            else:  # neighbor_owner == player (friendly)
                # Reinforce only if it resolves a threat
                # Check if neighbor is threatened (enemy nearby with more stones)
                neighbor_threatened_by = None
                for nn in neighbor.neighbors(config.board_size):
                    if board.get_owner(nn) == opponent:
                        enemy_stones = board.get_stones(nn)
                        if enemy_stones > neighbor_stones:
                            neighbor_threatened_by = enemy_stones
                            break

                if neighbor_threatened_by is not None:
                    # Neighbor is threatened - does our reinforcement help?
                    reinforced_stones = neighbor_stones + half_stones
                    if reinforced_stones >= neighbor_threatened_by:
                        # Reinforcement resolves the threat
                        options.append(create_simple_move_action(pos, neighbor, half_stones))
                # else: not threatened or reinforcement doesn't help - don't include

        return options

    def _sample_moves(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
        n: int,
    ) -> list[PlayerTurnActions]:
        """Sample n diverse moves when full enumeration is too expensive."""
        moves = []
        territories = list(state.board.positions_owned_by(player))

        # Always include all-stay
        all_stay = tuple(create_grow_action(p) for p in territories)
        moves.append(PlayerTurnActions(player=player, actions=all_stay))

        # Generate random samples
        for _ in range(n - 1):
            actions = []
            for pos in territories:
                options = self._get_territory_options(pos, state.board, config)
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
        """Order moves for better alpha-beta pruning.

        Simplified scoring (user hypotheses):
        1. EXPANSION - scored by destination's neutral neighbor count
        2. ATTACK with advantage - binary (has advantage = good)
        3. REINFORCE that resolves threat - high priority
        4. STAY/GROW - baseline
        """
        opponent = player.opponent()
        board = state.board

        def move_score(move: PlayerTurnActions) -> float:
            score = 0.0

            for action in move.actions:
                if action.is_grow:
                    # STAY/GROW - baseline
                    score += 10

                elif action.is_move:
                    for movement in action.movements:
                        dest = movement.destination
                        dest_owner = board.get_owner(dest)
                        stones_moving = movement.count

                        # 1. EXPANSION to neutral - score by future potential
                        if dest_owner == Owner.NEUTRAL:
                            # Count neutral neighbors of destination
                            neutral_neighbors = sum(
                                1 for nn in dest.neighbors(config.board_size)
                                if board.get_owner(nn) == Owner.NEUTRAL
                            )
                            # Best expansions have most neutral neighbors
                            score += 200 + neutral_neighbors * 30

                        # 2. ATTACK enemy - binary scoring (we already filtered no-advantage)
                        elif dest_owner == opponent:
                            score += 100  # All attacks here have advantage

                        # 3. REINFORCE friendly (we already filtered non-resolving)
                        elif dest_owner == player:
                            score += 80  # All reinforcements here resolve threats

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

        # Terminal or depth limit
        if state.is_complete or depth == 0:
            return evaluate_board(
                state.board, player, config,
                state.current_turn, self._weights
            )

        moves = self._generate_moves(state, player, config)
        if not moves:
            return evaluate_board(
                state.board, player, config,
                state.current_turn, self._weights
            )

        moves = self._order_moves(moves, state, player, config)
        if len(moves) > self._max_moves:
            moves = moves[:self._max_moves]

        best_value = float('-inf')

        for i, move in enumerate(moves):
            value = self._min_opponent(
                state, player, move, depth, alpha, beta, config
            )

            best_value = max(best_value, value)
            alpha = max(alpha, value)

            if beta <= alpha:
                # Pruning! Count remaining moves as pruned
                self._nodes_pruned += len(moves) - i - 1
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
        """Minimizing opponent's response to our move."""
        opponent = player.opponent()

        opp_moves = self._generate_moves(state, opponent, config)
        if not opp_moves:
            # Opponent has no moves - apply our move only
            next_state = self._apply_turn(state, my_move, player, config)
            return self._max_player(next_state, player, depth - 1, alpha, beta, config)

        # Limit opponent moves for speed (same limit as our moves)
        opp_moves = self._order_moves(opp_moves, state, opponent, config)
        if len(opp_moves) > self._max_moves:
            opp_moves = opp_moves[:self._max_moves]

        best_value = float('inf')

        for i, opp_move in enumerate(opp_moves):
            next_state = self._apply_turn_both(
                state, my_move, opp_move, player, config
            )

            value = self._max_player(
                next_state, player, depth - 1, alpha, beta, config
            )

            best_value = min(best_value, value)
            beta = min(beta, value)

            if beta <= alpha:
                # Pruning! Count remaining opponent moves as pruned
                self._nodes_pruned += len(opp_moves) - i - 1
                break

        return best_value

    def _apply_turn(
        self,
        state: GameState,
        move: PlayerTurnActions,
        player: Owner,
        config: GameConfig,
    ) -> GameState:
        """Apply a single player's move (opponent does nothing)."""
        opponent = player.opponent()

        # Create empty actions for opponent
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

        # Use fixed seed for consistency in evaluation
        eval_rng = Random(42)
        return apply_turn(state, turn_actions, config, eval_rng)

    def _all_stay(
        self,
        state: GameState,
        player: Owner,
    ) -> PlayerTurnActions:
        """Create actions where all territories stay."""
        actions = [
            create_grow_action(pos)
            for pos in state.board.positions_owned_by(player)
        ]
        return PlayerTurnActions(player=player, actions=tuple(actions))
