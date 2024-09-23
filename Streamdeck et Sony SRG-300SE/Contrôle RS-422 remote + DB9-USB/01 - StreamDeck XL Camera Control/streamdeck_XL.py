import time
import serial
from StreamDeck.DeviceManager import DeviceManager
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper
import json

# Numéro de la caméra (initialisé à 1)
camera_number = 1

# Dictionnaire pour stocker les presets associés à chaque caméra et chaque bouton
preset_camera_map = {}  # Associe chaque bouton de rappel à une caméra et un preset spécifique
camera_preset_count = {i: 1 for i in range(1, 9)}  # Compte les presets pour chaque caméra
camera_presets = {i: [] for i in range(1, 9)}  # Liste des presets actifs pour chaque caméra
recording_enabled = False  # Statut de l'enregistrement des presets
config_changed = False  # Indicateur de modification de la configuration

# Fonction pour envoyer une commande série à la caméra
def send_command(command, port='COM8', baudrate=38400):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            print(f"Envoi de la commande : {command.hex()}")
            ser.write(command)
            time.sleep(0.1)
            response = ser.read(64)
            if response:
                print(f"Réponse reçue: {response.hex()}")
            else:
                print("Aucune réponse reçue")
    except serial.SerialException as e:
        print(f"Erreur de communication série : {e}")

# Fonction pour vérifier s'il y a des "trous" dans les presets d'une caméra
def find_available_preset(camera):
    global camera_presets
    if camera not in camera_presets:
        camera_presets[camera] = []
    if camera not in camera_preset_count:
        camera_preset_count[camera] = 1

    for i in range(1, camera_preset_count[camera]):
        if i not in camera_presets[camera]:
            return i
    return camera_preset_count[camera]

# Fonction pour enregistrer un preset
def enregistrer_preset(button_number):
    global camera_preset_count, camera_presets, config_changed, recording_enabled

    if not recording_enabled:
        print("L'enregistrement des presets est désactivé. Veuillez activer l'enregistrement.")
        return

    if button_number + 8 in preset_camera_map:
        old_camera, old_preset = preset_camera_map[button_number + 8]

        if old_camera == camera_number:
            preset_number = old_preset
            print(f"Écrasement du preset {preset_number} pour la CAM {camera_number}")
        else:
            print(f"Suppression du preset {old_preset} pour la CAM {old_camera} et remplacement par la CAM {camera_number}")
            camera_presets[old_camera].remove(old_preset)
            preset_number = find_available_preset(camera_number)
            print(f"Enregistrement du preset {preset_number} pour la CAM {camera_number}")
            camera_presets[camera_number].append(preset_number)
    else:
        preset_number = find_available_preset(camera_number)
        print(f"Enregistrement du preset {preset_number} pour la CAM {camera_number}")
        camera_presets[camera_number].append(preset_number)

    command = bytes([0x80 + camera_number, 0x01, 0x04, 0x3F, 0x01, preset_number - 1, 0xFF])
    send_command(command)

    preset_camera_map[button_number + 8] = (camera_number, preset_number)

    if preset_number == camera_preset_count[camera_number]:
        camera_preset_count[camera_number] += 1

    config_changed = True
    update_save_button_color(deck, "orange")

# Fonction pour rappeler un preset
def rappeler_preset(button_number):
    if button_number in preset_camera_map:
        camera_to_use, preset_number = preset_camera_map[button_number]
        print(f"Rappel du preset {preset_number} pour la CAM {camera_to_use}")
        
        command = bytes([0x80 + camera_to_use, 0x01, 0x04, 0x3F, 0x02, preset_number - 1, 0xFF])
        send_command(command)
    else:
        print(f"Aucun preset enregistré pour le bouton {button_number}.")

# Fonction pour créer une image avec du texte
def create_text_image(deck, text, color="black", text_color="white"):
    image = Image.new("RGB", (48, 48), color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((image.width - text_width) // 2, (image.height - text_height) // 2)
    
    draw.text(text_position, text, fill=text_color, font=font)
    return PILHelper.to_native_format(deck, image)

# Fonction pour mettre à jour l'affichage du numéro de caméra sur le bouton 4
def update_camera_display(deck):
    camera_image = create_text_image(deck, f"Cam {camera_number}")
    deck.set_key_image(4, camera_image)

# Fonction pour changer la couleur et le texte du bouton toggle (bouton 8)
def update_toggle_button_color(deck, color, text):
    toggle_image = create_text_image(deck, text, color=color)
    deck.set_key_image(8, toggle_image)

# Fonction pour changer la couleur et le texte du bouton de sauvegarde (bouton 16)
def update_save_button_color(deck, color, text="Save"):
    save_image = create_text_image(deck, text, color=color)
    deck.set_key_image(16, save_image)

# Fonction pour sauvegarder la configuration dans un fichier
def sauvegarder_configuration():
    global config_changed
    with open("save.conf", "w") as config_file:
        json.dump({"preset_camera_map": preset_camera_map, "camera_preset_count": camera_preset_count, "camera_presets": camera_presets}, config_file)
    print("Configuration sauvegardée dans save.conf.")
    config_changed = False
    update_save_button_color(deck, "green", "Save")

# Fonction pour charger la configuration depuis un fichier
def charger_configuration():
    global preset_camera_map, camera_preset_count, camera_presets
    try:
        with open("save.conf", "r") as config_file:
            data = json.load(config_file)
            preset_camera_map = {int(k): v for k, v in data.get("preset_camera_map", {}).items()}  # Convertir les clés en entiers
            camera_preset_count = data.get("camera_preset_count", {i: 1 for i in range(1, 9)})
            camera_presets = data.get("camera_presets", {i: [] for i in range(1, 9)})
        print("Configuration chargée depuis save.conf.")
        print(f"preset_camera_map: {preset_camera_map}")
    except FileNotFoundError:
        print("Aucun fichier save.conf trouvé. Utilisation de la configuration par défaut.")

    for i in range(1, 9):
        camera_preset_count.setdefault(i, 1)
        camera_presets.setdefault(i, [])

# Fonction appelée lorsqu'un bouton du Stream Deck est pressé ou relâché
def handle_streamdeck_event(deck, key, state):
    global camera_number, recording_enabled, config_changed

    if state:
        print(f"Le bouton avec l'ID {key} a été pressé.")

        if key == 3:
            camera_number = max(1, camera_number - 1)
            print(f"Sélection de la caméra {camera_number}")
            update_camera_display(deck)
        elif key == 5:
            camera_number = min(8, camera_number + 1)
            print(f"Sélection de la caméra {camera_number}")
            update_camera_display(deck)
        elif 9 <= key <= 15:
            enregistrer_preset(key)
        elif 17 <= key <= 23:
            rappeler_preset(key)
        elif key == 8:
            recording_enabled = not recording_enabled
            status = "activé" if recording_enabled else "désactivé"
            color = "green" if recording_enabled else "red"
            print(f"L'enregistrement des presets est {status}.")
            update_toggle_button_color(deck, color, f"Rec {'ON' if recording_enabled else 'OFF'}")
        elif key == 16:
            sauvegarder_configuration()
    else:
        print(f"Le bouton avec l'ID {key} a été relâché.")

# Initialisation du Stream Deck
if __name__ == "__main__":
    charger_configuration()

    devices = DeviceManager().enumerate()
    if len(devices) == 0:
        print("Aucun Stream Deck détecté.")
        exit()

    deck = devices[0]
    deck.open()
    deck.set_brightness(30)

    update_camera_display(deck)
    update_toggle_button_color(deck, "red", "Rec OFF")
    update_save_button_color(deck, "green", "Save")

    deck.set_key_callback(handle_streamdeck_event)

    print("Stream Deck prêt. Appuyez sur les boutons pour enregistrer/rappeler les presets et changer la caméra.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        deck.close()
