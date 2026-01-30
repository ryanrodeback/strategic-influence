"""Protocol definition for game agents.

V2: Stone-count and combat mechanics.

This module defines the Agent protocol that all player implementations must satisfy.
Using Protocol (structural typing) allows any class with the right methods to work,
without requiring inheritance.
"""

from typing import Protocol, runtime_checkable

from ..types import Owner, GameState, SetupAction, PlayerTurnActions
from ..config import GameConfig


@runtime_checkable
class Agent(Protocol):
    """Protocol that all agents must implement.

    Agents receive the game state and return their actions.
    The protocol uses structural typing - any class with matching methods works.
    """

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Choose where to place initial stone during setup.

        Args:
            state: Current game state (in SETUP phase).
            player: Which player this agent is.
            config: Game configuration.

        Returns:
            SetupAction with position in player's setup zone.
        """
        ...

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Choose actions for all owned territories.

        Args:
            state: Current game state.
            player: Which player this agent is.
            config: Game configuration.

        Returns:
            PlayerTurnActions with one action per owned territory
            (either GROW or MOVE for each).
        """
        ...

    def reset(self) -> None:
        """Reset for a new game.

        Called before setup of each new game.
        Use this to clear any internal state.
        """
        ...

    @property
    def name(self) -> str:
        """Human-readable name for this agent."""
        ...


def validate_agent(agent: object) -> bool:
    """Check if an object satisfies the Agent protocol.

    Args:
        agent: Object to check.

    Returns:
        True if the object is a valid Agent.
    """
    return isinstance(agent, Agent)
