"""Monte Carlo simulation-based agent implementation.

V4: Simplified 3-option movement system with simulation-based evaluation.

This agent generates candidate moves using the 3-option system,
simulates random games from each candidate, and selects the move
with the highest win rate.
"""

from copy import deepcopy
from dataclasses import dataclass
from random import Random

from ..types import (
    Owner,
    Position,
    GameState,
    GamePhase,
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


@dataclass
class CandidateEvaluation:
    """Evaluation result for a candidate move."""
    actions: PlayerTurnActions
    wins: int
    simulations: int

    @property
    def win_rate(self) -> float:
        if self.simulations == 0:
            return 0.0
        return self.wins / self.simulations


class MonteCarloAgent:
    """Agent that uses Monte Carlo simulation with 3-option movement.

    Strategy:
    - Generate candidate moves using STAY/SEND_HALF/SEND_ALL options
    - For each candidate, simulate multiple random games
    - Select the candidate with the highest win rate
    """

    def __init__(
        self,
        seed: int | None = None,
        num_simulations: int = 50,
        num_candidates: int = 8,
    ):
        self._initial_seed = seed
        self._rng = Random(seed)
        self._num_simulations = num_simulations
        self._num_candidates = num_candidates

    @property
    def name(self) -> str:
        return f"MonteCarloBot({self._num_simulations})"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)

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
        best_distance = center_distance(valid_positions[0])
        best_positions = [
            p for p in valid_positions
            if center_distance(p) <= best_distance + 1
        ]

        return SetupAction(player=player, position=self._rng.choice(best_positions))

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose actions using Monte Carlo simulation."""
        candidates = self._generate_candidates(state, player, config)

        if not candidates:
            return self._create_all_stay_actions(state, player)

        if len(candidates) == 1:
            return candidates[0]

        # Evaluate each candidate
        best_evaluation: CandidateEvaluation | None = None

        for candidate in candidates:
            evaluation = self._evaluate_candidate(
                state, player, candidate, config
            )

            if best_evaluation is None or evaluation.win_rate > best_evaluation.win_rate:
                best_evaluation = evaluation

        return best_evaluation.actions if best_evaluation else candidates[0]

    def _generate_candidates(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> list[PlayerTurnActions]:
        """Generate diverse candidate moves using 3-option system."""
        candidates: list[PlayerTurnActions] = []
        owned_positions = list(state.board.positions_owned_by(player))

        if not owned_positions:
            return []

        opponent = player.opponent()

        # Candidate 1: All stay (defensive)
        candidates.append(self._create_all_stay_actions(state, player))

        # Generate candidates for each territory
        for pos in owned_positions:
            territory = state.board.get(pos)
            stones = territory.stones
            half_stones = calculate_half(stones)
            neighbors = list(pos.neighbors(config.board_size))

            for neighbor in neighbors:
                neighbor_territory = state.board.get(neighbor)

                # SEND_HALF to this neighbor (others stay)
                candidate = self._create_single_action_candidate(
                    state, player, pos, neighbor, half_stones, config
                )
                if candidate not in candidates:
                    candidates.append(candidate)

                # SEND_ALL to enemy or valuable neutral (others stay)
                if neighbor_territory.owner == opponent or (
                    neighbor_territory.owner == Owner.NEUTRAL
                ):
                    candidate = self._create_single_action_candidate(
                        state, player, pos, neighbor, stones, config
                    )
                    if candidate not in candidates:
                        candidates.append(candidate)

        # Add random candidates if we have room
        while len(candidates) < self._num_candidates:
            random_candidate = self._create_random_candidate(state, player, config)
            if random_candidate not in candidates:
                candidates.append(random_candidate)
            else:
                break

        # Limit to num_candidates
        if len(candidates) > self._num_candidates:
            heuristic_count = max(4, self._num_candidates // 2)
            heuristic_candidates = candidates[:heuristic_count]
            remaining = candidates[heuristic_count:]
            self._rng.shuffle(remaining)
            candidates = heuristic_candidates + remaining[:self._num_candidates - heuristic_count]

        return candidates

    def _create_all_stay_actions(
        self,
        state: GameState,
        player: Owner,
    ) -> PlayerTurnActions:
        """Create actions where all territories stay and grow."""
        actions = []
        for pos in state.board.positions_owned_by(player):
            actions.append(create_grow_action(pos))
        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _create_single_action_candidate(
        self,
        state: GameState,
        player: Owner,
        source: Position,
        destination: Position,
        stones: int,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Create candidate where one territory moves, others stay."""
        actions = []
        for pos in state.board.positions_owned_by(player):
            if pos == source:
                actions.append(create_simple_move_action(pos, destination, stones))
            else:
                actions.append(create_grow_action(pos))
        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _create_random_candidate(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Create a random candidate using 3-option system."""
        actions = []

        for pos in state.board.positions_owned_by(player):
            territory = state.board.get(pos)
            stones = territory.stones
            neighbors = list(pos.neighbors(config.board_size))

            # Random choice: STAY, SEND_HALF, or SEND_ALL
            choice = self._rng.random()
            if choice < 0.4 or not neighbors:
                # STAY (40% or no neighbors)
                actions.append(create_grow_action(pos))
            elif choice < 0.7:
                # SEND_HALF (30%)
                dest = self._rng.choice(neighbors)
                half_stones = calculate_half(stones)
                actions.append(create_simple_move_action(pos, dest, half_stones))
            else:
                # SEND_ALL (30%)
                dest = self._rng.choice(neighbors)
                actions.append(create_simple_move_action(pos, dest, stones))

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _evaluate_candidate(
        self,
        state: GameState,
        player: Owner,
        candidate: PlayerTurnActions,
        config: GameConfig,
    ) -> CandidateEvaluation:
        """Evaluate a candidate via Monte Carlo simulation."""
        wins = 0

        for _ in range(self._num_simulations):
            sim_seed = self._rng.randint(0, 2**31 - 1)
            sim_rng = Random(sim_seed)

            result = self._simulate_random_game(
                state, player, candidate, config, sim_rng
            )

            if result == player:
                wins += 1

        return CandidateEvaluation(
            actions=candidate,
            wins=wins,
            simulations=self._num_simulations,
        )

    def _simulate_random_game(
        self,
        state: GameState,
        player: Owner,
        candidate: PlayerTurnActions,
        config: GameConfig,
        rng: Random,
    ) -> Owner | None:
        """Simulate a game to completion with random play."""
        opponent = player.opponent()
        current_state = state

        # Apply the candidate move with random opponent move
        if current_state.phase == GamePhase.PLAYING and not current_state.is_complete:
            opponent_actions = self._random_actions(current_state, opponent, config, rng)

            if player == Owner.PLAYER_1:
                turn_actions = TurnActions(
                    player1_actions=candidate,
                    player2_actions=opponent_actions,
                    turn_number=current_state.current_turn + 1,
                )
            else:
                turn_actions = TurnActions(
                    player1_actions=opponent_actions,
                    player2_actions=candidate,
                    turn_number=current_state.current_turn + 1,
                )

            current_state = apply_turn(current_state, turn_actions, config, rng)

        # Continue with random play
        while not current_state.is_complete:
            p1_actions = self._random_actions(current_state, Owner.PLAYER_1, config, rng)
            p2_actions = self._random_actions(current_state, Owner.PLAYER_2, config, rng)

            turn_actions = TurnActions(
                player1_actions=p1_actions,
                player2_actions=p2_actions,
                turn_number=current_state.current_turn + 1,
            )

            current_state = apply_turn(current_state, turn_actions, config, rng)

        return current_state.winner

    def _random_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
        rng: Random,
    ) -> PlayerTurnActions:
        """Generate random actions using 3-option system."""
        actions = []

        for pos in state.board.positions_owned_by(player):
            territory = state.board.get(pos)
            stones = territory.stones
            neighbors = list(pos.neighbors(config.board_size))

            choice = rng.random()
            if choice < 0.35 or not neighbors:
                # STAY
                actions.append(create_grow_action(pos))
            elif choice < 0.65:
                # SEND_HALF
                dest = rng.choice(neighbors)
                half_stones = calculate_half(stones)
                actions.append(create_simple_move_action(pos, dest, half_stones))
            else:
                # SEND_ALL
                dest = rng.choice(neighbors)
                actions.append(create_simple_move_action(pos, dest, stones))

        return PlayerTurnActions(player=player, actions=tuple(actions))
