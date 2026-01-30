"""Human player agent for CLI interaction.

V3: Stone-count with split movement support.

This agent prompts the user for input through the terminal.
"""

from ..types import (
    Owner,
    Position,
    GameState,
    SetupAction,
    PlayerTurnActions,
    create_grow_action,
    create_simple_move_action,
)
from ..config import GameConfig


class HumanAgent:
    """Agent that prompts a human player for input.

    Uses simple text input for CLI games.
    For richer interaction, use the visualizer module.
    """

    def __init__(self, name: str = "Human"):
        """Initialize the human agent.

        Args:
            name: Display name for this player.
        """
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def reset(self) -> None:
        """Nothing to reset for human players."""
        pass

    def choose_setup(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> SetupAction:
        """Prompt the human for their setup placement."""
        print(f"\n=== SETUP PHASE: {player} ({self._name}) ===")
        print(f"Current board:")
        print(state.board)

        # Determine valid positions
        if player == Owner.PLAYER_1:
            valid_col = 0
            zone_name = "leftmost column (col 0)"
        else:
            valid_col = config.board_size - 1
            zone_name = f"rightmost column (col {valid_col})"

        print(f"\nPlace your starting stone in the {zone_name}.")
        print("Enter row number (0-4):\n")

        while True:
            try:
                user_input = input("Setup> ").strip()
            except EOFError:
                # Default to center
                row = config.board_size // 2
                break

            try:
                row = int(user_input)
            except ValueError:
                print("Invalid input. Enter a row number.")
                continue

            if row < 0 or row >= config.board_size:
                print(f"Row must be between 0 and {config.board_size - 1}.")
                continue

            pos = Position(row, valid_col)
            if state.board.get_owner(pos) != Owner.NEUTRAL:
                print(f"Position {pos} is already occupied. Choose another row.")
                continue

            break

        pos = Position(row, valid_col)
        print(f"Placing stone at {pos}")
        return SetupAction(player=player, position=pos)

    def choose_actions(
        self,
        state: GameState,
        player: Owner,
        config: GameConfig,
    ) -> PlayerTurnActions:
        """Prompt the human for actions for each territory."""
        print(f"\n=== TURN {state.current_turn + 1}: {player} ({self._name}) ===")
        print(f"Current board:")
        print(state.board)

        owned_positions = list(state.board.positions_owned_by(player))
        owned_positions.sort(key=lambda p: (p.row, p.col))

        print(f"\nYou control {len(owned_positions)} territories.")
        print("For each territory, choose:")
        print("  'g' or 'grow' - Stay and grow (+1 stone)")
        print("  'u/d/l/r' or 'up/down/left/right' - Move all stones in that direction\n")

        actions = []

        for pos in owned_positions:
            territory = state.board.get(pos)
            neighbors = pos.neighbors(config.board_size)

            print(f"\n--- Territory at {pos} ({territory.stones} stones) ---")
            print(f"Neighbors: ", end="")
            for n in sorted(neighbors, key=lambda p: (p.row, p.col)):
                n_terr = state.board.get(n)
                if n_terr.owner == Owner.NEUTRAL:
                    print(f"{n}[empty] ", end="")
                elif n_terr.owner == player:
                    print(f"{n}[yours:{n_terr.stones}] ", end="")
                else:
                    print(f"{n}[enemy:{n_terr.stones}] ", end="")
            print()

            while True:
                try:
                    user_input = input("Action> ").strip().lower()
                except EOFError:
                    user_input = "g"

                if user_input in ("g", "grow"):
                    actions.append(create_grow_action(pos))
                    print(f"  -> GROW at {pos}")
                    break

                # Parse direction
                direction = self._parse_direction(user_input)
                if direction is None:
                    print("Invalid input. Enter 'g', 'u', 'd', 'l', or 'r'.")
                    continue

                dest = self._apply_direction(pos, direction)
                if dest not in neighbors:
                    print(f"Cannot move {direction} from {pos} - not a valid neighbor.")
                    continue

                actions.append(create_simple_move_action(pos, dest, territory.stones))
                print(f"  -> MOVE {territory.stones} stones to {dest}")
                break

        return PlayerTurnActions(player=player, actions=tuple(actions))

    def _parse_direction(self, user_input: str) -> str | None:
        """Parse direction input."""
        directions = {
            "u": "up", "up": "up",
            "d": "down", "down": "down",
            "l": "left", "left": "left",
            "r": "right", "right": "right",
        }
        return directions.get(user_input)

    def _apply_direction(self, pos: Position, direction: str) -> Position:
        """Apply a direction to get new position."""
        deltas = {
            "up": (1, 0),   # Up means higher row number
            "down": (-1, 0),
            "left": (0, -1),
            "right": (0, 1),
        }
        dr, dc = deltas[direction]
        return Position(pos.row + dr, pos.col + dc)
