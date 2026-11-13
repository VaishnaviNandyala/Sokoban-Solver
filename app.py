"""Sokoban Solver - game-style Streamlit app.

Run:  streamlit run app.py
Everything (level, algorithm, options, Run solver) is on the main screen.
"""
import glob
import os
import re
import time

import pandas as pd
import streamlit as st

from src.heuristics import HEURISTICS
from src.level_parser import load_level
from src.runner import CONFIGS, run_config, run_custom, solution_states
from src.viz import board_html

st.set_page_config(page_title="Sokoban Solver", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1400px;}
div[data-testid="stMetric"] {
    background: rgba(128,128,128,0.12);
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 12px; padding: 12px 16px;
}
.board-wrap {display: flex; justify-content: center; padding: 8px 0 12px;}
</style>
""", unsafe_allow_html=True)


def natural_key(path):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", os.path.basename(path))]


level_files = sorted(glob.glob("levels/*.txt"), key=natural_key)
if not level_files:
    st.error("No level files found in levels/")
    st.stop()

if st.session_state.get("level_select") not in level_files:
    st.session_state["level_select"] = level_files[0]


def go_level(delta):
    cur = level_files.index(st.session_state["level_select"])
    st.session_state["level_select"] = level_files[max(0, min(len(level_files) - 1, cur + delta))]


def step_by(delta, last, key):
    st.session_state[key] = max(0, min(last, st.session_state.get(key, 0) + delta))


# ===================== top bar: title + level chooser =====================
st.title("Sokoban Solver")
st.caption("Push every box onto a goal. Boxes can only be pushed, never pulled.")

c_prev, c_level, c_next, _ = st.columns([1.2, 2.5, 1.2, 5])
idx_now = level_files.index(st.session_state["level_select"])
c_prev.button("Previous level", key="prev_level", on_click=go_level, args=(-1,),
              disabled=idx_now == 0, use_container_width=True)
level_path = c_level.selectbox("Level", level_files, key="level_select",
                               format_func=lambda p: os.path.basename(p),
                               label_visibility="collapsed")
level_idx = level_files.index(level_path)
c_next.button("Next level", key="next_level", on_click=go_level, args=(1,),
              disabled=level_idx == len(level_files) - 1, type="primary",
              use_container_width=True)

level = load_level(level_path)
level_name = os.path.splitext(os.path.basename(level_path))[0]
st.subheader(f"{level_name}  ({level_idx + 1} of {len(level_files)})")

# ===================== settings panel =====================
with st.container(border=True):
    a, b, c, d, e, f = st.columns([2.2, 2, 1.7, 1.7, 2.2, 1.5], vertical_alignment="bottom")
    algo = a.radio("Search algorithm", ["BFS", "DFS", "A*", "Greedy"], index=2, horizontal=True, key="algo")
    heuristic = b.selectbox("Heuristic (A* / Greedy)", list(HEURISTICS), index=1,
                            disabled=algo not in ("A*", "Greedy"), key="heuristic")
    push_moves = c.checkbox("Push-based moves", value=True, key="push_moves")
    deadlock = d.checkbox("Prune deadlocks", value=True, key="deadlock")
    time_limit = e.slider("Time limit (seconds)", 1, 60, 10, key="time_limit")
    run = f.button("Run solver", type="primary", key="run_solver", use_container_width=True)

if run:
    with st.spinner("Searching..."):
        res_new = run_custom(level, {"BFS": "bfs", "DFS": "dfs", "A*": "astar", "Greedy": "greedy"}[algo], heuristic,
                             push_moves, deadlock, time_limit)
    st.session_state["run_id"] = st.session_state.get("run_id", 0) + 1
    st.session_state["result"] = (level_name, res_new)

stored = st.session_state.get("result")
res = stored[1] if stored and stored[0] == level_name else None

# ===================== game area =====================
cell = max(32, min(72, 760 // max(level.width, 1)))
left, right = st.columns([1.5, 1])

with left:
    board = st.empty()
    if res is not None and res.solved:
        states = solution_states(level, res.solution)
        last = len(states) - 1
        skey = f"step_{level_name}_{st.session_state.get('run_id', 0)}"
        st.session_state.setdefault(skey, 0)

        b1, b2, b3 = st.columns(3)
        b1.button("Back", key="step_back", on_click=step_by, args=(-1, last, skey),
                  use_container_width=True)
        b2.button("Forward", key="step_fwd", on_click=step_by, args=(1, last, skey),
                  use_container_width=True)
        play = b3.button("Play solution", key="play_solution", use_container_width=True)
        step = st.slider("Step", 0, last, key=skey)

        def draw(i):
            board.markdown(f'<div class="board-wrap">{board_html(level, states[i], cell)}</div>',
                           unsafe_allow_html=True)

        draw(step)
        if play:
            for i in range(step, last + 1):
                draw(i)
                time.sleep(0.25)
    else:
        board.markdown(f'<div class="board-wrap">{board_html(level, level.start, cell)}</div>',
                       unsafe_allow_html=True)

with right:
    if res is None:
        st.info("Choose the algorithm and options above, then press Run solver.")
    else:
        if res.solved:
            st.success("Solved. All boxes are on goals.")
        elif res.status == "unsolvable":
            st.error("This level cannot be solved.")
        else:
            st.warning(f"Not solved: {res.status}")
        m1, m2 = st.columns(2)
        m1.metric("Moves", res.moves)
        m2.metric("Pushes", res.pushes)
        m3, m4 = st.columns(2)
        m3.metric("Nodes expanded", res.nodes_expanded)
        m4.metric("Time (s)", res.time_sec)
        if res.solved:
            st.caption("Solution (lowercase = step, UPPERCASE = push)")
            st.code(res.solution)

# ===================== comparison =====================
st.header("Algorithm comparison on this level")
if st.button("Compare all configurations (live)", key="compare_live"):
    rows = []
    for label in CONFIGS:
        r = run_config(level, label, time_limit)
        rows.append({"config": label, "status": r.status, "moves": r.moves,
                     "nodes_expanded": r.nodes_expanded, "time_sec": r.time_sec})
    st.session_state["compare"] = (level_name, pd.DataFrame(rows))

cmp_ = st.session_state.get("compare")
if cmp_ and cmp_[0] == level_name:
    df = cmp_[1]
elif os.path.exists("experiments/results_all.csv"):
    all_df = pd.read_csv("experiments/results_all.csv")
    df = all_df[all_df["level"] == level_name].drop(columns=["level"], errors="ignore")
    st.caption("Showing saved results from experiments/results_all.csv")
else:
    df = None
    st.info("Press the button above, or run `python -m experiments.run_all` first.")

if df is not None and len(df):
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.bar_chart(df.set_index("config")["nodes_expanded"])