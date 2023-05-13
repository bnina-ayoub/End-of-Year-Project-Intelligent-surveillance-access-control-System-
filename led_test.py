from gpiozero import RGBLED
from colorzero import Color
import time

led = RGBLED(red=18, green=23, blue=24)
update_period = 10  # seconds

while True:
    led.color = Color(1, 0, 0)  # red
    time.sleep(1)
    led.color = Color(0, 1, 0)  # green
    time.sleep(1)
    led.color = Color(0, 0, 1)  # blue
    time.sleep(1)
    led.color = Color(0, 0, 0)  # off
    time.sleep(update_period - 3)
