# streamdeck_XL.py (main)
import time
from tally import update_tally
from presets import enregistrer_preset, rappeler_preset, save_configuration, load_configuration, set_current_page
from streamdeck import initialize_streamdeck, set_toggle_button, update_camera_buttons
from atem import connect_to_atem
from display import update_save_button

# Initialisation des paramètres
recording_enabled = False
camera_number = 1
config_changed = False
current_page = 1

def update_display(deck):
    global recording_enabled, config_changed
    if recording_enabled:
        update_camera_buttons(deck, camera_number, recording_enabled)
    else:
        update_tally(deck)
    set_toggle_button(deck, "STORE" if recording_enabled else "RECALL")
    update_save_button(deck, config_changed)

def change_page():
    global current_page
    current_page = (current_page % 3) + 1
    set_current_page(current_page)
    print(f"Changement de page : Page {current_page}")

deck = initialize_streamdeck()
print("Vérification de l'existence de save.conf...")
if load_configuration(deck):
    config_changed = False
    print("Configuration existante chargée. SAVE est vert.")
else:
    config_changed = True
    print("Aucun fichier save.conf trouvé. SAVE démarre en orange.")

connect_to_atem()
set_toggle_button(deck, "RECALL")
update_display(deck)

def perform_save(deck):
    global config_changed
    if config_changed and recording_enabled:
        save_configuration(deck)
        config_changed = False
        update_save_button(deck, config_changed)

def streamdeck_callback(deck, key, state):
    global recording_enabled, config_changed, camera_number
    if state:
        if key == 8:
            recording_enabled = not recording_enabled
            set_toggle_button(deck, "STORE" if recording_enabled else "RECALL")
        elif key == 16:
            perform_save(deck)
        elif key == 24:
            change_page()
        elif key in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30]:
            if recording_enabled:
                enregistrer_preset(deck, key, camera_number, recording_enabled, current_page)
                config_changed = True
                print(f"Enregistrement du preset pour le bouton {key}. SAVE devient orange.")
            else:
                rappeler_preset(deck, key, current_page)
                print(f"Rappel du preset pour le bouton {key}.")
        elif key in [7, 15, 23, 31]:
            camera_number = (key - 7) // 8 + 1
            update_display(deck)

    update_display(deck)

deck.set_key_callback(streamdeck_callback)

try:
    while True:
        update_display(deck)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    deck.close()
