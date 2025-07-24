from PIL import Image, ImageDraw, ImageFont
import time
from gpiozero import RotaryEncoder, Button

# Encodeur (doit être le même que dans main.py)
encoder = RotaryEncoder(a=17, b=27, max_steps=100)
button = Button(22)

font = ImageFont.load_default()

def afficher_menu_selection(titre, options, oled=None):
    selected = 0

    def afficher():
        image = Image.new("1", (128, 64))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), titre, font=font, fill=1)
        for i, opt in enumerate(options):
            y = 12 + i * 10
            if i == selected:
                draw.rectangle((0, y, 128, y+10), outline=1, fill=1)
                draw.text((2, y), opt, font=font, fill=0)
            else:
                draw.text((2, y), opt, font=font, fill=1)
        if oled:
            oled.image(image)
            oled.show()

    encoder.steps = 0
    afficher()

    while True:
        direction = encoder.steps
        encoder.steps = 0
        if direction != 0:
            selected += direction
            selected = max(0, min(len(options)-1, selected))
            afficher()
        if button.is_pressed:
            time.sleep(0.3)  # anti-rebond
            return options[selected]
        time.sleep(0.05)
