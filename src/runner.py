"""One place that knows every algorithm configuration.

Used by experiments/run_all.py and by app.py so both always agree.
"""
from .astar import astar
from .baselines import uninformed_search
from .moves import apply_action
from .state import State

# label -> settings. Order matters: it is the order of the report table.
CONFIGS = {
    "BFS (steps)":                  dict(kind="bfs",   heuristic=None,       push_moves=False, deadlock=False),
    "DFS (steps)":                  dict(kind="dfs",   heuristic=None,       push_moves=False, deadlock=False),
    "A* sum (steps)":               dict(kind="astar", heuristic="sum",      push_moves=False, deadlock=False),
    "A* sum (pushes)":              dict(kind="astar", heuristic="sum",      push_moves=True,  deadlock=False),
    "A* sum (pushes+deadlock)":     dict(kind="astar", heuristic="sum",      push_moves=True,  deadlock=True),
    "A* matching (pushes+deadlock)": dict(kind="astar", heuristic="matching", push_moves=True,  deadlock=True),
    "WA* w=3 (pushes+deadlock)":    dict(kind="wastar", heuristic="matching", push_moves=True,  deadlock=True, weight=3),
    "Greedy (pushes+deadlock)":     dict(kind="greedy", heuristic="matching", push_moves=True,  deadlock=True),
}


def run_custom(level, kind, heuristic="sum", push_moves=True, deadlock=True,
               time_limit=10, max_nodes=None, weight=3):
    """kind: bfs | dfs | astar | wastar (weighted A*, uses `weight`) | greedy."""
    if kind == "astar":
        return astar(level, heuristic=heuristic, use_deadlock=deadlock,
                     push_moves=push_moves, time_limit=time_limit, max_nodes=max_nodes)
    if kind == "wastar":
        return astar(level, heuristic=heuristic, use_deadlock=deadlock,
                     push_moves=push_moves, time_limit=time_limit, max_nodes=max_nodes,
                     weight=weight)
    if kind == "greedy":
        return astar(level, heuristic=heuristic, use_deadlock=deadlock,
                     push_moves=push_moves, time_limit=time_limit, max_nodes=max_nodes,
                     greedy=True)
    return uninformed_search(level, strategy=kind, use_deadlock=deadlock,
                             push_moves=push_moves, time_limit=time_limit, max_nodes=max_nodes)


def run_config(level, label, time_limit=10, max_nodes=None):
    c = CONFIGS[label]
    return run_custom(level, c["kind"], c["heuristic"], c["push_moves"],
                      c["deadlock"], time_limit, max_nodes, c.get("weight", 3))


def solution_states(level, solution):
    """List of States after 0, 1, 2, ... actions (for replay in the GUI)."""
    states = [level.start]
    s = level.start
    for a in solution or "":
        s = apply_action(level, s, a)
        if s is None:
            raise ValueError(f"Illegal action {a!r} in solution")
        states.append(s)
    return states
