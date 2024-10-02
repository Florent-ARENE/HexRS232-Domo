# tally.py
from atem import switcher
from display import create_button_image

camera_input_map = {
    1: "input1",
    2: "input2",
    3: "input3",
    4: "input8"
}

def update_tally(deck):
    try:
        program_input = str(switcher.programInput[0].videoSource)
        preview_input = str(switcher.previewInput[0].videoSource)

        print(f"Program Input exact: {program_input}")
        print(f"Preview Input exact: {preview_input}")

        for button_id, input_id in zip([7, 15, 23, 31], camera_input_map.values()):
            if program_input == input_id:
                color = (255, 0, 0)
                print(f"Bouton {button_id} en Program (rouge)")
            elif preview_input == input_id:
                color = (0, 255, 0)
                print(f"Bouton {button_id} en Preview (vert)")
            else:
                color = (0, 0, 0)
                print(f"Bouton {button_id} inactif (noir)")

            deck.set_key_image(button_id, create_button_image(deck, f"Cam {button_id // 8 + 1}", color))

    except Exception as e:
        print(f"Erreur lors de la mise à jour du Tally: {e}")
