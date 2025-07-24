import cv2
import os
import numpy as np
import time
from PIL import Image, ImageDraw

DOSSIER_CARTES = "cartes"
RESOLUTION = (200, 300)

SCORE_DEPART = {
    "valet": 18,
    "9": 14,
    "valet + 9": 32,
    "aucun": 0
}

VALEURS_POINTS = {
    "7": 0, "8": 0, "9": 0,
    "10": 10, "vallet": 2,
    "dame": 3, "roi": 4, "as": 11
}

def afficher_score(score, oled, font):
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    draw.text((0, 20), f"Score final :", font=font, fill=1)
    draw.text((0, 36), f"{score} points", font=font, fill=1)
    oled.image(image)
    oled.show()

def charger_cartes():
    cartes = {}
    for f in os.listdir(DOSSIER_CARTES):
        if f.endswith(".jpg") or f.endswith(".png"):
            chemin = os.path.join(DOSSIER_CARTES, f)
            img = cv2.imread(chemin, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, RESOLUTION)
                cartes[f.split(".")[0].lower()] = img
    return cartes

def comparer_images(img1, img2):
    return cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)[0][0]

def trouver_carte(img_test, cartes_ref):
    img_gray = cv2.cvtColor(img_test, cv2.COLOR_BGR2GRAY)
    img_resized = cv2.resize(img_gray, RESOLUTION)
    best_score = -1
    meilleure = "inconnue"
    for nom, img_ref in cartes_ref.items():
        score = comparer_images(img_resized, img_ref)
        if score > best_score:
            best_score = score
            meilleure = nom
    return meilleure

def compter_points(option, oled, font):
    print(f"Option : {option}")
    score = SCORE_DEPART.get(option.lower(), 0)
    deja_vue = set()

    cartes_ref = charger_cartes()
    if not cartes_ref:
        print("Aucune carte.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Caméra absente.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            nom = trouver_carte(frame, cartes_ref)
            print(f"Carte : {nom}")

            if nom == "fin":
                print("Fin détectée.")
                break

            valeur = nom.split("_")[0].lower()
            if nom not in deja_vue and valeur in VALEURS_POINTS:
                score += VALEURS_POINTS[valeur]
                deja_vue.add(nom)
                print(f"+{VALEURS_POINTS[valeur]} → total = {score}")

            time.sleep(1)

    finally:
        cap.release()

    afficher_score(score, oled, font)
