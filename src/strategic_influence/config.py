"""Configuration loading and validation for Strategic Influence.

V2: Stone-count and combat mechanics (replacing influence-based system).

This module provides the GameConfig frozen dataclass and utilities for
loading configuration from YAML files.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class CombatConfig:
    """Configuration for combat mechanics."""
    hit_chance: float  # Probability of a hit (default 0.5)


@dataclass(frozen=True)
class GrowthConfig:
    """Configuration for territory growth."""
    stones_per_turn: int  # Stones gained when choosing GROW
    max_stones: int  # Maximum stones per territory (growth stops at this limit)


@dataclass(frozen=True)
class SetupConfig:
    """Configuration for game setup phase."""
    stones_per_placement: int  # Stones placed per territory during setup


@dataclass(frozen=True)
class GameRulesConfig:
    """Core game rules configuration."""
    board_size: int
    num_turns: int
    combat: CombatConfig
    growth: GrowthConfig
    setup: SetupConfig
    expansion_success_rate: float  # Probability per stone when expanding (1.0 = always succeeds)


@dataclass(frozen=True)
class SimulationConfig:
    """Simulation runner configuration."""
    default_num_games: int
    parallel_workers: int
    random_seed: int | None


@dataclass(frozen=True)
class DisplaySymbolsConfig:
    """Display symbol configuration."""
    player1: str
    player2: str
    neutral: str


@dataclass(frozen=True)
class DisplayBoardConfig:
    """Board display configuration."""
    cell_width: int
    show_coordinates: bool


@dataclass(frozen=True)
class DisplayVerbosityConfig:
    """Verbosity settings for game output."""
    show_combat_rolls: bool
    show_movements: bool
    show_growth: bool


@dataclass(frozen=True)
class DisplayConfig:
    """All display-related configuration."""
    symbols: DisplaySymbolsConfig
    board: DisplayBoardConfig
    verbosity: DisplayVerbosityConfig


@dataclass(frozen=True)
class RandomAIConfig:
    """Random AI configuration."""
    name: str


@dataclass(frozen=True)
class AggressiveAIWeightsConfig:
    """Weight configuration for aggressive AI."""
    attack_enemy: float
    defend_own: float
    expand_neutral: float
    stone_count_bonus: float


@dataclass(frozen=True)
class AggressiveAIConfig:
    """Aggressive AI configuration."""
    name: str
    weights: AggressiveAIWeightsConfig


@dataclass(frozen=True)
class AIConfig:
    """All AI-related configuration."""
    random: RandomAIConfig
    aggressive: AggressiveAIConfig


@dataclass(frozen=True)
class GameConfig:
    """Complete game configuration.

    This frozen dataclass contains all configurable parameters for the game.
    It is loaded from game_config.yaml and passed to all game functions.
    Being frozen (immutable) ensures thread-safety for parallel simulations.
    """
    game: GameRulesConfig
    simulation: SimulationConfig
    display: DisplayConfig
    ai: AIConfig

    @property
    def board_size(self) -> int:
        """Convenience accessor for board size."""
        return self.game.board_size

    @property
    def num_turns(self) -> int:
        """Convenience accessor for number of turns."""
        return self.game.num_turns

    @property
    def hit_chance(self) -> float:
        """Convenience accessor for combat hit chance."""
        return self.game.combat.hit_chance

    @property
    def max_stones(self) -> int:
        """Convenience accessor for maximum stones per territory."""
        return self.game.growth.max_stones

    @property
    def expansion_success_rate(self) -> float:
        """Convenience accessor for expansion success rate."""
        return self.game.expansion_success_rate


def load_config(config_path: Path | str | None = None) -> GameConfig:
    """Load game configuration from a YAML file.

    Args:
        config_path: Path to the YAML config file. If None, uses default location.

    Returns:
        GameConfig: Frozen configuration object.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        ValueError: If the config file has invalid structure.
    """
    if config_path is None:
        # Default to config/game_config.yaml relative to project root
        config_path = Path(__file__).parent.parent.parent / "config" / "game_config.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path) as f:
        raw_config = yaml.safe_load(f)

    return _parse_config(raw_config)


def _parse_config(raw: dict[str, Any]) -> GameConfig:
    """Parse raw YAML dict into typed GameConfig."""
    # Parse combat config
    combat = CombatConfig(
        hit_chance=raw.get("game", {}).get("combat", {}).get("hit_chance", 0.5),
    )

    # Parse growth config
    growth = GrowthConfig(
        stones_per_turn=raw.get("game", {}).get("growth", {}).get("stones_per_turn", 1),
        max_stones=raw.get("game", {}).get("growth", {}).get("max_stones", 10),
    )

    # Parse setup config
    setup = SetupConfig(
        stones_per_placement=raw.get("game", {}).get("setup", {}).get("stones_per_placement", 1),
    )

    game = GameRulesConfig(
        board_size=raw.get("game", {}).get("board_size", 5),
        num_turns=raw.get("game", {}).get("num_turns", 10),
        combat=combat,
        growth=growth,
        setup=setup,
        expansion_success_rate=raw.get("game", {}).get("expansion_success_rate", 1.0),
    )

    simulation = SimulationConfig(
        default_num_games=raw.get("simulation", {}).get("default_num_games", 1000),
        parallel_workers=raw.get("simulation", {}).get("parallel_workers", 4),
        random_seed=raw.get("simulation", {}).get("random_seed", None),
    )

    symbols = DisplaySymbolsConfig(
        player1=raw.get("display", {}).get("symbols", {}).get("player1", "1"),
        player2=raw.get("display", {}).get("symbols", {}).get("player2", "2"),
        neutral=raw.get("display", {}).get("symbols", {}).get("neutral", "."),
    )

    board_display = DisplayBoardConfig(
        cell_width=raw.get("display", {}).get("board", {}).get("cell_width", 5),
        show_coordinates=raw.get("display", {}).get("board", {}).get("show_coordinates", True),
    )

    verbosity = DisplayVerbosityConfig(
        show_combat_rolls=raw.get("display", {}).get("verbosity", {}).get("show_combat_rolls", True),
        show_movements=raw.get("display", {}).get("verbosity", {}).get("show_movements", True),
        show_growth=raw.get("display", {}).get("verbosity", {}).get("show_growth", True),
    )

    display = DisplayConfig(
        symbols=symbols,
        board=board_display,
        verbosity=verbosity,
    )

    random_ai = RandomAIConfig(
        name=raw.get("ai", {}).get("random", {}).get("name", "RandomBot"),
    )

    aggressive_weights = AggressiveAIWeightsConfig(
        attack_enemy=raw.get("ai", {}).get("aggressive", {}).get("weights", {}).get("attack_enemy", 1.0),
        defend_own=raw.get("ai", {}).get("aggressive", {}).get("weights", {}).get("defend_own", 0.8),
        expand_neutral=raw.get("ai", {}).get("aggressive", {}).get("weights", {}).get("expand_neutral", 0.5),
        stone_count_bonus=raw.get("ai", {}).get("aggressive", {}).get("weights", {}).get("stone_count_bonus", 0.2),
    )

    aggressive_ai = AggressiveAIConfig(
        name=raw.get("ai", {}).get("aggressive", {}).get("name", "AggressiveBot"),
        weights=aggressive_weights,
    )

    ai = AIConfig(random=random_ai, aggressive=aggressive_ai)

    return GameConfig(
        game=game,
        simulation=simulation,
        display=display,
        ai=ai,
    )


def create_default_config() -> GameConfig:
    """Create a GameConfig with default values (no file needed).

    Useful for testing and when config file is not available.
    """
    return GameConfig(
        game=GameRulesConfig(
            board_size=5,
            num_turns=20,
            combat=CombatConfig(hit_chance=1.0),  # Deterministic: always hits
            growth=GrowthConfig(stones_per_turn=1, max_stones=10),
            setup=SetupConfig(stones_per_placement=3),
            expansion_success_rate=1.0,  # Deterministic: always succeeds
        ),
        simulation=SimulationConfig(
            default_num_games=1000,
            parallel_workers=4,
            random_seed=None,
        ),
        display=DisplayConfig(
            symbols=DisplaySymbolsConfig(
                player1="1",
                player2="2",
                neutral=".",
            ),
            board=DisplayBoardConfig(
                cell_width=5,
                show_coordinates=True,
            ),
            verbosity=DisplayVerbosityConfig(
                show_combat_rolls=True,
                show_movements=True,
                show_growth=True,
            ),
        ),
        ai=AIConfig(
            random=RandomAIConfig(name="RandomBot"),
            aggressive=AggressiveAIConfig(
                name="AggressiveBot",
                weights=AggressiveAIWeightsConfig(
                    attack_enemy=1.0,
                    defend_own=0.8,
                    expand_neutral=0.5,
                    stone_count_bonus=0.2,
                ),
            ),
        ),
    )


def _config_to_dict(config: GameConfig) -> dict[str, Any]:
    """Convert GameConfig back to a raw dictionary."""
    return {
        "game": {
            "board_size": config.game.board_size,
            "num_turns": config.game.num_turns,
            "combat": {
                "hit_chance": config.game.combat.hit_chance,
            },
            "growth": {
                "stones_per_turn": config.game.growth.stones_per_turn,
                "max_stones": config.game.growth.max_stones,
            },
            "expansion_success_rate": config.game.expansion_success_rate,
            "setup": {
                "stones_per_placement": config.game.setup.stones_per_placement,
            },
        },
        "simulation": {
            "default_num_games": config.simulation.default_num_games,
            "parallel_workers": config.simulation.parallel_workers,
            "random_seed": config.simulation.random_seed,
        },
        "display": {
            "symbols": {
                "player1": config.display.symbols.player1,
                "player2": config.display.symbols.player2,
                "neutral": config.display.symbols.neutral,
            },
            "board": {
                "cell_width": config.display.board.cell_width,
                "show_coordinates": config.display.board.show_coordinates,
            },
            "verbosity": {
                "show_combat_rolls": config.display.verbosity.show_combat_rolls,
                "show_movements": config.display.verbosity.show_movements,
                "show_growth": config.display.verbosity.show_growth,
            },
        },
        "ai": {
            "random": {
                "name": config.ai.random.name,
            },
            "aggressive": {
                "name": config.ai.aggressive.name,
                "weights": {
                    "attack_enemy": config.ai.aggressive.weights.attack_enemy,
                    "defend_own": config.ai.aggressive.weights.defend_own,
                    "expand_neutral": config.ai.aggressive.weights.expand_neutral,
                    "stone_count_bonus": config.ai.aggressive.weights.stone_count_bonus,
                },
            },
        },
    }
