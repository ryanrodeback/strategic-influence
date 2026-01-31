"""GreedyStrategicAgent: Fast heuristic using Minimax insights.

This agent uses all the strategic knowledge we encoded into Minimax:
- Best expansion = neutral with most neutral neighbors
- 1-stone territories must STAY
- Only attacks with advantage
- Only reinforcements that resolve threats

But instead of searching, it just picks the highest-scored move.
Essentially "depth-0 Minimax" - all the strategy, none of the search.

Speed: ~1ms per move (vs ~20s for Minimax depth-2)
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
from .common import find_valid_setup_positions


class GreedyStrategicAgent:
    """Fast heuristic agent using Minimax-derived strategy.

    Applies all our strategic insights without search:
    - Expansion scored by future potential (neutral neighbors)
    - 1-stone territories must STAY
    - Only useful moves considered
    - Pick the single best move per territory
    """

    def __init__(self, seed: int | None = None):
        self._initial_seed = seed
        self._rng = Random(seed)

    @property
    def name(self) -> str:
        return "GreedyStrategic"

    def reset(self) -> None:
        self._rng = Random(self._initial_seed)

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose setup position - prefer center with most neighbors."""
        board_size = config.board_size
        mid = board_size // 2

        valid_positions = find_valid_setup_positions(state, player, config)

        def setup_score(pos: Position) -> float:
            dist = abs(pos.row - mid) + abs(pos.col - mid)
            num_neighbors = len(pos.neighbors(board_size))
            return -dist + num_neighbors * 0.5

        valid_positions.sort(key=setup_score, reverse=True)
        return SetupAction(player=player, position=valid_positions[0])

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose best action for each territory using strategic scoring."""
        actions: list[TerritoryAction] = []
        board = state.board
        opponent = player.opponent()

        for pos in board.positions_owned_by(player):
            action = self._choose_best_action(pos, state, player, config)
            actions.append(action)

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _choose_best_action(
        self,
        pos: Position,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> TerritoryAction:
        """Choose the single best action for a territory."""
        board = state.board
        territory = board.get(pos)
        stones = territory.stones
        opponent = player.opponent()

        # 1-stone territories must STAY
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
                # SEND_HALF to neutral - score by future potential
                neutral_neighbors = sum(
                    1 for nn in neighbor.neighbors(config.board_size)
                    if board.get_owner(nn) == Owner.NEUTRAL
                )
                score = 200.0 + neutral_neighbors * 30.0
                options.append((score, create_simple_move_action(pos, neighbor, half_stones)))

            elif neighbor_owner == opponent:
                # Attack only with advantage
                if half_stones > neighbor_stones:
                    # SEND_HALF wins - best (keeps our territory)
                    options.append((100.0, create_simple_move_action(pos, neighbor, half_stones)))
                elif stones > neighbor_stones:
                    # Only SEND_ALL wins
                    options.append((90.0, create_simple_move_action(pos, neighbor, stones)))

            else:  # friendly
                # Reinforce only if it resolves a threat
                neighbor_threatened_by = None
                for nn in neighbor.neighbors(config.board_size):
                    if board.get_owner(nn) == opponent:
                        enemy_stones = board.get_stones(nn)
                        if enemy_stones > neighbor_stones:
                            neighbor_threatened_by = enemy_stones
                            break

                if neighbor_threatened_by is not None:
                    reinforced = neighbor_stones + half_stones
                    if reinforced >= neighbor_threatened_by:
                        options.append((80.0, create_simple_move_action(pos, neighbor, half_stones)))

        # Pick highest scored option
        options.sort(key=lambda x: x[0], reverse=True)

        # If multiple options have same score, pick randomly among them
        best_score = options[0][0]
        best_options = [opt for opt in options if opt[0] == best_score]

        return self._rng.choice(best_options)[1]
