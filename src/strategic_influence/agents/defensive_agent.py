"""Defensive/positional heuristic agent implementation.

V4: Simplified 3-option movement system (STAY, SEND_HALF, SEND_ALL).

This agent uses a defensive, positional strategy that prioritizes:
- Safe expansion (prefer SEND_HALF to maintain territory)
- Growth before expansion (build up strength)
- Defensive reinforcement (protect borders)
- Avoiding overextension (don't spread thin)
- Core protection (value well-connected territories)
"""

from random import Random

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
from .common import find_valid_setup_positions


class DefensiveAgent:
    """Agent that uses defensive/positional heuristics with 3-option movement.

    Strategy:
    - Setup: Choose positions closer to center for better connectivity
    - Play: Strongly prefer STAY (growing) and SEND_HALF over SEND_ALL
    - SEND_HALF for expansion: Maintains territory ownership
    - Only SEND_ALL when attacking with clear advantage
    """

    # =========================================================================
    # HEURISTIC WEIGHTS
    # =========================================================================

    # Growth evaluation weights
    STAY_BASE_VALUE = 1.5          # High base value - defensive agent loves growing
    STAY_THREAT_BONUS = 0.4        # Bonus for growing when enemy is adjacent
    STAY_EARLY_GAME_BONUS = 0.3    # Bonus for growing in early game
    STAY_LOW_STONES_BONUS = 0.5    # Bonus for growing when we have few stones

    # Movement evaluation weights
    HALF_EXPAND_VALUE = 1.0        # Value of expanding with half (keeps territory)
    HALF_REINFORCE_VALUE = 0.5     # Value of reinforcing with half
    ALL_EXPAND_VALUE = 0.4         # Lower value - loses territory
    ALL_ATTACK_VALUE = 0.6         # Only use when we have advantage
    ALL_ATTACK_ADVANTAGE = 0.3     # Bonus per stone advantage

    # Strategic thresholds
    STONE_BUILDUP_THRESHOLD = 4    # Prefer growing until we have this many stones
    LATE_GAME_TURN_FRACTION = 0.7  # When late game begins

    def __init__(self, seed: int | None = None):
        """Initialize the defensive agent."""
        self._initial_seed = seed
        self._rng = Random(seed)

    @property
    def name(self) -> str:
        return "DefensiveBot"

    def reset(self) -> None:
        """Reset RNG for new game."""
        self._rng = Random(self._initial_seed)

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose setup position prioritizing connectivity and center proximity."""
        board_size = config.board_size
        mid = board_size // 2

        valid_positions = find_valid_setup_positions(state, player, config)

        def score_position(pos: Position) -> float:
            center_dist = abs(pos.row - mid) + abs(pos.col - mid)
            neutral_neighbors = sum(
                1 for n in pos.neighbors(board_size)
                if state.board.get_owner(n) == Owner.NEUTRAL
            )
            return -center_dist + neutral_neighbors * 0.5

        valid_positions.sort(key=score_position, reverse=True)
        return SetupAction(player=player, position=valid_positions[0])

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose actions using defensive evaluation heuristics."""
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
        """Decide STAY, SEND_HALF, or SEND_ALL using defensive heuristics."""
        board = state.board
        stones = territory.stones
        neighbors = list(pos.neighbors(config.board_size))

        if not neighbors:
            return create_grow_action(pos)

        game_progress = state.current_turn / config.num_turns
        is_late_game = game_progress >= self.LATE_GAME_TURN_FRACTION

        # Evaluate staying (growing)
        stay_value = self._evaluate_stay(
            pos, stones, player, opponent, state, config, game_progress
        )

        # Find best move option
        best_action = None
        best_value = stay_value

        half_stones = calculate_half(stones)

        for neighbor in neighbors:
            neighbor_territory = board.get(neighbor)
            neighbor_owner = neighbor_territory.owner

            # Evaluate SEND_HALF
            half_value = self._evaluate_send_half(
                neighbor, neighbor_territory, player, opponent,
                half_stones, stones, state, config, is_late_game
            )

            # Evaluate SEND_ALL (defensive agent is cautious with this)
            all_value = self._evaluate_send_all(
                neighbor, neighbor_territory, player, opponent,
                stones, state, config, is_late_game
            )

            if half_value > best_value:
                best_value = half_value
                best_action = (MoveType.SEND_HALF, neighbor, half_stones)

            if all_value > best_value:
                best_value = all_value
                best_action = (MoveType.SEND_ALL, neighbor, stones)

        # Defensive principle: favor staying when values are close
        if best_action is None or stay_value >= best_value - 0.2:
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
        game_progress: float,
    ) -> float:
        """Evaluate the value of staying and growing."""
        board = state.board
        value = self.STAY_BASE_VALUE

        # Already at max stones - less value in staying
        if stones >= config.max_stones:
            value -= 0.8

        # Grow more when we have few stones
        if stones < self.STONE_BUILDUP_THRESHOLD:
            value += self.STAY_LOW_STONES_BONUS * (1 - stones / self.STONE_BUILDUP_THRESHOLD)

        # Grow more when threatened
        for neighbor in pos.neighbors(config.board_size):
            if board.get_owner(neighbor) == opponent:
                value += self.STAY_THREAT_BONUS
                break

        # Grow more in early game
        if game_progress < 0.3:
            value += self.STAY_EARLY_GAME_BONUS

        return value

    def _evaluate_send_half(
        self,
        target: Position,
        target_territory,
        player: Owner,
        opponent: Owner,
        half_stones: int,
        total_stones: int,
        state: GameState,
        config: GameConfig,
        is_late_game: bool,
    ) -> float:
        """Evaluate sending half stones.

        Defensive agent loves SEND_HALF because it maintains territory ownership.
        """
        target_owner = target_territory.owner
        board = state.board

        if target_owner == Owner.NEUTRAL:
            # Expand with half - keeps our territory!
            value = self.HALF_EXPAND_VALUE

            # Extra bonus for "cell division" strategy
            value += 0.4  # This is the key defensive advantage

            # Late game: more valuable to expand
            if is_late_game:
                value += 0.3

            # Position value
            value += self._position_value(target, player, opponent, board, config) * 0.3

            return value

        elif target_owner == player:
            # Reinforce friendly position
            value = self.HALF_REINFORCE_VALUE

            # More valuable if target is threatened
            for adj in target.neighbors(config.board_size):
                if board.get_owner(adj) == opponent:
                    value += 0.3
                    break

            return value

        else:  # opponent
            # Attack with half - only if we still have advantage
            enemy_stones = target_territory.stones
            if half_stones > enemy_stones:
                advantage = half_stones - enemy_stones
                return 0.3 + advantage * 0.2
            return -0.5  # Not worth attacking without advantage

    def _evaluate_send_all(
        self,
        target: Position,
        target_territory,
        player: Owner,
        opponent: Owner,
        stones: int,
        state: GameState,
        config: GameConfig,
        is_late_game: bool,
    ) -> float:
        """Evaluate sending all stones.

        Defensive agent is very cautious about SEND_ALL since it loses the territory.
        """
        target_owner = target_territory.owner
        board = state.board

        if target_owner == Owner.NEUTRAL:
            # Expand with all - loses territory, not preferred
            value = self.ALL_EXPAND_VALUE

            # Only acceptable in late game when we need territory
            if is_late_game:
                value += 0.2
            else:
                value -= 0.3  # Strong penalty in early/mid game

            return value

        elif target_owner == player:
            # Reinforce - might be ok for threatened positions
            value = 0.3
            for adj in target.neighbors(config.board_size):
                adj_territory = board.get(adj)
                if adj_territory.owner == opponent and adj_territory.stones >= board.get(target).stones:
                    value += 0.4  # Under serious threat
                    break
            return value

        else:  # opponent
            # Attack with all - only with clear advantage
            enemy_stones = target_territory.stones
            advantage = stones - enemy_stones

            if advantage <= 0:
                return -1.0  # Never attack without advantage

            value = self.ALL_ATTACK_VALUE + self.ALL_ATTACK_ADVANTAGE * advantage

            # Late game makes attacking more necessary
            if is_late_game:
                value += 0.3

            return value

    def _position_value(
        self,
        pos: Position,
        player: Owner,
        opponent: Owner,
        board: TerritoryBoard,
        config: GameConfig,
    ) -> float:
        """Evaluate strategic value of a position."""
        mid = config.board_size // 2
        center_dist = abs(pos.row - mid) + abs(pos.col - mid)
        max_dist = mid * 2

        value = 0.2 * (1 - center_dist / max_dist)

        # Friendly neighbors are good
        for neighbor in pos.neighbors(config.board_size):
            if board.get_owner(neighbor) == player:
                value += 0.1

        return value
