import pygame, catppuccin, copy, typing

COLORS              = catppuccin.PALETTE.macchiato.colors
WHITE               = (255,255,255)
HOVER               = (166, 173, 200)
BUTTON_RADIUS       = 6

def fix_color(the_color: tuple) -> tuple[int,int,int]:
    return (the_color.rgb.r, the_color.rgb.g, the_color.rgb.b)

def lighten_color(the_color: tuple, by: int = 20) -> tuple[int,int,int]:
    return ( min(the_color[0] + by, 255), min(the_color[1] + by, 255), min(the_color[2] + by, 255) )

class Card():
    def __init__(self, x: int, y: int, id: str, contents: pygame.Surface):
        self.x = x
        self.y = y
        self.id  = id
        self.contents = contents

        self.surface = self.contents
        self.collide_rect = copy.copy(self.surface.get_rect())
        self.collide_rect.x = self.x
        self.collide_rect.y = self.y

    def is_being_pointed_at(self, pointer: tuple[int,int]) -> bool:
        return self.collide_rect.collidepoint(pointer)

    def draw(self, surface=pygame.Surface):
        surface.blit(self.surface, (self.x,self.y))

class Button(Card):
    def __init__(self, x: int, y: int, id: str, contents: pygame.Surface, color: tuple[int,int,int], callback: typing.Callable, enabled: bool=True):
        self.color = color
        self.is_enabled = enabled
        self.callback = callback
        self.is_being_pressed = False
        super().__init__(x=x, y=y, id=id, contents=contents)
        self.enabled_surface = pygame.Surface(self.contents.get_rect().size)
        self.not_enabled_surface = pygame.Surface(self.contents.get_rect().size)
        self.hover_surface = pygame.Surface(self.contents.get_rect().size)
        self.pressed_surface = pygame.Surface(self.contents.get_rect().size)

        self.enabled_surface.blit(self.contents, (0,0))
        pygame.draw.rect(surface=self.enabled_surface, color=self.color, rect=self.enabled_surface.get_rect(), border_radius=BUTTON_RADIUS, width=1)

        self.not_enabled_surface.blit(self.contents, (0,0))
        pygame.draw.rect(surface=self.not_enabled_surface, color=fix_color(COLORS.subtext0), rect=self.not_enabled_surface.get_rect(), border_radius=BUTTON_RADIUS, width=1)
        
        self.surface = self.enabled_surface if self.is_enabled else self.not_enabled_surface

        self.hover_surface.blit(self.contents, (0,0))
        pygame.draw.rect(surface=self.hover_surface, color=self.color, rect=self.hover_surface.get_rect(), border_radius=BUTTON_RADIUS, width=1)
        hover_rect = self.hover_surface.get_rect()
        hover_rect.width  -= 2
        hover_rect.height -= 2
        hover_rect.left   += 1
        hover_rect.top    += 1
        pygame.draw.rect(surface=self.hover_surface, color=HOVER, rect=hover_rect, border_radius=BUTTON_RADIUS, width=1)

        PRESS_DEPTH = 1
        self.pressed_surface.blit(self.contents, (0,0))
        press_rect = self.pressed_surface.get_rect()
        press_rect.width -= PRESS_DEPTH * 2
        press_rect.height -= PRESS_DEPTH * 2
        press_rect.left += PRESS_DEPTH
        press_rect.top += PRESS_DEPTH

        pygame.draw.rect(surface=self.pressed_surface, color=self.color, rect=press_rect, border_radius=BUTTON_RADIUS, width=1)
        hover_rect.left += PRESS_DEPTH
        hover_rect.top += PRESS_DEPTH
        hover_rect.width -= PRESS_DEPTH * 2
        hover_rect.height -= PRESS_DEPTH * 2
        pygame.draw.rect(surface=self.pressed_surface, color=HOVER, rect=hover_rect, border_radius=BUTTON_RADIUS, width=1)

    def hover(self):
        if self.is_being_pressed: return
        self.surface = self.hover_surface if self.is_enabled else self.not_enabled_surface

    def unhover(self):
        if self.is_being_pressed: return
        self.surface = self.enabled_surface if self.is_enabled else self.not_enabled_surface

    def handle_mouse_down(self, pointer=tuple[int,int]):
        if self.is_being_pointed_at(pointer=pointer) and self.is_enabled:
            self.surface = self.pressed_surface
            self.is_being_pressed = True
        else:
            self.is_being_pressed = False
        return self.is_being_pressed
    
    def handle_mouse_up(self, pointer=tuple[int,int] ):
        self.surface = self.enabled_surface if self.is_enabled else self.not_enabled_surface
        self.is_being_pressed = False
        if self.is_being_pointed_at(pointer=pointer):
            self.callback(self.id)
            return True