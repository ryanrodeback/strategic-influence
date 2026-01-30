"""Board and game state rendering for CLI.

This module provides functions for displaying the game board
and other game information in the terminal using Rich.
"""

import time
from typing import Callable

from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
from rich import box

from ..types import Board, Owner, Position, GameState, TurnResult, PlayerMove, ResolutionResult
from ..config import GameConfig
from ..influence import calculate_influence_map, calculate_probabilities


console = Console()

# Column labels for chess notation (A-E for 5x5, extends if needed)
COL_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def pos_to_chess(pos: Position) -> str:
    """Convert Position to chess notation (e.g., A1, B3)."""
    col_letter = COL_LABELS[pos.col]
    row_number = pos.row + 1  # 1-indexed
    return f"{col_letter}{row_number}"


def chess_to_pos(notation: str, board_size: int) -> Position | None:
    """Convert chess notation to Position. Returns None if invalid."""
    notation = notation.strip().upper()
    if len(notation) < 2:
        return None

    col_letter = notation[0]
    row_str = notation[1:]

    if col_letter not in COL_LABELS[:board_size]:
        return None

    try:
        row_num = int(row_str)
    except ValueError:
        return None

    if row_num < 1 or row_num > board_size:
        return None

    col = COL_LABELS.index(col_letter)
    row = row_num - 1  # Convert to 0-indexed

    return Position(row, col)


def get_cell_style(owner: Owner) -> str:
    """Get Rich style for a cell based on owner."""
    if owner == Owner.PLAYER_1:
        return "bold cyan"
    elif owner == Owner.PLAYER_2:
        return "bold red"
    return "dim white"


def get_cell_symbol(owner: Owner, config: GameConfig) -> str:
    """Get display symbol for a cell."""
    symbols = config.display.symbols
    if owner == Owner.PLAYER_1:
        return symbols.player1
    elif owner == Owner.PLAYER_2:
        return symbols.player2
    return symbols.neutral


def create_board_table(
    board: Board,
    config: GameConfig,
    title: str | None = None,
    highlight_cells: dict[Position, str] | None = None,
    attention_p1: dict[Position, int] | None = None,
    attention_p2: dict[Position, int] | None = None,
) -> Table:
    """Create a Rich Table representing the board.

    Args:
        board: Board state to render.
        config: Game configuration.
        title: Optional title for the table.
        highlight_cells: Dict of positions to highlight styles.
        attention_p1: Player 1's attention allocations to show.
        attention_p2: Player 2's attention allocations to show.
    """
    highlight = highlight_cells or {}
    attn_p1 = attention_p1 or {}
    attn_p2 = attention_p2 or {}

    table = Table(
        title=title,
        show_header=True,
        header_style="bold",
        box=None,
        padding=(0, 1),
        collapse_padding=True,
    )

    # Add column headers (A, B, C, D, E)
    table.add_column("", style="dim", width=3, justify="right")
    for c in range(board.size):
        table.add_column(COL_LABELS[c], justify="center", width=5)

    for row in range(board.size):
        cells = [f"{row + 1}"]  # Row number (1-indexed)

        for col in range(board.size):
            pos = Position(row, col)
            owner = board.get_owner(pos)
            symbol = get_cell_symbol(owner, config)
            style = get_cell_style(owner)

            # Build cell content
            cell_text = Text()

            # Check for attention markers
            p1_attn = attn_p1.get(pos, 0)
            p2_attn = attn_p2.get(pos, 0)

            if p1_attn > 0 or p2_attn > 0:
                # Show attention counts above/below symbol
                if p1_attn > 0:
                    cell_text.append(f"+{p1_attn}", style="cyan")
                else:
                    cell_text.append("  ")
                cell_text.append(symbol, style=style)
                if p2_attn > 0:
                    cell_text.append(f"+{p2_attn}", style="red")
            else:
                cell_text.append(f" {symbol} ", style=style)

            # Apply highlight if present
            if pos in highlight:
                cell_text.stylize(highlight[pos])

            cells.append(cell_text)

        table.add_row(*cells)

    return table


def render_board(
    board: Board,
    config: GameConfig,
    title: str | None = None,
) -> None:
    """Render the board to console."""
    table = create_board_table(board, config, title)
    console.print()
    console.print(Align.center(table))


def render_scoreboard(state: GameState, config: GameConfig) -> Text:
    """Create a scoreboard line."""
    counts = state.board.count_territories()

    content = Text()
    content.append("You: ", style="bold cyan")
    content.append(f"{counts[Owner.PLAYER_1]}", style="cyan")
    content.append("  |  ")
    content.append("Opponent: ", style="bold red")
    content.append(f"{counts[Owner.PLAYER_2]}", style="red")
    content.append("  |  ")
    content.append("Neutral: ", style="dim")
    content.append(f"{counts[Owner.NEUTRAL]}", style="dim")
    content.append("  |  ")
    content.append(f"Turn {state.current_turn}/{config.num_turns}", style="bold")

    return content


def render_game_state(state: GameState, config: GameConfig) -> None:
    """Render the current game state."""
    console.clear()
    console.print()
    console.print(Align.center(Text("STRATEGIC INFLUENCE", style="bold cyan")))
    console.print()
    console.print(Align.center(render_scoreboard(state, config)))
    render_board(state.board, config)
    console.print()


def render_attention_phase(
    state: GameState,
    config: GameConfig,
    p1_move: PlayerMove,
    p2_move: PlayerMove,
) -> None:
    """Render the board with attention allocations shown."""
    console.clear()
    console.print()
    console.print(Align.center(Text("ATTENTION PHASE", style="bold yellow")))
    console.print()
    console.print(Align.center(render_scoreboard(state, config)))

    # Convert moves to attention dicts
    attn_p1 = {a.position: a.amount for a in p1_move.allocations}
    attn_p2 = {a.position: a.amount for a in p2_move.allocations}

    table = create_board_table(
        state.board, config,
        attention_p1=attn_p1,
        attention_p2=attn_p2,
    )
    console.print()
    console.print(Align.center(table))

    # Show allocation summary
    console.print()
    p1_summary = " ".join(f"{pos_to_chess(a.position)}" for a in p1_move.allocations for _ in range(a.amount))
    p2_summary = " ".join(f"{pos_to_chess(a.position)}" for a in p2_move.allocations for _ in range(a.amount))
    console.print(f"[cyan]You:[/cyan] {p1_summary}")
    console.print(f"[red]Opponent:[/red] {p2_summary}")
    console.print()


def animate_resolution(
    board_before: Board,
    board_after: Board,
    resolutions: tuple[ResolutionResult, ...],
    p1_move: PlayerMove,
    p2_move: PlayerMove,
    config: GameConfig,
    delay: float = 0.5,
) -> None:
    """Animate the resolution phase with focus on contested/changed cells."""

    # Find contested cells (both players allocated attention)
    p1_positions = {a.position for a in p1_move.allocations}
    p2_positions = {a.position for a in p2_move.allocations}
    contested = p1_positions & p2_positions

    # Find cells that changed
    changed = [r for r in resolutions if r.changed]

    # Cells to highlight (contested or changed)
    interesting_cells = contested | {r.position for r in changed}

    if not interesting_cells:
        console.print("[dim]No contested cells this turn.[/dim]")
        time.sleep(delay)
        return

    console.print(Align.center(Text("RESOLUTION", style="bold magenta")))
    console.print()

    # Show each interesting cell's resolution
    for res in resolutions:
        if res.position not in interesting_cells:
            continue

        pos_name = pos_to_chess(res.position)
        probs = res.probabilities

        # Build the resolution line
        line = Text()
        line.append(f"  {pos_name}: ", style="bold")

        # Show probabilities
        line.append(f"You {probs[0]:.0%}", style="cyan")
        line.append(" vs ")
        line.append(f"Opp {probs[1]:.0%}", style="red")
        line.append(" vs ")
        line.append(f"Neutral {probs[2]:.0%}", style="dim")
        line.append(" → ")

        # Show outcome
        if res.new_owner == Owner.PLAYER_1:
            line.append("YOU", style="bold cyan reverse")
        elif res.new_owner == Owner.PLAYER_2:
            line.append("OPPONENT", style="bold red reverse")
        else:
            line.append("NEUTRAL", style="dim reverse")

        if res.changed:
            line.append(" !")

        console.print(line)
        time.sleep(delay * 0.3)

    console.print()


def render_turn_summary(
    turn_result: TurnResult,
    config: GameConfig,
) -> None:
    """Render a summary after resolution."""
    changes = turn_result.changes

    if changes:
        console.print(f"[bold]{len(changes)} cell(s) changed this turn.[/bold]")

        # Highlight changed cells on the board
        highlights = {}
        for c in changes:
            if c.new_owner == Owner.PLAYER_1:
                highlights[c.position] = "on cyan"
            elif c.new_owner == Owner.PLAYER_2:
                highlights[c.position] = "on red"
            else:
                highlights[c.position] = "on white"

        table = create_board_table(
            turn_result.board_after, config,
            highlight_cells=highlights,
        )
        console.print()
        console.print(Align.center(table))
    else:
        console.print("[dim]No cells changed this turn.[/dim]")
        render_board(turn_result.board_after, config)


def render_game_over(state: GameState, config: GameConfig) -> None:
    """Render the game over screen."""
    console.clear()
    counts = state.board.count_territories()

    if state.winner is None:
        result_text = "[yellow bold]DRAW![/yellow bold]"
        style = "yellow"
    elif state.winner == Owner.PLAYER_1:
        result_text = "[cyan bold]YOU WIN![/cyan bold]"
        style = "cyan"
    else:
        result_text = "[red bold]OPPONENT WINS![/red bold]"
        style = "red"

    console.print()
    console.print(Panel(
        Align.center(Text.from_markup(f"""
{result_text}

[cyan]You:[/cyan] {counts[Owner.PLAYER_1]} territories
[red]Opponent:[/red] {counts[Owner.PLAYER_2]} territories
[dim]Neutral:[/dim] {counts[Owner.NEUTRAL]} territories
""")),
        title="[bold]GAME OVER[/bold]",
        style=style,
    ))

    render_board(state.board, config, title="Final Board")


def render_welcome() -> None:
    """Render the welcome message."""
    console.clear()
    console.print()
    console.print(Panel(
        Align.center(Text.from_markup("""
[bold cyan]STRATEGIC INFLUENCE[/bold cyan]

A turn-based territorial strategy game

[dim]Control the board by allocating attention.
Each turn, spend 5 attention across the grid.
Influence determines probability of control.
Most territory after 5 turns wins.[/dim]
""")),
        style="cyan",
    ))


def render_input_help(config: GameConfig) -> None:
    """Show input format help."""
    max_col = COL_LABELS[config.board_size - 1]
    console.print(f"[dim]Enter positions using chess notation (A1-{max_col}{config.board_size})[/dim]")
    console.print(f"[dim]Repeat a position to allocate more attention to it[/dim]")
    console.print(f"[dim]Example: 'C3 C3 C3 B3 D3' = 3 attention on C3, 1 each on B3 and D3[/dim]")
    console.print()


def get_player_input(config: GameConfig) -> list[Position]:
    """Get player's attention allocation via chess notation input.

    Returns list of positions (repeats indicate multiple attention).
    """
    while True:
        render_input_help(config)

        try:
            user_input = console.input("[cyan]Your attention → [/cyan]").strip()
        except EOFError:
            return []

        if not user_input:
            console.print("[red]Please enter your allocation.[/red]")
            continue

        # Parse positions
        tokens = user_input.split()
        positions = []
        valid = True

        for token in tokens:
            pos = chess_to_pos(token, config.board_size)
            if pos is None:
                console.print(f"[red]Invalid position: {token}[/red]")
                valid = False
                break
            positions.append(pos)

        if not valid:
            continue

        # Check total
        if len(positions) != config.attention_per_turn:
            console.print(f"[red]You must allocate exactly {config.attention_per_turn} attention (you entered {len(positions)})[/red]")
            continue

        return positions


def render_simulation_progress(completed: int, total: int) -> None:
    """Render simulation progress."""
    pct = completed / total * 100
    console.print(f"\rSimulating: {completed}/{total} ({pct:.0f}%)", end="")
    if completed == total:
        console.print()
