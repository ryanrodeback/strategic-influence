"""Constants for the simplified Pygame visualizer.

V5: Minimal - simple grid, simple stones with numbers.
"""

# Window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
FPS = 60

# Colors (RGB tuples)
COLOR_BG = (30, 30, 35)           # Dark background
COLOR_GRID = (80, 80, 90)         # Grid lines
COLOR_SPOT = (60, 60, 70)         # Empty intersection spots

COLOR_PLAYER_1 = (230, 230, 225)  # White stones
COLOR_PLAYER_2 = (40, 40, 45)     # Black stones
COLOR_TEXT_ON_WHITE = (30, 30, 35)
COLOR_TEXT_ON_BLACK = (220, 220, 215)

COLOR_SELECTED = (255, 200, 50)   # Gold selection
COLOR_PENDING = (100, 200, 100)   # Green for pending moves
COLOR_TEXT = (200, 200, 195)      # UI text
COLOR_TEXT_DIM = (120, 120, 115)  # Dimmed text

# Board layout
BOARD_SIZE = 5
CELL_SIZE = 90
BOARD_MARGIN = 80

# Computed
BOARD_LEFT = BOARD_MARGIN
BOARD_TOP = 100
BOARD_WIDTH = CELL_SIZE * (BOARD_SIZE - 1)
BOARD_HEIGHT = CELL_SIZE * (BOARD_SIZE - 1)

# Stone display
STONE_RADIUS = 32
SPOT_RADIUS = 8

# Font sizes
FONT_LARGE = 28
FONT_MEDIUM = 20
FONT_SMALL = 16
FONT_STONE = 22
