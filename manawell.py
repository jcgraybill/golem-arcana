import colors

STARTING_MANA = 12
COLLECTION_AMOUNT = 6

class ManaWell:
    def __init__(self):
        self.mana = STARTING_MANA
        self.visible = True
        self.exhausted = False
    def __str__(self) -> str:
        if self.visible:
            if self.exhausted:
                return colors.fg.lightgrey + 'M' + colors.reset
            else:
                return colors.fg.blue + 'M' + colors.reset
        else:
            return ''
    
    def collect(self):
        if self.mana > COLLECTION_AMOUNT:
            self.mana -= COLLECTION_AMOUNT
            return COLLECTION_AMOUNT
        elif self.mana == COLLECTION_AMOUNT:
            self.mana -= COLLECTION_AMOUNT
            self.exhausted = True
            return COLLECTION_AMOUNT
        elif self.mana > 0:
            remainder = self.mana
            self.mana -= self.mana
            self.exhausted = True
            return remainder
        else:
            return 0