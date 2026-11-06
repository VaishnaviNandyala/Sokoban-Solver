import heapq
import itertools
import time
from typing import Callable, Dict, Optional, Tuple

from .heuristics import HEURISTICS
from .level_parser import Level
from .moves import canonical, get_push_successors, get_successors, is_goal
from .state import State

DeadlockCheck = Callable[[Level, State], bool]


def _result(method, mode, solved, solution, explored, generated, t0, reason):
    return {
        "method": method,
        "mode": mode,
        "solved": solved,
        "solution": solution,
        "length": len(solution) if solution is not None else 0,
        "pushes": sum(1 for ch in solution if ch.isupper()) if solution else 0,
        "states_explored": explored,
        "states_generated": generated,
        "time": round(time.perf_counter() - t0, 4),
        "reason": reason,
    }


def _trace(parent: Dict[State, Optional[Tuple[State, str]]], key: State) -> str:
    """Follow the breadcrumbs from the goal back to the start."""
    actions = []
    while parent[key] is not None:
        key, action = parent[key]
        actions.append(action)
    return "".join(reversed(actions))


def solve_astar(level: Level, mode: str = "push", heuristic: str = "simple",
                time_limit: float = 60.0, max_states: Optional[int] = None,
                deadlock: Optional[DeadlockCheck] = None) -> dict:
    """Solve `level` with A*. Returns the shared result dictionary."""
    if mode == "step":
        successors, key_of = get_successors, (lambda s: s)
    elif mode == "push":
        successors, key_of = get_push_successors, (lambda s: canonical(level, s))
    else:
        raise ValueError("mode must be 'step' or 'push'")
    if heuristic not in HEURISTICS:
        raise ValueError("heuristic must be one of %s" % sorted(HEURISTICS))

    h = HEURISTICS[heuristic](level)
    method = "astar" + ("" if heuristic == "simple" else "-" + heuristic)
    if deadlock is not None:
        method += "+dl"

    t0 = time.perf_counter()
    start = level.start
    start_key = key_of(start)

    best_g: Dict[State, int] = {start_key: 0}   # cheapest cost found per state
    parent: Dict[State, Optional[Tuple[State, str]]] = {start_key: None}
    counter = itertools.count()                 # breaks ties in the heap
    heap = [(h(start), h(start), next(counter), 0, start, start_key)]
    explored = 0
    loops = 0

    def finish(solved, solution, reason):
        return _result(method, mode, solved, solution, explored,
                       len(best_g), t0, reason)

    while heap:
        loops += 1
        if max_states is not None and explored > max_states:
            return finish(False, None, "state limit")
        if loops % 256 == 0 and time.perf_counter() - t0 > time_limit:
            return finish(False, None, "timeout")

        _f, _h, _n, g, state, key = heapq.heappop(heap)
        if g > best_g[key]:                     # an older, worse copy: skip
            continue
        explored += 1

        if is_goal(level, state):
            return finish(True, _trace(parent, key), "solved")

        for action, nxt, cost in successors(level, state):
            if deadlock is not None and deadlock(level, nxt):
                continue
            nkey = key_of(nxt)
            ng = g + cost
            if nkey not in best_g or ng < best_g[nkey]:
                best_g[nkey] = ng
                parent[nkey] = (key, action)
                hv = h(nxt)
                heapq.heappush(heap, (ng + hv, hv, next(counter), ng, nxt, nkey))

    return finish(False, None, "no solution")
