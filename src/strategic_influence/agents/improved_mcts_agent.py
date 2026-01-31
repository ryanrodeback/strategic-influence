"""ImprovedMCTSAgent: MCTS with heuristic rollouts.

Improvements over basic MonteCarloAgent:
1. Heuristic rollout policy (not random)
2. UCB1 for action selection with adaptive exploration
3. Better candidate generation
4. Early termination when clear winner emerges

The key insight: random rollouts dilute signal from good moves.
Using lightweight heuristics in rollouts preserves strategic information.

TUNING GUIDE:
- num_simulations: More = better estimates but slower (50-200 typical)
- exploration_c: Higher = explore more, lower = exploit more (1.0-2.0)
- rollout_smartness: 0.0=random, 1.0=fully heuristic
"""

import math
import time
from dataclasses import dataclass, field
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
from ..evaluation import is_position_threatened
from .common import center_aware_setup


@dataclass
class CandidateStats:
    """Statistics for a candidate move."""
    actions: PlayerTurnActions
    wins: float = 0  # Can be fractional (draws count as 0.5)
    simulations: int = 0

    @property
    def win_rate(self) -> float:
        if self.simulations == 0:
            return 0.0
        return self.wins / self.simulations

    def ucb_value(self, total_sims: int, exploration_c: float) -> float:
        """Calculate UCB1 value for this candidate."""
        if self.simulations == 0:
            return float('inf')  # Unexplored - high priority
        exploitation = self.wins / self.simulations
        exploration = exploration_c * math.sqrt(math.log(max(1, total_sims)) / self.simulations)
        return exploitation + exploration


class ImprovedMCTSAgent:
    """MCTS agent with heuristic rollout policy.

    Uses UCB1 to balance exploration/exploitation when allocating
    simulations across candidates.

    Rollout policy uses lightweight heuristics:
    - Attack when stronger
    - Expand when safe
    - Defend when threatened
    - Prefer SEND_HALF for flexibility

    Key parameters:
    - num_simulations: How many games to simulate (default 100)
    - exploration_c: UCB exploration constant (default 1.414 = sqrt(2))
    - rollout_smartness: 0.0=random, 1.0=heuristic (default 0.7)
    """

    def __init__(
        self,
        seed: int | None = None,
        num_simulations: int = 100,
        num_candidates: int = 15,
        exploration_c: float = 1.414,
        rollout_smartness: float = 0.7,  # How heuristic vs random the rollout is
        verbose: bool = False,
    ):
        self._initial_seed = seed
        self._rng = Random(seed)
        self._num_simulations = num_simulations
        self._num_candidates = num_candidates
        self._exploration_c = exploration_c
        self._rollout_smartness = rollout_smartness
        self._verbose = verbose
        self._last_search_time = 0.0

    @property
    def name(self) -> str:
        return f"ImprovedMCTS({self._num_simulations})"

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
        """Choose actions using improved MCTS."""
        start_time = time.time()

        candidates = self._generate_candidates(state, player, config)

        if not candidates:
            return self._all_stay(state, player)

        if len(candidates) == 1:
            return candidates[0].actions

        if self._verbose:
            print(f"  MCTS: {len(candidates)} candidates, {self._num_simulations} sims")

        # Run simulations using UCB1 to select which candidate to simulate
        total_sims = 0
        for _ in range(self._num_simulations):
            # Select candidate with highest UCB value
            best_candidate = max(
                candidates,
                key=lambda c: c.ucb_value(total_sims + 1, self._exploration_c)
            )

            # Run simulation
            result = self._simulate_game(
                state, player, best_candidate.actions, config
            )

            # Update statistics
            best_candidate.simulations += 1
            if result == player:
                best_candidate.wins += 1
            elif result is None:  # Draw - count as half win
                best_candidate.wins += 0.5

            total_sims += 1

            # Early termination: if one candidate is clearly better
            if total_sims >= 30 and self._should_terminate_early(candidates):
                break

        self._last_search_time = time.time() - start_time

        if self._verbose:
            best = max(candidates, key=lambda c: c.win_rate)
            print(f"  MCTS: {total_sims} sims in {self._last_search_time:.2f}s, best={best.win_rate:.1%}")

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

        # Sort by simulations
        sorted_cands = sorted(candidates, key=lambda c: c.simulations, reverse=True)
        best = sorted_cands[0]
        second = sorted_cands[1]

        if best.simulations < 10 or second.simulations < 5:
            return False

        # Best has 3x+ simulations with clear win rate advantage
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
                break  # Avoid infinite loop

        # Limit candidates
        if len(candidates) > self._num_candidates:
            # Keep first few (heuristic) plus random sample
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
        """Generate a random candidate with some heuristic bias."""
        actions = []

        for pos in state.board.positions_owned_by(player):
            territory = state.board.get(pos)
            stones = territory.stones
            neighbors = list(pos.neighbors(config.board_size))

            # Biased random: prefer SEND_HALF for expansion
            choice = self._rng.random()
            if choice < 0.4 or not neighbors:
                actions.append(create_grow_action(pos))
            elif choice < 0.75:
                # SEND_HALF (preferred)
                dest = self._rng.choice(neighbors)
                actions.append(create_simple_move_action(pos, dest, calculate_half(stones)))
            else:
                # SEND_ALL
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
        """Simulate game to completion using heuristic rollout."""
        opponent = player.opponent()
        current_state = state

        # Apply candidate move with heuristic opponent response
        if not current_state.is_complete:
            opp_actions = self._heuristic_actions(current_state, opponent, config)

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

        # Continue with heuristic play
        while not current_state.is_complete:
            p1_actions = self._heuristic_actions(current_state, Owner.PLAYER_1, config)
            p2_actions = self._heuristic_actions(current_state, Owner.PLAYER_2, config)

            turn_actions = TurnActions(
                player1_actions=p1_actions,
                player2_actions=p2_actions,
                turn_number=current_state.current_turn + 1,
            )

            sim_rng = Random(self._rng.randint(0, 2**31 - 1))
            current_state = apply_turn(current_state, turn_actions, config, sim_rng)

        return current_state.winner

    def _heuristic_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Generate actions using lightweight heuristics.

        This is the key improvement: instead of random play,
        use simple heuristics that approximate good strategy.
        """
        actions = []
        opponent = player.opponent()
        board = state.board

        # Calculate relative strength
        my_stones = board.total_stones(player)
        enemy_stones = board.total_stones(opponent)
        relative_strength = my_stones / max(1, enemy_stones)

        for pos in board.positions_owned_by(player):
            territory = board.get(pos)
            stones = territory.stones
            neighbors = list(pos.neighbors(config.board_size))

            if not neighbors:
                actions.append(create_grow_action(pos))
                continue

            action = self._choose_heuristic_action(
                pos, stones, neighbors, board, player, opponent,
                relative_strength, config
            )
            actions.append(action)

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _choose_heuristic_action(
        self,
        pos: Position,
        stones: int,
        neighbors: list[Position],
        board,
        player: Owner,
        opponent: Owner,
        relative_strength: float,
        config: GameConfig,
    ) -> TerritoryAction:
        """Choose action based on simple heuristics.

        The rollout_smartness parameter controls how heuristic vs random:
        - 0.0 = pure random
        - 1.0 = always follow heuristics
        """
        half_stones = calculate_half(stones)

        # With probability (1 - smartness), just pick randomly
        if self._rng.random() > self._rollout_smartness:
            # Random action
            choice = self._rng.random()
            if choice < 0.4 or not neighbors:
                return create_grow_action(pos)
            elif choice < 0.7:
                return create_simple_move_action(pos, self._rng.choice(neighbors), half_stones)
            else:
                return create_simple_move_action(pos, self._rng.choice(neighbors), stones)

        # Otherwise, use heuristics
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

        # Heuristic 1: Attack weaker enemies when strong
        if enemy_neighbors and relative_strength >= 1.0:
            attackable = [(n, s) for n, s in enemy_neighbors if stones > s]
            if attackable:
                target, enemy_stones = min(attackable, key=lambda x: x[1])
                # SEND_HALF if it can win (safer), SEND_ALL if needed
                if half_stones > enemy_stones:
                    return create_simple_move_action(pos, target, half_stones)
                elif stones > enemy_stones:
                    return create_simple_move_action(pos, target, stones)

        # Heuristic 2: Expand into neutral (prefer SEND_HALF - keeps territory)
        if neutral_neighbors:
            target = self._rng.choice(neutral_neighbors)
            # Almost always SEND_HALF for expansion (safe division principle)
            if self._rng.random() < 0.8:
                return create_simple_move_action(pos, target, half_stones)
            else:
                return create_simple_move_action(pos, target, stones)

        # Heuristic 3: Defend when weak and threatened
        is_threatened = bool(enemy_neighbors)
        if is_threatened and stones < 4:
            return create_grow_action(pos)

        # Heuristic 4: Reinforce threatened friendly
        if friendly_neighbors:
            threatened_friends = [
                (n, s) for n, s in friendly_neighbors
                if any(board.get_owner(nn) == opponent
                       for nn in n.neighbors(config.board_size))
            ]
            if threatened_friends:
                target = self._rng.choice([n for n, _ in threatened_friends])
                return create_simple_move_action(pos, target, half_stones)

        # Default: mostly stay and grow
        if self._rng.random() < 0.7:
            return create_grow_action(pos)
        elif neighbors:
            return create_simple_move_action(
                pos, self._rng.choice(neighbors), half_stones
            )
        else:
            return create_grow_action(pos)

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
