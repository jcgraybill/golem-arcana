import army, board, golem
import math, random

class CombatResult:
    def __init__(self, to_hit: int = 0, roll: int = 0, hit: bool = False, damage: int = 0):
        self.to_hit = to_hit
        self.roll = roll
        self.hit = hit
        self.damage = damage

def attack(the_board: board.Board, attacker: golem.Golem, attacker_army: army.Army, target: golem.Golem, attack: str) -> CombatResult:
    if attacker.get_attack_options()[attack]['ap'] > attacker_army.ap:
        return CombatResult(to_hit=0, roll=0, hit=False, damage=0)
    damage = 0
    hit = False
    to_hit = calculate_to_hit(the_board=the_board, attacker=attacker, target=target, attack=attack)
    roll = roll_attack_dice()
    if roll <= to_hit or roll % 11 == 0:
        hit = True
        damage = attacker.get_attack_options()[attack]['damage']
        if roll <= to_hit and roll % 11 == 0:
            damage = math.floor(damage * 1.5)
        damage -= target.armor
        target.health -= damage
    if target.health < 0:
        target.health = 0

    attacker_army.ap -= attacker.get_attack_options()[attack]['ap']
    if roll > 0:
        attacker.activate_cooldown(ability=attacker.get_attack_options()[attack])
    return CombatResult(to_hit=to_hit, roll=roll, hit=hit, damage=damage)

def destroy_golem(the_board: board.Board, the_golem: golem.Golem, the_army: army.Army):
    the_board.board[the_golem.y][the_golem.x].remove(the_golem)
    the_army.mana += math.floor(the_golem.apv * .2)
    the_army.golems.remove(the_golem)    

def find_targets_within_range(the_board: board.Board, attacker: golem.Golem, attack: str) -> list:
    targets = list()
    if attacker.get_attack_attribute(attack=attack, attribute='range') == 0:
        for target in the_board.board[attacker.y][attacker.x].golems():
            if target.army != attacker.army:
                targets.append(target)
    else:
        for r in the_board.regions():
            if r.coords() != attacker.coords():
                for target in r.golems():
                    if target.army != attacker.army:
                        if range_to_target(the_board=the_board, attacker=attacker, target=target, attack=attack) <= attacker.get_attack_attribute(attack=attack, attribute='range'):
                            targets.append(target)                                                    
    return targets

def range_to_target(the_board: board.Board, attacker: golem.Golem, target: golem.Golem, attack: str) -> int:
    if target.coords() == attacker.coords():
        return 0
    range = math.floor(math.dist(attacker.coords(), target.coords()))
    range += the_board.board[attacker.y][attacker.x].range_modifier()
    range += the_board.board[target.y][target.x].range_modifier()
    return range

def calculate_to_hit(the_board: board.Board, attacker: golem.Golem, target: golem.Golem, attack: str):
    if attacker.get_attack_attribute(attack=attack, attribute='range') == 0:
        return calculate_melee_to_hit(attacker=attacker, target=target, attack=attack)
    else:
        return calculate_ranged_to_hit(the_board=the_board, attacker=attacker, target=target, attack=attack)

def calculate_melee_to_hit(attacker: golem.Golem, target: golem.Golem, attack: str) -> int:
    if attacker.coords() == target.coords():
        if attacker.army != target.army:
            if attacker.get_attack_attribute(attack=attack, attribute='range') == 0:
                return attacker.get_attack_attribute(attack=attack, attribute='tohit') - target.dodge
    return -1

def calculate_ranged_to_hit(the_board: board.Board, attacker: golem.Golem, target: golem.Golem, attack: str) -> int:
    to_hit = -1
    if attacker.get_attack_attribute(attack=attack, attribute='range') > 0:
        if attacker.coords() != target.coords():
            if range_to_target(the_board=the_board, attacker=attacker, target=target, attack=attack) <= attacker.get_attack_attribute(attack=attack, attribute='range'):
                if not is_target_blocked(the_board=the_board, attacker=attacker, target=target, attack=attack):
                    to_hit = attacker.get_attack_attribute(attack=attack, attribute='tohit')- target.dodge
                    if the_board.board[target.y][target.x].is_contested():
                        to_hit -= 20
                    to_hit += the_board.board[target.y][target.x].ranged_accuracy_modifier()
                    to_hit += the_board.board[attacker.y][attacker.x].ranged_accuracy_modifier()
                    for r in the_board.regions():
                        if is_region_in_line_of_sight(region=r.coords(), point_a=attacker.coords(), point_b=target.coords()):
                            if r.coords() == attacker.coords():
                                to_hit += 0
                            elif r.coords() == target.coords():
                                to_hit -= r.cover_for_golem_size(attacker.size)
                            else:
                                to_hit -= r.intervening_cover_for_golem_size(attacker.size)
    return to_hit

def is_region_in_line_of_sight(region: tuple, point_a: tuple, point_b: tuple) -> bool:
    X, Y, RADIUS = 0,1,1

    if region[X] > max(point_a[X], point_b[X]): return False
    if region[Y] > max(point_a[Y], point_b[Y]): return False
    if region[X] < min(point_a[X], point_b[X]): return False
    if region[Y] < min(point_a[Y], point_b[Y]): return False

    if len(region) < 2 or len(point_a) < 2 or len(point_b) < 2: return False

    if point_a[X] == point_b[X]: 
        slope = 1e12
    else:
        slope = (point_b[Y] - point_a[Y]) / (point_b[X] - point_a[X])

    y_intercept = point_a[Y] - slope * point_a[X]

    A = 1 + slope**2
    B = 2 * (slope * (y_intercept - region[Y]) - region[X])
    C = region[X]**2 + (y_intercept - region[Y])**2 - RADIUS**2

    discriminant = B**2 - 4 * A * C
    return True if discriminant >= 0 else False

def is_target_blocked(the_board: board.Board, attacker: golem.Golem, target: golem.Golem, attack: str) -> bool:
    for r in the_board.regions():
        if is_region_in_line_of_sight(region=r.coords(), point_a=attacker.coords(), point_b=target.coords()):
            if r.block_los(): 
                return True
            if r.block_los_unelevated_attacker(): 
                if r.coords() != target.coords() and \
                    not the_board.board[attacker.y][attacker.x].is_elevated():
                    return True            
    return False

def roll_attack_dice():
    return random.randint(0,99)