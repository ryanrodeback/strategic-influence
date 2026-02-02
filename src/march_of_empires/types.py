"""Core types for March of Empires.

This module defines all the immutable data structures used throughout the game:
- Coordinate systems (HexCoord, CornerCoord)
- Game entities (Army, Settlement)
- Board state (HexBoard)
- Game state (GameState)
- Actions and results
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Mapping, Iterator


# =============================================================================
# Enums
# =============================================================================


class Player(Enum):
    """Players in the game."""

    PLAYER_1 = 1
    PLAYER_2 = 2

    def __str__(self) -> str:
        return "Player 1" if self == Player.PLAYER_1 else "Player 2"

    def opponent(self) -> Player:
        """Return the opposing player."""
        return Player.PLAYER_2 if self == Player.PLAYER_1 else Player.PLAYER_1


class GamePhase(Enum):
    """Current phase of the game."""

    SETUP = auto()  # Players placing starting settlements
    PLAYING = auto()  # Main game turns
    COMPLETE = auto()  # Game over


class CornerDirection(Enum):
    """Direction of a corner relative to a hex center.

    In pointy-top orientation, NORTH is the top vertex and SOUTH is the bottom.
    """

    NORTH = auto()
    SOUTH = auto()


# =============================================================================
# Coordinate Types
# =============================================================================


@dataclass(frozen=True, slots=True)
class HexCoord:
    """A hex position using axial coordinates.

    Uses the standard axial coordinate system where:
    - q increases to the right
    - r increases downward
    - s = -q - r (implicit, computed when needed)

    For a radius-3 board centered at (0,0), valid hexes have:
    max(|q|, |r|, |s|) <= 3
    """

    q: int
    r: int

    @property
    def s(self) -> int:
        """Compute the implicit third coordinate."""
        return -self.q - self.r

    def __str__(self) -> str:
        return f"Hex({self.q},{self.r})"

    def __repr__(self) -> str:
        return f"HexCoord({self.q}, {self.r})"

    def distance_to(self, other: HexCoord) -> int:
        """Manhattan distance in cube coordinates."""
        return max(
            abs(self.q - other.q), abs(self.r - other.r), abs(self.s - other.s)
        )

    def is_valid(self, radius: int) -> bool:
        """Check if this hex is within a hexagonal board of given radius."""
        return max(abs(self.q), abs(self.r), abs(self.s)) <= radius

    def neighbors(self) -> tuple[HexCoord, ...]:
        """Return the 6 adjacent hex positions (not filtered for board bounds)."""
        return (
            HexCoord(self.q + 1, self.r),  # East
            HexCoord(self.q + 1, self.r - 1),  # Northeast
            HexCoord(self.q, self.r - 1),  # Northwest
            HexCoord(self.q - 1, self.r),  # West
            HexCoord(self.q - 1, self.r + 1),  # Southwest
            HexCoord(self.q, self.r + 1),  # Southeast
        )

    def valid_neighbors(self, radius: int) -> frozenset[HexCoord]:
        """Return adjacent hexes that are within board bounds."""
        return frozenset(n for n in self.neighbors() if n.is_valid(radius))

    def corners(self) -> tuple[CornerCoord, ...]:
        """Return the 6 corners of this hex."""
        return (
            CornerCoord(self.q, self.r, CornerDirection.NORTH),  # Top
            CornerCoord(self.q, self.r, CornerDirection.SOUTH),  # Bottom
            CornerCoord(self.q + 1, self.r - 1, CornerDirection.SOUTH),  # NE
            CornerCoord(self.q, self.r - 1, CornerDirection.SOUTH),  # NW
            CornerCoord(self.q, self.r + 1, CornerDirection.NORTH),  # SW
            CornerCoord(self.q + 1, self.r, CornerDirection.NORTH),  # SE
        )

    def valid_corners(self, radius: int) -> frozenset[CornerCoord]:
        """Return corners of this hex that are valid for the board."""
        return frozenset(c for c in self.corners() if c.is_valid(radius))


@dataclass(frozen=True, slots=True)
class CornerCoord:
    """A corner (vertex) position on the hex grid.

    Identified by a reference hex (q, r) and whether it's the NORTH or SOUTH
    corner of that hex. This ensures each corner has a canonical representation.

    Each corner touches exactly 3 hexes.
    """

    q: int
    r: int
    direction: CornerDirection

    def __str__(self) -> str:
        d = "N" if self.direction == CornerDirection.NORTH else "S"
        return f"Corner({self.q},{self.r},{d})"

    def __repr__(self) -> str:
        return f"CornerCoord({self.q}, {self.r}, {self.direction})"

    def adjacent_hexes(self) -> frozenset[HexCoord]:
        """Return the 3 hexes that touch this corner."""
        if self.direction == CornerDirection.NORTH:
            return frozenset(
                {
                    HexCoord(self.q, self.r),  # Reference hex
                    HexCoord(self.q, self.r - 1),  # Hex above-left
                    HexCoord(self.q + 1, self.r - 1),  # Hex above-right
                }
            )
        else:  # SOUTH
            return frozenset(
                {
                    HexCoord(self.q, self.r),  # Reference hex
                    HexCoord(self.q - 1, self.r + 1),  # Hex below-left
                    HexCoord(self.q, self.r + 1),  # Hex below-right
                }
            )

    def valid_adjacent_hexes(self, radius: int) -> frozenset[HexCoord]:
        """Return adjacent hexes that are within board bounds."""
        return frozenset(h for h in self.adjacent_hexes() if h.is_valid(radius))

    def is_valid(self, radius: int) -> bool:
        """A corner is valid if at least one of its adjacent hexes is on the board."""
        return len(self.valid_adjacent_hexes(radius)) > 0

    def adjacent_corners(self) -> tuple[CornerCoord, ...]:
        """Return the 3 corners adjacent to this one (connected by hex edges)."""
        if self.direction == CornerDirection.NORTH:
            return (
                CornerCoord(
                    self.q, self.r - 1, CornerDirection.SOUTH
                ),  # Upper-left
                CornerCoord(
                    self.q + 1, self.r - 1, CornerDirection.SOUTH
                ),  # Upper-right
                CornerCoord(
                    self.q, self.r, CornerDirection.SOUTH
                ),  # Directly below
            )
        else:  # SOUTH
            return (
                CornerCoord(
                    self.q - 1, self.r + 1, CornerDirection.NORTH
                ),  # Lower-left
                CornerCoord(
                    self.q, self.r + 1, CornerDirection.NORTH
                ),  # Lower-right
                CornerCoord(
                    self.q, self.r, CornerDirection.NORTH
                ),  # Directly above
            )

    def valid_adjacent_corners(self, radius: int) -> frozenset[CornerCoord]:
        """Return adjacent corners that are valid for the board."""
        return frozenset(c for c in self.adjacent_corners() if c.is_valid(radius))


# Position is a union of HexCoord and CornerCoord
Position = HexCoord | CornerCoord


# =============================================================================
# Game Entities
# =============================================================================


@dataclass(frozen=True, slots=True)
class Army:
    """A mobile army unit.

    Armies can occupy either hex centers or corners.
    Each army has 2 movement points per turn.
    """

    id: int
    owner: Player
    position: Position
    movement_remaining: int = 2

    def __str__(self) -> str:
        return f"Army({self.id}, {self.owner}, {self.position}, MP:{self.movement_remaining})"

    @property
    def is_on_hex(self) -> bool:
        return isinstance(self.position, HexCoord)

    @property
    def is_on_corner(self) -> bool:
        return isinstance(self.position, CornerCoord)

    def with_position(self, new_pos: Position, mp_spent: int = 0) -> Army:
        """Return a new Army at a new position with reduced movement."""
        return Army(
            id=self.id,
            owner=self.owner,
            position=new_pos,
            movement_remaining=self.movement_remaining - mp_spent,
        )

    def with_movement_reset(self, movement_points: int = 2) -> Army:
        """Return a new Army with movement points reset for new turn."""
        return Army(
            id=self.id,
            owner=self.owner,
            position=self.position,
            movement_remaining=movement_points,
        )


@dataclass(frozen=True, slots=True)
class Settlement:
    """A settlement placed at a corner vertex.

    Settlements:
    - Sit on corners (vertices)
    - Create friendly territory (the 3 hexes touching that corner)
    - Generate visibility (you can see those 3 hexes)
    - Contribute +1 to army cap
    """

    id: int
    owner: Player
    position: CornerCoord

    def __str__(self) -> str:
        return f"Settlement({self.id}, {self.owner}, {self.position})"

    def friendly_hexes(self, radius: int) -> frozenset[HexCoord]:
        """Return hexes made friendly by this settlement."""
        return self.position.valid_adjacent_hexes(radius)

    def with_owner(self, new_owner: Player) -> Settlement:
        """Return settlement with new owner (for capture)."""
        return Settlement(id=self.id, owner=new_owner, position=self.position)


# =============================================================================
# Board State
# =============================================================================


@dataclass(frozen=True)
class GameBoard:
    """Complete immutable game board state.

    Stores all settlements and armies with their positions.
    """

    radius: int
    settlements: frozenset[Settlement]
    armies: frozenset[Army]
    _next_army_id: int = 1
    _next_settlement_id: int = 1

    def __str__(self) -> str:
        return f"GameBoard(r={self.radius}, {len(self.settlements)} settlements, {len(self.armies)} armies)"

    # -------------------------------------------------------------------------
    # Queries
    # -------------------------------------------------------------------------

    def all_hexes(self) -> frozenset[HexCoord]:
        """Return all valid hexes on the board."""
        return generate_hex_board(self.radius)

    def all_corners(self) -> frozenset[CornerCoord]:
        """Return all valid corners on the board."""
        return generate_all_corners(self.radius)

    def settlement_at(self, corner: CornerCoord) -> Settlement | None:
        """Get settlement at a corner, if any."""
        for s in self.settlements:
            if s.position == corner:
                return s
        return None

    def armies_at(self, pos: Position) -> frozenset[Army]:
        """Get all armies at a position."""
        return frozenset(a for a in self.armies if a.position == pos)

    def army_by_id(self, army_id: int) -> Army | None:
        """Find army by ID."""
        for a in self.armies:
            if a.id == army_id:
                return a
        return None

    def settlements_of(self, player: Player) -> frozenset[Settlement]:
        """Get all settlements owned by a player."""
        return frozenset(s for s in self.settlements if s.owner == player)

    def armies_of(self, player: Player) -> frozenset[Army]:
        """Get all armies owned by a player."""
        return frozenset(a for a in self.armies if a.owner == player)

    def army_count(self, player: Player) -> int:
        """Count armies for a player."""
        return len(self.armies_of(player))

    def settlement_count(self, player: Player) -> int:
        """Count settlements for a player (equals army cap)."""
        return len(self.settlements_of(player))

    def army_cap(self, player: Player) -> int:
        """Maximum armies a player can have (equals settlement count)."""
        return self.settlement_count(player)

    def friendly_hexes(self, player: Player) -> frozenset[HexCoord]:
        """Get all hexes that are friendly to a player.

        A hex is friendly if touched by any of the player's settlements.
        """
        hexes: set[HexCoord] = set()
        for settlement in self.settlements_of(player):
            hexes.update(settlement.friendly_hexes(self.radius))
        return frozenset(hexes)

    def is_hex_friendly(self, hex_coord: HexCoord, player: Player) -> bool:
        """Check if a hex is friendly to a player."""
        return hex_coord in self.friendly_hexes(player)

    def hex_owner(self, hex_coord: HexCoord) -> Player | None:
        """Get the owner of a hex for movement cost purposes.

        A hex is 'owned' by a player if only that player has settlements touching it.
        If both or neither have settlements touching it, returns None.
        """
        p1_touches = hex_coord in self.friendly_hexes(Player.PLAYER_1)
        p2_touches = hex_coord in self.friendly_hexes(Player.PLAYER_2)

        if p1_touches and not p2_touches:
            return Player.PLAYER_1
        elif p2_touches and not p1_touches:
            return Player.PLAYER_2
        return None

    # -------------------------------------------------------------------------
    # Mutations (return new board)
    # -------------------------------------------------------------------------

    def with_settlement(self, corner: CornerCoord, owner: Player) -> tuple[GameBoard, Settlement]:
        """Return new board with settlement added."""
        settlement = Settlement(
            id=self._next_settlement_id, owner=owner, position=corner
        )
        return (
            GameBoard(
                radius=self.radius,
                settlements=self.settlements | {settlement},
                armies=self.armies,
                _next_army_id=self._next_army_id,
                _next_settlement_id=self._next_settlement_id + 1,
            ),
            settlement,
        )

    def with_army(self, pos: Position, owner: Player, movement: int = 2) -> tuple[GameBoard, Army]:
        """Return new board with army added."""
        army = Army(
            id=self._next_army_id,
            owner=owner,
            position=pos,
            movement_remaining=movement,
        )
        return (
            GameBoard(
                radius=self.radius,
                settlements=self.settlements,
                armies=self.armies | {army},
                _next_army_id=self._next_army_id + 1,
                _next_settlement_id=self._next_settlement_id,
            ),
            army,
        )

    def without_army(self, army_id: int) -> GameBoard:
        """Return new board with army removed."""
        return GameBoard(
            radius=self.radius,
            settlements=self.settlements,
            armies=frozenset(a for a in self.armies if a.id != army_id),
            _next_army_id=self._next_army_id,
            _next_settlement_id=self._next_settlement_id,
        )

    def with_army_moved(self, army_id: int, new_pos: Position, mp_spent: int) -> GameBoard:
        """Return new board with army moved to new position."""
        old_army = self.army_by_id(army_id)
        if old_army is None:
            raise ValueError(f"Army {army_id} not found")

        new_army = old_army.with_position(new_pos, mp_spent)
        return GameBoard(
            radius=self.radius,
            settlements=self.settlements,
            armies=(self.armies - {old_army}) | {new_army},
            _next_army_id=self._next_army_id,
            _next_settlement_id=self._next_settlement_id,
        )

    def with_army_movement_reset(self, army_id: int, movement: int = 2) -> GameBoard:
        """Return new board with army's movement points reset."""
        old_army = self.army_by_id(army_id)
        if old_army is None:
            raise ValueError(f"Army {army_id} not found")

        new_army = old_army.with_movement_reset(movement)
        return GameBoard(
            radius=self.radius,
            settlements=self.settlements,
            armies=(self.armies - {old_army}) | {new_army},
            _next_army_id=self._next_army_id,
            _next_settlement_id=self._next_settlement_id,
        )

    def with_settlement_captured(self, settlement_id: int, new_owner: Player) -> GameBoard:
        """Return new board with settlement ownership changed."""
        old_settlement = None
        for s in self.settlements:
            if s.id == settlement_id:
                old_settlement = s
                break
        if old_settlement is None:
            raise ValueError(f"Settlement {settlement_id} not found")

        new_settlement = old_settlement.with_owner(new_owner)
        return GameBoard(
            radius=self.radius,
            settlements=(self.settlements - {old_settlement}) | {new_settlement},
            armies=self.armies,
            _next_army_id=self._next_army_id,
            _next_settlement_id=self._next_settlement_id,
        )


def create_empty_board(radius: int = 3) -> GameBoard:
    """Create an empty game board."""
    return GameBoard(
        radius=radius,
        settlements=frozenset(),
        armies=frozenset(),
        _next_army_id=1,
        _next_settlement_id=1,
    )


# =============================================================================
# Actions
# =============================================================================


@dataclass(frozen=True, slots=True)
class MoveAction:
    """Move an army to an adjacent position."""

    army_id: int
    to_position: Position


@dataclass(frozen=True, slots=True)
class SettleAction:
    """Found a settlement at the army's current corner position."""

    army_id: int


@dataclass(frozen=True, slots=True)
class PassAction:
    """Army does nothing for the rest of the turn."""

    army_id: int


# Union type for all actions
Action = MoveAction | SettleAction | PassAction


@dataclass(frozen=True)
class TurnActions:
    """All actions for a player's turn.

    Actions are executed in order. Each army can have multiple move actions
    (up to their movement points allow) followed by optionally a settle action.
    """

    player: Player
    actions: tuple[Action, ...]

    def __str__(self) -> str:
        return f"{self.player}: {len(self.actions)} actions"


# =============================================================================
# Results
# =============================================================================


@dataclass(frozen=True)
class CombatResult:
    """Result of combat between armies."""

    position: Position
    attacker_armies: tuple[Army, ...]
    defender_armies: tuple[Army, ...]
    attacker_survivors: int
    defender_survivors: int
    attacker_destroyed: tuple[int, ...]  # Army IDs
    defender_destroyed: tuple[int, ...]  # Army IDs


@dataclass(frozen=True)
class CaptureResult:
    """Result of a settlement capture."""

    settlement_id: int
    corner: CornerCoord
    capturing_player: Player
    previous_owner: Player
    defender_destroyed: int | None  # Army ID if defender was destroyed


@dataclass(frozen=True)
class SpawnResult:
    """Result of army spawning."""

    army: Army
    settlement: Settlement
    reason: str  # "new_settlement" or "respawn"


@dataclass(frozen=True)
class TurnResult:
    """Complete result of a player's turn."""

    turn_number: int
    player: Player
    actions: TurnActions
    spawns: tuple[SpawnResult, ...]
    combats: tuple[CombatResult, ...]
    captures: tuple[CaptureResult, ...]
    new_settlements: tuple[Settlement, ...]
    board_before: GameBoard
    board_after: GameBoard


# =============================================================================
# Game State
# =============================================================================


@dataclass(frozen=True)
class GameState:
    """Complete immutable game state."""

    board: GameBoard
    phase: GamePhase
    current_turn: int
    active_player: Player
    turn_history: tuple[TurnResult, ...]
    setup_complete: frozenset[Player]
    winner: Player | None

    def __str__(self) -> str:
        return f"GameState(turn={self.current_turn}, phase={self.phase.name}, active={self.active_player})"

    @property
    def is_complete(self) -> bool:
        return self.phase == GamePhase.COMPLETE

    @property
    def is_setup(self) -> bool:
        return self.phase == GamePhase.SETUP


@dataclass(frozen=True)
class VisibleState:
    """Game state filtered by fog of war for a specific player."""

    viewer: Player
    visible_hexes: frozenset[HexCoord]
    visible_corners: frozenset[CornerCoord]
    board: GameBoard  # Full board but only visible info should be used
    phase: GamePhase
    current_turn: int
    active_player: Player


# =============================================================================
# Board Generation
# =============================================================================


def generate_hex_board(radius: int) -> frozenset[HexCoord]:
    """Generate all valid hexes for a hexagonal board of given radius.

    Radius 3 gives 37 hexes (1 + 6 + 12 + 18 = 37).
    """
    hexes: list[HexCoord] = []
    for q in range(-radius, radius + 1):
        for r in range(-radius, radius + 1):
            coord = HexCoord(q, r)
            if coord.is_valid(radius):
                hexes.append(coord)
    return frozenset(hexes)


def generate_all_corners(radius: int) -> frozenset[CornerCoord]:
    """Generate all valid corners for a hexagonal board.

    A corner is valid if at least one of its adjacent hexes is on the board.
    """
    corners: set[CornerCoord] = set()
    for q in range(-radius - 1, radius + 2):
        for r in range(-radius - 1, radius + 2):
            for direction in CornerDirection:
                corner = CornerCoord(q, r, direction)
                if corner.is_valid(radius):
                    corners.add(corner)
    return frozenset(corners)
