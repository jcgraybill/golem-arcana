import copy

class Army():
    def __init__(self, name: str, color: str, golems: list):
        self.name = name
        self.__base_ap = 0
        self.ap = 0
        self.mana = 0
        self.color = color
        self.golems = list()
        self.apv = 0
        self.vp = 0
        for golem in golems:
            self.golems.append( copy.deepcopy(golem) )
            self.apv += golem.apv
            golem.army = self.name
        for golem in self.golems:
            golem.color = self.color
            golem.army  = self.name
    
    def __str__(self) -> str:
        return self.name

    def set_ap(self, ap: int):
        self.__base_ap = ap
        self.ap = self.__base_ap

    def end_turn(self):
        self.mana += self.ap
        self.ap = self.__base_ap
        for golem in self.golems:
            golem.end_turn()