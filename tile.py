import json, copy
import region
tiles = dict()

def init():
    global tiles
    with open('tiles.json') as json_data:
        t = json.load(json_data)
        tiles = copy.copy(t['tiles'])
        json_data.close()

class Tile():
    def __init__(self, tile: str):
        if tile in tiles.keys():
            self.tileset = tiles[tile]['tileset']
            self.regions = list()
            i = 0
            for y in range(3):
                self.regions.append(list())
                for x in range(3):
                    self.regions[y].append(region.Region())
                    self.regions[y][x].set_terrain( terrain = tiles[tile]['regions'][i]['terrain'] )
                    self.regions[y][x].set_cover(cover = tiles[tile]['regions'][i]['cover'] )
                    if 'obstructions' in tiles[tile]['regions'][i]:
                        self.regions[y][x].set_obstructions( obstructions = tiles[tile]['regions'][i]['obstructions'])
                    i += 1
    
    def __str__(self):
        contents = ''
        for y in range(3):
            for x in range(3):
                contents += self.regions[y][x].terrain[0]
            contents += " "
            for x in range(3):
                contents += self.regions[y][x].cover[0]
            contents += " "
            for x in range(3):
                contents += str(self.regions[y][x].obstructions)
            contents += "\n"
        return contents

    def rotate(self, times: int = 1):
        for time in range(times):
            self.regions = list(zip(*self.regions[::-1]))

init()

if __name__ == "__main__":
    for show_tile in sorted(tiles.keys()):
        print(show_tile)
        print(Tile(show_tile))
