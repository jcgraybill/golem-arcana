#!/bin/env python3
import board

DISPLAY = True
the_board = board.Board(1,1)
r = the_board.region(0,0)

r.terrain = "Plains"
assert r.cover_for_golem_size("Warsprite") == 0

r.cover = "Medium cover"
assert r.cover_for_golem_size("Ogre") == 10
assert r.intervening_cover_for_golem_size("Titan") == 2

r.terrain = "Shallow Water"
assert r.cover_for_golem_size("Warsprite") == 10
r.terrain = "Plains"
