'''
    Chip8 Util module
'''

__author__ = "Martin Dimondo"
__license__ = "Revised BSD"
__email__ = "martin.dimondo@gmail.com"


def x(op):
    return op & 0xF00

def y(op):
    return op & 0xF0

def n(op):
    return op & 0xF

def nn(op):
    return op & 0xFF

def nnn(op):
    return op & 0xFFF