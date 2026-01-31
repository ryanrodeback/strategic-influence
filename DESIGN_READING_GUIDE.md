# Game Design Exploration - Reading Guide

## Document Overview

### Main Document: GAME_DESIGN_EXPLORATION.md
**Length:** ~15 KB | **Reading Time:** 20-30 minutes

Contains complete analysis of 8 game concepts built around principles of elegant simplicity:

**Primary Explorations:**
1. **Attention + Influence** (Grid) - Place stones, probabilistic area claiming
2. **A+I Rolling Score** - Cumulative scoring variation
3. **A+I Hex Variation** - Triangular regions, 33% per corner
4. **Place or Attack** (Grid) - Place OR attack, 50% per adjacent
5. **P/A Triangular Grid** - 3-neighbor maximum variation

**Additional Concepts:**
6. **Watershed** - Voronoi proximity control (deterministic)
7. **Creep** - 3 seeds, automatic spreading
8. **Fault Lines** - Group survival probability

---

## Quick Reference

### If You Want Pure Elegance
**Read:** Watershed section
- One rule determines everything
- Fully deterministic
- Closest to Go's aesthetic

### If You Want Rich Strategic Depth
**Read:** Attention + Influence (Hex) section
- Beautiful 33% per corner math
- Gradient control creates nuance
- Recommended overall design

### If You Want Simple Implementation
**Read:** Place or Attack section
- "One action, two choices"
- Straightforward rules
- Strong AI tractability

### If You Want Interesting Risk/Reward
**Read:** Fault Lines section
- Connection tactics
- Probability only at resolution
- Deep human decisions

---

## Ratings Summary

| Game | Elegance | Depth | AI |
|------|----------|-------|-----|
| A+I Grid | 7/10 | 8/10 | 7/10 |
| A+I Rolling | 7/10 | 8/10 | 7/10 |
| **A+I Hex** | **9/10** | **9/10** | **8/10** |
| P/A Grid | 8/10 | 7/10 | 9/10 |
| P/A Triangular | 8/10 | 8/10 | 6/10 |
| **Watershed** | **9/10** | 7/10 | **10/10** |
| Creep | 8/10 | 6/10 | 10/10 |
| **Fault Lines** | 8/10 | **8/10** | 9/10 |

**Top Recommendations:** A+I Hex, Watershed, Fault Lines

---

## Design Philosophy

All games follow these principles:
1. One stone per place maximum
2. One primary decision per turn
3. Simple win conditions
4. Probability at resolution moments (not chaos throughout)
5. AI tractability (minimax/expectimax friendly)
6. Emergent depth from simple rules

---

## Detailed Documents

For in-depth analysis of specific games, see the docs/ folder:
- `docs/ROLLING_SCORE_VARIANT.md` - Full rolling score analysis
- `docs/game-concepts/place-or-attack-design.md` - Full Place or Attack analysis
- `HEX_VARIATION_DESIGN.md` - Full hex geometry analysis
- `TRIANGULAR_GRID_CONCEPT.md` - Full triangular grid analysis
- `NEW_GAME_DESIGNS.md` - Watershed, Creep, and Fault Lines details

---

## Next Steps

1. **Choose a game** to prototype based on your priorities
2. **Implement basic version** - most take 1-2 days
3. **Playtest** against simple AI or human opponent
4. **Iterate** based on feel and balance

Start with the main document (GAME_DESIGN_EXPLORATION.md) for the complete picture.
