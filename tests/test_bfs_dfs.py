import glob
import os

import pytest

from src.bfs_dfs import bfs, dfs, solve
from src.level_parser import load_level, parse_level
from src.moves import apply_action, is_goal

LEVELS = os.path.join(os.path.dirname(__file__), "..", "levels")


def lv(name):
    return load_level(os.path.join(LEVELS, name))


def replay(level, solution):
    """Apply the action string with Member 1's engine; return final state or None."""
    state = level.start
    for a in solution:
        state = apply_action(level, state, a)
        if state is None:
            return None
    return state


SOLVABLE = ["Level-14.txt", "Level-01.txt", "Level-2.txt", "Level-03.txt",
            "Level-06.txt"]


@pytest.mark.parametrize("name", SOLVABLE)
@pytest.mark.parametrize("method", ["bfs", "dfs"])
@pytest.mark.parametrize("mode", ["step", "push"])
def test_solution_replays_to_goal(name, method, mode):
    level = lv(name)
    res = solve(level, method, mode=mode, time_limit=30)
    assert res["solved"], res
    final = replay(level, res["solution"])
    assert final is not None and is_goal(level, final)
    assert res["length"] == len(res["solution"])


@pytest.mark.parametrize("name", ["Level-15.txt", "Level-16.txt"])
@pytest.mark.parametrize("method", ["bfs", "dfs"])
@pytest.mark.parametrize("mode", ["step", "push"])
def test_unsolvable_returns_none(name, method, mode):
    res = solve(lv(name), method, mode=mode, time_limit=30)
    assert not res["solved"]
    assert res["solution"] is None
    assert res["reason"] == "no solution"


def test_bfs_is_shortest_in_steps():
    level = lv("Level-01.txt")
    b, d = bfs(level), dfs(level)
    assert b["length"] <= d["length"]


def test_bfs_trivial_level_is_one_push():
    res = bfs(lv("Level-14.txt"))
    assert res["solution"] == "R"
    assert res["pushes"] == 1


def test_already_solved_level():
    level = parse_level("#####\n#@* #\n#####\n")
    res = bfs(level)
    assert res["solved"] and res["solution"] == ""


def test_state_limit_stops_search():
    res = bfs(lv("Level-09.txt"), max_states=50)
    assert not res["solved"] and res["reason"] == "state limit"


def test_time_limit_stops_search():
    res = dfs(lv("Level-10.txt"), time_limit=0.0)
    assert not res["solved"] and res["reason"] == "timeout"


def test_bad_arguments():
    with pytest.raises(ValueError):
        solve(lv("Level-01.txt"), "astar")
    with pytest.raises(ValueError):
        solve(lv("Level-01.txt"), "bfs", mode="jump")
