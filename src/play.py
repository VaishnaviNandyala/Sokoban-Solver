"""Logic for playing Sokoban by hand (used by the Streamlit app).

No Streamlit import here, so it can be unit-tested.
"""
from dataclasses import dataclass, field, replace
from typing import List, Optional, Tuple

from .astar import astar
from .deadlock import is_deadlock
from .level_parser import Level
from .moves import apply_action, is_goal
from .state import State

WORDS = {"U": "Up", "D": "Down", "L": "Left", "R": "Right"}


@dataclass
class Game:
    level: Level
    state: State = None
    history: List[Tuple[State, bool]] = field(default_factory=list)  # (previous state, was_push)
    moves: int = 0
    pushes: int = 0

    def __post_init__(self):
        if self.state is None:
            self.state = self.level.start

    # --- actions -----------------------------------------------------
    def move(self, action: str) -> bool:
        """Try one step (U/D/L/R). Returns False if the move is illegal."""
        if self.solved:
            return False
        new = apply_action(self.level, self.state, action)
        if new is None:
            return False
        pushed = new.boxes != self.state.boxes
        self.history.append((self.state, pushed))
        self.state = new
        self.moves += 1
        self.pushes += int(pushed)
        return True

    def undo(self) -> bool:
        if not self.history:
            return False
        self.state, pushed = self.history.pop()
        self.moves -= 1
        self.pushes -= int(pushed)
        return True

    def reset(self) -> None:
        self.state = self.level.start
        self.history.clear()
        self.moves = 0
        self.pushes = 0

    # --- status ------------------------------------------------------
    @property
    def solved(self) -> bool:
        return is_goal(self.level, self.state)

    @property
    def stuck(self) -> bool:
        """True if the current position can never be solved (deadlock)."""
        return (not self.solved) and is_deadlock(self.level, self.state)


def hint(level: Level, state: State, time_limit: float = 10.0) -> Optional[str]:
    """Shortest solution from `state` (action string), or None if none found."""
    here = replace(level, start=state)
    res = astar(here, "matching", use_deadlock=True, push_moves=True, time_limit=time_limit)
    return res.solution if res.solved else None
