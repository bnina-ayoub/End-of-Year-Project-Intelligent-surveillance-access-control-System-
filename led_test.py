from gpiozero import Button, RGBLED
from colorzero import Color
import time, requests

update_period = 10 # seconds
led = RGBLED(red=18, green=23, blue=24)
button = Button(25)

cheerlights_url = "http://api.thingspeak.com/channels/1417/field/2/last.txt"
old_color = None

def pressed():
    led.color = Color(0, 0, 0)  # LED off
button.when_pressed = pressed

while True:
    try:
        cheerlights = requests.get(cheerlights_url)
        color = cheerlights.content             # the color as text
        if color != old_color:
            led.color = Color(color)            # the color as an object
            old_color = color           
    except Exception as e:
        print(e)
    time.sleep(update_period) 