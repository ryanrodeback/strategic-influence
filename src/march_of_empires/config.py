"""Configuration for March of Empires.

All game parameters are defined here as frozen dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MovementConfig:
    """Movement point costs."""

    points_per_turn: int = 2
    friendly_hex_cost: int = 1
    neutral_hex_cost: int = 2
    enemy_hex_cost: int = 2
    hex_corner_transition: int = 1
    settle_cost: int = 2  # Must equal points_per_turn (full turn to settle)


@dataclass(frozen=True)
class CaptureConfig:
    """Settlement capture requirements."""

    undefended_armies_required: int = 2
    defended_armies_required: int = 3


@dataclass(frozen=True)
class GameRulesConfig:
    """Core game rules."""

    board_radius: int = 3  # Radius-3 hexagonal board = 37 hexes
    num_turns: int = 25  # Each player gets ~12-13 turns
    movement: MovementConfig = field(default_factory=MovementConfig)
    capture: CaptureConfig = field(default_factory=CaptureConfig)


@dataclass(frozen=True)
class SimulationConfig:
    """Simulation settings."""

    default_num_games: int = 100
    parallel_workers: int = 4
    random_seed: int | None = None


@dataclass(frozen=True)
class DisplayConfig:
    """Display settings."""

    player_1_symbol: str = "1"
    player_2_symbol: str = "2"
    neutral_symbol: str = "."
    army_symbol: str = "A"
    settlement_symbol: str = "S"


@dataclass(frozen=True)
class GameConfig:
    """Complete game configuration."""

    game: GameRulesConfig = field(default_factory=GameRulesConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)

    @property
    def board_radius(self) -> int:
        return self.game.board_radius

    @property
    def num_turns(self) -> int:
        return self.game.num_turns

    @property
    def movement(self) -> MovementConfig:
        return self.game.movement

    @property
    def capture(self) -> CaptureConfig:
        return self.game.capture


def create_default_config() -> GameConfig:
    """Create default game configuration."""
    return GameConfig()
