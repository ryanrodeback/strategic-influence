# Game Variant Examples - Concrete Scenarios

This document provides concrete gameplay examples for each variant to illustrate how mechanics differ from the base game.

---

## Setup Reference (All Variants)

All variants start with the same initial setup:
- 5x5 board
- Player 1 (White) starts in columns A-B and bottom-middle
- Player 2 (Black) starts in columns D-E and top-middle
- Center spot (C3) unclaimed
- Both players place 3 stones during setup

---

## Variant A: TOWER DEFENSE - Scenario

### Turn 1

**Setup:** Player 1 places at A1, A2, B1. Player 2 places at E4, E5, D4.

**Turn 1 Actions:**
- P1: Expands from A1 toward C1 (neutral) - sends 2 stones to bottom level
- P1: Grows at A2
- P1: Grows at B1

- P2: Expands from E4 toward C4 - sends 2 stones to bottom level
- P2: Grows at E5
- P2: Grows at D4

**Resolution:**
- C1 claimed by P1 at level 0 (2 stones at bottom, vulnerable)
- C4 claimed by P2 at level 0
- Other territories grow +1

**Key Difference:** P1 doesn't control C1 yet - they must climb the tower!

### Turn 2

**Turn 2 Actions:**
- P1: Climbs 1 stone from C1 level 0 → level 1
- P1: Climbs 1 stone from C1 level 0 → level 1
- (C1 now has 2 stones at level 1, level 0 empty, higher levels unclaimed)

- P2: Climbs both stones from C4 level 0 → level 1 (similar situation)

**Key Difference:** Taking territory is a multi-turn process. Tower isn't "controlled" until top is held.

### Turn 3 - Combat Scenario

Player 1 decides to assault P2's tower. P1 sends 3 stones from B2 to C4:

- P1: Sends 3 stones to C4 (arrive at level 0)
- P2: Reinforces C4 from D4 (3 stones, arriving at level 1 to defend)

**Combat Resolution (Level-by-level):**
- **Level 0:** P1 has 3 stones, P2 has 0. P1 wins level 0.
- **Level 1:** P1 has 0 stones (just arrived), P2 has 3. P2 wins level 1.
- **Levels 2-4:** Both have 0 stones.

**Outcome:** P2 still controls C4 (holds level 1). P1 controls level 0 but not the tower.
Game continues for 2+ more turns if P1 wants C4.

**Key Learning:** Territory control requires controlling the top. This teaches siege warfare—can you weaken lower levels and breakthrough? Should P2 retreat? Should P1 double down?

---

## Variant B: TIME & DISTANCE - Scenario

### Turn 1

**Setup:** Same as above.

**Turn 1 Actions:**
- P1: Path order to C2 (1 step away) - arrives next turn
- P1: Path order to C2 (same destination from B1) - different stone, also arrives Turn 2
- P1: Grow at A2

- P2: Path order to C3 (1 step away) - arrives next turn
- P2: Path order to C3 (same) - arrives Turn 2
- P2: Grow at D4

**After Turn 1 Resolution:**
- Board shows **in-transit stones** en route to C2 (P1) and C3 (P2)
- Both players see all paths clearly
- Stones are locked into path—cannot change direction

### Turn 2

**Turn 2 Actions:**
- P1: The 2 in-transit stones arrive at C2, resolving as normal expansion (neutral → P1)
- P1: Send stones from A2 to B2 (1 step, arrives Turn 3)
- P1: Send stones from B1 to B2 (1 step, arrives Turn 3)

- P2: The 2 in-transit stones arrive at C3, resolving as normal expansion
- P2: Send stones from E4 to D3 (1 step, arrives Turn 3)
- P2: Send stones from E5 to D3 (1 step, arrives Turn 3)

**Board State:**
- P1 controls C2 (just expanded)
- P2 controls C3 (just expanded)
- 2 P1 stones in-transit to B2 (arrive Turn 3)
- 2 P2 stones in-transit to D3 (arrive Turn 3)

**Player Psychology:** Both players can see reinforcements coming in Turn 3. They must predict what opponent will do when those troops arrive.

### Turn 3 - Feint Example

**Turn 3 Actions:**
- P1: Send the reinforcing stones from C2 toward C3 (attack path, 2 steps)
  - Path commitment: arrive Turn 5
  - Board shows attack route clearly

- P2 sees the attack coming 2 turns away. Options:
  - Reinforce C3 now (waste stones?)
  - Retreat from C3 (abandon territory?)
  - Counter-attack elsewhere (ignore threat?)
  - Send intercepting force (try to stop in-transit?)

**Key Difference:**
- P1's commitment is visible 2 turns early
- P2 must predict if P1 will actually commit or change plan
- True fog of war: not from hidden board, but from hidden intentions

**Turn 5 - Attack Resolves:**
- P1's stones finally arrive at C3
- By then, P2 may have abandoned it, reinforced massively, or counter-attacked
- Different from base game's immediate resolution

**Key Learning:** Planning and deception. Feinting becomes real because your opponent must predict your next move before seeing it.

---

## Variant C: ART OF WAR - Scenario

### Setup Notes

**Terrain:**
- Center (C3): ELEVATED (+1 strength to combatants)
- Edges (A1-E1, A5-E5, A1-A5, E1-E5): FORTIFIED (defenders +1 roll)
- Corridors (A3, B3, C3, D3, E3): KEY POINTS (extra value)

### Turn 5 - Terrain Advantage

**Scenario:** P1 has built up at B3 (key point) with 5 stones. Wants to assault C3 (elevated, center).
P2 has 3 stones at C3.

**Attack Options:**

**Option A: Direct Assault**
- Send 5 stones to C3 from B3 (adjacent)
- Combat: P1 (5 stones) vs P2 (3 stones at elevated position)
- Terrain bonus: P2 gets +1 from elevation
- Effective combat: P1 (5) vs P2 (4 effectively)
- Still favors P1, but elevation makes a real difference

**Option B: Strategic Retreat (New!)**
- P1 reconsiders. If they lose heavily, they can retreat, saving 50% of surviving stones
- Instead of all-or-nothing, can try gradual pressure
- P2 faces choice: hold and fight, or retreat and regroup

**Outcome with Retreat Option:**
- P1 Attacks with 5 stones
- Combat: P1 loses 3, P2 loses 2
- P2 survives with 1 stone at C3 but P1 has 2 arriving
- P2 Chooses RETREAT: keep 1 stone, P1 takes territory but with 2 stones

**Key Difference:** Battle outcome isn't purely determined by math. Tactical retreat allows P2 to live to fight another day.

### Turn 6 - Deception in Play

**Scenario:** P1 has expanded to control: B3, C3, C2, C4 (forming a + shape)

**Turn 6 Deception:**
- P2 wants to deceive P1 about intended growth
- P2 marks two false territories as "growing" (shows growth markers)
  - Actually: D3 (corridor), D4 (real territory)
  - False: E3 (corridor), E5 (edge)
- P1 sees growth at D3, D4, E3, E5
- P1 prepares defense at edge and corridor

**Turn 7 Reveal:**
- P2 reveals E3 and E5 were false decoys
- P1 has wasted resources preparing unnecessary defense
- P2 actually focused on controlling D3 and D4

**Key Learning:**
- Information becomes weapon
- Not about hidden board, but about hidden intentions
- Creates reading game (can I tell if opponent is faking?)

### Turn 8 - Multiple Victory Conditions

**Board State (Turn 8 of 20):**
- P1 Controls: 8 territories (majority control)
- P2 Controls: 6 territories
- But P2 has 12 total stones, P1 has 10

**Victory Types Possible:**

1. **Territory Victory (Default):** Control most territories at end of 20 turns
   - P1 ahead currently

2. **Attrition Victory:** Reduce opponent to 0 territories
   - Possible, but P2 is too strong

3. **Positioning Victory:** Control all terrain advantage squares + 50% board for 3 consecutive turns
   - Terrain advantages: C3 (P1), corners (P2 has 2), edges (mixed)
   - P2 could pursue this by controlling key points

4. **Strategic Withdrawal Victory:** Force opponent to retreat 5+ times, then control 60% board
   - P2 has already forced 2 retreats, needs 3 more then dominate
   - Alternative path if attrition seems impossible

**Key Difference:**
- Players can pursue different victory types
- Same game, multiple valid strategies
- Encourages diverse playstyles

---

## Variant D: ATTENTION/INCEPTION - Scenario

### Setup Notes

Territories are "ideas" on spectrum: Neutral → Established Thought

### Turn 1

**Setup:** P1 and P2 place seeds (1 stone each) at 3 positions.

**Turn 1 Actions:**
- P1: Places at A1 (idea seed)
- P1: Places at A2 (idea seed)
- P1: Places at B1 (idea seed)
- P2: Places at E4, E5, D4 (idea seeds)

**Key Difference:** Stones are "seeds" of ideas, not occupying troops.

### Turn 2

**Turn 2 Actions:**
- P1: Grow at A1 (+1 attention)
- P1: Spread attention to B1 (associating A1 and B1 ideas)
- P1: Grow at A2

- P2: Grow at E4
- P2: Grow at D4
- P2: Move to D3 (spreading idea seed downward)

**After Turn 2:**
- A1: 2 stones (P1 established idea)
- A2: 2 stones (P1 established idea)
- B1: 1 stone (P1 seed)
- A1 ↔ B1: ASSOCIATED (now cascading)

### Turn 3 - Cascade Effect

**Automatic Cascade:**
- A1 and B1 are adjacent and both P1's
- B1 gets +1 cascade growth (automatic, no action needed)
- B1 now has 2 stones

- A2 is adjacent to A1, but not A1's controlled status, so no cascade yet

**Turn 3 Actions:**
- P1: Grow at A1 (+1)
- P1: Associate A1 with A2 (spread idea from A1 to A2)
- P1: Grow at B1 (now 2→3, approaching established threshold)

- P2: Plant at C4 (expansion attempt with 3 stones)
  - Requires commitment: next turn will establish or fail

**After Turn 3:**
- A1: 3 stones (fully established, associated with B1)
- B1: 3 stones (fully established)
- A2: 1 stone + association pending
- Network forming: A1-B1 connected (cascade active)

### Turn 4 - Cluster and Planting

**Turn 4 Actions:**
- P1: Grow at A2
- P1: Plant at B2 (expand with 3 stones to establish new idea)
  - First turn of planting: B2 now has 1 P1 stone (seed established)

- P2: Complete plant at C4 (now has 3 stones, idea established)
- P2: Plant at C3 (new expansion, 2 stones, risky)
  - C3 expansion: 50% failure chance (with 2 stones)

**Cascade Updates:**
- B1 ↔ A1 (still cascading)
- Now consider: B1 ↔ B2 potential?
  - After successful plant, can't cascade yet (only 1 seed)
  - Next turn: if B2 grows, B1↔B2 cascade activates

### Turn 5 - Viral Moment

**Cascades Activate:**
- A1 (3) ↔ B1 (3): B1 grows +1 from cascade
- B1 (4) ↔ B2 (1): B2 grows +1 from cascade
- A1 (3) ↔ A2: A2 grows +1 from association

**Turn 5 Actions:**
- P1: Grow at A1, B1, B2, A2 (spreads cascade to multiple ideas)
  - Multiple growth actions activate multiple cascades

**After Turn 5 Cascade Resolution:**
- A1: 4 stones
- A2: 3 stones
- B1: 5 stones (grown from cascade)
- B2: 3 stones (grown from cascade)

**Key Moment:** P1 created chain reaction through strategic association. This is the "Inception" moment—planted seeds that grew and spread by themselves through network effect.

### Turn 6 - Persuasion Combat

**Scenario:** P2's idea at C4 is adjacent to P1's B4 (neutral).

**Situation:**
- P1 has cascading network: A1-B1-B2-A2
- P2 has isolated ideas: C4, C3
- P1 tries to persuade C4 to their side

**Persuasion (Not Combat!):**
- P1 sends 2 stones to C4 from B4
- P2 has 3 stones at C4
- Persuasion: P1 (2 stones) vs P2 (3 stones)

**Combat Mechanics:**
- Roll as normal: each stone 50% chance to be convinced/convinced others
- But outcome: not elimination, but conversion
- P1 wins: 1 P2 stone converts to P1, P1 takes partial control
- P2 wins: P1 stones can retreat, keep some (strategic withdrawal)
- Mutual: Some stones from both sides remain, territory contested

**Outcome:** P1 wins 2/3 rolls, gets 2 converted + survives
- C4 now has mixed: 2 P1 + 1 P2
- Territory goes to P1 (majority)

**Key Difference:** No destruction in ideas—persuasion. You're converting minds, not eliminating armies.

### Turn 8+ - Cascade Victory

**Winning Condition:** Cluster Victory
- P1 controls connected cluster: A1-A2-B1-B2-C1-C2
- 3+ connected territories with 3+ stones each
- All cascading together into powerful network

**Alternative Cascade Defeat:**
- If P2 breaks one link (persuades one territory)
- Entire cascade stops
- P1's network splits, loses cascade bonus

**Key Learning:** Network architecture matters. Control the connectors, break the system.

---

## Variant E: MOMENTUM - Scenario

### Turn 1-2: Building Momentum

**Turn 1:**
- P1: Send 2 stones NORTH from A2 to A3 (committing to northward direction)
- Previous direction for A2 stones: None (fresh)
- Now: Momentum 1 (moved north once)

**Turn 2:**
- P1: Send same 2 stones NORTH again from A3 to A4
- Previous direction: North
- Current direction: North (same!)
- Momentum: Now 2 (moved north twice)
- Combat bonus: +1 strength when attacking (at momentum 2)

**Turn 3:**
- P1: Send stones NORTH again from A4 to A5 (expansion)
- Previous direction: North
- Current direction: North (same!)
- Momentum: Now 3 (max momentum)
- Expansion attempt: 2 stones vs 50% success
  - With momentum 3: Effective +1 to roll (easier expansion)
  - Resolve: Success! A5 now P1's

**Key Difference:** P1's consistent northward advance built momentum that made expansion easier.

### Turn 4 - Momentum Loss

**P2 Sees Threat:** P1 is advancing northward with 3 momentum

**P2 Counterattack from E2:**
- Send 3 stones WEST to D2 (toward the advancing P1)
- Encounters P1's advanced stones at A5 after P1 retreats

**P1's Turn 4 Decision:**
- Option A: Continue NORTH to A5 (keep momentum, extend attack)
  - Direction: North (again)
  - Momentum: Still 3
  - But: Takes casualty from P2's earlier countermove

- Option B: Retreat SOUTH from A4 to A3 (regroup, consolidate)
  - Direction: South (different from North)
  - Momentum: RESETS to 1 (changing direction costs momentum)
  - But: Save stones, regroup, change strategy

**P1 Chooses Option B - Retreat to Consolidate**
- Sends stones SOUTH from A4 to A3
- Direction changes: SOUTH (was North)
- Momentum resets: Momentum 0 (or 1 for new direction)
- Trade: Lost momentum advantage, but saved forces

**Turn 5 - New Momentum Direction**

**P1 Pivots:**
- Sends stones EAST from A3 to B3
- New direction: East
- Momentum: 1 (building in new direction)
- Strategy: Changed from northward pressure to eastward expansion

**Key Learning:**
- Momentum rewards persistence
- But changing strategy costs momentum
- Forces decision: commit deep or adapt to enemy pressure?

### Turn 6 - Momentum Chain Reaction

**P1 Continues EAST:**
- B3 to C3 (East, 2nd momentum)
- C3 to D3 (East, 3rd momentum)
- D3 (into enemy area) = expansion with momentum +1 bonus
- Succeeds! P1 has advanced eastward with 3 momentum

**P1 Now Controls Connected Territories:**
- A3 (retreat point)
- B3, C3, D3 (advancing eastward)
- Momentum: 3 (peak)

**P2 Realizes Threat:**
- P1 is creating northward-then-eastward corridor
- Chain of 4 connected territories
- With momentum +3 bonus, P1 is very strong

**Key Moment:** P1's momentum created visible, unstoppable advance. This is satisfying—player commitment paid off.

---

## Design Lesson: Variant Moments

Each variant creates different **memorable moments**:

| Variant | Memorable Moment |
|---------|-----------------|
| **Tower Defense** | Breaking through top level after 3-turn siege |
| **Time & Distance** | Executing feint perfectly; opponent wasted resources |
| **Art of War** | Forcing enemy retreat; gaining terrain advantage |
| **Inception** | Cascade activation: network self-reinforces |
| **Momentum** | Chain victories building unstoppable advance |
| **Base Game** | Successful expansion with 2 stones (lucky break) |

Each teaches different lesson through play.

---

## Summary

These examples show:

1. **Tower Defense**: Multi-step territorial conquest; siege mentality
2. **Time & Distance**: Planning and deception through commitment
3. **Art of War**: Strategic diversity; terrain and retreat matter
4. **Inception**: Network effects; viral cascades; persuasion not destruction
5. **Momentum**: Persistence rewards; directional commitment

All variants preserve individual stone agency and simultaneous action—core strengths of the base game—while adding new decision points and strategic dimensions.
