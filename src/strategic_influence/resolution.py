"""Resolution logic for Strategic Influence.

V4: Truly simultaneous movement resolution.

Resolution order:
1. All departures happen simultaneously (stones leave sources)
2. Reinforcements resolve (stones to friendly territory - always succeeds)
3. Expansions resolve (with simultaneous contested handling)
4. Attacks resolve (combat against post-reinforcement defenders)
5. Growth phase (territories that chose GROW gain stones)

All functions are pure - the RNG is passed in explicitly for reproducibility.
"""

from random import Random
from collections import defaultdict

from .types import (
    Owner,
    Position,
    TerritoryBoard,
    StoneMovement,
    TurnActions,
    MovementResult,
    CombatResult,
    CombatOutcome,
    ExpansionRoll,
    ExpansionResult,
    create_neutral_territory,
    create_territory,
)
from .config import GameConfig
from .combat import resolve_combat


def resolve_expansion(
    position: Position,
    expander: Owner,
    stones: int,
    success_rate: float,
    rng: Random,
) -> ExpansionResult:
    """Resolve an expansion attempt into neutral territory.

    Each stone has success_rate probability to succeed.
    If ANY stone succeeds, all stones claim the territory.
    If ALL stones fail, all stones are lost.

    With success_rate=1.0, expansion is deterministic (always succeeds).
    """
    rolls = []
    any_success = False

    for _ in range(stones):
        roll_value = rng.random()
        success = roll_value < success_rate
        rolls.append(ExpansionRoll(roll_value=roll_value, success=success))
        if success:
            any_success = True

    return ExpansionResult(
        position=position,
        expander=expander,
        stones_sent=stones,
        rolls=tuple(rolls),
        succeeded=any_success,
        stones_surviving=stones if any_success else 0,
    )


def _apply_all_departures(
    board: TerritoryBoard,
    actions: TurnActions,
) -> TerritoryBoard:
    """Remove all moving stones from their sources simultaneously.

    Returns the board state after all stones have left but before arrivals.
    """
    # Collect total departures per source
    departures: dict[Position, int] = defaultdict(int)

    for movement in actions.player1_actions.get_all_movements():
        departures[movement.source] += movement.count
    for movement in actions.player2_actions.get_all_movements():
        departures[movement.source] += movement.count

    # Apply departures
    current_board = board
    for source, count in departures.items():
        territory = current_board.get(source)
        remaining = territory.stones - count
        if remaining > 0:
            current_board = current_board.with_stones(source, territory.owner, remaining)
        else:
            # Territory abandoned
            current_board = current_board.with_territory(source, create_neutral_territory())

    return current_board


def _group_movements_by_destination(
    actions: TurnActions,
) -> dict[Position, dict[Owner, list[StoneMovement]]]:
    """Group all movements by destination, then by owner."""
    result: dict[Position, dict[Owner, list[StoneMovement]]] = defaultdict(
        lambda: {Owner.PLAYER_1: [], Owner.PLAYER_2: []}
    )

    for movement in actions.player1_actions.get_all_movements():
        result[movement.destination][Owner.PLAYER_1].append(movement)
    for movement in actions.player2_actions.get_all_movements():
        result[movement.destination][Owner.PLAYER_2].append(movement)

    return result


def resolve_all_movements(
    board: TerritoryBoard,
    actions: TurnActions,
    config: GameConfig,
    rng: Random,
) -> tuple[TerritoryBoard, tuple[MovementResult, ...]]:
    """Resolve all movements simultaneously.

    Resolution order:
    1. All departures (stones leave sources)
    2. Reinforcements (stones to friendly territory)
    3. Expansions (contested handled simultaneously)
    4. Attacks (combat against post-reinforcement defenders)
    """
    results: list[MovementResult] = []

    # Phase 1: All departures happen simultaneously
    post_departure_board = _apply_all_departures(board, actions)

    # Group movements by destination
    movements_by_dest = _group_movements_by_destination(actions)

    # Track the current board state as we process arrivals
    current_board = post_departure_board

    # Phase 2: Reinforcements first (for both players)
    # This ensures defenders get reinforcements before being attacked
    for dest, by_owner in movements_by_dest.items():
        dest_owner = current_board.get_owner(dest)

        for owner in [Owner.PLAYER_1, Owner.PLAYER_2]:
            movements = by_owner[owner]
            if not movements:
                continue

            # Check if this is a reinforcement (moving to own territory)
            if dest_owner == owner:
                total_stones = sum(m.count for m in movements)
                current_stones = current_board.get_stones(dest)
                current_board = current_board.with_stones(
                    dest, owner, current_stones + total_stones
                )

                # Record results for each movement
                for movement in movements:
                    results.append(MovementResult(
                        movement=movement,
                        owner=owner,
                        combat=None,
                        expansion=None,
                        retreat_count=0,
                    ))

    # Phase 3: Expansions (to neutral territories)
    # Handle contested expansions simultaneously
    # Track destinations already fully processed (to skip in attack phase)
    processed_destinations: set[Position] = set()

    for dest, by_owner in movements_by_dest.items():
        dest_owner = current_board.get_owner(dest)
        if dest_owner != Owner.NEUTRAL:
            continue  # Not neutral, handle in attack phase

        p1_movements = by_owner[Owner.PLAYER_1]
        p2_movements = by_owner[Owner.PLAYER_2]
        p1_total = sum(m.count for m in p1_movements)
        p2_total = sum(m.count for m in p2_movements)

        if p1_total > 0 and p2_total > 0:
            # Contested expansion - both roll simultaneously
            current_board, p1_results, p2_results = _resolve_contested_expansion(
                current_board, dest, p1_movements, p2_movements, config, rng
            )
            results.extend(p1_results)
            results.extend(p2_results)
            # Mark as processed so attack phase doesn't re-process
            processed_destinations.add(dest)

        elif p1_total > 0:
            # Only P1 expanding
            current_board, exp_results = _resolve_uncontested_expansion(
                current_board, dest, p1_movements, Owner.PLAYER_1, config, rng
            )
            results.extend(exp_results)

        elif p2_total > 0:
            # Only P2 expanding
            current_board, exp_results = _resolve_uncontested_expansion(
                current_board, dest, p2_movements, Owner.PLAYER_2, config, rng
            )
            results.extend(exp_results)

    # Phase 4: Attacks (to enemy territories)
    for dest, by_owner in movements_by_dest.items():
        # Skip if already fully processed in expansion phase (contested expansion)
        if dest in processed_destinations:
            continue

        dest_territory = current_board.get(dest)
        dest_owner = dest_territory.owner

        if dest_owner == Owner.NEUTRAL:
            continue  # Already handled in expansion phase

        # Find attacking movements (from opponent)
        if dest_owner == Owner.PLAYER_1:
            attacking_movements = by_owner[Owner.PLAYER_2]
            attacker = Owner.PLAYER_2
        else:
            attacking_movements = by_owner[Owner.PLAYER_1]
            attacker = Owner.PLAYER_1

        if not attacking_movements:
            continue  # No attack on this territory

        # Combine all attacking stones
        total_attackers = sum(m.count for m in attacking_movements)
        defender_stones = dest_territory.stones

        # Resolve combat
        combat_result = resolve_combat(
            position=dest,
            attacker=attacker,
            attacker_stones=total_attackers,
            defender=dest_owner,
            defender_stones=defender_stones,
            config=config,
            rng=rng,
        )

        # Apply combat result
        if combat_result.outcome == CombatOutcome.ATTACKER_WINS:
            current_board = current_board.with_stones(
                dest, attacker, combat_result.attacker_surviving
            )
        elif combat_result.outcome == CombatOutcome.DEFENDER_HOLDS:
            current_board = current_board.with_stones(
                dest, dest_owner, combat_result.defender_surviving
            )
            # Handle retreat - survivors go back to their sources
            if combat_result.attacker_surviving > 0:
                current_board = _handle_retreat(
                    current_board, attacking_movements,
                    combat_result.attacker_surviving, attacker
                )
        else:  # MUTUAL_DESTRUCTION
            current_board = current_board.with_territory(dest, create_neutral_territory())

        # Record results for each movement (share the combat result)
        for movement in attacking_movements:
            # Calculate proportional retreat for this movement
            proportion = movement.count / total_attackers
            retreat = round(combat_result.attacker_surviving * proportion)
            results.append(MovementResult(
                movement=movement,
                owner=attacker,
                combat=combat_result,
                expansion=None,
                retreat_count=retreat,
            ))

    return current_board, tuple(results)


def _resolve_uncontested_expansion(
    board: TerritoryBoard,
    dest: Position,
    movements: list[StoneMovement],
    owner: Owner,
    config: GameConfig,
    rng: Random,
) -> tuple[TerritoryBoard, list[MovementResult]]:
    """Resolve expansion when only one player is expanding to this position."""
    total_stones = sum(m.count for m in movements)

    expansion_result = resolve_expansion(
        position=dest,
        expander=owner,
        stones=total_stones,
        success_rate=config.expansion_success_rate,
        rng=rng,
    )

    if expansion_result.succeeded:
        board = board.with_stones(dest, owner, total_stones)
    # else: stones are lost, territory stays neutral

    # Create results for each movement
    results = []
    for movement in movements:
        results.append(MovementResult(
            movement=movement,
            owner=owner,
            combat=None,
            expansion=expansion_result,
            retreat_count=0,
        ))

    return board, results


def _resolve_contested_expansion(
    board: TerritoryBoard,
    dest: Position,
    p1_movements: list[StoneMovement],
    p2_movements: list[StoneMovement],
    config: GameConfig,
    rng: Random,
) -> tuple[TerritoryBoard, list[MovementResult], list[MovementResult]]:
    """Resolve expansion when both players are expanding to the same neutral position.

    Both players roll simultaneously. Then:
    - If only one succeeds: they claim the territory
    - If both succeed: combat between survivors
    - If neither succeeds: territory stays neutral, all stones lost
    """
    p1_total = sum(m.count for m in p1_movements)
    p2_total = sum(m.count for m in p2_movements)

    # Both players roll for expansion
    p1_expansion = resolve_expansion(dest, Owner.PLAYER_1, p1_total, config.expansion_success_rate, rng)
    p2_expansion = resolve_expansion(dest, Owner.PLAYER_2, p2_total, config.expansion_success_rate, rng)

    p1_results = []
    p2_results = []
    combat_result = None

    if p1_expansion.succeeded and p2_expansion.succeeded:
        # Both succeeded - combat!
        combat_result = resolve_combat(
            position=dest,
            attacker=Owner.PLAYER_1,  # Arbitrary - both are "attacking" neutral
            attacker_stones=p1_total,
            defender=Owner.PLAYER_2,
            defender_stones=p2_total,
            config=config,
            rng=rng,
        )

        if combat_result.outcome == CombatOutcome.ATTACKER_WINS:
            board = board.with_stones(dest, Owner.PLAYER_1, combat_result.attacker_surviving)
        elif combat_result.outcome == CombatOutcome.DEFENDER_HOLDS:
            board = board.with_stones(dest, Owner.PLAYER_2, combat_result.defender_surviving)
        # else: MUTUAL_DESTRUCTION - stays neutral

    elif p1_expansion.succeeded:
        # Only P1 succeeded
        board = board.with_stones(dest, Owner.PLAYER_1, p1_total)

    elif p2_expansion.succeeded:
        # Only P2 succeeded
        board = board.with_stones(dest, Owner.PLAYER_2, p2_total)

    # else: neither succeeded, territory stays neutral, all stones lost

    # Create results for P1 movements
    for movement in p1_movements:
        p1_results.append(MovementResult(
            movement=movement,
            owner=Owner.PLAYER_1,
            combat=combat_result,  # May be None if no combat
            expansion=p1_expansion,
            retreat_count=0,  # No retreat in contested expansion
        ))

    # Create results for P2 movements
    for movement in p2_movements:
        p2_results.append(MovementResult(
            movement=movement,
            owner=Owner.PLAYER_2,
            combat=combat_result,
            expansion=p2_expansion,
            retreat_count=0,
        ))

    return board, p1_results, p2_results


def _handle_retreat(
    board: TerritoryBoard,
    movements: list[StoneMovement],
    total_survivors: int,
    owner: Owner,
) -> TerritoryBoard:
    """Distribute retreating survivors back to their source territories.

    Survivors are distributed proportionally to how many stones each source sent.
    """
    if total_survivors == 0:
        return board

    total_sent = sum(m.count for m in movements)

    # Group by source
    by_source: dict[Position, int] = defaultdict(int)
    for movement in movements:
        by_source[movement.source] += movement.count

    # Distribute survivors proportionally
    distributed = 0
    sources = list(by_source.items())
    for i, (source, sent) in enumerate(sources):
        if i == len(sources) - 1:
            # Last source gets remainder to avoid rounding errors
            retreat_count = total_survivors - distributed
        else:
            retreat_count = round(total_survivors * sent / total_sent)
            distributed += retreat_count

        if retreat_count > 0:
            source_territory = board.get(source)
            if source_territory.owner == Owner.NEUTRAL:
                # Source was abandoned, reclaim it
                board = board.with_stones(source, owner, retreat_count)
            elif source_territory.owner == owner:
                # Add to existing stones
                board = board.with_stones(
                    source, owner, source_territory.stones + retreat_count
                )
            # If someone else owns it now (very edge case), survivors are lost

    return board


def apply_growth(
    board: TerritoryBoard,
    actions: TurnActions,
    config: GameConfig,
) -> tuple[TerritoryBoard, tuple[Position, ...]]:
    """Apply growth to territories that chose GROW.

    Territories that chose GROW (and still exist) gain stones_per_turn stones,
    up to the maximum allowed (max_stones).
    """
    grown_positions: list[Position] = []
    current_board = board
    stones_to_add = config.game.growth.stones_per_turn
    max_stones = config.max_stones

    # Check all actions - GROW means no movements from that territory
    for player_actions in [actions.player1_actions, actions.player2_actions]:
        for action in player_actions.actions:
            if action.is_grow:
                pos = action.position
                territory = current_board.get(pos)

                # Territory must still be owned by the same player
                if territory.owner == player_actions.player:
                    # Cap at max_stones
                    current_stones = territory.stones
                    if current_stones < max_stones:
                        new_stones = min(current_stones + stones_to_add, max_stones)
                        current_board = current_board.with_stones(
                            pos, territory.owner, new_stones
                        )
                        grown_positions.append(pos)

    return current_board, tuple(grown_positions)


def cap_territory_stones(
    board: TerritoryBoard,
    max_stones: int,
) -> TerritoryBoard:
    """Cap all territory stone counts at the maximum allowed.

    This handles cases where multiple sources send stones to the same destination,
    potentially exceeding the cap.
    """
    current_board = board
    for pos in board.all_positions():
        territory = board.get(pos)
        if territory.owner != Owner.NEUTRAL and territory.stones > max_stones:
            current_board = current_board.with_stones(
                pos, territory.owner, max_stones
            )
    return current_board


def resolve_turn(
    board: TerritoryBoard,
    actions: TurnActions,
    config: GameConfig,
    rng: Random,
) -> tuple[TerritoryBoard, tuple[MovementResult, ...], tuple[Position, ...]]:
    """Resolve a complete turn.

    Turn resolution order:
    1. Resolve all movements simultaneously
    2. Cap stones at maximum
    3. Apply growth to GROW territories

    Args:
        board: Board state at start of turn.
        actions: Both players' actions.
        config: Game configuration.
        rng: Random number generator.

    Returns:
        Tuple of (final_board, movement_results, grown_positions).
    """
    # Phase 1: Resolve movements (simultaneous)
    board_after_movement, movement_results = resolve_all_movements(
        board, actions, config, rng
    )

    # Phase 2: Cap stones at maximum (handles multi-source reinforcements/attacks)
    board_capped = cap_territory_stones(board_after_movement, config.max_stones)

    # Phase 3: Apply growth
    final_board, grown_positions = apply_growth(
        board_capped, actions, config
    )

    return final_board, movement_results, grown_positions
