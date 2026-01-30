"""Random agent implementation.

V4: Simplified 3-option movement system (STAY, SEND_HALF, SEND_ALL).

This agent makes random choices for setup and turn actions.
Useful as a baseline for testing and comparison.
"""

from random import Random

from ..types import (
    Owner,
    Position,
    GameState,
    SetupAction,
    PlayerTurnActions,
    MoveType,
    get_valid_actions,
    create_action_from_move_type,
)
from ..config import GameConfig


class RandomAgent:
    """Agent that makes random moves.

    During setup: places stone at random position in setup zone.
    During play: randomly chooses from STAY, SEND_HALF, or SEND_ALL for each territory.
    """

    def __init__(self, seed: int | None = None):
        """Initialize the random agent.

        Args:
            seed: Random seed for reproducibility. None for random behavior.
        """
        self._initial_seed = seed
        self._rng = Random(seed)

    @property
    def name(self) -> str:
        return "RandomBot"

    def reset(self) -> None:
        """Reset RNG to initial state for new game."""
        self._rng = Random(self._initial_seed)

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose a random position in the player's setup zone."""
        board_size = config.board_size

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

        # Pick randomly
        chosen = self._rng.choice(valid_positions)
        return SetupAction(player=player, position=chosen)

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose random actions for each owned territory.

        Each territory randomly picks from its valid actions:
        - STAY (grow)
        - SEND_HALF to any neighbor
        - SEND_ALL to any neighbor
        """
        actions = []

        for pos in state.board.positions_owned_by(player):
            territory = state.board.get(pos)
            stones = territory.stones

            # Get all valid actions for this territory
            valid = get_valid_actions(pos, stones, config.board_size)

            # Pick randomly
            move_type, dest, count = self._rng.choice(valid)
            action = create_action_from_move_type(pos, move_type, dest, stones)
            actions.append(action)

        return PlayerTurnActions(player=player, actions=tuple(actions))
