"""Simplified state management for the Pygame visualizer.

V6: 3-option movement system (STAY, SEND_HALF, SEND_ALL).
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from random import Random

from ..types import Position, Owner, GameState, MoveType, calculate_half
from ..config import GameConfig


class Mode(Enum):
    """Visualizer operating mode."""
    WATCH = auto()  # AI vs AI observation
    PLAY = auto()   # Human vs AI


class Phase(Enum):
    """Current phase."""
    SETUP = auto()      # Placing initial stone
    PLANNING = auto()   # Choosing moves
    GAME_OVER = auto()  # Game finished


@dataclass
class TerritoryCommand:
    """A planned action for a single territory.

    Each territory has exactly one action:
    - STAY: Don't move, grow +1 stone
    - SEND_HALF: Send half stones (rounded up) to a neighbor
    - SEND_ALL: Send all stones to a neighbor
    """
    move_type: MoveType
    destination: Optional[Position] = None  # None for STAY


@dataclass
class PendingActions:
    """Tracks planned actions for the human player's territories.

    Default behavior: All territories STAY (grow).
    Player can set specific actions for each territory.
    """
    # Map from position to planned action
    actions: dict[Position, TerritoryCommand] = field(default_factory=dict)

    def set_action(
        self,
        source: Position,
        move_type: MoveType,
        destination: Optional[Position] = None,
    ) -> None:
        """Set the action for a territory."""
        self.actions[source] = TerritoryCommand(move_type, destination)

    def get_action(self, source: Position) -> TerritoryCommand:
        """Get the action for a territory. Defaults to STAY."""
        return self.actions.get(source, TerritoryCommand(MoveType.STAY))

    def clear_action(self, source: Position) -> None:
        """Clear action for a territory (revert to STAY)."""
        if source in self.actions:
            del self.actions[source]

    def clear(self) -> None:
        """Clear all actions (all territories revert to STAY)."""
        self.actions.clear()

    def has_action(self, source: Position) -> bool:
        """Check if a territory has a non-default action."""
        return source in self.actions and self.actions[source].move_type != MoveType.STAY


@dataclass
class VisualizerState:
    """Complete visualizer state."""
    mode: Mode
    phase: Phase
    game_state: GameState
    config: GameConfig

    # Human input - now uses TerritoryCommand system
    pending_actions: PendingActions = field(default_factory=PendingActions)
    selected_territory: Optional[Position] = None

    # Hover
    hover_position: Optional[Position] = None

    # RNG
    rng: Random = field(default_factory=Random)

    # System
    should_quit: bool = False


def create_initial_state(
    mode: Mode,
    game_state: GameState,
    config: GameConfig,
    seed: int | None = None,
) -> VisualizerState:
    """Create initial visualizer state."""
    return VisualizerState(
        mode=mode,
        phase=Phase.SETUP if mode == Mode.PLAY else Phase.PLANNING,
        game_state=game_state,
        config=config,
        rng=Random(seed),
    )
