import board, region, gameterrains
import enum, pygame, pygame.freetype, pygame.gfxdraw

FONTFACE            = "bodoni72smallcapsbook"

MAP_COLORS = {
    "Mana Well": (173, 216, 230),
    "Exhausted Mana Well": (128, 128, 128),
}

class display_modes(enum.Enum):
    DEFAULT         = 0
    NOT_SELECTABLE  = 1
    SELECTABLE      = 2

class GameRegion():
    WHITE    = (216,216,216)
    BLACK    = (0,0,0)
    HOVER    = (166, 173, 200)
    BORDER   = BLACK
    PRESSED  = BLACK
    SELECTED = (0, 200, 0)
    INACTIVE = (64, 64, 64)

    def __init__(self, rect: pygame.Rect, image: pygame.Surface, region: region.Region):
        self.region = region
        self.rect = rect
        PRESSED_DEPTH = 1
        self.pressed_rect = pygame.Rect(rect.left + PRESSED_DEPTH, rect.top + PRESSED_DEPTH, rect.width - PRESSED_DEPTH * 2, rect.height - PRESSED_DEPTH * 2)
        self.image = image
        self.being_pressed = False
        self.selected = False
        pygame.freetype.init()
        self.font = pygame.freetype.SysFont(FONTFACE, int(self.rect.height / 2) - 30 )
    
    def is_being_pointed_at(self, pointer: tuple[int,int]) -> bool:
        if self.region.get_terrain() == "Map Edge": return False
        return self.rect.collidepoint(pointer)
    
    def draw(self, canvas=pygame.Surface, pointer: tuple[int,int]=(0,0), mode: display_modes=display_modes.DEFAULT):
        if self.region.get_terrain() != "Map Edge":
            if mode == display_modes.NOT_SELECTABLE:
                pygame.draw.rect(surface=canvas, color=self.INACTIVE, rect=self.rect)
                pygame.draw.rect(surface=canvas, color=self.BORDER, rect=self.rect, width=1)
            else:
                canvas.blit(self.image, self.rect)

        if not mode == display_modes.NOT_SELECTABLE:
            if self.selected:
                if self.being_pressed:
                    pygame.draw.rect(surface=canvas, color=self.BORDER, rect=self.rect, width=1)
                    pygame.draw.rect(surface=canvas, color=self.SELECTED, rect=self.pressed_rect, width=1)
                else:
                    pygame.draw.rect(surface=canvas, color=self.SELECTED, rect=self.rect, width=1)
            else:
                if self.is_being_pointed_at(pointer=pointer):
                    if self.being_pressed:
                        pygame.draw.rect(surface=canvas, color=self.BORDER, rect=self.rect, width=1)
                        pygame.draw.rect(surface=canvas, color=self.HOVER, rect=self.pressed_rect, width=1)
                    else:
                        pygame.draw.rect(surface=canvas, color=self.HOVER, rect=self.rect, width=1)
                else:            
                    pygame.draw.rect(surface=canvas, color=self.BORDER, rect=self.rect, width=1)

        mana_well = self.region.mana_well()
        if mana_well and mana_well.visible:
            pygame.gfxdraw.filled_circle(canvas, int(self.rect.center[0]), int(self.rect.center[1]), int((self.rect.width / 2) * 0.2), MAP_COLORS['Mana Well'])
            if mana_well.exhausted:
                pygame.gfxdraw.filled_circle(canvas, int(self.rect.center[0]), int(self.rect.center[1]), int((self.rect.width / 2) * 0.2 - 3), MAP_COLORS['Exhausted Mana Well'])
            pygame.gfxdraw.aacircle(canvas, int(self.rect.center[0]), int(self.rect.center[1]), int((self.rect.width / 2) * 0.2), self.INACTIVE)
            pygame.gfxdraw.aacircle(canvas, int(self.rect.center[0]), int(self.rect.center[1]), int((self.rect.width / 2) * 0.2) - 3, self.INACTIVE)
        i, j, quarter, half = 1, 1, int(self.rect.width / 4), int(self.rect.width / 2)

        for o in range(self.region.get_obstructions()):
            if i == 3:
                j = 3
                i = 1
            else:
                i = 3
        for g in self.region.golems():
            pygame.gfxdraw.filled_circle(canvas, int(self.rect.left + i * quarter), int(self.rect.top + j * quarter), int(quarter * 0.8), self.WHITE)
            pygame.gfxdraw.aacircle(canvas, int(self.rect.left + i * quarter), int(self.rect.top + j * quarter), int(quarter * 0.8), self.INACTIVE)
            pygame.gfxdraw.aacircle(canvas, int(self.rect.left + i * quarter), int(self.rect.top + j * quarter), int(quarter * 0.8) - 1, g.color)
            pygame.gfxdraw.aacircle(canvas, int(self.rect.left + i * quarter), int(self.rect.top + j * quarter), int(quarter * 0.8) - 2, g.color)
            pygame.gfxdraw.aacircle(canvas, int(self.rect.left + i * quarter), int(self.rect.top + j * quarter), int(quarter * 0.8) - 3, g.color)
            pygame.gfxdraw.aacircle(canvas, int(self.rect.left + i * quarter), int(self.rect.top + j * quarter), int(quarter * 0.8) - 4, self.INACTIVE)
            label, tx_rect = self.font.render(g.name[0], self.BLACK)
            canvas.blit(label, (self.rect.left + int(i/2) * half + (half - tx_rect.width) / 2, self.rect.top + int(j/2) * half + (half - tx_rect.height) / 2))
            if i == 3:
                j = 3
                i = 1
            else:
                i = 3

class GameBoard(board.Board):
    def __init__(self, w: int, h: int, display_size: tuple[int,int]):
        self.w = w
        self.h = h
        self.region_originally_clicked = None
        self.canvas_width = display_size[0]
        self.canvas_height = display_size[1]
        if self.canvas_width / self.w > self.canvas_height / self.h:
            region_dimensions = self.canvas_height / self.h
            self.display_width = region_dimensions * self.w
            self.display_height = region_dimensions * self.h
            self.origin = ( (self.canvas_width - region_dimensions * self.w ) / 2, 0)
        else:
            region_dimensions = self.canvas_width / self.w
            self.display_width = region_dimensions * self.w
            self.display_height = region_dimensions * self.h
            self.origin = (0, (self.canvas_height - region_dimensions * self.h ) / 2 )
        self.rect_width = self.display_width / self.w
        self.rect_height = self.display_height / self.h
        self.terrains = gameterrains.Terrains(w=self.rect_width, h=self.rect_height)
        super().__init__(w=w, h=h)
        self.refresh_display()

    def refresh_display(self):
        self.display = list()
        for y in range(self.h):
            self.display.append(list())
            for x in range(self.w):
                self.display[y].append(GameRegion(
                    rect = pygame.Rect(self.origin[0] + x * self.rect_width, self.origin[1] + y * self.rect_height, self.rect_width, self.rect_height ),
                    image=self.terrains.image(terrain=self.region(x,y).get_terrain(), cover=self.region(x,y).get_cover(), obstructions=self.region(x,y).get_obstructions()),
                    region = self.region(x,y)
                ))

    def get_display_regions(self) -> list[GameRegion]:
        regions = list()
        for row in self.display:
            regions.extend(row)
        return regions

    def display_board(self, canvas=pygame.Surface, pointer: tuple[int,int]=(0,0), locations: list=[]):
        for r in self.get_display_regions():
            if len(locations) > 0:
                if locations[r.region.y][r.region.x] and r.region.get_terrain() != "Map Edge":
                    r.draw(canvas=canvas, pointer=pointer, mode=display_modes.SELECTABLE)
                else:
                    r.draw(canvas=canvas, pointer=pointer, mode=display_modes.NOT_SELECTABLE)
            else:
                if r.region.get_terrain() == "Map Edge":
                    r.draw(canvas=canvas, pointer=pointer, mode=display_modes.NOT_SELECTABLE)
                else:
                    r.draw(canvas=canvas, pointer=pointer, mode=display_modes.DEFAULT)

    def region_being_pointed_at(self, pointer: tuple[int,int]=(0,0)):
        for r in self.get_display_regions():
            if r.is_being_pointed_at(pointer=pointer):
                return r
    
    def selected_region(self):
        for r in self.get_display_regions():
            if r.selected:
                return r.region
    
    def deselect_all(self):
        for r in self.get_display_regions():
            r.selected = False
            r.being_pressed = False

    def handle_mouse_down(self, pointer: tuple[int,int]=(0,0)):
        if self.region_originally_clicked == None:
            for r in self.get_display_regions():
                if r.is_being_pointed_at(pointer=pointer):
                    self.region_originally_clicked = r
                    r.being_pressed = True
        else:
            for r in self.get_display_regions():
                if r == self.region_originally_clicked:
                    if r.is_being_pointed_at(pointer=pointer):
                        r.being_pressed = True
                    else:
                        r.being_pressed = False

    def handle_mouse_up(self, pointer: tuple[int,int]=(0,0), locations: list=[]):
        region_just_selected = None
        for r in self.get_display_regions():
            restrict_to_valid_move_locations = False
            is_valid_move_location = False
            if len(locations) > 0:
                restrict_to_valid_move_locations = True
                is_valid_move_location = locations[r.region.y][r.region.x]
            if not restrict_to_valid_move_locations:
                if r.selected == True and r.being_pressed == True and r == self.region_originally_clicked:
                    r.selected = False
                elif r.selected == False and r.being_pressed == True and r == self.region_originally_clicked:
                    r.selected = True
                    region_just_selected = r
            elif restrict_to_valid_move_locations and is_valid_move_location:
                if r.being_pressed == True and r == self.region_originally_clicked:
                    r.being_pressed = False
                    self.region_originally_clicked = None
                    return {'x': r.region.x, 'y': r.region.y}
            r.being_pressed = False            
        self.region_originally_clicked = None
        if region_just_selected:
            for r in self.get_display_regions():
                if not r == region_just_selected:
                    r.selected = False
            region_just_selected = None
            return True