import board
import digitalio
import busio
import adafruit_ssd1306
from gpiozero import RotaryEncoder, Button
from PIL import Image, ImageDraw, ImageFont
import time
from trier_cartes import trier_cartes
from compter_points import compter_points
from melanger import melanger
from president import president
from belotte import belotte




# ----------- OLED SETUP ----------
spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)
dc = digitalio.DigitalInOut(board.D25)
reset = digitalio.DigitalInOut(board.D24)
cs = digitalio.DigitalInOut(board.CE0)

oled = adafruit_ssd1306.SSD1306_SPI(128, 64, spi, dc, reset, cs)
font = ImageFont.load_default()

# ----------- ENCODEUR ----------
encoder = RotaryEncoder(a=17, b=27, max_steps=100)
button = Button(22)

# ----------- MENUS ----------
main_menu = ["Sélectionner un jeu", "Trier", "Mélanger", "Compter les points"]
submenu_jeux = ["Belotte", "Poker", "President", "Retour"]
submenu_points = ["valet", "9", "valet + 9", "aucun", "Retour"]

current_menu = main_menu
selected_index = 0
menu_stack = []

# ----------- AFFICHAGE ----------
def afficher_menu():
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    for i, item in enumerate(current_menu):
        y = i * 12
        if i == selected_index:
            draw.rectangle((0, y, oled.width, y + 12), outline=1, fill=1)
            draw.text((2, y), item, font=font, fill=0)
        else:
            draw.text((2, y), item, font=font, fill=1)
    oled.image(image)
    oled.show()

def afficher_message(texte):
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    draw.text((0, 20), texte, font=font, fill=1)
    oled.image(image)
    oled.show()
    time.sleep(2)

# ----------- ACTIONS ----------
def demarrer_jeu(nom):
    if nom.lower() == "president":
        president()
    elif nom.lower() == "belotte":
        belotte()
    else:
        afficher_message(f"Jeu : {nom}")



# ----------- INTERACTIONS ----------
def on_rotate():
    global selected_index
    direction = encoder.steps
    encoder.steps = 0
    selected_index += direction
    selected_index = max(0, min(selected_index, len(current_menu) - 1))
    afficher_menu()

def on_click():
    global current_menu, selected_index, menu_stack
    selection = current_menu[selected_index]

    if selection == "Retour":
        if menu_stack:
            current_menu, selected_index = menu_stack.pop()
            afficher_menu()
        return

    if current_menu == main_menu:
        if selection == "Sélectionner un jeu":
            menu_stack.append((current_menu, selected_index))
            current_menu = submenu_jeux
            selected_index = 0
            afficher_menu()
        elif selection == "Trier":
            trier_cartes(oled, font)
        elif selection == "Mélanger":
            afficher_message("Mélange en cours...")
            melanger()
        elif selection == "Compter les points":
            menu_stack.append((current_menu, selected_index))
            current_menu = submenu_points
            selected_index = 0
            afficher_menu()

    elif current_menu == submenu_jeux:
        demarrer_jeu(selection)

    elif current_menu == submenu_points:
        compter_points(selection, oled, font)

# ----------- INITIALISATION ----------
encoder.when_rotated = on_rotate
button.when_pressed = on_click
oled.fill(0)
oled.show()
afficher_menu()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    oled.fill(0)
    oled.show()
    print("Arrêt.")
