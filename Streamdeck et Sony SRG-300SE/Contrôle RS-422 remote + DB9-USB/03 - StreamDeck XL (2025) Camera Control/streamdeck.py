## streamdeck.py
from display import create_button_image
from StreamDeck.DeviceManager import DeviceManager

def initialize_streamdeck():
    devices = DeviceManager().enumerate()
    if len(devices) == 0:
        print("Aucun Stream Deck détecté.")
        exit()

    deck = devices[0]
    deck.open()
    deck.set_brightness(30)
    return deck

previous_mode = None
previous_camera_number = None

def update_camera_buttons(deck, camera_number, recording_enabled):
    global previous_camera_number
    if recording_enabled:
        if camera_number != previous_camera_number:
            print(f"Caméra {camera_number} sélectionnée (bleu)")
            previous_camera_number = camera_number  
        
        for button, camera in zip(range(3, 8), range(1, 6)):
            color = "blue" if camera == camera_number else "black"
            deck.set_key_image(button, create_button_image(deck, f"CAM {camera}", color))

def set_toggle_button(deck, mode):
    global previous_mode
    color = "green" if mode == "STORE" else "red"
    deck.set_key_image(0, create_button_image(deck, mode, color))  
    if mode != previous_mode:
        print(f"Bouton toggle mis à jour pour le mode : {mode}")
        previous_mode = mode

def handle_streamdeck_event(deck, key, state, camera_number, recording_enabled, save_configuration, enregistrer_preset, rappeler_preset):
    if state:
        if key == 0:
            recording_enabled = not recording_enabled
            mode = "STORE" if recording_enabled else "RECALL"
            print(f"Changement de mode : {mode}")
            set_toggle_button(deck, mode)
            update_camera_buttons(deck, camera_number, recording_enabled)
        
        elif key == 1:
            save_configuration(deck)

        elif key in range(3, 8):
            if recording_enabled:
                camera_number = range(3, 8).index(key) + 1
                print(f"Caméra sélectionnée : {camera_number}")
                update_camera_buttons(deck, camera_number, recording_enabled)

        elif key in range(8, 32):
            if recording_enabled:
                enregistrer_preset(deck, key, camera_number, recording_enabled)
            else:
                rappeler_preset(deck, key)
                print(f"Preset rappelé pour la caméra {camera_number} avec le bouton {key}")

    return recording_enabled, camera_number
