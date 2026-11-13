"""Run every algorithm configuration on every level and save a CSV (Member 5).

    python -m experiments.run_all                          # all levels, all configs
    python -m experiments.run_all --time-limit 30
    python -m experiments.run_all --repeats 3              # median time of 3 runs
    python -m experiments.run_all --levels levels/Level-1.txt levels/Level-2.txt

Run only some configurations and keep the other rows of the CSV:
    python -m experiments.run_all --configs "WA*" "Greedy" --merge --time-limit 30
(--configs matches by substring of the configuration name.)
"""
import argparse
import csv
import glob
import os
import re
import statistics

from src.level_parser import load_level
from src.moves import is_goal
from src.runner import CONFIGS, run_config, solution_states

FIELDS = ["level", "config", "status", "solved", "moves", "pushes",
          "nodes_expanded", "nodes_generated", "time_sec"]


def natural_key(path):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", os.path.basename(path))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", nargs="*", help="level files (default: levels/*.txt)")
    ap.add_argument("--configs", nargs="*", help="only configs whose name contains one of these")
    ap.add_argument("--merge", action="store_true",
                    help="keep existing rows of --out that are not re-run")
    ap.add_argument("--out", default="experiments/results_all.csv")
    ap.add_argument("--time-limit", type=float, default=10.0, help="seconds per run")
    ap.add_argument("--repeats", type=int, default=1,
                    help="runs per level/config; the median time is saved")
    ap.add_argument("--max-nodes", type=int, default=None)
    args = ap.parse_args()

    files = args.levels or sorted(glob.glob("levels/*.txt"), key=natural_key)
    labels = [c for c in CONFIGS
              if not args.configs or any(a.lower() in c.lower() for a in args.configs)]
    if not labels:
        raise SystemExit("No configuration matches --configs")

    rows = []
    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        level = load_level(path)
        for label in labels:
            results = [run_config(level, label, args.time_limit, args.max_nodes)
                       for _ in range(max(1, args.repeats))]
            res = results[0]
            if res.solved:  # sanity check: replay must reach the goal
                assert is_goal(level, solution_states(level, res.solution)[-1]), (name, label)
            t = round(statistics.median(r.time_sec for r in results), 4)
            rows.append({"level": name, "config": label, "status": res.status,
                         "solved": res.solved, "moves": res.moves, "pushes": res.pushes,
                         "nodes_expanded": res.nodes_expanded,
                         "nodes_generated": res.nodes_generated, "time_sec": t})
            print(f"{name:10s} {label:32s} {res.status:10s} moves={res.moves:<4d} "
                  f"nodes={res.nodes_expanded:<8d} {t}s")

    if args.merge and os.path.exists(args.out):
        done = {(r["level"], r["config"]) for r in rows}
        with open(args.out, newline="", encoding="utf-8") as f:
            old = [r for r in csv.DictReader(f) if (r["level"], r["config"]) not in done]
        rows = old + rows
        order = {c: i for i, c in enumerate(CONFIGS)}
        rows.sort(key=lambda r: (natural_key(r["level"]), order.get(r["config"], 99)))

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
