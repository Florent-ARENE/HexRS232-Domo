# streamdeck_XL.py (main)
import time
import sequences  # Import du module pour accéder à sequence_running dynamiquement
from tally import update_tally
from presets import enregistrer_preset, rappeler_preset, save_configuration, load_configuration, set_current_page
from streamdeck import initialize_streamdeck, set_toggle_button, update_camera_buttons
from atem import connect_to_atem
from display import update_save_button, update_toggle_button

recording_enabled = False
camera_number = 1
config_changed = False
current_page = 1

# Mise à jour de l'affichage
def update_display(deck):
    global recording_enabled, config_changed
    
    # Ne pas mettre à jour l'affichage pendant une séquence (clignotement en cours)
    if sequences.sequence_running:
        return
    
    if recording_enabled:
        update_camera_buttons(deck, camera_number, recording_enabled)
    else:
        update_tally(deck)
    
    # Appel des fonctions pour les boutons Toggle et Save avec les nouvelles couleurs
    update_toggle_button(deck, "STORE" if recording_enabled else "RECALL")
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
    
    # Ignorer les événements pendant une séquence
    if sequences.sequence_running:
        return
    
    if state:
        if key == 0:
            recording_enabled = not recording_enabled
            update_toggle_button(deck, "STORE" if recording_enabled else "RECALL")
        elif key == 1:
            perform_save(deck)
        elif key == 2:
            change_page()
        elif key in range(8, 32):
            if recording_enabled:
                enregistrer_preset(deck, key, camera_number, recording_enabled, current_page)
                config_changed = True
                print(f"Enregistrement du preset pour le bouton {key}. SAVE devient orange.")
            else:
                rappeler_preset(deck, key, current_page)
                print(f"Rappel du preset pour le bouton {key}.")
        elif key in range(3, 8):
            camera_number = key - 2
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
