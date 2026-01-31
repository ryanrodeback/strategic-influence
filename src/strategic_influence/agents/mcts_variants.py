"""MCTS Variants: Different evaluation strategies for MCTS.

This module explores improvements to MCTS by replacing random rollouts with:
1. MCTSHeuristicEval: Uses heuristic evaluation function (depth-0 minimax)
2. MCTSMinimaxEval: Uses shallow minimax search (depth-1) at leaf nodes
3. MCTSHeuristicRollout: Uses heuristic-guided rollouts (greedy moves)

The goal is to replace random rollout bias with strategic signal.
"""

import math
import time
from dataclasses import dataclass
from random import Random

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


@dataclass
class CandidateStats:
    """Statistics for a candidate move."""
    actions: PlayerTurnActions
    wins: float = 0  # Can be fractional (draws count as 0.5)
    total_value: float = 0.0  # For storing evaluation scores
    simulations: int = 0

    @property
    def win_rate(self) -> float:
        if self.simulations == 0:
            return 0.0
        return self.wins / self.simulations

    @property
    def avg_value(self) -> float:
        if self.simulations == 0:
            return 0.0
        return self.total_value / self.simulations

    def ucb_value(self, total_sims: int, exploration_c: float) -> float:
        """Calculate UCB1 value for this candidate."""
        if self.simulations == 0:
            return float('inf')  # Unexplored - high priority
        exploitation = self.wins / self.simulations
        exploration = exploration_c * math.sqrt(math.log(max(1, total_sims)) / self.simulations)
        return exploitation + exploration


class MCTSHeuristicEval:
    """MCTS with heuristic evaluation at leaf nodes (depth-0 minimax).

    Instead of random rollouts, uses a heuristic evaluation function
    to estimate board value at leaf nodes. This provides immediate
    strategic signal about position quality.

    The evaluation function scores based on:
    - Territory count
    - Stone count
    - Territory threats
    - Expansion potential
    """

    def __init__(
        self,
        seed: int | None = None,
        num_simulations: int = 100,
        num_candidates: int = 15,
        exploration_c: float = 1.414,
        weights: EvaluationWeights | None = None,
        verbose: bool = False,
    ):
        self._initial_seed = seed
        self._rng = Random(seed)
        self._num_simulations = num_simulations
        self._num_candidates = num_candidates
        self._exploration_c = exploration_c
        self._weights = weights or BALANCED_WEIGHTS
        self._verbose = verbose
        self._last_search_time = 0.0

    @property
    def name(self) -> str:
        return f"MCTSHeuristic({self._num_simulations})"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)

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
        """Choose actions using MCTS with heuristic evaluation."""
        start_time = time.time()

        candidates = self._generate_candidates(state, player, config)

        if not candidates:
            return self._all_stay(state, player)

        if len(candidates) == 1:
            return candidates[0].actions

        if self._verbose:
            print(f"  MCTSHeuristic: {len(candidates)} candidates, {self._num_simulations} sims")

        # Run simulations using UCB1
        total_sims = 0
        for _ in range(self._num_simulations):
            # Select candidate with highest UCB value
            best_candidate = max(
                candidates,
                key=lambda c: c.ucb_value(total_sims + 1, self._exploration_c)
            )

            # Run simulation with heuristic evaluation
            result = self._simulate_with_eval(
                state, player, best_candidate.actions, config
            )

            # Update statistics (convert evaluation to win/loss)
            best_candidate.simulations += 1
            best_candidate.total_value += result
            if result > 0.5:
                best_candidate.wins += 1
            elif result == 0.5:
                best_candidate.wins += 0.5

            total_sims += 1

            # Early termination
            if total_sims >= 30 and self._should_terminate_early(candidates):
                break

        self._last_search_time = time.time() - start_time

        if self._verbose:
            best = max(candidates, key=lambda c: c.win_rate)
            print(f"  MCTSHeuristic: {total_sims} sims in {self._last_search_time:.2f}s, best={best.win_rate:.1%}")

        # Return candidate with highest win rate
        best = max(candidates, key=lambda c: c.win_rate)
        return best.actions

    def get_stats(self) -> dict:
        """Get statistics from last search."""
        return {
            "search_time": self._last_search_time,
            "simulations": self._num_simulations,
        }

    def _should_terminate_early(self, candidates: list[CandidateStats]) -> bool:
        """Check if we can stop early due to clear winner."""
        if len(candidates) < 2:
            return True

        sorted_cands = sorted(candidates, key=lambda c: c.simulations, reverse=True)
        best = sorted_cands[0]
        second = sorted_cands[1]

        if best.simulations < 10 or second.simulations < 5:
            return False

        if best.simulations >= second.simulations * 3:
            if best.win_rate > second.win_rate + 0.15:
                return True

        return False

    def _generate_candidates(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> list[CandidateStats]:
        """Generate diverse candidate moves."""
        candidates: list[CandidateStats] = []
        owned = list(state.board.positions_owned_by(player))

        if not owned:
            return []

        opponent = player.opponent()
        board = state.board

        # Candidate 1: All stay (defensive baseline)
        all_stay = self._all_stay(state, player)
        candidates.append(CandidateStats(actions=all_stay))

        # Generate targeted candidates for each territory
        for pos in owned:
            territory = board.get(pos)
            stones = territory.stones
            half_stones = calculate_half(stones)
            neighbors = list(pos.neighbors(config.board_size))

            for neighbor in neighbors:
                neighbor_owner = board.get_owner(neighbor)
                neighbor_stones = board.get_stones(neighbor) if neighbor_owner != Owner.NEUTRAL else 0

                # SEND_HALF expansion/attack
                cand = self._single_action_candidate(
                    state, player, pos, neighbor, half_stones, config
                )
                if cand not in [c.actions for c in candidates]:
                    candidates.append(CandidateStats(actions=cand))

                # SEND_ALL for strong attacks or full expansion
                if neighbor_owner == opponent or neighbor_owner == Owner.NEUTRAL:
                    cand = self._single_action_candidate(
                        state, player, pos, neighbor, stones, config
                    )
                    if cand not in [c.actions for c in candidates]:
                        candidates.append(CandidateStats(actions=cand))

        # Add random candidates to fill remaining slots
        while len(candidates) < self._num_candidates:
            random_cand = self._random_candidate(state, player, config)
            if random_cand not in [c.actions for c in candidates]:
                candidates.append(CandidateStats(actions=random_cand))
            else:
                break

        # Limit candidates
        if len(candidates) > self._num_candidates:
            heuristic_count = max(4, self._num_candidates // 2)
            keep = candidates[:heuristic_count]
            remaining = candidates[heuristic_count:]
            self._rng.shuffle(remaining)
            candidates = keep + remaining[:self._num_candidates - heuristic_count]

        return candidates

    def _single_action_candidate(
        self,
        state: GameState,
        player: Owner,
        source: Position,
        dest: Position,
        stones: int,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Create candidate where one territory moves, others stay."""
        actions = []
        for pos in state.board.positions_owned_by(player):
            if pos == source:
                actions.append(create_simple_move_action(pos, dest, stones))
            else:
                actions.append(create_grow_action(pos))
        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _random_candidate(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Generate a random candidate."""
        actions = []

        for pos in state.board.positions_owned_by(player):
            territory = state.board.get(pos)
            stones = territory.stones
            neighbors = list(pos.neighbors(config.board_size))

            choice = self._rng.random()
            if choice < 0.4 or not neighbors:
                actions.append(create_grow_action(pos))
            elif choice < 0.75:
                dest = self._rng.choice(neighbors)
                actions.append(create_simple_move_action(pos, dest, calculate_half(stones)))
            else:
                dest = self._rng.choice(neighbors)
                actions.append(create_simple_move_action(pos, dest, stones))

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _simulate_with_eval(
        self,
        state: GameState,
        player: Owner,
        candidate: PlayerTurnActions,
        config: GameConfig,
    ) -> float:
        """Simulate one step with candidate, then evaluate board heuristically.

        Returns normalized evaluation: 1.0 = win, 0.5 = draw, 0.0 = loss
        """
        opponent = player.opponent()

        # Apply candidate move with greedy opponent response
        if not state.is_complete:
            opp_actions = self._greedy_actions(state, opponent, config)

            if player == Owner.PLAYER_1:
                turn_actions = TurnActions(
                    player1_actions=candidate,
                    player2_actions=opp_actions,
                    turn_number=state.current_turn + 1,
                )
            else:
                turn_actions = TurnActions(
                    player1_actions=opp_actions,
                    player2_actions=candidate,
                    turn_number=state.current_turn + 1,
                )

            sim_rng = Random(self._rng.randint(0, 2**31 - 1))
            current_state = apply_turn(state, turn_actions, config, sim_rng)
        else:
            current_state = state

        # Evaluate the resulting board
        if current_state.is_complete:
            # Game ended - return actual result
            if current_state.winner == player:
                return 1.0
            elif current_state.winner is None:
                return 0.5
            else:
                return 0.0
        else:
            # Evaluate board heuristically
            eval_score = evaluate_board(
                current_state.board, player, config,
                current_state.current_turn, self._weights
            )
            # Normalize to [0, 1] range (eval_score ranges roughly [-1, 1])
            return (eval_score + 1.0) / 2.0

    def _greedy_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Generate actions using greedy heuristic strategy."""
        actions = []
        opponent = player.opponent()
        board = state.board

        for pos in board.positions_owned_by(player):
            territory = board.get(pos)
            stones = territory.stones
            neighbors = list(pos.neighbors(config.board_size))

            if not neighbors:
                actions.append(create_grow_action(pos))
                continue

            action = self._choose_greedy_action(
                pos, stones, neighbors, board, player, opponent, config
            )
            actions.append(action)

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _choose_greedy_action(
        self,
        pos: Position,
        stones: int,
        neighbors: list[Position],
        board,
        player: Owner,
        opponent: Owner,
        config: GameConfig,
    ) -> TerritoryAction:
        """Choose greedy action based on simple scoring."""
        half_stones = calculate_half(stones)

        # Categorize neighbors
        enemy_neighbors = []
        neutral_neighbors = []
        friendly_neighbors = []

        for n in neighbors:
            owner = board.get_owner(n)
            if owner == opponent:
                enemy_neighbors.append((n, board.get_stones(n)))
            elif owner == Owner.NEUTRAL:
                neutral_neighbors.append(n)
            else:
                friendly_neighbors.append((n, board.get_stones(n)))

        # Score all valid options
        options: list[tuple[float, TerritoryAction]] = []

        # STAY/GROW (baseline)
        options.append((10.0, create_grow_action(pos)))

        # Attack enemy if stronger
        for enemy_pos, enemy_stones in enemy_neighbors:
            if half_stones > enemy_stones:
                options.append((100.0, create_simple_move_action(pos, enemy_pos, half_stones)))
            elif stones > enemy_stones:
                options.append((95.0, create_simple_move_action(pos, enemy_pos, stones)))

        # Expand into neutral (prefer SEND_HALF)
        for neutral_pos in neutral_neighbors:
            neutral_neighbors_count = sum(
                1 for nn in neutral_pos.neighbors(config.board_size)
                if board.get_owner(nn) == Owner.NEUTRAL
            )
            score = 200.0 + neutral_neighbors_count * 30.0
            options.append((score, create_simple_move_action(pos, neutral_pos, half_stones)))

        # Defend by growing if threatened
        if enemy_neighbors and stones < 4:
            options.append((50.0, create_grow_action(pos)))

        # Pick highest scored option
        options.sort(key=lambda x: x[0], reverse=True)
        return options[0][1]

    def _all_stay(
        self,
        state: GameState,
        player: Owner,
    ) -> PlayerTurnActions:
        """Create all-stay actions."""
        actions = [
            create_grow_action(pos)
            for pos in state.board.positions_owned_by(player)
        ]
        return PlayerTurnActions(player=player, actions=tuple(actions))


class MCTSMinimaxEval:
    """MCTS with minimax depth-1 evaluation at leaf nodes.

    Uses shallow minimax search (depth 1) to evaluate candidate moves.
    This provides better lookahead than immediate heuristic evaluation
    while remaining fast.
    """

    def __init__(
        self,
        seed: int | None = None,
        num_simulations: int = 100,
        num_candidates: int = 15,
        exploration_c: float = 1.414,
        weights: EvaluationWeights | None = None,
        verbose: bool = False,
    ):
        self._initial_seed = seed
        self._rng = Random(seed)
        self._num_simulations = num_simulations
        self._num_candidates = num_candidates
        self._exploration_c = exploration_c
        self._weights = weights or BALANCED_WEIGHTS
        self._verbose = verbose
        self._last_search_time = 0.0

    @property
    def name(self) -> str:
        return f"MCTSMinimax({self._num_simulations})"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)

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
        """Choose actions using MCTS with minimax depth-1 evaluation."""
        start_time = time.time()

        candidates = self._generate_candidates(state, player, config)

        if not candidates:
            return self._all_stay(state, player)

        if len(candidates) == 1:
            return candidates[0].actions

        if self._verbose:
            print(f"  MCTSMinimax: {len(candidates)} candidates, {self._num_simulations} sims")

        # Run simulations using UCB1
        total_sims = 0
        for _ in range(self._num_simulations):
            best_candidate = max(
                candidates,
                key=lambda c: c.ucb_value(total_sims + 1, self._exploration_c)
            )

            # Evaluate with depth-1 minimax
            result = self._eval_with_depth1_minimax(
                state, player, best_candidate.actions, config
            )

            # Update statistics
            best_candidate.simulations += 1
            best_candidate.total_value += result
            if result > 0.5:
                best_candidate.wins += 1
            elif result == 0.5:
                best_candidate.wins += 0.5

            total_sims += 1

            if total_sims >= 30 and self._should_terminate_early(candidates):
                break

        self._last_search_time = time.time() - start_time

        if self._verbose:
            best = max(candidates, key=lambda c: c.win_rate)
            print(f"  MCTSMinimax: {total_sims} sims in {self._last_search_time:.2f}s, best={best.win_rate:.1%}")

        best = max(candidates, key=lambda c: c.win_rate)
        return best.actions

    def get_stats(self) -> dict:
        """Get statistics from last search."""
        return {
            "search_time": self._last_search_time,
            "simulations": self._num_simulations,
        }

    def _should_terminate_early(self, candidates: list[CandidateStats]) -> bool:
        """Check if we can stop early due to clear winner."""
        if len(candidates) < 2:
            return True

        sorted_cands = sorted(candidates, key=lambda c: c.simulations, reverse=True)
        best = sorted_cands[0]
        second = sorted_cands[1]

        if best.simulations < 10 or second.simulations < 5:
            return False

        if best.simulations >= second.simulations * 3:
            if best.win_rate > second.win_rate + 0.15:
                return True

        return False

    def _generate_candidates(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> list[CandidateStats]:
        """Generate diverse candidate moves."""
        candidates: list[CandidateStats] = []
        owned = list(state.board.positions_owned_by(player))

        if not owned:
            return []

        opponent = player.opponent()
        board = state.board

        all_stay = self._all_stay(state, player)
        candidates.append(CandidateStats(actions=all_stay))

        for pos in owned:
            territory = board.get(pos)
            stones = territory.stones
            half_stones = calculate_half(stones)
            neighbors = list(pos.neighbors(config.board_size))

            for neighbor in neighbors:
                neighbor_owner = board.get_owner(neighbor)
                neighbor_stones = board.get_stones(neighbor) if neighbor_owner != Owner.NEUTRAL else 0

                cand = self._single_action_candidate(
                    state, player, pos, neighbor, half_stones, config
                )
                if cand not in [c.actions for c in candidates]:
                    candidates.append(CandidateStats(actions=cand))

                if neighbor_owner == opponent or neighbor_owner == Owner.NEUTRAL:
                    cand = self._single_action_candidate(
                        state, player, pos, neighbor, stones, config
                    )
                    if cand not in [c.actions for c in candidates]:
                        candidates.append(CandidateStats(actions=cand))

        while len(candidates) < self._num_candidates:
            random_cand = self._random_candidate(state, player, config)
            if random_cand not in [c.actions for c in candidates]:
                candidates.append(CandidateStats(actions=random_cand))
            else:
                break

        if len(candidates) > self._num_candidates:
            heuristic_count = max(4, self._num_candidates // 2)
            keep = candidates[:heuristic_count]
            remaining = candidates[heuristic_count:]
            self._rng.shuffle(remaining)
            candidates = keep + remaining[:self._num_candidates - heuristic_count]

        return candidates

    def _single_action_candidate(
        self,
        state: GameState,
        player: Owner,
        source: Position,
        dest: Position,
        stones: int,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Create candidate where one territory moves, others stay."""
        actions = []
        for pos in state.board.positions_owned_by(player):
            if pos == source:
                actions.append(create_simple_move_action(pos, dest, stones))
            else:
                actions.append(create_grow_action(pos))
        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _random_candidate(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Generate a random candidate."""
        actions = []

        for pos in state.board.positions_owned_by(player):
            territory = state.board.get(pos)
            stones = territory.stones
            neighbors = list(pos.neighbors(config.board_size))

            choice = self._rng.random()
            if choice < 0.4 or not neighbors:
                actions.append(create_grow_action(pos))
            elif choice < 0.75:
                dest = self._rng.choice(neighbors)
                actions.append(create_simple_move_action(pos, dest, calculate_half(stones)))
            else:
                dest = self._rng.choice(neighbors)
                actions.append(create_simple_move_action(pos, dest, stones))

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _eval_with_depth1_minimax(
        self,
        state: GameState,
        player: Owner,
        candidate: PlayerTurnActions,
        config: GameConfig,
    ) -> float:
        """Evaluate candidate using depth-1 minimax search.

        We play our candidate move, then consider opponent's best response,
        and evaluate the resulting position.
        """
        opponent = player.opponent()

        # Apply our candidate move
        if not state.is_complete:
            # Get opponent's best greedy response
            opp_actions = self._greedy_actions(state, opponent, config)

            if player == Owner.PLAYER_1:
                turn_actions = TurnActions(
                    player1_actions=candidate,
                    player2_actions=opp_actions,
                    turn_number=state.current_turn + 1,
                )
            else:
                turn_actions = TurnActions(
                    player1_actions=opp_actions,
                    player2_actions=candidate,
                    turn_number=state.current_turn + 1,
                )

            eval_rng = Random(42)  # Fixed seed for consistency
            current_state = apply_turn(state, turn_actions, config, eval_rng)
        else:
            current_state = state

        # Check for game end
        if current_state.is_complete:
            if current_state.winner == player:
                return 1.0
            elif current_state.winner is None:
                return 0.5
            else:
                return 0.0
        else:
            # Evaluate the position
            eval_score = evaluate_board(
                current_state.board, player, config,
                current_state.current_turn, self._weights
            )
            return (eval_score + 1.0) / 2.0

    def _greedy_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Generate greedy actions."""
        actions = []
        opponent = player.opponent()
        board = state.board

        for pos in board.positions_owned_by(player):
            territory = board.get(pos)
            stones = territory.stones
            neighbors = list(pos.neighbors(config.board_size))

            if not neighbors:
                actions.append(create_grow_action(pos))
                continue

            action = self._choose_greedy_action(
                pos, stones, neighbors, board, player, opponent, config
            )
            actions.append(action)

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _choose_greedy_action(
        self,
        pos: Position,
        stones: int,
        neighbors: list[Position],
        board,
        player: Owner,
        opponent: Owner,
        config: GameConfig,
    ) -> TerritoryAction:
        """Choose greedy action."""
        half_stones = calculate_half(stones)

        enemy_neighbors = []
        neutral_neighbors = []
        friendly_neighbors = []

        for n in neighbors:
            owner = board.get_owner(n)
            if owner == opponent:
                enemy_neighbors.append((n, board.get_stones(n)))
            elif owner == Owner.NEUTRAL:
                neutral_neighbors.append(n)
            else:
                friendly_neighbors.append((n, board.get_stones(n)))

        options: list[tuple[float, TerritoryAction]] = []

        options.append((10.0, create_grow_action(pos)))

        for enemy_pos, enemy_stones in enemy_neighbors:
            if half_stones > enemy_stones:
                options.append((100.0, create_simple_move_action(pos, enemy_pos, half_stones)))
            elif stones > enemy_stones:
                options.append((95.0, create_simple_move_action(pos, enemy_pos, stones)))

        for neutral_pos in neutral_neighbors:
            neutral_neighbors_count = sum(
                1 for nn in neutral_pos.neighbors(config.board_size)
                if board.get_owner(nn) == Owner.NEUTRAL
            )
            score = 200.0 + neutral_neighbors_count * 30.0
            options.append((score, create_simple_move_action(pos, neutral_pos, half_stones)))

        if enemy_neighbors and stones < 4:
            options.append((50.0, create_grow_action(pos)))

        options.sort(key=lambda x: x[0], reverse=True)
        return options[0][1]

    def _all_stay(
        self,
        state: GameState,
        player: Owner,
    ) -> PlayerTurnActions:
        """Create all-stay actions."""
        actions = [
            create_grow_action(pos)
            for pos in state.board.positions_owned_by(player)
        ]
        return PlayerTurnActions(player=player, actions=tuple(actions))


class MCTSHeuristicRollout:
    """MCTS with heuristic-guided rollouts.

    Similar to ImprovedMCTSAgent but uses pure greedy strategy
    for rollouts instead of weighted random. Tests whether
    fully deterministic heuristic rollouts help MCTS.
    """

    def __init__(
        self,
        seed: int | None = None,
        num_simulations: int = 100,
        num_candidates: int = 15,
        exploration_c: float = 1.414,
        verbose: bool = False,
    ):
        self._initial_seed = seed
        self._rng = Random(seed)
        self._num_simulations = num_simulations
        self._num_candidates = num_candidates
        self._exploration_c = exploration_c
        self._verbose = verbose
        self._last_search_time = 0.0

    @property
    def name(self) -> str:
        return f"MCTSHeuristicRollout({self._num_simulations})"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)

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
        """Choose actions using MCTS with pure heuristic rollouts."""
        start_time = time.time()

        candidates = self._generate_candidates(state, player, config)

        if not candidates:
            return self._all_stay(state, player)

        if len(candidates) == 1:
            return candidates[0].actions

        if self._verbose:
            print(f"  MCTSHeuristicRollout: {len(candidates)} candidates, {self._num_simulations} sims")

        total_sims = 0
        for _ in range(self._num_simulations):
            best_candidate = max(
                candidates,
                key=lambda c: c.ucb_value(total_sims + 1, self._exploration_c)
            )

            # Simulate game to completion using pure greedy rollout
            result = self._simulate_game(
                state, player, best_candidate.actions, config
            )

            best_candidate.simulations += 1
            if result == player:
                best_candidate.wins += 1
            elif result is None:
                best_candidate.wins += 0.5

            total_sims += 1

            if total_sims >= 30 and self._should_terminate_early(candidates):
                break

        self._last_search_time = time.time() - start_time

        if self._verbose:
            best = max(candidates, key=lambda c: c.win_rate)
            print(f"  MCTSHeuristicRollout: {total_sims} sims in {self._last_search_time:.2f}s, best={best.win_rate:.1%}")

        best = max(candidates, key=lambda c: c.win_rate)
        return best.actions

    def get_stats(self) -> dict:
        """Get statistics from last search."""
        return {
            "search_time": self._last_search_time,
            "simulations": self._num_simulations,
        }

    def _should_terminate_early(self, candidates: list[CandidateStats]) -> bool:
        """Check if we can stop early."""
        if len(candidates) < 2:
            return True

        sorted_cands = sorted(candidates, key=lambda c: c.simulations, reverse=True)
        best = sorted_cands[0]
        second = sorted_cands[1]

        if best.simulations < 10 or second.simulations < 5:
            return False

        if best.simulations >= second.simulations * 3:
            if best.win_rate > second.win_rate + 0.15:
                return True

        return False

    def _generate_candidates(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> list[CandidateStats]:
        """Generate diverse candidate moves."""
        candidates: list[CandidateStats] = []
        owned = list(state.board.positions_owned_by(player))

        if not owned:
            return []

        opponent = player.opponent()
        board = state.board

        all_stay = self._all_stay(state, player)
        candidates.append(CandidateStats(actions=all_stay))

        for pos in owned:
            territory = board.get(pos)
            stones = territory.stones
            half_stones = calculate_half(stones)
            neighbors = list(pos.neighbors(config.board_size))

            for neighbor in neighbors:
                neighbor_owner = board.get_owner(neighbor)
                neighbor_stones = board.get_stones(neighbor) if neighbor_owner != Owner.NEUTRAL else 0

                cand = self._single_action_candidate(
                    state, player, pos, neighbor, half_stones, config
                )
                if cand not in [c.actions for c in candidates]:
                    candidates.append(CandidateStats(actions=cand))

                if neighbor_owner == opponent or neighbor_owner == Owner.NEUTRAL:
                    cand = self._single_action_candidate(
                        state, player, pos, neighbor, stones, config
                    )
                    if cand not in [c.actions for c in candidates]:
                        candidates.append(CandidateStats(actions=cand))

        while len(candidates) < self._num_candidates:
            random_cand = self._random_candidate(state, player, config)
            if random_cand not in [c.actions for c in candidates]:
                candidates.append(CandidateStats(actions=random_cand))
            else:
                break

        if len(candidates) > self._num_candidates:
            heuristic_count = max(4, self._num_candidates // 2)
            keep = candidates[:heuristic_count]
            remaining = candidates[heuristic_count:]
            self._rng.shuffle(remaining)
            candidates = keep + remaining[:self._num_candidates - heuristic_count]

        return candidates

    def _single_action_candidate(
        self,
        state: GameState,
        player: Owner,
        source: Position,
        dest: Position,
        stones: int,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Create candidate where one territory moves, others stay."""
        actions = []
        for pos in state.board.positions_owned_by(player):
            if pos == source:
                actions.append(create_simple_move_action(pos, dest, stones))
            else:
                actions.append(create_grow_action(pos))
        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _random_candidate(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Generate a random candidate."""
        actions = []

        for pos in state.board.positions_owned_by(player):
            territory = state.board.get(pos)
            stones = territory.stones
            neighbors = list(pos.neighbors(config.board_size))

            choice = self._rng.random()
            if choice < 0.4 or not neighbors:
                actions.append(create_grow_action(pos))
            elif choice < 0.75:
                dest = self._rng.choice(neighbors)
                actions.append(create_simple_move_action(pos, dest, calculate_half(stones)))
            else:
                dest = self._rng.choice(neighbors)
                actions.append(create_simple_move_action(pos, dest, stones))

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _simulate_game(
        self,
        state: GameState,
        player: Owner,
        candidate: PlayerTurnActions,
        config: GameConfig,
    ) -> Owner | None:
        """Simulate game to completion using pure greedy play."""
        opponent = player.opponent()
        current_state = state

        # Apply candidate move with greedy opponent response
        if not current_state.is_complete:
            opp_actions = self._greedy_actions(current_state, opponent, config)

            if player == Owner.PLAYER_1:
                turn_actions = TurnActions(
                    player1_actions=candidate,
                    player2_actions=opp_actions,
                    turn_number=current_state.current_turn + 1,
                )
            else:
                turn_actions = TurnActions(
                    player1_actions=opp_actions,
                    player2_actions=candidate,
                    turn_number=current_state.current_turn + 1,
                )

            sim_rng = Random(self._rng.randint(0, 2**31 - 1))
            current_state = apply_turn(current_state, turn_actions, config, sim_rng)

        # Continue with greedy play
        while not current_state.is_complete:
            p1_actions = self._greedy_actions(current_state, Owner.PLAYER_1, config)
            p2_actions = self._greedy_actions(current_state, Owner.PLAYER_2, config)

            turn_actions = TurnActions(
                player1_actions=p1_actions,
                player2_actions=p2_actions,
                turn_number=current_state.current_turn + 1,
            )

            sim_rng = Random(self._rng.randint(0, 2**31 - 1))
            current_state = apply_turn(current_state, turn_actions, config, sim_rng)

        return current_state.winner

    def _greedy_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Generate pure greedy actions for a player."""
        actions = []
        opponent = player.opponent()
        board = state.board

        for pos in board.positions_owned_by(player):
            territory = board.get(pos)
            stones = territory.stones
            neighbors = list(pos.neighbors(config.board_size))

            if not neighbors:
                actions.append(create_grow_action(pos))
                continue

            action = self._choose_greedy_action(
                pos, stones, neighbors, board, player, opponent, config
            )
            actions.append(action)

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _choose_greedy_action(
        self,
        pos: Position,
        stones: int,
        neighbors: list[Position],
        board,
        player: Owner,
        opponent: Owner,
        config: GameConfig,
    ) -> TerritoryAction:
        """Choose the best greedy action for a territory."""
        half_stones = calculate_half(stones)

        enemy_neighbors = []
        neutral_neighbors = []
        friendly_neighbors = []

        for n in neighbors:
            owner = board.get_owner(n)
            if owner == opponent:
                enemy_neighbors.append((n, board.get_stones(n)))
            elif owner == Owner.NEUTRAL:
                neutral_neighbors.append(n)
            else:
                friendly_neighbors.append((n, board.get_stones(n)))

        options: list[tuple[float, TerritoryAction]] = []

        options.append((10.0, create_grow_action(pos)))

        for enemy_pos, enemy_stones in enemy_neighbors:
            if half_stones > enemy_stones:
                options.append((100.0, create_simple_move_action(pos, enemy_pos, half_stones)))
            elif stones > enemy_stones:
                options.append((95.0, create_simple_move_action(pos, enemy_pos, stones)))

        for neutral_pos in neutral_neighbors:
            neutral_neighbors_count = sum(
                1 for nn in neutral_pos.neighbors(config.board_size)
                if board.get_owner(nn) == Owner.NEUTRAL
            )
            score = 200.0 + neutral_neighbors_count * 30.0
            options.append((score, create_simple_move_action(pos, neutral_pos, half_stones)))

        if enemy_neighbors and stones < 4:
            options.append((50.0, create_grow_action(pos)))

        options.sort(key=lambda x: x[0], reverse=True)
        return options[0][1]

    def _all_stay(
        self,
        state: GameState,
        player: Owner,
    ) -> PlayerTurnActions:
        """Create all-stay actions."""
        actions = [
            create_grow_action(pos)
            for pos in state.board.positions_owned_by(player)
        ]
        return PlayerTurnActions(player=player, actions=tuple(actions))
