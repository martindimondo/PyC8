'''
    Display functions
    
    To improve this, you can implement many renders 
    using a super class Chip8Render and subclasses of it
    charged to render 2d (OpenGl, Sdl, etc).
'''

__author__ = "Martin Dimondo"
__license__ = "Revised BSD"
__email__ = "martin.dimondo@gmail.com"


SCREEN_RESOLUTION = (64, 32)
FONT_ADDRESS = 0x0050
FONT_ROWS = 5

def clear():
    pass

def get_font_address(vx):
    return FONT_ADDRESS + vx * FONT_ROWS 