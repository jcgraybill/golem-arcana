#!/bin/env python3
import army, board, colors, golem, movement

DISPLAY = False

def test_performing_a_test():
    return True

def test_walking():
    the_board=board.Board(5,1)
    results = movement.find_valid_moves(
        the_board = the_board,
        starting_region=(0,0),
        move_type="Walk",
        current_golem_army=None,
        movement_values={'mp': 3, 'nimble': False}
    )
    if DISPLAY: movement.display_valid_moves(results=results, starting_region=(0,0), the_board=the_board)
    return results == [[False, True, True, True, False]]

def test_hills():
    the_board = board.Board(5,1)
    the_board.region(1,0).terrain = "Hills"
    results = movement.find_valid_moves(
        the_board = the_board,
        starting_region=(0,0),
        move_type="Walk",
        current_golem_army=None,
        movement_values={'mp': 3, 'nimble': False}
    )
    if DISPLAY: movement.display_valid_moves(results=results, starting_region=(0,0), the_board=the_board)
    return results == [[False, True, True, False, False]]

def test_mountains():
    the_board = board.Board(5,1)
    the_board.region(2,0).terrain = "Mountains"
    results = movement.find_valid_moves(
        the_board = the_board,
        starting_region=(0,0),
        move_type="Walk",
        current_golem_army=None,
        movement_values={'mp': 3, 'nimble': False}
    )
    if DISPLAY: movement.display_valid_moves(results=results, starting_region=(0,0), the_board=the_board)
    return results == [[False, True, False, False, False]]

def test_water():
    the_board = board.Board(5,1)
    the_board.region(1,0).terrain = "Shallow water"
    the_board.region(2,0).terrain = "Deep water"
    results = movement.find_valid_moves(
        the_board = the_board,
        starting_region=(0,0),
        move_type="Walk",
        current_golem_army=None,
        movement_values={'mp': 3, 'nimble': False}
    )
    if DISPLAY: movement.display_valid_moves(results=results, starting_region=(0,0), the_board=the_board)
    return results == [[False, True, True, False, False]]

def test_flying_mountains():
    the_board = board.Board(5,1)
    the_board.region(2,0).terrain = "Mountains"
    results = movement.find_valid_moves(
        the_board = the_board,
        starting_region=(0,0),
        move_type="Fly",
        current_golem_army=None,
        movement_values={'mp': 3, 'nimble': False}
    )
    if DISPLAY: movement.display_valid_moves(results=results, starting_region=(0,0), the_board=the_board)
    return results == [[False, True, False, True, False]]

def test_map_edge():
    the_board = board.Board(5,2)
    the_board.region(1,0).terrain = "Map Edge"
    the_board.region(2,0).terrain = "Map Edge"
    results = movement.find_valid_moves(
        the_board = the_board,
        starting_region=(0,0),
        move_type="Fly",
        current_golem_army=None,
        movement_values={'mp': 4, 'nimble': False}
    )
    if DISPLAY: movement.display_valid_moves(results=results, starting_region=(0,0), the_board=the_board)
    return results == [ [False, False, False, False, False], 
                        [True,  True,  True,  True,  False]]

def test_movement():
    the_board = board.Board(5,1)
    the_army  = army.Army(name="test", ap=1, color=colors.fg.green, 
                        golems=[ golem.golems['G0001'] ])
    the_board.populate([the_army])
    assert False == movement.move(the_board=the_board, the_golem=the_army.golems[0], the_army=the_army, to_region=(5,1), move_type="Make the test fail", move_type_index=0)
    assert False == movement.move(the_board=the_board, the_golem=the_army.golems[0], the_army=the_army, to_region=(5,1), move_type="Walk", move_type_index=2)
    assert False == movement.move(the_board=the_board, the_golem=the_army.golems[0], the_army=the_army, to_region=(4,0), move_type="Walk", move_type_index=0)
    assert True == movement.move(the_board=the_board, the_golem=the_army.golems[0], the_army=the_army, to_region=(3,0), move_type="Walk", move_type_index=0)
    if DISPLAY: print(the_board)

if __name__ == "__main__":
    assert test_performing_a_test()
    assert test_walking()
    assert test_hills()
    assert test_mountains()
    assert test_water()
    assert test_flying_mountains()
    assert test_map_edge()
    test_movement()