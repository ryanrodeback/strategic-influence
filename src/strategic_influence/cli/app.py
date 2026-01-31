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
from ..types import Owner, Position, TurnActions, SetupAction, PlayerTurnActions
from ..engine import create_game, apply_turn, apply_setup
from ..agents import RandomAgent, DefensiveAgent, HumanAgent, GreedyStrategicAgent
from ..agents.protocol import Agent
from ..simulation import run_simulation, run_parameter_sweep, ParameterSweep
from ..simulation.statistics import analysis_report

console = Console()


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
    elif agent_type == "greedy" or agent_type == "greedy_strategic":
        return GreedyStrategicAgent(seed=seed)
    elif agent_type == "defensive":
        return DefensiveAgent(seed=seed)
    else:
        raise typer.BadParameter(
            f"Unknown agent type: {agent_type}. "
            f"Valid options: human, random, greedy, greedy_strategic, defensive"
        )


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
        help="Opponent type: random, greedy, defensive",
    ),
    seed: Optional[int] = typer.Option(
        None,
        "--seed", "-s",
        help="Random seed for reproducibility",
    ),
) -> None:
    """Play a game against an AI opponent.

    NOTE: Human player support requires visualizer integration.
    For now, this command simulates two AI players.
    """
    config = load_game_config(config_file)

    console.print("\n[bold]Strategic Influence[/bold]")
    console.print(f"[dim]Playing vs: {opponent}[/dim]\n")

    # Create opponent
    opp = get_agent(opponent, seed=(seed + 1000 if seed else None))

    # Create human player (as random for now, since interactive play needs renderer)
    player1 = RandomAgent(seed=seed)

    # Play game
    from ..engine import simulate_game
    state = simulate_game(config, player1, opp, seed=seed)

    # Show results
    console.print(state.board)
    console.print(f"\n[bold]Game Over[/bold]")
    counts = state.board.count_territories()
    console.print(f"Player 1: {counts[Owner.PLAYER_1]} territories")
    console.print(f"Player 2: {counts[Owner.PLAYER_2]} territories")
    if state.winner:
        console.print(f"[green]Winner: {state.winner}[/green]")
    else:
        console.print("[yellow]Result: Draw[/yellow]")


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
        help="Player 1 type: random, greedy, defensive",
    ),
    player2: str = typer.Option(
        "greedy",
        "--p2",
        help="Player 2 type: random, greedy, defensive",
    ),
    seed: Optional[int] = typer.Option(
        None,
        "--seed", "-s",
        help="Random seed for reproducibility",
    ),
) -> None:
    """Watch two AI players compete."""
    config = load_game_config(config_file)

    p1 = get_agent(player1, seed=seed)
    p2 = get_agent(player2, seed=(seed + 1000 if seed else None))

    console.print(f"\n[bold]Watching: [cyan]{p1.name}[/cyan] vs [red]{p2.name}[/red][/bold]\n")

    from ..engine import simulate_game
    state = simulate_game(config, p1, p2, seed=seed)

    # Show final board
    console.print(state.board)
    console.print(f"\n[bold]Game Over (Turn {state.current_turn})[/bold]")
    counts = state.board.count_territories()
    console.print(f"[cyan]{p1.name}[/cyan]: {counts[Owner.PLAYER_1]} territories")
    console.print(f"[red]{p2.name}[/red]: {counts[Owner.PLAYER_2]} territories")
    if state.winner:
        winner_name = p1.name if state.winner == Owner.PLAYER_1 else p2.name
        console.print(f"[green]Winner: {winner_name}[/green]")
    else:
        console.print("[yellow]Result: Draw[/yellow]")


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
