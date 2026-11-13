from src.level_parser import parse_level
from src.play import Game, hint
from src.moves import apply_action

EASY = "#####\n# @ #\n# $ #\n# . #\n#####\n"
MED = "#######\n#     #\n# $ $ #\n#  @  #\n# .   #\n#   . #\n#######\n"


def test_move_wall_and_push():
    g = Game(parse_level(EASY))
    assert not g.move("U")            # wall
    assert g.moves == 0
    assert g.move("L") and g.moves == 1 and g.pushes == 0
    assert g.move("R") and g.move("D") and g.pushes == 1


def test_win_and_no_move_after_win():
    g = Game(parse_level(EASY))
    assert g.move("D")
    assert g.solved and g.moves == 1 and g.pushes == 1
    assert not g.move("L")            # game over, moves ignored


def test_undo_and_reset():
    g = Game(parse_level(MED))
    start = g.state
    g.move("L"); g.move("U")
    assert g.moves == 2
    assert g.undo() and g.moves == 1
    assert g.undo() and g.state == start and g.moves == 0
    assert not g.undo()
    g.move("R"); g.reset()
    assert g.state == start and g.moves == 0 and not g.history


def test_undo_push_counter():
    g = Game(parse_level("#######\n#@$   #\n#   . #\n#######\n"))
    g.move("R")
    assert g.pushes == 1
    g.undo()
    assert g.pushes == 0 and g.moves == 0


def test_not_stuck_on_open_level():
    assert not Game(parse_level(MED)).stuck
    assert not Game(parse_level("#####\n#@$.#\n#####\n")).stuck


def test_stuck_corner():
    g = Game(parse_level("#####\n#@$ #\n# . #\n#####\n"))
    g.move("R"); g.move("R")                # box pushed into the top-right corner
    assert g.stuck


def test_hint_leads_to_win():
    level = parse_level(MED)
    g = Game(level)
    sol = hint(level, g.state)
    assert sol
    for a in sol:
        assert g.move(a)
    assert g.solved


def test_hint_from_midgame():
    level = parse_level(MED)
    g = Game(level)
    g.move("L"); g.move("L")
    sol = hint(level, g.state)
    for a in sol:
        assert g.move(a)
    assert g.solved


def test_hint_none_when_unsolvable():
    level = parse_level("#####\n#$ .#\n# @ #\n#####\n")
    assert hint(level, level.start) is None
