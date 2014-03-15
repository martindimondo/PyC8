from __future__ import print_function
import re

import logging

logging.basicConfig(level=logging.INFO)

class Executor(object):

    def __init__(self, op_map):
        processed = {}
        for pattern, f in op_map.iteritems():
            s = self._build_pattern_groups(pattern.lower())
            processed[re.compile(s)] = f

        self.operations = processed

    def execute(self, context, op):
        s = "%04x" % op
        for pattern, f in self.operations.iteritems():
            m = pattern.match(s)
            if m:
                return f(context, *[int(v, base=16) for v in m.groups()])
        assert False, s

    def _build_pattern_groups(self, pattern):
        s = pattern.replace('?', '.')
        for id in ['x', 'y', 'z']:
            m = re.search('%s+' % id, s)
            if m:
                s = s[:m.start()] + ('(.{%s})' % (m.end() - m.start())) + s[m.end():] 
        return '^' + s + '$'

def set_mem_v0_vx(context, x):
    for i in range(x):
        context.memory.write_byte(context.index_reg + i, context.v[i])
    context.pc += 2
    
def fill_v0_vx(context, x):
    for i in range(x+1):
        context.v[i] = context.memory.get_byte(context.index_reg + i)
    context.pc += 2
    
def set_bcd_vx(context, x):
    val = int(context.v[x])
    context.memory.write_byte(context.index_reg, val / 100)
    context.memory.write_byte(context.index_reg + 1, val % 100 / 10)
    context.memory.write_byte(context.index_reg + 2, val % 100 % 10)
    context.pc += 2
        
def set_i_font(context, x):
    context.index_reg = context.memory.get_font_address(context.v[x])
    context.pc += 2
    
def add_reg_ind(context, x):
    context.index_reg += context.v[x]
    context.pc += 2
        
def set_delay_timer(context, x):
    context.delay_timer = context.v[x]
    context.pc += 2

def set_sound_timer(context, x):
    context.sound_timer = context.v[x]
    context.pc += 2
    
def set_vx_key_pressed(context, x):
    context.v[x] = context.keypad.wait_for_keypress()
    context.pc += 2

def set_vx_delay_timer(context, x):
    context.v[x] = context.delay_timer
    context.pc += 2
    
def skip_key_vx(context, x, result=True):
    if context.keypad.is_keypressed(context.v[x]) == result:
        context.pc += 2
    context.pc += 2
    
def draw_sprite(context, x, y, n):
    sprite = []
    for cb in range(n):
        sprite.append(context.memory.get_byte(context.index_reg + cb))
    collision = context.screen.draw(context.v[x], context.v[y], sprite)
    context.v[15] = collision
    context.pc += 2
            
def jump_nnn_v0(context, nnn):
    context.pc = context.v[0] + nnn

def set_vx_rand(context, x, nn):
    import random
    context.v[x] = random.randint(0, 0xFF) & nn
    context.pc += 2
    
def jump_noteq(context, x, y):
    if context.v[x] != context.v[y]:
        context.pc += 2
    context.pc += 2
    
def shift_vy_left(context, x, y):
    context.v[15] = context.v[15] >> 7 # First value
    context.v[x] = (context.v[y] << 1) % 255
    context.pc += 2

def shift_right(context, x, y):
    context.v[15] = context.v[y] & 0x1
    context.v[x] = context.v[y] >> 1
    context.pc += 2

def sub_vx_vy_vf(context, x, y):
    logging.info('Setting V[X] = V[X] - V[Y], V[F] = 1 if V[Y] > V[X]')
    context.v[15] = 1 if context.v[y] > context.v[x] else 0
    context.v[x] = context.v[x] - context.v[y]
    context.pc += 2
    
def add_vx_vy(context, x, y):
    logging.info('Setting V[X] = V[X] + V[Y]')
    val = context.v[x] + context.v[y]
    context.v[15] = 1 if val > 255 else 0
    context.v[x] = val % 256
    context.pc += 2

def sub_vx_vy(context, x, y):
    logging.info('Setting V[X] = V[X] - V[Y]')
    val = context.v[x] - context.v[y]
    context.v[15] = 1 if val < 0 else 0
    context.v[x] = val % 256
    context.pc += 2
    
def set_vx_or_vy(context, x, y):
    logging.info('Setting V[X] = V[X] | V[Y]')
    context.v[x] = context.v[x] | context.v[y]
    context.pc += 2
    
def set_vx_xor_vy(context, x, y):
    logging.info('Setting V[X] = V[X] ^ V[Y]')
    context.v[x] = context.v[x] ^ context.v[y]
    context.pc += 2

def set_vx_and_vy(context, x, y):
    logging.info('Setting V[X] = V[X] & V[Y]')
    context.v[x] = context.v[x] & context.v[y]
    context.pc += 2

def set_vx_vy(context, x, y):
    logging.info('Setting V[X] = V[Y]')
    context.v[x] = context.v[y]
    context.pc += 2
    
def add_reg(context, x, nnn):
    logging.info('Adding NNN to V[X]')
    context.v[x] = (context.v[x] + nnn) % 256
    context.pc += 2

def set_i(context, nnn):
    logging.info('Setting NNN to index_reg')
    context.index_reg = nnn
    context.pc += 2

def pop_stack(context):
    logging.info('Returning from a subroutine')
    context.pc = context.stack.pop()

def call_rca1082(context, address): #TODO
    print("operation not implemented yet:", address)
    context.pc += 1 

def clear(context):
    logging.info('Clearing screen')
    context.screen.clear()
    context.pc += 2

def jump(context, address):
    logging.info('Jump at 0x%2x address' % address)
    context.pc = address

def call(context, address):
    logging.info('Calling subroutine at 0x%2x address' % address)
    context.pc += 2
    context.stack.append(context.pc)
    context.pc = address

def skip_equal(context, x, nnn, ifeq=True):
    logging.info('Skip if V[X] === NNN is %s' % ifeq)
    if (context.v[x] == nnn) == ifeq:
        context.pc += 2
    context.pc += 2

def skip_eq_reg(context, x, y):
    logging.info('Skip if V[X] === V[Y]')
    if context.v[x] == context.v[y]:
        context.pc += 2
    context.pc += 2

def set_reg(context, x, nnn):
    logging.info('Set NNN to cpu reg V[x]')
    context.v[x] = nnn
    context.pc += 2

op_map = {
    '0?E0': clear,
    '0?EE': pop_stack,
    '0XXX': call_rca1082,
    '1XXX': jump,
    '2XXX': call,
    '3XYY': skip_equal,
    '4XYY': lambda context, x, nn: skip_equal(context, x, nn, ifeq = False),
    '5XY0': skip_eq_reg,
    '6XYY': set_reg,
    '7XYY': add_reg,
    '8XY0': set_vx_vy,
    '8XY1': set_vx_or_vy,
    '8XY2': set_vx_and_vy,
    '8XY3': set_vx_xor_vy,
    '8XY4': add_vx_vy,
    '8XY5': sub_vx_vy,
    '8XY6': shift_right,
    '8XY7': sub_vx_vy_vf,
    '8XYE': shift_vy_left,
    '9XY0': jump_noteq,
    'AXXX': set_i,
    'BXXX': jump_nnn_v0,
    'CXYY': set_vx_rand,
    'DXYZ': draw_sprite,
    'EX9E': lambda context, x: skip_key_vx(x, result=False),
    'EXA1': skip_key_vx,
    'FX07': set_vx_delay_timer,
    'FX0A': set_vx_key_pressed,
    'FX15': set_delay_timer,
    'FX18': set_sound_timer,
    'FX1E': add_reg_ind,
    'FX29': set_i_font,
    'FX33': set_bcd_vx,
    'FX55': set_mem_v0_vx,
    'FX65': fill_v0_vx
}


