"""Text rendering, handy for debugging without a GUI."""
from .level_parser import Level
from .state import State


def render(level: Level, state: State) -> str:
    rows = []
    for r in range(level.height):
        row = []
        for c in range(level.width):
            p = (r, c)
            if p in level.walls:
                ch = "#"
            elif p == state.player:
                ch = "+" if p in level.goals else "@"
            elif p in state.boxes:
                ch = "*" if p in level.goals else "$"
            elif p in level.goals:
                ch = "."
            else:
                ch = " "
            row.append(ch)
        rows.append("".join(row).rstrip())
    return "\n".join(rows)
