"""Aggressive Rush AI agent implementation.

V4: Simplified 3-option movement system (STAY, SEND_HALF, SEND_ALL).

This agent implements an early-game pressure strategy focused on:
1. Early expansion - Grab territory fast using SEND_HALF to keep growing
2. Momentum - Keep pressure on opponent with continuous expansion
3. Calculated aggression - Attack when you have numerical advantage
4. Territory over stones - Use SEND_HALF to maximize territory count
5. Deny center - Control central positions aggressively
"""

from random import Random

from ..types import (
    Owner,
    Position,
    GameState,
    SetupAction,
    PlayerTurnActions,
    TerritoryAction,
    MoveType,
    calculate_half,
    create_grow_action,
    create_simple_move_action,
)
from ..config import GameConfig


class RushAgent:
    """Agent that uses aggressive early-game rush tactics with 3-option movement.

    Strategy Philosophy:
    - Setup: Claim center-most position
    - Early game: Use SEND_HALF to rapidly expand while keeping territories
    - Mid game: Attack weak enemy positions
    - Late game: Consolidate lead
    """

    # Evaluation weights
    EXPAND_HALF_VALUE = 3.5      # High value for expansion while keeping territory
    EXPAND_ALL_VALUE = 2.0       # Lower value since we lose source
    ATTACK_VALUE = 3.0           # Value for attacking
    STAY_VALUE = 1.0             # Low value for staying (rush wants action!)
    CENTER_BONUS = 2.0           # Bonus for center positions
    STONE_ADVANTAGE_BONUS = 1.0  # Bonus per stone advantage
    WEAK_ENEMY_BONUS = 2.0       # Bonus for attacking 1-stone enemies

    # Phase multipliers
    EARLY_GAME_AGGRESSION = 1.5
    LATE_GAME_CAUTION = 0.8

    def __init__(self, seed: int | None = None):
        self._initial_seed = seed
        self._rng = Random(seed)

    @property
    def name(self) -> str:
        return "RushBot"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose setup position closest to center."""
        board_size = config.board_size
        center = board_size // 2

        valid_positions = [
            Position(r, c)
            for r in range(board_size)
            for c in range(board_size)
            if Position(r, c).is_in_setup_zone(board_size, player)
            and state.board.get_owner(Position(r, c)) == Owner.NEUTRAL
        ]

        if not valid_positions:
            raise ValueError(f"No valid setup positions for {player}")

        def center_score(pos: Position) -> float:
            return abs(pos.row - center) * 2 + abs(pos.col - center)

        valid_positions.sort(key=center_score)
        return SetupAction(player=player, position=valid_positions[0])

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose actions using rush strategy."""
        actions = []
        opponent = player.opponent()
        phase_modifier = self._get_phase_modifier(state, config)
        territory_lead = self._get_territory_lead(state, player, opponent)

        for pos in state.board.positions_owned_by(player):
            territory = state.board.get(pos)
            action = self._choose_action_for_territory(
                state, pos, territory, player, opponent, config,
                phase_modifier, territory_lead
            )
            actions.append(action)

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _get_phase_modifier(self, state: GameState, config: GameConfig) -> float:
        """Get aggression modifier based on game phase."""
        turn = state.current_turn
        total = config.num_turns
        if turn <= total // 3:
            return self.EARLY_GAME_AGGRESSION
        elif turn >= total * 3 // 4:
            return self.LATE_GAME_CAUTION
        return 1.0

    def _get_territory_lead(
        self,
        state: GameState,
        player: Owner,
        opponent: Owner,
    ) -> int:
        """Get our territory lead over opponent."""
        counts = state.board.count_territories()
        return counts[player] - counts[opponent]

    def _choose_action_for_territory(
        self,
        state: GameState,
        pos: Position,
        territory,
        player: Owner,
        opponent: Owner,
        config: GameConfig,
        phase_modifier: float,
        territory_lead: int,
    ) -> TerritoryAction:
        """Decide STAY, SEND_HALF, or SEND_ALL."""
        board = state.board
        stones = territory.stones
        neighbors = list(pos.neighbors(config.board_size))

        if not neighbors:
            return create_grow_action(pos)

        # Evaluate staying
        stay_value = self._evaluate_stay(
            pos, stones, player, opponent, state, config, territory_lead
        )

        # Find best move
        best_action = None
        best_value = stay_value

        half_stones = calculate_half(stones)
        center = config.board_size // 2

        for neighbor in neighbors:
            neighbor_territory = board.get(neighbor)
            neighbor_owner = neighbor_territory.owner

            # Position bonus for center
            dist_to_center = abs(neighbor.row - center) + abs(neighbor.col - center)
            position_bonus = self.CENTER_BONUS if dist_to_center == 0 else (
                self.CENTER_BONUS * 0.5 if dist_to_center <= 2 else 0
            )

            if neighbor_owner == Owner.NEUTRAL:
                # SEND_HALF to neutral - key rush strategy!
                half_value = self.EXPAND_HALF_VALUE + position_bonus
                half_value *= phase_modifier

                # SEND_ALL to neutral
                all_value = self.EXPAND_ALL_VALUE + position_bonus
                all_value *= phase_modifier

                if half_value > best_value:
                    best_value = half_value
                    best_action = (MoveType.SEND_HALF, neighbor, half_stones)

                if all_value > best_value:
                    best_value = all_value
                    best_action = (MoveType.SEND_ALL, neighbor, stones)

            elif neighbor_owner == opponent:
                enemy_stones = neighbor_territory.stones

                # SEND_HALF attack
                if half_stones >= enemy_stones:
                    half_attack_value = self.ATTACK_VALUE + position_bonus
                    half_attack_value += self.STONE_ADVANTAGE_BONUS * (half_stones - enemy_stones)
                    if enemy_stones == 1:
                        half_attack_value += self.WEAK_ENEMY_BONUS
                    half_attack_value *= phase_modifier

                    if half_attack_value > best_value:
                        best_value = half_attack_value
                        best_action = (MoveType.SEND_HALF, neighbor, half_stones)

                # SEND_ALL attack
                all_attack_value = self.ATTACK_VALUE + position_bonus
                stone_diff = stones - enemy_stones
                if stone_diff > 0:
                    all_attack_value += self.STONE_ADVANTAGE_BONUS * stone_diff
                else:
                    all_attack_value -= abs(stone_diff) * 0.8
                if enemy_stones == 1:
                    all_attack_value += self.WEAK_ENEMY_BONUS
                all_attack_value *= phase_modifier

                # Behind on territory? Be more aggressive
                if territory_lead < -2:
                    all_attack_value += 1.0

                if all_attack_value > best_value:
                    best_value = all_attack_value
                    best_action = (MoveType.SEND_ALL, neighbor, stones)

        # Randomness for unpredictability
        if best_action and self._rng.random() < 0.1:
            if stay_value >= best_value - 0.5:
                return create_grow_action(pos)

        if best_action is None:
            return create_grow_action(pos)

        move_type, dest, count = best_action
        return create_simple_move_action(pos, dest, count)

    def _evaluate_stay(
        self,
        pos: Position,
        stones: int,
        player: Owner,
        opponent: Owner,
        state: GameState,
        config: GameConfig,
        territory_lead: int,
    ) -> float:
        """Evaluate staying and growing."""
        value = self.STAY_VALUE
        board = state.board

        # Already at max - staying is less valuable
        if stones >= config.max_stones:
            value -= 0.5

        # Under threat - might want to grow for defense
        for neighbor in pos.neighbors(config.board_size):
            neighbor_territory = board.get(neighbor)
            if neighbor_territory.owner == opponent:
                if neighbor_territory.stones >= stones:
                    value += 1.0
                    break

        # Behind on territory - should be expanding!
        if territory_lead < -2:
            value -= 1.0
        elif territory_lead > 2:
            value += 0.5

        return value
