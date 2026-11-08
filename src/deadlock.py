"""Deadlock detection for Sokoban.

Detects boxes that can never reach any goal.
"""

from collections import deque
from functools import lru_cache

from .level_parser import Level
from .state import Pos, State


DIRECTIONS = [
    (-1, 0),  # Up
    (1, 0),   # Down
    (0, -1),  # Left
    (0, 1),   # Right
]


def add(pos: Pos, direction: Pos) -> Pos:
    return (
        pos[0] + direction[0],
        pos[1] + direction[1]
    )


def is_corner_deadlock(level: Level, box: Pos) -> bool:
    """Check whether a box is stuck in a non-goal corner."""

    if box in level.goals:
        return False

    up = level.is_wall(add(box, (-1, 0)))
    down = level.is_wall(add(box, (1, 0)))
    left = level.is_wall(add(box, (0, -1)))
    right = level.is_wall(add(box, (0, 1)))

    return (up or down) and (left or right)


@lru_cache(maxsize=None)
def _goal_reachable_positions(level: Level) -> frozenset:
    """Find box positions from which a goal can be reached.

    Reverse-push search starts at every goal. Other boxes are
    ignored, making this a safe static dead-square test.
    """

    reachable = set(level.goals)
    queue = deque(level.goals)

    while queue:
        current = queue.popleft()

        for direction in DIRECTIONS:
            previous = (
                current[0] - direction[0],
                current[1] - direction[1]
            )

            player_stand = (
                previous[0] - direction[0],
                previous[1] - direction[1]
            )

            if level.is_wall(previous):
                continue

            if level.is_wall(player_stand):
                continue

            if previous not in reachable:
                reachable.add(previous)
                queue.append(previous)

    return frozenset(reachable)


def is_wall_deadlock(level: Level, box: Pos) -> bool:
    """Check for a box trapped in a non-goal wall dead square."""

    if box in level.goals:
        return False

    if is_corner_deadlock(level, box):
        return False

    adjacent_to_wall = any(
        level.is_wall(add(box, direction))
        for direction in DIRECTIONS
    )

    if not adjacent_to_wall:
        return False

    return box not in _goal_reachable_positions(level)


def is_2x2_deadlock(level: Level, state: State) -> bool:
    """Check whether a 2x2 area is blocked by walls and boxes.

    A blocked 2x2 area is a deadlock if at least one box
    inside it is not already on a goal.
    """

    boxes = state.boxes

    for box in boxes:
        r, c = box

        for row in (r - 1, r):
            for col in (c - 1, c):
                cells = {
                    (row, col),
                    (row + 1, col),
                    (row, col + 1),
                    (row + 1, col + 1),
                }

                blocked = all(
                    level.is_wall(cell) or cell in boxes
                    for cell in cells
                )

                has_unsolved_box = any(
                    cell in boxes and cell not in level.goals
                    for cell in cells
                )

                if blocked and has_unsolved_box:
                    return True

    return False


def is_deadlocked(level: Level, state: State) -> bool:
    """Return True if any box is in a detected deadlock."""

    reachable = _goal_reachable_positions(level)

    if any(box not in reachable for box in state.boxes):
        return True

    return is_2x2_deadlock(level, state)
