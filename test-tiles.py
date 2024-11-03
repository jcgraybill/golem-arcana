#!/bin/env python3
import board, tile

the_board = board.Board(5,5)
the_board.reset_terrain()
print(the_board)
t = tile.Tile("1A")
print(t)
t.rotate()
the_board.place_tile(t, origin=(0,1))
print(the_board)