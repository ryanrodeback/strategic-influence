"""Core data types for Strategic Influence.

V3: Stone-count with split movement support and Go-style aesthetics.

All types are immutable (frozen dataclasses) to ensure:
- Pure functions can't accidentally mutate state
- Safe parallel simulation (no race conditions)
- Deterministic replay capability
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Mapping


class Owner(Enum):
    """Territory ownership state."""
    NEUTRAL = 0
    PLAYER_1 = 1  # White stones
    PLAYER_2 = 2  # Black stones

    def __str__(self) -> str:
        if self == Owner.NEUTRAL:
            return "Neutral"
        elif self == Owner.PLAYER_1:
            return "White"
        else:
            return "Black"

    def opponent(self) -> "Owner":
        """Return the opponent player, or NEUTRAL if called on NEUTRAL."""
        if self == Owner.PLAYER_1:
            return Owner.PLAYER_2
        elif self == Owner.PLAYER_2:
            return Owner.PLAYER_1
        return Owner.NEUTRAL


@dataclass(frozen=True)
class Position:
    """A position on the board (immutable).

    On a Go board, positions are at line intersections.
    Coordinates are 0-indexed, with (0, 0) at bottom-left.
    """
    row: int
    col: int

    def __str__(self) -> str:
        return f"({self.row}, {self.col})"

    def neighbors(self, board_size: int) -> frozenset["Position"]:
        """Return orthogonal neighbors (following the lines)."""
        adjacent = [
            Position(self.row - 1, self.col),  # Down
            Position(self.row + 1, self.col),  # Up
            Position(self.row, self.col - 1),  # Left
            Position(self.row, self.col + 1),  # Right
        ]
        return frozenset(
            p for p in adjacent
            if 0 <= p.row < board_size and 0 <= p.col < board_size
        )

    def is_valid(self, board_size: int) -> bool:
        """Check if this position is within board bounds."""
        return 0 <= self.row < board_size and 0 <= self.col < board_size

    def is_in_setup_zone(self, board_size: int, player: Owner) -> bool:
        """Check if this position is in a player's setup zone.

        Player 1 (White): columns 0-1 + bottom 2 rows of middle column
        Player 2 (Black): columns 3-4 + top 2 rows of middle column
        Center spot (row 2, col 2 on 5x5) is excluded.

        For 5x5 board:
        - P1: cols A,B (0,1) or (col C and rows 1,2)
        - P2: cols D,E (3,4) or (col C and rows 4,5)
        """
        mid_col = board_size // 2  # 2 for 5x5
        mid_row = board_size // 2  # 2 for 5x5

        if player == Owner.PLAYER_1:
            # Left two columns
            if self.col < mid_col:
                return True
            # Bottom part of middle column (rows 0, 1 for 5x5) - not center
            if self.col == mid_col and self.row < mid_row:
                return True
            return False
        elif player == Owner.PLAYER_2:
            # Right two columns
            if self.col > mid_col:
                return True
            # Top part of middle column (rows 3, 4 for 5x5) - not center
            if self.col == mid_col and self.row > mid_row:
                return True
            return False
        return False


@dataclass(frozen=True)
class Territory:
    """A territory with stone count.

    A territory can be:
    - NEUTRAL with 0 stones (empty intersection)
    - Owned by a player with 1+ stones (pile of stones)
    """
    owner: Owner
    stones: int

    def __post_init__(self) -> None:
        if self.stones < 0:
            raise ValueError("Stone count cannot be negative")
        if self.owner != Owner.NEUTRAL and self.stones < 1:
            raise ValueError("Owned territory must have at least 1 stone")
        if self.owner == Owner.NEUTRAL and self.stones != 0:
            raise ValueError("Neutral territory cannot have stones")

    def __str__(self) -> str:
        if self.owner == Owner.NEUTRAL:
            return "."
        symbol = "W" if self.owner == Owner.PLAYER_1 else "B"
        return f"{symbol}{self.stones}"


def create_neutral_territory() -> Territory:
    """Create an empty intersection."""
    return Territory(owner=Owner.NEUTRAL, stones=0)


def create_territory(owner: Owner, stones: int) -> Territory:
    """Create a territory with the specified owner and stone count."""
    return Territory(owner=owner, stones=stones)


@dataclass(frozen=True)
class TerritoryBoard:
    """Immutable board state with stone counts.

    The board represents intersections on a Go-style grid.
    """
    size: int
    _cells: tuple[tuple[Territory, ...], ...]

    def get(self, pos: Position) -> Territory:
        """Get the territory at a position."""
        if not pos.is_valid(self.size):
            raise ValueError(f"Position {pos} is outside board of size {self.size}")
        return self._cells[pos.row][pos.col]

    def get_owner(self, pos: Position) -> Owner:
        """Get the owner of a cell."""
        return self.get(pos).owner

    def get_stones(self, pos: Position) -> int:
        """Get the stone count at a position."""
        return self.get(pos).stones

    def with_territory(self, pos: Position, territory: Territory) -> "TerritoryBoard":
        """Return a new board with one cell changed."""
        if not pos.is_valid(self.size):
            raise ValueError(f"Position {pos} is outside board of size {self.size}")

        new_cells = [list(row) for row in self._cells]
        new_cells[pos.row][pos.col] = territory
        return TerritoryBoard(
            size=self.size,
            _cells=tuple(tuple(row) for row in new_cells)
        )

    def with_stones(self, pos: Position, owner: Owner, stones: int) -> "TerritoryBoard":
        """Return a new board with updated stones at a position."""
        if stones == 0:
            territory = create_neutral_territory()
        else:
            territory = create_territory(owner, stones)
        return self.with_territory(pos, territory)

    def all_positions(self) -> frozenset[Position]:
        """Return all positions on the board."""
        return frozenset(
            Position(r, c)
            for r in range(self.size)
            for c in range(self.size)
        )

    def positions_owned_by(self, owner: Owner) -> frozenset[Position]:
        """Return all positions owned by the given player."""
        return frozenset(
            Position(r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self._cells[r][c].owner == owner
        )

    def count_territories(self) -> dict[Owner, int]:
        """Count territories for each owner."""
        counts = {Owner.NEUTRAL: 0, Owner.PLAYER_1: 0, Owner.PLAYER_2: 0}
        for row in self._cells:
            for territory in row:
                counts[territory.owner] += 1
        return counts

    def total_stones(self, owner: Owner) -> int:
        """Count total stones for a player."""
        total = 0
        for row in self._cells:
            for territory in row:
                if territory.owner == owner:
                    total += territory.stones
        return total

    def __str__(self) -> str:
        """String representation of the board."""
        lines = []
        # Print from top row to bottom (row 4 to 0)
        for row in range(self.size - 1, -1, -1):
            cells = []
            for col in range(self.size):
                territory = self._cells[row][col]
                if territory.owner == Owner.NEUTRAL:
                    cells.append("  + ")
                else:
                    symbol = "W" if territory.owner == Owner.PLAYER_1 else "B"
                    cells.append(f"{symbol}{territory.stones:2d}")
            lines.append(f"{row+1} " + " ".join(cells))
        # Column labels
        labels = "   " + "  ".join(f" {chr(65+c)} " for c in range(self.size))
        lines.append(labels)
        return "\n".join(lines)


def create_empty_board(size: int) -> TerritoryBoard:
    """Create a new board with all intersections empty."""
    neutral = create_neutral_territory()
    cells = tuple(
        tuple(neutral for _ in range(size))
        for _ in range(size)
    )
    return TerritoryBoard(size=size, _cells=cells)


@dataclass(frozen=True)
class StoneMovement:
    """A movement of stones from one intersection to an adjacent one."""
    source: Position
    destination: Position
    count: int

    def __post_init__(self) -> None:
        if self.count < 1:
            raise ValueError("Movement must move at least 1 stone")

    def __str__(self) -> str:
        return f"{self.source} -> {self.destination} ({self.count})"


@dataclass(frozen=True)
class TerritoryAction:
    """Action for a single territory in a turn.

    A territory can either:
    - Stay (grow): movements is empty, gains +1 stone at end of turn
    - Move: one or more movements directing stones to adjacent intersections

    Stones can be split - sent in different directions from the same pile.
    """
    position: Position
    movements: tuple[StoneMovement, ...] = ()

    @property
    def is_grow(self) -> bool:
        """True if this territory is staying to grow."""
        return len(self.movements) == 0

    @property
    def is_move(self) -> bool:
        """True if this territory is sending stones."""
        return len(self.movements) > 0

    @property
    def total_stones_moving(self) -> int:
        """Total stones being moved."""
        return sum(m.count for m in self.movements)

    def __str__(self) -> str:
        if self.is_grow:
            return f"{self.position}: GROW"
        moves = ", ".join(str(m) for m in self.movements)
        return f"{self.position}: MOVE [{moves}]"


@dataclass(frozen=True)
class PlayerTurnActions:
    """All actions for one player in a turn."""
    player: Owner
    actions: tuple[TerritoryAction, ...]

    def get_action_for(self, pos: Position) -> TerritoryAction | None:
        """Get the action for a specific territory."""
        for action in self.actions:
            if action.position == pos:
                return action
        return None

    def get_all_movements(self) -> tuple[StoneMovement, ...]:
        """Get all movements from this turn."""
        movements = []
        for action in self.actions:
            movements.extend(action.movements)
        return tuple(movements)

    def __str__(self) -> str:
        actions_str = ", ".join(str(a) for a in self.actions)
        return f"{self.player}: [{actions_str}]"


@dataclass(frozen=True)
class TurnActions:
    """Both players' actions for a single turn."""
    player1_actions: PlayerTurnActions
    player2_actions: PlayerTurnActions
    turn_number: int

    def get_actions(self, player: Owner) -> PlayerTurnActions:
        """Get actions for a specific player."""
        if player == Owner.PLAYER_1:
            return self.player1_actions
        elif player == Owner.PLAYER_2:
            return self.player2_actions
        raise ValueError(f"Invalid player: {player}")


class CombatOutcome(Enum):
    """Outcome of combat resolution."""
    ATTACKER_WINS = auto()      # Attacker eliminates defender
    DEFENDER_HOLDS = auto()     # Defender survives, attacker retreats
    MUTUAL_DESTRUCTION = auto() # Both eliminated, intersection empty


@dataclass(frozen=True)
class CombatRoll:
    """A single roll in combat."""
    roller: Owner
    target: Owner
    roll_value: float  # The actual roll (0.0 to 1.0)
    hit: bool
    roller_stones_after: int
    target_stones_after: int

    def __str__(self) -> str:
        result = "HIT" if self.hit else "miss"
        return f"{self.roller} rolls {self.roll_value:.2f}: {result}"


@dataclass(frozen=True)
class CombatResult:
    """Complete result of combat at a position."""
    position: Position
    attacker: Owner
    defender: Owner
    attacker_initial: int
    defender_initial: int
    attacker_surviving: int
    defender_surviving: int
    rolls: tuple[CombatRoll, ...]
    outcome: CombatOutcome

    @property
    def winner(self) -> Owner:
        """Get the winner of combat (NEUTRAL if mutual destruction)."""
        if self.outcome == CombatOutcome.ATTACKER_WINS:
            return self.attacker
        elif self.outcome == CombatOutcome.DEFENDER_HOLDS:
            return self.defender
        return Owner.NEUTRAL

    def __str__(self) -> str:
        return (
            f"Combat at {self.position}: "
            f"{self.attacker}({self.attacker_initial}) vs {self.defender}({self.defender_initial}) "
            f"-> {self.outcome.name} ({self.attacker_surviving} vs {self.defender_surviving})"
        )


@dataclass(frozen=True)
class ExpansionRoll:
    """A single roll in an expansion attempt."""
    roll_value: float  # The actual roll (0.0 to 1.0)
    success: bool  # Whether this stone succeeded


@dataclass(frozen=True)
class ExpansionResult:
    """Result of attempting to expand into neutral territory.

    Each stone has a 50% chance to succeed.
    If ANY stone succeeds, all stones claim the territory.
    If ALL stones fail, all stones are lost.
    """
    position: Position
    expander: Owner
    stones_sent: int
    rolls: tuple[ExpansionRoll, ...]
    succeeded: bool  # True if at least one roll succeeded
    stones_surviving: int  # All if succeeded, 0 if failed

    def __str__(self) -> str:
        successes = sum(1 for r in self.rolls if r.success)
        if self.succeeded:
            return f"Expansion to {self.position}: SUCCESS ({successes}/{self.stones_sent} rolls succeeded)"
        else:
            return f"Expansion to {self.position}: FAILED (all {self.stones_sent} rolls failed, stones lost)"


@dataclass(frozen=True)
class MovementResult:
    """Result of a stone movement (may involve combat or expansion risk)."""
    movement: StoneMovement
    owner: Owner  # Who moved these stones
    combat: CombatResult | None  # Set if attacking enemy territory
    expansion: ExpansionResult | None  # Set if expanding to neutral
    retreat_count: int  # Stones retreating back to source (0 if none)

    @property
    def successful(self) -> bool:
        """Whether the movement was successful (claimed territory)."""
        if self.combat is not None:
            return self.combat.outcome == CombatOutcome.ATTACKER_WINS
        if self.expansion is not None:
            return self.expansion.succeeded
        return True  # Reinforcement always succeeds


@dataclass(frozen=True)
class TurnResult:
    """Complete result of a turn."""
    turn_number: int
    actions: TurnActions
    board_before: TerritoryBoard
    board_after: TerritoryBoard
    movements: tuple[MovementResult, ...]
    territories_grown: tuple[Position, ...]

    @property
    def combats(self) -> tuple[CombatResult, ...]:
        """Get all combats from this turn."""
        return tuple(
            m.combat for m in self.movements if m.combat is not None
        )


class GamePhase(Enum):
    """Current phase of the game."""
    SETUP = auto()      # Players placing initial stones
    PLAYING = auto()    # Normal turn-based play
    COMPLETE = auto()   # Game over


@dataclass(frozen=True)
class SetupAction:
    """A single setup placement."""
    player: Owner
    position: Position

    def __post_init__(self) -> None:
        if self.player == Owner.NEUTRAL:
            raise ValueError("Neutral cannot place setup stones")


@dataclass(frozen=True)
class GameState:
    """Complete game state at any point."""
    board: TerritoryBoard
    phase: GamePhase
    current_turn: int
    turn_history: tuple[TurnResult, ...]
    setup_complete: tuple[Owner, ...]
    winner: Owner | None

    @property
    def is_complete(self) -> bool:
        """Whether the game is complete."""
        return self.phase == GamePhase.COMPLETE

    @property
    def total_turns(self) -> int:
        """Number of turns that have been played."""
        return len(self.turn_history)


def create_initial_state(board_size: int) -> GameState:
    """Create the initial game state with an empty board in setup phase."""
    return GameState(
        board=create_empty_board(board_size),
        phase=GamePhase.SETUP,
        current_turn=0,
        turn_history=(),
        setup_complete=(),
        winner=None,
    )


# Helper functions for creating actions
def create_grow_action(position: Position) -> TerritoryAction:
    """Create a GROW action (stay and gain +1 stone)."""
    return TerritoryAction(position=position, movements=())


def create_move_action(
    position: Position,
    movements: list[tuple[Position, int]],
) -> TerritoryAction:
    """Create a MOVE action with potentially split movements.

    Args:
        position: Source position
        movements: List of (destination, count) tuples
    """
    stone_movements = tuple(
        StoneMovement(source=position, destination=dest, count=count)
        for dest, count in movements
    )
    return TerritoryAction(position=position, movements=stone_movements)


def create_simple_move_action(
    source: Position,
    destination: Position,
    count: int,
) -> TerritoryAction:
    """Create a simple MOVE action (all stones one direction)."""
    return TerritoryAction(
        position=source,
        movements=(StoneMovement(source=source, destination=destination, count=count),)
    )


class MoveType(Enum):
    """The three allowed move types for simplified mechanics."""
    STAY = auto()       # Stay and grow (+1 stone)
    SEND_HALF = auto()  # Send half (rounded up) in one direction
    SEND_ALL = auto()   # Send all stones in one direction


def calculate_half(stones: int) -> int:
    """Calculate half of stones, rounded up.

    Examples:
        1 stone -> send 1 (nothing stays)
        2 stones -> send 1
        3 stones -> send 2
        4 stones -> send 2
        5 stones -> send 3
    """
    return (stones + 1) // 2


def get_valid_actions(
    position: Position,
    stones: int,
    board_size: int,
) -> list[tuple[MoveType, Position | None, int]]:
    """Get all valid actions for a territory.

    Returns a list of (MoveType, destination, stones_to_send) tuples.
    For STAY, destination is None and stones_to_send is 0.

    Args:
        position: The position of the territory
        stones: Number of stones at this position
        board_size: Size of the game board

    Returns:
        List of valid action tuples
    """
    actions: list[tuple[MoveType, Position | None, int]] = []

    # STAY is always valid
    actions.append((MoveType.STAY, None, 0))

    # Get neighbors for movement options
    neighbors = position.neighbors(board_size)
    half_stones = calculate_half(stones)

    for neighbor in neighbors:
        # SEND_HALF option
        actions.append((MoveType.SEND_HALF, neighbor, half_stones))
        # SEND_ALL option
        actions.append((MoveType.SEND_ALL, neighbor, stones))

    return actions


def create_action_from_move_type(
    position: Position,
    move_type: MoveType,
    destination: Position | None,
    stones: int,
) -> TerritoryAction:
    """Create a TerritoryAction from a move type.

    Args:
        position: Source position
        move_type: Type of move (STAY, SEND_HALF, SEND_ALL)
        destination: Target position (None for STAY)
        stones: Total stones at the position

    Returns:
        TerritoryAction for this move
    """
    if move_type == MoveType.STAY:
        return create_grow_action(position)
    elif move_type == MoveType.SEND_HALF:
        half = calculate_half(stones)
        return create_simple_move_action(position, destination, half)
    else:  # SEND_ALL
        return create_simple_move_action(position, destination, stones)
