"""Agent protocol for March of Empires."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..types import (
    Player,
    CornerCoord,
    GameState,
    VisibleState,
    TurnActions,
)
from ..config import GameConfig


@runtime_checkable
class Agent(Protocol):
    """Protocol for March of Empires AI agents.

    Agents receive game state (potentially filtered by fog of war)
    and return actions.
    """

    @property
    def name(self) -> str:
        """Human-readable agent name."""
        ...

    def reset(self) -> None:
        """Reset for a new game."""
        ...

    def choose_setup(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> CornerCoord:
        """Choose where to place starting settlement.

        Args:
            state: Current game state.
            player: Which player this agent is.
            config: Game configuration.

        Returns:
            Corner coordinate for settlement placement.
        """
        ...

    def choose_actions(
        self,
        state: GameState,
        player: Player,
        config: GameConfig,
    ) -> TurnActions:
        """Choose actions for all armies this turn.

        Args:
            state: Current game state.
            player: Which player this agent is.
            config: Game configuration.

        Returns:
            TurnActions with actions for this turn.
        """
        ...
