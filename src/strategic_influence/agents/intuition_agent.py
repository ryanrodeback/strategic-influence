"""IntuitionAgent: Implements user's strategic hypothesis.

Core strategy principles:
1. Safe division is optimal when no threat can reach before recovery
2. Expansion over growth in opening (more territories = more growth)
3. Value positions that can merge back together
4. Safe conquest reduces enemy growth potential
5. Threat-aware timing for splits

The key insight: Safely dividing maximizes growth for next turn.
Split -> grow -> grow -> merge creates compound growth advantage.
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
from ..evaluation import (
    INTUITION_WEIGHTS,
    is_position_threatened,
    can_safely_divide,
    turns_until_threat_reaches,
)


class IntuitionAgent:
    """Agent implementing user's strategic hypothesis.

    Decision hierarchy:
    1. If safely dividable AND have expansion target -> SEND_HALF to expand
    2. If safely dividable AND friendly neighbor -> SEND_HALF to grow both
    3. If can safely conquer enemy -> attack (reduces their growth)
    4. If threatened -> defend (reinforce or retreat)
    5. Default -> STAY and grow

    The "safely dividable" check is key: only split if no threat
    can reach you before you can recover (grow back or merge).
    """

    def __init__(self, seed: int | None = None):
        self._initial_seed = seed
        self._rng = Random(seed)

    @property
    def name(self) -> str:
        return "IntuitionBot"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose setup position - prefer center for expansion potential."""
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

        # Prefer positions closer to center (more expansion options)
        def center_score(pos: Position) -> float:
            dist = abs(pos.row - mid) + abs(pos.col - mid)
            # Also prefer positions with more neighbors
            num_neighbors = len(pos.neighbors(board_size))
            return -dist + num_neighbors * 0.5

        valid_positions.sort(key=center_score, reverse=True)

        # Pick from top positions with some randomness
        top_k = min(3, len(valid_positions))
        return SetupAction(player=player, position=self._rng.choice(valid_positions[:top_k]))

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose actions following the intuition strategy."""
        actions: list[TerritoryAction] = []
        board = state.board
        opponent = player.opponent()

        owned_positions = list(board.positions_owned_by(player))

        for pos in owned_positions:
            action = self._choose_action_for_territory(
                pos, state, player, config
            )
            actions.append(action)

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _choose_action_for_territory(
        self,
        pos: Position,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> TerritoryAction:
        """Decide action for a single territory."""
        board = state.board
        territory = board.get(pos)
        stones = territory.stones
        half_stones = calculate_half(stones)
        neighbors = list(pos.neighbors(config.board_size))
        opponent = player.opponent()

        # Categorize neighbors
        neutral_neighbors: list[Position] = []
        enemy_neighbors: list[tuple[Position, int]] = []
        friendly_neighbors: list[tuple[Position, int]] = []

        for n in neighbors:
            n_owner = board.get_owner(n)
            if n_owner == Owner.NEUTRAL:
                neutral_neighbors.append(n)
            elif n_owner == opponent:
                enemy_neighbors.append((n, board.get_stones(n)))
            else:
                friendly_neighbors.append((n, board.get_stones(n)))

        # Check if we can safely divide
        safely_dividable = can_safely_divide(pos, board, player, config)
        is_threatened = is_position_threatened(pos, board, player, config)

        # Priority 1: If threatened and weak, defend
        if is_threatened and stones <= 3:
            # Try to reinforce from this position or stay to grow
            if friendly_neighbors:
                # Find the safest friendly neighbor
                safest = self._find_safest_neighbor(
                    friendly_neighbors, board, player, config
                )
                if safest:
                    return create_simple_move_action(pos, safest, stones)
            # Stay and grow to defend
            return create_grow_action(pos)

        # Priority 2: Safe expansion (user insight: expand first when safe)
        if safely_dividable and neutral_neighbors:
            # Prefer center-ward expansion
            best_neutral = self._best_expansion_target(
                neutral_neighbors, config
            )
            # SEND_HALF to keep this territory
            return create_simple_move_action(pos, best_neutral, half_stones)

        # Priority 3: Safe conquest (reduces enemy growth)
        if enemy_neighbors:
            # Find enemy we can beat with SEND_HALF (safest attack)
            for enemy_pos, enemy_stones in sorted(enemy_neighbors, key=lambda x: x[1]):
                if half_stones > enemy_stones and safely_dividable:
                    # Safe conquest with SEND_HALF - we keep our territory!
                    return create_simple_move_action(pos, enemy_pos, half_stones)
                elif stones > enemy_stones + 1:
                    # Can beat with full force, worth it if we're strong
                    if stones >= 4:  # Only commit if we have reserves
                        return create_simple_move_action(pos, enemy_pos, stones)

        # Priority 4: Safe division to friendly (compound growth)
        # User insight: split -> grow -> grow -> merge creates advantage
        if safely_dividable and friendly_neighbors:
            # Find friendly neighbor that could also grow
            for friend_pos, friend_stones in friendly_neighbors:
                if friend_stones < config.max_stones:
                    # Send half to friend, both can grow next turn
                    return create_simple_move_action(pos, friend_pos, half_stones)

        # Priority 5: Expand even if not perfectly safe (early game aggression)
        early_game = state.current_turn < config.num_turns * 0.3
        if early_game and neutral_neighbors and stones >= 2:
            best_neutral = self._best_expansion_target(neutral_neighbors, config)
            return create_simple_move_action(pos, best_neutral, half_stones)

        # Default: Stay and grow
        return create_grow_action(pos)

    def _best_expansion_target(
        self,
        neutral_neighbors: list[Position],
        config: GameConfig,
    ) -> Position:
        """Find the best neutral to expand into (prefer center)."""
        mid = config.board_size // 2

        def score(pos: Position) -> float:
            dist = abs(pos.row - mid) + abs(pos.col - mid)
            # More neighbors = more future options
            num_neighbors = len(pos.neighbors(config.board_size))
            return -dist + num_neighbors * 0.3

        return max(neutral_neighbors, key=score)

    def _find_safest_neighbor(
        self,
        friendly_neighbors: list[tuple[Position, int]],
        board,
        player: Owner,
        config: GameConfig,
    ) -> Position | None:
        """Find the safest friendly neighbor to retreat to."""
        if not friendly_neighbors:
            return None

        def safety_score(item: tuple[Position, int]) -> float:
            pos, stones = item
            # Higher stones = safer
            # Fewer enemy neighbors = safer
            threat_level = 0
            for n in pos.neighbors(config.board_size):
                if board.get_owner(n) == player.opponent():
                    threat_level += board.get_stones(n)
            return stones - threat_level * 0.5

        best = max(friendly_neighbors, key=safety_score)
        return best[0]
