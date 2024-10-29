# streamdeck_XL.py
import time
from tally import update_tally
from presets import enregistrer_preset, rappeler_preset, save_configuration, load_configuration, on_preset_changed, set_current_page
from streamdeck import initialize_streamdeck, set_toggle_button, update_camera_buttons, handle_streamdeck_event
from atem import connect_to_atem
from display import create_button_image, update_save_button

# Initialisation
recording_enabled = False  # Mode RECALL par défaut
camera_number = 1  # Caméra active initialisée correctement
config_changed = False  # Initial state for configuration changes
current_page = 1  # Page actuelle du Stream Deck

# Fonction pour mettre à jour l'affichage en fonction du mode
def update_display(deck):
    global recording_enabled, config_changed
    if recording_enabled:
        update_camera_buttons(deck, camera_number, recording_enabled)  # Mode STORE
    else:
        update_tally(deck)  # Mode RECALL

    set_toggle_button(deck, "STORE" if recording_enabled else "RECALL")
    update_save_button(deck, config_changed)

# Fonction pour gérer le changement de page
def change_page():
    global current_page
    current_page = (current_page % 3) + 1  # Limiter à 3 pages
    set_current_page(current_page)  # Mettre à jour la page active dans presets.py
    print(f"Changement de page : Page {current_page}")

# Initialisation du Stream Deck
deck = initialize_streamdeck()

# Vérification de l'existence de save.conf pour le démarrage
print("Vérification de l'existence de save.conf...")
if load_configuration(deck):  # Configuration chargée avec succès
    config_changed = False
    print("Configuration existante chargée. SAVE est vert.")
else:
    config_changed = True  # Aucun fichier, SAVE démarre en orange
    print("Aucun fichier save.conf trouvé. SAVE démarre en orange.")

connect_to_atem()

# Initialisation de l'affichage
set_toggle_button(deck, "RECALL")
update_display(deck)

# Fonction de sauvegarde avec vérification unique (STORE mode only)
def perform_save(deck):
    global config_changed
    if config_changed and recording_enabled:  # Save only if in STORE mode
        save_configuration(deck)
        config_changed = False  # Reset only after confirmed save
        update_save_button(deck, config_changed)

# Configuration des événements du Stream Deck
def streamdeck_callback(deck, key, state):
    global recording_enabled, config_changed, camera_number, current_page  # Ensure camera_number is accessible
    if state:
        if key == 8:  # Toggle entre STORE et RECALL
            recording_enabled = not recording_enabled
            set_toggle_button(deck, "STORE" if recording_enabled else "RECALL")
        elif key == 16:  # Bouton SAVE
            perform_save(deck)
        elif key == 24:  # Bouton pour changer de page
            change_page()
        elif key in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30]:
            # Gestion des presets selon le mode
            if recording_enabled:  # STORE mode: enregistrer preset
                enregistrer_preset(deck, key, camera_number, recording_enabled, current_page)
                config_changed = True
                print(f"Enregistrement du preset pour le bouton {key}. SAVE devient orange.")
            else:  # RECALL mode: rappeler preset
                rappeler_preset(deck, key, current_page)
                print(f"Rappel du preset pour le bouton {key}.")
        elif key in [7, 15, 23, 31]:  # Boutons de sélection de caméras
            camera_number = (key - 7) // 8 + 1  # Mapping directe pour [Cam 1, Cam 2, Cam 3, Cam 4]
            update_display(deck)

    update_display(deck)

deck.set_key_callback(streamdeck_callback)

try:
    while True:
        update_display(deck)  # Maintient l'affichage à jour
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    deck.close()
