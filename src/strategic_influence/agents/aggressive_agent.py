"""Aggressive heuristic agent implementation.

V4: Simplified 3-option movement system (STAY, SEND_HALF, SEND_ALL).

This agent uses heuristics to make strategic decisions about
when to stay vs when to attack, and whether to commit fully or partially.
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


class AggressiveAgent:
    """Agent that uses aggressive heuristics with 3-option movement.

    Strategy:
    - Setup: Choose center position in setup zone
    - Play: Evaluate STAY vs SEND_HALF vs SEND_ALL for each neighbor
    - Prefers attacking enemies and expanding into neutral territory
    - Uses SEND_HALF to maintain territory ownership while expanding
    """

    def __init__(self, seed: int | None = None):
        """Initialize the aggressive agent.

        Args:
            seed: Random seed for tie-breaking. None for random.
        """
        self._initial_seed = seed
        self._rng = Random(seed)

    @property
    def name(self) -> str:
        return "AggressiveBot"

    def reset(self) -> None:
        """Reset RNG for new game."""
        self._rng = Random(self._initial_seed)

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose center position in setup zone for best expansion potential."""
        board_size = config.board_size
        mid = board_size // 2

        # Find all valid setup positions
        valid_positions = [
            Position(r, c)
            for r in range(board_size)
            for c in range(board_size)
            if Position(r, c).is_in_setup_zone(board_size, player)
            and state.board.get_owner(Position(r, c)) == Owner.NEUTRAL
        ]

        if not valid_positions:
            raise ValueError(f"No valid setup positions for {player}")

        # Prefer positions closer to center of board
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
        """Choose actions based on aggressive evaluation."""
        actions = []
        opponent = player.opponent()

        for pos in state.board.positions_owned_by(player):
            territory = state.board.get(pos)
            action = self._choose_action_for_territory(
                state, pos, territory, player, opponent, config
            )
            actions.append(action)

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _choose_action_for_territory(
        self,
        state: GameState,
        pos: Position,
        territory,
        player: Owner,
        opponent: Owner,
        config: GameConfig,
    ) -> TerritoryAction:
        """Decide STAY, SEND_HALF, or SEND_ALL for a single territory."""
        weights = config.ai.aggressive.weights
        board = state.board
        stones = territory.stones
        neighbors = list(pos.neighbors(config.board_size))

        if not neighbors:
            return create_grow_action(pos)

        # Evaluate staying (GROW)
        stay_value = self._evaluate_stay(pos, player, opponent, state, config)

        # Evaluate each possible action (SEND_HALF and SEND_ALL to each neighbor)
        best_action = None
        best_value = stay_value

        half_stones = calculate_half(stones)

        for neighbor in neighbors:
            neighbor_territory = board.get(neighbor)

            # Evaluate SEND_HALF
            half_value = self._evaluate_move(
                neighbor, neighbor_territory, player, opponent,
                half_stones, stones, keep_territory=True, config=config
            )

            # Evaluate SEND_ALL
            all_value = self._evaluate_move(
                neighbor, neighbor_territory, player, opponent,
                stones, stones, keep_territory=False, config=config
            )

            # Track best option
            if half_value > best_value:
                best_value = half_value
                best_action = (MoveType.SEND_HALF, neighbor, half_stones)

            if all_value > best_value:
                best_value = all_value
                best_action = (MoveType.SEND_ALL, neighbor, stones)

        # Add small randomness to prevent predictability
        if best_action is None or self._rng.random() < 0.05:
            # Sometimes stay even if moving seems slightly better
            if best_value < stay_value + 0.2:
                return create_grow_action(pos)

        if best_action is None:
            return create_grow_action(pos)

        move_type, dest, count = best_action
        return create_simple_move_action(pos, dest, count)

    def _evaluate_move(
        self,
        target: Position,
        target_territory,
        player: Owner,
        opponent: Owner,
        stones_sent: int,
        total_stones: int,
        keep_territory: bool,
        config: GameConfig,
    ) -> float:
        """Evaluate how valuable a move is.

        Args:
            target: Destination position
            target_territory: Territory at destination
            player: Our player
            opponent: Enemy player
            stones_sent: Number of stones being sent
            total_stones: Total stones at source
            keep_territory: Whether we keep the source territory (SEND_HALF vs SEND_ALL)
            config: Game configuration
        """
        weights = config.ai.aggressive.weights
        value = 0.0

        if target_territory.owner == Owner.NEUTRAL:
            # Expanding into neutral
            value = weights.expand_neutral

            # Bonus for keeping territory (cell division strategy)
            if keep_territory:
                value += 0.3  # Extra value for maintaining growth potential

        elif target_territory.owner == opponent:
            # Attacking enemy
            enemy_stones = target_territory.stones

            # Base attack value
            value = weights.attack_enemy

            # Bonus/penalty based on stone advantage
            if stones_sent > enemy_stones:
                value += weights.stone_count_bonus * (stones_sent - enemy_stones)
            else:
                value -= weights.stone_count_bonus * (enemy_stones - stones_sent) * 1.5

            # Bonus for keeping territory while attacking
            if keep_territory and stones_sent >= enemy_stones:
                value += 0.2

        else:
            # Moving to own territory (reinforcing) - usually not great
            value = weights.defend_own * 0.2

        return value

    def _evaluate_stay(
        self,
        pos: Position,
        player: Owner,
        opponent: Owner,
        state: GameState,
        config: GameConfig,
    ) -> float:
        """Evaluate how valuable staying and growing is."""
        weights = config.ai.aggressive.weights
        board = state.board
        territory = board.get(pos)
        value = weights.defend_own

        # Less value if already at max stones
        if territory.stones >= config.max_stones:
            value -= 0.5

        # Check if under threat (enemy adjacent)
        for neighbor in pos.neighbors(config.board_size):
            neighbor_territory = board.get(neighbor)
            if neighbor_territory.owner == opponent:
                # Under threat - growing might be good defense
                value += weights.defend_own * 0.3

        # Growing is more valuable early game to build up forces
        if state.current_turn < config.num_turns // 3:
            value += 0.2

        return value
