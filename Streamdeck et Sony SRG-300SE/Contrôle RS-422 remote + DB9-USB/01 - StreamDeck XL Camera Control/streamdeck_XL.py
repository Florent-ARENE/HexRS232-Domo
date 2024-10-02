import time
from tally import update_tally
from presets import enregistrer_preset, rappeler_preset, save_configuration, load_configuration
from streamdeck import initialize_streamdeck, update_camera_buttons, handle_streamdeck_event, set_toggle_button
from atem import connect_to_atem

# Initialisation
recording_enabled = False  # Définit le mode (RECALL par défaut)
camera_number = 1  # Caméra active (par défaut à 1)

# Fonction pour mettre à jour l'affichage et gérer les modes
def update_display(deck, recording_enabled):
    if recording_enabled:
        update_camera_buttons(deck, camera_number, recording_enabled)
    else:
        update_tally(deck)

# Fonction pour gérer les événements du Stream Deck
def handle_streamdeck_event(deck, key, state):
    global recording_enabled, camera_number

    if state:
        if key == 8:
            # Toggle entre les modes STORE et RECALL
            recording_enabled = not recording_enabled
            mode = "STORE" if recording_enabled else "RECALL"
            print(f"Changement de mode : {mode}")
            set_toggle_button(deck, mode)
            update_display(deck, recording_enabled)  # Met à jour l'affichage selon le mode

        elif key == 16:
            save_configuration(deck)  # Sauvegarde la configuration avec le bouton 16

        elif key in [7, 15, 23, 31]:
            camera_number = [7, 15, 23, 31].index(key) + 1
            print(f"Caméra sélectionnée : {camera_number}")
            update_camera_buttons(deck, camera_number, recording_enabled)

        elif key in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30]:
            if recording_enabled:
                enregistrer_preset(deck, key, camera_number, recording_enabled)
            else:
                rappeler_preset(deck, key)

# Initialisation du Stream Deck
deck = initialize_streamdeck()

# Charger la configuration avant de connecter à l'ATEM
load_configuration(deck)

# Connecter à l'ATEM après avoir chargé la configuration
connect_to_atem()

# Initialisation des boutons caméra
update_camera_buttons(deck, camera_number, recording_enabled)

# Bouton toggle par défaut (rouge) pour "recall preset"
set_toggle_button(deck, "RECALL")

# Configuration des événements du Stream Deck
deck.set_key_callback(handle_streamdeck_event)

print("### Stream Deck prêt... OK")

try:
    while True:
        # Mise à jour uniquement en mode RECALL
        if not recording_enabled:
            update_tally(deck)  # Mise à jour du Tally en mode RECALL
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    deck.close()
