import RPi.GPIO as GPIO
import time

# GPIO (TB6612FNG avec moteurs A et B)
AIN1 = 13  # Moteur A IN1
AIN2 = 19  # Moteur A IN2
BIN1 = 20  # Moteur B IN1
BIN2 = 21  # Moteur B IN2

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)

def melanger():
    print("Mélange en cours...")

    # Moteur A dans un sens
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)

    # Moteur B dans un sens
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)

    time.sleep(5)  # Temps de mélange

    # Arrêt moteurs
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.LOW)

    print("Mélange terminé")

def cleanup_gpio():
    GPIO.cleanup()
