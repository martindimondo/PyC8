'''
    CPU chip-8 emulator module
'''
import display as dp


MEMORY_LIMIT = 4096 # 4k bytes support
MEMORY_START = 0x200
CPU_REGISTERS = 16
STACK_LEVEL = 16

class CPUEmulator(object):
    
    def __init__(self):
        self.pc = 0 # Program Counter
        self.delay_timer = 0
        self.sound_timer = 0
        self.interrupted = False
        self._init_mem()
        self._init_registers()
        
    def _init_registers(self):
        self.index_reg = 0
        self.v = [0x0] * CPU_REGISTERS
        self.stack = [0x0] * STACK_LEVEL
        
    def _init_mem(self):
        self.mem = [0x0] * MEMORY_LIMIT

    def main_loop(self):
        while True:
            op = self._fetch()
            self._execute(op)
            
            if self.delay_timer > 0:
                self.delay_timer -= 1
            
            if self.sound_timer > 0:
                self.sound_timer -= 1
                #if self.sound_timer == 0:
                print('\a') # Nonzero value produce a beep in a Chip8
            if self.interrupted:
                raise InterruptedException, 'CPU execution cycle was interrupted'

    def interrupt(self):
        self.interrupted = True
        
    def _fetch(self):
        '''
            Fetch two bytes and merge it
            in an opcode
            
            left shift 8 bits to merge with the second byte
            because the size of the operation code is of 2 bytes
        '''
        return self.mem[self.pc] << 8 | self.mem[self.pc + 1]


    def _execute(self, op):
        instr = op & 0xF000 # extract the operation
        if instr == 0x0:
            sec_byte = op & 0xF
            if sec_byte == 0x0:
                print('Clear screen')
            elif sec_byte == 0xE:
                print('Return subroutine')
            else
                raise Exception, 'Not supported operation'
        elif instr == 0xA000:
            pass


class InterruptedException(Exception):
    pass