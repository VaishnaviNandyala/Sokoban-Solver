import glob
import os
from collections import deque

import pytest

from src.level_parser import load_level, parse_level
from src.moves import (apply_action, canonical, get_push_successors,
                       get_successors, is_goal)
from src.render import render
from src.state import State

LEVELS = os.path.join(os.path.dirname(__file__), "..", "levels")


def lv(name):
    return load_level(os.path.join(LEVELS, name))


# ---------------- parser ----------------
def test_parse_basic():
    level = parse_level("#####\n#@$.#\n#####\n")
    assert level.start.player == (1, 1)
    assert level.start.boxes == frozenset({(1, 2)})
    assert level.goals == frozenset({(1, 3)})
    assert (0, 0) in level.walls


def test_parse_box_and_player_on_goal():
    level = parse_level("#######\n#+ $ *#\n#######\n")
    assert level.start.player == (1, 1)
    assert level.start.boxes == frozenset({(1, 3), (1, 5)})
    assert level.goals == frozenset({(1, 1), (1, 5)})


def test_parse_errors():
    with pytest.raises(ValueError):
        parse_level("###\n# #\n###\n")            # no player
    with pytest.raises(ValueError):
        parse_level("####\n#@@$.#\n####\n")       # two players
    with pytest.raises(ValueError):
        parse_level("#####\n#@$ #\n#####\n")      # box without goal
    with pytest.raises(ValueError):
        parse_level("#####\n#@x.#\n#####\n")      # bad symbol


def test_all_level_files_load():
    files = glob.glob(os.path.join(LEVELS, "*.txt"))
    assert len(files) >= 5
    for f in files:
        load_level(f)


# ---------------- state ----------------
def test_state_hashable_and_equal():
    a = State((1, 1), frozenset({(2, 2)}))
    b = State((1, 1), frozenset({(2, 2)}))
    assert a == b and hash(a) == hash(b)
    assert len({a, b}) == 1


# ---------------- moves ----------------
def test_plain_move_and_wall_block():
    level = lv("Level-01.txt")
    s = level.start                      # player (1,2), box (2,2)
    assert apply_action(level, s, "U") is None       # wall above
    s2 = apply_action(level, s, "L")
    assert s2.player == (1, 1) and s2.boxes == s.boxes


def test_push_box():
    level = lv("Level-01.txt")
    s = apply_action(level, level.start, "D")
    assert s.player == (2, 2)
    assert s.boxes == frozenset({(3, 2)})


def test_push_into_wall_illegal():
    level = lv("Level-01.txt")
    s = apply_action(level, level.start, "D")   # box now on goal (3,2)
    assert apply_action(level, s, "D") is None  # box would hit wall at (4,2)


def test_push_box_into_box_illegal():
    level = parse_level("#######\n#@$$ .#\n#   . #\n#######\n")
    assert apply_action(level, level.start, "R") is None


def test_goal_test():
    level = lv("Level-01.txt")
    assert not is_goal(level, level.start)
    assert is_goal(level, apply_action(level, level.start, "D"))


def test_successor_letters():
    level = lv("Level-01.txt")
    acts = {a for a, _, _ in get_successors(level, level.start)}
    assert "D" in acts       # uppercase = push
    assert "l" in acts and "r" in acts   # lowercase = plain step
    assert all(c == 1 for _, _, c in get_successors(level, level.start))


def test_render_roundtrip():
    text = "#####\n# @ #\n# $ #\n# . #\n#####"
    level = parse_level(text)
    assert render(level, level.start) == text


# ---------------- push successors ----------------
def test_push_successors_replayable():
    level = lv("Level-04.txt")
    for action, new, cost in get_push_successors(level, level.start):
        s = level.start
        for a in action:
            s = apply_action(level, s, a)
            assert s is not None
        assert s == new and cost == len(action)


def test_canonical_same_region():
    level = lv("Level-01.txt")
    a = level.start
    b = apply_action(level, a, "L")
    assert canonical(level, a) == canonical(level, b)


# ---------------- reference BFS (sanity check for the engine only) ----------------
def bfs(level, limit=300000):
    start = level.start
    seen, q = {start}, deque([(start, "")])
    while q and len(seen) < limit:
        s, path = q.popleft()
        if is_goal(level, s):
            return path
        for a, n, _ in get_successors(level, s):
            if n not in seen:
                seen.add(n)
                q.append((n, path + a))
    return None


@pytest.mark.parametrize("name", ["Level-14.txt", "Level-01.txt",
                                  "Level-04.txt", "Level-05.txt"])
def test_solvable_levels_are_solvable(name):
    level = lv(name)
    path = bfs(level)
    assert path is not None
    s = level.start
    for a in path:
        s = apply_action(level, s, a)
    assert is_goal(level, s)


def test_unsolvable_level():
    assert bfs(lv("Level-15.txt")) is None
