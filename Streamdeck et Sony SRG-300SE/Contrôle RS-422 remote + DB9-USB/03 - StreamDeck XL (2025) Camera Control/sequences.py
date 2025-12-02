## sequences.py
import time
import threading
from atem import switcher  # Importation de la connexion ATEM depuis atem.py
from tally import camera_input_map  # Importation du tableau des caméras depuis tally.py
from camera import send_command  # Importation de la fonction depuis camera.py
from display import create_button_image

# Variables globales pour le clignotement
_blink_active = False
_blink_thread = None

# Flag exporté pour bloquer update_display() pendant la séquence
sequence_running = False

def _blink_recall_button(deck):
    """Thread qui fait pulser le bouton RECALL pendant la séquence (effet breathing)"""
    global _blink_active
    
    min_intensity = 30
    max_intensity = 255
    steps = 20
    delay = 0.04
    
    intensity = min_intensity
    direction = 1
    step_size = (max_intensity - min_intensity) // (steps // 2)
    
    while _blink_active:
        try:
            deck.set_key_image(0, create_button_image(deck, "RECALL", (intensity, 0, 0), text_color="white", bold=True))
        except Exception:
            pass  # Ignorer les erreurs si le deck est occupé
        
        intensity += direction * step_size
        
        if intensity >= max_intensity:
            intensity = max_intensity
            direction = -1
        elif intensity <= min_intensity:
            intensity = min_intensity
            direction = 1
        
        time.sleep(delay)

def start_blink(deck):
    """Démarre le clignotement du bouton RECALL"""
    global _blink_active, _blink_thread, sequence_running
    sequence_running = True
    _blink_active = True
    _blink_thread = threading.Thread(target=_blink_recall_button, args=(deck,), daemon=True)
    _blink_thread.start()

def stop_blink(deck):
    """Arrête le clignotement et restaure le bouton RECALL normal"""
    global _blink_active, _blink_thread, sequence_running
    _blink_active = False
    if _blink_thread:
        _blink_thread.join(timeout=0.5)
    sequence_running = False
    # Restaurer le bouton RECALL en rouge foncé normal
    try:
        deck.set_key_image(0, create_button_image(deck, "RECALL", (139, 0, 0), text_color="white", bold=True))
    except Exception:
        pass

def set_camera_preview(camera_number):
    try:
        if camera_number in camera_input_map:
            input_name = f"input{camera_input_map[camera_number]}"
            print(f"Passage de la caméra {camera_number} (input {input_name}) en Preview")
            switcher.setPreviewInputVideoSource(0, input_name)
        else:
            print(f"Erreur : La caméra {camera_number} n'est pas valide ou n'est pas mappée.")
    except Exception as e:
        print(f"Erreur: Impossible de mettre la caméra {camera_number} en Preview : {e}")

def auto_transition():
    try:
        print("Lancement de la transition AUTO")
        switcher.execAutoME(0)
        print("Transition AUTO effectuée avec succès")
    except Exception as e:
        print(f"Erreur: La transition automatique a échoué : {e}")

def recall_preset(camera_number, preset_number):
    command_prefix = 0x80 + camera_number
    print(f"Rappel du preset {preset_number} pour la caméra {camera_number}")
    visca_command = bytes([command_prefix, 0x01, 0x04, 0x3F, 0x02, preset_number - 1, 0xFF])
    send_command(visca_command)


def sequence_actions(camera_number, preset_number, deck=None):
    """
    Exécute la séquence de transition avec clignotement du bouton RECALL.
    
    Args:
        camera_number: Numéro de la caméra cible
        preset_number: Numéro du preset à rappeler
        deck: Instance du Stream Deck (optionnel, pour le clignotement)
    """
    # Démarrer le clignotement si le deck est fourni
    if deck:
        start_blink(deck)
    
    try:
        # Étape 1: Rappel explicite du preset 16 pour la caméra 6 (plan large)
        print("Forçage du rappel du preset 16 pour la caméra 6 (plan large)")
        recall_preset(6, 16)
        print("Preset 16 pour la caméra 6 envoyé avec succès")

        # Étape 2: Temporisation
        time.sleep(2)

        # Étape 3: Passer la caméra 6 en Preview
        set_camera_preview(6)

        # Étape 4: Lancer la transition AUTO
        auto_transition()
        time.sleep(1.5)

        # Étape 5: Rappel du preset de la caméra active
        if camera_number != 6:
            recall_preset(camera_number, preset_number)

        # Étape 6: Temporisation
        time.sleep(2)

        # Étape 7: Passer la caméra active en Preview
        set_camera_preview(camera_number)

        # Étape 8: Lancer la transition AUTO
        auto_transition()
        time.sleep(1.5)
        
        # Étape 9: Rappel explicite du preset 15 pour la caméra 6 (plan flou)
        print("Forçage du rappel du preset 15 pour la caméra 6 (plan flou)")
        recall_preset(6, 15)
        print("Preset 15 pour la caméra 6 envoyé avec succès")
    
    finally:
        # Arrêter le clignotement dans tous les cas
        if deck:
            stop_blink(deck)
