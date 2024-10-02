## streamdeck_XL.py (main)
import time
from tally import update_tally
from presets import enregistrer_preset, rappeler_preset, save_configuration, load_configuration
from streamdeck import initialize_streamdeck, handle_streamdeck_event, set_toggle_button
from atem import connect_to_atem

# Initialisation
recording_enabled = False  # Définit le mode (RECALL par défaut)
camera_number = 1  # Caméra active (par défaut à 1)

# Fonction pour mettre à jour l'affichage et gérer les modes
def update_display(deck):
    global recording_enabled, camera_number
    if recording_enabled:
        handle_streamdeck_event(deck, None, True, camera_number, recording_enabled, save_configuration, enregistrer_preset, rappeler_preset)  # Mode STORE : mise à jour de la caméra sélectionnée
    else:
        update_tally(deck)  # Mode RECALL : mise à jour du Tally

# Initialisation du Stream Deck
deck = initialize_streamdeck()

# Charger la configuration avant de connecter à l'ATEM
load_configuration(deck)

# Connecter à l'ATEM après avoir chargé la configuration
connect_to_atem()

# Initialisation des boutons caméra en fonction du mode RECALL par défaut
update_display(deck)

# Bouton toggle par défaut (rouge) pour "recall preset"
set_toggle_button(deck, "RECALL")

# Configuration des événements du Stream Deck
def streamdeck_callback(deck, key, state):
    global recording_enabled, camera_number
    recording_enabled, camera_number = handle_streamdeck_event(deck, key, state, camera_number, recording_enabled, save_configuration, enregistrer_preset, rappeler_preset)
    
    # Forcer la mise à jour du Tally immédiatement après bascule vers RECALL
    if not recording_enabled:
        update_tally(deck)

deck.set_key_callback(streamdeck_callback)

print("### Stream Deck prêt... OK")

try:
    while True:
        # Mise à jour uniquement en mode RECALL
        if not recording_enabled:
            update_tally(deck)  # Mise à jour régulière du Tally en mode RECALL
        time.sleep(1)  # Attente de 1 seconde entre les mises à jour
except KeyboardInterrupt:
    pass
finally:
    deck.close()
