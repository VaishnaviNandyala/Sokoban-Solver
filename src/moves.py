"""Move rules and successor generation.

Action letters: U D L R.
    lowercase (u d l r) = plain step
    UPPERCASE (U D L R) = step that pushed a box
Boxes can only be pushed, never pulled.

Two successor functions are provided:
    get_successors       - one player step per action (simple, cost 1)
    get_push_successors  - one box push per action (walking included in cost);
                           far fewer states, recommended for A*.
"""
from collections import deque
from typing import Dict, List, Optional, Tuple

from .level_parser import Level
from .state import Pos, State

DIRECTIONS: Dict[str, Pos] = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}

Successor = Tuple[str, State, int]  # (action(s), next_state, cost)


def _add(p: Pos, d: Pos) -> Pos:
    return (p[0] + d[0], p[1] + d[1])


def is_goal(level: Level, state: State) -> bool:
    return state.boxes == level.goals


def apply_action(level: Level, state: State, action: str) -> Optional[State]:
    """Apply one step. Returns the new State, or None if the move is illegal."""
    d = DIRECTIONS[action.upper()]
    nxt = _add(state.player, d)
    if level.is_wall(nxt):
        return None
    if nxt in state.boxes:
        beyond = _add(nxt, d)
        if level.is_wall(beyond) or beyond in state.boxes:
            return None
        return State(nxt, (state.boxes - {nxt}) | {beyond})
    return State(nxt, state.boxes)


def get_successors(level: Level, state: State) -> List[Successor]:
    """All legal single steps from `state`. Cost is 1 per step."""
    out: List[Successor] = []
    for name in DIRECTIONS:
        new = apply_action(level, state, name)
        if new is None:
            continue
        pushed = new.boxes != state.boxes
        out.append((name if pushed else name.lower(), new, 1))
    return out


# ----------------------- push-based search (bonus) -----------------------

def reachable(level: Level, state: State) -> Dict[Pos, str]:
    """Cells the player can walk to without pushing; maps cell -> path string."""
    paths: Dict[Pos, str] = {state.player: ""}
    queue = deque([state.player])
    while queue:
        cur = queue.popleft()
        for name, d in DIRECTIONS.items():
            nxt = _add(cur, d)
            if nxt in paths or level.is_wall(nxt) or nxt in state.boxes:
                continue
            paths[nxt] = paths[cur] + name.lower()
            queue.append(nxt)
    return paths


def canonical(level: Level, state: State) -> State:
    """Same state with the player moved to the top-left cell of its region.

    Use this as the `visited` key in push-based search: two states with the
    same boxes and the same reachable region are the same puzzle position.
    """
    return State(min(reachable(level, state)), state.boxes)


def get_push_successors(level: Level, state: State) -> List[Successor]:
    """All legal box pushes. Action is the full walk + push, e.g. 'uurR'.

    Cost = number of player steps (walk + push), so total cost equals the
    total move count of the final solution.
    """
    out: List[Successor] = []
    paths = reachable(level, state)
    for box in state.boxes:
        for name, d in DIRECTIONS.items():
            stand = (box[0] - d[0], box[1] - d[1])  # player must stand here
            beyond = _add(box, d)
            if stand not in paths:
                continue
            if level.is_wall(beyond) or beyond in state.boxes:
                continue
            walk = paths[stand]
            new = State(box, (state.boxes - {box}) | {beyond})
            out.append((walk + name, new, len(walk) + 1))
    return out
