"""Terminal renderer for March of Empires."""

from __future__ import annotations

from ..types import (
    Player,
    HexCoord,
    CornerCoord,
    CornerDirection,
    GameBoard,
    GameState,
    generate_hex_board,
)
from ..config import GameConfig
from ..engine import calculate_score


def render_board(board: GameBoard, config: GameConfig | None = None) -> str:
    """Render the game board as ASCII art.

    Uses a simplified hex representation where each hex is shown
    with its control status and any armies/settlements.
    """
    radius = board.radius
    lines: list[str] = []

    # Calculate hex ownership for display
    p1_hexes = board.friendly_hexes(Player.PLAYER_1)
    p2_hexes = board.friendly_hexes(Player.PLAYER_2)

    # Build hex grid representation
    # We'll use offset coordinates for display
    # Row by row from top to bottom

    for r in range(-radius, radius + 1):
        # Calculate indent for this row
        indent = " " * (abs(r) * 2)
        row_hexes = []

        for q in range(-radius, radius + 1):
            hex_coord = HexCoord(q, r)
            if not hex_coord.is_valid(radius):
                continue

            # Determine hex symbol
            armies_here = board.armies_at(hex_coord)
            p1_armies = sum(1 for a in armies_here if a.owner == Player.PLAYER_1)
            p2_armies = sum(1 for a in armies_here if a.owner == Player.PLAYER_2)

            if p1_armies > 0 and p2_armies > 0:
                symbol = "!"  # Contested
            elif p1_armies > 0:
                symbol = str(min(p1_armies, 9))
            elif p2_armies > 0:
                symbol = str(min(p2_armies, 9)).lower()
            elif hex_coord in p1_hexes and hex_coord in p2_hexes:
                symbol = "X"  # Disputed
            elif hex_coord in p1_hexes:
                symbol = "1"
            elif hex_coord in p2_hexes:
                symbol = "2"
            else:
                symbol = "."

            row_hexes.append(f"[{symbol}]")

        if row_hexes:
            lines.append(indent + " ".join(row_hexes))

    # Add legend
    lines.append("")
    lines.append("Legend: [.]=neutral [1]=P1 territory [2]=P2 territory [X]=disputed")
    lines.append("        [N]=P1 armies [n]=P2 armies [!]=contested")

    return "\n".join(lines)


def render_game_state(state: GameState, config: GameConfig | None = None) -> str:
    """Render complete game state including scores and status."""
    lines: list[str] = []

    # Header
    lines.append("=" * 50)
    lines.append(f"March of Empires - Turn {state.current_turn}")
    lines.append(f"Phase: {state.phase.name}")
    if not state.is_complete:
        lines.append(f"Active Player: {state.active_player}")
    lines.append("=" * 50)

    # Scores
    p1_score = calculate_score(state.board, Player.PLAYER_1)
    p2_score = calculate_score(state.board, Player.PLAYER_2)
    p1_settlements = state.board.settlement_count(Player.PLAYER_1)
    p2_settlements = state.board.settlement_count(Player.PLAYER_2)
    p1_armies = state.board.army_count(Player.PLAYER_1)
    p2_armies = state.board.army_count(Player.PLAYER_2)

    lines.append("")
    lines.append(f"Player 1: {p1_score} hexes, {p1_settlements} settlements, {p1_armies} armies")
    lines.append(f"Player 2: {p2_score} hexes, {p2_settlements} settlements, {p2_armies} armies")

    if state.is_complete:
        lines.append("")
        if state.winner:
            lines.append(f"*** WINNER: {state.winner} ***")
        else:
            lines.append("*** DRAW ***")

    # Board
    lines.append("")
    lines.append(render_board(state.board, config))

    # Settlement positions
    lines.append("")
    lines.append("Settlements:")
    for settlement in sorted(state.board.settlements, key=lambda s: (s.owner.value, s.id)):
        lines.append(f"  {settlement.owner}: {settlement.position}")

    return "\n".join(lines)


def render_compact(state: GameState) -> str:
    """Render a compact one-line summary."""
    p1_score = calculate_score(state.board, Player.PLAYER_1)
    p2_score = calculate_score(state.board, Player.PLAYER_2)

    if state.is_complete:
        winner = state.winner.name if state.winner else "DRAW"
        return f"Turn {state.current_turn}: P1={p1_score} P2={p2_score} -> {winner}"
    else:
        return f"Turn {state.current_turn}: P1={p1_score} P2={p2_score} ({state.active_player}'s turn)"
