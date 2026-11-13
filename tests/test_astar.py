import pytest

from src.astar import astar
from src.baselines import uninformed_search
from src.deadlock import dead_squares, is_deadlock
from src.heuristics import HEURISTICS, h_matching, h_sum_distance
from src.level_parser import parse_level
from src.moves import is_goal
from src.runner import CONFIGS, run_config, solution_states
from src.state import State

EASY = "#####\n# @ #\n# $ #\n# . #\n#####\n"
TWO = "#######\n#.    #\n#  $  #\n# @$  #\n#  .  #\n#######\n"
MED = "#######\n#     #\n# $ $ #\n#  @  #\n# .   #\n#   . #\n#######\n"
CORNER = "#####\n#$ .#\n# @ #\n#####\n"
WALL = "#######\n# $   #\n#@    #\n#    .#\n#######\n"


def reaches_goal(level, res):
    return is_goal(level, solution_states(level, res.solution)[-1])


# ---------------- heuristics ----------------
def test_heuristic_zero_at_goal():
    level = parse_level("#####\n#@$.#\n#####\n")
    solved = State((1, 2), frozenset({(1, 3)}))
    for h in HEURISTICS.values():
        assert h(level, solved) == 0


def test_heuristic_values():
    level = parse_level(EASY)
    assert h_sum_distance(level, level.start) == 1
    assert h_matching(level, level.start) == 1


def test_matching_at_least_sum():
    level = parse_level(MED)
    assert h_matching(level, level.start) >= h_sum_distance(level, level.start)


@pytest.mark.parametrize("text", [EASY, TWO, MED])
def test_heuristics_admissible(text):
    level = parse_level(text)
    optimal = astar(level, "zero", use_deadlock=False, push_moves=False).moves
    for name in ("sum", "matching"):
        assert HEURISTICS[name](level, level.start) <= optimal


# ---------------- deadlock ----------------
def test_corner_is_dead_square():
    level = parse_level(CORNER)
    assert (1, 1) in dead_squares(level)
    assert is_deadlock(level, level.start)


def test_goal_square_is_never_dead():
    level = parse_level(MED)
    assert not (level.goals & dead_squares(level))


def test_wall_deadlock():
    level = parse_level(WALL)
    assert is_deadlock(level, level.start)       # top-wall box, goal not on that wall


def test_2x2_freeze():
    level = parse_level("#######\n#@    #\n#     #\n# $$  #\n# $$  #\n#  ...#\n#   . #\n#######\n")
    frozen = State((1, 1), frozenset({(3, 2), (3, 3), (4, 2), (4, 3)}))
    assert is_deadlock(level, frozen)


def test_start_of_solvable_not_deadlock():
    for text in (EASY, TWO, MED):
        level = parse_level(text)
        assert not is_deadlock(level, level.start)


# ---------------- A* ----------------
@pytest.mark.parametrize("text", [EASY, TWO, MED])
@pytest.mark.parametrize("push", [True, False])
def test_astar_solves_and_replays(text, push):
    level = parse_level(text)
    res = astar(level, "sum", use_deadlock=True, push_moves=push)
    assert res.solved and res.solution
    assert reaches_goal(level, res)
    assert res.moves == len(res.solution)


@pytest.mark.parametrize("text", [TWO, MED])
def test_astar_optimal_vs_bfs_steps(text):
    level = parse_level(text)
    bfs = uninformed_search(level, "bfs", push_moves=False)
    for h in ("sum", "matching"):
        for push in (True, False):
            res = astar(level, h, use_deadlock=True, push_moves=push)
            assert res.moves == bfs.moves        # A* finds a shortest solution


@pytest.mark.parametrize("text", [CORNER, WALL])
def test_astar_unsolvable(text):
    level = parse_level(text)
    res = astar(level, "sum", use_deadlock=True)
    assert not res.solved and res.status == "unsolvable" and res.solution is None
    res2 = astar(level, "sum", use_deadlock=False)      # still correct without pruning
    assert res2.status == "unsolvable"


def test_deadlock_pruning_reduces_nodes():
    level = parse_level(MED)
    a = astar(level, "sum", use_deadlock=False, push_moves=True)
    b = astar(level, "sum", use_deadlock=True, push_moves=True)
    assert b.nodes_expanded <= a.nodes_expanded


def test_node_limit():
    level = parse_level(MED)
    res = astar(level, "zero", use_deadlock=False, push_moves=False, max_nodes=256)
    assert res.status in ("node_limit", "solved")


# ---------------- baselines + runner ----------------
@pytest.mark.parametrize("kind", ["bfs", "dfs"])
def test_baselines_solve(kind):
    level = parse_level(TWO)
    res = uninformed_search(level, kind)
    assert res.solved and reaches_goal(level, res)


def test_dfs_not_shorter_than_bfs():
    level = parse_level(MED)
    assert uninformed_search(level, "dfs").moves >= uninformed_search(level, "bfs").moves


def test_all_configs_run():
    level = parse_level(TWO)
    for label in CONFIGS:
        res = run_config(level, label, time_limit=10)
        assert res.solved, label
        assert reaches_goal(level, res)


# ---------------- weighted A* and greedy ----------------
@pytest.mark.parametrize("text", [EASY, TWO, MED])
def test_weight_one_equals_astar(text):
    level = parse_level(text)
    a = astar(level, "matching")
    b = astar(level, "matching", weight=1.0)
    assert (a.moves, a.nodes_expanded) == (b.moves, b.nodes_expanded)


@pytest.mark.parametrize("text", [TWO, MED])
def test_weighted_and_greedy_solve_and_replay(text):
    level = parse_level(text)
    optimal = astar(level, "matching").moves
    for res in (astar(level, "matching", weight=3), astar(level, "matching", greedy=True)):
        assert res.solved and reaches_goal(level, res)
        assert res.moves >= optimal          # never shorter than the shortest solution


@pytest.mark.parametrize("text", [CORNER, WALL])
def test_greedy_unsolvable(text):
    level = parse_level(text)
    res = astar(level, "matching", greedy=True)
    assert not res.solved and res.status == "unsolvable"
