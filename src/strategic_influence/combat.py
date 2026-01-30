"""Combat resolution for Strategic Influence.

V2: Stone-count and combat mechanics.

This module handles combat between attacking and defending stones.
Combat uses alternating 50% dice rolls:
1. Defender rolls first
2. Alternating rolls until one side is eliminated
3. Eliminated stones don't roll

All functions are pure - the RNG is passed in explicitly for reproducibility.
"""

from random import Random

from .types import (
    Owner,
    Position,
    StoneMovement,
    CombatRoll,
    CombatResult,
    CombatOutcome,
)
from .config import GameConfig


def roll_hit(rng: Random, hit_chance: float) -> tuple[bool, float]:
    """Roll for a hit in combat.

    Args:
        rng: Random number generator.
        hit_chance: Probability of a hit (0.0 to 1.0).

    Returns:
        Tuple of (is_hit, roll_value).
    """
    roll = rng.random()
    return roll < hit_chance, roll


def resolve_combat(
    position: Position,
    attacker: Owner,
    attacker_stones: int,
    defender: Owner,
    defender_stones: int,
    config: GameConfig,
    rng: Random,
) -> CombatResult:
    """Resolve combat between attacker and defender.

    Combat proceeds with alternating rolls:
    1. Defender rolls first (50% chance to eliminate one attacker stone)
    2. Then attacker rolls (50% chance to eliminate one defender stone)
    3. Continue alternating until one side is eliminated
    4. Eliminated stones don't get to roll

    Outcomes:
    - ATTACKER_WINS: All defender stones eliminated, attackers claim territory
    - DEFENDER_HOLDS: All attacker stones eliminated, defender keeps territory
    - MUTUAL_DESTRUCTION: Both sides eliminated, territory becomes neutral

    Args:
        position: The position being contested.
        attacker: The attacking player.
        attacker_stones: Number of attacking stones.
        defender: The defending player.
        defender_stones: Number of defending stones.
        config: Game configuration.
        rng: Random number generator.

    Returns:
        CombatResult with the outcome and all rolls.
    """
    if attacker == Owner.NEUTRAL:
        raise ValueError("Neutral cannot attack")
    if attacker_stones < 1:
        raise ValueError("Attacker must have at least 1 stone")
    if defender_stones < 1:
        raise ValueError("Defender must have at least 1 stone")

    rolls: list[CombatRoll] = []
    current_attacker = attacker_stones
    current_defender = defender_stones
    hit_chance = config.hit_chance

    # Defender rolls first
    defender_turn = True

    while current_attacker > 0 and current_defender > 0:
        if defender_turn:
            # Defender rolls against attacker
            hit, roll_value = roll_hit(rng, hit_chance)
            if hit:
                current_attacker -= 1
            rolls.append(CombatRoll(
                roller=defender,
                target=attacker,
                roll_value=roll_value,
                hit=hit,
                roller_stones_after=current_defender,
                target_stones_after=current_attacker,
            ))
        else:
            # Attacker rolls against defender
            hit, roll_value = roll_hit(rng, hit_chance)
            if hit:
                current_defender -= 1
            rolls.append(CombatRoll(
                roller=attacker,
                target=defender,
                roll_value=roll_value,
                hit=hit,
                roller_stones_after=current_attacker,
                target_stones_after=current_defender,
            ))

        # Only switch turns if the current roller still has stones
        if defender_turn and current_defender > 0:
            defender_turn = False
        elif not defender_turn and current_attacker > 0:
            defender_turn = True

    # Determine outcome
    if current_attacker == 0 and current_defender == 0:
        outcome = CombatOutcome.MUTUAL_DESTRUCTION
    elif current_defender == 0:
        outcome = CombatOutcome.ATTACKER_WINS
    else:
        outcome = CombatOutcome.DEFENDER_HOLDS

    return CombatResult(
        position=position,
        attacker=attacker,
        defender=defender,
        attacker_initial=attacker_stones,
        defender_initial=defender_stones,
        attacker_surviving=current_attacker,
        defender_surviving=current_defender,
        rolls=tuple(rolls),
        outcome=outcome,
    )


def resolve_combat_deterministic(
    position: Position,
    attacker: Owner,
    attacker_stones: int,
    defender: Owner,
    defender_stones: int,
    roll_values: list[float],
    hit_chance: float = 0.5,
) -> CombatResult:
    """Resolve combat with predetermined roll values.

    Useful for testing and replay.

    Args:
        position: The position being contested.
        attacker: The attacking player.
        attacker_stones: Number of attacking stones.
        defender: The defending player.
        defender_stones: Number of defending stones.
        roll_values: List of random values to use for each roll [0, 1).
        hit_chance: Probability threshold for a hit.

    Returns:
        CombatResult with the outcome.
    """
    if attacker == Owner.NEUTRAL:
        raise ValueError("Neutral cannot attack")
    if attacker_stones < 1:
        raise ValueError("Attacker must have at least 1 stone")
    if defender_stones < 1:
        raise ValueError("Defender must have at least 1 stone")

    rolls: list[CombatRoll] = []
    current_attacker = attacker_stones
    current_defender = defender_stones
    roll_index = 0

    defender_turn = True

    while current_attacker > 0 and current_defender > 0:
        # Use provided roll or default to miss if we run out
        if roll_index < len(roll_values):
            roll_value = roll_values[roll_index]
            roll_index += 1
        else:
            roll_value = 1.0  # Default to miss

        hit = roll_value < hit_chance

        if defender_turn:
            if hit:
                current_attacker -= 1
            rolls.append(CombatRoll(
                roller=defender,
                target=attacker,
                roll_value=roll_value,
                hit=hit,
                roller_stones_after=current_defender,
                target_stones_after=current_attacker,
            ))
        else:
            if hit:
                current_defender -= 1
            rolls.append(CombatRoll(
                roller=attacker,
                target=defender,
                roll_value=roll_value,
                hit=hit,
                roller_stones_after=current_attacker,
                target_stones_after=current_defender,
            ))

        if defender_turn and current_defender > 0:
            defender_turn = False
        elif not defender_turn and current_attacker > 0:
            defender_turn = True

    if current_attacker == 0 and current_defender == 0:
        outcome = CombatOutcome.MUTUAL_DESTRUCTION
    elif current_defender == 0:
        outcome = CombatOutcome.ATTACKER_WINS
    else:
        outcome = CombatOutcome.DEFENDER_HOLDS

    return CombatResult(
        position=position,
        attacker=attacker,
        defender=defender,
        attacker_initial=attacker_stones,
        defender_initial=defender_stones,
        attacker_surviving=current_attacker,
        defender_surviving=current_defender,
        rolls=tuple(rolls),
        outcome=outcome,
    )


def calculate_combat_odds(
    attacker_stones: int,
    defender_stones: int,
    hit_chance: float = 0.5,
    num_simulations: int = 10000,
    seed: int | None = None,
) -> dict[CombatOutcome, float]:
    """Calculate approximate odds for each combat outcome.

    Useful for AI decision making.

    Args:
        attacker_stones: Number of attacking stones.
        defender_stones: Number of defending stones.
        hit_chance: Probability of a hit.
        num_simulations: Number of simulations to run.
        seed: Random seed for reproducibility.

    Returns:
        Dictionary mapping CombatOutcome to probability (0.0 to 1.0).
    """
    from .config import create_default_config

    rng = Random(seed)
    config = create_default_config()

    counts = {
        CombatOutcome.ATTACKER_WINS: 0,
        CombatOutcome.DEFENDER_HOLDS: 0,
        CombatOutcome.MUTUAL_DESTRUCTION: 0,
    }

    for _ in range(num_simulations):
        result = resolve_combat(
            position=Position(0, 0),  # Dummy position
            attacker=Owner.PLAYER_1,
            attacker_stones=attacker_stones,
            defender=Owner.PLAYER_2,
            defender_stones=defender_stones,
            config=config,
            rng=rng,
        )
        counts[result.outcome] += 1

    return {
        outcome: count / num_simulations
        for outcome, count in counts.items()
    }


def describe_combat(result: CombatResult) -> str:
    """Generate a human-readable description of combat.

    Args:
        result: The combat result to describe.

    Returns:
        Multi-line string describing the combat.
    """
    lines = [
        f"Combat at {result.position}",
        f"  {result.attacker} ({result.attacker_initial} stones) attacks",
        f"  {result.defender} ({result.defender_initial} stones) defends",
        "",
        "  Rolls:",
    ]

    for i, roll in enumerate(result.rolls, 1):
        hit_str = "HIT!" if roll.hit else "miss"
        lines.append(
            f"    {i}. {roll.roller} rolls {roll.roll_value:.2f}: {hit_str} "
            f"(attacker: {roll.target_stones_after if roll.target == result.attacker else roll.roller_stones_after}, "
            f"defender: {roll.roller_stones_after if roll.target == result.attacker else roll.target_stones_after})"
        )

    lines.append("")
    lines.append(f"  Result: {result.outcome.name}")
    lines.append(f"    Attacker surviving: {result.attacker_surviving}")
    lines.append(f"    Defender surviving: {result.defender_surviving}")

    return "\n".join(lines)
