import RPi.GPIO as GPIO
import time
import cv2
import os
import numpy as np

# -------------------
# CONFIGURATION GPIO
# -------------------

# Moteur tri
TRI_IN1 = 5
TRI_IN2 = 6

# Moteur distribution
NEW_IN1 = 13
NEW_IN2 = 19

# Moteur pas à pas
STEPPER_STEP = 23
STEPPER_DIR = 24

# Capteur infrarouge
CAPTEUR_IR = 12

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRI_IN1, GPIO.OUT)
GPIO.setup(TRI_IN2, GPIO.OUT)
GPIO.setup(NEW_IN1, GPIO.OUT)
GPIO.setup(NEW_IN2, GPIO.OUT)
GPIO.setup(STEPPER_STEP, GPIO.OUT)
GPIO.setup(STEPPER_DIR, GPIO.OUT)
GPIO.setup(CAPTEUR_IR, GPIO.IN)

# -------------------
# PARAMÈTRES
# -------------------

NB_PAS_PAR_AVANCE = 200
DOSSIER_CARTES = "cartes"
RESOLUTION = (200, 300)

# -------------------
# CONTRÔLE MOTEURS
# -------------------

def activer_moteurs_cc():
    GPIO.output(TRI_IN1, GPIO.HIGH)
    GPIO.output(TRI_IN2, GPIO.LOW)
    GPIO.output(NEW_IN1, GPIO.HIGH)
    GPIO.output(NEW_IN2, GPIO.LOW)

def stopper_moteurs_cc():
    GPIO.output(TRI_IN1, GPIO.LOW)
    GPIO.output(TRI_IN2, GPIO.LOW)
    GPIO.output(NEW_IN1, GPIO.LOW)
    GPIO.output(NEW_IN2, GPIO.LOW)

def avancer_stepper(nb_pas):
    GPIO.output(STEPPER_DIR, GPIO.HIGH)
    for _ in range(nb_pas):
        GPIO.output(STEPPER_STEP, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(STEPPER_STEP, GPIO.LOW)
        time.sleep(0.001)

# -------------------
# RECONNAISSANCE CAMERA
# -------------------

def charger_cartes():
    cartes = {}
    for f in os.listdir(DOSSIER_CARTES):
        if f.endswith(".jpg") or f.endswith(".png"):
            img = cv2.imread(os.path.join(DOSSIER_CARTES, f), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, RESOLUTION)
                cartes[f.split(".")[0].lower()] = img
    return cartes

def comparer_images(img1, img2):
    return cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)[0][0]

def trouver_carte(img, cartes):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, RESOLUTION)
    meilleur_score = -1
    meilleure_carte = "inconnue"
    for nom, ref in cartes.items():
        score = comparer_images(resized, ref)
        if score > meilleur_score:
            meilleur_score = score
            meilleure_carte = nom
    return meilleure_carte

# -------------------
# LOGIQUE PRINCIPALE
# -------------------

def president():
    print("Mode PRESIDENT lancé")
    cartes_ref = charger_cartes()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erreur caméra.")
        return

    try:
        while True:
            activer_moteurs_cc()
            print("Moteurs CC en cours...")

            while GPIO.input(CAPTEUR_IR) == 0:
                time.sleep(0.01)

            print("Carte détectée par capteur IR")
            stopper_moteurs_cc()

            print(f"Avance du moteur pas à pas de {NB_PAS_PAR_AVANCE} pas")
            avancer_stepper(NB_PAS_PAR_AVANCE)

            ret, frame = cap.read()
            if not ret:
                continue

            carte = trouver_carte(frame, cartes_ref)
            print(f"Carte reconnue : {carte}")

            if carte == "fin":
                print("Fin détectée, arrêt")
                break

            time.sleep(0.5)

    finally:
        cap.release()
        stopper_moteurs_cc()
        GPIO.cleanup()
        print("Fin du mode PRESIDENT")
