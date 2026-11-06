"""Run BFS and DFS on every level and print / save a results table.

    python -m experiments.run_bfs_dfs
    python -m experiments.run_bfs_dfs --time-limit 30 --mode push
    python -m experiments.run_bfs_dfs --levels levels/Level-01.txt levels/Level-04.txt

Writes experiments/results_bfs_dfs.csv (for Member 4's report / graphs).
"""
import argparse
import csv
import glob
import os

from src.bfs_dfs import solve
from src.level_parser import load_level

COLUMNS = ["level", "method", "mode", "solved", "reason", "states_explored",
           "states_generated", "time", "length", "pushes"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", nargs="*", help="level files (default: all in levels/)")
    ap.add_argument("--mode", choices=["step", "push", "both"], default="both")
    ap.add_argument("--time-limit", type=float, default=60.0)
    ap.add_argument("--max-states", type=int, default=None)
    ap.add_argument("--out", default="experiments/results_bfs_dfs.csv")
    args = ap.parse_args()

    files = args.levels or sorted(glob.glob("levels/*.txt"))
    modes = ["step", "push"] if args.mode == "both" else [args.mode]

    rows = []
    print(f"{'level':<16}{'method':<6}{'mode':<6}{'solved':<8}{'explored':>10}"
          f"{'time(s)':>10}{'length':>8}{'pushes':>8}  reason")
    for path in files:
        level = load_level(path)
        name = os.path.splitext(os.path.basename(path))[0]
        for mode in modes:
            for method in ("bfs", "dfs"):
                r = solve(level, method, mode=mode, time_limit=args.time_limit,
                          max_states=args.max_states)
                row = {"level": name, **{k: r[k] for k in COLUMNS if k != "level"}}
                rows.append(row)
                print(f"{name:<16}{method:<6}{mode:<6}{str(r['solved']):<8}"
                      f"{r['states_explored']:>10}{r['time']:>10}{r['length']:>8}"
                      f"{r['pushes']:>8}  {r['reason']}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
