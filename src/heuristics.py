from typing import Callable, Dict, Tuple

from .level_parser import Level
from .state import Pos, State

Heuristic = Callable[[State], int]


def manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def simple_heuristic(level: Level) -> Heuristic:
    """Sum over boxes of the distance to the NEAREST goal.

    Weakness: two boxes may both pick the same goal.
    """
    goals = list(level.goals)
    nearest: Dict[Pos, int] = {}

    def h(state: State) -> int:
        total = 0
        for box in state.boxes:
            if box not in nearest:
                nearest[box] = min(manhattan(box, g) for g in goals)
            total += nearest[box]
        return total

    return h


def matching_heuristic(level: Level) -> Heuristic:
    """Give every box its OWN goal so that the total distance is smallest.

    Stronger than simple_heuristic (never smaller), so A* explores fewer
    states. Uses a small dynamic programme over sets of goals, which is fine
    for the few boxes our levels have.
    """
    goals = sorted(level.goals)
    cache: Dict[Tuple[Pos, ...], int] = {}

    def h(state: State) -> int:
        boxes = tuple(sorted(state.boxes))
        if boxes in cache:
            return cache[boxes]
        n = len(boxes)
        inf = float("inf")
        best = [inf] * (1 << n) 
        best[0] = 0
        for mask in range(1 << n):
            if best[mask] == inf:
                continue
            i = bin(mask).count("1")
            if i >= n:
                continue
            for j in range(n):
                if mask >> j & 1:
                    continue
                new = mask | (1 << j)
                cost = best[mask] + manhattan(boxes[i], goals[j])
                if cost < best[new]:
                    best[new] = cost
        cache[boxes] = best[(1 << n) - 1]
        return cache[boxes]

    return h


HEURISTICS = {"simple": simple_heuristic, "matching": matching_heuristic}
