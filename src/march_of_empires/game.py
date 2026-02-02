"""Game runner for March of Empires."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .types import (
    Player,
    GameState,
    TurnActions,
)
from .config import GameConfig, create_default_config
from .engine import (
    create_game,
    apply_setup,
    apply_turn,
    calculate_score,
)
from .agents.protocol import Agent


@dataclass(frozen=True)
class GameResult:
    """Result of a completed game."""

    winner: Player | None
    p1_score: int
    p2_score: int
    total_turns: int
    final_state: GameState


def run_game(
    player1: Agent,
    player2: Agent,
    config: GameConfig | None = None,
    on_turn: Callable[[GameState, int], None] | None = None,
    verbose: bool = False,
) -> GameResult:
    """Run a complete game between two agents.

    Args:
        player1: Agent for Player 1.
        player2: Agent for Player 2.
        config: Game configuration.
        on_turn: Optional callback after each turn.
        verbose: Print progress if True.

    Returns:
        GameResult with final outcome.
    """
    if config is None:
        config = create_default_config()

    # Reset agents
    player1.reset()
    player2.reset()

    # Create game
    state = create_game(config)

    if verbose:
        print(f"Starting game: {player1.name} vs {player2.name}")

    # Setup phase
    for player, agent in [(Player.PLAYER_1, player1), (Player.PLAYER_2, player2)]:
        corner = agent.choose_setup(state, player, config)
        state = apply_setup(state, corner, player, config)
        if verbose:
            print(f"  {player} placed settlement at {corner}")

    if verbose:
        print("Setup complete. Starting main game.")

    # Main game loop
    turn_count = 0
    while not state.is_complete:
        current = state.active_player
        agent = player1 if current == Player.PLAYER_1 else player2

        actions = agent.choose_actions(state, current, config)
        state = apply_turn(state, actions, config)

        turn_count += 1
        if on_turn:
            on_turn(state, turn_count)

        if verbose and turn_count % 10 == 0:
            p1_score = calculate_score(state.board, Player.PLAYER_1)
            p2_score = calculate_score(state.board, Player.PLAYER_2)
            print(f"  Turn {turn_count}: P1={p1_score}, P2={p2_score}")

    # Calculate final scores
    p1_score = calculate_score(state.board, Player.PLAYER_1)
    p2_score = calculate_score(state.board, Player.PLAYER_2)

    if verbose:
        print(f"Game over! Final scores: P1={p1_score}, P2={p2_score}")
        if state.winner:
            print(f"Winner: {state.winner}")
        else:
            print("Draw!")

    return GameResult(
        winner=state.winner,
        p1_score=p1_score,
        p2_score=p2_score,
        total_turns=turn_count,
        final_state=state,
    )


def run_games(
    player1: Agent,
    player2: Agent,
    num_games: int,
    config: GameConfig | None = None,
    swap_sides: bool = True,
    verbose: bool = False,
) -> list[GameResult]:
    """Run multiple games between two agents.

    Args:
        player1: First agent.
        player2: Second agent.
        num_games: Number of games to play.
        config: Game configuration.
        swap_sides: If True, play half games with swapped sides.
        verbose: Print progress if True.

    Returns:
        List of game results.
    """
    results: list[GameResult] = []

    games_per_side = num_games // 2 if swap_sides else num_games

    # Play with original sides
    for i in range(games_per_side):
        if verbose:
            print(f"Game {i + 1}/{num_games}")
        result = run_game(player1, player2, config, verbose=False)
        results.append(result)

    # Play with swapped sides
    if swap_sides:
        for i in range(num_games - games_per_side):
            if verbose:
                print(f"Game {games_per_side + i + 1}/{num_games} (swapped)")
            result = run_game(player2, player1, config, verbose=False)
            # Swap result perspective
            results.append(GameResult(
                winner=result.winner.opponent() if result.winner else None,
                p1_score=result.p2_score,
                p2_score=result.p1_score,
                total_turns=result.total_turns,
                final_state=result.final_state,
            ))

    return results
