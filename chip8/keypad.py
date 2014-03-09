'''
    Basic implementation of an emulator of Chip8 in python
    to research low level purpose
    
    More info about tech spec: http://en.wikipedia.org/wiki/CHIP-8
        or http://es.wikipedia.org/wiki/CHIP-8
'''

__author__ = "Martin Dimondo"
__license__ = "Revised BSD"
__email__ = "martin.dimondo@gmail.com"


import sys
import pygame
from pygame.locals import *


KEYMAP = {
    K_1: 0x1, K_2: 0x2, K_3: 0x3, K_4: 0x4,
    K_q: 0x5, K_w: 0x6, K_e: 0x7, K_r: 0x8,
    K_a: 0x9, K_s: 0xA, K_d: 0xB, K_f: 0xC,
    K_z: 0xD, K_x: 0xE, K_c: 0xF
}


class Chip8Keypad(object):
    def __init__(self):
        self.k_presseds = []

    def wait_for_keypress(self):
        key = None
        while not key:
            key = self.check_keys()
        return key

    def is_keypressed(self, key):
        return key in self.k_presseds

    def check_keys(self):
        key = None
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = event.key
                if event.key == pygame.locals.K_ESCAPE:
                    self.k_presseds.append(key)
                else:
                    key = KEYMAP.get(key)
                    if key:
                        self.k_presseds.append(key)
            if event.type == pygame.KEYUP:
                key_remove = KEYMAP.get(event.key)
                if key_remove in self.k_presseds:
                    self.k_presseds.remove(key_remove)
        return key
    
    def is_esc_pressed(self):
        return self.is_keypressed(pygame.locals.K_ESCAPE)