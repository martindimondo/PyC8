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


CLOCK_RATE = 60 # Run at 60hz
CPU_REGISTERS = 16


logging.basicConfig(level=logging.INFO)


class CPUEmulator(object):
    
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
        self._execute(self.op)
        
    def _fetch(self):
        '''
            Fetch opcode bytes
        '''
        byte_a = self.memory.get_byte(self.pc) << 8 # shift to left 8 bits
        byte_b = self.memory.get_byte(self.pc + 1)
        return byte_a | byte_b

    def _execute(self, op):
        instr = op & 0xF000 # extract the operation
        logging.debug('Instruction: 0x%02x ' % instr)
        tmppc = self.pc
        
        if instr == 0x0:
            sec_byte = op & 0xF
            if sec_byte == 0x0:
                self._op_clear()
            elif sec_byte == 0xE:
                self._op_pop_stack()
        elif instr == 0x1000:
            self._op_jump(util.nnn(op))
        elif instr == 0x2000:
            self._op_call(util.nnn(op))
        elif instr == 0x3000:
            self._op_skip_equal(util.x(op), util.nn(op))
        elif instr == 0x4000:
            self._op_skip_equal(util.x(op), util.nn(op), ifeq = False)
        elif instr == 0x5000:
            self._op_skip_eq_reg(util.x(op), util.y(op))
        elif instr == 0x6000:
            self._op_set_reg(util.x(op), util.nn(op))
        elif instr == 0x7000:
            self._op_add_reg(util.x(op), util.nn(op))
        elif instr == 0x8000:
            subop = util.n(op)
            if subop == 0x0:
                self._op_set_vx_vy(util.x(op), util.y(op))
            elif subop == 0x1:
                self._op_set_vx_or_vy(util.x(op), util.y(op))
            elif subop == 0x2:
                self._op_set_vx_and_vy(util.x(op), util.y(op))
            elif subop == 0x3:
                self._op_set_vx_xor_vy(util.x(op), util.y(op))
            elif subop == 0x4:
                self._op_add_vx_vy(util.x(op), util.y(op))
            elif subop == 0x5:
                self._op_sub_vx_vy(util.x(op), util.y(op))
            elif subop == 0x6:
                self._op_shift_right(util.x(op), util.y(op))
            elif subop == 0x7:
                self._op_sub_vx_vy_vf(util.x(op), util.y(op))
            elif subop == 0xE:
                self._op_shift_vy_left(util.x(op), util.y(op))
        elif instr == 0x9000:
            self._op_jump_noteq(util.x(op), util.y(op))
        elif instr == 0xA000:
            self._op_set_i(util.nnn(op))
        elif instr == 0xB000:
            self._op_jump_nnn_v0(util.nnn(op))
        elif instr == 0xC000:
            self._op_set_vx_rand(util.x(op), util.nn(op))
        elif instr == 0xD000:
            self._op_draw_sprite(util.x(op), util.y(op), util.n(op))
        elif instr == 0xE000:
            subop = op & 0xF
            if subop == 0x1:
                self._op_skip_key_vx(util.x(op), result=False)
            elif subop == 0xE:
                self._op_skip_key_vx(util.x(op))
        elif instr == 0xF000:
            subop = op & 0xFF
            if subop == 0x7:
                self._op_set_vx_delay_timer(util.x(op))
            elif subop == 0xA:
                self._op_set_vx_key_pressed(util.x(op))
            elif subop == 0x15:
                self._op_set_delay_timer(util.x(op))
            elif subop == 0x18:
                self._op_set_sound_timer(util.x(op))
            elif subop == 0x1E:
                self._op_add_reg_ind(util.x(op))
            elif subop == 0x29:
                self._op_set_i_font(util.x(op))
            elif subop == 0x33:
                self._op_set_bcd_vx(util.x(op))
            elif subop == 0x55:
                self._op_set_mem_v0_vx(util.x(op))
            elif subop == 0x65:
                self._op_fill_v0_vx(util.x(op) + 1)

                
    def _op_set_mem_v0_vx(self, x):
        for i in range(x):
            self.memory.write_byte(self.index_reg + i, self.v[i])
        self.pc += 2
        
    def _op_fill_v0_vx(self, x):
        for i in range(x):
            self.v[i] = self.memory.get_byte(self.index_reg + i)
        self.pc += 2
        
    def _op_set_bcd_vx(self, x):
        val = int(self.v[x])
        self.memory.write_byte(self.index_reg, val / 100)
        self.memory.write_byte(self.index_reg + 1, val % 100 / 10)
        self.memory.write_byte(self.index_reg + 2, val % 100 % 10)
        self.pc += 2
            
    def _op_set_i_font(self, x):
        self.index_reg = self.memory.get_font_address(self.v[x])
        self.pc += 2
        
    def _op_add_reg_ind(self, x):
        self.index_reg += self.v[x]
        self.pc += 2
            
    def _op_set_delay_timer(self, x):
        self.delay_timer = self.v[x]
        self.pc += 2
    
    def _op_set_sound_timer(self, x):
        self.sound_timer = self.v[x]
        self.pc += 2
        
    def _op_set_vx_key_pressed(self, x):
        self.v[x] = self.keypad.wait_for_keypress()
        self.pc += 2
    
    def _op_set_vx_delay_timer(self, x):
        self.v[x] = self.delay_timer
        self.pc += 2
        
    def _op_skip_key_vx(self, x, result=True):
        if self.keypad.is_keypressed(self.v[x]) == result:
            self.pc += 2
        self.pc += 2
        
    def _op_draw_sprite(self, x, y, n):
        sprite = []
        for cb in range(n):
            sprite.append(self.memory.get_byte(self.index_reg + cb))
        collision = self.screen.draw(self.v[x], self.v[y], sprite)
        self.v[15] = collision
        self.pc += 2
                
    def _op_jump_nnn_v0(self, nnn):
        self.pc = self.v[0] + nnn
    
    def _op_set_vx_rand(self, x, nn):
        import random
        self.v[x] = random.randint(0, 0xFF) & nn
        self.pc += 2
        
    def _op_jump_noteq(self, x, y):
        if self.v[x] != self.v[y]:
            self.pc += 2
        self.pc += 2
        
    def _op_shift_vy_left(self, x, y):
        self.v[15] = self.v[15] >> 7 # First value
        self.v[x] = (self.v[y] << 1) % 255
        self.pc += 2

    def _op_shift_right(self, x, y):
        self.v[15] = self.v[y] & 0x1
        self.v[x] = self.v[y] >> 1
        self.pc += 2
    
    def _op_sub_vx_vy_vf(self, x, y):
        logging.info('Setting V[X] = V[X] - V[Y], V[F] = 1 if V[Y] > V[X]')
        self.v[15] = 1 if self.v[y] > self.v[x] else 0
        self.v[x] = self.v[x] - self.v[y]
        self.pc += 2
        
    def _op_add_vx_vy(self, x, y):
        logging.info('Setting V[X] = V[X] + V[Y]')
        val = self.v[x] + self.v[y]
        self.v[15] = 1 if val > 255 else 0
        self.v[x] = val % 256
        self.pc += 2
    
    def _op_sub_vx_vy(self, x, y):
        logging.info('Setting V[X] = V[X] - V[Y]')
        val = self.v[x] - self.v[y]
        self.v[15] = 1 if val < 0 else 0
        self.v[x] = val % 256
        self.pc += 2
        
    def _op_set_vx_or_vy(self, x, y):
        logging.info('Setting V[X] = V[X] | V[Y]')
        self.v[x] = self.v[x] | self.v[y]
        self.pc += 2
        
    def _op_set_vx_xor_vy(self, x, y):
        logging.info('Setting V[X] = V[X] ^ V[Y]')
        self.v[x] = self.v[x] ^ self.v[y]
        self.pc += 2

    def _op_set_vx_and_vy(self, x, y):
        logging.info('Setting V[X] = V[X] & V[Y]')
        self.v[x] = self.v[x] & self.v[y]
        self.pc += 2

    def _op_set_vx_vy(self, x, y):
        logging.info('Setting V[X] = V[Y]')
        self.v[x] = self.v[y]
        self.pc += 2
        
    def _op_add_reg(self, x, nnn):
        logging.info('Adding NNN to V[X]')
        self.v[x] = (self.v[x] + nnn) % 256
        self.pc += 2
    
    def _op_set_i(self, nnn):
        logging.info('Setting NNN to index_reg')
        self.index_reg = nnn
        self.pc += 2
    
    def _op_pop_stack(self):
        logging.info('Returning from a subroutine')
        self.pc = self.stack.pop()
        
    def _op_clear(self):
        logging.info('Clearing screen')
        self.screen.clear()
        self.pc += 2
    
    def _op_jump(self, address):
        logging.info('Jump at 0x%2x address' % address)
        self.pc = address
    
    def _op_call(self, address):
        logging.info('Calling subroutine at 0x%2x address' % address)
        self.pc += 2
        self.stack.append(self.pc)
        self.pc = address
    
    def _op_skip_equal(self, x, nnn, ifeq=True):
        logging.info('Skip if V[X] === NNN is %s' % ifeq)
        if (self.v[x] == nnn) == ifeq:
            self.pc += 2
        self.pc += 2
    
    def _op_skip_eq_reg(self, x, y):
        logging.info('Skip if V[X] === V[Y]')
        if self.v[x] == self.v[y]:
            self.pc += 2
        self.pc += 2
    
    def _op_set_reg(self, x, nnn):
        logging.info('Set NNN to cpu reg V[x]')
        self.v[x] = nnn
        self.pc += 2

class InterruptedException(Exception):
    pass