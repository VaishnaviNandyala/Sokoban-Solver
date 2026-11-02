"""Game state for Sokoban.

A State is immutable and hashable, so solvers can put it directly in
`visited` sets, dicts and priority queues. Walls and goals never change,
so they live in the Level object (see level_parser.py), not in the State.
"""
from typing import FrozenSet, NamedTuple, Tuple

Pos = Tuple[int, int]  # (row, col), row 0 is the top line of the level file


class State(NamedTuple):
    player: Pos
    boxes: FrozenSet[Pos]
