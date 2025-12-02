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

# Flag pour demander l'arrêt de la séquence
sequence_stop_requested = False

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
    global _blink_active, _blink_thread, sequence_running, sequence_stop_requested
    sequence_running = True
    sequence_stop_requested = False  # Réinitialiser le flag d'arrêt
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

def request_stop():
    """Demande l'arrêt de la séquence en cours"""
    global sequence_stop_requested
    sequence_stop_requested = True
    print("⚠️ Arrêt de la séquence demandé par l'utilisateur")

def is_stop_requested():
    """Vérifie si l'arrêt a été demandé"""
    return sequence_stop_requested

def interruptible_sleep(duration, check_interval=0.1):
    """
    Sleep interruptible qui vérifie périodiquement si l'arrêt est demandé.
    
    Args:
        duration: Durée totale du sleep en secondes
        check_interval: Intervalle de vérification en secondes
    
    Returns:
        True si le sleep s'est terminé normalement, False si interrompu
    """
    elapsed = 0
    while elapsed < duration:
        if sequence_stop_requested:
            return False
        time.sleep(min(check_interval, duration - elapsed))
        elapsed += check_interval
    return True

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
    La séquence peut être interrompue en appelant request_stop().
    
    Args:
        camera_number: Numéro de la caméra cible
        preset_number: Numéro du preset à rappeler
        deck: Instance du Stream Deck (optionnel, pour le clignotement)
    """
    global sequence_stop_requested
    
    # Démarrer le clignotement si le deck est fourni
    if deck:
        start_blink(deck)
    
    try:
        # Étape 1: Rappel explicite du preset 16 pour la caméra 6 (plan large)
        if is_stop_requested():
            print("🛑 Séquence interrompue avant l'étape 1")
            return
        print("Forçage du rappel du preset 16 pour la caméra 6 (plan large)")
        recall_preset(6, 16)
        print("Preset 16 pour la caméra 6 envoyé avec succès")

        # Étape 2: Temporisation (interruptible)
        if not interruptible_sleep(2):
            print("🛑 Séquence interrompue pendant la temporisation 1")
            return

        # Étape 3: Passer la caméra 6 en Preview
        if is_stop_requested():
            print("🛑 Séquence interrompue avant l'étape 3")
            return
        set_camera_preview(6)

        # Étape 4: Lancer la transition AUTO
        if is_stop_requested():
            print("🛑 Séquence interrompue avant l'étape 4")
            return
        auto_transition()
        
        if not interruptible_sleep(1.5):
            print("🛑 Séquence interrompue pendant la transition 1")
            return

        # Étape 5: Rappel du preset de la caméra active
        if is_stop_requested():
            print("🛑 Séquence interrompue avant l'étape 5")
            return
        if camera_number != 6:
            recall_preset(camera_number, preset_number)

        # Étape 6: Temporisation (interruptible)
        if not interruptible_sleep(2):
            print("🛑 Séquence interrompue pendant la temporisation 2")
            return

        # Étape 7: Passer la caméra active en Preview
        if is_stop_requested():
            print("🛑 Séquence interrompue avant l'étape 7")
            return
        set_camera_preview(camera_number)

        # Étape 8: Lancer la transition AUTO
        if is_stop_requested():
            print("🛑 Séquence interrompue avant l'étape 8")
            return
        auto_transition()
        
        if not interruptible_sleep(1.5):
            print("🛑 Séquence interrompue pendant la transition 2")
            return
        
        # Étape 9: Rappel explicite du preset 15 pour la caméra 6 (plan flou)
        if is_stop_requested():
            print("🛑 Séquence interrompue avant l'étape 9")
            return
        print("Forçage du rappel du preset 15 pour la caméra 6 (plan flou)")
        recall_preset(6, 15)
        print("Preset 15 pour la caméra 6 envoyé avec succès")
        
        print("✅ Séquence terminée avec succès")
    
    finally:
        # Réinitialiser le flag d'arrêt
        sequence_stop_requested = False
        # Arrêter le clignotement dans tous les cas
        if deck:
            stop_blink(deck)
