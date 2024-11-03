#!/bin/env python3
import army, board, colors, golem, manawell

DISPLAY = False

def display():
    if DISPLAY:
        for army in armies:
            print(army.color, army.name, colors.reset, " | AP: ", army.ap, " | Mana: ", army.mana)
        print(the_board)

AP = 0
the_board = board.Board(1,1)
armies = list()
armies.append(army.Army(name="Player 1", ap=AP, color=colors.fg.green, 
                        golems=[ 
                            golem.golems['G0001'],
                              ]))
armies.append(army.Army(name="Player 2", ap=AP, color=colors.fg.red,
                         golems=[ 
                             golem.golems['G0001'],
                             ]))
the_mana_well = manawell.ManaWell()
the_mana_well.visible = False
the_board.region(0,0).add(the_mana_well)
display()

the_board.region(0,0).add(armies[0].golems[0])

assert(armies[0].mana == 0)
assert(armies[1].mana == 0)
display()

the_board.begin_turn(armies[0])
assert(armies[0].mana == 6)
assert(armies[1].mana == 0)
the_board.region(0,0).add(armies[1].golems[0])
display()

the_board.begin_turn(armies[1])
assert(armies[0].mana == 6)
assert(armies[1].mana == 0)
the_board.region(0,0).remove(armies[1].golems[0])
display()

the_board.begin_turn(armies[0])
assert(armies[0].mana == 12)
assert(armies[1].mana == 0)

the_board.begin_turn(armies[1])
assert(armies[0].mana == 12)
assert(armies[1].mana == 0)

the_board.begin_turn(armies[0])
assert(armies[0].mana == 12)
assert(armies[1].mana == 0)
display()