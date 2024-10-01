import time
import serial
from StreamDeck.DeviceManager import DeviceManager
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper
import os
import json
import PyATEMMax  # Ajout de la librairie PyATEMMax pour le Tally

# Connexion à l'ATEM
switcher = PyATEMMax.ATEMMax()
switcher.connect('172.18.29.12')
switcher.waitForConnection()

# Vérification de connexion
if not switcher.connected:
    print("Erreur de connexion à l'ATEM")
    exit()
else:
    print("Connecté à l'ATEM")

# Initialisation
camera_number = 1
recording_enabled = False
config_changed = False
preset_camera_map = {}
camera_preset_count = {i: 1 for i in range(1, 5)}
camera_presets = {i: [] for i in range(1, 5)}

# Configuration des caméras sur les boutons du Stream Deck
camera_input_map = {
    1: "input1",  # Caméra 1
    2: "input2",  # Caméra 2
    3: "input3",  # Caméra 3
    4: "input8"   # Caméra 4
}

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
    for i in range(1, camera_preset_count[camera]):
        if i not in camera_presets[camera]:
            return i
    return camera_preset_count[camera]

# Fonction pour ajuster le camera_preset_count lors du chargement
def adjust_camera_preset_count():
    global camera_preset_count, camera_presets
    for camera in camera_presets:
        if camera_presets[camera]:
            # Ajuste le compteur de presets à un au-dessus du dernier preset enregistré
            camera_preset_count[camera] = max(camera_presets[camera]) + 1
        else:
            # Si aucun preset n'existe pour la caméra, on démarre à 1
            camera_preset_count[camera] = 1

# Fonction pour enregistrer un preset
def enregistrer_preset(button_number):
    global camera_preset_count, camera_presets, config_changed

    if not recording_enabled:
        print("L'enregistrement des presets est désactivé. Veuillez activer l'enregistrement.")
        return

    preset_number = find_available_preset(camera_number)
    print(f"Enregistrement du preset {preset_number} pour la CAM {camera_number}")
    camera_presets[camera_number].append(preset_number)

    preset_camera_map[button_number] = (camera_number, preset_number)
    config_changed = True

    # Commande VISCA pour enregistrer un preset pour la caméra sélectionnée
    command = bytes([0x80 + camera_number, 0x01, 0x04, 0x3F, 0x01, preset_number - 1, 0xFF])
    send_command(command)

    # Changer la couleur du bouton 16 pour indiquer que la configuration a changé
    deck.set_key_image(16, create_button_image(deck, "Save", "orange"))

# Fonction pour rappeler un preset
def rappeler_preset(button_number):
    if button_number in preset_camera_map:
        camera_to_use, preset_number = preset_camera_map[button_number]
        print(f"Rappel du preset {preset_number} pour la CAM {camera_to_use}")
        command = bytes([0x80 + camera_to_use, 0x01, 0x04, 0x3F, 0x02, preset_number - 1, 0xFF])
        send_command(command)
    else:
        print(f"Aucun preset enregistré pour le bouton {button_number}.")

# Fonction pour créer une image avec texte et couleur de fond pour les boutons
def create_button_image(deck, text, color):
    image = Image.new("RGB", (48, 48), color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_position = ((image.width - (text_bbox[2] - text_bbox[0])) // 2,
                     (image.height - (text_bbox[3] - text_bbox[1])) // 2)
    draw.text(text_position, text, fill="white", font=font)
    return PILHelper.to_native_format(deck, image)

# Fonction pour mettre à jour les boutons de caméra en mode RECALL avec le Tally
def update_tally(deck):
    try:
        program_input = str(switcher.programInput[0].videoSource)
        preview_input = str(switcher.previewInput[0].videoSource)

        # Afficher les inputs récupérés pour débogage
        print(f"Program Input exact: {program_input}")
        print(f"Preview Input exact: {preview_input}")

        # Mise à jour des boutons 7, 15, 23, 31 en fonction des inputs
        for button_id, input_id in zip([7, 15, 23, 31], camera_input_map.values()):
            if program_input == input_id:
                color = (255, 0, 0)  # Rouge pour Program
                print(f"Bouton {button_id} en Program (rouge)")
            elif preview_input == input_id:
                color = (0, 255, 0)  # Vert pour Preview
                print(f"Bouton {button_id} en Preview (vert)")
            else:
                color = (0, 0, 0)  # Noir pour inactif
                print(f"Bouton {button_id} inactif (noir)")

            # Mettre à jour le bouton correspondant avec la couleur
            deck.set_key_image(button_id, create_button_image(deck, f"Cam {button_id // 8 + 1}", color))

    except Exception as e:
        print(f"Erreur lors de la mise à jour du Tally: {e}")

# Fonction pour sauvegarder la configuration dans un fichier
def save_configuration():
    config_data = {
        'preset_camera_map': list(preset_camera_map.items()),
        'camera_preset_count': camera_preset_count
    }
    with open("save.conf", "w") as config_file:
        json.dump(config_data, config_file)
    print("Configuration sauvegardée dans save.conf")
    deck.set_key_image(16, create_button_image(deck, "Save", "green"))

# Fonction pour charger la configuration depuis un fichier
def load_configuration():
    global preset_camera_map, camera_preset_count
    if os.path.exists("save.conf"):
        with open("save.conf", "r") as config_file:
            config_data = json.load(config_file)
            preset_camera_map = dict(config_data.get('preset_camera_map', []))
            camera_preset_count = config_data.get('camera_preset_count', {i: 1 for i in range(1, 5)})
            print("Configuration chargée depuis save.conf")
            adjust_camera_preset_count()  # Appelle la fonction pour ajuster les presets
            deck.set_key_image(16, create_button_image(deck, "Save", "green"))
    else:
        print("Aucune configuration trouvée. Nouveau départ.")
        deck.set_key_image(16, create_button_image(deck, "Save", "orange"))

# Fonction pour gérer les événements du StreamDeck
def handle_streamdeck_event(deck, key, state):
    global recording_enabled, camera_number, config_changed, is_recall_mode
    if state:
        if key == 8:
            recording_enabled = not recording_enabled
            mode = "STORE" if recording_enabled else "RECALL"
            print(f"Changement de mode : {mode}")
            color = "green" if recording_enabled else "red"
            deck.set_key_image(8, create_button_image(deck, mode, color))
            is_recall_mode = not recording_enabled  # Définit si on est en mode RECALL
            update_camera_buttons(deck)  # Mettre à jour les boutons caméra
        elif key == 16:
            save_configuration()
        elif key in [7, 15, 23, 31]:
            camera_number = [7, 15, 23, 31].index(key) + 1
            print(f"Caméra sélectionnée : {camera_number} en mode {'STORE' if recording_enabled else 'RECALL'}")
            update_camera_buttons(deck)
        elif key in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30]:
            if recording_enabled:
                enregistrer_preset(key)
            else:
                rappeler_preset(key)
    else:
        print(f"Le bouton avec l'ID {key} a été relâché.")

# Fonction pour mettre à jour les boutons caméra en fonction du mode actuel
def update_camera_buttons(deck):
    if recording_enabled:
        # Mode STORE : affichage des boutons dessinés
        for button, camera in zip([7, 15, 23, 31], range(1, 5)):
            color = "blue" if camera == camera_number else "black"
            deck.set_key_image(button, create_button_image(deck, f"Cam {camera}", color))
    else:
        # Mode RECALL : mise à jour du Tally
        update_tally(deck)

# Initialisation du Stream Deck
devices = DeviceManager().enumerate()
if len(devices) == 0:
    print("Aucun Stream Deck détecté.")
    exit()

deck = devices[0]
deck.open()
deck.set_brightness(30)

load_configuration()

# Initialisation des boutons caméra
update_camera_buttons(deck)

# Bouton toggle par défaut (rouge) pour "recall preset"
deck.set_key_image(8, create_button_image(deck, "RECALL", "red"))

deck.set_key_callback(handle_streamdeck_event)

print("Stream Deck prêt. Appuyez sur les boutons pour enregistrer/rappeler les presets et changer la caméra.")

# Boucle principale pour mettre à jour les Tally toutes les secondes
try:
    while True:
        if not recording_enabled:
            update_tally(deck)  # Mettre à jour le Tally seulement en mode RECALL
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    deck.close()
    switcher.disconnect()
