"""Small CLI for Member 1's engine.

    python -m src.main --level levels/Level-1.txt
    python -m src.main --level levels/Level-1.txt --replay D
"""
import argparse

from .level_parser import load_level
from .moves import apply_action, is_goal
from .render import render


def main() -> None:
    ap = argparse.ArgumentParser(description="Sokoban engine demo")
    ap.add_argument("--level", required=True)
    ap.add_argument("--replay", default="", help="action string, e.g. 'uurDD'")
    args = ap.parse_args()

    level = load_level(args.level)
    state = level.start
    print(render(level, state))

    for i, a in enumerate(args.replay, 1):
        new = apply_action(level, state, a)
        if new is None:
            print(f"\nIllegal move '{a}' at step {i}")
            return
        state = new
        print(f"\nStep {i}: {a}")
        print(render(level, state))

    if args.replay:
        print("\nSOLVED!" if is_goal(level, state) else "\nNot solved yet.")


if __name__ == "__main__":
    main()
