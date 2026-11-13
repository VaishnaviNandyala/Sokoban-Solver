"""Sokoban - play it yourself, or watch the solver (Streamlit, full-screen layout).
 
Run:  streamlit run app_play.py
Level chooser on top, two tabs: "Play yourself" and "Solver demo".
All solver options are on the main screen (no sidebar).
"""
import glob
import os
import re
import time
 
import pandas as pd
import streamlit as st
 
from src.heuristics import HEURISTICS
from src.level_parser import load_level
from src.play import WORDS, Game, hint
from src.runner import CONFIGS, run_config, run_custom, solution_states
from src.viz import board_html
 
st.set_page_config(page_title="Sokoban", layout="wide", initial_sidebar_state="collapsed")
 
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
st.title("Sokoban")
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
is_last = level_idx == len(level_files) - 1
st.subheader(f"{level_name}  ({level_idx + 1} of {len(level_files)})")
 
cell = max(32, min(72, 760 // max(level.width, 1)))
 
 
def board_markup(state):
    return f'<div class="board-wrap">{board_html(level, state, cell)}</div>'
 
 
tab_play, tab_solver = st.tabs(["Play yourself", "Solver demo"])
 
# =====================================================================
# TAB 1: play by hand
# =====================================================================
with tab_play:
    gkey = f"game::{level_name}"
    if gkey not in st.session_state:
        st.session_state[gkey] = Game(level)
    game = st.session_state[gkey]
 
    def do_move(action):
        game.move(action)
 
    def do_undo():
        game.undo()
 
    def do_reset():
        game.reset()
        st.session_state.pop("hint", None)
 
    def do_hint():
        sol = hint(level, game.state, time_limit=10)
        st.session_state["hint"] = (game.state, sol)
 
    def do_apply_hint():
        h = st.session_state.get("hint")
        if h and h[1] and h[0] == game.state:
            game.move(h[1][0])
 
    left, right = st.columns([1.5, 1])
    with left:
        st.markdown(board_markup(game.state), unsafe_allow_html=True)
        st.caption("Blue circle = you, brown square = box, green ring = goal, "
                   "green square = box on goal.")
 
    with right:
        if game.solved:
            st.success(f"Solved in {game.moves} moves ({game.pushes} pushes).")
            st.button("Next level", key="next_after_solve", on_click=go_level, args=(1,),
                      type="primary", disabled=is_last, use_container_width=True)
        elif game.stuck:
            st.error("Stuck! A box can never reach a goal from here. Press Undo or Reset.")
        else:
            st.info("Use the arrow buttons to move.")
 
        m1, m2 = st.columns(2)
        m1.metric("Moves", game.moves)
        m2.metric("Pushes", game.pushes)
 
        _, up_c, _ = st.columns([1, 1, 1])
        up_c.button("Up", key="mv_U", on_click=do_move, args=("U",), use_container_width=True)
        lc, dc, rc = st.columns([1, 1, 1])
        lc.button("Left", key="mv_L", on_click=do_move, args=("L",), use_container_width=True)
        dc.button("Down", key="mv_D", on_click=do_move, args=("D",), use_container_width=True)
        rc.button("Right", key="mv_R", on_click=do_move, args=("R",), use_container_width=True)
 
        u1, u2, u3 = st.columns(3)
        u1.button("Undo", key="undo", on_click=do_undo, use_container_width=True)
        u2.button("Reset", key="reset", on_click=do_reset, use_container_width=True)
        u3.button("Hint (A*)", key="hint", on_click=do_hint, use_container_width=True)
 
        h = st.session_state.get("hint")
        if h and h[0] == game.state and not game.solved:
            if h[1]:
                st.success(f"Hint: move **{WORDS[h[1][0].upper()]}**. "
                           f"The solver can finish from here in {len(h[1])} moves.")
                st.button("Apply hint move", key="apply_hint", on_click=do_apply_hint)
            else:
                st.warning("The solver found no solution from here. Try Undo.")
 
# =====================================================================
# TAB 2: solver demo
# =====================================================================
with tab_solver:
    with st.container(border=True):
        a, b, c, d, e, f = st.columns([2.2, 2, 1.7, 1.7, 2.2, 1.5], vertical_alignment="bottom")
        algo = a.radio("Search algorithm", ["BFS", "DFS", "A*", "Greedy"], index=2,
                       horizontal=True, key="algo")
        heuristic = b.selectbox("Heuristic (A* / Greedy)", list(HEURISTICS), index=1,
                                disabled=algo not in ("A*", "Greedy"), key="heuristic")
        push_moves = c.checkbox("Push-based moves", value=True, key="push_moves")
        deadlock = d.checkbox("Prune deadlocks", value=True, key="deadlock")
        time_limit = e.slider("Time limit (seconds)", 1, 60, 10, key="time_limit")
        run = f.button("Run solver", type="primary", key="run_solver", use_container_width=True)
 
    if run:
        kind = {"BFS": "bfs", "DFS": "dfs", "A*": "astar", "Greedy": "greedy"}[algo]
        with st.spinner("Searching..."):
            res_new = run_custom(level, kind, heuristic, push_moves, deadlock, time_limit)
        st.session_state["run_id"] = st.session_state.get("run_id", 0) + 1
        st.session_state["result"] = (level_name, res_new)
 
    stored = st.session_state.get("result")
    res = stored[1] if stored and stored[0] == level_name else None
 
    s_left, s_right = st.columns([1.5, 1])
    with s_left:
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
 
            board.markdown(board_markup(states[step]), unsafe_allow_html=True)
            if play:
                for i in range(step, last + 1):
                    board.markdown(board_markup(states[i]), unsafe_allow_html=True)
                    time.sleep(0.25)
        else:
            board.markdown(board_markup(level.start), unsafe_allow_html=True)
 
    with s_right:
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
 
