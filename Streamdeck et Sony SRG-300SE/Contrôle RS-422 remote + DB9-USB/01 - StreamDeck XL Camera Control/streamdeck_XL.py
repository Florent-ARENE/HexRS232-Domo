import time
import serial
from StreamDeck.DeviceManager import DeviceManager
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper

# Numéro de la caméra (initialisé à 1)
camera_number = 1

# Dictionnaire pour stocker les presets associés à chaque caméra et chaque bouton
preset_camera_map = {}  # Associe chaque bouton de rappel à une caméra et un preset spécifique
camera_preset_count = {i: 1 for i in range(1, 9)}  # Compte les presets pour chaque caméra
camera_presets = {i: [] for i in range(1, 9)}  # Liste des presets actifs pour chaque caméra

# État du toggle pour l'enregistrement (False = désactivé, True = activé)
recording_enabled = False

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

# Fonction pour enregistrer un preset
def enregistrer_preset(button_number):
    global camera_preset_count, camera_presets, recording_enabled

    if not recording_enabled:
        print("Enregistrement de presets désactivé.")
        return

    # Si un preset a déjà été enregistré sur ce bouton, on vérifie si c'est pour la même caméra
    if button_number + 8 in preset_camera_map:
        old_camera, old_preset = preset_camera_map[button_number + 8]
        
        if old_camera == camera_number:
            preset_number = old_preset
            print(f"Écrasement du preset {preset_number} pour la CAM {camera_number}")
        else:
            # Si c'était pour une autre caméra, on supprime le preset de cette caméra
            print(f"Suppression du preset {old_preset} pour la CAM {old_camera} et remplacement par la CAM {camera_number}")
            camera_presets[old_camera].remove(old_preset)
            # Trouver un "trou" à combler pour la caméra actuelle
            preset_number = find_available_preset(camera_number)
            print(f"Enregistrement du preset {preset_number} pour la CAM {camera_number}")
            camera_presets[camera_number].append(preset_number)
    else:
        # Si aucun preset n'était enregistré sur ce bouton, on enregistre normalement
        preset_number = find_available_preset(camera_number)
        print(f"Enregistrement du preset {preset_number} pour la CAM {camera_number}")
        camera_presets[camera_number].append(preset_number)

    # Commande VISCA pour enregistrer un preset pour la caméra sélectionnée
    command = bytes([0x80 + camera_number, 0x01, 0x04, 0x3F, 0x01, preset_number - 1, 0xFF])
    send_command(command)

    # Associer le bouton de rappel correspondant (17 à 23) avec la caméra et le preset enregistré
    preset_camera_map[button_number + 8] = (camera_number, preset_number)

    # Incrémenter le compteur de preset uniquement si aucun "trou" n'a été comblé
    if preset_number == camera_preset_count[camera_number]:
        camera_preset_count[camera_number] += 1

# Fonction pour rappeler un preset
def rappeler_preset(button_number):
    if button_number in preset_camera_map:
        camera_to_use, preset_number = preset_camera_map[button_number]
        print(f"Rappel du preset {preset_number} pour la CAM {camera_to_use}")
        
        # Commande VISCA pour rappeler un preset pour la caméra associée
        command = bytes([0x80 + camera_to_use, 0x01, 0x04, 0x3F, 0x02, preset_number - 1, 0xFF])
        send_command(command)
    else:
        print(f"Aucun preset enregistré pour le bouton {button_number}.")

# Fonction pour créer une image avec le numéro de la caméra ou l'état du toggle
def create_camera_image(deck, number):
    image = Image.new("RGB", (48, 48), "black")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # Centrer le texte (numéro de caméra)
    text = f"Cam {number}"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((image.width - text_width) // 2, (image.height - text_height) // 2)
    
    draw.text(text_position, text, fill="white", font=font)
    return PILHelper.to_native_format(deck, image)

# Fonction pour créer une image verte ou rouge pour le toggle
def create_toggle_image(deck, is_enabled):
    image = Image.new("RGB", (48, 48), "green" if is_enabled else "red")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # Centrer le texte (On ou Off)
    text = "On" if is_enabled else "Off"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((image.width - text_width) // 2, (image.height - text_height) // 2)
    
    draw.text(text_position, text, fill="white", font=font)
    return PILHelper.to_native_format(deck, image)

# Fonction pour mettre à jour l'affichage du numéro de caméra sur le bouton 4
def update_camera_display(deck):
    camera_image = create_camera_image(deck, camera_number)
    deck.set_key_image(4, camera_image)

# Fonction pour mettre à jour l'affichage du bouton toggle sur le bouton 8
def update_toggle_display(deck):
    toggle_image = create_toggle_image(deck, recording_enabled)
    deck.set_key_image(8, toggle_image)

# Fonction appelée lorsqu'un bouton du Stream Deck est pressé ou relâché
def handle_streamdeck_event(deck, key, state):
    global camera_number, recording_enabled
    if state:  # Si le bouton est pressé
        print(f"Le bouton avec l'ID {key} a été pressé.")
        
        # Bouton toggle sur le bouton 8
        if key == 8:
            recording_enabled = not recording_enabled
            update_toggle_display(deck)
            status = "activé" if recording_enabled else "désactivé"
            print(f"Enregistrement de presets {status}.")
        
        # Boutons pour changer le numéro de la caméra (flèches < et >)
        elif key == 3:  # Flèche <
            camera_number = max(1, camera_number - 1)
            print(f"Sélection de la caméra {camera_number}")
            update_camera_display(deck)
        elif key == 5:  # Flèche >
            camera_number = min(8, camera_number + 1)  # Limité à 8 caméras
            print(f"Sélection de la caméra {camera_number}")
            update_camera_display(deck)
        
        # Boutons pour enregistrer les presets (9 à 15)
        elif 9 <= key <= 15:
            enregistrer_preset(key)
        
        # Boutons pour rappeler les presets (17 à 23)
        elif 17 <= key <= 23:
            rappeler_preset(key)
    else:
        print(f"Le bouton avec l'ID {key} a été relâché.")

if __name__ == "__main__":
    devices = DeviceManager().enumerate()
    if len(devices) == 0:
        print("Aucun Stream Deck détecté.")
        exit()

    deck = devices[0]  # Utiliser le premier Stream Deck détecté
    deck.open()

    # Réduire la luminosité
    deck.set_brightness(30)

    # Mise à jour initiale de l'affichage du numéro de caméra et du toggle
    update_camera_display(deck)
    update_toggle_display(deck)

    # Enregistrer la fonction de rappel pour les appuis et relâchements de touches
    deck.set_key_callback(handle_streamdeck_event)

    print("Stream Deck prêt. Appuyez sur les boutons pour enregistrer/rappeler les presets et changer la caméra.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        # Libérer le Stream Deck avant de quitter
        deck.close()
