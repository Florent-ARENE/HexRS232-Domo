# presets.py
import json
import os
import threading
from display import create_button_image, update_save_button
from camera import send_command
from sequences import sequence_actions

preset_camera_map = {}
camera_preset_count = {i: 1 for i in range(1, 7)}  # 6 caméras (1-6)
camera_presets = {i: [] for i in range(1, 7)}      # 6 caméras (1-6)
config_changed = False
current_page = 1

def get_real_button_number(button_number):
    return (current_page - 1) * 32 + button_number + 1

def set_current_page(page):
    global current_page
    current_page = page

def find_available_preset(camera):
    """
    Finds the next available preset number for a specific camera to ensure uniqueness.
    """
    existing_presets = set(camera_presets[camera])
    for i in range(1, camera_preset_count[camera] + 1):
        if i not in existing_presets:
            return i
    return camera_preset_count[camera]

def enregistrer_preset(deck, key, camera_number, recording_enabled, page):
    """
    Register a preset, ensuring uniqueness and handling overwrites.
    """
    global config_changed
    set_current_page(page)
    real_key = get_real_button_number(key)

    if not recording_enabled:
        print("L'enregistrement des presets est désactivé.")
        return

    if real_key in preset_camera_map:
        old_camera, old_preset = preset_camera_map[real_key]
        if old_preset in camera_presets[old_camera]:
            print(f"Suppression du preset {old_preset} pour la caméra {old_camera}.")
            camera_presets[old_camera].remove(old_preset)
        preset_number = old_preset if old_camera == camera_number else find_available_preset(camera_number)
    else:
        preset_number = find_available_preset(camera_number)

    # Ensure preset number is added to the list and increment if it's a new highest preset
    if preset_number not in camera_presets[camera_number]:
        camera_presets[camera_number].append(preset_number)
    if preset_number >= camera_preset_count[camera_number]:
        camera_preset_count[camera_number] = preset_number + 1

    command = bytes([0x80 + camera_number, 0x01, 0x04, 0x3F, 0x01, preset_number - 1, 0xFF])
    send_command(command)
    preset_camera_map[real_key] = (camera_number, preset_number)
    config_changed = True
    update_save_button(deck, config_changed)
    print(f"Enregistrement du preset {preset_number} pour la caméra {camera_number} sur le bouton {key}.")

def rappeler_preset(deck, key, page):
    """
    Recall a preset based on the button key and page.
    Lance la séquence dans un thread séparé pour permettre l'interruption.
    """
    set_current_page(page)
    real_key = get_real_button_number(key)

    if real_key in preset_camera_map:
        camera_to_use, preset_number = preset_camera_map[real_key]
        if preset_number in camera_presets[camera_to_use]:
            # Lancer la séquence dans un thread séparé pour ne pas bloquer le callback
            sequence_thread = threading.Thread(
                target=sequence_actions,
                args=(camera_to_use, preset_number, deck),
                daemon=True
            )
            sequence_thread.start()
            print(f"Rappel du preset {preset_number} pour la caméra {camera_to_use} depuis le bouton {key}.")
        else:
            print(f"Erreur : le preset {preset_number} n'existe pas pour la caméra {camera_to_use}.")
    else:
        print(f"Aucun preset enregistré pour le bouton {real_key}.")

def save_configuration(deck):
    global config_changed
    config_data = {
        'preset_camera_map': list(preset_camera_map.items()),
        'camera_preset_count': camera_preset_count
    }
    try:
        with open("save.conf", "w") as config_file:
            json.dump(config_data, config_file)
        config_changed = False
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
            camera_preset_count = config_data.get('camera_preset_count', {i: 1 for i in range(1, 7)})

            camera_presets = {i: [] for i in range(1, 7)}  # 6 caméras (1-6)
            for button, (camera, preset) in preset_camera_map.items():
                if camera in camera_presets:
                    camera_presets[camera].append(preset)

        adjust_camera_preset_count()
        update_save_button(deck, config_changed=False)
        print("Configuration chargée depuis save.conf.")
        return True
    else:
        update_save_button(deck, config_changed=True)
        print("Aucune configuration trouvée.")
        return False

def adjust_camera_preset_count():
    for camera in camera_presets:
        if camera_presets[camera]:
            camera_preset_count[camera] = max(camera_presets[camera]) + 1
        else:
            camera_preset_count[camera] = 1
