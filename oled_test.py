import time
from oled_utils import OledUtils

oledUtils = OledUtils()

'''
with canvas(virtual) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((x, top),    'Line 1', fill="white", font=my_font)
    draw.text((x, top+20), 'Line 2', fill="white", font=my_font)
    draw.text((x, top+40), 'Line 3', fill="white", font=my_font)
'''

oledUtils.resetLcd()
oledUtils.writeFirst('Line 1')
oledUtils.writeSecond('Line 2')
oledUtils.writeThird('Line 3')

while True:
    time.sleep(1)