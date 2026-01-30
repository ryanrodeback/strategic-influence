"""Position evaluation heuristics for Strategic Influence.

Provides reusable evaluation functions for AI agents.
All functions evaluate from a specific player's perspective.
"""

from dataclasses import dataclass, field
from typing import Callable

from .types import (
    Owner, Position, GameState, TerritoryBoard,
    MoveType, calculate_half,
)
from .config import GameConfig


@dataclass
class EvaluationWeights:
    """Configurable weights for position evaluation."""
    territory_count: float = 10.0
    stone_advantage: float = 1.5
    growth_potential: float = 3.0
    expansion_opportunity: float = 2.5
    center_control: float = 2.0
    attack_opportunity: float = 1.5
    threatened_penalty: float = 2.0  # Applied as negative
    connectivity: float = 1.0
    merge_potential: float = 1.5  # Ability to merge back together


# Preset weight configurations
BALANCED_WEIGHTS = EvaluationWeights()

INTUITION_WEIGHTS = EvaluationWeights(
    territory_count=8.0,  # Important but growth potential matters more early
    stone_advantage=1.0,
    growth_potential=5.0,  # User insight: growth potential is super valuable
    expansion_opportunity=4.0,  # User insight: expand first when safe
    center_control=1.5,
    attack_opportunity=1.0,
    threatened_penalty=3.0,  # Threat awareness is key
    connectivity=1.5,
    merge_potential=2.5,  # User insight: merge-ability matters
)

AGGRESSIVE_WEIGHTS = EvaluationWeights(
    territory_count=10.0,
    stone_advantage=1.0,
    growth_potential=2.0,
    expansion_opportunity=3.5,
    center_control=2.5,
    attack_opportunity=3.0,  # Prioritize attacks
    threatened_penalty=1.5,
    connectivity=0.5,
    merge_potential=0.5,
)

DEFENSIVE_WEIGHTS = EvaluationWeights(
    territory_count=12.0,
    stone_advantage=2.0,
    growth_potential=4.0,
    expansion_opportunity=2.0,
    center_control=1.5,
    attack_opportunity=0.8,
    threatened_penalty=3.5,  # Very threat-aware
    connectivity=2.0,
    merge_potential=2.0,
)

# === NEW EXPERIMENTAL WEIGHTS ===

# Growth-First (Moderate): Growth is #1 but still balanced
GROWTH_FIRST_MODERATE = EvaluationWeights(
    territory_count=5.0,    # Still matters, but not dominant
    stone_advantage=1.0,    # Minor factor
    growth_potential=10.0,  # THE KING - most important!
    expansion_opportunity=8.0,  # Having places to expand
    center_control=2.0,     # Helps with expansion options
    attack_opportunity=1.0, # Low - only attack when necessary
    threatened_penalty=3.0, # Safety matters
    connectivity=2.0,       # Enables merging
    merge_potential=3.0,    # Can recover after splitting
)

# Growth-First (Extreme): Push growth to the limit
GROWTH_FIRST_EXTREME = EvaluationWeights(
    territory_count=2.0,    # Almost ignore current count
    stone_advantage=0.5,    # Barely matters
    growth_potential=15.0,  # EXTREMELY important
    expansion_opportunity=12.0,  # Must have expansion options
    center_control=1.0,     # Minor
    attack_opportunity=0.5, # Almost never attack
    threatened_penalty=4.0, # Safety still matters
    connectivity=1.0,       # Minor
    merge_potential=2.0,    # Minor
)

# Minimalist: Only growth_potential and threatened_penalty
MINIMALIST_WEIGHTS = EvaluationWeights(
    territory_count=0.0,    # Ignore!
    stone_advantage=0.0,    # Ignore!
    growth_potential=10.0,  # Primary factor
    expansion_opportunity=0.0,  # Ignore!
    center_control=0.0,     # Ignore!
    attack_opportunity=0.0, # Ignore!
    threatened_penalty=5.0, # Secondary factor (safety)
    connectivity=0.0,       # Ignore!
    merge_potential=0.0,    # Ignore!
)

# === ULTRA-MINIMAL: Test if territory_count alone is sufficient ===

# Territory-Only: User's hypothesis - territory count IS growth potential
# Let Minimax's lookahead handle threats naturally
TERRITORY_ONLY_WEIGHTS = EvaluationWeights(
    territory_count=10.0,   # THE ONLY THING THAT MATTERS
    stone_advantage=0.0,
    growth_potential=0.0,
    expansion_opportunity=0.0,
    center_control=0.0,
    attack_opportunity=0.0,
    threatened_penalty=0.0,  # Trust Minimax to see threats via lookahead
    connectivity=0.0,
    merge_potential=0.0,
)

# Territory + Safety: Same but with explicit threat awareness
# Tests whether depth-2 lookahead is sufficient or needs help
TERRITORY_SAFETY_WEIGHTS = EvaluationWeights(
    territory_count=10.0,   # Primary: maximize territories
    stone_advantage=0.0,
    growth_potential=0.0,
    expansion_opportunity=0.0,
    center_control=0.0,
    attack_opportunity=0.0,
    threatened_penalty=3.0,  # Secondary: don't get killed
    connectivity=0.0,
    merge_potential=0.0,
)


def get_phase_multipliers(current_turn: int, total_turns: int) -> dict[str, float]:
    """Return weight multipliers based on game phase.

    Early game: expansion and growth potential matter more
    Mid game: balanced
    Late game: territory count is critical
    """
    progress = current_turn / total_turns if total_turns > 0 else 0

    if progress < 0.3:  # Early game
        return {
            'territory_count': 0.7,
            'stone_advantage': 1.2,
            'growth_potential': 1.5,
            'expansion_opportunity': 1.4,
            'center_control': 1.2,
            'attack_opportunity': 0.5,
            'threatened_penalty': 0.8,
            'connectivity': 0.8,
            'merge_potential': 1.2,
        }
    elif progress < 0.7:  # Mid game
        return {
            'territory_count': 1.0,
            'stone_advantage': 1.0,
            'growth_potential': 1.0,
            'expansion_opportunity': 1.2,
            'center_control': 1.0,
            'attack_opportunity': 1.2,
            'threatened_penalty': 1.0,
            'connectivity': 1.0,
            'merge_potential': 1.0,
        }
    else:  # Late game
        return {
            'territory_count': 2.0,  # Critical!
            'stone_advantage': 0.6,
            'growth_potential': 0.5,
            'expansion_opportunity': 1.5,
            'center_control': 0.8,
            'attack_opportunity': 1.5,
            'threatened_penalty': 1.2,
            'connectivity': 0.8,
            'merge_potential': 0.5,
        }


# =============================================================================
# Core Evaluation Features
# =============================================================================

def territory_count_difference(board: TerritoryBoard, player: Owner) -> float:
    """Direct measure of winning condition."""
    counts = board.count_territories()
    return float(counts[player] - counts[player.opponent()])


def stone_advantage(board: TerritoryBoard, player: Owner) -> float:
    """Material advantage in total stones.

    Uses diminishing returns to discourage stone hoarding.
    """
    import math

    my_stones = board.total_stones(player)
    opp_stones = board.total_stones(player.opponent())
    my_territories = len(list(board.positions_owned_by(player)))

    # Diminishing returns: log scale
    if my_stones > 0 and my_territories > 0:
        effective_my = my_territories * math.log2(1 + my_stones / my_territories)
    else:
        effective_my = 0

    return effective_my - opp_stones * 0.8


def growth_potential(
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
) -> float:
    """Count territories that can beneficially grow.

    Bonus for territories that can grow safely (not threatened).
    """
    max_stones = config.max_stones
    score = 0.0

    for pos in board.positions_owned_by(player):
        territory = board.get(pos)
        if territory.stones < max_stones:
            # Can grow
            score += 1.0
            # Bonus if not under immediate threat
            if not is_position_threatened(pos, board, player, config):
                score += 0.5

    return score


def expansion_opportunities(
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
) -> float:
    """Score based on accessible neutral territories."""
    score = 0.0
    counted_neutrals: set[Position] = set()

    for pos in board.positions_owned_by(player):
        territory = board.get(pos)
        stones = territory.stones
        half_stones = calculate_half(stones)

        for neighbor in pos.neighbors(config.board_size):
            if board.get_owner(neighbor) == Owner.NEUTRAL and neighbor not in counted_neutrals:
                counted_neutrals.add(neighbor)
                # Base value for having expansion option
                score += 1.0
                # Bonus for safe expansion (half >= 2 for 75% success with deterministic)
                if half_stones >= 2:
                    score += 0.5
                # Extra bonus for very safe (half >= 3)
                if half_stones >= 3:
                    score += 0.3

    return score


def center_control(
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
) -> float:
    """Score based on proximity of owned territories to center."""
    score = 0.0
    mid = config.board_size // 2
    max_dist = mid * 2

    for pos in board.positions_owned_by(player):
        dist = abs(pos.row - mid) + abs(pos.col - mid)
        position_value = 1.0 - (dist / max_dist) if max_dist > 0 else 1.0
        score += position_value

    # Extra bonus for THE center position
    center_pos = Position(mid, mid)
    if board.get_owner(center_pos) == player:
        score += 1.5

    return score


def attack_opportunities(
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
) -> float:
    """Score based on weak enemy territories we could attack."""
    score = 0.0
    opponent = player.opponent()
    evaluated_targets: set[Position] = set()

    for pos in board.positions_owned_by(player):
        territory = board.get(pos)
        my_stones = territory.stones
        half_stones = calculate_half(my_stones)

        for neighbor in pos.neighbors(config.board_size):
            if neighbor in evaluated_targets:
                continue

            neighbor_territory = board.get(neighbor)
            if neighbor_territory.owner == opponent:
                evaluated_targets.add(neighbor)
                enemy_stones = neighbor_territory.stones

                # Score based on combat advantage
                if my_stones > enemy_stones:
                    advantage = my_stones - enemy_stones
                    score += 0.5 + 0.2 * advantage

                    # Extra bonus if SEND_HALF can win (keeps territory!)
                    if half_stones > enemy_stones:
                        score += 0.8  # Very valuable

    return score


def threatened_territories(
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
) -> float:
    """Penalty for territories that could be attacked next turn.

    Returns a positive number (to be used as penalty).
    """
    penalty = 0.0
    opponent = player.opponent()

    for pos in board.positions_owned_by(player):
        my_stones = board.get_stones(pos)

        for neighbor in pos.neighbors(config.board_size):
            neighbor_territory = board.get(neighbor)
            if neighbor_territory.owner == opponent:
                enemy_stones = neighbor_territory.stones

                if enemy_stones >= my_stones:
                    # Serious threat
                    penalty += 1.0 + 0.2 * (enemy_stones - my_stones)
                elif enemy_stones >= my_stones - 2:
                    # Moderate threat
                    penalty += 0.5

                break  # Count each territory's worst threat once

    return penalty


def connectivity_score(
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
) -> float:
    """Score for having connected, mutually-supporting territories."""
    score = 0.0

    for pos in board.positions_owned_by(player):
        friendly_neighbors = 0
        for neighbor in pos.neighbors(config.board_size):
            if board.get_owner(neighbor) == player:
                friendly_neighbors += 1

        if friendly_neighbors == 0:
            score -= 0.3  # Isolated territory penalty
        else:
            score += 0.3 * friendly_neighbors

    return score


def merge_potential(
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
) -> float:
    """Score for ability to merge territories back together.

    User insight: Being able to split and merge back is valuable
    because it allows compound growth while maintaining flexibility.
    """
    score = 0.0

    for pos in board.positions_owned_by(player):
        territory = board.get(pos)
        my_stones = territory.stones

        # Count friendly neighbors we could merge with
        friendly_neighbors = []
        for neighbor in pos.neighbors(config.board_size):
            if board.get_owner(neighbor) == player:
                friendly_neighbors.append(neighbor)

        if friendly_neighbors:
            # Merge potential: can reinforce each other
            score += 0.5 * len(friendly_neighbors)

            # Extra value if merging would create strong position
            # (combined stones > any nearby threat)
            combined_potential = my_stones + sum(
                board.get_stones(n) for n in friendly_neighbors
            )
            # This is capped at max_stones anyway, but indicates strength
            score += min(combined_potential / config.max_stones, 1.0) * 0.5

    return score


# =============================================================================
# Threat Analysis Helpers
# =============================================================================

def is_position_threatened(
    pos: Position,
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
) -> bool:
    """Check if a position is under immediate threat."""
    my_stones = board.get_stones(pos)
    opponent = player.opponent()

    for neighbor in pos.neighbors(config.board_size):
        if board.get_owner(neighbor) == opponent:
            enemy_stones = board.get_stones(neighbor)
            if enemy_stones >= my_stones:
                return True

    return False


def turns_until_threat_reaches(
    pos: Position,
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
) -> int:
    """Estimate turns until nearest threat could reach this position.

    Returns a large number (999) if no threats exist.

    User insight: This determines if we can safely split.
    """
    opponent = player.opponent()
    my_stones = board.get_stones(pos)

    # BFS from enemy positions
    enemy_positions = list(board.positions_owned_by(opponent))
    if not enemy_positions:
        return 999

    # Find minimum distance to a threatening enemy
    min_turns = 999

    for enemy_pos in enemy_positions:
        enemy_stones = board.get_stones(enemy_pos)
        if enemy_stones < my_stones:
            continue  # Not a threat

        # Simple Manhattan distance as turn estimate
        distance = abs(pos.row - enemy_pos.row) + abs(pos.col - enemy_pos.col)
        min_turns = min(min_turns, distance)

    return min_turns


def can_safely_divide(
    pos: Position,
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
    recovery_turns: int = 2,
) -> bool:
    """Check if a territory can safely divide.

    User insight: Split is optimal until a threat can reach you
    before you can grow strong again (or reinforce yourself).

    Args:
        recovery_turns: How many turns needed to recover from split
    """
    turns_to_threat = turns_until_threat_reaches(pos, board, player, config)
    return turns_to_threat > recovery_turns


# =============================================================================
# Complete Evaluation Function
# =============================================================================

def evaluate_position(
    state: GameState,
    player: Owner,
    config: GameConfig,
    weights: EvaluationWeights | None = None,
    use_phase_multipliers: bool = True,
) -> float:
    """Comprehensive position evaluation.

    Returns positive for player advantage, negative for disadvantage.
    """
    if weights is None:
        weights = BALANCED_WEIGHTS

    board = state.board

    # Get phase multipliers
    if use_phase_multipliers:
        phase_mult = get_phase_multipliers(state.current_turn, config.num_turns)
    else:
        phase_mult = {k: 1.0 for k in [
            'territory_count', 'stone_advantage', 'growth_potential',
            'expansion_opportunity', 'center_control', 'attack_opportunity',
            'threatened_penalty', 'connectivity', 'merge_potential'
        ]}

    # Calculate features
    score = 0.0

    score += territory_count_difference(board, player) * weights.territory_count * phase_mult['territory_count']
    score += stone_advantage(board, player) * weights.stone_advantage * phase_mult['stone_advantage']
    score += growth_potential(board, player, config) * weights.growth_potential * phase_mult['growth_potential']
    score += expansion_opportunities(board, player, config) * weights.expansion_opportunity * phase_mult['expansion_opportunity']
    score += center_control(board, player, config) * weights.center_control * phase_mult['center_control']
    score += attack_opportunities(board, player, config) * weights.attack_opportunity * phase_mult['attack_opportunity']
    score -= threatened_territories(board, player, config) * weights.threatened_penalty * phase_mult['threatened_penalty']
    score += connectivity_score(board, player, config) * weights.connectivity * phase_mult['connectivity']
    score += merge_potential(board, player, config) * weights.merge_potential * phase_mult['merge_potential']

    return score


def evaluate_board(
    board: TerritoryBoard,
    player: Owner,
    config: GameConfig,
    current_turn: int = 10,
    weights: EvaluationWeights | None = None,
) -> float:
    """Evaluate a board position directly (for use in search)."""
    if weights is None:
        weights = BALANCED_WEIGHTS

    phase_mult = get_phase_multipliers(current_turn, config.num_turns)

    score = 0.0
    score += territory_count_difference(board, player) * weights.territory_count * phase_mult['territory_count']
    score += stone_advantage(board, player) * weights.stone_advantage * phase_mult['stone_advantage']
    score += growth_potential(board, player, config) * weights.growth_potential * phase_mult['growth_potential']
    score += expansion_opportunities(board, player, config) * weights.expansion_opportunity * phase_mult['expansion_opportunity']
    score += center_control(board, player, config) * weights.center_control * phase_mult['center_control']
    score += attack_opportunities(board, player, config) * weights.attack_opportunity * phase_mult['attack_opportunity']
    score -= threatened_territories(board, player, config) * weights.threatened_penalty * phase_mult['threatened_penalty']
    score += connectivity_score(board, player, config) * weights.connectivity * phase_mult['connectivity']
    score += merge_potential(board, player, config) * weights.merge_potential * phase_mult['merge_potential']

    return score
