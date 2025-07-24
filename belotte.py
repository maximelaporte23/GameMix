import RPi.GPIO as GPIO
import time
import cv2
import os
import numpy as np
from utils_display import afficher_menu_selection  # Hypothèse : fonction pour affichage OLED interactif

# -------------------
# CONFIGURATION
# -------------------
NB_JOUEURS = 4
PAS_PAR_JOUEUR = 200
STEP = 23  # GPIO modifié pour éviter conflit encodeur
DIR = 24

# Moteur tri (distribution)
MOTOR_TRI_IN1 = 5
MOTOR_TRI_IN2 = 6

# Moteur distribution
MOTOR_DIST_IN1 = 13
MOTOR_DIST_IN2 = 19

# Capteur infrarouge
CAPTEUR_IR = 12
DOSSIER_CARTES = "cartes"
RESOLUTION = (200, 300)

GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(MOTOR_TRI_IN1, GPIO.OUT)
GPIO.setup(MOTOR_TRI_IN2, GPIO.OUT)
GPIO.setup(MOTOR_DIST_IN1, GPIO.OUT)
GPIO.setup(MOTOR_DIST_IN2, GPIO.OUT)
GPIO.setup(CAPTEUR_IR, GPIO.IN)

# -------------------
# MOTEURS
# -------------------
def activer_moteurs_distribution():
    GPIO.output(MOTOR_TRI_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_TRI_IN2, GPIO.LOW)
    GPIO.output(MOTOR_DIST_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_DIST_IN2, GPIO.LOW)

def stopper_moteurs_distribution():
    GPIO.output(MOTOR_TRI_IN1, GPIO.LOW)
    GPIO.output(MOTOR_TRI_IN2, GPIO.LOW)
    GPIO.output(MOTOR_DIST_IN1, GPIO.LOW)
    GPIO.output(MOTOR_DIST_IN2, GPIO.LOW)

def avancer_stepper(nb_pas):
    GPIO.output(DIR, GPIO.HIGH)
    for _ in range(int(nb_pas)):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(0.001)

def tourner_joueur(coeff=1):
    avancer_stepper(PAS_PAR_JOUEUR * coeff)

def distribuer_cartes(nb):
    for _ in range(nb):
        activer_moteurs_distribution()
        while GPIO.input(CAPTEUR_IR) == 0:
            time.sleep(0.01)
        stopper_moteurs_distribution()
        time.sleep(0.5)

# -------------------
# CAMERA
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
    best_score = -1
    best_nom = "inconnue"
    for nom, ref in cartes.items():
        score = comparer_images(resized, ref)
        if score > best_score:
            best_score = score
            best_nom = nom
    return best_nom

# -------------------
# LOGIQUE DE JEU
# -------------------
def phase_distrib(nb_cartes):
    for _ in range(NB_JOUEURS):
        distribuer_cartes(nb_cartes)
        tourner_joueur()

def poser_question_qui_a_pris():
    choix = ["joueur 1", "joueur 2", "joueur 3", "joueur 4", "personne"]
    return afficher_menu_selection("Qui a pris ?", choix)

def afficher_menu_fin():
    return afficher_menu_selection("Fin de manche", ["Prochain tour", "Fin de partie"])

def joueur_a_pris(index):
    for i in range(NB_JOUEURS):
        tourner_joueur(coeff=0.5)
        if i == index:
            distribuer_cartes(2)
        else:
            distribuer_cartes(3)

def personne_a_pris(cartes_ref):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return
    try:
        while True:
            distribuer_cartes(1)
            ret, frame = cap.read()
            if not ret:
                continue
            nom = trouver_carte(frame, cartes_ref)
            if nom == "fin":
                break
    finally:
        cap.release()

# -------------------
# MAIN
# -------------------
def belotte():
    cartes_ref = charger_cartes()
    joueur_depart = 0
    while True:
        # Distribution classique
        phase_distrib(3)
        phase_distrib(2)
        tourner_joueur(coeff=0.5)
        distribuer_cartes(1)

        # Choix preneur
        choix = poser_question_qui_a_pris()
        if choix == "personne":
            personne_a_pris(cartes_ref)
        else:
            index = ["joueur 1", "joueur 2", "joueur 3", "joueur 4"].index(choix)
            tourner_joueur(coeff=0.5)
            joueur_a_pris(index)

        # Menu fin de manche
        action = afficher_menu_fin()
        if action == "Fin de partie":
            break
        else:
            joueur_depart = (joueur_depart + 1) % NB_JOUEURS
            avancer_stepper(PAS_PAR_JOUEUR)

    GPIO.cleanup()