# streamdeck_XL.py (main)
import time
from StreamDeck.DeviceManager import DeviceManager
from display import create_button_image
from tally import update_tally
from presets import enregistrer_preset, rappeler_preset, save_configuration, load_configuration, adjust_camera_preset_count
from camera import select_camera
import os

# Initialisation
recording_enabled = False
is_recall_mode = True
camera_number = 1  # Initialisation par défaut à 1

def update_camera_buttons(deck):
    global camera_number  # On s'assure d'utiliser la variable globale
    if recording_enabled:
        # Mode STORE : affichage des boutons dessinés pour la caméra active
        for button, camera in zip([7, 15, 23, 31], range(1, 5)):
            color = "blue" if camera == camera_number else "black"
            print(f"Affichage de la caméra {camera} avec couleur {'blue' if camera == camera_number else 'black'}")
            deck.set_key_image(button, create_button_image(deck, f"Cam {camera}", color))
    else:
        # Mode RECALL : mise à jour du Tally
        update_tally(deck)

def handle_streamdeck_event(deck, key, state):
    global recording_enabled, camera_number, config_changed, is_recall_mode
    if state:
        if key == 8:
            recording_enabled = not recording_enabled
            mode = "STORE" if recording_enabled else "RECALL"
            print(f"Changement de mode : {mode}")
            color = "green" if recording_enabled else "red"
            deck.set_key_image(8, create_button_image(deck, mode, color))
            is_recall_mode = not recording_enabled
            update_camera_buttons(deck)
        elif key == 16:
            save_configuration(deck)  # Ajout de la fonction de sauvegarde lors de l'appui sur le bouton 16
        elif key in [7, 15, 23, 31]:
            camera_number = [7, 15, 23, 31].index(key) + 1
            print(f"Caméra sélectionnée : {camera_number}")
            update_camera_buttons(deck)
        elif key in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30]:
            if recording_enabled:
                enregistrer_preset(deck, key, camera_number, recording_enabled)
            else:
                rappeler_preset(deck, key)

# Initialisation du Stream Deck
devices = DeviceManager().enumerate()
if len(devices) == 0:
    print("Aucun Stream Deck détecté.")
    exit()

deck = devices[0]
deck.open()
deck.set_brightness(30)

load_configuration(deck)

# Initialisation des boutons caméra
update_camera_buttons(deck)

# Bouton toggle par défaut (rouge) pour "recall preset"
deck.set_key_image(8, create_button_image(deck, "RECALL", "red"))

deck.set_key_callback(handle_streamdeck_event)

print("Stream Deck prêt. Appuyez sur les boutons pour enregistrer/rappeler les presets et changer la caméra.")

try:
    while True:
        if not recording_enabled:
            update_tally(deck)  # Mise à jour du Tally seulement en mode RECALL
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    deck.close()
