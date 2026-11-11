
from src.level_parser import parse_level
from src.deadlock import (
    is_corner_deadlock,
    is_wall_deadlock,
    is_deadlocked,
    is_2x2_deadlock,
)


def test_corner_deadlock():
    level = parse_level(
        "#####\n"
        "#$ .#\n"
        "#@  #\n"
        "#####"
    )

    box = next(iter(level.start.boxes))

    assert is_corner_deadlock(level, box)
    assert is_deadlocked(level, level.start)


def test_box_on_goal_is_not_deadlocked():
    level = parse_level(
        "#####\n"
        "#* @#\n"
        "#####"
    )

    box = next(iter(level.start.boxes))

    assert not is_corner_deadlock(level, box)
    assert not is_wall_deadlock(level, box)
    assert not is_deadlocked(level, level.start)


def test_box_can_reach_goal():
    level = parse_level(
        "#######\n"
        "#@ $ .#\n"
        "#######"
    )

    box = next(iter(level.start.boxes))

    assert not is_deadlocked(level, level.start)
    assert not is_wall_deadlock(level, box)


def test_2x2_deadlock():
    level = parse_level(
        "########\n"
        "#@.... #\n"
        "# $$   #\n"
        "# $$   #\n"
        "#      #\n"
        "########"
    )

    assert is_2x2_deadlock(level, level.start)
    assert is_deadlocked(level, level.start)
def test_2x2_deadlock_with_goal_inside():
    level = parse_level(
        "########\n"
        "#@     #\n"
        "# *$   #\n"
        "# $$   #\n"
        "#   ...#\n"
        "########"
    )

    assert is_2x2_deadlock(level, level.start)


def test_2x2_boxes_all_on_goals():
    level = parse_level(
        "######\n"
        "#@   #\n"
        "# ** #\n"
        "# ** #\n"
        "#    #\n"
        "######"
    )

    assert not is_2x2_deadlock(level, level.start)
