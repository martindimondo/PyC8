#!/bin/python
import os
import sys
import pygame
from chip8 import cpu, display

def main():
    pygame.init()
    emulator = cpu.CPUEmulator()
    pygame.display.set_caption("Python Chip8 Emulator")
    emulator.load_program(load_rom(sys.argv[1]))
    emulator.main_loop()
    return 0

def load_rom(game):
    rom_content = []

    with open(game, "rb") as f:
        bytes = f.read()
        for byte in bytes:
            rom_content.append(ord(byte))

    return rom_content
    
if __name__ == '__main__':
    sys.exit(main())
