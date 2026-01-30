# Strategic Influence - Game Manual

## Overview
Strategic Influence is a turn-based territorial strategy game for two players on a 5x5 grid. Players compete to control the most territory by growing their forces and conquering enemy positions. The player controlling the most territories after 20 turns wins.

## Setup
1. The board starts empty
2. Each player places **3 stones** in their starting zone:
   - **Player 1 (White)**: Columns A-B, plus rows 1-2 of column C
   - **Player 2 (Black)**: Columns D-E, plus rows 4-5 of column C
   - The center spot (C3) cannot be chosen by either player
3. After both players place, the game begins

## Turn Structure
Each turn, players **simultaneously** choose actions for each territory they control. Then actions resolve.

### For each territory you control, choose:
- **GROW**: Stay in place and gain +1 stone
- **MOVE**: Send some or all stones to adjacent positions

### Key mechanic: Individual stone direction
You control **each stone individually**. If you have 3 stones at a position, you can:
- Send all 3 in the same direction
- Send 2 one way and 1 another way
- Send 1 in three different directions
- Keep some to GROW while others move

**If any stones stay (don't move), that territory GROWs (+1 stone).**

## Movement
- Stones can move to **orthogonally adjacent** positions (up, down, left, right)
- Moving to a **friendly** position reinforces it (adds stones) - always succeeds
- Moving to a **neutral** position triggers **expansion** (risky!)
- Moving to an **enemy** position triggers **combat**

## Expansion (into neutral territory)
Expanding into unclaimed territory is **not guaranteed**. Each stone has a 50% chance to succeed:

- If **ANY stone succeeds**: All stones claim the territory
- If **ALL stones fail**: All stones are **lost**

This creates risk/reward:
- 1 stone: 50% success, 50% lose the stone
- 2 stones: 75% success, 25% lose both
- 3 stones: 87.5% success, 12.5% lose all
- 4+ stones: Very safe (93%+)

**Committing more stones to expansion is safer.** Spreading thin (1 stone each) is risky.

## Combat (attacking enemy territory)
When your stones attack an enemy territory:

1. **Defender rolls first** (50% chance to eliminate 1 attacker)
2. **Attacker rolls** (50% chance to eliminate 1 defender)
3. **Alternate** until one side is eliminated
4. Eliminated stones don't roll

### Combat outcomes:
- **Attacker wins**: Surviving attackers claim the territory
- **Defender holds**: Surviving defenders keep the territory
- **Mutual destruction**: Both eliminated; territory becomes neutral

## Growth
After movement resolves, territories that chose GROW (or had stones stay) gain **+1 stone**.

## Winning
After **20 turns**, the player controlling the most territories wins.

Territory count determines the winner (not stone count).

Ties result in a draw.

## Controls (Visualizer)

### Setup Phase
- Click a position in your starting column to place your initial stone

### Planning Phase
- **Click** your stone to select it
- **Click adjacent spot** to send 1 stone there (repeat to send more)
- **Right-click** to undo last move from selected stone
- **Space/Enter** to execute the turn
- **Escape** to reset all pending moves

## Strategy Tips

1. **Commit to expansion**: Sending 1 stone is a coin flip; send 2-3 for safer expansion
2. **Grow before expanding**: Build up stones, then expand with force
3. **Reinforce is safe**: Moving to your own territory always works
4. **Stack for attacks**: Higher stone counts improve combat odds
5. **Defend the center**: Central positions threaten more of the board
6. **Watch the clock**: 20 turns gives time to build, but don't wait too long
