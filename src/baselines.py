"""Uninformed baselines (BFS / DFS) that return the shared SearchResult.

Used by the experiment runner so every algorithm is measured the same way
(same time limit, same node counting). They use the Member 1 engine only.
"""
import time
from collections import deque

from .deadlock import is_deadlock
from .level_parser import Level
from .moves import canonical, get_push_successors, get_successors, is_goal
from .result import SearchResult, make_result


def uninformed_search(level: Level, strategy="bfs", use_deadlock=False,
                      push_moves=False, time_limit=None, max_nodes=None) -> SearchResult:
    assert strategy in ("bfs", "dfs")
    name = strategy.upper()
    succ = get_push_successors if push_moves else get_successors
    key = (lambda s: canonical(level, s)) if push_moves else (lambda s: s)

    t0 = time.perf_counter()
    start = level.start
    if use_deadlock and is_deadlock(level, start):
        return make_result(name, "unsolvable", None, 0, 1, t0, time.perf_counter())

    frontier = deque([(start, "")])
    seen = {key(start)}
    expanded, generated = 0, 1

    while frontier:
        s, path = frontier.popleft() if strategy == "bfs" else frontier.pop()
        if is_goal(level, s):
            return make_result(name, "solved", path, expanded, generated,
                               t0, time.perf_counter())
        expanded += 1
        if expanded % 256 == 0:
            if time_limit is not None and time.perf_counter() - t0 > time_limit:
                return make_result(name, "timeout", None, expanded, generated,
                                   t0, time.perf_counter())
            if max_nodes is not None and expanded >= max_nodes:
                return make_result(name, "node_limit", None, expanded, generated,
                                   t0, time.perf_counter())
        for action, ns, _ in succ(level, s):
            if use_deadlock and is_deadlock(level, ns):
                continue
            k = key(ns)
            if k in seen:
                continue
            seen.add(k)
            generated += 1
            frontier.append((ns, path + action))

    return make_result(name, "unsolvable", None, expanded, generated, t0, time.perf_counter())
