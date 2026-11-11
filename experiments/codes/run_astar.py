import argparse
import csv
import glob
import os
from src.deadlock import is_deadlocked
from src.astar import solve_astar
from src.level_parser import load_level

COLUMNS = ["level", "method", "mode", "solved", "reason", "states_explored",
           "states_generated", "time", "length", "pushes"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", nargs="*", help="level files (default: all in levels/)")
    ap.add_argument("--mode", choices=["step", "push", "both"], default="both")
    ap.add_argument("--heuristics", nargs="+", default=["simple", "matching"],
                    choices=["simple", "matching"])
    ap.add_argument("--time-limit", type=float, default=60.0)
    ap.add_argument("--max-states", type=int, default=None)
    ap.add_argument("--deadlock", action="store_true",
                help="Enable deadlock detection")
    ap.add_argument("--out", default="experiments/results_astar.csv")
    args = ap.parse_args()

    files = args.levels or sorted(glob.glob("levels/*.txt"))
    modes = ["step", "push"] if args.mode == "both" else [args.mode]

    rows = []
    for path in files:
        level = load_level(path)
        name = os.path.splitext(os.path.basename(path))[0]
        for mode in modes:
            for heuristic in args.heuristics:
                r = solve_astar(level, mode=mode, heuristic=heuristic,
                time_limit=args.time_limit,
                max_states=args.max_states,
                deadlock=is_deadlocked if args.deadlock else None)
                rows.append({"level": name, **{k: r[k] for k in COLUMNS if k != "level"}})
                print(f"{name:<12}{r['method']:<16}{mode:<6}{str(r['solved']):<7}"
                      f"{r['states_explored']:>9}{r['time']:>9}{r['length']:>6}  {r['reason']}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()