#!/bin/env python3

import sys
import army, colors, golem, scenario, tile

s = scenario.Scenario()
s.title = "Last Golem Standing"
s.add_board(6,6)

s.add_army(army.Army(name="Player 1", color=colors.fg.green, 
                        golems=[ 
                            golem.golems['G0001'],
                              ]))
s.add_army(army.Army(name="Player 2", color=colors.fg.red,
                         golems=[ 
                             golem.golems['G0001'],
                             ]))

s.get_army("Player 1").golems[0].x,s.get_army("Player 1").golems[0].y = 1,1
s.get_army("Player 2").golems[0].x,s.get_army("Player 2").golems[0].y = 4,1
s.board.place_tile(tile.Tile('1A'), (0,3))
s.board.place_tile(tile.Tile('18B'), (3,3))
s.populate()

while True:
    print(colors.cls, end="")
    print("{}: Round {}".format(s.title, s.round))
    for a in s.armies():
        print(a.color, a.name, colors.reset, " | AP: ", a.ap, " | Mana: ", a.mana, " | VP: ", a.vp)

    if s.active_turn_state == scenario.turn_states.SELECT_GOLEM:
        for i, golem in enumerate(s.active_army().golems):
            golem.display_override = str(i+1)
    print(s.board)
    if s.active_turn_state == scenario.turn_states.SELECT_GOLEM:
        for golem in s.active_army().golems:
            golem.display_override = None

    for army in s.armies():
        if len(army.golems) == 0:
            print("{color}{name}{reset} loses the game.".format(
                color=army.color,
                name=army.name,
                reset=colors.reset
            ))
            sys.exit()

    match s.active_turn_state:
        case scenario.turn_states.SELECT_GOLEM:
            print(s.active_army().color, s.active_army().name, colors.reset, '> Select golem')
            for i, golem in enumerate(s.active_army().golems):
                print("[{i}] {name}".format(i=i + 1, name=golem.name))

        case scenario.turn_states.SELECT_ACTION:
            print(s.active_army().color, s.active_army().name, colors.reset, '> ', s.active_golem.name, ' > Select action')
            print("[A] Attack")
            print("[M] Move")

        case scenario.turn_states.SELECT_ATTACK:
            print(s.active_army().color, s.active_army().name, colors.reset, '> ', s.active_golem.name, ' > Attack > Select attack')
            attack_options = s.active_golem.get_attack_options()
            for i, attack in enumerate(sorted(attack_options.keys())):
                if attack_options[attack]['ap'] > s.active_army().ap: 
                    print("[ ] {attack}: {ap} AP, {tohit}% to hit, {damage} damage, {range} range".format(attack=attack, ap=attack_options[attack]['ap'], tohit=attack_options[attack]['tohit'], damage=attack_options[attack]['damage'], range=attack_options[attack]['range']), end='')
                else:
                    print("[{key}] {attack}: {ap} AP, {tohit}% to hit, {damage} damage, {range} range".format(key=i, attack=attack, ap=attack_options[attack]['ap'], tohit=attack_options[attack]['tohit'], damage=attack_options[attack]['damage'], range=attack_options[attack]['range']), end='')
                if 'cooldown_refresh' in attack_options[attack] and attack_options[attack]['cooldown_refresh'] > 0:
                    print(', cooldown refreshes after {rounds} rounds'.format(rounds=attack_options[attack]['cooldown_refresh']), end='')
                print()    
                print("    {description}".format(description=attack_options[attack]['description']))

        case scenario.turn_states.SELECT_ATTACK_TARGET:
            print(s.active_army().color, s.active_army().name, colors.reset, '> ', s.active_golem.name, ' > Attack > ', s.active_attack_name, ' > Select target')
            for i, target in enumerate(s.active_attack_target_options):
                print("[{}] {}{}{} (Health={}, To-Hit={})".format(i, target.color, target.name, colors.reset, \
                                                       target.health, \
                                                       s.calculate_to_hit(target=target)))

        case scenario.turn_states.SELECT_MOVEMENT_ACTION:
            print(s.active_army().color, s.active_army().name, colors.reset, '> ', s.active_golem.name, ' > Move > Select movement')
            movement_options = s.active_golem.get_movement_options()
            for ability in sorted(movement_options.keys()):
                for choice, choice_details in enumerate(movement_options[ability]):
                    key = "{}{}".format(ability[0], choice)
                    if movement_options[ability][choice]['ap'] > s.active_army().ap:
                        key = "  "
                    if movement_options[ability][choice]['ap'] > movement_options[ability][choice]['base_ap']:
                        print("[{key}] {full}: {color}{ap}{reset} AP, {mp} MP".format(key=key, 
                                                            full=ability, 
                                                            ap=movement_options[ability][choice]['ap'],
                                                            mp=movement_options[ability][choice]['mp'],
                                                            color=colors.fg.blue,
                                                            reset=colors.reset
                                                            ), end="")
                    else:
                        print("[{key}] {full}: {ap} AP, {mp} MP".format(key=key, 
                                                            full=ability, 
                                                            ap=movement_options[ability][choice]['ap'],
                                                            mp=movement_options[ability][choice]['mp']
                                                            ), end="")
                    if 'nimble' in movement_options[ability][choice] and movement_options[ability][choice]['nimble']:
                        print(", nimble", end='')
                    if 'cooldown_refresh' in movement_options[ability][choice] and movement_options[ability][choice]['cooldown_refresh']:
                        print(', cooldown refreshes after {rounds} rounds'.format(
                            rounds=movement_options[ability][choice]['cooldown_refresh']
                        ), end="")
                    print()

        case scenario.turn_states.SELECT_MOVEMENT_LOCATION:
            i = 1
            active_movement_location_options = list([None]) 
            for y, row in enumerate(s.active_movement_location_options):
                for x, column in enumerate(row):
                    if column:
                        print("[{i}] {column}{row}".format(i=i, column='ABCDEFGHIJKLMNOPQRSTUVWXYZ'[x], row=y))
                        active_movement_location_options.append((x,y))
                        i += 1
            if i == 1:
                print("No possible destination regions for {}.".format(active_movement_ability))

    if s.active_turn_state != scenario.turn_states.SELECT_GOLEM:
        print('[D] Done')
    print('[T] End turn')
    print('[Q] Quit')
    player_choice = input('> ').lower()

    if player_choice == 'q': break
    if player_choice == 't':
        s.end_turn()
        next

    match s.active_turn_state:
        case scenario.turn_states.SELECT_GOLEM:
            if player_choice.isdigit() and 0 < int(player_choice) <= len(s.active_army().golems):
                s.active_golem = s.active_army().golems[int(player_choice) - 1]
                s.active_golem.display_override = colors.bg.lightgrey + s.active_golem.name[0]
                s.active_turn_state = scenario.turn_states.SELECT_ACTION
        case scenario.turn_states.SELECT_ACTION:
            if player_choice == 'd':
                s.active_golem.display_override = None
                s.active_golem = None
                s.active_turn_state = scenario.turn_states.SELECT_GOLEM
            if player_choice == 'm':
                s.active_turn_state = scenario.turn_states.SELECT_MOVEMENT_ACTION
            if player_choice == 'a':
                s.active_turn_state = scenario.turn_states.SELECT_ATTACK
        case scenario.turn_states.SELECT_ATTACK:
            if player_choice == 'd':
                s.active_turn_state = scenario.turn_states.SELECT_ACTION
            attack_options = s.active_golem.get_attack_options()
            if player_choice.isdigit() and int(player_choice) < len(attack_options.keys()):
                selected_attack=sorted(attack_options.keys())[int(player_choice)]
                if s.active_army().ap >= attack_options[selected_attack]['ap']:
                    s.populate_attack_target_options(attack_name=selected_attack)
        case scenario.turn_states.SELECT_ATTACK_TARGET:
            if player_choice == 'd':
                s.active_turn_state = scenario.turn_states.SELECT_ATTACK
                s.active_attack_name = None
            if player_choice.isdigit():
                targets = s.active_attack_target_options
                if len(targets) >= int(player_choice):
                    target = targets[int(player_choice)]
                    combat_result = s.attack(target=target)
                    print("Roll: {roll} vs To-Hit: {to_hit}".format(roll=combat_result.roll, to_hit=combat_result.to_hit))
                    if combat_result.hit:
                        print("Attack hits for {damage} damage.".format(damage=combat_result.damage))
                    else:
                        print("Attack misses.")
                    if target.health <= 0:
                        print("{name} is destroyed.".format(name=target.name))
                    else:
                        print("{name} has {health} health remaining.".format(name=target.name,health=target.health))
                    s.active_attack_name = None
                    s.active_golem = None
                    s.active_turn_state = scenario.turn_states.SELECT_GOLEM
                    input("Press ENTER to continue.")
        case scenario.turn_states.SELECT_MOVEMENT_ACTION:
            if player_choice == 'd':
                s.active_turn_state = scenario.turn_states.SELECT_ACTION
            movement_options = s.active_golem.get_movement_options()
            for key in movement_options.keys():
                if player_choice[0] == key[0].lower():
                    if len(player_choice) > 1 and player_choice[1].isdigit() and int(player_choice[1]) < len(movement_options[key]):
                        if 'ap' in movement_options[key][int(player_choice[1])] and \
                            movement_options[key][int(player_choice[1])]['ap'] <= s.active_army().ap:
                            s.active_turn_state = scenario.turn_states.SELECT_MOVEMENT_LOCATION
                            active_movement_type = key
                            active_movement_ability = movement_options[key][int(player_choice[1])]
                            s.populate_movement_options(movement_type=active_movement_type, movement_options=active_movement_ability)
        case scenario.turn_states.SELECT_MOVEMENT_LOCATION:
            if player_choice == 'd':
                s.active_turn_state = scenario.turn_states.SELECT_MOVEMENT_ACTION
            if player_choice.isdigit() and 0 < int(player_choice) < len(active_movement_location_options):
                s.move_active_golem_to_location(x=active_movement_location_options[int(player_choice)][0], 
                                                y=active_movement_location_options[int(player_choice)][1])