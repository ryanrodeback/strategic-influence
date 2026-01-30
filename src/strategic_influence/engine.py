"""Game engine for Strategic Influence.

V3: Stone-count with split movement support.

This module contains the core game flow logic:
- Setup phase (each player places 1 stone in their zone)
- Turn execution (per territory: GROW or split MOVE)
- Combat resolution
- Win condition checking

All functions are pure - they take state and return new state.
"""

from random import Random
from typing import Protocol

from .types import (
    Owner,
    Position,
    TerritoryBoard,
    Territory,
    TurnActions,
    TurnResult,
    GameState,
    GamePhase,
    SetupAction,
    PlayerTurnActions,
    TerritoryAction,
    StoneMovement,
    create_empty_board,
    create_initial_state,
    create_territory,
    create_grow_action,
    create_move_action,
    create_simple_move_action,
)
from .config import GameConfig
from .resolution import resolve_turn


class PlayerProtocol(Protocol):
    """Interface that all players must implement."""

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose where to place initial stone during setup.

        Args:
            state: Current game state (in SETUP phase).
            player: Which player this is.
            config: Game configuration.

        Returns:
            SetupAction with position in player's setup zone.
        """
        ...

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose actions for all owned territories.

        Args:
            state: Current game state.
            player: Which player this is.
            config: Game configuration.

        Returns:
            PlayerTurnActions with one action per owned territory.
        """
        ...

    def reset(self) -> None:
        """Reset for a new game."""
        ...


def create_game(config: GameConfig) -> GameState:
    """Create a new game in setup phase.

    Args:
        config: Game configuration.

    Returns:
        Initial GameState ready for setup.
    """
    return create_initial_state(config.board_size)


def validate_setup_action(
    action: SetupAction,
    state: GameState,
    config: GameConfig,
) -> tuple[bool, str | None]:
    """Validate a setup action.

    Checks:
    - Position is within board bounds
    - Position is in player's setup zone
    - Position is unoccupied

    Args:
        action: The setup action to validate.
        state: Current game state.
        config: Game configuration.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not action.position.is_valid(config.board_size):
        return False, f"Position {action.position} is outside the board"

    if not action.position.is_in_setup_zone(config.board_size, action.player):
        return False, f"Position {action.position} is not in {action.player}'s setup zone"

    if state.board.get_owner(action.position) != Owner.NEUTRAL:
        return False, f"Position {action.position} is already occupied"

    return True, None


def apply_setup(
    state: GameState,
    action: SetupAction,
    config: GameConfig,
) -> GameState:
    """Apply a setup action.

    Args:
        state: Current game state.
        action: Setup action to apply.
        config: Game configuration.

    Returns:
        New GameState with the stone placed.

    Raises:
        ValueError: If setup action is invalid.
    """
    if state.phase != GamePhase.SETUP:
        raise ValueError("Cannot apply setup outside of SETUP phase")

    if action.player in state.setup_complete:
        raise ValueError(f"{action.player} has already completed setup")

    valid, error = validate_setup_action(action, state, config)
    if not valid:
        raise ValueError(f"Invalid setup action: {error}")

    # Place stone
    stones = config.game.setup.stones_per_placement
    new_board = state.board.with_stones(action.position, action.player, stones)

    # Mark player as complete
    new_setup_complete = state.setup_complete + (action.player,)

    # Check if setup is complete (both players done)
    if Owner.PLAYER_1 in new_setup_complete and Owner.PLAYER_2 in new_setup_complete:
        new_phase = GamePhase.PLAYING
    else:
        new_phase = GamePhase.SETUP

    return GameState(
        board=new_board,
        phase=new_phase,
        current_turn=0,
        turn_history=state.turn_history,
        setup_complete=new_setup_complete,
        winner=None,
    )


def validate_turn_actions(
    actions: PlayerTurnActions,
    state: GameState,
    config: GameConfig,
) -> tuple[bool, str | None]:
    """Validate a player's turn actions.

    Checks:
    - Each owned territory has exactly one action
    - MOVE actions have valid movements (split or single)
    - Movements go to adjacent positions
    - Total stones moved doesn't exceed available

    Args:
        actions: The actions to validate.
        state: Current game state.
        config: Game configuration.

    Returns:
        Tuple of (is_valid, error_message).
    """
    player = actions.player
    owned_positions = state.board.positions_owned_by(player)
    action_positions = frozenset(a.position for a in actions.actions)

    # Check all owned territories have an action
    missing = owned_positions - action_positions
    if missing:
        return False, f"Missing actions for territories: {missing}"

    # Check no actions for unowned territories
    extra = action_positions - owned_positions
    if extra:
        return False, f"Actions for unowned territories: {extra}"

    # Validate each action
    for action in actions.actions:
        if action.is_move:
            # Validate all movements for this territory
            territory = state.board.get(action.position)
            total_moved = 0

            for movement in action.movements:
                # Check source matches action position
                if movement.source != action.position:
                    return False, f"Movement source {movement.source} doesn't match action position {action.position}"

                # Check destination is adjacent
                neighbors = action.position.neighbors(config.board_size)
                if movement.destination not in neighbors:
                    return False, f"Movement destination {movement.destination} is not adjacent to {action.position}"

                # Check stone count is valid
                if movement.count < 1:
                    return False, f"Must move at least 1 stone"

                total_moved += movement.count

            # Check total stones moved doesn't exceed available
            if total_moved > territory.stones:
                return False, f"Cannot move {total_moved} stones from {action.position}: only {territory.stones} available"

    return True, None


def apply_turn(
    state: GameState,
    actions: TurnActions,
    config: GameConfig,
    rng: Random,
) -> GameState:
    """Apply a turn to the game state.

    Validates actions, resolves movements and combat, applies growth.

    Args:
        state: Current game state.
        actions: Both players' actions.
        config: Game configuration.
        rng: Random number generator.

    Returns:
        New GameState after the turn.

    Raises:
        ValueError: If actions are invalid or game is not in PLAYING phase.
    """
    if state.phase != GamePhase.PLAYING:
        raise ValueError("Cannot apply turn outside of PLAYING phase")

    if state.is_complete:
        raise ValueError("Cannot apply turn to completed game")

    # Validate both players' actions
    valid1, error1 = validate_turn_actions(actions.player1_actions, state, config)
    if not valid1:
        raise ValueError(f"Player 1 actions invalid: {error1}")

    valid2, error2 = validate_turn_actions(actions.player2_actions, state, config)
    if not valid2:
        raise ValueError(f"Player 2 actions invalid: {error2}")

    # Resolve the turn
    board_before = state.board
    board_after, movements, grown = resolve_turn(board_before, actions, config, rng)

    # Create turn result
    turn_result = TurnResult(
        turn_number=state.current_turn + 1,
        actions=actions,
        board_before=board_before,
        board_after=board_after,
        movements=movements,
        territories_grown=grown,
    )

    # Check if game is complete
    new_turn = state.current_turn + 1
    is_complete = new_turn >= config.num_turns

    # Determine winner if complete
    winner = None
    new_phase = GamePhase.PLAYING
    if is_complete:
        new_phase = GamePhase.COMPLETE
        winner = determine_winner(board_after)

    return GameState(
        board=board_after,
        phase=new_phase,
        current_turn=new_turn,
        turn_history=state.turn_history + (turn_result,),
        setup_complete=state.setup_complete,
        winner=winner,
    )


def determine_winner(board: TerritoryBoard) -> Owner | None:
    """Determine the winner based on territory count.

    Args:
        board: Final board state.

    Returns:
        Owner.PLAYER_1 or Owner.PLAYER_2 if there's a winner,
        None if it's a draw.
    """
    counts = board.count_territories()
    p1_count = counts[Owner.PLAYER_1]
    p2_count = counts[Owner.PLAYER_2]

    if p1_count > p2_count:
        return Owner.PLAYER_1
    elif p2_count > p1_count:
        return Owner.PLAYER_2
    else:
        return None  # Draw


def check_game_over(state: GameState, config: GameConfig) -> tuple[bool, Owner | None]:
    """Check if the game is over.

    Args:
        state: Current game state.
        config: Game configuration.

    Returns:
        Tuple of (is_over, winner). winner is None for draw or incomplete.
    """
    if state.current_turn >= config.num_turns:
        return True, determine_winner(state.board)
    return False, None


def simulate_game(
    config: GameConfig,
    player1: PlayerProtocol,
    player2: PlayerProtocol,
    seed: int | None = None,
) -> GameState:
    """Run a complete game between two players.

    Args:
        config: Game configuration.
        player1: Player 1 implementation.
        player2: Player 2 implementation.
        seed: Random seed for reproducibility.

    Returns:
        Final GameState after the game ends.
    """
    rng = Random(seed)

    # Reset players for new game
    player1.reset()
    player2.reset()

    # Initialize game
    state = create_game(config)

    # Setup phase
    setup1 = player1.choose_setup(state, Owner.PLAYER_1, config)
    state = apply_setup(state, setup1, config)

    setup2 = player2.choose_setup(state, Owner.PLAYER_2, config)
    state = apply_setup(state, setup2, config)

    # Play all turns
    while not state.is_complete:
        # Get actions from both players
        actions1 = player1.choose_actions(state, Owner.PLAYER_1, config)
        actions2 = player2.choose_actions(state, Owner.PLAYER_2, config)

        turn_actions = TurnActions(
            player1_actions=actions1,
            player2_actions=actions2,
            turn_number=state.current_turn + 1,
        )

        # Apply turn
        state = apply_turn(state, turn_actions, config, rng)

    return state


def get_game_summary(state: GameState) -> str:
    """Generate a human-readable summary of the game.

    Args:
        state: Game state to summarize.

    Returns:
        Multi-line string summary.
    """
    counts = state.board.count_territories()

    lines = [
        "Game Summary",
        "=" * 40,
        f"Turns played: {state.current_turn}",
        f"Player 1 territories: {counts[Owner.PLAYER_1]}",
        f"Player 1 total stones: {state.board.total_stones(Owner.PLAYER_1)}",
        f"Player 2 territories: {counts[Owner.PLAYER_2]}",
        f"Player 2 total stones: {state.board.total_stones(Owner.PLAYER_2)}",
        f"Neutral territories: {counts[Owner.NEUTRAL]}",
    ]

    if state.is_complete:
        if state.winner is None:
            lines.append("Result: Draw")
        else:
            lines.append(f"Result: {state.winner} wins!")
    else:
        lines.append(f"Status: {state.phase.name}")

    lines.append("")
    lines.append("Final board:")
    lines.append(str(state.board))

    return "\n".join(lines)


def create_player_actions(
    player: Owner,
    actions: list[TerritoryAction],
) -> PlayerTurnActions:
    """Create PlayerTurnActions from a list of actions."""
    return PlayerTurnActions(
        player=player,
        actions=tuple(actions),
    )
