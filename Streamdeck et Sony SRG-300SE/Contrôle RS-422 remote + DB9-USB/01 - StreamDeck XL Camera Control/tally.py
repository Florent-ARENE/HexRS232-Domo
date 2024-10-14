## tally.py
from atem import switcher
from display import create_button_image

# Correspondance unifiée entre les inputs ATEM et les numéros de caméras
camera_input_map = {
    1: 1,  # Caméra 1 correspond à 'input1' de l'ATEM
    2: 2,  # Caméra 2 correspond à 'input2' de l'ATEM
    3: 3,  # Caméra 3 correspond à 'input3' de l'ATEM
    4: 8   # Caméra 4 correspond à 'input8' de l'ATEM
}

# Inverser la correspondance pour retrouver la caméra depuis un input
input_to_camera_map = {str(v): k for k, v in camera_input_map.items()}

# Variables globales pour suivre l'état précédent du Tally
previous_program_input = None
previous_preview_input = None
previous_program_unknown = False
previous_preview_unknown = False

def update_tally(deck):
    global previous_program_input, previous_preview_input, previous_program_unknown, previous_preview_unknown

    try:
        # Extraire directement la valeur de la source de programme et de preview
        program_input = str(switcher.programInput[0].videoSource)  # Convertir l'objet ATEM en string
        preview_input = str(switcher.previewInput[0].videoSource)  # Convertir l'objet ATEM en string

        # Ajout de debug pour afficher les valeurs brutes de l'ATEM
        #print(f"Debug: Valeur brute program_input: {program_input}")
        #print(f"Debug: Valeur brute preview_input: {preview_input}")

        # Utiliser les valeurs extraites directement
        program_camera = input_to_camera_map.get(program_input.replace('input', ''), None)
        preview_camera = input_to_camera_map.get(preview_input.replace('input', ''), None)

        # Gestion des sources non mappées (affiche seulement si le changement survient)
        if program_camera is None and not previous_program_unknown:
            print(f"Debug: La source de program '{program_input}' n'est pas une caméra mappée.")
            previous_program_unknown = True
        elif program_camera is not None:
            previous_program_unknown = False

        if preview_camera is None and not previous_preview_unknown:
            print(f"Debug: La source de preview '{preview_input}' n'est pas une caméra mappée.")
            previous_preview_unknown = True
        elif preview_camera is not None:
            previous_preview_unknown = False

        # Mettre à jour l'affichage des boutons sur le Stream Deck
        for button_id, camera_num in zip([7, 15, 23, 31], camera_input_map.keys()):
            input_name = f"input{camera_input_map[camera_num]}"  # Concaténation pour obtenir 'input1', 'input8', etc.
            if program_input == input_name:
                color = (255, 0, 0)  # Rouge pour Program
            elif preview_input == input_name:
                color = (0, 255, 0)  # Vert pour Preview
            else:
                color = (0, 0, 0)    # Noir pour les autres

            deck.set_key_image(button_id, create_button_image(deck, f"Cam {camera_num}", color))

        # Si le Tally a changé, afficher les informations de verbose
        if program_input != previous_program_input or preview_input != previous_preview_input:
            program_message = f"Program : Cam {program_camera if program_camera else 'Unknown'} (rouge) | {program_input if program_camera else 'Source inconnue'}"
            preview_message = f"Preview : Cam {preview_camera if preview_camera else 'Unknown'} (vert) | {preview_input if preview_camera else 'Source inconnue'}"
            print(f"{program_message}\n{preview_message}")

            # Mettre à jour les valeurs précédentes uniquement si ça change
            previous_program_input = program_input
            previous_preview_input = preview_input

    except Exception as e:
        print(f"Erreur lors de la mise à jour du Tally: {e}")
