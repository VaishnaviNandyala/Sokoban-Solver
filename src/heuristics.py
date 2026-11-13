"""Heuristics for A* (Member 4).

All heuristics here are ADMISSIBLE (never overestimate the remaining number
of moves) because every box needs at least its Manhattan distance in pushes
and each push costs at least 1 move. Admissible => A* returns a shortest solution.
"""
from functools import lru_cache

from .level_parser import Level
from .state import State


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def h_zero(level: Level, state: State) -> int:
    """h = 0. A* then behaves like Dijkstra / uniform-cost search."""
    return 0


def h_sum_distance(level: Level, state: State) -> int:
    """Sum over boxes of the Manhattan distance to the NEAREST goal."""
    goals = tuple(level.goals)
    return sum(min(_manhattan(b, g) for g in goals) for b in state.boxes)


@lru_cache(maxsize=500000)
def _matching(goals, boxes):
    boxes = sorted(boxes)
    n = len(boxes)
    cost = [[_manhattan(b, g) for g in goals] for b in boxes]
    INF = float("inf")
    dp = {0: 0}
    for i in range(n):
        nxt = {}
        for mask, c in dp.items():
            for j in range(n):
                if not (mask >> j) & 1:
                    m2 = mask | (1 << j)
                    v = c + cost[i][j]
                    if v < nxt.get(m2, INF):
                        nxt[m2] = v
        dp = nxt
    return dp[(1 << n) - 1]


def h_matching(level: Level, state: State) -> int:
    """Min-cost one-to-one matching of boxes to goals (Manhattan costs).

    Tighter than h_sum_distance because two boxes may not share one goal.
    Exact bitmask DP for up to 9 boxes, otherwise falls back to h_sum_distance.
    """
    if len(state.boxes) > 9:
        return h_sum_distance(level, state)
    return _matching(tuple(sorted(level.goals)), state.boxes)


HEURISTICS = {
    "zero": h_zero,
    "sum": h_sum_distance,
    "matching": h_matching,
}


def get_heuristic(name_or_fn):
    if callable(name_or_fn):
        return name_or_fn
    return HEURISTICS[name_or_fn]
