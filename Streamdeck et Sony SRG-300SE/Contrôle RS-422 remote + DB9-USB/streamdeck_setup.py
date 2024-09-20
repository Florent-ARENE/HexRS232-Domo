import time
import serial
from StreamDeck.DeviceManager import DeviceManager

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

# Fonction pour enregistrer un preset
def enregistrer_preset(preset_number):
    print(f"Enregistrement du preset {preset_number} pour la CAM 1")
    # Commande VISCA pour enregistrer un preset
    command = bytes([0x81, 0x01, 0x04, 0x3F, 0x01, preset_number, 0xFF])
    send_command(command)

# Fonction pour rappeler un preset
def rappeler_preset(preset_number):
    print(f"Rappel du preset {preset_number} pour la CAM 1")
    # Commande VISCA pour rappeler un preset
    command = bytes([0x81, 0x01, 0x04, 0x3F, 0x02, preset_number, 0xFF])
    send_command(command)

# Fonction appelée lorsqu'un bouton du Stream Deck est pressé ou relâché
def handle_streamdeck_event(deck, key, state):
    if state:  # Si le bouton est pressé
        print(f"Le bouton avec l'ID {key} a été pressé.")
        
        # Associer les boutons 0, 1, 2 pour l'enregistrement des presets
        if key == 0:
            enregistrer_preset(0)  # Preset 1
        elif key == 1:
            enregistrer_preset(1)  # Preset 2
        elif key == 2:
            enregistrer_preset(2)  # Preset 3
        
        # Associer les boutons 3, 4, 5 pour le rappel des presets
        elif key == 3:
            rappeler_preset(0)  # Rappel Preset 1
        elif key == 4:
            rappeler_preset(1)  # Rappel Preset 2
        elif key == 5:
            rappeler_preset(2)  # Rappel Preset 3
    else:
        print(f"Le bouton avec l'ID {key} a été relâché.")

if __name__ == "__main__":
    # Initialisation du Stream Deck
    devices = DeviceManager().enumerate()
    if len(devices) == 0:
        print("Aucun Stream Deck détecté.")
        exit()

    deck = devices[0]  # Utiliser le premier Stream Deck détecté
    deck.open()
    deck.reset()  # Réinitialise l'état des boutons et des lumières

    # Réduire la luminosité
    deck.set_brightness(30)

    # Enregistrer la fonction de rappel pour les appuis et relâchements de touches
    deck.set_key_callback(handle_streamdeck_event)

    print("Stream Deck prêt. Appuyez sur les boutons pour enregistrer/rappeler les presets.")

    try:
        # Boucle pour maintenir le programme actif
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        # Libérer le Stream Deck avant de quitter
        deck.close()
