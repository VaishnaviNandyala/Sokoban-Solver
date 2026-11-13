"""Deadlock detection (Member 4).

A state is a deadlock if it can never be solved. Pruning these states makes
the search much faster. Two kinds are detected:

1. Dead squares (simple deadlock): a box standing on a square from which it can
   never be pushed to any goal, e.g. a corner that is not a goal, or a wall
   line with no goal along it. Computed once per level by pulling boxes
   backwards from the goals.
2. 2x2 freeze: four neighbouring cells forming a 2x2 block made of walls and
   boxes, with at least one box not on a goal. Those boxes can never move.
"""
from collections import deque
from functools import lru_cache

from .level_parser import Level
from .moves import DIRECTIONS
from .state import State


@lru_cache(maxsize=None)
def dead_squares(level: Level):
    live = set(level.goals)
    queue = deque(live)
    while queue:
        b = queue.popleft()
        for d in DIRECTIONS.values():
            p = (b[0] + d[0], b[1] + d[1])      # where the box would come from
            pl = (p[0] + d[0], p[1] + d[1])     # where the player must stand
            if p in live or level.is_wall(p) or level.is_wall(pl):
                continue
            live.add(p)
            queue.append(p)
    floor = {(r, c) for r in range(level.height) for c in range(level.width)
             if not level.is_wall((r, c))}
    return frozenset(floor - live)


def _square_freeze(level: Level, state: State) -> bool:
    boxes = state.boxes
    for (r, c) in boxes:
        for dr, dc in ((0, 0), (0, -1), (-1, 0), (-1, -1)):
            cells = [(r + dr, c + dc), (r + dr, c + dc + 1),
                     (r + dr + 1, c + dc), (r + dr + 1, c + dc + 1)]
            if all(level.is_wall(x) or x in boxes for x in cells) and \
               any(x in boxes and x not in level.goals for x in cells):
                return True
    return False


def is_deadlock(level: Level, state: State) -> bool:
    dead = dead_squares(level)
    if any(b in dead for b in state.boxes):
        return True
    return _square_freeze(level, state)
