import army, region, tile

class Board():
    def __init__(self, w: int, h: int):
        self.board = [[region.Region(x,y) for x in range(w)] for y in range(h)]
        self.w = w
        self.h = h

    def __str__(self):
        NEWLINE = '\n'
        HLINE = ('-' * 4) + ('-' * self.w * 5) +  NEWLINE
        XLABELS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        boardstring = HLINE

        boardstring += '|  |'
        for i in range(self.w):
            if i < len(XLABELS):
                boardstring += ' '
                boardstring += XLABELS[i]
                boardstring += '  |'
            else:
                boardstring += '# |'
        
        boardstring += NEWLINE + HLINE
        
        for y in range(self.h):
            boardstring += "|{:2d}|".format(y)
            for x in range(self.w):
                boardstring += str(self.board[y][x])
                boardstring += '|'
            boardstring += NEWLINE
            boardstring += "|  |"
            for x in range(self.w):
                boardstring += self.board[y][x].display()
                boardstring += '|'            
            boardstring += NEWLINE
            boardstring += HLINE

        return boardstring

    def deselect_all(self):
        # TODO - only implemented in the pygame superclass
        return

    def region(self, x: int, y: int):
        if y < len(self.board) and x < len(self.board[y]):
            return self.board[y][x]

    def regions(self) -> list:
        regions = list()
        for row in self.board:
            regions.extend(row)
        return regions

    def begin_turn(self, the_army: army.Army):
        for y in range(self.h):
            for x in range(self.w):
                the_army.mana += self.board[y][x].activate_mana_well(str(the_army))
    
    def reset_terrain(self, to_terrain: str="Map Edge", to_cover: str="No cover"):
        for r in self.regions():
            r.terrain = to_terrain
            r.cover = to_cover
    
    def erase_map(self):
        for r in self.regions():
            r.reset()

    def set_entire_map(self, terrain: str, cover: str):
        for r in self.regions():
            r.set_terrain(terrain=terrain)
            r.set_cover(cover=cover)
            r.set_obstructions(obstructions=0)

    def place_tile(self, the_tile: tile.Tile, origin: tuple=(0,0)):
        for i, row in enumerate(the_tile.regions):
            for j, r in enumerate(row):
                old_r = self.region(x=origin[0] + j, y=origin[1] + i)
                r.x, r.y = old_r.x, old_r.y
                r.set_obstructions(obstructions=old_r.get_obstructions())
                self.board[origin[1] + i][origin[0] + j] = r
