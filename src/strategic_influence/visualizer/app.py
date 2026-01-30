"""Simplified Pygame visualizer.

V6: 3-option movement system (STAY, SEND_HALF, SEND_ALL).
- Click territory to select
- Click neighbor = SEND_HALF (keeps source)
- Shift+Click neighbor = SEND_ALL (abandons source)
- Click selected territory = clear action (STAY)

V7: Added "pondering" - AI thinks while human plans.
- AI starts thinking immediately after each turn
- When human commits, AI result is often ready instantly
- Dramatically reduces perceived wait time for slow AIs (Minimax)
"""

from typing import Optional
from concurrent.futures import ThreadPoolExecutor, Future
import time

import pygame

from ..config import create_default_config, GameConfig
from ..types import (
    Owner, Position, TurnActions, SetupAction, GamePhase,
    PlayerTurnActions, TerritoryAction, StoneMovement,
    MoveType, calculate_half,
    create_grow_action, create_simple_move_action,
)
from ..engine import create_game, apply_turn, apply_setup
from ..agents import (
    RandomAgent, AggressiveAgent, DefensiveAgent,
    RushAgent, StrategicAgent, MonteCarloAgent,
    MinimaxAgent, IntuitionAgent, GreedyStrategicAgent,
)
from ..agents.protocol import Agent
from ..evaluation import BALANCED_WEIGHTS

# Map of opponent names to agent classes
OPPONENT_AGENTS = {
    "random": lambda seed: RandomAgent(seed=seed),
    "aggressive": lambda seed: AggressiveAgent(seed=seed),
    "defensive": lambda seed: DefensiveAgent(seed=seed),
    "rush": lambda seed: RushAgent(seed=seed),
    "strategic": lambda seed: StrategicAgent(seed=seed),
    "montecarlo": lambda seed: MonteCarloAgent(seed=seed, num_simulations=50),
    "intuition": lambda seed: IntuitionAgent(seed=seed),
    "greedy": lambda seed: GreedyStrategicAgent(seed=seed),
    "minimax": lambda seed: MinimaxAgent(seed=seed, max_depth=2, weights=BALANCED_WEIGHTS, max_moves=50),
    "minimax3": lambda seed: MinimaxAgent(seed=seed, max_depth=3, weights=BALANCED_WEIGHTS, max_moves=50),
}

from .constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    COLOR_BG, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_PLAYER_1, COLOR_PLAYER_2,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_STONE,
)
from .state import Mode, Phase, VisualizerState, create_initial_state, TerritoryCommand
from .board_renderer import render_board, screen_to_board


class Visualizer:
    """Simplified visualizer application."""

    def __init__(
        self,
        mode: Mode,
        config: Optional[GameConfig] = None,
        opponent_type: str = "aggressive",
        seed: Optional[int] = None,
    ):
        pygame.init()
        pygame.display.set_caption("Strategic Influence")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.fonts = {
            "large": pygame.font.Font(None, FONT_LARGE),
            "medium": pygame.font.Font(None, FONT_MEDIUM),
            "small": pygame.font.Font(None, FONT_SMALL),
            "stone": pygame.font.Font(None, FONT_STONE),
        }

        self.config = config or create_default_config()

        # Create AI opponent
        opponent_key = opponent_type.lower()
        if opponent_key in OPPONENT_AGENTS:
            self.opponent = OPPONENT_AGENTS[opponent_key](seed)
        else:
            self.opponent = AggressiveAgent(seed=seed)

        # For watch mode, also need P1 agent
        if mode == Mode.WATCH:
            self.player1_agent = RandomAgent(seed=seed)
        else:
            self.player1_agent = None

        # Initialize game
        game_state = create_game(self.config)
        self.state = create_initial_state(mode, game_state, self.config, seed)

        # Pondering: AI thinks while human plans
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._ai_future: Optional[Future] = None
        self._ponder_start_time: Optional[float] = None

        # Auto-setup for watch mode
        if mode == Mode.WATCH:
            self._auto_setup()

    def _auto_setup(self) -> None:
        """Auto-setup for watch mode."""
        setup1 = self.player1_agent.choose_setup(
            self.state.game_state, Owner.PLAYER_1, self.config
        )
        self.state.game_state = apply_setup(self.state.game_state, setup1, self.config)

        setup2 = self.opponent.choose_setup(
            self.state.game_state, Owner.PLAYER_2, self.config
        )
        self.state.game_state = apply_setup(self.state.game_state, setup2, self.config)

        self.state.phase = Phase.PLANNING
        self._start_pondering()

    def _start_pondering(self) -> None:
        """Start AI thinking in background while human plans.

        This is the key optimization: instead of waiting for the human
        to commit before the AI starts thinking, we start immediately.
        Since moves are simultaneous, the AI can compute its best move
        based on the current board state.
        """
        if self.state.game_state.is_complete:
            return

        self._ponder_start_time = time.time()
        self._ai_future = self._executor.submit(
            self.opponent.choose_actions,
            self.state.game_state,
            Owner.PLAYER_2,
            self.config,
        )

    def _get_ai_ponder_status(self) -> str:
        """Get status of AI pondering for display."""
        if self._ai_future is None:
            return ""

        if self._ai_future.done():
            return "AI ready"
        else:
            elapsed = time.time() - self._ponder_start_time if self._ponder_start_time else 0
            return f"AI thinking... ({elapsed:.0f}s)"

    def run(self) -> None:
        """Main game loop."""
        running = True

        try:
            while running:
                self.clock.tick(FPS)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            # Check for shift modifier
                            mods = pygame.key.get_mods()
                            shift_held = mods & pygame.KMOD_SHIFT
                            self._handle_click(event.pos, shift_held)
                        elif event.button == 3:
                            self._handle_right_click(event.pos)
                    elif event.type == pygame.KEYDOWN:
                        self._handle_key(event.key)
                    elif event.type == pygame.MOUSEMOTION:
                        self.state.hover_position = screen_to_board(event.pos)

                self._render()
                pygame.display.flip()

                if self.state.should_quit:
                    running = False
        finally:
            # Clean up pondering thread
            if self._ai_future:
                self._ai_future.cancel()
            self._executor.shutdown(wait=False)
            pygame.quit()

    def _handle_click(self, pos: tuple[int, int], shift_held: bool) -> None:
        """Handle left click.

        - Click own territory: select it
        - Click neighbor of selected: SEND_HALF (or SEND_ALL if shift)
        - Click selected territory again: clear action (STAY)
        """
        board_pos = screen_to_board(pos)
        if not board_pos:
            return

        if self.state.phase == Phase.SETUP:
            self._handle_setup_click(board_pos)
        elif self.state.phase == Phase.PLANNING:
            self._handle_planning_click(board_pos, shift_held)

    def _handle_setup_click(self, pos: Position) -> None:
        """Handle click during setup."""
        if not pos.is_in_setup_zone(self.config.board_size, Owner.PLAYER_1):
            return
        if self.state.game_state.board.get_owner(pos) != Owner.NEUTRAL:
            return

        # Place player stone
        setup = SetupAction(player=Owner.PLAYER_1, position=pos)
        self.state.game_state = apply_setup(self.state.game_state, setup, self.config)

        # AI places their stone
        setup2 = self.opponent.choose_setup(
            self.state.game_state, Owner.PLAYER_2, self.config
        )
        self.state.game_state = apply_setup(self.state.game_state, setup2, self.config)

        self.state.phase = Phase.PLANNING

        # Start AI pondering immediately
        self._start_pondering()

    def _handle_planning_click(self, pos: Position, shift_held: bool) -> None:
        """Handle click during planning phase.

        Click own territory: select it (or deselect if already selected)
        Click neighbor of selected: SEND_HALF (or SEND_ALL with shift)
        """
        board = self.state.game_state.board
        territory = board.get(pos)

        # If we have a selection and click adjacent, set action
        if self.state.selected_territory and pos != self.state.selected_territory:
            source = self.state.selected_territory
            if pos in source.neighbors(self.config.board_size):
                # Set SEND_HALF or SEND_ALL based on shift
                if shift_held:
                    self.state.pending_actions.set_action(
                        source, MoveType.SEND_ALL, pos
                    )
                else:
                    self.state.pending_actions.set_action(
                        source, MoveType.SEND_HALF, pos
                    )
                # Keep selection for potential changes
                return

        # Clicking own territory
        if territory.owner == Owner.PLAYER_1:
            if self.state.selected_territory == pos:
                # Clicking same territory - just deselect (don't clear action)
                self.state.selected_territory = None
            else:
                # Select new territory
                self.state.selected_territory = pos

    def _handle_right_click(self, pos: tuple[int, int]) -> None:
        """Handle right click - clear action for clicked territory."""
        if self.state.phase != Phase.PLANNING:
            return

        board_pos = screen_to_board(pos)
        if board_pos:
            # Clear action for the clicked territory (if it's ours)
            if self.state.game_state.board.get_owner(board_pos) == Owner.PLAYER_1:
                self.state.pending_actions.clear_action(board_pos)

    def _handle_key(self, key: int) -> None:
        """Handle keyboard input."""
        if key == pygame.K_ESCAPE:
            if self.state.phase == Phase.PLANNING:
                # Clear all actions and selection
                self.state.pending_actions.clear()
                self.state.selected_territory = None
            elif self.state.phase == Phase.GAME_OVER:
                self.state.should_quit = True

        elif key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.state.phase == Phase.PLANNING:
                self._execute_turn()

    def _execute_turn(self) -> None:
        """Execute the turn with current actions.

        Uses pondering result if available, otherwise waits for AI.
        """
        board = self.state.game_state.board
        owned = board.positions_owned_by(Owner.PLAYER_1)

        # Build actions for each territory
        actions = []
        for pos in owned:
            command = self.state.pending_actions.get_action(pos)
            stones = board.get_stones(pos)

            if command.move_type == MoveType.STAY:
                actions.append(create_grow_action(pos))
            elif command.move_type == MoveType.SEND_HALF:
                half = calculate_half(stones)
                actions.append(create_simple_move_action(pos, command.destination, half))
            else:  # SEND_ALL
                actions.append(create_simple_move_action(pos, command.destination, stones))

        p1_actions = PlayerTurnActions(player=Owner.PLAYER_1, actions=tuple(actions))

        # Get AI actions - use pondering result if available
        if self.state.mode == Mode.WATCH:
            p1_actions = self.player1_agent.choose_actions(
                self.state.game_state, Owner.PLAYER_1, self.config
            )

        if self._ai_future:
            # Use pondering result (blocks if not ready yet)
            p2_actions = self._ai_future.result()
            self._ai_future = None
        else:
            # Fallback: compute now (shouldn't happen normally)
            p2_actions = self.opponent.choose_actions(
                self.state.game_state, Owner.PLAYER_2, self.config
            )

        turn_actions = TurnActions(
            player1_actions=p1_actions,
            player2_actions=p2_actions,
            turn_number=self.state.game_state.current_turn + 1,
        )

        # Apply turn
        self.state.game_state = apply_turn(
            self.state.game_state, turn_actions, self.config, self.state.rng
        )

        # Clear pending actions
        self.state.pending_actions.clear()
        self.state.selected_territory = None

        # Check for game over
        if self.state.game_state.is_complete:
            self.state.phase = Phase.GAME_OVER
        else:
            # Start pondering for next turn immediately
            self._start_pondering()

    def _render(self) -> None:
        """Render the current frame."""
        self.screen.fill(COLOR_BG)

        # Title
        title = self.fonts["large"].render("STRATEGIC INFLUENCE", True, COLOR_TEXT)
        title_rect = title.get_rect(centerx=WINDOW_WIDTH // 2, top=20)
        self.screen.blit(title, title_rect)

        # Phase/status
        status = self._get_status_text()
        status_text = self.fonts["medium"].render(status, True, COLOR_TEXT_DIM)
        status_rect = status_text.get_rect(centerx=WINDOW_WIDTH // 2, top=55)
        self.screen.blit(status_text, status_rect)

        # Board
        render_board(self.screen, self.state, self.fonts)

        # Info panel
        self._render_info()

    def _get_status_text(self) -> str:
        """Get status text for current phase."""
        if self.state.phase == Phase.SETUP:
            return "Setup: Click in left column to place your stone"
        elif self.state.phase == Phase.PLANNING:
            turn = self.state.game_state.current_turn
            total = self.config.num_turns
            ai_status = self._get_ai_ponder_status()
            base = f"Turn {turn}/{total}: Click to select, click neighbor to act. Space to confirm."
            if ai_status:
                return f"{base}  [{ai_status}]"
            return base
        elif self.state.phase == Phase.GAME_OVER:
            winner = self.state.game_state.winner
            if winner == Owner.PLAYER_1:
                return "You win!"
            elif winner == Owner.PLAYER_2:
                return "Opponent wins!"
            else:
                return "Draw!"
        return ""

    def _render_info(self) -> None:
        """Render info panel."""
        y = 520
        x = 80

        # Score
        counts = self.state.game_state.board.count_territories()
        p1_count = counts[Owner.PLAYER_1]
        p2_count = counts[Owner.PLAYER_2]

        score_text = self.fonts["medium"].render(
            f"Score:  You {p1_count}  -  {p2_count} Opponent", True, COLOR_TEXT
        )
        self.screen.blit(score_text, (x, y))

        # Stone counts
        p1_stones = self.state.game_state.board.total_stones(Owner.PLAYER_1)
        p2_stones = self.state.game_state.board.total_stones(Owner.PLAYER_2)

        y += 30
        stones_text = self.fonts["small"].render(
            f"Stones: You {p1_stones} - {p2_stones} Opponent", True, COLOR_TEXT_DIM
        )
        self.screen.blit(stones_text, (x, y))

        # Controls
        y += 40
        controls = [
            "Click your stone to select it",
            "Click neighbor = SEND HALF (keep territory)",
            "Shift+Click = SEND ALL (abandon territory)",
            "Click selected = clear action (STAY/grow)",
            "[Space/Enter] Execute turn    [Esc] Reset",
        ]
        for line in controls:
            text = self.fonts["small"].render(line, True, COLOR_TEXT_DIM)
            self.screen.blit(text, (x, y))
            y += 22

        # Selected territory info
        if self.state.selected_territory:
            pos = self.state.selected_territory
            stones = self.state.game_state.board.get_stones(pos)
            command = self.state.pending_actions.get_action(pos)

            y += 10
            if command.move_type == MoveType.STAY:
                action_str = "STAY (grow +1)"
            elif command.move_type == MoveType.SEND_HALF:
                half = calculate_half(stones)
                action_str = f"SEND HALF ({half}) -> {command.destination}"
            else:
                action_str = f"SEND ALL ({stones}) -> {command.destination}"

            info = f"Selected: {stones} stones, Action: {action_str}"
            text = self.fonts["medium"].render(info, True, COLOR_PLAYER_1)
            self.screen.blit(text, (x, y))


def main(
    mode: str = "play",
    opponent: str = "aggressive",
    seed: Optional[int] = None,
) -> None:
    """Main entry point."""
    game_mode = Mode.PLAY if mode.lower() == "play" else Mode.WATCH
    viz = Visualizer(mode=game_mode, opponent_type=opponent, seed=seed)
    viz.run()


def cli_main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Strategic Influence")
    parser.add_argument(
        "--mode", "-m", choices=["play", "watch"], default="play",
        help="'play' for human vs AI, 'watch' for AI vs AI"
    )
    parser.add_argument(
        "--opponent", "-o",
        choices=["random", "aggressive", "defensive", "rush", "strategic", "montecarlo", "intuition", "greedy", "minimax", "minimax3"],
        default="aggressive",
        help="Opponent AI type (greedy=fast strategic, minimax=depth2 ~20s/move)"
    )
    parser.add_argument("--seed", "-s", type=int, default=None, help="Random seed")

    args = parser.parse_args()
    main(mode=args.mode, opponent=args.opponent, seed=args.seed)


if __name__ == "__main__":
    cli_main()
