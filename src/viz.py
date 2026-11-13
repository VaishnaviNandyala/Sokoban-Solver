"""HTML board drawing for the Streamlit app (no Streamlit import here)."""
from .level_parser import Level
from .state import State

_BASE = ("width:{c}px;height:{c}px;box-sizing:border-box;display:flex;"
         "align-items:center;justify-content:center;")


def board_html(level: Level, state: State, cell: int = 48) -> str:
    base = _BASE.format(c=cell)
    out = [f'<div style="display:grid;grid-template-columns:repeat({level.width},{cell}px);'
           f'width:{cell * level.width}px;border:1px solid #c9cddb;border-radius:8px;overflow:hidden">']
    for r in range(level.height):
        for c in range(level.width):
            p = (r, c)
            if p in level.walls:
                out.append(f'<div style="{base}background:#3b3f4e;border:1px solid #2d303c"></div>')
                continue
            inner = ""
            if p == state.player:
                inner = ('<div style="width:70%;height:70%;border-radius:50%;'
                         'background:#1c6ed5;border:3px solid #0f4a9e"></div>')
            elif p in state.boxes:
                col, edge = ("#1a7f4b", "#0f5a33") if p in level.goals else ("#c27a2c", "#7a4a12")
                inner = (f'<div style="width:80%;height:80%;border-radius:6px;'
                         f'background:{col};border:3px solid {edge}"></div>')
            elif p in level.goals:
                inner = ('<div style="width:36%;height:36%;border-radius:50%;'
                         'border:3px solid #1a7f4b"></div>')
            out.append(f'<div style="{base}background:#f6f7fb;border:1px solid #dfe2ec">{inner}</div>')
    out.append("</div>")
    return "".join(out)
