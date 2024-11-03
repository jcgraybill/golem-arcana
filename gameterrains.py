import pygame, random

image_dir = 'terrain/'

class Terrains:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.error_image = pygame.Surface((self.w,self.h))
        self.error_image.fill((0,0,0))
        self.assign(['t00', 't01', 't02'], terrain='Plains', cover='No cover')
        self.assign(['t03', 't04', 't05', 't06'], terrain='Plains', cover='Ground cover')
        self.assign(['t07', 't08', 't09', 't10', 't11'], terrain='Plains', cover='Medium cover')
        self.assign(['t12', 't13'], terrain='Hills', cover='No cover')
        self.assign(['t14'], terrain='Hills', cover='Ground cover')
        self.assign(['t15'], terrain='Hills', cover='Medium cover')
        self.assign(['t16', 't17'], terrain='Mountains', cover='No cover')
        self.assign(['t18', 't19', 't20', 't21'], terrain='Shallow water', cover='No cover')
        self.assign(['t22', 't23'], terrain='Deep water', cover='No cover')
        self.assign(['t24'], terrain='Miasma swamp', cover='No cover')
        self.assign(['t25'], terrain='The Pit', cover='No cover')
        self.assign(['t26'], terrain='Map Edge', cover='No cover')
        self.assign(['t27', 't28'], terrain='Plains', cover='Heavy cover1')
        self.assign(['t29', 't30'], terrain='Plains', cover='Heavy cover2')

    def assign(self, images: list, terrain: str, cover: str="No cover", obstructions: int=0):
        if obstructions == 1 or obstructions == 2: cover += str(obstructions)
        if not hasattr(self, 'i') or type(self.i) != dict:
            self.i = dict()
        if not terrain in self.i.keys() or type(self.i[terrain]) != dict:
                self.i[terrain] = dict()
        if not cover in self.i[terrain] or type(self.i[terrain][cover]) != list:
             self.i[terrain][cover] = list()
        for image in images:
            self.i[terrain][cover].append(pygame.image.load(image_dir + image + '.jpeg'))
            
    def image(self, terrain: str, cover: str="No cover", obstructions: int=0) -> pygame.Surface:
        if obstructions == 1 or obstructions == 2: cover += str(obstructions)
        if not terrain in self.i.keys(): return self.error_image
        if not cover in self.i[terrain].keys(): return self.error_image
        if len(self.i[terrain][cover]) == 0: return self.error_image
        random_selection = random.randint(0,len(self.i[terrain][cover]) - 1)
        terrain_surface = pygame.Surface.copy(self.i[terrain][cover][random_selection])
        random_rotation = random.randint(0,3) * 90
        if obstructions == 1 or obstructions == 2:
            rotated_surface = terrain_surface
        else:
            rotated_surface = pygame.transform.rotate(terrain_surface, random_rotation)             
        scaled_surface = pygame.transform.smoothscale(rotated_surface, (self.w, self.h))
        return scaled_surface