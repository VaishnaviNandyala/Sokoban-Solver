"""Level loading.

File format (standard Sokoban symbols):
    #  wall            @  player            +  player on goal
    $  box             *  box on goal       .  goal
    (space) floor
"""
from dataclasses import dataclass
from typing import FrozenSet

from .state import Pos, State


@dataclass(frozen=True)
class Level:
    walls: FrozenSet[Pos]
    goals: FrozenSet[Pos]
    start: State
    height: int
    width: int

    def is_wall(self, pos: Pos) -> bool:
        """Out-of-bounds counts as wall, so open-edged levels are safe."""
        r, c = pos
        if r < 0 or c < 0 or r >= self.height or c >= self.width:
            return True
        return pos in self.walls


def parse_level(text: str) -> Level:
    lines = text.rstrip("\n").split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        raise ValueError("Empty level")

    width = max(len(line) for line in lines)
    walls, goals, boxes = set(), set(), set()
    player = None

    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            pos = (r, c)
            if ch == "#":
                walls.add(pos)
            elif ch == ".":
                goals.add(pos)
            elif ch == "$":
                boxes.add(pos)
            elif ch == "*":
                boxes.add(pos)
                goals.add(pos)
            elif ch in "@+":
                if player is not None:
                    raise ValueError("Level has more than one player")
                player = pos
                if ch == "+":
                    goals.add(pos)
            elif ch == " ":
                pass
            else:
                raise ValueError(f"Unknown symbol {ch!r} at {pos}")

    if player is None:
        raise ValueError("Level has no player")
    if len(boxes) != len(goals):
        raise ValueError(f"{len(boxes)} boxes but {len(goals)} goals")

    return Level(
        walls=frozenset(walls),
        goals=frozenset(goals),
        start=State(player, frozenset(boxes)),
        height=len(lines),
        width=width,
    )


def load_level(path: str) -> Level:
    with open(path, encoding="utf-8") as f:
        return parse_level(f.read())
