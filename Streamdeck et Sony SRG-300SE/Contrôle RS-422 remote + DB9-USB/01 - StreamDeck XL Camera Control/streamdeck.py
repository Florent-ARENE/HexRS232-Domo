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

def update_camera_buttons(deck, camera_number, recording_enabled):
    # Mode STORE : affichage des boutons dessinés pour la caméra active
    if recording_enabled:
        for button, camera in zip([7, 15, 23, 31], range(1, 5)):
            color = "blue" if camera == camera_number else "black"
            deck.set_key_image(button, create_button_image(deck, f"Cam {camera}", color))
        print(f"Caméra {camera_number} sélectionnée (blue)")
    else:
        print(f"Mode RECALL actif, mise à jour des boutons non nécessaire.")

def set_toggle_button(deck, mode):
    color = "green" if mode == "STORE" else "red"
    deck.set_key_image(8, create_button_image(deck, mode, color))

def handle_streamdeck_event(deck, key, state, camera_number, recording_enabled, save_configuration, enregistrer_preset, rappeler_preset, update_camera_buttons):
    if state:
        if key == 8:
            recording_enabled = not recording_enabled
            mode = "STORE" if recording_enabled else "RECALL"
            set_toggle_button(deck, mode)
            update_camera_buttons(deck, camera_number, recording_enabled)
        elif key == 16:
            save_configuration(deck)
        elif key in [7, 15, 23, 31]:
            camera_number = [7, 15, 23, 31].index(key) + 1
            update_camera_buttons(deck, camera_number, recording_enabled)
        elif key in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30]:
            if recording_enabled:
                enregistrer_preset(deck, key, camera_number, recording_enabled)
            else:
                rappeler_preset(deck, key)
