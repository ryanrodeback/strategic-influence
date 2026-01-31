#!/usr/bin/env python3
"""Analyze move generation performance.

Run with: python analyze_move_generation.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from strategic_influence.config import create_default_config
from strategic_influence.engine import create_game, apply_setup
from strategic_influence.types import Owner
from strategic_influence.agents.minimax_agent import MinimaxAgent
from strategic_influence.agents.random_agent import RandomAgent
from strategic_influence.evaluation import TERRITORY_ONLY_WEIGHTS


def main():
    """Analyze move generation."""
    print("Move Generation Analysis")
    print("="*80)

    config = create_default_config()

    # Create a game state
    state = create_game(config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_1, config), config)
    state = apply_setup(state, RandomAgent().choose_setup(state, Owner.PLAYER_2, config), config)

    agent = MinimaxAgent(max_depth=0, weights=TERRITORY_ONLY_WEIGHTS, verbose=True)

    print(f"Board size: {config.board_size}x{config.board_size}")
    print(f"Current turn: {state.current_turn}")
    print(f"Owned territories: P1={len(list(state.board.positions_owned_by(Owner.PLAYER_1)))}, "
          f"P2={len(list(state.board.positions_owned_by(Owner.PLAYER_2)))}")

    print("\nAnalyzing move generation for Player 1...")
    print("This will show what happens during choose_actions()...\n")

    start = time.time()
    try:
        result = agent.choose_actions(state, Owner.PLAYER_1, config)
        elapsed = time.time() - start
        print(f"\nDone! Took {elapsed:.2f}s")
        print(f"Result: {result}")
    except KeyboardInterrupt:
        elapsed = time.time() - start
        print(f"\nInterrupted after {elapsed:.2f}s")
        raise


if __name__ == "__main__":
    main()
