## camera.py
import serial
import time

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

def recall_preset_for_camera(camera_number, preset_number):
    # Commande VISCA pour rappeler un preset donné pour une caméra spécifique
    command_preset = b'\x81\x01\x04\x3F\x02' + preset_number.to_bytes(1, 'big') + b'\xFF'
    send_command(command_preset)
    print(f"Rappel du preset {preset_number} pour la caméra {camera_number}")

def pause_for_camera_movement():
    time.sleep(1.5)
    print("Pause de 1,5 seconde")
