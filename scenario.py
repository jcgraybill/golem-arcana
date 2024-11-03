import army, board, combat, golem, movement
import enum

class turn_states(enum.Enum):
    SELECT_GOLEM                        = 0
    SELECT_ACTION                       = 1
    SELECT_MOVEMENT_ACTION              = 2
    SELECT_MOVEMENT_LOCATION            = 3
    SELECT_ATTACK                       = 4
    SELECT_ATTACK_TARGET                = 5
    END_OF_MATCH                        = 6

class Scenario():
    def __init__(self):
        self.title = str()
        self.description = str()
        self.__armies = dict()
        self.__army_turn_order = list()
        self.__army_turn_order_index = 0
        self.round = 1
        self.board = board.Board
        self.ap = 4
        self.victor = None

        self.active_turn_state = turn_states.SELECT_GOLEM
        self.active_golem = golem.Golem

        self.active_movement_type = str()
        self.active_movement_options = dict()
        self.active_movement_location_options = list()

        self.active_attack_name = str()
        self.active_attack_options = dict()
        self.active_attack_target_options = list()
        self.active_attack_target = golem.Golem

    def check_for_victory_condition(self):
        armies_with_golems = 0
        for a in self.armies():
            if len(a.golems) > 0:
                armies_with_golems += 1
                self.victor = a
        if armies_with_golems == 1:
            self.active_turn_state = turn_states.END_OF_MATCH
        else:
            self.victor = None

    def add_board(self, w: int, h: int):
        self.board = board.Board(w=w,h=h)
        
    def add_army(self, the_army: army.Army):
        the_army.set_ap(self.ap)
        self.__armies[the_army.name] = the_army
        self.__army_turn_order.append(the_army.name)

    def get_army(self, name: str):
        if name in self.__armies.keys():
            return self.__armies[name]

    def active_army(self) -> army.Army:
        return self.__armies[self.__army_turn_order[self.__army_turn_order_index]]

    def armies(self) -> list[army.Army]:
        army_list = list()
        for i in range(len(self.__army_turn_order)):
            army_list.append(self.__armies[self.__army_turn_order[i]])
        return army_list

    def populate(self):
       # TODO: remove all golems to make this idempotent
       for a in self.__armies.values():
            for g in a.golems:
                self.board.region(g.x, g.y).add(g)        

    def populate_movement_options(self, movement_type: str, movement_options: dict):
        self.active_movement_type = movement_type
        self.active_movement_options = movement_options
        self.active_turn_state = turn_states.SELECT_MOVEMENT_LOCATION
        self.active_movement_location_options = movement.find_valid_moves(the_board=self.board, 
                                           starting_region=(self.active_golem.x, self.active_golem.y), 
                                           move_type=movement_type,
                                           current_golem_army=self.active_army().name, 
                                           movement_values=movement_options,
                                           current_golem_base_size=self.active_golem.base_size
                                           )

    def populate_attack_target_options(self, attack_name: str):
        self.active_turn_state = turn_states.SELECT_ATTACK_TARGET
        self.active_attack_name = attack_name
        self.active_attack_options = self.active_golem.get_attack_options()[attack_name]
        self.active_attack_target_options = combat.find_targets_within_range(the_board=self.board, \
                                                    attacker=self.active_golem, attack=self.active_attack_name)

    def calculate_to_hit(self, target: golem.Golem) -> int:
        return combat.calculate_to_hit(the_board=self.board, attacker=self.active_golem, \
                                       target=target, attack=self.active_attack_name)

    def attack(self, target: golem.Golem) -> combat.CombatResult:
        self.active_attack_target = target
        combat_result = combat.attack(the_board=self.board, attacker=self.active_golem, \
                        attacker_army=self.active_army(), target=target, attack=self.active_attack_name)
        if target.health <= 0:
            combat.destroy_golem(the_board=self.board, the_golem=target, \
                            the_army=self.get_army(name=target.army))
            self.check_for_victory_condition()
        return combat_result

    def move_active_golem_to_location(self, x: int, y: int) -> bool:
        if self.active_turn_state == turn_states.SELECT_MOVEMENT_LOCATION and \
            y <= len(self.active_movement_location_options) and x < len(self.active_movement_location_options[y]) and \
            isinstance(self.active_golem, golem.Golem) and self.active_movement_type and type(self.active_movement_options) == dict and \
            self.active_army().ap >= self.active_movement_options['ap']:
            self.active_turn_state = turn_states.SELECT_GOLEM
            self.board.deselect_all()
            result = movement.move(the_board=self.board, the_golem=self.active_golem, the_army=self.active_army(),
                            to_region=(x,y), move_type=self.active_movement_type, move_options=self.active_movement_options)
            self.active_movement_type = str()
            self.active_movement_options = dict()
            self.active_movement_location_options = list()
            self.active_golem = None
            return result
        else:
            return False
        
    def end_turn(self):
        self.active_army().end_turn()
        self.__army_turn_order_index += 1
        self.__army_turn_order_index %= len(self.__army_turn_order)
        if self.__army_turn_order_index == 0:
                 self.round += 1
        for i in range(len(self.__army_turn_order)):
            self.__armies[self.__army_turn_order[i]].is_current = True if i == self.__army_turn_order_index else False
        self.board.begin_turn(the_army=self.active_army())
        self.active_turn_state = turn_states.SELECT_GOLEM
        if self.active_golem != None:
            self.active_golem.display_override = None
        self.active_golem = None
        self.active_movement_location_options = list()
        self.active_movement_type = str()
        self.active_movement_options = dict()
        return

# Each army has a faction:
# Golems have an Arcana. Each faction is limited to certain arcana
# The Durani Empire: Durani, Urugal, Zikia
# The Gudanna Dominion: Gudanna, Urugal, Zikia
# The Mercenary Kings: Urugal, Zikia
# APV: 500, 1000, 2000, or 3000
# Army has VPs    
# Title & Description
# Player Positions - 2 to 8
# Map tile layout
# Deployment zones
# Capture, Mana well regions
# Victory conditions
# VP for golem destruction: 1 constructs/warsprites, 2 ogres, 3 titans, 5 colossi
# VP for capture regions
# VP for objectives
# Game end: last man standing, vp total, objective completion
# deployment/turn order: Lowest->higest APV, Player Position Order, Random
# Golems can be held off-board