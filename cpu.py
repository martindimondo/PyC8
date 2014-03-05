

class CPUEmulator(object):
    MEMORY_LIMIT = 4096 # 4k chip 8 support
    MEMORY_START = 0x200
    
    
    def __init__(self):
        self.pc = 0 # Program Counter
        self.delay_timer = 0
        self.sound_timer = 0
        self.interrupted = False
        
    def _init_mem(self):
        self.mem = [None] * CPU.MEMORY_LIMIT

    def main_loop(self):
        while not self.interrupted:
            op = self._fetch_opcode()
            self._execute_opcode(op)
            
            if self.delay_timer > 0:
                self.delay_timer -= 1
            
            if self.sound_timer > 0:
                self.sound_timer -= 1
                if self.sound_timer == 0:
                    print('\a') # Beep
                    
            
    def _fetch_opcode(self):
        '''
            Fetch two byes and merge it
            in an opcode
        '''
        return self.mem[pc] << 8 | self.mem[pc + 1], pc + 2


    def _execute_opcode(self, op):
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

    