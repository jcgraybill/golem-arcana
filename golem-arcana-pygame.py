#!/bin/env python3
import pygame, pygame.freetype, catppuccin
import army, combat, golem, manawell, region, scenario, tile
import gameboard, gamecontrols

STATUSBAR           = 24
WIDTH, HEIGHT       = 1440,768
HEIGHT              -= STATUSBAR
COLORS              = catppuccin.PALETTE.macchiato.colors
MARGINS             = 10
FONTFACE            = "bodoni72smallcapsbook"
FONTSIZE            = 18

font        = pygame.freetype.Font
click_sound = None
mouse_was_just_down = False
currently_pressed_button = None

statusbar = pygame.Surface((WIDTH, STATUSBAR))
arena = pygame.Surface((WIDTH * 3/4,HEIGHT))
ui    = pygame.Surface((WIDTH * 1/4, HEIGHT))
region_card = None
player_card = None
buttons = list()
combat_result_card = None
combat_result_card_ypos = 0

s = scenario.Scenario()
s.title = "Last Golem Standing"
s.board = gameboard.GameBoard(w=6,h=6, display_size=(WIDTH * 3/4, HEIGHT))
s.board.set_entire_map(terrain="Plains", cover="No cover")
s.board.region(0,0).set_cover( cover   = "Ground cover" )
s.board.region(1,0).set_cover( cover   = "Medium cover" )
s.board.region(2,0).set_terrain( terrain = "Hills" )
s.board.region(3,0).set_terrain( terrain = "Hills" )
s.board.region(3,0).set_cover( cover   = "Ground cover" )
s.board.region(4,0).set_terrain( terrain = "Hills" )
s.board.region(4,0).set_cover( cover   = "Medium cover" )
s.board.region(5,0).set_terrain( terrain = "Mountains" )
s.board.region(0,2).set_terrain( terrain = "Shallow water" )
s.board.region(1,2).set_terrain( terrain = "Deep water" )
s.board.region(2,2).set_terrain( terrain = "Miasma swamp" )
s.board.region(3,2).set_terrain( terrain = "The Pit" )
s.board.region(0,1).set_obstructions( obstructions = 1 )
s.board.region(5,1).set_obstructions( obstructions = 2 )

s.board.region(3,1).add(manawell.ManaWell())
s.board.place_tile(tile.Tile('1A'), (0,3))
s.board.place_tile(tile.Tile('18B'), (3,3))
s.board.refresh_display()

s.add_army(army.Army(name="Player 1", color=(128, 128, 0), 
                        golems=[ 
                            golem.golems['G0001'],
                            golem.golems['G0028'],
                              ]))
s.add_army(army.Army(name="Player 2", color=(178,34,34),
                         golems=[ 
                             golem.golems['G0001'],
                             ]))

s.get_army("Player 1").golems[0].x,s.get_army("Player 1").golems[0].y = 1,1
s.get_army("Player 1").golems[1].x,s.get_army("Player 1").golems[1].y = 3,1
s.get_army("Player 2").golems[0].x,s.get_army("Player 2").golems[0].y = 4,1
s.populate()

def init():
    global font, click_sound
    click_sound = pygame.mixer.Sound("click.mp3")
    font        = pygame.freetype.SysFont(FONTFACE, FONTSIZE)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT + STATUSBAR))
    pygame.display.set_caption("Golem Arcana")
    reset_buttons()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pointer = handle_mouse()
        generate_statusbar()
        generate_arena(pointer=(pointer[0], pointer[1]-STATUSBAR))
        generate_ui(pointer=(pointer[0] - WIDTH * 3/4, pointer[1]-STATUSBAR))

        screen.blit(statusbar, (0,0))
        screen.blit(arena, (0,STATUSBAR))
        screen.blit(ui, (WIDTH * 3/4, STATUSBAR))
        pygame.display.update()

def word_wrap(the_string: str, max_char_length: int) -> list[str]:
    lines = list()
    current_line = str()
    for word in the_string.split():
        if len(current_line) + len(word) <= max_char_length:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

def generate_statusbar():
    global statusbar
    if s.active_turn_state == scenario.turn_states.END_OF_MATCH:
        status_bar_text = "{victor} wins!".format(victor=s.victor.name)
        statusbar.fill(s.victor.color)
    else:
        status_bar_text = "{scenario} | Round {round} | {player}'s turn".format(scenario=s.title, round=str(s.round), player=s.active_army().name)
        statusbar.fill(s.active_army().color)
    text_surface, tx_rect = font.render(status_bar_text, COLORS.mantle.hex)
    sb_rect = statusbar.get_rect()
    statusbar.blit(text_surface, ((sb_rect.width - tx_rect.width) / 2, (sb_rect.height - tx_rect.height) / 2))

def generate_arena(pointer:tuple[int,int]=(0,0)):
    global arena, s
    arena.fill(COLORS.base.hex)
    if s.active_turn_state == scenario.turn_states.SELECT_MOVEMENT_LOCATION and len(s.active_movement_location_options) > 0:
        s.board.display_board(canvas=arena, pointer=pointer, locations=s.active_movement_location_options)
    else:
        s.board.display_board(canvas=arena, pointer=pointer)

def generate_ui(pointer: tuple[int,int]):
    global ui, s, buttons, region_card, combat_result_card_ypos
    ui.fill(COLORS.mantle.hex)

    if player_card == None:
        generate_player_card()
    player_card.draw(surface=ui)
    ypos = player_card.surface.get_height()

    selected_region = s.board.selected_region()
    if selected_region == None:
        if region_card != None:
            region_card = None
            reset_buttons()
    else:
        id = '|'.join((str(selected_region.x),str(selected_region.y)))
        if region_card == None or region_card.id != id:
            s.active_golem = None
            s.active_turn_state = scenario.turn_states.SELECT_GOLEM
            reset_buttons()
            generate_region_card(the_region=selected_region, ypos=ypos)
        region_card.draw(surface=ui)

        match s.active_turn_state:
            case scenario.turn_states.SELECT_GOLEM:
                # TODO there are many more edge cases than this
                # len - 1 because of the end turn button - very fragile
                if len(buttons) != len(selected_region.golems()) + 1:
                    reset_buttons()
                    ypos += region_card.contents.get_height() + MARGINS

                    for i, g in enumerate(selected_region.golems()):
                        id = '|'.join((str(selected_region.x),str(selected_region.y),str(i)))
                        buttons.append(generate_golem_button(the_golem=g, id=id, ypos=ypos))
                        ypos += buttons[-1].surface.get_height() + MARGINS

            case scenario.turn_states.SELECT_ACTION:
                if s.active_golem != None and len(buttons) == 1:
                    ypos += region_card.contents.get_height() + MARGINS
                    buttons.append(generate_golem_button(the_golem=s.active_golem , id=id, ypos=ypos, enabled=False))
                    ypos += buttons[-1].surface.get_height() + MARGINS

                    if 'Walk' in s.active_golem.get_movement_options():
                        for i,w in enumerate(s.active_golem.get_movement_options()['Walk']):
                            buttons.append(generate_ability_button(ability="Walk", index=i, attributes=w, ypos=ypos))
                            ypos += buttons[-1].surface.get_height() + MARGINS
                    if 'Fly' in s.active_golem.get_movement_options():
                        for i,f in enumerate(s.active_golem.get_movement_options()['Fly']):
                            buttons.append(generate_ability_button(ability="Fly", index=i, attributes=f, ypos=ypos))
                            ypos += buttons[-1].surface.get_height() + MARGINS
                    for a in sorted(s.active_golem.get_attack_options()):
                            buttons.append(generate_ability_button(ability=a, index=0, attributes=s.active_golem.get_attack_options()[a], ypos=ypos))
                            ypos += buttons[-1].surface.get_height() + MARGINS
                    
                    for i, g in enumerate(selected_region.golems()):
                        if g != s.active_golem:
                            id = '|'.join((str(selected_region.x),str(selected_region.y),str(i)))
                            buttons.append(generate_golem_button(the_golem=g, id=id, ypos=ypos))
                            ypos += buttons[-1].surface.get_height() + MARGINS

            case scenario.turn_states.SELECT_MOVEMENT_LOCATION:
                if s.active_golem != None and len(buttons) == 1:
                    ypos += region_card.contents.get_height() + MARGINS
                    buttons.append(generate_golem_button(the_golem=s.active_golem , id=id, ypos=ypos, enabled=False))
                    ypos += buttons[-1].surface.get_height() + MARGINS
                    buttons.append(generate_ability_button(ability=s.active_movement_type, index=0, attributes=s.active_movement_options, ypos=ypos))
                    ypos += buttons[-1].surface.get_height() + MARGINS

            case scenario.turn_states.SELECT_ATTACK_TARGET | scenario.turn_states.END_OF_MATCH:
                if s.active_golem != None and len(buttons) == 1:
                    ypos += region_card.contents.get_height() + MARGINS
                    buttons.append(generate_golem_button(the_golem=s.active_golem , id=id, ypos=ypos, enabled=False))
                    ypos += buttons[-1].surface.get_height() + MARGINS
                    buttons.append(generate_ability_button(ability=s.active_attack_name, index=0, attributes=s.active_attack_options, ypos=ypos))
                    ypos += buttons[-1].surface.get_height() + MARGINS
                    for i, g in enumerate(s.active_attack_target_options):
                        id = str(i)
                        buttons.append(generate_golem_button(the_golem=g, id=id, ypos=ypos, target=True))
                        ypos += buttons[-1].surface.get_height() + MARGINS
                    combat_result_card_ypos = ypos + MARGINS

    if combat_result_card != None:
        combat_result_card.draw(surface=ui)

    for button in buttons:
        if button.is_being_pointed_at(pointer=pointer):
            button.hover()
        else:
            button.unhover()
        button.draw(surface=ui)

def generate_player_card():
    global player_card
    player_details = list()
    player_details.append(font.render("Armies:", COLORS.text.hex)[0])
    for a in s.armies():
        player_details.append(font.render("   {name} | {ap} AP | {mana} Mana | {vp} VP".format(name=a.name, ap=a.ap, mana=a.mana, vp=a.vp), \
                                           COLORS.text.hex)[0])
    player_surface =  pygame.Surface((ui.get_rect().width, MARGINS + len(player_details) * FONTSIZE))
    player_surface.fill(gamecontrols.fix_color(COLORS.mantle))
    for i, pd in enumerate(player_details):
        player_surface.blit(pd, (MARGINS, MARGINS + i * FONTSIZE))
        if i > 0:
            player_surface.blit(font.render("   {name}".format(name=s.armies()[i-1].name), s.armies()[i-1].color, gamecontrols.fix_color(COLORS.mantle))[0], (MARGINS, MARGINS + i * FONTSIZE))
    player_card = gamecontrols.Card(x=0, y=0, id="playercard", contents=player_surface)

def generate_region_card(the_region: region.Region, ypos: int=0):
    global region_card
    region_details = list()
    region_details.append(font.render("Region {x},{y}: ".format(x = the_region.x, y = the_region.y), COLORS.text.hex)[0])
    region_details.append(font.render("   Terrain: {terrain}".format(terrain=the_region.get_terrain()), COLORS.text.hex)[0])
    region_details.append(font.render("   Cover: {cover}".format(cover  = the_region.get_cover()), COLORS.text.hex)[0])
    
    mana_well = the_region.mana_well()
    if the_region.get_obstructions() == 1:
        region_details.append(font.render("   One obstruction", COLORS.text.hex)[0])
    elif the_region.get_obstructions() > 1:
        region_details.append(font.render("   {} obstructions".format(the_region.get_obstructions()), COLORS.text.hex)[0])
    if mana_well:
        if mana_well.exhausted:
            region_details.append(font.render("   Exhausted Mana Well", COLORS.text.hex)[0])
        else:
            region_details.append(font.render("   Mana well containing {mana} mana".format(mana=mana_well.mana), COLORS.text.hex)[0])

    region_surface = pygame.Surface((ui.get_rect().width, MARGINS + len(region_details) * FONTSIZE ))
    region_surface.fill(COLORS.mantle.hex)
    for i, rd in enumerate(region_details):
        region_surface.blit(rd, (MARGINS, MARGINS + i * FONTSIZE))
    id = '|'.join((str(the_region.x),str(the_region.y)))
    region_card = gamecontrols.Card(x=0, y=ypos, id=id, contents=region_surface)

def generate_golem_button(the_golem: golem.Golem, id: str, ypos: int=0, enabled: bool=True, target: bool=False) -> gamecontrols.Button:
    button_is_enabled = True
    if target:
        if s.active_army().ap < s.active_attack_options['ap']:
            button_is_enabled = False
    else:
        if not enabled or the_golem.army != s.active_army().name:
            button_is_enabled = False
    army_name_surface, army_name_rect = font.render(the_golem.army, the_golem.color)
    lineheight = int(army_name_rect.height * 1.5)
    indent = 2 if target else 1
    golem_surface = pygame.Surface(((WIDTH * 1/4) - indent * 2 * MARGINS, 2 * MARGINS + 3 * lineheight))
    if button_is_enabled:
        golem_surface.fill(gamecontrols.fix_color(COLORS.mantle))
    else:
        not_enabled_color = gamecontrols.lighten_color(gamecontrols.fix_color(COLORS.mantle))
        golem_surface.fill(gamecontrols.fix_color(COLORS.mantle))
        pygame.draw.rect(surface=golem_surface, color=not_enabled_color, rect=golem_surface.get_rect(), border_radius=gamecontrols.BUTTON_RADIUS)

    if target:
        to_hit = s.calculate_to_hit(target=the_golem)
        golem_surface.blit(font.render("{name}: {to_hit}% to hit".format(name=the_golem.name, to_hit=to_hit), \
                                       gamecontrols.fix_color(COLORS.text))[0], (MARGINS,MARGINS))
    else:
        golem_surface.blit(font.render(the_golem.name, gamecontrols.fix_color(COLORS.text))[0], (MARGINS,MARGINS))

    golem_surface.blit(army_name_surface, (golem_surface.get_width() - army_name_rect.width - MARGINS,MARGINS))
    golem_surface.blit(font.render("{size}, {hp} health, {armor} armor, {dodge} dodge".format(
        size=the_golem.size, hp=the_golem.health, armor=the_golem.armor, dodge=the_golem.dodge
    ), gamecontrols.fix_color(COLORS.text))[0], (MARGINS,MARGINS + lineheight))
    golem_abilities = "Mov: {}".format(', '.join(the_golem.get_movement_options().keys()))
    golem_abilities += ", Atk: {}".format(', '.join(the_golem.get_attack_options().keys()))
    golem_surface.blit(font.render(golem_abilities, gamecontrols.fix_color(COLORS.text))[0], (MARGINS, MARGINS + lineheight * 2))
    if button_is_enabled:
        return gamecontrols.Button(x=indent * MARGINS, y=ypos, id=id, contents=golem_surface, color=the_golem.color, callback=handle_golem_button)
    else:
        return gamecontrols.Button(x=indent * MARGINS, y=ypos, id=id, contents=golem_surface, color=the_golem.color, callback=handle_golem_button, enabled=False)

def generate_ability_button(ability: str, index: int, attributes: dict, ypos: int = 0, enabled: bool=True) -> gamecontrols.Button:
    global s
    ability_details = list()
    ability_string = ability
    if s.active_army().ap < attributes['ap']: 
        enabled = False
    if ability == 'Walk' or ability == 'Fly':
        ability_string += ": {ap} AP, {mp} MP".format( 
                                        full=ability, 
                                        ap=attributes['ap'],
                                        mp=attributes['mp']
                                        )
        if 'nimble' in attributes and attributes['nimble']:
            ability_string += ", nimble"
        ability_details.append(font.render(ability_string, gamecontrols.fix_color(COLORS.text))[0])
    else:
        ability_string += ": {ap} AP".format(ap=attributes['ap'])
        ability_details.append(font.render(ability_string, gamecontrols.fix_color(COLORS.text))[0])
        if attributes['range'] > 0:
            attack_string = "{tohit}% base to hit, {damage} dmg, {range} range".format(
                tohit=attributes['tohit'], damage=attributes['damage'], range=attributes['range'])
        else:
            attack_string = "{tohit}% base to hit, {damage} dmg, melee".format(
                tohit=attributes['tohit'], damage=attributes['damage'])
        ability_details.append(font.render(attack_string, gamecontrols.fix_color(COLORS.text))[0])
        for line in word_wrap(the_string=attributes['description'], max_char_length=40):
            ability_details.append(font.render(line, gamecontrols.fix_color(COLORS.text))[0])
        
    if 'cooldown_refresh' in attributes and attributes['cooldown_refresh']:
        show_s = 's' if attributes['cooldown_refresh'] != 1 else ''
        ability_details.append(font.render('Cooldown in {rounds} round{s}'.format( rounds=attributes['cooldown_refresh'], s=show_s), gamecontrols.fix_color(COLORS.text))[0])

    ability_surface =  pygame.Surface((ui.get_rect().width - 4 * MARGINS, MARGINS + len(ability_details) * FONTSIZE + MARGINS))
    if enabled:
        ability_surface.fill(COLORS.mantle.hex)
    else:
        not_enabled_color = gamecontrols.lighten_color(gamecontrols.fix_color(COLORS.mantle))
        ability_surface.fill(COLORS.mantle.hex)
        pygame.draw.rect(surface=ability_surface, color=not_enabled_color, rect=ability_surface.get_rect(), border_radius=gamecontrols.BUTTON_RADIUS)
    for i, ad in enumerate(ability_details):
        ability_surface.blit(ad, (MARGINS, MARGINS + i * FONTSIZE))

    if s.active_turn_state == scenario.turn_states.SELECT_MOVEMENT_LOCATION or s.active_turn_state == scenario.turn_states.SELECT_ATTACK_TARGET:
        cancel, cancel_rect = font.render("Cancel", gamecontrols.fix_color(COLORS.red))
        ability_surface.blit(cancel, (ability_surface.get_width() - cancel_rect.width - MARGINS, MARGINS))

    return gamecontrols.Button(x=2 * MARGINS, y=ypos, id="{}|{}".format(ability, str(index)), contents=ability_surface, color=gamecontrols.fix_color(COLORS.text), callback=handle_ability_button, enabled=enabled)

def generate_combat_result_card(combat_result: combat.CombatResult):
    global s, combat_result_card, combat_result_card_ypos
    combat_result_text = list()
    combat_result_text.append(font.render("Roll: {roll} vs To-Hit: {to_hit}".format(roll=combat_result.roll, to_hit=combat_result.to_hit), gamecontrols.fix_color(COLORS.text))[0])
    if combat_result.hit:
        combat_result_text.append(font.render("Attack hits for {damage} damage.".format(damage=combat_result.damage), gamecontrols.fix_color(COLORS.text))[0])
    else:
        combat_result_text.append(font.render("Attack misses.", gamecontrols.fix_color(COLORS.text))[0])
    if s.active_attack_target.health <= 0:
        combat_result_text.append(font.render("{name} is destroyed.".format(name=s.active_attack_target.name), gamecontrols.fix_color(COLORS.text))[0])
    else:
        combat_result_text.append(font.render("{name} has {health} health remaining.".format(name=s.active_attack_target.name,health=s.active_attack_target.health), gamecontrols.fix_color(COLORS.text))[0])
    combat_result_card_contents = pygame.Surface((ui.get_rect().width, MARGINS + len(combat_result_text) * FONTSIZE + MARGINS ))
    combat_result_card_contents.fill(COLORS.mantle.hex)
    for i, rd in enumerate(combat_result_text):
        combat_result_card_contents.blit(rd, (MARGINS * 3, MARGINS + i * FONTSIZE))
    combat_result_card = gamecontrols.Card(x=0, y=combat_result_card_ypos, id="combat_result", contents=combat_result_card_contents)

def generate_end_turn_button() -> gamecontrols.Button:
    text_surface, text_rect = font.render("End turn", gamecontrols.fix_color(COLORS.text))
    button_surface = pygame.Surface(((WIDTH * 1/4) - 2 * MARGINS, 2 * MARGINS + text_rect.height))
    button_surface.fill(gamecontrols.fix_color(COLORS.mantle))
    button_surface.blit(text_surface, ( int((button_surface.get_width() - text_rect.width) / 2) , MARGINS))
    return gamecontrols.Button(x=MARGINS, y=ui.get_height() - MARGINS - button_surface.get_height(), id="endturn", \
                               contents=button_surface, color=gamecontrols.fix_color(COLORS.text), callback=handle_end_turn_button)

def reset_buttons():
    global buttons
    buttons = [generate_end_turn_button()]

def handle_mouse():
    global arena, s, mouse_was_just_down, currently_pressed_button, player_card, buttons, combat_result_card
    pointer = pygame.mouse.get_pos()
    if s.active_turn_state == scenario.turn_states.END_OF_MATCH: return pointer
    board_pointer = (pointer[0], pointer[1] - STATUSBAR)
    ui_pointer = (pointer[0] - WIDTH * 3/4, pointer[1]-STATUSBAR)
    mousedown = pygame.mouse.get_pressed()[0]

    if mousedown:
        mouse_was_just_down = True
        if arena.get_rect().collidepoint(board_pointer):
            s.board.handle_mouse_down(pointer=board_pointer)
        elif ui.get_rect().collidepoint(ui_pointer):
            if currently_pressed_button:
                currently_pressed_button.handle_mouse_down(pointer=ui_pointer)
            else:
                for button in buttons:
                    if button.handle_mouse_down(pointer=ui_pointer):
                        currently_pressed_button = button
    elif mouse_was_just_down:
        mouse_was_just_down = False
        something_was_clicked = False
        combat_result_card = None
        if s.active_turn_state == scenario.turn_states.SELECT_MOVEMENT_LOCATION:
            move_to = s.board.handle_mouse_up(pointer=board_pointer, locations=s.active_movement_location_options)
            if type(move_to) == dict:
                something_was_clicked = s.move_active_golem_to_location(x=move_to['x'], y=move_to['y'])
                player_card = None
        else:
            something_was_clicked = s.board.handle_mouse_up(pointer=board_pointer)
        if currently_pressed_button:
            something_was_clicked = something_was_clicked or currently_pressed_button.handle_mouse_up(pointer=ui_pointer)
            currently_pressed_button = None
        if something_was_clicked:
            click_sound.play(loops=0)
    return pointer

def handle_golem_button(text: str):
    global player_card
    match s.active_turn_state:
        case scenario.turn_states.SELECT_GOLEM | scenario.turn_states.SELECT_ACTION:
            x, y, g = text.split('|') 
            selected_golem = s.board.region(x=int(x), y=int(y)).golems()[int(g)]
            s.active_turn_state = scenario.turn_states.SELECT_ACTION
            s.active_golem = selected_golem
            reset_buttons()
        case scenario.turn_states.SELECT_ATTACK_TARGET:
            selected_golem = s.active_attack_target_options[int(text)]
            generate_combat_result_card( combat_result=s.attack(target=selected_golem) )
            player_card = None
            reset_buttons()

def handle_ability_button(text: str):
    global s
    ability_type, index = text.split('|')
    if ability_type == 'Walk' or ability_type == 'Fly':
        if s.active_turn_state == scenario.turn_states.SELECT_MOVEMENT_LOCATION:
            s.active_turn_state = scenario.turn_states.SELECT_ACTION
        else:
            s.populate_movement_options(movement_type=ability_type, movement_options=s.active_golem.get_movement_options()[ability_type][int(index)])
    else:
        if s.active_turn_state == scenario.turn_states.SELECT_ATTACK_TARGET:
            s.active_turn_state = scenario.turn_states.SELECT_ACTION
        else:
            s.populate_attack_target_options(attack_name=ability_type)
    reset_buttons()

def handle_end_turn_button(text: str):
    global player_card, region_card
    reset_buttons()
    player_card = None
    region_card = None
    s.end_turn()

pygame.init()
pygame.mixer.init()
pygame.freetype.init()
init()
main()
pygame.freetype.quit()
pygame.mixer.quit()
pygame.quit()