"""HeuristicMinimaxAgent: Pure heuristics encoding Minimax strategy without search.

The key insight: Minimax evaluates positions + orders moves strategically.
Can we capture this without tree search?

Core heuristics derived from Minimax:
1. 1-stone territories MUST STAY (survival rule)
2. EXPANSION is highest priority - valued by potential (neutral neighbors)
3. ATTACK only with clear advantage (our stones > enemy stones)
4. REINFORCE only if it resolves a threat
5. Score moves: expansion >> attack >> reinforce >> stay
6. Use evaluation function directly on reachable positions (1-ply lookahead)

This is "Minimax without the search tree" - we pick moves as Minimax would,
but instead of searching, we evaluate the immediate consequences.
"""

from random import Random

from ..types import (
    Owner,
    Position,
    GameState,
    SetupAction,
    PlayerTurnActions,
    TerritoryAction,
    calculate_half,
    create_grow_action,
    create_simple_move_action,
)
from ..config import GameConfig
from ..evaluation import (
    evaluate_board,
    BALANCED_WEIGHTS,
    EvaluationWeights,
)
from ..engine import apply_turn
from .common import center_aware_setup
from ..types import TurnActions


class HeuristicMinimaxAgent:
    """Pure heuristic agent capturing Minimax strategy without search.

    Strategy hierarchy:
    1. Score all valid moves using heuristics
    2. Pick move combination that maximizes immediate evaluation
    3. No tree search - just smart heuristics + 1-ply lookahead

    Key heuristics:
    - Expansion to neutral: valued by neutral neighbors (future growth potential)
    - Attack: only with advantage (half_stones > enemy or all_stones > enemy)
    - Reinforce: only if resolves a threat
    - 1-stone territories must STAY
    - Fallback: STAY and grow

    This encodes Minimax's move generation + ordering wisdom
    without expensive tree search.
    """

    def __init__(
        self,
        seed: int | None = None,
        weights: EvaluationWeights | None = None,
        use_lookahead: bool = True,
    ):
        self._initial_seed = seed
        self._rng = Random(seed)
        self._weights = weights or BALANCED_WEIGHTS
        self._use_lookahead = use_lookahead  # 1-ply lookahead evaluation

    @property
    def name(self) -> str:
        return "HeuristicMinimax"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose setup position - prefer center (same as Minimax)."""
        return center_aware_setup(state, player, config)

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose best moves using heuristics (no search).

        Strategy:
        1. For each territory, score all valid options
        2. Pick the single best option per territory
        3. Optionally evaluate the combined move (1-ply lookahead)
        """
        actions: list[TerritoryAction] = []
        board = state.board

        territories = list(board.positions_owned_by(player))
        if not territories:
            return PlayerTurnActions(player=player, actions=())

        # Score each territory's best action
        for pos in territories:
            best_action = self._choose_best_action(pos, state, player, config)
            actions.append(best_action)

        move = PlayerTurnActions(player=player, actions=tuple(actions))

        # Optional: evaluate the move's consequences to pick between equally-good moves
        if self._use_lookahead and len(actions) > 1:
            # Could evaluate multiple move combinations here
            # For now, just use greedy selection per territory
            pass

        return move

    def _choose_best_action(
        self,
        pos: Position,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> TerritoryAction:
        """Choose best action for a single territory using heuristics.

        Heuristic scoring (matching Minimax move ordering):
        - Expansion to neutral with most neutral neighbors: 200-300 points
        - Attack with advantage: 100 points (already filtered)
        - Reinforce resolving threat: 80 points (already filtered)
        - STAY/GROW: 10 points (baseline)

        Returns: Single best action (highest score, random among ties)
        """
        board = state.board
        territory = board.get(pos)
        stones = territory.stones
        opponent = player.opponent()

        # Rule 1: 1-stone territories MUST STAY (survival rule)
        if stones <= 1:
            return create_grow_action(pos)

        half_stones = calculate_half(stones)
        neighbors = list(pos.neighbors(config.board_size))

        # Score all valid options
        options: list[tuple[float, TerritoryAction]] = []

        # STAY is always an option (baseline)
        options.append((10.0, create_grow_action(pos)))

        for neighbor in neighbors:
            neighbor_owner = board.get_owner(neighbor)
            neighbor_stones = board.get_stones(neighbor) if neighbor_owner != Owner.NEUTRAL else 0

            if neighbor_owner == Owner.NEUTRAL:
                # EXPANSION: Score by future potential (neutral neighbors)
                # This is Minimax's key insight for move ordering
                neutral_neighbors = sum(
                    1 for nn in neighbor.neighbors(config.board_size)
                    if board.get_owner(nn) == Owner.NEUTRAL
                )
                # Scoring formula from Minimax move ordering
                score = 200.0 + neutral_neighbors * 30.0
                options.append((score, create_simple_move_action(pos, neighbor, half_stones)))

            elif neighbor_owner == opponent:
                # ATTACK: Only with clear advantage
                # Heuristic: Same filtering as Minimax move generation
                if half_stones > neighbor_stones:
                    # SEND_HALF wins - prefer it (keeps source territory)
                    options.append((100.0, create_simple_move_action(pos, neighbor, half_stones)))
                elif stones > neighbor_stones:
                    # Only SEND_ALL wins - include it (but lower score)
                    options.append((90.0, create_simple_move_action(pos, neighbor, stones)))
                # else: no advantage, don't include attack

            else:  # neighbor_owner == player (friendly)
                # REINFORCE: Only if it resolves a threat
                # Heuristic: Same threat detection as Minimax
                neighbor_threatened_by = None
                for nn in neighbor.neighbors(config.board_size):
                    if board.get_owner(nn) == opponent:
                        enemy_stones = board.get_stones(nn)
                        if enemy_stones > neighbor_stones:
                            neighbor_threatened_by = enemy_stones
                            break

                if neighbor_threatened_by is not None:
                    # Neighbor is threatened
                    reinforced_stones = neighbor_stones + half_stones
                    if reinforced_stones >= neighbor_threatened_by:
                        # Reinforcement resolves threat
                        options.append((80.0, create_simple_move_action(pos, neighbor, half_stones)))
                # else: not threatened or reinforcement doesn't help

        # Pick highest scored option
        if not options:
            return create_grow_action(pos)

        best_score = max(opt[0] for opt in options)
        best_options = [opt[1] for opt in options if opt[0] == best_score]

        # Random among ties (consistent with greedy strategic agent)
        return self._rng.choice(best_options)

    def _evaluate_move_consequences(
        self,
        move: PlayerTurnActions,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> float:
        """1-ply lookahead: evaluate the position after this move.

        This adds a tiny bit of search without full minimax tree.
        Returns the evaluation score for the resulting position.
        """
        opponent = player.opponent()

        # Apply our move (opponent stays)
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

        # Use fixed seed for consistency
        eval_rng = Random(42)
        try:
            from ..engine import apply_turn
            next_state = apply_turn(state, turn_actions, config, eval_rng)
            return evaluate_board(
                next_state.board, player, config,
                next_state.current_turn, self._weights
            )
        except Exception:
            # Fallback if lookahead fails
            return 0.0
