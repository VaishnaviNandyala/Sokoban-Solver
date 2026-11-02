# Sokoban Solver (AI Course Project)

Push boxes onto goals. Boxes can only be pushed, never pulled. The solver
uses BFS / DFS / A* with heuristics and deadlock detection.

## Status
| Part | Owner | Status |
|---|---|---|
| Game engine (state, parser, moves, render) | Member 1 | done |
| Search algorithms (BFS, DFS, A*) | Member 2 | todo |
| Heuristics + deadlock detection | Member 3 | todo |
| GUI, experiments, report | Member 4 | todo |

## Quick start
```bash
pip install -r requirements.txt
python -m pytest -q
python -m src.main --level levels/easy_01.txt --replay D
```

## Engine API (Member 1) - please do not change signatures without telling the team
```python
from src.level_parser import load_level, parse_level   # -> Level
from src.state import State                            # State(player, boxes)
from src.moves import (get_successors, get_push_successors, is_goal,
                       apply_action, canonical, reachable)
from src.render import render
```
| Function | Returns |
|---|---|
| `load_level(path)` | `Level` with `.walls`, `.goals`, `.start`, `.height`, `.width` |
| `get_successors(level, state)` | list of `(action, next_state, cost)`; one player step, cost 1 |
| `get_push_successors(level, state)` | same shape; one box push, action = walk + push (e.g. `"uurR"`), cost = steps. Far fewer states: recommended for A* |
| `canonical(level, state)` | state with player normalized to its reachable region; use as the `visited` key with push successors |
| `is_goal(level, state)` | `True` when `state.boxes == level.goals` |
| `apply_action(level, state, "R")` | new `State` or `None` if illegal |
| `render(level, state)` | multi-line string |

## Conventions
- Coordinates are `(row, col)`, row 0 is the top line of the level file.
- Actions: `U D L R`. lowercase = plain step, UPPERCASE = step that pushed a box.
- A solver should return the solution as one action string (or `None` if unsolvable), so it can be replayed with `--replay`.
- `State` is immutable and hashable. Walls and goals are in `Level`, not in `State`.

## Level symbols
`#` wall, `@` player, `+` player on goal, `$` box, `*` box on goal, `.` goal, space = floor.

Levels: `trivial_01`, `easy_01`, `medium_01`, `medium_02`, `hard_01`, `unsolvable_01` (box stuck in a corner).

## Git workflow
- `main` is protected: merge only through pull requests.
- One branch per member/feature: `feature/engine-state-parser`, `feature/search-astar`, `feature/heuristics-deadlock`, `feature/gui-experiments`.
- Start: `git checkout main && git pull && git checkout -b feature/<name>`
- Finish: push the branch, open a PR, get one review, merge when tests pass, delete the branch.
- Before continuing your own work after a merge: `git checkout <your-branch> && git merge main`.
- Edit only your own files to avoid conflicts.
