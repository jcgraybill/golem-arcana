import army, board, golem, colors, region

X, Y = 0, 1

def move(the_board: board.Board, the_golem: golem.Golem, the_army: army.Army, to_region: tuple, move_type: str, move_options: dict):
    if to_region[X] >= the_board.w or to_region[Y] >= the_board.h: return False
    if move_type not in the_golem.get_movement_options().keys(): return False
    valid_moves = find_valid_moves(the_board=the_board,
                                   starting_region=(the_golem.x, the_golem.y),
                                   move_type=move_type,
                                   current_golem_army=the_army.name,
                                   movement_values=move_options,
                                   current_golem_base_size=the_golem.base_size
                                   )
    if valid_moves[to_region[Y]][to_region[X]] == False: return False
    the_board.board[the_golem.y][the_golem.x].remove(the_golem)
    the_golem.x = to_region[X]
    the_golem.y = to_region[Y]
    the_board.region(x=the_golem.x, y=the_golem.y).add(the_golem)
    the_army.ap -= move_options['ap']
    the_golem.activate_cooldown(move_options)
    return True

def evaluate_region(the_board: board.Board, starting_region: tuple, current_region: tuple, \
                    move_type: str, mp: int, nimble: bool, current_golem_army: str, current_golem_base_size: int, \
                    results: list):

    if current_region != starting_region:
        if the_board.board[current_region[Y]][current_region[X]].occupancy() + current_golem_base_size <= region.MAX_CAPACITY and \
            the_board.board[current_region[Y]][current_region[X]].can_end_movement_in():
            results[current_region[Y]][current_region[X]] = True

        if move_type == 'Walk':
            for g in the_board.region(current_region[X],current_region[Y]).golems():
                if g.army != current_golem_army:
                    return results

    # North
    if current_region[Y] > 0 and \
        the_board.board[current_region[Y] - 1][current_region[X]].mp_to_enter(move_type) <= mp:
            evaluate_region(the_board=the_board, 
                starting_region=starting_region,
                current_region=(current_region[X], current_region[Y] - 1),
                move_type = move_type,
                mp = mp - the_board.board[current_region[Y] - 1][current_region[X]].mp_to_enter(move_type),
                nimble = nimble,
                current_golem_army=current_golem_army,
                current_golem_base_size=current_golem_base_size,
                results = results
            )
        
    # Northeast
    if nimble and current_region[Y] > 0 and current_region[X] < len(the_board.board[0]) - 1 and \
        the_board.board[current_region[Y] - 1][current_region[X] + 1].mp_to_enter(move_type) <= mp:
            evaluate_region(the_board=the_board, 
                starting_region=starting_region,
                current_region=(current_region[X] + 1, current_region[Y] - 1),
                move_type = move_type,
                mp = mp - the_board.board[current_region[Y] - 1][current_region[X] + 1].mp_to_enter(move_type),
                nimble = nimble,
                current_golem_army=current_golem_army,
                current_golem_base_size=current_golem_base_size,
                results = results
            )
    
    # East
    if current_region[X] < len(the_board.board[0]) - 1 and \
        the_board.board[current_region[Y]][current_region[X] + 1].mp_to_enter(move_type) <= mp:
            evaluate_region(the_board=the_board, 
                starting_region=starting_region,
                current_region=(current_region[X] + 1, current_region[Y]),
                move_type = move_type,
                mp = mp - the_board.board[current_region[Y]][current_region[X] + 1].mp_to_enter(move_type),
                nimble = nimble,
                current_golem_army=current_golem_army,
                current_golem_base_size=current_golem_base_size,
                results = results
            )

    # Southeast
    if nimble and current_region[Y] < len(the_board.board) - 1 and current_region[X] < len(the_board.board[0]) - 1 and \
        the_board.board[current_region[Y] + 1][current_region[X] + 1].mp_to_enter(move_type) <= mp:
            evaluate_region(the_board=the_board, 
                starting_region=starting_region,
                current_region=(current_region[X] + 1, current_region[Y] + 1),
                move_type = move_type,
                mp = mp - the_board.board[current_region[Y] + 1][current_region[X] + 1].mp_to_enter(move_type),
                nimble = nimble,
                current_golem_army=current_golem_army,
                current_golem_base_size=current_golem_base_size,
                results = results
            )
    
    # South
    if current_region[Y] < len(the_board.board) - 1 and \
        the_board.board[current_region[Y] + 1][current_region[X]].mp_to_enter(move_type) <= mp:
            evaluate_region(the_board=the_board, 
                starting_region=starting_region,
                current_region=(current_region[X], current_region[Y] + 1),
                move_type = move_type,
                mp = mp - the_board.board[current_region[Y] + 1][current_region[X]].mp_to_enter(move_type),
                nimble = nimble,
                current_golem_army=current_golem_army,
                current_golem_base_size=current_golem_base_size,
                results = results
            )
    
    # Southwest
    if nimble and current_region[Y] < len(the_board.board) - 1 and current_region[X] > 0 and \
        the_board.board[current_region[Y] + 1][current_region[X] - 1].mp_to_enter(move_type) <= mp:
            evaluate_region(the_board=the_board, 
                starting_region=starting_region,
                current_region=(current_region[X] - 1, current_region[Y] + 1),
                move_type = move_type,
                mp = mp - the_board.board[current_region[Y] + 1][current_region[X] - 1].mp_to_enter(move_type),
                nimble = nimble,
                current_golem_army=current_golem_army,
                current_golem_base_size=current_golem_base_size,
                results = results
            )

    # West
    if current_region[X] > 0 and \
        the_board.board[current_region[Y]][current_region[X] - 1].mp_to_enter(move_type) <= mp:
            evaluate_region(the_board=the_board, 
                starting_region=starting_region,
                current_region=(current_region[X] - 1, current_region[Y]),
                move_type = move_type,
                mp = mp - the_board.board[current_region[Y]][current_region[X] - 1].mp_to_enter(move_type),
                nimble = nimble,
                current_golem_army=current_golem_army,
                current_golem_base_size=current_golem_base_size,
                results = results
            )
        
    # Northwest
    if nimble and current_region[Y] > 0 and current_region[X] > 0 and \
        the_board.board[current_region[Y] - 1][current_region[X] - 1].mp_to_enter(move_type) <= mp:
            evaluate_region(the_board=the_board, 
                starting_region=starting_region,
                current_region=(current_region[X] - 1, current_region[Y] - 1),
                move_type = move_type,
                mp = mp - the_board.board[current_region[Y] - 1][current_region[X] - 1].mp_to_enter(move_type),
                nimble = nimble,
                current_golem_army=current_golem_army,
                current_golem_base_size=current_golem_base_size,
                results = results
            )    

def find_valid_moves(the_board: board.Board, starting_region: tuple, \
                     move_type: str, current_golem_army: str, \
                        movement_values: dict, current_golem_base_size: int = 1 ):
    results = [[False for x in range(the_board.w)] for y in range(the_board.h)]

    breakaway_cost = 0
    for g in the_board.region(starting_region[X],starting_region[Y]).golems():
        if g.army != current_golem_army:
            movement_options = g.get_movement_options()
            if move_type in movement_options and len(movement_options[move_type]) > 0:
                breakaway_cost = 1

    if the_board.board[starting_region[Y]][starting_region[X]].breakaway_modifier() > 0:
         breakaway_cost += the_board.board[starting_region[Y]][starting_region[X]].breakaway_modifier()

    evaluate_region(the_board=the_board,
                    starting_region=starting_region,
                    current_region=starting_region,
                    move_type=move_type,
                    mp=movement_values['mp'] - breakaway_cost,
                    nimble=movement_values['nimble'],
                    current_golem_army=current_golem_army,
                    current_golem_base_size=current_golem_base_size,
                    results=results)
    
    results[starting_region[Y]][starting_region[X]] = False
    return results

def display_valid_moves(results: list, starting_region: tuple, the_board: board.Board):
    for y in range(len(results)):
        for x in range(len(results[0])):
            if results[y][x]:
                print(colors.fg.green, end="")
            else:
                print(colors.fg.darkgrey, end="")
            if x == starting_region[0] and y == starting_region[1]:
                print("*", end="")
            else:
                print(the_board.region(x,y).get_terrain()[0], end="")
        print()

if __name__ == "__main__":
    the_board = board.Board(9,9)
    starting_region=(4,4)
    results = find_valid_moves(the_board=the_board,
                     starting_region=starting_region,
                     move_type="Walk",
                     current_golem_army='',
                     movement_values={'ap': 1, 'mp': 3, 'nimble': True}
                     )
    print(colors.cls, end="")
    display_valid_moves(results=results, starting_region=starting_region, the_board=the_board)