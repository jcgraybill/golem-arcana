import json, copy, golem, manawell

MAX_CAPACITY = 4

terrains, covers = dict(), dict()

def init():
    global terrains, covers
    with open('terrains.json') as json_data:
        t = json.load(json_data)
        json_data.close()

    terrains = copy.copy(t['terrains'])
    covers   = copy.copy(t['covers'])

class Region():
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
        self.reset()

    def reset(self):
        self.objects = list()
        self.__terrain = "Map Edge"
        self.__cover = "No cover"
        self.__obstructions = 0

    def get_terrain(self) -> str:
        return self.__terrain

    def set_terrain(self, terrain: str) -> bool:
        if terrain in terrains:
            self.__terrain = terrain
            self.set_cover(cover=self.get_cover())
            return True
        else:
            return False

    def get_cover(self) -> str:
        return self.__cover

    def set_cover(self, cover: str) -> bool:
        if cover == "No cover":
            self.__cover = cover
            return True
        elif cover in covers:
            valid_covers_for_terrain = self.__terrain_value(value="Valid cover")
            if type(valid_covers_for_terrain) == list and cover in self.__terrain_value(value="Valid cover"):
                self.__cover = cover
                return True
            else:
                self.__cover = "No cover"
                return False
        else:
            return False

    def get_obstructions(self) -> int:
        return self.__obstructions

    def set_obstructions(self, obstructions: int) -> bool:
        if obstructions == 0:
            self.set_cover(cover="No cover")
            self.__obstructions = obstructions
            return True
        elif obstructions == 1 or obstructions == 2:
            if self.set_cover(cover="Heavy cover"):
                self.__obstructions = obstructions
                return True
            else:
                return False
        else:
            return False

    def __str__(self):
        visible_spaces = 4
        contents = ''
        for o in range(self.__obstructions):
            contents += "O"
            visible_spaces -= 1
        for object in self.golems():
            if visible_spaces <= 0:
                break
            contents += str(object)
            visible_spaces -= 1
        for i in range(visible_spaces):
            contents += ' '
        return contents
           
    def coords(self) -> tuple:
        return (self.x, self.y)
    
    def display(self):
        contents = self.__terrain[0]
        contents += self.__cover[0]
        visible_spaces = 2
        for object in self.objects:
            if visible_spaces <= 0:
                break
            if isinstance(object, manawell.ManaWell) and object.visible:
                contents += str(object)
                visible_spaces -= 1
        for i in range(visible_spaces):
            contents += ' '
        return contents

    def add(self, object):
        if self.occupancy() <= MAX_CAPACITY or isinstance(object, manawell.ManaWell):
            self.objects.append(object)

        mana_well = None
        region_contains_golem = False
        for object in self.objects:
            if isinstance(object, manawell.ManaWell):
                mana_well = object
            elif isinstance(object, golem.Golem):
                region_contains_golem = True
        if mana_well and region_contains_golem:
            mana_well.visible = True

    def remove(self, object):
        self.objects.remove(object)

    def golems(self) -> list[golem.Golem]:
        golems = list()
        for object in self.objects:
            if isinstance(object, golem.Golem):
                golems.append(object)
        return golems

    def mana_well(self):
        for object in self.objects:
            if isinstance(object, manawell.ManaWell) and object.visible:
                return object

    def is_contested(self) -> bool:
        army_name = ""
        for g in self.golems():
            if army_name == "":
                army_name = g.army
            elif army_name != g.army:
                return True
        return False

    def occupancy(self) -> int:
        occupancy = 0
        occupancy += self.__obstructions
        for g in self.golems():
            occupancy += g.base_size
        return occupancy

    def activate_mana_well(self, army_name: str) -> int:
        mana_well = None
        occupied_by_current_army_golems = False
        occupied_by_opposing_army_golems = False
        for object in self.objects:
            if isinstance(object, manawell.ManaWell):
                mana_well = object
            elif isinstance(object, golem.Golem):
                if object.army == army_name:
                    occupied_by_current_army_golems = True
                else:
                    occupied_by_opposing_army_golems = True

        if mana_well and (occupied_by_current_army_golems or occupied_by_opposing_army_golems):
            mana_well.visible = True

        if mana_well and occupied_by_current_army_golems and not occupied_by_opposing_army_golems:
            return mana_well.collect()
        else:
            return 0
    
    def __terrain_value(self, value: str):
        if self.__terrain in terrains and value in terrains[self.__terrain]:
            return terrains[self.__terrain][value]

    def __cover_value(self, value: str):
        cover = self.__cover
        if self.__terrain_value('cover_type'):
            cover = self.__terrain_value('cover_type')
        if cover in covers and value in covers[cover]:
            return covers[cover][value]

    def mp_to_enter(self, move_type: str) -> int:
        terrain_attributes = self.__terrain_value('mp')
        cover_attributes = self.__cover_value('mp')
        if move_type in terrain_attributes:
            t = terrain_attributes[move_type]
        if move_type in cover_attributes:
            c = cover_attributes[move_type]
        if t and c:
            return max(t,c)
        else:
            return 99

    def cover_for_golem_size(self, golem_size: str) -> int:
        if golem_size in self.__cover_value('cover'):
            return self.__cover_value('cover')[golem_size]
        return 0

    def intervening_cover_for_golem_size(self, golem_size: str) -> int:
        if golem_size in self.__cover_value('intervening'):
            return self.__cover_value('intervening')[golem_size]        
        return 0

    def block_los(self) -> bool:
        return self.__terrain_value('block_los') or False
    
    def block_los_unelevated_attacker(self) -> bool:
        return self.__terrain_value('block_los_unelevated_attacker') or False
    
    def is_elevated(self) -> bool:
        return self.__terrain_value('is_elevated') or False
    
    def can_end_movement_in(self) -> bool:
        return self.__terrain_value('can_end_movement_in') or False

    def breakaway_modifier(self) -> int:
        return self.__terrain_value('breakaway_modifier') or 0
    
    def range_modifier(self) -> int:
        return self.__terrain_value('range_modifier') or 0

    def ranged_accuracy_modifier(self) -> int:
        return self.__terrain_value('ranged_accuracy_modifier') or 0
        
init()