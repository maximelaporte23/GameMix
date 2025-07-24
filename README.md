# GameMix - Système de distribution et de tri de cartes automatique

GameMix est un projet embarqué sur Raspberry Pi qui permet de :
- Mélanger automatiquement des cartes
- Trier les cartes en fonction de leur valeur
- Distribuer les cartes selon différents jeux (Belotte, Président, etc.)
- Compter les points d'une manche en analysant les cartes jouées
- Contrôler toutes ces fonctions via un écran OLED et un encodeur rotatif cliquable

## 📦 Contenu

- `main.py` : Point d'entrée du système de menu
- `belotte.py` : Distribution des cartes pour le jeu de belotte
- `president.py` : Distribution automatique pour le jeu du président
- `melanger.py` : Mélange automatique de cartes (activation des moteurs)
- `trier_cartes.py` : Tri des cartes bonnes/mauvaises
- `compter_points.py` : Comptage de points par reconnaissance de cartes
- `utils_display.py` : Fonctions partagées pour l’affichage OLED

## 🔧 Dépendances Python

Les bibliothèques nécessaires sont listées dans `requirements.txt`. Pour les installer :

```bash
pip install -r requirements.txt
```

## 🧠 Fonctionnement général

- L’utilisateur navigue à l’aide de l’encodeur rotatif.
- Une fois un mode sélectionné, le système active les moteurs correspondants et utilise la caméra pour détecter les cartes.
- L’affichage se fait sur un écran OLED SPI (SSD1306).

## 📷 Dossier 'cartes'

Ce dossier contient les images de référence pour la reconnaissance :
- Nommer les fichiers comme `7_coeur.jpg`, `roi_pique.png`, etc.
- Une image nommée `fin.png` est utilisée pour indiquer la fin de la détection

## ⚙️ Configuration GPIO

Tous les moteurs, capteurs et boutons sont câblés à des GPIO spécifiques. Voir le fichier `GPIO_GameMix_Récapitulatif.pdf`.

## 👨‍🔧 Auteurs

Projet développé par Maxime dans le cadre du projet GameMix.
