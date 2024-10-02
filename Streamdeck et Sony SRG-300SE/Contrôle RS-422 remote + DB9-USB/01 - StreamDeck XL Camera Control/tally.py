## tally.py
from atem import switcher
from display import create_button_image

# Correspondance entre les inputs ATEM et les numéros de caméras
camera_input_map = {
    1: "input1",
    2: "input2",
    3: "input3",
    4: "input8"
}

# Inverser la correspondance pour retrouver la caméra depuis un input
input_to_camera_map = {v: k for k, v in camera_input_map.items()}

# Variables globales pour suivre l'état précédent du Tally
previous_program_input = None
previous_preview_input = None

def update_tally(deck):
    global previous_program_input, previous_preview_input

    try:
        program_input = str(switcher.programInput[0].videoSource)
        preview_input = str(switcher.previewInput[0].videoSource)

        # Trouver les caméras associées aux inputs
        program_camera = input_to_camera_map.get(program_input, "Unknown")
        preview_camera = input_to_camera_map.get(preview_input, "Unknown")

        # Mettre à jour l'affichage des boutons sur le Stream Deck
        for button_id, input_id in zip([7, 15, 23, 31], camera_input_map.values()):
            if program_input == input_id:
                color = (255, 0, 0)  # Rouge pour Program
            elif preview_input == input_id:
                color = (0, 255, 0)  # Vert pour Preview
            else:
                color = (0, 0, 0)    # Noir pour les autres

            deck.set_key_image(button_id, create_button_image(deck, f"Cam {button_id // 8 + 1}", color))

        # Si le Tally a changé, afficher les informations de verbose
        if program_input != previous_program_input or preview_input != previous_preview_input:
            program_message = f"Program : Cam {program_camera} (rouge) | {program_input} Bouton {7 + (program_camera - 1) * 8}"
            preview_message = f"Preview : Cam {preview_camera} (vert) | {preview_input} Bouton {7 + (preview_camera - 1) * 8}"
            print(f"{program_message}\n{preview_message}")

            # Mettre à jour les valeurs précédentes uniquement si ça change
            previous_program_input = program_input
            previous_preview_input = preview_input

    except Exception as e:
        print(f"Erreur lors de la mise à jour du Tally: {e}")
