import cv2
import os
import numpy as np
import RPi.GPIO as GPIO
import time

# ---------------------------
# CONFIGURATION
# ---------------------------

DOSSIER_CARTES = "cartes"
RESOLUTION = (200, 300)
BONNES_VALEURS = ['7', '8', '9', '10', 'vallet', 'dame', 'roi', 'as']

# Moteur tri
PIN_TRI_IN1 = 5
PIN_TRI_IN2 = 6

# Moteur distribution
PIN_DIST_IN1 = 13
PIN_DIST_IN2 = 19

# Moteur poubelle
PIN_POUBELLE_IN1 = 20
PIN_POUBELLE_IN2 = 21

# Initialisation GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_TRI_IN1, GPIO.OUT)
GPIO.setup(PIN_TRI_IN2, GPIO.OUT)
GPIO.setup(PIN_DIST_IN1, GPIO.OUT)
GPIO.setup(PIN_DIST_IN2, GPIO.OUT)
GPIO.setup(PIN_POUBELLE_IN1, GPIO.OUT)
GPIO.setup(PIN_POUBELLE_IN2, GPIO.OUT)

# ---------------------------
# COMMANDES MOTEURS
# ---------------------------

def activer_ejection():
    GPIO.output(PIN_DIST_IN1, GPIO.HIGH)
    GPIO.output(PIN_DIST_IN2, GPIO.LOW)
    GPIO.output(PIN_POUBELLE_IN1, GPIO.HIGH)
    GPIO.output(PIN_POUBELLE_IN2, GPIO.LOW)

def arreter_ejection():
    GPIO.output(PIN_DIST_IN1, GPIO.LOW)
    GPIO.output(PIN_DIST_IN2, GPIO.LOW)
    GPIO.output(PIN_POUBELLE_IN1, GPIO.LOW)
    GPIO.output(PIN_POUBELLE_IN2, GPIO.LOW)

def activer_moteur_tri_bonne():
    GPIO.output(PIN_TRI_IN1, GPIO.HIGH)
    GPIO.output(PIN_TRI_IN2, GPIO.LOW)

def activer_moteur_tri_mauvaise():
    GPIO.output(PIN_TRI_IN1, GPIO.LOW)
    GPIO.output(PIN_TRI_IN2, GPIO.HIGH)

def arreter_moteur_tri():
    GPIO.output(PIN_TRI_IN1, GPIO.LOW)
    GPIO.output(PIN_TRI_IN2, GPIO.LOW)

# ---------------------------
# OUTILS DE COMPARAISON D’IMAGE
# ---------------------------

def charger_cartes():
    cartes = {}
    for filename in os.listdir(DOSSIER_CARTES):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            chemin = os.path.join(DOSSIER_CARTES, filename)
            img = cv2.imread(chemin, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, RESOLUTION)
                cartes[filename.split(".")[0].lower()] = img
    return cartes

def comparer_images(img1, img2):
    result = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)
    return result[0][0]

def trouver_carte(img_test, cartes_ref):
    img_gray = cv2.cvtColor(img_test, cv2.COLOR_BGR2GRAY)
    img_resized = cv2.resize(img_gray, RESOLUTION)
    meilleur_score = -1
    carte_trouvee = "inconnue"
    for nom, img_ref in cartes_ref.items():
        score = comparer_images(img_resized, img_ref)
        if score > meilleur_score:
            meilleur_score = score
            carte_trouvee = nom
    return carte_trouvee

# ---------------------------
# TRI PRINCIPAL
# ---------------------------

def trier_cartes(oled=None, font=None):
    print("Début du tri")
    if oled and font:
        from PIL import Image, ImageDraw
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        draw.text((0, 20), "Tri en cours...", font=font, fill=1)
        oled.image(image)
        oled.show()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erreur : caméra non détectée.")
        return

    cartes_ref = charger_cartes()
    print(f"{len(cartes_ref)} cartes chargées pour comparaison.")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Erreur lors de la capture de l’image.")
        return

    carte_identifiee = trouver_carte(frame, cartes_ref)
    print(f"Carte détectée : {carte_identifiee}")

    valeur = carte_identifiee.split("_")[0].lower()

    activer_ejection()
    if valeur in BONNES_VALEURS:
        print("Carte bonne – tri vers bon bac")
        activer_moteur_tri_bonne()
    else:
        print("Carte mauvaise – tri vers poubelle")
        activer_moteur_tri_mauvaise()

    time.sleep(1)
    arreter_moteur_tri()
    arreter_ejection()

    print("Tri terminé")

# ---------------------------
# CLEANUP (optionnel)
# ---------------------------
def cleanup_gpio():
    GPIO.cleanup()