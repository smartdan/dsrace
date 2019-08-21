import time

from luma.core.serial import i2c, spi, noop
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from PIL import ImageFont, ImageDraw

class OledUtils(object):
    """Utilities: Utilities for managing LCD OLED DISPLAY

    Attributes:
        first_line 
        second_line 
        third_line   
    """

    def __init__(self):
        ''' Init class '''
        self.first_line = ''
        self.second_line = ''
        self.third_line = ''

        # rev.1 users set port=0
        # substitute spi(device=0, port=0) below if using that interface
        self.serial = i2c(port=1, address=0x3C)

        # substitute ssd1331(...) or sh1106(...) below if using that device
        self.device = ssd1306(self.serial)
        self.padding = 2
        self.shape_width = 20
        self.top = self.padding
        self.x = self.padding
        self.font_size = 14
        self.my_font = ImageFont.truetype("/home/pi/luma.examples/examples/fonts/pixelmix.ttf", self.font_size)
        self.my_font_1 = ImageFont.truetype("/home/pi/luma.examples/examples/fonts/pixelmix.ttf", 16)
        self.my_font_2 = ImageFont.truetype("/home/pi/luma.examples/examples/fonts/pixelmix.ttf", 16)
        self.my_font_3 = ImageFont.truetype("/home/pi/luma.examples/examples/fonts/pixelmix.ttf", 16)
        self.virtual = viewport(self.device, width=200, height=100)
            

    def resetLcd(self):
        ''' RESET lines'''       
        self.device.clear()
    
    def writeFirst(self, first_line):
        ''' WRITE first_line '''
        self.first_line = first_line
        self.update()
        
    def writeSecond(self, second_line):
        ''' WRITE second_line '''
        self.second_line = second_line
        self.update()            

    def writeThird(self, third_line):
        ''' WRITE third_line '''
        self.third_line = third_line
        self.update()
    
    def update(self):
        with canvas(self.virtual) as draw:
            draw.rectangle(self.device.bounding_box, outline="white", fill="black")
            draw.text((self.x, self.top), self.first_line, fill="white", font=self.my_font_1)
            draw.text((self.x, self.top + 20), self.second_line, fill="white", font=self.my_font_2)
            draw.text((self.x, self.top + 40), self.third_line, fill="white", font=self.my_font_3)
