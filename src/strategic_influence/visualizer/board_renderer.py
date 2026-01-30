"""Simplified board rendering.

V6: 3-option movement system.
Stones scale with count. Shows action arrows for planned moves.
"""

import pygame
from typing import Optional
import math

from ..types import Owner, Position, MoveType, calculate_half
from .constants import (
    BOARD_SIZE, CELL_SIZE, BOARD_LEFT, BOARD_TOP,
    COLOR_BG, COLOR_GRID, COLOR_SPOT,
    COLOR_PLAYER_1, COLOR_PLAYER_2,
    COLOR_TEXT_ON_WHITE, COLOR_TEXT_ON_BLACK,
    STONE_RADIUS, SPOT_RADIUS,
)
from .state import VisualizerState, Phase


# Stone sizing
MIN_RADIUS = 20   # Radius for 1 stone
MAX_RADIUS = 38   # Max radius for many stones
TRANSIT_SCALE = 0.5  # In-transit stones are half size


def get_stone_radius(stones: int) -> int:
    """Get stone radius based on count. More stones = bigger."""
    if stones <= 1:
        return MIN_RADIUS
    # Scale up with more stones, capped at MAX_RADIUS
    extra = min(stones - 1, 8) * 2
    return min(MIN_RADIUS + extra, MAX_RADIUS)


def get_pos_center(pos: Position) -> tuple[int, int]:
    """Get screen coordinates for a board position."""
    screen_row = BOARD_SIZE - 1 - pos.row
    x = BOARD_LEFT + pos.col * CELL_SIZE
    y = BOARD_TOP + screen_row * CELL_SIZE
    return (x, y)


def screen_to_board(screen_pos: tuple[int, int]) -> Optional[Position]:
    """Convert screen coordinates to board position."""
    x, y = screen_pos

    col = round((x - BOARD_LEFT) / CELL_SIZE)
    screen_row = round((y - BOARD_TOP) / CELL_SIZE)
    row = BOARD_SIZE - 1 - screen_row

    if not (0 <= col < BOARD_SIZE and 0 <= row < BOARD_SIZE):
        return None

    # Check distance to intersection
    center = get_pos_center(Position(row, col))
    dx, dy = x - center[0], y - center[1]
    if dx * dx + dy * dy > (CELL_SIZE * 0.45) ** 2:
        return None

    return Position(row, col)


def render_board(surface: pygame.Surface, state: VisualizerState, fonts: dict) -> None:
    """Render the game board."""
    # Draw grid lines
    for i in range(BOARD_SIZE):
        x = BOARD_LEFT + i * CELL_SIZE
        y1, y2 = BOARD_TOP, BOARD_TOP + (BOARD_SIZE - 1) * CELL_SIZE
        pygame.draw.line(surface, COLOR_GRID, (x, y1), (x, y2), 2)

        y = BOARD_TOP + i * CELL_SIZE
        x1, x2 = BOARD_LEFT, BOARD_LEFT + (BOARD_SIZE - 1) * CELL_SIZE
        pygame.draw.line(surface, COLOR_GRID, (x1, y), (x2, y), 2)

    board = state.game_state.board

    # Draw spots at empty intersections
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            pos = Position(row, col)
            center = get_pos_center(pos)

            if board.get_owner(pos) == Owner.NEUTRAL:
                pygame.draw.circle(surface, COLOR_SPOT, center, SPOT_RADIUS)

                # During setup, highlight valid positions
                if state.phase == Phase.SETUP:
                    if pos.is_in_setup_zone(BOARD_SIZE, Owner.PLAYER_1):
                        pygame.draw.circle(surface, COLOR_PLAYER_1, center, SPOT_RADIUS + 4, 2)
            else:
                # Render stone with scaling
                stones = board.get_stones(pos)
                render_stone(surface, center, board.get_owner(pos), stones, fonts)

    # Render selection highlight (simple ring around selected stone)
    if state.selected_territory:
        center = get_pos_center(state.selected_territory)
        stones = board.get_stones(state.selected_territory)
        radius = get_stone_radius(stones)
        # Use a slightly lighter version of the stone color for highlight
        owner = board.get_owner(state.selected_territory)
        if owner == Owner.PLAYER_1:
            highlight = (255, 255, 255)
        else:
            highlight = (100, 100, 105)
        pygame.draw.circle(surface, highlight, center, radius + 5, 3)

    # Draw arrows for pending actions
    for source, command in state.pending_actions.actions.items():
        if command.move_type != MoveType.STAY and command.destination:
            src_center = get_pos_center(source)
            dest_center = get_pos_center(command.destination)

            # Draw arrow from source to destination
            owner = board.get_owner(source)
            arrow_color = (200, 200, 255) if owner == Owner.PLAYER_1 else (255, 200, 200)

            # Calculate arrow points
            dx = dest_center[0] - src_center[0]
            dy = dest_center[1] - src_center[1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                # Normalize
                dx, dy = dx / dist, dy / dist

                # Start after source stone, end before destination
                stones = board.get_stones(source)
                src_radius = get_stone_radius(stones) + 5
                start_x = src_center[0] + dx * src_radius
                start_y = src_center[1] + dy * src_radius
                end_x = dest_center[0] - dx * 20
                end_y = dest_center[1] - dy * 20

                # Arrow line
                pygame.draw.line(surface, arrow_color, (start_x, start_y), (end_x, end_y), 3)

                # Arrowhead
                head_size = 10
                angle = math.atan2(dy, dx)
                left_angle = angle + 2.5
                right_angle = angle - 2.5
                left_x = end_x - head_size * math.cos(left_angle)
                left_y = end_y - head_size * math.sin(left_angle)
                right_x = end_x - head_size * math.cos(right_angle)
                right_y = end_y - head_size * math.sin(right_angle)
                pygame.draw.polygon(surface, arrow_color, [
                    (end_x, end_y),
                    (left_x, left_y),
                    (right_x, right_y),
                ])

                # Show count being sent
                half = calculate_half(stones)
                count = half if command.move_type == MoveType.SEND_HALF else stones
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                text = fonts["small"].render(str(count), True, arrow_color)
                text_rect = text.get_rect(center=(mid_x, mid_y - 10))
                surface.blit(text, text_rect)


def render_stone(
    surface: pygame.Surface,
    center: tuple[int, int],
    owner: Owner,
    stones: int,
    fonts: dict,
) -> None:
    """Render a stone with number. Size scales with count."""
    if owner == Owner.PLAYER_1:
        fill = COLOR_PLAYER_1
        text_color = COLOR_TEXT_ON_WHITE
    else:
        fill = COLOR_PLAYER_2
        text_color = COLOR_TEXT_ON_BLACK

    radius = get_stone_radius(stones)

    # Stone circle
    pygame.draw.circle(surface, fill, center, radius)

    # Border for visibility
    border_color = (150, 150, 145) if owner == Owner.PLAYER_1 else (80, 80, 85)
    pygame.draw.circle(surface, border_color, center, radius, 2)

    # Stone count
    text = fonts["stone"].render(str(stones), True, text_color)
    text_rect = text.get_rect(center=center)
    surface.blit(text, text_rect)


def render_transit_stone(
    surface: pygame.Surface,
    center: tuple[int, int],
    owner: Owner,
    count: int,
    fonts: dict,
) -> None:
    """Render an in-transit stone (smaller, on the line)."""
    if owner == Owner.PLAYER_1:
        fill = COLOR_PLAYER_1
        text_color = COLOR_TEXT_ON_WHITE
    else:
        fill = COLOR_PLAYER_2
        text_color = COLOR_TEXT_ON_BLACK

    # Half the size of a normal stone
    radius = int(get_stone_radius(count) * TRANSIT_SCALE)

    # Stone circle
    pygame.draw.circle(surface, fill, center, radius)

    # Border
    border_color = (150, 150, 145) if owner == Owner.PLAYER_1 else (80, 80, 85)
    pygame.draw.circle(surface, border_color, center, radius, 2)

    # Count text (use smaller font)
    text = fonts["small"].render(str(count), True, text_color)
    text_rect = text.get_rect(center=center)
    surface.blit(text, text_rect)
