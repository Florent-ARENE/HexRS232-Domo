## camera.py
import serial
import time
from display import create_button_image

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

def select_camera(deck, key=None):
    global camera_number

    if key:
        camera_number = [7, 15, 23, 31].index(key) + 1
        print(f"Caméra sélectionnée : {camera_number}")

    for button, camera in zip([7, 15, 23, 31], range(1, 5)):
        color = "blue" if camera == camera_number else "black"
        deck.set_key_image(button, create_button_image(deck, f"Cam {camera}", color))
