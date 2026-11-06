import glob
import os

import pytest

from src.astar import solve_astar
from src.bfs_dfs import bfs
from src.level_parser import load_level, parse_level
from src.moves import apply_action, is_goal

LEVELS = os.path.join(os.path.dirname(__file__), "..", "levels")
FILES = sorted(glob.glob(os.path.join(LEVELS, "*.txt")))
BFS_LIMIT = 20000 


def replay(level, solution):
    state = level.start
    for action in solution:
        state = apply_action(level, state, action)
        assert state is not None, "illegal move %r in the solution" % action
    return state


def reference(path):
    level = load_level(path)
    ref = bfs(level, max_states=BFS_LIMIT, time_limit=10)
    if ref["reason"] in ("state limit", "timeout"):
        pytest.skip("too big for the BFS reference")
    return level, ref


@pytest.mark.parametrize("path", FILES, ids=os.path.basename)
@pytest.mark.parametrize("heuristic", ["simple", "matching"])
def test_step_mode_is_as_short_as_bfs(path, heuristic):
    level, ref = reference(path)
    res = solve_astar(level, mode="step", heuristic=heuristic, time_limit=20)
    if not ref["solved"]:
        assert res["reason"] == "no solution"
        return
    assert res["solved"]
    assert is_goal(level, replay(level, res["solution"]))
    assert res["length"] == ref["length"]        

@pytest.mark.parametrize("path", FILES, ids=os.path.basename)
def test_push_mode_replays_to_goal(path):
    level, ref = reference(path)
    res = solve_astar(level, mode="push", time_limit=20)
    if not ref["solved"]:
        assert res["reason"] == "no solution"
        return
    assert res["solved"]
    assert is_goal(level, replay(level, res["solution"]))
    assert res["length"] >= ref["length"]        

def test_matching_never_explores_more_than_simple_on_small_level():
    level = parse_level("#######\n#.    #\n#  $  #\n# @$  #\n#  .  #\n#######\n")
    a = solve_astar(level, mode="step", heuristic="simple")
    b = solve_astar(level, mode="step", heuristic="matching")
    assert a["length"] == b["length"]
    assert b["states_explored"] <= a["states_explored"]


def test_state_limit_stops_search():
    level = parse_level("#######\n#.    #\n#  $  #\n# @$  #\n#  .  #\n#######\n")
    res = solve_astar(level, mode="step", max_states=5)
    assert not res["solved"] and res["reason"] == "state limit"


def test_deadlock_hook_is_used():
    level = parse_level("#####\n# @ #\n# $ #\n# . #\n#####\n")
    res = solve_astar(level, deadlock=lambda lv, st: True) 
    assert not res["solved"] and res["reason"] == "no solution"


def test_bad_arguments():
    level = parse_level("#####\n# @ #\n# $ #\n# . #\n#####\n")
    with pytest.raises(ValueError):
        solve_astar(level, mode="jump")
    with pytest.raises(ValueError):
        solve_astar(level, heuristic="magic")
