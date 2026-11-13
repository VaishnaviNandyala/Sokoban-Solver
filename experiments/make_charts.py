"""Make the report charts and a summary table from experiments/results_all.csv.

    python -m experiments.make_charts
Writes PNG files to results/charts/ and results/results_summary.csv.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CSV = "experiments/results_all.csv"
OUT = "results/charts"


def natural(level):
    return int(level.split("-")[-1])


def main():
    os.makedirs(OUT, exist_ok=True)
    df = pd.read_csv(CSV)
    configs = list(dict.fromkeys(df["config"]))
    levels = sorted(df["level"].unique(), key=natural)
    cmap = plt.get_cmap("tab10")
    colors = {c: cmap(i) for i, c in enumerate(configs)}
    solved = df[df["status"] == "solved"]
    unsolvable_levels = sorted(set(df[df["status"] == "unsolvable"]["level"]), key=natural)
    plot_levels = [l for l in levels if l not in unsolvable_levels]
    x = np.arange(len(plot_levels))
    width = 0.8 / len(configs)

    def grouped(ax, column, cfgs, ylabel, title, mark_timeouts=True):
        w = 0.8 / len(cfgs)
        for i, c in enumerate(cfgs):
            vals, tmo = [], []
            for l in plot_levels:
                r = df[(df.level == l) & (df.config == c)].iloc[0]
                vals.append(r[column] if r["status"] == "solved" else np.nan)
                tmo.append(r["status"] != "solved")
            pos = x - 0.4 + w * (i + 0.5)
            ax.bar(pos, vals, w, label=c, color=colors[c])
            if mark_timeouts:
                for p, t in zip(pos, tmo):
                    if t:
                        ax.plot(p, 1, marker="x", color=colors[c], markersize=5)
        ax.set_yscale("log")
        ax.set_xticks(x)
        ax.set_xticklabels([l.replace("Level-", "L") for l in plot_levels])
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.3)

    # 1. nodes expanded
    fig, ax = plt.subplots(figsize=(14, 5.5))
    grouped(ax, "nodes_expanded", configs, "nodes expanded (log scale)",
            "Nodes expanded per level (x = not solved within the time limit)")
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout(); fig.savefig(f"{OUT}/nodes_expanded.png", dpi=150); plt.close(fig)

    # 2. solution length
    fig, ax = plt.subplots(figsize=(14, 5.5))
    grouped(ax, "moves", configs, "moves in the solution (log scale)",
            "Solution length per level (shorter is better)")
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout(); fig.savefig(f"{OUT}/solution_length.png", dpi=150); plt.close(fig)

    # 3. time
    fig, ax = plt.subplots(figsize=(14, 5.5))
    grouped(ax, "time_sec", configs, "time in seconds (log scale)",
            "Running time per level (x = not solved within the time limit)")
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout(); fig.savefig(f"{OUT}/time.png", dpi=150); plt.close(fig)

    # 4. summary: levels solved + total nodes on levels every config solved
    common = [l for l in levels if all(
        ((df.level == l) & (df.config == c) & (df.status == "solved")).any() for c in configs)]
    summary = []
    for c in configs:
        sub = df[df.config == c]
        summary.append({
            "config": c,
            "levels_solved": int((sub.status == "solved").sum()),
            "unsolvable_detected": int((sub.status == "unsolvable").sum()),
            "timeouts": int((sub.status == "timeout").sum()),
            "common_levels_total_nodes": int(sub[sub.level.isin(common)].nodes_expanded.sum()),
            "common_levels_total_time_s": round(float(sub[sub.level.isin(common)].time_sec.sum()), 2),
        })
    sm = pd.DataFrame(summary)
    os.makedirs("results", exist_ok=True)
    sm.to_csv("results/results_summary.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ypos = np.arange(len(configs))
    axes[0].barh(ypos, sm["levels_solved"], color=[colors[c] for c in configs])
    axes[0].set_yticks(ypos); axes[0].set_yticklabels(configs, fontsize=8)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("levels solved")
    axes[0].set_title(f"Levels solved (of {len(levels) - len(unsolvable_levels)} solvable)")
    axes[1].barh(ypos, sm["common_levels_total_nodes"], color=[colors[c] for c in configs])
    axes[1].set_yticks(ypos); axes[1].set_yticklabels([])
    axes[1].invert_yaxis(); axes[1].set_xscale("log")
    axes[1].set_xlabel("total nodes expanded (log scale)")
    axes[1].set_title(f"Total nodes on the {len(common)} levels all configs solved")
    fig.tight_layout(); fig.savefig(f"{OUT}/summary.png", dpi=150); plt.close(fig)

    print("Saved charts to", OUT, "and results/results_summary.csv")
    print(sm.to_string(index=False))


if __name__ == "__main__":
    main()
