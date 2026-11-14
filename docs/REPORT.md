## Sokoban Solver: Comparing BFS, DFS, A*, Weighted A* and Greedy Search

## 1. Introduction

Sokoban is a puzzle in which a player pushes boxes around a grid onto designated goal squares. Boxes can only be **pushed, never pulled**, so an incorrect push can place a box in a position from which the puzzle can no longer be completed.

This project develops a Sokoban solver using multiple search strategies and compares their performance on 16 puzzle levels.

The implemented search algorithms are:

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- A\* Search
- Weighted A\* Search
- Greedy Best-First Search

The project also improves search using:

- heuristic functions,
- push-based search,
- deadlock pruning.

The main objectives are:

1. Solve Sokoban levels automatically using different search strategies.
2. Compare the algorithms in terms of solution length, nodes expanded and execution time.
3. Study the effect of different heuristics.
4. Study the effect of push-based search and deadlock pruning.
5. Compare optimal search with faster, non-optimal approaches.

---

## 2. Team and Contributions

| Member   | Name                   | Responsibility                                                                                            |
| -------- | ---------------------- | --------------------------------------------------------------------------------------------------------- |
| Member 1 | Panuganti Vishishta    | Game rules and setup: `level_parser.py`, `state.py`, `moves.py`, `render.py`, `main.py`, `test_engine.py` |
| Member 2 | Kollati Devi Chandrika | BFS and DFS: `bfs_dfs.py`, `run_bfs_dfs.py`, `test_bfs_dfs.py`                                            |
| Member 3 | Nandyala Vaishnavi     | A\* search and heuristics: `astar.py`, `heuristics.py`                                                    |
| Member 4 | Namburi Veda Aishwarya | Deadlock detection and the demo app: `deadlock.py`, `app.py`, `viz.py`                                    |
| Member 5 | Chaitrali Zode         | Levels, experiments, results table and charts, report, slides                                             |

Member 3 is responsible for the A* search implementation and heuristic functions. The `astar.py` module contains A*, Weighted A\* and Greedy search, while `heuristics.py` contains the distance and box-goal matching heuristics.

---

## 3. Project Structure and Level Representation

The project contains 16 text-based Sokoban levels.

The main components are:

```text
Sokoban-Solver/
├── README.md
├── requirements.txt
├── app.py
├── app_play.py
├── levels/
├── src/
│   ├── level_parser.py
│   ├── state.py
│   ├── moves.py
│   ├── render.py
│   ├── main.py
│   ├── bfs_dfs.py
│   ├── astar.py
│   ├── heuristics.py
│   ├── deadlock.py
│   ├── baselines.py
│   ├── result.py
│   ├── play.py
│   ├── runner.py
│   └── viz.py
├── experiments/
│   ├── run_bfs_dfs.py
│   ├── run_all.py
│   ├── make_charts.py
│   ├── results_bfs_dfs.csv
│   ├── results_all.csv
│   └── results_long.csv
├── results/
│   ├── results_summary.csv
│   └── charts/
└── tests/
```

### Level file format

| Symbol | Meaning          |
| ------ | ---------------- |
| `#`    | Wall             |
| `@`    | Player           |
| `+`    | Player on a goal |
| `$`    | Box              |
| `*`    | Box on a goal    |
| `.`    | Goal             |
| space  | Floor            |

Each level contains exactly one player and the number of boxes is equal to the number of goals.

---

## 4. Search Algorithms

### 4.1 Breadth-First Search

BFS explores states level by level using a queue.

When every action has the same cost, BFS returns the shortest solution.

The main advantage of BFS is optimality, but its memory and search time can increase rapidly as the state space grows.

---

### 4.2 Depth-First Search

DFS follows one branch as deeply as possible before backtracking.

It requires less memory than BFS, but it does not guarantee the shortest solution.

Therefore, DFS can find very long solutions even when a much shorter solution exists.

---

### 4.3 A\* Search

A\* selects the state with the lowest:

\[
f(n)=g(n)+h(n)
\]

where:

- \(g(n)\) is the cost already spent reaching the state.
- \(h(n)\) is the estimated remaining cost.
- \(f(n)\) is the total estimated cost of the solution through that state.

A\* therefore combines the actual cost already incurred with an estimate of the remaining cost.

With an admissible heuristic, A\* can find a shortest solution.

---

### 4.4 Weighted A\*

Weighted A* modifies the A* evaluation function to:

\[
f(n)=g(n)+3h(n)
\]

in the experiments.

The heuristic is therefore given more importance than in normal A\*.

This makes the search more strongly directed toward the goal and can greatly reduce the number of states expanded.

The trade-off is that Weighted A\* does not guarantee the shortest solution.

In this project, Weighted A\* uses the `matching` heuristic together with push-based search and deadlock pruning.

---

### 4.5 Greedy Best-First Search

Greedy search ranks states using only:

\[
f(n)=h(n)
\]

It ignores the cost already spent, \(g(n)\).

This makes it very fast because it focuses directly on states that appear closest to the goal.

However, it provides no shortest-path guarantee and can produce substantially longer solutions.

---

## 5. Heuristics

The project uses two main heuristics.

### 5.1 Sum of Distances

For every box, the Manhattan distance to its nearest goal is calculated and the distances are added:

\[
h(n)=\sum_i \min_j d(box_i,goal_j)
\]

This heuristic is simple and inexpensive.

Its weakness is that multiple boxes may effectively choose the same goal when calculating the estimate.

---

### 5.2 Box-Goal Matching

The matching heuristic assigns every box to a distinct goal.

It calculates the minimum total Manhattan distance for a one-to-one assignment between boxes and goals.

This gives a tighter estimate because two boxes cannot be assigned to the same goal.

Both heuristics never overestimate the required number of pushes, so they are admissible for the A\* formulation used in the project.

---

## 6. Deadlock Detection

Deadlock detection is used to prevent the search from wasting time on states that cannot lead to a solution.

A state can be discarded when:

- a box is placed on a dead square,
- a box is trapped in a corner that is not a goal,
- a box is trapped along a wall with no possible goal,
- boxes and walls create an unsolvable 2×2 block.

Deadlock pruning is an optimization applied to the search. It is separate from the heuristic calculation.

---

## 7. Search Configurations

The experiments compare eight configurations:

| Configuration                    | Description                                                         |
| -------------------------------- | ------------------------------------------------------------------- |
| BFS                              | One search step = one player step                                   |
| DFS                              | One search step = one player step                                   |
| A\* sum (steps)                  | A\* with sum heuristic, one step per player step                    |
| A\* sum (pushes)                 | One search step = one box push; walking is included in the cost     |
| A\* sum (pushes + deadlock)      | Push-based A\* with sum heuristic and deadlock pruning              |
| A\* matching (pushes + deadlock) | Push-based A\* with matching heuristic and deadlock pruning         |
| WA\* w=3 (pushes + deadlock)     | Weighted A\* with weight 3, matching heuristic and deadlock pruning |
| Greedy (pushes + deadlock)       | Greedy search with matching heuristic and deadlock pruning          |

---

## 8. Experimental Setup

All experiments use:

- 16 levels
- 8 algorithm configurations
- 10-second time limit per configuration
- one run per configuration

The raw results are stored in:

```text
experiments/results_all.csv
```

The summary and charts are generated from this data.

The experiment measures:

- solved status,
- solution length,
- nodes expanded,
- execution time.

The results use the same time limit and node-counting approach for the configurations being compared.

---

## 9. Results

### 9.1 Nodes Expanded

| Level    |             BFS |             DFS | A\* sum (steps) | A\* sum (pushes) | A\* sum + deadlock | A\* matching + deadlock |       WA\* w=3 |         Greedy |
| -------- | --------------: | --------------: | --------------: | ---------------: | -----------------: | ----------------------: | -------------: | -------------: |
| Level-1  |               1 |              64 |               1 |                1 |                  1 |                       1 |              1 |              1 |
| Level-2  |              12 |               2 |               2 |                2 |                  2 |                       2 |              2 |              2 |
| Level-3  |           1,078 |           1,501 |             183 |               43 |                 32 |                      22 |              4 |              4 |
| Level-4  |           1,983 |           4,076 |             233 |               51 |                 24 |                      18 |              5 |              5 |
| Level-5  |          23,639 |          29,451 |           3,348 |              760 |                382 |                     284 |             40 |              5 |
| Level-6  |           1,051 |             378 |             400 |               73 |                 43 |                      41 |             10 |              3 |
| Level-7  |             378 |           4,660 |              76 |               11 |                  9 |                       9 |              4 |              4 |
| Level-8  |             726 |           2,607 |             145 |               25 |                 23 |                      18 |              8 |              5 |
| Level-9  |         207,129 |          88,456 |          87,634 |           18,363 |              4,466 |                   3,436 |             13 |             12 |
| Level-10 |         timeout |         timeout |         timeout |          timeout |            timeout |                  15,346 |             30 |             18 |
| Level-11 |         timeout |         timeout |         timeout |          timeout |            timeout |                 timeout |             24 |             17 |
| Level-12 |         timeout |         timeout |         timeout |          timeout |            timeout |                 timeout |             64 |             11 |
| Level-13 |         350,591 |         215,853 |          76,618 |           17,377 |             10,877 |                   8,119 |            634 |              8 |
| Level-14 |               1 |               1 |               1 |                1 |                  1 |                       1 |              1 |              1 |
| Level-15 |  unsolvable (5) |  unsolvable (5) |  unsolvable (5) |   unsolvable (1) |     unsolvable (0) |          unsolvable (0) | unsolvable (0) | unsolvable (0) |
| Level-16 | unsolvable (70) | unsolvable (70) | unsolvable (70) |   unsolvable (7) |     unsolvable (0) |          unsolvable (0) | unsolvable (0) | unsolvable (0) |

---

### 9.2 Solution Length

| Level    |   Shortest |     DFS | WA\* w=3 | Greedy | Pushes (shortest) |
| -------- | ---------: | ------: | -------: | -----: | ----------------: |
| Level-1  |          1 |       1 |        1 |      1 |                 1 |
| Level-2  |          2 |       2 |        2 |      2 |                 2 |
| Level-3  |         10 |     117 |       12 |     12 |                 6 |
| Level-4  |         12 |     275 |       13 |     13 |                 5 |
| Level-5  |         15 |     480 |       16 |     21 |                 5 |
| Level-6  |         14 |      72 |       14 |     14 |                 5 |
| Level-7  |          9 |      12 |       10 |     10 |                 4 |
| Level-8  |         10 |     126 |       10 |     16 |                 5 |
| Level-9  |         26 |    2145 |       31 |     32 |                12 |
| Level-10 |         29 | timeout |       31 |     56 |                13 |
| Level-11 |        41† | timeout |       45 |     44 |                17 |
| Level-12 |        28† | timeout |       28 |     39 |                11 |
| Level-13 |         28 |     154 |       28 |     30 |                 8 |
| Level-14 |          1 |       1 |        1 |      1 |                 1 |
| Level-15 | unsolvable |       - |        - |      - |                 - |
| Level-16 | unsolvable |       - |        - |      - |                 - |

† Exact A\* with the matching heuristic requires a longer time limit for Levels 11 and 12. A separate 80-second experiment found 41 moves for Level-11 in about 12.9 seconds and 28 moves for Level-12 in about 12.1 seconds.

---

## 10. Summary of Results

| Configuration                    | Levels solved | Total nodes expanded | Total time (s) |
| -------------------------------- | ------------: | -------------------: | -------------: |
| BFS                              |      11 of 14 |              586,589 |           7.36 |
| DFS                              |      11 of 14 |              347,049 |           3.67 |
| A\* sum (steps)                  |      11 of 14 |              168,641 |           3.74 |
| A\* sum (pushes)                 |      11 of 14 |               36,707 |           4.48 |
| A\* sum (pushes + deadlock)      |      11 of 14 |               15,860 |           5.05 |
| A\* matching (pushes + deadlock) |      12 of 14 |               11,951 |           6.79 |
| WA\* w=3 (pushes + deadlock)     |      14 of 14 |                  722 |           0.11 |
| Greedy (pushes + deadlock)       |      14 of 14 |                   50 |           0.01 |

The 14 solvable levels are Levels 1–14. Levels 15 and 16 are intentionally unsolvable test levels.

---

## 11. Findings

### 11.1 A\* expands far fewer nodes than BFS

Over the common levels, BFS expanded 586,589 nodes, while exact A\* using matching, push-based search and deadlock pruning expanded 11,951 nodes.

This is approximately:

\[
\frac{586589}{11951}\approx49
\]

Therefore, the improved A\* configuration expanded about **49 times fewer nodes** than BFS.

---

### 11.2 Each optimization reduces the search effort

The total number of nodes decreases progressively:

```text
BFS                         586,589
A* steps                    168,641
A* pushes                    36,707
A* pushes + deadlock         15,860
A* matching + deadlock       11,951
```

This shows the benefit of combining a better state representation, pruning and a stronger heuristic.

---

### 11.3 BFS and exact A\* produce shortest solutions

BFS and the exact A\* configurations return shortest solutions for the levels they solve.

DFS does not guarantee shortest solutions.

For example:

- Level-9 shortest solution: 26 moves
- DFS solution: 2,145 moves

Similarly:

- Level-5 shortest solution: 15 moves
- DFS solution: 480 moves

---

### 11.4 Weighted A\* and Greedy are much faster

Weighted A\* and Greedy solve all 14 solvable levels within the 10-second limit.

Their node counts are also dramatically smaller:

- Weighted A\*: 722 total nodes
- Greedy: 50 total nodes

However, this speed comes at the cost of optimality.

---

### 11.5 The cost of faster search is longer solutions

Across the 14 solvable levels:

- Shortest solutions total **226 moves**
- Weighted A\* totals **242 moves**
- Greedy totals **291 moves**

Therefore:

- Weighted A\* is about **7% longer** than the shortest total.
- Greedy is about **29% longer** than the shortest total.

This demonstrates the trade-off between speed and optimality.

---

### 11.6 Matching is a stronger heuristic

The matching heuristic gives a tighter estimate because each box is assigned to a different goal.

Within the experiment, exact A* with matching solves one more level than exact A* with the simple heuristic under the 10-second limit.

Level-10 is solved by A* matching within the limit, while the simpler A* configurations time out.

---

### 11.7 Deadlock pruning detects unsolvable levels early

Levels 15 and 16 are intentionally unsolvable.

Without deadlock pruning, the search expands some states before determining that no solution exists.

With deadlock pruning:

```text
Level-15 → 0 nodes
Level-16 → 0 nodes
```

The deadlock-aware configurations therefore identify these impossible levels immediately.

---

### 11.8 Fewer nodes does not always mean less time

A\* can expand fewer nodes but still take more time because each state requires additional computation for:

- heuristic evaluation,
- priority queue operations,
- push-based state processing,
- deadlock checks.

Therefore, node count and execution time are related but are not identical measures of performance.

---

## 12. Limitations

The main limitations of the experiments are:

1. Each configuration was run once, so execution times can vary between runs.
2. The experiments use a fixed 10-second limit.
3. Weighted A\* and Greedy sacrifice optimality for speed.
4. The results are based on 16 levels, so larger level collections could produce different performance patterns.
5. The implementation uses relatively simple Manhattan-distance-based heuristics.
6. More advanced deadlock patterns could further reduce search effort.

For more reliable timing comparisons, the experiments can be repeated several times and median execution times can be reported.

---

## 13. Future Work

Possible improvements include:

- adding more advanced deadlock patterns,
- using pattern databases,
- benchmarking on larger level collections,
- repeating experiments to obtain more stable timing measurements,
- adding a custom level editor,
- supporting level export/import,
- improving accessibility and mobile controls.

---

## 14. Conclusion

This project demonstrates how different search strategies behave on the Sokoban problem.

BFS provides shortest solutions but can require a large amount of memory and search effort. DFS uses less memory but can produce very long solutions.

A\* improves the search by combining the actual cost with a heuristic estimate. Push-based search, deadlock pruning and the matching heuristic further reduce the search effort.

Weighted A\* and Greedy search provide a different trade-off. They solve all 14 solvable levels very quickly, but their solutions can be longer than the shortest possible solutions.

Overall, the experiments show that the best search strategy depends on the objective:

- **Shortest solution:** BFS or exact A\*
- **Reduced search effort:** A\* with push-based search, matching and deadlock pruning
- **Very fast solution:** Weighted A\* or Greedy
- **No-solution detection:** deadlock-aware configurations

The project therefore demonstrates the practical trade-off between **optimality, search effort and execution speed** in Sokoban solving.

---

## Appendix: How to Reproduce

Run the following commands from the project root:

```bash
python -m pytest -q
```

Run all experiments:

```bash
python -m experiments.run_all --time-limit 10
```

Regenerate charts:

```bash
python -m experiments.make_charts
```

Run the Streamlit solver:

```bash
streamlit run app.py
```

Run the play-mode application:

```bash
streamlit run app_play.py
```

Run the command-line level viewer:

```bash
python -m src.main --level levels/Level-2.txt
```

Replay a solution:

```bash
python -m src.main --level levels/Level-2.txt --replay RR
```

Example of using A\* directly:

```python
from src.level_parser import load_level
from src.astar import astar

res = astar(load_level("levels/Level-9.txt"), "matching")
print(res.status, res.moves, res.nodes_expanded, res.solution)
```
