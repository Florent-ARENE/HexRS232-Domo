# presets.py
import json
import os
from display import create_button_image
from camera import send_command

preset_camera_map = {}
camera_preset_count = {i: 1 for i in range(1, 5)}
camera_presets = {i: [] for i in range(1, 5)}

# Fonction pour trouver un preset disponible
def find_available_preset(camera):
    global camera_presets, camera_preset_count
    # Cherche le premier numéro de preset disponible pour cette caméra
    for i in range(1, camera_preset_count[camera]):
        if i not in camera_presets[camera]:
            return i
    return camera_preset_count[camera]

# Fonction pour ajuster le camera_preset_count lors du chargement
def adjust_camera_preset_count():
    global camera_preset_count, camera_presets
    for camera in camera_presets:
        if camera_presets[camera]:
            camera_preset_count[camera] = max(camera_presets[camera]) + 1
        else:
            camera_preset_count[camera] = 1

# Fonction pour enregistrer un preset
def enregistrer_preset(deck, key, camera_number, recording_enabled):
    global camera_preset_count, camera_presets, config_changed, preset_camera_map

    if not recording_enabled:
        print("L'enregistrement des presets est désactivé. Veuillez activer l'enregistrement.")
        return

    if key in preset_camera_map:
        old_camera, old_preset = preset_camera_map[key]
        
        # Vérifie que l'ancien preset existe bien avant de le supprimer
        if old_preset in camera_presets[old_camera]:
            print(f"Suppression du preset {old_preset} pour la caméra {old_camera} et remplacement par la caméra {camera_number}")
            camera_presets[old_camera].remove(old_preset)
        else:
            print(f"Erreur : le preset {old_preset} n'existe pas pour la caméra {old_camera}, impossible de le supprimer.")
        
        # Écrasement si même caméra, sinon remplacement par une autre caméra
        if old_camera == camera_number:
            preset_number = old_preset
            print(f"Écrasement du preset {preset_number} pour la caméra {camera_number}")
        else:
            preset_number = find_available_preset(camera_number)
            print(f"Enregistrement du nouveau preset {preset_number} pour la caméra {camera_number}")
            camera_presets[camera_number].append(preset_number)
    else:
        preset_number = find_available_preset(camera_number)
        print(f"Enregistrement du preset {preset_number} pour la caméra {camera_number}")
        camera_presets[camera_number].append(preset_number)

    # Commande VISCA pour enregistrer un preset pour la caméra sélectionnée
    command = bytes([0x80 + camera_number, 0x01, 0x04, 0x3F, 0x01, preset_number - 1, 0xFF])
    send_command(command)

    preset_camera_map[key] = (camera_number, preset_number)
    config_changed = True

    # Augmenter le compteur si le preset enregistré est le plus grand numéro de preset
    if preset_number == camera_preset_count[camera_number]:
        camera_preset_count[camera_number] += 1

    # Changer la couleur du bouton 16 pour indiquer que la configuration a changé
    deck.set_key_image(16, create_button_image(deck, "Save", "orange"))

def rappeler_preset(deck, button_number):
    if button_number in preset_camera_map:
        camera_to_use, preset_number = preset_camera_map[button_number]
        
        # Vérifie si le preset existe dans la caméra avant de tenter de le rappeler
        if preset_number in camera_presets[camera_to_use]:
            print(f"Rappel du preset {preset_number} pour la caméra {camera_to_use}")
            command = bytes([0x80 + camera_to_use, 0x01, 0x04, 0x3F, 0x02, preset_number - 1, 0xFF])
            send_command(command)
        else:
            print(f"Erreur : le preset {preset_number} n'existe pas pour la caméra {camera_to_use}")
    else:
        print(f"Aucun preset enregistré pour le bouton {button_number}.")

def save_configuration(deck):
    global preset_camera_map, camera_preset_count
    config_data = {
        'preset_camera_map': list(preset_camera_map.items()),
        'camera_preset_count': camera_preset_count
    }
    try:
        with open("save.conf", "w") as config_file:
            json.dump(config_data, config_file)
        print("Configuration sauvegardée dans save.conf")
        deck.set_key_image(16, create_button_image(deck, "Save", "green"))  # Changer en vert après la sauvegarde
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")
        deck.set_key_image(16, create_button_image(deck, "Save", "red"))  # Indiquer une erreur si besoin

def load_configuration(deck):
    global preset_camera_map, camera_preset_count, camera_presets

    if os.path.exists("save.conf"):
        with open("save.conf", "r") as config_file:
            config_data = json.load(config_file)
            preset_camera_map = dict(config_data.get('preset_camera_map', []))
            camera_preset_count = config_data.get('camera_preset_count', {i: 1 for i in range(1, 5)})

            # Restaurer les presets dans camera_presets pour chaque caméra
            camera_presets = {i: [] for i in range(1, 5)}
            for button, (camera, preset) in preset_camera_map.items():
                camera_presets[camera].append(preset)

        print("Configuration chargée depuis save.conf")
        adjust_camera_preset_count()  # Ajuste les presets après chargement
        deck.set_key_image(16, create_button_image(deck, "Save", "green"))
    else:
        print("Aucune configuration trouvée. Nouveau départ.")
        deck.set_key_image(16, create_button_image(deck, "Save", "orange"))

