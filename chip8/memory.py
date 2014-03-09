'''
    Basic implementation of an emulator of Chip8 in python
    to research low level purpose
    
    More info about tech spec: http://en.wikipedia.org/wiki/CHIP-8
        or http://es.wikipedia.org/wiki/CHIP-8
'''

__author__ = "Martin Dimondo"
__license__ = "Revised BSD"
__email__ = "martin.dimondo@gmail.com"


MEMORY_LIMIT = 4096 # 4k bytes support
MEMORY_START = 0x200
MEMORY_LIMIT = 4096 # 4k bytes support
FONT_ADDRESS = 0x0050
FONT_ROWS = 5


class Chip8Memory(object):
    
    def __init__(self):
        self.mem = [0x0] * MEMORY_LIMIT
    
    def write_byte(self, location, data):
        self.mem[location] = data
    
    def write_array(self, location, data):
        for index, b in enumerate(data):
            self.mem[location + index] = b
            
    def get_byte(self, location):
        return self.mem[location]
    
    def get_array(self, location, size):
        return self.mem[location:(location + size)]
    
    def get_font_address(self, vx):
        return FONT_ADDRESS + vx * FONT_ROWS
    
    