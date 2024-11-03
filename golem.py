import json, copy
import colors

golems = dict()

def init():
    global golems
    with open('golems.json') as json_data:
        g = json.load(json_data)
        json_data.close()

        for golem in g['golems']:
            golems[golem['collectors-number']] = Golem(golem)

class Golem:
    def __init__(self, json_dict: dict):
        self.movement = copy.copy(json_dict['movement'])
        for movements in self.movement.values():
            for actions in movements:
                if 'ap' in actions:
                    actions['base_ap'] = actions['ap']

        self.attacks = copy.copy(json_dict['attacks'])
        for attack in self.attacks.values():
            if 'ap' in attack:
                attack['base_ap'] = attack['ap']

        self.name = json_dict['name']
        self.army = str()
        self.apv = json_dict['apv']
        self.color = str()
        self.health = json_dict['health']
        self.armor = json_dict['armor']
        self.dodge = json_dict['dodge']
        self.size = json_dict['size']
        match self.size:
            case 'Warsprite':
                self.base_size = 1
            case 'Ogre':
                self.base_size = 1
            case 'Titan':
                self.base_size = 2
            case 'Colossus':
                self.base_size = 4

        self.x, self.y = 0,0
        self.display_override = None

    def __str__(self):
        if self.display_override:
            return self.color + self.display_override + colors.reset
        else:
            return self.color + self.name[0] + colors.reset

    def coords(self) -> tuple:
        return (self.x, self.y)

    def get_attack_attribute(self, attack: str, attribute: str):
        if attack in self.get_attack_options().keys():
            if attribute in self.get_attack_options()[attack]:
                return self.get_attack_options()[attack][attribute]

    def get_attack_options(self):
        return copy.copy(self.attacks)

    def get_movement_options(self) -> dict:
        movement_options = dict()
        for movement in sorted(self.movement.keys()):
            if len(self.movement[movement]) > 0:
                movement_options[movement] = copy.copy(self.movement[movement])
        return movement_options
    
    def activate_cooldown(self, ability: dict):
        if not 'ap' in ability.keys(): return
        ability['ap'] *= 2
        if 'cooldown_refresh' in ability.keys() and ability['cooldown_refresh'] > 0:
            ability['cooldown_refresh'] += 1
        elif 'tohit' in ability.keys(): # Attacks
            ability['cooldown_refresh'] = 2
        else: # movement
            ability['cooldown_refresh'] = 1

    def end_turn(self):
        for movements in self.movement.values():
            for actions in movements:
                if 'cooldown_refresh' in actions:
                    if actions['cooldown_refresh'] == 1:
                        actions['cooldown_refresh'] = 0
                        if 'base_ap' in actions and 'ap' in actions:
                            actions['ap'] = actions['base_ap']
                    elif actions['cooldown_refresh'] > 1:
                        actions['cooldown_refresh'] -= 1
        for attack in self.attacks.values():
            if 'cooldown_refresh' in attack:
                if attack['cooldown_refresh'] == 1:
                    attack['cooldown_refresh'] = 0
                    if 'base_ap' in attack and 'ap' in attack:
                        attack['ap'] = attack['base_ap']
                elif attack['cooldown_refresh'] > 1:
                    attack['cooldown_refresh'] -= 1

init()