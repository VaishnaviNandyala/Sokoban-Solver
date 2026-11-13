"""A* search for Sokoban (Member 4).

astar(level, heuristic="sum", use_deadlock=True, push_moves=True, ...)

push_moves=True  : one search step = one box push (walking is included in the
                   cost). States are compared exactly (player position included),
                   so the returned solution has the minimum number of MOVES.
merge_regions    : with push_moves, treat states whose player can reach the same
                   cells as equal (canonical key). Faster, but the solution can be
                   a move or two longer than the true minimum.
push_moves=False : one search step = one player step (cost 1).
weight           : weighted A*, priority f = g + weight * h. weight=1 is normal A*.
                   weight > 1 is faster but the solution may be longer than optimal.
greedy=True      : greedy best-first search, priority f = h (ignores the cost so far).
                   Usually the fastest, but gives no guarantee on solution length.
All return the same SearchResult as the BFS/DFS baselines.
"""
import heapq
import itertools
import time

from .deadlock import is_deadlock
from .heuristics import get_heuristic
from .level_parser import Level
from .moves import canonical, get_push_successors, get_successors, is_goal
from .result import SearchResult, make_result


def astar(level: Level, heuristic="sum", use_deadlock=True, push_moves=True,
          time_limit=None, max_nodes=None, merge_regions=False,
          weight=1.0, greedy=False) -> SearchResult:
    h = get_heuristic(heuristic)
    hname = heuristic if isinstance(heuristic, str) else heuristic.__name__
    if greedy:
        name = f"Greedy({hname})"
    elif weight != 1:
        name = f"WA*({hname}, w={weight:g})"
    else:
        name = f"A*({hname})"

    def prio(g, hv):
        return hv if greedy else g + weight * hv
    succ = get_push_successors if push_moves else get_successors
    key = (lambda s: canonical(level, s)) if (push_moves and merge_regions) else (lambda s: s)

    t0 = time.perf_counter()
    start = level.start
    if use_deadlock and is_deadlock(level, start):
        return make_result(name, "unsolvable", None, 0, 1, t0, time.perf_counter())

    tie = itertools.count()
    k0 = key(start)
    best = {k0: 0}
    h0 = h(level, start)
    openq = [(prio(0, h0), h0, next(tie), 0, k0, start, "")]   # f, h, tiebreak, g, key, state, path
    expanded, generated = 0, 1

    while openq:
        f, _, _, g, k, s, path = heapq.heappop(openq)
        if g > best.get(k, float("inf")):
            continue                                   # stale queue entry
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
        for action, ns, cost in succ(level, s):
            if use_deadlock and is_deadlock(level, ns):
                continue
            nk = key(ns)
            ng = g + cost
            if greedy and nk in best:
                continue                               # greedy: each state only once
            if ng < best.get(nk, float("inf")):
                best[nk] = ng
                generated += 1
                nh = h(level, ns)
                heapq.heappush(openq, (prio(ng, nh), nh, next(tie), ng, nk, ns, path + action))

    return make_result(name, "unsolvable", None, expanded, generated, t0, time.perf_counter())
