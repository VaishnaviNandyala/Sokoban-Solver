# Bug list (found by hand testing)

Hand tests by Member 5. Every item below was reproduced. "Open" means it is not fixed yet; the owner is the member who wrote that file.

## Bugs and inconsistencies

| # | Where | What happens | How to reproduce | Suggested fix | Status |
|---|---|---|---|---|---|
| 1 | `src/main.py`, `src/moves.py` (Member 1) | An invalid letter in `--replay` crashes with a `KeyError` traceback instead of the friendly "Illegal move" message. | `python -m src.main --level levels/Level-01.txt --replay x` | In `main.py`, check that every letter is in `UDLRudlr` before replaying, or catch `KeyError` and print "Illegal move". | Open |
| 2 | `src/main.py` (Member 1) | A wrong level path ends with a raw `FileNotFoundError` traceback. | `python -m src.main --level levels/nope.txt` | Catch `FileNotFoundError` and print "Level file not found". | Open |
| 3 | `experiments/codes/run_bfs_dfs.py` (Member 2) | The command written in the docstring does not work, because the file lives in `experiments/codes/`. | `python -m experiments.run_bfs_dfs` gives "No module named experiments.run_bfs_dfs" | Write `python -m experiments.codes.run_bfs_dfs` in the docstring. | Open |
| 4 | `run_bfs_dfs.py` (Member 2) and `run_astar.py` (Member 3) | The default `--out` is `experiments/results_*.csv`, but the results are kept in `experiments/results/`. A run without `--out` creates a stray file outside that folder. | `python -m experiments.codes.run_bfs_dfs --levels levels/Level-01.txt` saves `experiments/results_bfs_dfs.csv` | Change the defaults to `experiments/results/...`. | Open |
| 5 | `run_bfs_dfs.py` docstring (Member 2) | It says the CSV is "for Member 4's report"; the report is Member 5's. | Read the first lines of the file. | Fix the text. | Open |

## Design limit (not a coding mistake)

| # | Where | What happens | Cause | Status |
|---|---|---|---|---|
| 6 | `src/astar.py`, push mode (Member 3) | A* in push mode can return a solution 1 to 2 moves longer than the optimum: 12 against 10 on Level-03, 13 against 12 on Level-04, 16 against 15 on Level-05. | States are merged by the region the player can walk in (`canonical()`), so a better player position inside the region is dropped. With an exact (player, boxes) key the results match the step-mode optimum on Levels 03 to 08. | Known, documented in the report |

## Tested and working

* A level that starts already solved is accepted and solved with an empty solution.
* Windows line endings (CRLF) and extra blank lines at the end of a level file load correctly.
* A level with no boxes and no goals loads and counts as solved.
* A tab character in a level file gives a clear error message with its position.
* A level with a different number of boxes and goals is rejected with a clear message.
* Rows of different length are accepted and padded (the missing cells count as wall).
* Moving into a wall or pushing a box into a wall or another box returns "illegal", not a crash.
* `time_limit=0` and `max_states` stop BFS, DFS and A* with the reasons `timeout` and `state limit`.
* The deadlock check never marks the start state of any of the 14 solvable levels as dead (no false alarm). It marks Levels 15 and 16 as dead, which is correct.
* Both heuristics stay at or below the optimal number of moves at the start of every level that BFS solved (they never overestimate).
* All 96 existing tests pass.
