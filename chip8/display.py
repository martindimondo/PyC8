'''
    Display functions
    
    To improve this, you can implement many renders 
    using a super class Chip8Render and subclasses of it
    charged to render 2d (OpenGl, Sdl, etc).
'''

__author__ = "Martin Dimondo"
__license__ = "Revised BSD"
__email__ = "martin.dimondo@gmail.com"

import pygame
from pygame.locals import *

SCREEN_RESOLUTION = (64, 32)
FONT_ADDRESS = 0x0050


FONT_SPRITES = [
    0x60, 0x90, 0x90, 0x90, 0x60, # 0
    0x60, 0x20, 0x20, 0x20, 0x70, # 1
    0xE0, 0x10, 0x60, 0x80, 0xF0, # 2
    0x60, 0x10, 0x20, 0x10, 0x60, # 3
    0xA0, 0xA0, 0xF0, 0x20, 0x20, # 4
    0xF0, 0x80, 0xE0, 0x10, 0xE0, # 5
    0x60, 0x80, 0xE0, 0x90, 0x60, # 6
    0x70, 0x10, 0x30, 0x10, 0x10, # 7
    0x60, 0x90, 0x60, 0x90, 0x60, # 8
    0x70, 0x90, 0x70, 0x10, 0x10, # 9
    0x60, 0x90, 0x90, 0xF0, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0x70, 0x80, 0x80, 0x80, 0x70, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xE0, 0x80, 0xC0, 0x80, 0xE0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80, # F
]


bg = pygame.image.load("chip8/images/background.jpg")
bg_rect = bg.get_rect()


class Chip8Screen(object):
    def __init__(self, fullscreen=False, pixel_size=10):
        pygame.display.init()
        self.pixel = pixel_size
        flags = 0
        if fullscreen:
            flags = pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(
                map(lambda x: x * pixel_size, SCREEN_RESOLUTION),
                flags)
        self.clear()
    
    def clear(self):
        self.screen_buffer = [[0x0] * SCREEN_RESOLUTION[0]] * SCREEN_RESOLUTION[1]
        
    def draw(self, x, y, sprite):
        flipped = 0
        import pdb; pdb.set_trace()
        for j, byte in enumerate(sprite):
            for i in range(8):
                bit = (byte >> i) & 0x1
                if not flipped:
                    flipped = self.screen_buffer[y + j][x + i] ^ bit
                self.screen_buffer[y + j][x + i] = bit
        return flipped
    
    def update(self):
        self.screen.blit(bg, (0, 0))
        for j, row in enumerate(self.screen_buffer):
            for i, on in enumerate(row):
                if on == 1:
                    pygame.draw.rect(self.screen, (255, 255, 255), 
                        (i * self.pixel,  j * self.pixel, self.pixel, self.pixel))
        pygame.display.flip()
