'''
    Basic implementation of an emulator of Chip8 in python
    to research low level purpose
    
    More info about tech spec: http://en.wikipedia.org/wiki/CHIP-8
        or http://es.wikipedia.org/wiki/CHIP-8
'''

__author__ = "Martin Dimondo"
__license__ = "Revised BSD"
__email__ = "martin.dimondo@gmail.com"

from datetime import datetime
import logging
import time

import display
import keypad
import memory
import util
import pygame
import operations


CLOCK_RATE = 60 # Run at 60hz
CPU_REGISTERS = 16


logging.basicConfig(level=logging.INFO)


class CPUEmulator(object):
    
    executor = operations.Executor(operations.op_map)

    def __init__(self):
        self.pc = memory.MEMORY_START # Program Counter
        self.delay_timer = 0
        self.sound_timer = 0
        self.interrupted = False
        self.screen = display.Chip8Screen()
        self.memory = memory.Chip8Memory()
        self.keypad = keypad.Chip8Keypad()
        self._init_mem()
        self._init_registers()
        
    def _init_registers(self):
        logging.info("Initializing cpu registers")
        self.index_reg = 0
        self.v = [0x0] * CPU_REGISTERS
        self.stack = []
        self.op = None
        
    def _init_mem(self):
        logging.info("Initializing memory")
        self.memory.write_array(memory.FONT_ADDRESS, display.FONT_SPRITES)
    
    def load_program(self, prog):
        logging.info("Loading program into memory")
        self.memory.write_array(memory.MEMORY_START, prog)

    def main_loop(self):
        logging.info("Running main loop emulator...")
        clock = pygame.time.Clock()
        while True:
            clock.tick(CLOCK_RATE)
            self.screen.update()
            self.keypad.check_keys()                
            self.cycle()            

            if self.delay_timer > 0:
                self.delay_timer -= 1
                logging.debug('Delay timer: %s' % self.delay_timer)

            if self.sound_timer > 0:
                if self.sound_timer == 1:
                    logging.debug('BEEP - Sound timer: %s' % self.sound_timer)
                    print('\a') # Nonzero value produce a beep in a Chip8
                            # better ... shoot to the computer speaker
                self.sound_timer -= 1

            if self.keypad.is_esc_pressed():
                raise InterruptedException('CPU execution cycle was interrupted')
            
    def cycle(self):
        self.op = self._fetch()
        logging.debug('Current OpCode: 0x%02x' % self.op)
        self.executor.execute(self, self.op)
        
    def _fetch(self):
        '''
            Fetch opcode bytes
        '''
        byte_a = self.memory.get_byte(self.pc) << 8 # shift to left 8 bits
        byte_b = self.memory.get_byte(self.pc + 1)
        return byte_a | byte_b

class InterruptedException(Exception):
    pass
