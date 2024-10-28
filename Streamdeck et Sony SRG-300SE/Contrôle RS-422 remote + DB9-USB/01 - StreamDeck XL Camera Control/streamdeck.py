## streamdeck.py
from display import create_button_image
from StreamDeck.DeviceManager import DeviceManager

# Fonction pour initialiser le Stream Deck
def initialize_streamdeck():
    devices = DeviceManager().enumerate()
    if len(devices) == 0:
        print("Aucun Stream Deck détecté.")
        exit()

    deck = devices[0]
    deck.open()
    deck.set_brightness(30)
    return deck

# Variable pour suivre le dernier mode et éviter les répétitions de messages
previous_mode = None

# Fonction pour mettre à jour les boutons des caméras en mode STORE
# Ajouter une variable globale pour mémoriser la caméra précédemment sélectionnée
previous_camera_number = None

# Fonction pour mettre à jour les boutons des caméras en mode STORE
def update_camera_buttons(deck, camera_number, recording_enabled):
    global previous_camera_number
    # Mode STORE : affichage des boutons dessinés pour la caméra active
    if recording_enabled:
        # Ne pas répéter l'affichage si la caméra sélectionnée est la même que la précédente
        if camera_number != previous_camera_number:
            print(f"Caméra {camera_number} sélectionnée (blue)")
            previous_camera_number = camera_number  # Mettre à jour l'état précédent
        
        for button, camera in zip([7, 15, 23, 31], range(1, 5)):
            color = "blue" if camera == camera_number else "black"
            deck.set_key_image(button, create_button_image(deck, f"Cam {camera}", color))

# Fonction pour gérer le bouton de bascule entre STORE et RECALL
def set_toggle_button(deck, mode):
    global previous_mode
    color = "green" if mode == "STORE" else "red"
    deck.set_key_image(8, create_button_image(deck, mode, color))  # Toujours mettre à jour le visuel du bouton
    # Vérifie si le mode a changé pour éviter les doublons d'affichage du message
    if mode != previous_mode:
        print(f"Bouton toggle mis à jour pour le mode : {mode}")
        previous_mode = mode  # Met à jour le dernier mode utilisé pour le suivi du message

# Fonction pour gérer les événements du Stream Deck
def handle_streamdeck_event(deck, key, state, camera_number, recording_enabled, save_configuration, enregistrer_preset, rappeler_preset):
    if state:
        if key == 8:
            # Basculer entre les modes STORE et RECALL
            recording_enabled = not recording_enabled
            mode = "STORE" if recording_enabled else "RECALL"
            print(f"Changement de mode : {mode}")
            set_toggle_button(deck, mode)
            update_camera_buttons(deck, camera_number, recording_enabled)
        
        elif key == 16:
            # Sauvegarde de la configuration
            save_configuration(deck)

        elif key in [7, 15, 23, 31]:
            # Sélection de la caméra uniquement en mode STORE
            if recording_enabled:
                camera_number = [7, 15, 23, 31].index(key) + 1
                print(f"Caméra sélectionnée : {camera_number}")
                update_camera_buttons(deck, camera_number, recording_enabled)

        elif key in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30]:
            # Enregistrer ou rappeler un preset selon le mode actuel
            if recording_enabled:
                enregistrer_preset(deck, key, camera_number, recording_enabled)
            else:
                rappeler_preset(deck, key)
                print(f"Preset rappelé pour la caméra {camera_number} avec le bouton {key}")

    return recording_enabled, camera_number
