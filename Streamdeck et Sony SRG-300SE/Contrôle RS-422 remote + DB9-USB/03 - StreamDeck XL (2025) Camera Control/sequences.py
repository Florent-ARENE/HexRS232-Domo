## sequences.py
import time
from atem import switcher  # Importation de la connexion ATEM depuis atem.py
from tally import camera_input_map  # Importation du tableau des caméras depuis tally.py
from camera import send_command  # Importation de la fonction depuis camera.py

def set_camera_preview(camera_number):
    try:
        if camera_number in camera_input_map:
            input_name = f"input{camera_input_map[camera_number]}"  # Concaténation pour obtenir 'input1', 'input8', etc.
            print(f"Passage de la caméra {camera_number} (input {input_name}) en Preview")
            switcher.setPreviewInputVideoSource(0, input_name)  # Met la caméra en Preview sur ME 0
        else:
            print(f"Erreur : La caméra {camera_number} n'est pas valide ou n'est pas mappée.")
    except Exception as e:
        print(f"Erreur: Impossible de mettre la caméra {camera_number} en Preview : {e}")

def auto_transition():
    try:
        print("Lancement de la transition AUTO")
        switcher.execAutoME(0)  # Effectue la transition auto sur le bus ME 0
        print("Transition AUTO effectuée avec succès")
    except Exception as e:
        print(f"Erreur: La transition automatique a échoué : {e}")

def recall_preset(camera_number, preset_number):
    # Ajuster l'octet de départ en fonction du numéro de la caméra
    command_prefix = 0x80 + camera_number  # Par exemple, 0x84 pour la caméra 4
    print(f"Rappel du preset {preset_number} pour la caméra {camera_number}")
    
    # Construire la commande VISCA en fonction de la caméra et du preset
    visca_command = bytes([command_prefix, 0x01, 0x04, 0x3F, 0x02, preset_number - 1, 0xFF])
    
    # Envoyer la commande
    send_command(visca_command)



def sequence_actions(camera_number, preset_number):
    # Étape 1: Rappel explicite du preset 16 pour la caméra 6 (plan large)
    print("Forçage du rappel du preset 16 pour la caméra 6 (plan large)")
    recall_preset(6, 16)  # Envoi explicite du preset 16
    print("Preset 16 pour la caméra 6 envoyé avec succès")  # Log ajouté ici

    # Étape 2: Temporisation de 1,5 seconde pour laisser le temps à la caméra de se caler
    time.sleep(2)

    # Étape 3: Passer la caméra 6 en Preview
    set_camera_preview(6)

    # Étape 4: Lancer la transition AUTO pour la caméra 6
    auto_transition()
    time.sleep(1.5)

    # Étape 5: Rappel du preset de la caméra active (par exemple, caméra 1)
    if camera_number != 6:  # Ne pas rappeler le preset si c'est déjà la caméra 6
        recall_preset(camera_number, preset_number)

    # Étape 6: Temporisation de 1,5 seconde pour laisser la caméra se caler
    time.sleep(2)

    # Étape 7: Passer la caméra active en Preview
    set_camera_preview(camera_number)

    # Étape 8: Lancer la transition AUTO pour la caméra active
    auto_transition()
    time.sleep(1.5)
    
    # Étape 9: Rappel explicite du preset 15 pour la caméra 6 (plan flou)
    print("Forçage du rappel du preset 16 pour la caméra 6 (plan flou)")
    recall_preset(6, 15)  # Envoi explicite du preset 16
    print("Preset 15 pour la caméra 6 envoyé avec succès")  # Log ajouté ici
