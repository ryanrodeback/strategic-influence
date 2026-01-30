"""Strategic/Balanced heuristic agent implementation.

V4: Simplified 3-option movement system with phase-aware play.

This agent uses a balanced approach with:
- Phase-aware strategy (early/mid/late game)
- Positional evaluation (center control, connectivity)
- Strategic choice between STAY, SEND_HALF, and SEND_ALL
"""

from random import Random
import math

from ..types import (
    Owner,
    Position,
    GameState,
    SetupAction,
    PlayerTurnActions,
    TerritoryAction,
    TerritoryBoard,
    MoveType,
    calculate_half,
    create_grow_action,
    create_simple_move_action,
)
from ..config import GameConfig


class StrategicAgent:
    """Agent using phase-aware strategy with 3-option movement.

    Design Philosophy:
    1. Phase-aware play - Different strategy early vs mid vs late game
    2. Positional evaluation - Score territories by strategic value
    3. Resource management - Balance growth vs expansion vs attack
    4. Territory preservation - Prefer SEND_HALF to maintain ownership
    """

    # Phase boundaries
    EARLY_GAME_END = 6    # Turns 1-6: Build up, safe expansion
    MID_GAME_END = 14     # Turns 7-14: Contest key territories

    # Positional weights
    CENTER_VALUE_WEIGHT = 2.0
    CONNECTIVITY_WEIGHT = 1.5

    # Action base values
    STAY_BASE_VALUE = 3.0
    EXPAND_HALF_VALUE = 4.5   # High value - keeps territory
    EXPAND_ALL_VALUE = 3.0    # Lower - loses territory
    ATTACK_BASE_VALUE = 4.0
    REINFORCE_BASE_VALUE = 1.5

    def __init__(self, seed: int | None = None):
        self._initial_seed = seed
        self._rng = Random(seed)

    @property
    def name(self) -> str:
        return "StrategicBot"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose setup position prioritizing strategic value."""
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

        def position_score(pos: Position) -> float:
            center_dist = abs(pos.row - mid) + abs(pos.col - mid)
            max_dist = mid * 2
            score = (max_dist - center_dist) * self.CENTER_VALUE_WEIGHT

            neighbors = pos.neighbors(board_size)
            expansion_options = sum(
                1 for n in neighbors
                if state.board.get_owner(n) == Owner.NEUTRAL
            )
            score += expansion_options * 0.5
            return score

        valid_positions.sort(key=position_score, reverse=True)
        return SetupAction(player=player, position=valid_positions[0])

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose actions based on phase-aware strategic evaluation."""
        actions = []
        opponent = player.opponent()
        phase = self._determine_phase(state.current_turn, config.num_turns)

        # Calculate position values
        position_values = {
            pos: self._evaluate_position_value(pos, state, player, config)
            for pos in state.board.all_positions()
        }

        # Get strategic context
        my_territories = len(list(state.board.positions_owned_by(player)))
        enemy_territories = len(list(state.board.positions_owned_by(opponent)))
        my_stones = state.board.total_stones(player)
        enemy_stones = state.board.total_stones(opponent)

        for pos in state.board.positions_owned_by(player):
            territory = state.board.get(pos)
            action = self._choose_action_for_territory(
                state, pos, territory, player, opponent, config,
                phase, position_values, my_territories, enemy_territories,
                my_stones, enemy_stones
            )
            actions.append(action)

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _determine_phase(self, current_turn: int, total_turns: int) -> str:
        if current_turn <= self.EARLY_GAME_END:
            return 'early'
        elif current_turn <= self.MID_GAME_END:
            return 'mid'
        return 'late'

    def _evaluate_position_value(
        self,
        pos: Position,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> float:
        """Evaluate strategic value of a position."""
        board = state.board
        board_size = config.board_size
        mid = board_size // 2
        opponent = player.opponent()

        # Center proximity
        center_dist = abs(pos.row - mid) + abs(pos.col - mid)
        max_dist = mid * 2
        value = (max_dist - center_dist) / max_dist * self.CENTER_VALUE_WEIGHT

        # Connectivity
        neighbors = pos.neighbors(board_size)
        friendly_neighbors = sum(
            1 for n in neighbors if board.get_owner(n) == player
        )
        value += friendly_neighbors * self.CONNECTIVITY_WEIGHT * 0.3

        # Stone count (if owned)
        territory = board.get(pos)
        if territory.owner == player and territory.stones > 0:
            value += math.log2(territory.stones + 1) * 0.3

        return value

    def _choose_action_for_territory(
        self,
        state: GameState,
        pos: Position,
        territory,
        player: Owner,
        opponent: Owner,
        config: GameConfig,
        phase: str,
        position_values: dict[Position, float],
        my_territories: int,
        enemy_territories: int,
        my_stones: int,
        enemy_stones: int,
    ) -> TerritoryAction:
        """Decide STAY, SEND_HALF, or SEND_ALL for a territory."""
        board = state.board
        stones = territory.stones
        neighbors = list(pos.neighbors(config.board_size))

        if not neighbors:
            return create_grow_action(pos)

        # Is this position threatened?
        is_threatened = any(
            board.get_owner(n) == opponent for n in neighbors
        )

        # Evaluate STAY
        stay_value = self._evaluate_stay(
            pos, stones, phase, is_threatened,
            enemy_stones - my_stones, position_values[pos], config
        )

        # Evaluate all moves
        best_action = None
        best_value = stay_value

        half_stones = calculate_half(stones)

        for neighbor in neighbors:
            neighbor_territory = board.get(neighbor)
            neighbor_owner = neighbor_territory.owner
            target_value = position_values[neighbor]

            if neighbor_owner == Owner.NEUTRAL:
                # SEND_HALF expansion (keeps territory!)
                half_ev = self._evaluate_expand_half(
                    target_value, phase, my_territories, enemy_territories
                )
                if half_ev > best_value:
                    best_value = half_ev
                    best_action = (MoveType.SEND_HALF, neighbor, half_stones)

                # SEND_ALL expansion
                all_ev = self._evaluate_expand_all(
                    target_value, phase
                )
                if all_ev > best_value:
                    best_value = all_ev
                    best_action = (MoveType.SEND_ALL, neighbor, stones)

            elif neighbor_owner == opponent:
                enemy_stones_at_target = neighbor_territory.stones

                # SEND_HALF attack
                if half_stones >= enemy_stones_at_target:
                    half_attack = self._evaluate_attack(
                        half_stones, enemy_stones_at_target, target_value,
                        phase, my_territories, enemy_territories, keep_source=True
                    )
                    if half_attack > best_value:
                        best_value = half_attack
                        best_action = (MoveType.SEND_HALF, neighbor, half_stones)

                # SEND_ALL attack
                all_attack = self._evaluate_attack(
                    stones, enemy_stones_at_target, target_value,
                    phase, my_territories, enemy_territories, keep_source=False
                )
                if all_attack > best_value:
                    best_value = all_attack
                    best_action = (MoveType.SEND_ALL, neighbor, stones)

            else:  # Friendly
                # SEND_HALF reinforce
                half_reinforce = self._evaluate_reinforce(
                    target_value, phase, is_target_threatened=any(
                        board.get_owner(n) == opponent for n in neighbor.neighbors(config.board_size)
                    )
                )
                if half_reinforce > best_value:
                    best_value = half_reinforce
                    best_action = (MoveType.SEND_HALF, neighbor, half_stones)

        # Add randomness
        if best_action and self._rng.random() < 0.05:
            if stay_value >= best_value - 0.3:
                return create_grow_action(pos)

        if best_action is None:
            return create_grow_action(pos)

        move_type, dest, count = best_action
        return create_simple_move_action(pos, dest, count)

    def _evaluate_stay(
        self,
        pos: Position,
        stones: int,
        phase: str,
        is_threatened: bool,
        stone_deficit: int,
        position_value: float,
        config: GameConfig,
    ) -> float:
        """Evaluate staying and growing."""
        value = self.STAY_BASE_VALUE

        # Already at max - less value
        if stones >= config.max_stones:
            value -= 1.0

        # Phase modifier
        if phase == 'early':
            value += 1.5
        elif phase == 'mid':
            value += 0.5
        else:
            value -= 0.5

        # Threat bonus
        if is_threatened:
            value += 2.0 / (1 + stones * 0.3)

        # Stone deficit
        if stone_deficit > 3:
            value += 0.5
        elif stone_deficit < -3:
            value -= 0.3

        # Position value
        value += position_value * 0.3

        # Low stones bonus
        if stones <= 2:
            value += 1.0

        return value

    def _evaluate_expand_half(
        self,
        target_value: float,
        phase: str,
        my_territories: int,
        enemy_territories: int,
    ) -> float:
        """Evaluate SEND_HALF expansion (keeps source territory)."""
        value = self.EXPAND_HALF_VALUE + target_value

        # Big bonus for cell division strategy
        value += 1.0

        # Phase modifier
        if phase == 'early':
            value *= 0.9  # Slightly cautious
        elif phase == 'mid':
            value *= 1.2  # Prime expansion time
        else:
            # Late: expand more if behind
            if my_territories < enemy_territories:
                value *= 1.2
            else:
                value *= 0.9

        return value

    def _evaluate_expand_all(
        self,
        target_value: float,
        phase: str,
    ) -> float:
        """Evaluate SEND_ALL expansion (loses source territory)."""
        value = self.EXPAND_ALL_VALUE + target_value

        # Phase modifier - prefer SEND_HALF except in specific situations
        if phase == 'early':
            value *= 0.6  # Strong penalty early
        elif phase == 'mid':
            value *= 0.8
        else:
            value *= 0.7

        return value

    def _evaluate_attack(
        self,
        our_stones: int,
        enemy_stones: int,
        target_value: float,
        phase: str,
        my_territories: int,
        enemy_territories: int,
        keep_source: bool,
    ) -> float:
        """Evaluate attacking enemy territory."""
        advantage = our_stones - enemy_stones
        value = self.ATTACK_BASE_VALUE + target_value

        # Stone advantage bonus/penalty
        if advantage >= 3:
            value += 2.0
        elif advantage >= 2:
            value += 1.5
        elif advantage >= 1:
            value += 1.0
        elif advantage == 0:
            value -= 0.5
        elif advantage >= -1:
            value -= 1.5
        else:
            value -= 3.0  # Don't attack at disadvantage

        # Bonus for keeping source (SEND_HALF)
        if keep_source:
            value += 0.5

        # Phase modifier
        if phase == 'early':
            value *= 0.7  # Cautious early
        elif phase == 'late':
            if my_territories < enemy_territories:
                value *= 1.3  # Need to catch up
            else:
                value *= 0.8  # Protect lead

        return value

    def _evaluate_reinforce(
        self,
        target_value: float,
        phase: str,
        is_target_threatened: bool,
    ) -> float:
        """Evaluate reinforcing friendly territory."""
        value = self.REINFORCE_BASE_VALUE

        if is_target_threatened:
            value += 1.5

        if phase == 'late':
            value += 0.5

        return value
