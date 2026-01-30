"""Tests for agent implementations.

V3: Stone-count with split movement support.
"""

import pytest

from strategic_influence.config import create_default_config
from strategic_influence.types import Owner, Position, GamePhase
from strategic_influence.engine import create_game, apply_setup
from strategic_influence.agents import RandomAgent, AggressiveAgent
from strategic_influence.agents.protocol import Agent, validate_agent


class TestAgentProtocol:
    """Tests for agent protocol."""

    def test_random_agent_satisfies_protocol(self):
        """RandomAgent satisfies Agent protocol."""
        agent = RandomAgent()
        assert validate_agent(agent)

    def test_aggressive_agent_satisfies_protocol(self):
        """AggressiveAgent satisfies Agent protocol."""
        agent = AggressiveAgent()
        assert validate_agent(agent)

    def test_agents_have_names(self):
        """Agents have name property."""
        assert RandomAgent().name == "RandomBot"
        assert AggressiveAgent().name == "AggressiveBot"


class TestRandomAgent:
    """Tests for RandomAgent."""

    def test_choose_setup_in_valid_zone(self, default_config):
        """Setup choice is in player's valid zone."""
        agent = RandomAgent(seed=42)
        state = create_game(default_config)

        # P1 setup
        setup = agent.choose_setup(state, Owner.PLAYER_1, default_config)
        assert setup.position.is_in_setup_zone(default_config.board_size, Owner.PLAYER_1)
        assert setup.player == Owner.PLAYER_1

    def test_choose_setup_p2(self, default_config):
        """P2 setup is in valid zone."""
        agent = RandomAgent(seed=42)
        state = create_game(default_config)

        setup = agent.choose_setup(state, Owner.PLAYER_2, default_config)
        assert setup.position.is_in_setup_zone(default_config.board_size, Owner.PLAYER_2)
        assert setup.player == Owner.PLAYER_2

    def test_choose_actions_for_all_territories(self, default_config):
        """Agent provides action for each owned territory."""
        agent = RandomAgent(seed=42)
        state = create_game(default_config)

        # Setup
        setup1 = agent.choose_setup(state, Owner.PLAYER_1, default_config)
        state = apply_setup(state, setup1, default_config)
        setup2 = agent.choose_setup(state, Owner.PLAYER_2, default_config)
        state = apply_setup(state, setup2, default_config)

        # Get actions
        actions = agent.choose_actions(state, Owner.PLAYER_1, default_config)

        owned = state.board.positions_owned_by(Owner.PLAYER_1)
        action_positions = frozenset(a.position for a in actions.actions)
        assert action_positions == owned

    def test_reproducible_with_seed(self, default_config):
        """Same seed produces same choices."""
        agent1 = RandomAgent(seed=42)
        agent2 = RandomAgent(seed=42)
        state = create_game(default_config)

        setup1 = agent1.choose_setup(state, Owner.PLAYER_1, default_config)
        setup2 = agent2.choose_setup(state, Owner.PLAYER_1, default_config)

        assert setup1.position == setup2.position

    def test_reset_restores_initial_state(self, default_config):
        """Reset restores agent to initial state."""
        agent = RandomAgent(seed=42)
        state = create_game(default_config)

        setup1 = agent.choose_setup(state, Owner.PLAYER_1, default_config)
        agent.reset()
        setup2 = agent.choose_setup(state, Owner.PLAYER_1, default_config)

        assert setup1.position == setup2.position


class TestAggressiveAgent:
    """Tests for AggressiveAgent."""

    def test_prefers_center_setup(self, default_config):
        """Aggressive agent prefers positions closer to center."""
        agent = AggressiveAgent(seed=42)
        state = create_game(default_config)

        setup = agent.choose_setup(state, Owner.PLAYER_1, default_config)
        # Should be in valid setup zone and close to center
        assert setup.position.is_in_setup_zone(default_config.board_size, Owner.PLAYER_1)
        # Should prefer closer to center (not corner)
        mid = default_config.board_size // 2
        dist = abs(setup.position.row - mid) + abs(setup.position.col - mid)
        assert dist <= 2  # Should be reasonably close to center

    def test_choose_actions_valid(self, default_config):
        """Agent provides valid actions."""
        agent = AggressiveAgent(seed=42)
        state = create_game(default_config)

        # Setup
        setup1 = agent.choose_setup(state, Owner.PLAYER_1, default_config)
        state = apply_setup(state, setup1, default_config)
        setup2 = agent.choose_setup(state, Owner.PLAYER_2, default_config)
        state = apply_setup(state, setup2, default_config)

        # Get actions
        actions = agent.choose_actions(state, Owner.PLAYER_1, default_config)

        # All owned positions should have actions
        owned = state.board.positions_owned_by(Owner.PLAYER_1)
        action_positions = frozenset(a.position for a in actions.actions)
        assert action_positions == owned

    def test_reset_allows_reproducibility(self, default_config):
        """Reset allows agent to be used for another game with same results."""
        agent = AggressiveAgent(seed=42)
        state = create_game(default_config)

        # First game setup
        setup1 = agent.choose_setup(state, Owner.PLAYER_1, default_config)

        # Reset and try again
        agent.reset()
        setup2 = agent.choose_setup(state, Owner.PLAYER_1, default_config)

        assert setup1.position == setup2.position
