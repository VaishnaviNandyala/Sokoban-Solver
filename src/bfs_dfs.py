"""BFS and DFS solvers (Member 2).

Works with Member 1's engine:
    load_level(path)                 -> Level
    get_successors(level, state)     -> [(action, next_state, cost)]   one step
    get_push_successors(level, state)-> same shape, one box push (walk + push)
    canonical(level, state)          -> state key to use with push successors
    is_goal(level, state)            -> bool

Usage:
    from src.level_parser import load_level
    from src.bfs_dfs import bfs, dfs

    level = load_level("levels/Level-1.txt")
    result = bfs(level)
    print(result["solution"])        # e.g. "dDD"  (None if unsolved)
    print(result["states_explored"], result["time"], result["length"])

The solution is ONE action string (lowercase = step, UPPERCASE = push), so
it can be replayed with:   python -m src.main --level <file> --replay <solution>

Two modes (argument `mode`):
    "step" (default)  one player step per action. Simple, matches the project
                      plan. BFS gives the fewest total moves.
    "push"            one box push per action (walking included). Far fewer
                      states, so it solves bigger levels. Uses canonical()
                      as the visited key, as Member 1 recommends.
"""
import time
from collections import deque
from typing import Callable, Dict, List, Optional, Tuple

from .level_parser import Level
from .moves import canonical, get_push_successors, get_successors, is_goal
from .state import State

# Result dict keys (share this format with Members 3, 4 and 5):
#   solved           bool
#   solution         str or None    action string, None if not solved
#   length           int            number of player moves (len(solution))
#   pushes           int            number of box pushes (uppercase letters)
#   states_explored  int            states taken out of the queue / stack
#   states_generated int            states created and stored (memory proxy)
#   time             float          seconds
#   reason           str            "solved" | "no solution" | "timeout" | "state limit"
#   method, mode     str


def _make_result(method, mode, solved, solution, explored, generated, t0, reason):
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


def _setup(level: Level, mode: str):
    """Pick the successor function and the visited-key function for a mode."""
    if mode == "step":
        return get_successors, (lambda s: s)
    if mode == "push":
        return get_push_successors, (lambda s: canonical(level, s))
    raise ValueError("mode must be 'step' or 'push'")


def _trace(parent: Dict[State, Optional[Tuple[State, str]]], key: State) -> str:
    """Walk back from the goal key to the start and build the action string."""
    actions: List[str] = []
    while parent[key] is not None:
        key, action = parent[key]
        actions.append(action)
    return "".join(reversed(actions))


def solve(level: Level, method: str = "bfs", mode: str = "step",
          time_limit: float = 60.0, max_states: Optional[int] = None) -> dict:
    """Run BFS or DFS on `level`. See the module docstring for the result dict."""
    if method not in ("bfs", "dfs"):
        raise ValueError("method must be 'bfs' or 'dfs'")
    successors, key_of = _setup(level, mode)

    t0 = time.perf_counter()
    explored = 0
    start = level.start
    start_key = key_of(start)

    def finish(solved, solution, reason):
        return _make_result(method, mode, solved, solution, explored,
                            len(parent), t0, reason)

    # parent[key] = (previous_key, action)  or None for the start.
    # It is also the VISITED SET: a key in parent has been seen already.
    parent: Dict[State, Optional[Tuple[State, str]]] = {start_key: None}

    if is_goal(level, start):
        return finish(True, "", "solved")

    def out_of_budget() -> Optional[str]:
        if max_states is not None and explored > max_states:
            return "state limit"
        if explored % 256 == 0 and time.perf_counter() - t0 > time_limit:
            return "timeout"
        return None

    # ------------------------------ BFS ------------------------------
    if method == "bfs":
        queue = deque([start])                 # FIFO: oldest first
        while queue:
            state = queue.popleft()
            explored += 1
            stop = out_of_budget()
            if stop:
                return finish(False, None, stop)

            for action, nxt, _cost in successors(level, state):
                k = key_of(nxt)
                if k in parent:                # already visited
                    continue
                parent[k] = (key_of(state), action)
                if is_goal(level, nxt):        # first goal found = fewest steps
                    return finish(True, _trace(parent, k), "solved")
                queue.append(nxt)
        return finish(False, None, "no solution")

    # ------------------------------ DFS ------------------------------
    # Stack holds (state, previous_key, action). We mark a state visited when
    # it is POPPED, so every state is expanded at most once.
    parent = {}
    stack: List[Tuple[State, Optional[State], Optional[str]]] = [(start, None, None)]
    while stack:
        state, prev_key, action = stack.pop()  # LIFO: newest first
        k = key_of(state)
        if k in parent:                        # already visited
            continue
        parent[k] = None if prev_key is None else (prev_key, action)
        explored += 1
        stop = out_of_budget()
        if stop:
            return finish(False, None, stop)

        if is_goal(level, state):
            return finish(True, _trace(parent, k), "solved")

        for a, nxt, _cost in successors(level, state):
            if key_of(nxt) not in parent:
                stack.append((nxt, k, a))
    return finish(False, None, "no solution")


def bfs(level: Level, **kw) -> dict:
    return solve(level, "bfs", **kw)


def dfs(level: Level, **kw) -> dict:
    return solve(level, "dfs", **kw)
