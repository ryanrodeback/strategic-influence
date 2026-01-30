"""CLI application entry point for Strategic Influence.

This module provides the main CLI commands:
- play: Play a game between two players
- simulate: Run batch simulations
- sweep: Run parameter sweep experiments
"""

import time
from pathlib import Path
from random import Random
from typing import Optional

import typer
from rich.console import Console

from ..config import load_config, create_default_config, GameConfig
from ..types import Owner, Position, TurnMoves
from ..engine import create_game, apply_turn, create_move_from_positions
from ..agents import RandomAgent, GreedyAgent, HumanAgent
from ..agents.protocol import Agent
from ..simulation import run_simulation, run_parameter_sweep, ParameterSweep
from ..simulation.statistics import analysis_report
from .renderer import (
    render_welcome,
    render_game_state,
    render_attention_phase,
    animate_resolution,
    render_turn_summary,
    render_game_over,
    render_simulation_progress,
    get_player_input,
    console,
)


app = typer.Typer(
    name="strategic-influence",
    help="Strategic Influence - A turn-based territorial strategy game",
    no_args_is_help=True,
)


def get_agent(agent_type: str, seed: int | None = None) -> Agent:
    """Create an agent based on type string."""
    agent_type = agent_type.lower()

    if agent_type == "human":
        return HumanAgent()
    elif agent_type == "random":
        return RandomAgent(seed=seed)
    elif agent_type == "greedy":
        return GreedyAgent(seed=seed)
    else:
        raise typer.BadParameter(f"Unknown agent type: {agent_type}")


def load_game_config(config_path: Path | None) -> GameConfig:
    """Load config from file or use defaults."""
    if config_path is None:
        # Try default location
        default_path = Path("config/game_config.yaml")
        if default_path.exists():
            return load_config(default_path)
        return create_default_config()

    return load_config(config_path)


@app.command()
def play(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="Path to game configuration file",
    ),
    opponent: str = typer.Option(
        "greedy",
        "--opponent", "-o",
        help="Opponent type: random, greedy",
    ),
    seed: Optional[int] = typer.Option(
        None,
        "--seed", "-s",
        help="Random seed for reproducibility",
    ),
    animation_speed: float = typer.Option(
        0.5,
        "--speed",
        help="Animation speed (seconds per step, lower = faster)",
    ),
) -> None:
    """Play a game against an AI opponent."""
    config = load_game_config(config_file)

    render_welcome()
    time.sleep(1)

    # Create opponent
    opp = get_agent(opponent, seed=(seed + 1000 if seed else None))
    opp.reset()

    console.print(f"\n[bold]Playing against: [red]{opp.name}[/red][/bold]")
    console.print("[dim]Press Enter to start...[/dim]")
    try:
        input()
    except EOFError:
        pass

    # Initialize game
    rng = Random(seed)
    state = create_game(config)

    # Game loop
    while not state.is_complete:
        # Show current state
        render_game_state(state, config)

        console.print(f"\n[bold cyan]Turn {state.current_turn + 1}[/bold cyan]")
        console.print()

        # Get player's move
        positions = get_player_input(config)
        if not positions:
            console.print("[yellow]Game aborted.[/yellow]")
            return

        p1_move = create_move_from_positions(Owner.PLAYER_1, positions)

        # Get opponent's move
        console.print(f"\n[red]{opp.name} is thinking...[/red]")
        time.sleep(0.5)
        p2_move = opp.choose_move(state, Owner.PLAYER_2, config)

        # Show attention phase
        render_attention_phase(state, config, p1_move, p2_move)

        console.print("[dim]Press Enter to resolve...[/dim]")
        try:
            input()
        except EOFError:
            pass

        # Apply turn
        moves = TurnMoves(
            player1_move=p1_move,
            player2_move=p2_move,
            turn_number=state.current_turn + 1,
        )
        state = apply_turn(state, moves, config, rng)

        # Animate resolution
        turn_result = state.turn_history[-1]
        animate_resolution(
            turn_result.board_before,
            turn_result.board_after,
            turn_result.resolutions,
            p1_move,
            p2_move,
            config,
            delay=animation_speed,
        )

        # Show turn summary
        render_turn_summary(turn_result, config)

        if not state.is_complete:
            console.print("\n[dim]Press Enter to continue...[/dim]")
            try:
                input()
            except EOFError:
                pass

    # Game over
    render_game_over(state, config)


@app.command()
def watch(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="Path to game configuration file",
    ),
    player1: str = typer.Option(
        "random",
        "--p1",
        help="Player 1 type: random, greedy",
    ),
    player2: str = typer.Option(
        "greedy",
        "--p2",
        help="Player 2 type: random, greedy",
    ),
    seed: Optional[int] = typer.Option(
        None,
        "--seed", "-s",
        help="Random seed for reproducibility",
    ),
    animation_speed: float = typer.Option(
        0.3,
        "--speed",
        help="Animation speed (seconds per step)",
    ),
    auto: bool = typer.Option(
        False,
        "--auto",
        help="Auto-advance without waiting for Enter",
    ),
) -> None:
    """Watch two AI players compete."""
    config = load_game_config(config_file)

    p1 = get_agent(player1, seed=seed)
    p2 = get_agent(player2, seed=(seed + 1000 if seed else None))
    p1.reset()
    p2.reset()

    render_welcome()
    console.print(f"\n[bold][cyan]{p1.name}[/cyan] vs [red]{p2.name}[/red][/bold]")

    if not auto:
        console.print("[dim]Press Enter to start...[/dim]")
        try:
            input()
        except EOFError:
            pass

    rng = Random(seed)
    state = create_game(config)

    while not state.is_complete:
        render_game_state(state, config)

        console.print(f"\n[bold]Turn {state.current_turn + 1}[/bold]")
        time.sleep(animation_speed)

        # Get moves
        p1_move = p1.choose_move(state, Owner.PLAYER_1, config)
        p2_move = p2.choose_move(state, Owner.PLAYER_2, config)

        # Show attention phase
        render_attention_phase(state, config, p1_move, p2_move)
        time.sleep(animation_speed * 2)

        # Apply turn
        moves = TurnMoves(
            player1_move=p1_move,
            player2_move=p2_move,
            turn_number=state.current_turn + 1,
        )
        state = apply_turn(state, moves, config, rng)

        # Animate resolution
        turn_result = state.turn_history[-1]
        animate_resolution(
            turn_result.board_before,
            turn_result.board_after,
            turn_result.resolutions,
            p1_move,
            p2_move,
            config,
            delay=animation_speed,
        )

        render_turn_summary(turn_result, config)

        if not state.is_complete and not auto:
            console.print("\n[dim]Press Enter to continue...[/dim]")
            try:
                input()
            except EOFError:
                pass
        elif not state.is_complete:
            time.sleep(animation_speed * 2)

    render_game_over(state, config)


@app.command()
def simulate(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="Path to game configuration file",
    ),
    player1: str = typer.Option(
        "random",
        "--p1",
        help="Player 1 type: random, greedy",
    ),
    player2: str = typer.Option(
        "random",
        "--p2",
        help="Player 2 type: random, greedy",
    ),
    num_games: int = typer.Option(
        100,
        "--games", "-n",
        help="Number of games to simulate",
    ),
    seed: Optional[int] = typer.Option(
        42,
        "--seed", "-s",
        help="Random seed for reproducibility",
    ),
) -> None:
    """Run batch simulations between AI players."""
    config = load_game_config(config_file)

    console.print(f"\n[bold]Running {num_games} games...[/bold]")
    console.print(f"[cyan]Player 1:[/cyan] {player1}")
    console.print(f"[red]Player 2:[/red] {player2}")
    console.print()

    def p1_factory():
        return get_agent(player1, seed=None)

    def p2_factory():
        return get_agent(player2, seed=None)

    def progress(completed, total):
        render_simulation_progress(completed, total)

    results = run_simulation(
        config=config,
        player1_factory=p1_factory,
        player2_factory=p2_factory,
        num_games=num_games,
        base_seed=seed,
        parallel_workers=1,
        progress_callback=progress,
    )

    console.print()
    console.print(analysis_report(results))


@app.command()
def sweep(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="Path to game configuration file",
    ),
    parameter: str = typer.Argument(
        ...,
        help="Parameter path to sweep (e.g., 'influence.k_value')",
    ),
    values: str = typer.Argument(
        ...,
        help="Comma-separated values to test",
    ),
    runs: int = typer.Option(
        100,
        "--runs", "-n",
        help="Number of games per parameter value",
    ),
    player1: str = typer.Option(
        "random",
        "--p1",
        help="Player 1 type",
    ),
    player2: str = typer.Option(
        "random",
        "--p2",
        help="Player 2 type",
    ),
    seed: int = typer.Option(
        42,
        "--seed", "-s",
        help="Random seed",
    ),
) -> None:
    """Run parameter sweep experiments."""
    config = load_game_config(config_file)

    # Parse values
    try:
        parsed_values = [float(v.strip()) for v in values.split(",")]
    except ValueError:
        # Try as strings
        parsed_values = [v.strip() for v in values.split(",")]

    console.print(f"\n[bold]Parameter Sweep: {parameter}[/bold]")
    console.print(f"Values: {parsed_values}")
    console.print(f"Games per value: {runs}")
    console.print()

    sweep_def = ParameterSweep(
        path=parameter,
        values=parsed_values,
    )

    def p1_factory():
        return get_agent(player1, seed=None)

    def p2_factory():
        return get_agent(player2, seed=None)

    def progress(value, completed, total):
        console.print(f"  {parameter}={value}: {completed}/{total}")

    results = run_parameter_sweep(
        base_config=config,
        sweep=sweep_def,
        player1_factory=p1_factory,
        player2_factory=p2_factory,
        runs_per_value=runs,
        base_seed=seed,
        progress_callback=progress,
    )

    console.print()
    console.print(results.summary_table())


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
