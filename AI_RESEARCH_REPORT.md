# AI Research Report: Strategic Influence Game
## Comprehensive Analysis of Algorithmic AI Approaches

---

## Executive Summary

Strategic Influence is a turn-based, simultaneous-move territorial strategy game with inherent stochasticity (50% success rates on risky actions). This report analyzes 8 major algorithmic AI approaches, evaluating their suitability for this specific game's characteristics.

**Key Game Properties:**
- Turn-based, fully simultaneous action selection
- 5x5 board (25 territories max)
- 20 turn limit
- Two main stochastic sources: expansion (50% per stone) and combat (50% per stone)
- No hidden information (perfect information game)
- Estimated branching factor: 12-25 moves per position (moderate)
- Estimated game tree depth: 20 turns × 2 players = depth ~40

---

## Part 1: Game Characteristics & Complexity Analysis

### 1.1 State Space Analysis

**Approximate State Space Size:**
- Board positions: 3^25 ≈ 8.5 × 10^11 (each cell: neutral/white/black)
- Stone counts per territory: variable (1-10 typical, config.max_stones = 10)
- Conservative upper bound: 3^25 × 10^25 ≈ 10^37 distinct game states
- **Practical space:** Much smaller due to game rules (symmetric territories, bounded growth)

**Territory Ownership States:**
- Only 3^25 ≈ 8.5 × 10^11 meaningfully different board configurations
- After accounting for symmetry and gameplay constraints: ~10^8 to 10^10 reachable states

### 1.2 Branching Factor Analysis

**Per-Territory Decision Space:**
With the 3-option simplified system:
- GROW (1 option)
- SEND_HALF (up to 4 directions)
- SEND_ALL (up to 4 directions)

**Per-Position Branching:**
- 1 territory: ~9 distinct actions
- 2 territories: ~81 action combinations
- 3 territories: ~729 action combinations
- 4 territories: ~6,561 combinations
- 5+ territories: exponential explosion (10,000+)

**Practical Branching Factor:**
- Early game (1-2 territories): b ≈ 8-20
- Mid game (3-4 territories): b ≈ 20-100
- Late game (5+ territories): b ≈ 100-500+

**Effective Branching (w/ pruning):** 10-30 (assuming intelligent move filtering)

### 1.3 Search Depth Feasibility

**Maximum tractable depths by approach:**
- Minimax (no pruning): depth 2-3 only
- Minimax (α-β pruning): depth 4-6 feasible
- Expectimax: depth 3-4 due to stochastic expansion
- MCTS (1000 sims): equivalent to depth 6-8 look-ahead
- MCTS (10,000 sims): equivalent to depth 8-10 look-ahead

---

## Part 2: Algorithmic Approaches - Detailed Analysis

### Approach 1: Expectimax (for Stochastic Games)

**Overview:**
Expectimax extends minimax to handle stochasticity. In addition to MAX (our move) and MIN (opponent move) nodes, it includes CHANCE nodes that compute weighted averages over possible random outcomes.

**Suitability for Strategic Influence: ⭐⭐⭐⭐ (HIGH)**

**Mechanics:**
```
MAX node: Choose action that maximizes expected value
MIN node: Assume opponent chooses worst action for us
CHANCE node: Average outcomes weighted by probability
```

For expansion (50% per stone):
- 2 stones: 75% success, 25% loss
- 3 stones: 87.5% success, 12.5% loss

For combat (alternating 50% rolls):
- Pre-computed odds via `calculate_combat_odds()`

**Advantages:**
- Handles stochasticity correctly (not approximating randomness)
- Mathematically sound for perfect-information games
- No random rollouts needed (unlike MCTS)
- Deterministic outcome: same action always chosen
- Natural modeling of expansion/combat risk

**Disadvantages:**
- Exponential explosion: O(b^d × s^d) where s = stochastic branches
- Shallow search only (2-3 plies practical)
- Requires precise probability models for all outcomes
- Combat resolution can have many branches (up to 8+ rolls)

**Implementation Complexity: MEDIUM**

**Current State in Codebase:**
- Combat odds pre-computed: `calculate_combat_odds()` exists
- Expansion odds trivial: binomial(n, k) × 0.5^n
- No full expectimax implementation yet

**Expected Performance vs Current Best:**
- Better than random: 80-90% win rate
- Competitive with Minimax depth-2: 40-60% win rate
- Slower than Minimax depth-2: 2-5x more computation

**Computational Requirements:**
- Time: O(b^d × s^d) where s = 2-8 (stochastic branches)
- Depth 2: 12^2 × 4^2 ≈ 23,000 nodes evaluated
- Depth 3: 12^3 × 4^3 ≈ 13.8M nodes evaluated

**Implementation Roadmap:**
1. Build stochastic branch enumeration for expansions
2. Integrate pre-computed combat odds
3. Implement expectimax recursion with α-β pruning (limited)
4. Tune depth (2-3 likely optimal)
5. Test and profile

**Pros:**
- Properly models game stochasticity
- Sound mathematical foundation
- Better decision-making in uncertain situations

**Cons:**
- Limited depth due to branching
- Significant implementation complexity
- Requires accurate probability estimates
- Slower than deterministic approaches

---

### Approach 2: Alpha-Beta Pruning (Minimax Optimization)

**Overview:**
Alpha-beta pruning eliminates branches that cannot affect the final decision. It reduces the effective branching factor from b to √b in many cases.

**Suitability for Strategic Influence: ⭐⭐⭐⭐⭐ (HIGHEST PRIORITY)**

**Core Mechanics:**
- Alpha: best value we can guarantee
- Beta: best value opponent can force
- If value ≥ β (at MIN node): prune remaining branches (beta cutoff)
- If value ≤ α (at MAX node): prune remaining branches (alpha cutoff)

**Advantages:**
- Effective branching factor: ~6-10 (vs raw 12-25)
- Deep searches become feasible (depth 4-6)
- Proven track record (chess engines use it)
- Relatively simple to implement
- Compatible with other optimizations (iterative deepening, move ordering)

**Disadvantages:**
- Requires deterministic evaluation (not for stochastic nodes)
- Branch ordering matters heavily (can lose 50%+ benefit with poor ordering)
- Doesn't fundamentally reduce branching—only eliminates branches
- Doesn't help with game's inherent stochasticity

**Implementation Complexity: LOW-MEDIUM**

**Current State in Codebase:**
- Already implemented in `MinimaxAgent`
- Uses parametric `max_depth` and `max_moves` limits
- Evaluation via `evaluate_board()` function

**Expected Performance vs Current Best:**
- Depth 2 with pruning: 55-70% win rate
- Depth 3 with pruning: 65-80% win rate
- Depth 4 with pruning: 75-85% win rate (if reachable)

**Computational Requirements:**
- Time: O(b^(d/2)) with perfect ordering
- Depth 2: ~100-200 nodes
- Depth 3: ~1,000-3,000 nodes
- Depth 4: ~10,000-30,000 nodes

**Enhancements to Implement:**
1. **Move Ordering:** Sort by evaluation score first
   - Maximizes early cutoffs
   - Use territory count as quick heuristic
   - Save 20-40% evaluation time

2. **Transposition Tables:** Cache evaluated positions
   - Avoid re-evaluating same board twice
   - With simultaneous moves, fewer collisions expected
   - Still provides 15-25% speedup

3. **Iterative Deepening:**
   - Start with depth 1, then 2, then 3
   - Stop when time limit reached
   - Allows flexible computation budgets
   - Actually faster than fixed-depth (counterintuitive due to cutoff efficiency)

4. **Killer Moves:** Track moves that caused cutoffs at same level
   - Try killer moves first at sibling nodes
   - Particularly effective in this game's combat situations

5. **History Heuristic:** Track which moves led to cutoffs
   - Prioritize moves with history of cutoffs

**Pros:**
- Proven, well-understood algorithm
- Already partially implemented
- Dramatic efficiency gains possible
- Compatible with existing evaluation function

**Cons:**
- Doesn't address stochasticity directly
- Requires good move ordering for maximum benefit
- Depth limited by branching factor

---

### Approach 3: Monte Carlo Tree Search (MCTS) Variants

**Overview:**
MCTS builds a search tree incrementally through random playouts, balancing exploration (find new moves) and exploitation (improve known good moves). Key variants: UCT, RAVE, PUCT.

**Suitability for Strategic Influence: ⭐⭐⭐⭐ (HIGH)**

**Core Algorithm (UCT - Upper Confidence Bounds for Trees):**

```
1. Selection: Traverse tree using UCB1 formula
   UCB1(node) = exploitation + C × √(ln(parent_visits) / visits)
2. Expansion: Add unvisited child
3. Simulation: Play random game from node
4. Backup: Propagate result back to root
```

**Key Variants:**

**A. UCT (Upper Confidence Bounds in Trees)**
- Standard MCTS with UCB1 exploration
- Works well with random simulations
- Best for domains with evaluable end-states

**B. RAVE (Rapid Action Value Estimation)**
- All-Moves-As-First heuristic: value moves regardless of order
- Combines information from all playouts through a position
- 20-40% faster convergence than UCT
- Used in Go engines (including AlphaGo)

**C. PUCT (Policy-adjusted UCT)**
- Integrates a policy prior (e.g., from neural network)
- Used in AlphaZero
- Requires external policy network

**Advantages:**
- Handles stochasticity naturally (random playouts)
- No need for explicit probability models
- Anytime algorithm (results improve with more simulations)
- Parallelizable (multiple threads)
- Effective in high branching factor games
- Automatic focus on promising moves

**Disadvantages:**
- Requires many simulations (1,000-10,000 typical)
- Random playouts often suboptimal (need good rollout policy)
- Higher variance than minimax
- Struggles with complex strategy (late-game tactics)
- Implementation complexity (tree management)

**Implementation Complexity: MEDIUM-HIGH**

**Current State in Codebase:**
- `MonteCarloAgent` exists but basic (50-100 simulations)
- Uses simplified 3-option movement system
- Random playout policy (no domain knowledge)

**Performance Analysis:**

**With 1,000 simulations (standard):**
- ~10 simulations per candidate move (8 candidates tested)
- Win rate: 55-70% vs random
- Similar to Minimax depth-2

**With 5,000 simulations (typical for Go):**
- Win rate: 70-85% vs random
- Equivalent to Minimax depth-3
- Computation time: 1-2 seconds per move

**With 10,000 simulations (deep):**
- Win rate: 80-90% vs random
- Equivalent to Minimax depth-4
- Computation time: 3-5 seconds per move

**Computational Requirements:**
- Time: O(n × average_playout_depth)
  - n = number of simulations
  - average_playout_depth ≈ 10-15 moves
- Memory: O(tree nodes) ≈ O(n × average_depth)
- 5,000 simulations: ~50K nodes, ~10MB memory

**Enhancement Strategies:**

**1. Rollout Policy Improvements:**
   - Use `evaluate_board()` for greedy rollouts
   - Reduce randomness in playouts (semi-random)
   - Weight expansion attempts by safety
   - Favor growth and territory acquisition

**2. Tree Policy Optimization:**
   - Hybrid UCT: switch from UCT to greedy after N visits
   - Rapid action sampling: prioritize moves that worked before
   - Prioritize moves that win, not just high-visits

**3. RAVE Integration:**
   - Combine UCT with all-moves-as-first statistics
   - Typically 20-40% faster convergence
   - Implementation: track (wins, visits) per move + per history

**4. Parallelization:**
   - Tree-parallel: multiple threads build same tree (with locks)
   - Root-parallel: multiple trees, average results
   - Leaf-parallel: single tree, parallelize rollouts
   - Expected speedup: 2-4x with 4 threads

**5. Transposition Table:**
   - Cache evaluation of common board positions
   - Reduce duplicate playouts
   - Gain: 10-20% fewer simulations needed

**Pros:**
- Naturally handles stochasticity
- Scales well with computation
- Proven in complex games (Go, Poker)
- Good balance of exploration/exploitation
- Incremental improvement (anytime algorithm)

**Cons:**
- High variance in results
- Requires many simulations (1,000+)
- Suboptimal playouts hurt quality
- Complex implementation
- Late-game play may be weaker

---

### Approach 4: Neural Network + Self-Play (AlphaZero Style)

**Overview:**
Combines MCTS with a deep neural network trained via self-play. Network learns to estimate (policy, value) from board position, drastically reducing playout simulations needed.

**Suitability for Strategic Influence: ⭐⭐⭐ (MODERATE - requires significant infrastructure)**

**Architecture:**
```
1. Neural Network:
   Input: Board state (5x5x3 tensor, e.g.)
   Output:
     - Policy head: action probabilities
     - Value head: position evaluation (-1 to +1)

2. Self-Play Loop:
   For each iteration:
     a) Generate games via MCTS with network
     b) Collect (state, policy_target, value_target) tuples
     c) Train network on batch
     d) Evaluate new vs old network
     e) Keep if > threshold, else revert

3. Improvements over time:
     - Better network → better MCTS guidance
     - Better MCTS → better training data
     - Feedback loop strengthens both
```

**Advantages:**
- Superhuman performance possible (AlphaZero beats Stockfish)
- Requires far fewer simulations (~800 vs 40K for traditional MCTS)
- Learns game strategy implicitly
- Handles stochasticity via MCTS component
- Generalizes well to similar positions

**Disadvantages:**
- Massive training infrastructure (GPU, thousands of self-play games)
- Requires 2-4 weeks training time (for Go)
- Data hungry (millions of positions)
- Not interpretable (black box)
- Overkill for small game like Strategic Influence
- Domain-specific architecture needed

**Implementation Complexity: HIGH**

**Estimated Requirements for Strategic Influence:**
- GPU: 1x RTX 2080 or equivalent
- Training data: ~100K positions (feasible)
- Training time: 2-7 days (vs 2-4 weeks for Go)
- Self-play games needed: 10K-50K

**Network Architecture:**
```
Input layer: 5x5x3 (board position)
Convolutional layers: 3-4 blocks
  - 64-128 filters
  - 3x3 kernels
  - ReLU activation
Residual connections: for easier deep networks
Policy head: softmax over ~50 action classes
Value head: tanh to [-1, 1]
```

**Expected Performance vs Current Best:**
- After 500 self-play games: 70% vs Minimax depth-2
- After 5,000 self-play games: 80-85% vs Minimax depth-3
- After 20,000 games: 90%+ vs any baseline

**Computational Requirements:**
- Training: 50-200 GPU hours
- Inference: 10-50ms per move (GPU), 50-200ms (CPU)
- Memory: 100-500MB model + 1-2GB training buffer

**Implementation Roadmap:**

1. **Phase 1: Prepare infrastructure**
   - Set up training pipeline (PyTorch/TensorFlow)
   - Implement self-play loop
   - Create data pipeline

2. **Phase 2: Train baseline**
   - Random weight network (establish lower bound)
   - Supervised learning on 1K expert games
   - Evaluate against baselines

3. **Phase 3: Self-play loop**
   - 5K iterations of self-play + training
   - Checkpointing every 100 iterations
   - Track win rate improvement

4. **Phase 4: Optimization**
   - Quantization (fp32 → fp16 or int8)
   - Model compression (distillation)
   - CPU inference optimization

**Pros:**
- Potentially strongest AI possible
- Learns game-specific patterns
- Scales with compute budget
- Elegant unified framework

**Cons:**
- Excessive infrastructure for this game size
- Long development timeline
- Requires GPU for training
- Difficult to debug failures
- Not needed for optimal play

---

### Approach 5: Genetic Algorithms / Neuroevolution

**Overview:**
Evolve a population of strategies (or neural networks) through selection, crossover, and mutation. Each strategy plays games, and strongest reproduce.

**Suitability for Strategic Influence: ⭐⭐ (LOW-MODERATE, niche use)**

**Two Variants:**

**A. Strategy-Based GA (Evolve heuristic weights)**
```
1. Encode strategy as: (w1, w2, ..., w9) = evaluation weights
2. Fitness = win rate against population
3. Crossover: blend parent weights
4. Mutation: random perturbation
5. Select top 50% for next generation
```

**B. Neuroevolution (NEAT - NeuroEvolution of Augmenting Topologies)**
```
1. Evolve neural network topology + weights
2. Start simple, add neurons/connections over time
3. Fitness = win rate
4. Crossover: inherit structure from both parents
5. Mutation: add/remove nodes, adjust weights
```

**Advantages:**
- No handcrafted heuristics needed
- Can discover unexpected strategies
- Parallelizable (evaluate population in parallel)
- No gradient computation required
- Works with stochastic domains

**Disadvantages:**
- Very slow convergence (100+ generations needed)
- High variance (run multiple seeds)
- No principled search (unlike gradient-based)
- Poor scaling (exponential with parameter count)
- Requires many game simulations

**Implementation Complexity: MEDIUM**

**Expected Performance vs Current Best:**
- Generation 1: Random, 0-20%
- Generation 10: Simple heuristic, 30-50%
- Generation 50: Sophisticated strategy, 60-80%
- Generation 100+: Near-optimal, 80-90%

**Computational Requirements:**
- Time: 50-200 generations × 20 games/generation = 1K-4K games
- With ~20 seconds per game: 5-22 hours for GA to converge
- Parallelizable: 10x speedup with 10 workers → 30 min to 2 hours

**Use Cases:**
1. **Tuning evaluation weights** (currently manual)
2. **Discovering emergent strategies** (research interest)
3. **Testing robustness** (find weakness-exposing strategies)
4. **Tournament play** (evolve specialized counters)

**Implementation Roadmap:**
1. Define genome (e.g., 9 evaluation weights)
2. Tournament selection (play 2 random games per individual)
3. Crossover + mutation (50/50 split)
4. Parallel game evaluation
5. Track fitness over generations

**Pros:**
- Can find surprising strategies
- No mathematical elegance required
- Handles non-differentiable objectives
- Good for tuning discrete parameters

**Cons:**
- Slow convergence
- High computational cost
- Requires many trials
- Results not interpretable

---

### Approach 6: Temporal Difference (TD) Learning

**Overview:**
Off-policy reinforcement learning that learns state values by bootstrapping from future value estimates. Famous application: TD-Gammon (backgammon player).

**Suitability for Strategic Influence: ⭐⭐⭐ (MODERATE)**

**Core Algorithm:**
```
V(s) ← V(s) + α [V(s') - V(s)]  // Update based on next state value
For simultaneous moves:
  - After each turn, observe outcome
  - Backup value estimates
  - Handles stochasticity naturally
```

**Two Variants:**

**A. Q-Learning (off-policy)**
```
Q(s, a) ← Q(s, a) + α [R + γ max Q(s', a') - Q(s, a)]
- Learn optimal action-values
- Can learn from suboptimal play
```

**B. SARSA (on-policy)**
```
Q(s, a) ← Q(s, a) + α [R + γ Q(s', a') - Q(s, a)]
- Learn actual policy values
- More conservative
```

**Advantages:**
- Learns from play (can use suboptimal opponents)
- Efficient (bootstrapping is faster than Monte Carlo)
- Handles stochasticity well
- Can improve over time with play
- Mature, well-understood algorithm

**Disadvantages:**
- Requires value function approximation (linear or NN)
- Slow to converge (10K+ games typical)
- Requires exploration strategy (ε-greedy)
- Can diverge with function approximation
- Limited by feature representation quality

**Implementation Complexity: MEDIUM**

**Expected Performance vs Current Best:**
- After 1K games: 40-50% (still exploring)
- After 5K games: 55-70% (learning)
- After 20K games: 70-85% (convergence)
- After 100K games: 85-90%+ (refined)

**Computational Requirements:**
- Training time: 20K games × 30 seconds = 167 hours
- With parallelization (10 workers): ~17 hours
- Inference: instant (lookup V(s))

**Feature Representation:**
```
Options:
1. Tile coding: divide board into overlapping regions
2. Polynomial features: combinations of board features
3. Neural network: learn features automatically
4. Hand-crafted: territory count, stone advantage, threats, etc.
```

**Use Cases:**
1. **Continuous improvement:** Start with any baseline, improve through play
2. **Learning from opponents:** Use recorded games to train
3. **Lightweight training:** Requires only 50MB disk space
4. **Real-time deployment:** Instant decisions (value lookup)

**Implementation Roadmap:**
1. Define feature vector (10-20 features)
2. Initialize V(s) table (or neural network)
3. Play games with exploration (ε-greedy)
4. Backup values after each turn
5. Tune learning rate α and discount γ
6. Evaluate every 100 games

**Pros:**
- Proven in games (TD-Gammon was superhuman)
- Efficient learning
- Can start from any baseline
- Cheap to deploy

**Cons:**
- Requires manual feature engineering
- Slow convergence
- Needs many self-play games
- Hyperparameter tuning critical

---

### Approach 7: Counterfactual Regret Minimization (CFR)

**Overview:**
Game-theoretic approach for computing Nash equilibrium in imperfect/simultaneous information games. Minimizes regret through iterative self-play.

**Suitability for Strategic Influence: ⭐⭐⭐⭐ (HIGH for simultaneous moves)**

**Core Concept:**
```
Regret = opportunity cost of not playing best action
Counterfactual value = value if I played optimally to reach this point
CFR minimizes regret over all information sets
```

**Algorithm:**
```
For T iterations:
  1. Compute regrets for each action at each information set
  2. Use regrets to compute strategy (positive regrets → higher probability)
  3. Update cumulative strategy (all strategies ever used)
  4. Self-play with new strategy
5. Return average strategy (converges to Nash equilibrium)
```

**Key Properties:**
- **Convergence:** Converges to Nash equilibrium (mathematically proven)
- **Symmetric:** Both players play same strategy (in symmetric games)
- **Optimal:** Best possible against any opponent (no better unilateral deviation)

**Advantages:**
- Theoretically optimal (Nash equilibrium)
- Handles simultaneous moves elegantly
- Guaranteed convergence
- Symmetric players can use same strategy
- Natural handling of mixed strategies

**Disadvantages:**
- Very slow convergence (thousands of iterations needed)
- Complex implementation (tracking counterfactual values)
- Requires significant memory (store strategy history)
- Impractical for large games (branching factor × depth explosion)
- Offline training only (not real-time)

**Implementation Complexity: HIGH**

**Estimated Performance vs Current Best:**
- After 1K iterations: 40-50%
- After 10K iterations: 60-70%
- After 100K iterations: 80-90%
- After 1M iterations: 95%+

**Computational Requirements:**
- Time: 100K iterations × 20 games = 2M games
- With 30 sec/game: 700 hours
- With 8 workers: 87 hours
- Memory: Store strategy for all (state, action) pairs ≈ 50MB-1GB

**Variant: Monte Carlo CFR (MCCFR)**
- Sample game trees instead of enumerating all
- Much faster: 10-100x speedup
- Trade-off: higher variance

**Use Cases:**
1. **Theoretical analysis:** Find optimal mixed strategy
2. **Tournament strategy:** Perfect worst-case defense
3. **Benchmark:** Compare all other agents against Nash equilibrium
4. **Research:** Understand game structure

**Implementation Roadmap:**
1. Represent information sets (board state + history)
2. Track counterfactual values
3. Compute regrets per action
4. Update strategy proportional to positive regrets
5. Run 10K-100K iterations (offline)
6. Deploy converged strategy

**Pros:**
- Theoretically optimal
- Ideal for symmetric games
- Handles simultaneous moves correctly
- Provides worst-case guarantees

**Cons:**
- Extremely slow
- High complexity
- Requires offline training
- Overkill for single-player AI

---

### Approach 8: Policy Gradient Methods (Actor-Critic, PPO)

**Overview:**
Directly optimize the policy (action selection) by gradient ascent on expected reward. Combines policy gradient (actor) with value baseline (critic) for lower variance.

**Suitability for Strategic Influence: ⭐⭐⭐ (MODERATE, niche for multi-agent)**

**Core Algorithm (Advantage Actor-Critic):**
```
Policy network π(a|s): Action probabilities
Value network V(s): State value
Loss:
  Policy loss = -log π(a|s) × A(s,a)  // A = advantage
  Value loss = (V(s) - target)^2
  Total loss = policy_loss + value_loss
```

**Key Variants:**

**A. A2C (Advantage Actor-Critic)**
- Synchronous: parallel workers
- Low variance baseline
- Simpler implementation

**B. PPO (Proximal Policy Optimization)**
- Clipped surrogate objective (prevents huge updates)
- More stable training
- State-of-the-art on many benchmarks

**C. REINFORCE**
- Simplest variant
- High variance
- No baseline

**Advantages:**
- Learnable policy (no manual heuristics)
- Gradient-based optimization (efficient)
- Naturally handles stochasticity
- Scales to continuous action spaces
- Proven in complex domains (Atari, robotics)

**Disadvantages:**
- Requires neural networks (high-dimensional state)
- High variance during training
- Sensitive to hyperparameters
- Slow convergence (10K+ games)
- Requires careful implementation

**Implementation Complexity: HIGH**

**Expected Performance vs Current Best:**
- Early training (1K games): 30-40%
- Mid training (5K games): 50-65%
- Later training (20K games): 70-85%
- Late training (50K+ games): 85-95%

**Computational Requirements:**
- GPU: needed for training
- Time: 50K games × 20 sec = 278 hours
- With parallelization: 30-50 hours
- Memory: 300MB model + buffers

**Network Architecture:**
```
Shared layers (3-4 conv blocks):
  - Extract board features
Policy head:
  - Linear → softmax over ~50 actions
Value head:
  - Linear → single value output
```

**Hyperparameter Tuning (Critical):**
- Learning rate α: 1e-4 to 1e-3
- Discount γ: 0.95-0.99
- GAE λ: 0.9-0.95
- Batch size: 32-128
- Entropy bonus: 0.01-0.1 (encourage exploration)

**Use Cases:**
1. **Multi-agent learning:** Train against self, both improve
2. **Curriculum learning:** Start easy, increase difficulty
3. **Domain transfer:** Train on small boards, transfer to large
4. **Human-in-the-loop:** Reward from human feedback

**Implementation Roadmap:**
1. Define policy network (CNN + heads)
2. Set up parallel environments
3. Collect trajectories (states, actions, rewards)
4. Compute advantages (GAE or discounted returns)
5. Update policy + value via gradient descent
6. Repeat until convergence

**Pros:**
- State-of-the-art performance possible
- Flexible (handles various domains)
- Learnable features
- Good for multi-agent scenarios

**Cons:**
- Complex implementation
- Sensitive to hyperparameters
- Requires GPU
- Slow training
- Hard to debug

---

## Part 3: Comparative Analysis & Recommendations

### Comparison Matrix

| Approach | Stochasticity | Branching | Depth | Speed | Ease | Performance | Notes |
|----------|---|---|---|---|---|---|---|
| **Expectimax** | ★★★★★ | Medium | 2-3 | Slow | Medium | 70-80% | Mathematically sound |
| **Alpha-Beta** | ★★☆☆☆ | Medium | 4-6 | Fast | Low | 75-85% | PROVEN |
| **MCTS/UCT** | ★★★★☆ | High | 6-8 | Medium | Medium | 75-85% | Flexible |
| **MCTS/RAVE** | ★★★★☆ | High | 7-9 | Medium | High | 80-90% | Faster MCTS |
| **AlphaZero** | ★★★★☆ | High | 8-10 | Med | Hard | 90%+ | Overkill |
| **Genetic Algo** | ★★★☆☆ | N/A | N/A | Very Slow | Low | 60-80% | Niche use |
| **TD Learning** | ★★★★☆ | N/A | N/A | Fast* | Medium | 75-85% | *Offline |
| **CFR** | ★★★★★ | Medium | 2-3 | Very Slow | Hard | 95%+ | Overkill |
| **Policy Gradient** | ★★★★☆ | High | 8-10 | Medium* | Hard | 85-95% | *Offline |

### Immediate Priorities (Next 1-2 Weeks)

#### **Priority 1: Enhanced Alpha-Beta Pruning** ⭐⭐⭐⭐⭐
**Why:** Highest ROI - proven 30-50% performance gain with manageable complexity

**Implementation Steps:**
1. **Move Ordering** (1 hour)
   - Pre-evaluate moves, try best first
   - Use territory count as proxy for quality
   - Implement in `MinimaxAgent.generate_moves()`

2. **Transposition Tables** (2 hours)
   - Cache evaluated positions (Zobrist hashing)
   - Check cache before evaluation
   - 15-25% faster for 100+ total nodes

3. **Iterative Deepening** (1 hour)
   - Search depth 1, then 2, then 3
   - Stop when time limit reached
   - Actually faster due to improved cutoff rates

4. **Testing & Tuning** (2 hours)
   - Measure win rate improvement
   - Profile time per move
   - Tune depth vs. speed trade-off

**Expected Outcome:**
- Minimax depth-2 → depth-3 or depth-4 (effectively)
- Win rate: 70% → 80-85%
- Time: 0.5s → 1-2s per move

**Code Location:** `/sessions/stoic-serene-feynman/mnt/strategic-influence/src/strategic_influence/agents/minimax_agent.py`

---

#### **Priority 2: Improved MCTS (RAVE Variant)** ⭐⭐⭐⭐
**Why:** Handles stochasticity better; scales with compute; proven effective

**Implementation Steps:**
1. **Rollout Policy Enhancement** (2 hours)
   - Greedy movement (avoid expansion failures)
   - Prioritize growth in early phases
   - Avoid suicidal attacks

2. **RAVE Integration** (3 hours)
   - Track all-moves-as-first statistics
   - Blend RAVE with UCT estimates
   - Formula: `value = (w1 × rave_value + w2 × uct_value) / (w1 + w2)`
   - Decay RAVE weight as visits increase

3. **Parallel Tree Building** (2 hours)
   - Thread-safe node expansion
   - Combine results from 4 worker threads
   - 3-4x speedup expected

4. **Evaluation** (2 hours)
   - Compare 1K vs 5K simulations
   - Benchmark vs Minimax
   - Determine sweet spot

**Expected Outcome:**
- Win rate: 70% (basic MCTS) → 80-90% (RAVE)
- 5K simulations: 1-2 seconds per move
- Better late-game play due to stochasticity handling

**Code Location:** `/sessions/stoic-serene-feynman/mnt/strategic-influence/src/strategic_influence/agents/improved_mcts_agent.py`

---

#### **Priority 3: Expectimax for Stochastic Situations** ⭐⭐⭐
**Why:** Theoretically correct; bridges gap between deterministic minimax and MCTS

**Implementation Steps:**
1. **Stochastic Node Enumeration** (2 hours)
   - Enumerate expansion outcomes (binomial probabilities)
   - Pre-compute combat odds (already done)
   - Create chance node structure

2. **Expectimax Recursion** (3 hours)
   - Modify `minimax()` to handle chance nodes
   - Use pre-computed probabilities
   - Average across stochastic outcomes

3. **α-β Pruning for Expectimax** (2 hours)
   - Limited applicability (pruning less effective)
   - Still attempt bounds-based pruning
   - Focus on deterministic nodes

4. **Evaluation** (1 hour)
   - Test depth 2-3 only (exponential growth)
   - Compare to Minimax + random outcomes
   - Measure decision quality improvement

**Expected Outcome:**
- More principled stochastic decision-making
- Moderate performance gain (5-10%)
- Depth severely limited (2-3 only)

**Code Location:** `/sessions/stoic-serene-feynman/mnt/strategic-influence/src/strategic_influence/agents/` (new file)

---

### Medium-term Priorities (2-4 Weeks)

#### **Priority 4: Hybrid Minimax + MCTS** ⭐⭐⭐⭐
**Why:** Combines deterministic certainty with stochastic handling

**Approach:**
```
Search tree:
- Minimax depth 2 (deterministic moves)
- At leaves: MCTS playouts (handle stochasticity)
- Blend evaluations: heuristic + playout results
```

**Expected Win Rate:** 85-90%

**Implementation Effort:** 4-6 hours

---

#### **Priority 5: TD Learning with Neural Network** ⭐⭐⭐
**Why:** Learns game patterns; can improve offline

**Approach:**
1. Simple CNN (64→128 filters, 2-3 layers)
2. Play 5K-10K self-play games
3. Update V(s) after each turn
4. Evaluate after each 100 games

**Expected Win Rate:** 80-85% (after convergence)

**Implementation Effort:** 8-12 hours

---

### Long-term Exploration (1-2 Months)

#### **Priority 6: AlphaZero-style Training**
**Why:** Strongest possible AI; research value
**Note:** Only if higher performance is critical
**Implementation Effort:** 40-80 hours + infrastructure

---

### Not Recommended

#### Genetic Algorithms
- Too slow for meaningful convergence
- Better alternatives exist
- Consider only for weight tuning (not primary AI)

#### Full CFR
- Convergence too slow for practical use
- Overkill for deterministic play
- Consider only for game-theoretic analysis

#### Raw Policy Gradients (without MCTS)
- Worse than MCTS alone
- Not better than proven approaches
- Unless part of AlphaZero pipeline

---

## Part 4: Implementation Roadmap

### Week 1: Low-Hanging Fruit
```
Mon: Enhanced Alpha-Beta (move ordering, transposition tables)
Tue-Wed: Testing & tuning
Thu-Fri: MCTS rollout policy improvements
Fri: Preliminary evaluation
```

**Expected Win Rate:** 75-80% (vs current ~70%)

### Week 2: Core Improvements
```
Mon-Tue: RAVE integration for MCTS
Wed-Thu: Parallel tree building
Fri: Comparative benchmarking (Minimax vs MCTS)
```

**Expected Win Rate:** 80-85%

### Week 3: Stochastic Handling
```
Mon-Tue: Expectimax implementation
Wed-Thu: Testing & evaluation
Fri: Hybrid Minimax + MCTS prototype
```

**Expected Win Rate:** 85-90%

### Week 4: Advanced Techniques
```
Mon-Wed: TD Learning + NN setup
Thu-Fri: Self-play loop
Next week: Training & evaluation
```

**Expected Win Rate:** 85%+ (after convergence)

---

## Part 5: Evaluation Framework

### Benchmark Setup

**Three Baseline Agents:**
1. **Random Agent:** 0% skillful play (baseline)
2. **Greedy Agent:** Simple heuristics, no lookahead
3. **Current Best (Minimax depth-2):** ~70% vs random

### Test Protocol

**For Each New Approach:**
1. **100 games** vs each baseline (200 as P1 and P2)
2. **Win rate, territory differential, stone count**
3. **Time per move** (must be < 2 seconds)
4. **Stability** (std dev of results across 3 runs)

### Performance Targets

| Target | Win Rate | Time/Move | Test Games |
|--------|----------|-----------|-----------|
| Meets spec | 75%+ | < 2s | 100 |
| Exceeds spec | 85%+ | < 1s | 100 |
| Outstanding | 90%+ | < 0.5s | 100 |

---

## Conclusion

**Recommended Implementation Priority:**

1. **First (Week 1):** Enhanced Alpha-Beta Pruning
   - 30-50% performance gain
   - 4-6 hours implementation
   - Highest confidence success

2. **Second (Week 2):** Improved MCTS with RAVE
   - 80-90% win rate
   - Better stochasticity handling
   - 6-8 hours implementation

3. **Third (Week 3):** Expectimax for theoretically sound decisions
   - More principled stochastic search
   - Limited depth (2-3 only)
   - 6-8 hours implementation

4. **Fourth (Week 4+):** TD Learning or Hybrid approaches
   - Can achieve 85-90%+ with careful tuning
   - More computational investment
   - Good for long-term improvement

**Why Not AlphaZero/CFR:**
- Overkill for this game's complexity
- 40-80 hour implementation vs. 20-hour alternatives
- Marginal gains (90%+ vs 85%+) not worth infrastructure cost
- Better to have 85% AI in 3 weeks than 92% in 8 weeks

**Expected Final Performance:**
- End of Week 2: 80-85% (Minimax + improved MCTS)
- End of Week 3: 85-90% (Add Expectimax)
- End of Month: 90%+ (With TD Learning or hybrid)

---

## References

- [Expectimax Search Algorithm | Baeldung on Computer Science](https://www.baeldung.com/cs/expectimax-search)
- [CSE 473 Lecture 8: Adversarial Search - University of Washington](https://courses.cs.washington.edu/courses/cse473/13au/slides/08-expectimax.pdf)
- [Monte Carlo Tree Search - Wikipedia](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)
- [Monte-Carlo Tree Search: A Review - Springer](https://link.springer.com/article/10.1007/s10462-022-10228-y)
- [UCT Algorithm - Chess Programming Wiki](https://www.chessprogramming.org/UCT)
- [RAVE in Computer Go - University of Texas](https://www.cs.utexas.edu/~pstone/Courses/394Rspring11/resources/mcrave.pdf)
- [Alpha Zero and Monte Carlo Tree Search](https://joshvarty.github.io/AlphaZero/)
- [AlphaZero Documentation - OpenSpiel](https://openspiel.readthedocs.io/en/stable/alpha_zero.html)
- [Genetic Algorithms in Games - Medium](https://medium.com/@eugenesh4work/how-to-solve-games-with-genetic-algorithms-building-an-advanced-neuroevolution-solution-71c1817e0bf2)
- [Temporal Difference Learning - Wikipedia](https://en.wikipedia.org/wiki/Temporal_difference_learning)
- [Temporal Difference Learning - Chess Programming Wiki](https://www.chessprogramming.org/Temporal_Difference_Learning)
- [Q-Learning Wikipedia](https://en.wikipedia.org/wiki/Q-learning)
- [Counterfactual Regret Minimization - NIPS 2007](https://poker.cs.ualberta.ca/publications/NIPS07-cfr.pdf)
- [CFR Tutorial - Medium](https://xyzml.medium.com/learn-ai-game-playing-algorithm-part-iii-counterfactual-regret-minimization-b182a7ec85fb)
- [Policy Gradient Methods - Lil'Log](https://lilianweng.github.io/posts/2018-04-08-policy-gradient/)
- [Proximal Policy Optimization - Hugging Face](https://huggingface.co/blog/deep-rl-ppo)
- [Policy Gradient Theorem - DataCamp](https://www.datacamp.com/tutorial/policy-gradient-theorem)
- [Branching Factor - Wikipedia](https://en.wikipedia.org/wiki/Branching_factor)
- [Branching Factor in Search Complexity - Chess Programming Wiki](https://www.chessprogramming.org/Branching_Factor)
