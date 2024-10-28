## presets.py
import json
import os
from display import create_button_image, update_save_button
from camera import send_command
from sequences import sequence_actions

preset_camera_map = {}
camera_preset_count = {i: 1 for i in range(1, 5)}
camera_presets = {i: [] for i in range(1, 5)}
config_changed = False  # Start as False, set True on preset creation

# Variable globale pour suivre la page actuelle
current_page = 1

# Fonction pour ajuster le numéro du bouton en fonction de la page
def get_real_button_number(page, button_number):
    return (page - 1) * 32 + button_number + 1

# Fonction pour trouver un preset disponible
def find_available_preset(camera):
    for i in range(1, camera_preset_count[camera]):
        if i not in camera_presets[camera]:
            return i
    return camera_preset_count[camera]

def enregistrer_preset(deck, key, camera_number, recording_enabled):
    real_key = get_real_button_number(current_page, key)

    if not recording_enabled:
        print("L'enregistrement des presets est désactivé.")
        return

    # Gestion de la suppression et de l'écrasement des presets existants
    if real_key in preset_camera_map:
        old_camera, old_preset = preset_camera_map[real_key]
        
        if old_preset in camera_presets[old_camera]:
            camera_presets[old_camera].remove(old_preset)
            print(f"Suppression du preset {old_preset} pour la caméra {old_camera}.")
        
        # Si on écrase le même preset pour la même caméra, on garde le numéro
        preset_number = old_preset if old_camera == camera_number else find_available_preset(camera_number)
    else:
        # Sinon, on enregistre un nouveau preset
        preset_number = find_available_preset(camera_number)

    # Ajout du preset au dictionnaire et envoi de la commande
    camera_presets[camera_number].append(preset_number)
    command = bytes([0x80 + camera_number, 0x01, 0x04, 0x3F, 0x01, preset_number - 1, 0xFF])
    send_command(command)
    preset_camera_map[real_key] = (camera_number, preset_number)

    on_preset_changed(deck)
    print(f"Enregistrement du preset {preset_number} pour la caméra {camera_number} sur le bouton {key}.")

    # Mise à jour de camera_preset_count si nécessaire
    if preset_number >= camera_preset_count[camera_number]:
        camera_preset_count[camera_number] = preset_number + 1

def rappeler_preset(deck, key):
    real_key = get_real_button_number(current_page, key)

    if real_key in preset_camera_map:
        camera_to_use, preset_number = preset_camera_map[real_key]
        if preset_number in camera_presets[camera_to_use]:
            sequence_actions(camera_to_use, preset_number)
            print(f"Rappel du preset {preset_number} pour la caméra {camera_to_use} depuis le bouton {key}.")
        else:
            print(f"Erreur : le preset {preset_number} n'existe pas pour la caméra {camera_to_use}.")
    else:
        print(f"Aucun preset enregistré pour le bouton {real_key}.")

def save_configuration(deck):
    global preset_camera_map, camera_preset_count, config_changed
    config_data = {
        'preset_camera_map': list(preset_camera_map.items()),
        'camera_preset_count': camera_preset_count
    }
    try:
        with open("save.conf", "w") as config_file:
            json.dump(config_data, config_file)
        config_changed = False  # Reset after save
        update_save_button(deck, config_changed)
        print("Configuration sauvegardée dans save.conf.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")
        deck.set_key_image(16, create_button_image(deck, "Save", "red"))

def load_configuration(deck):
    global preset_camera_map, camera_preset_count, camera_presets

    if os.path.exists("save.conf"):
        with open("save.conf", "r") as config_file:
            config_data = json.load(config_file)
            preset_camera_map = dict(config_data.get('preset_camera_map', []))
            camera_preset_count = config_data.get('camera_preset_count', {i: 1 for i in range(1, 5)})

            camera_presets = {i: [] for i in range(1, 5)}
            for button, (camera, preset) in preset_camera_map.items():
                camera_presets[camera].append(preset)

        adjust_camera_preset_count()
        print("Configuration chargée depuis save.conf.")
        update_save_button(deck, config_changed=False)  # Start as green if config is saved
        return True
    else:
        print("Aucune configuration trouvée.")
        update_save_button(deck, config_changed=True)  # Start as orange if config needs saving
        return False

def adjust_camera_preset_count():
    for camera in camera_presets:
        if camera_presets[camera]:
            camera_preset_count[camera] = max(camera_presets[camera]) + 1
        else:
            camera_preset_count[camera] = 1

# Function to indicate a preset has changed, updating SAVE button to orange
def on_preset_changed(deck):
    global config_changed
    config_changed = True
    update_save_button(deck, config_changed)  # Show orange for unsaved changes
