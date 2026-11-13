"""Shared result object returned by every solver (BFS, DFS, A*)."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class SearchResult:
    algorithm: str
    solved: bool
    status: str                 # "solved" | "unsolvable" | "timeout" | "node_limit"
    solution: Optional[str]     # action string, replayable with apply_action
    moves: int                  # len(solution), 0 if not solved
    pushes: int                 # number of uppercase letters (box pushes)
    nodes_expanded: int
    nodes_generated: int
    time_sec: float

    def as_dict(self):
        return asdict(self)


def make_result(algorithm, status, solution, expanded, generated, t0, now):
    solved = status == "solved"
    return SearchResult(
        algorithm=algorithm,
        solved=solved,
        status=status,
        solution=solution if solved else None,
        moves=len(solution) if solved else 0,
        pushes=sum(1 for c in solution if c.isupper()) if solved else 0,
        nodes_expanded=expanded,
        nodes_generated=generated,
        time_sec=round(now - t0, 4),
    )
