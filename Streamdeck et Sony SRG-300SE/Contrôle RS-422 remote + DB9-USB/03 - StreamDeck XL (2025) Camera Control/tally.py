## tally.py
from atem import switcher
from display import create_button_image

camera_input_map = {
    1: 1,  
    2: 2,  
    3: 3,  
    4: 4,  
    5: 5,  
    6: 6   
}

input_to_camera_map = {str(v): k for k, v in camera_input_map.items()}

previous_program_input = None
previous_preview_input = None
previous_program_unknown = False
previous_preview_unknown = False

def update_tally(deck):
    global previous_program_input, previous_preview_input, previous_program_unknown, previous_preview_unknown

    try:
        program_input = str(switcher.programInput[0].videoSource)  
        preview_input = str(switcher.previewInput[0].videoSource)  

        program_camera = input_to_camera_map.get(program_input.replace('input', ''), None)
        preview_camera = input_to_camera_map.get(preview_input.replace('input', ''), None)

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

        for button_id, camera_num in zip(range(3, 8), camera_input_map.keys()):
            input_name = f"input{camera_input_map[camera_num]}"
            if program_input == input_name:
                color = (255, 0, 0)  
            elif preview_input == input_name:
                color = (0, 200, 0)
            else:
                color = (0, 0, 0)    

            deck.set_key_image(button_id, create_button_image(deck, f"CAM {camera_num}", color))

        if program_input != previous_program_input or preview_input != previous_preview_input:
            program_message = f"Program : CAM {program_camera if program_camera else 'Unknown'} (rouge) | {program_input if program_camera else 'Source inconnue'}"
            preview_message = f"Preview : CAM {preview_camera if preview_camera else 'Unknown'} (vert) | {preview_input if preview_camera else 'Source inconnue'}"
            print(f"{program_message}\n{preview_message}")

            previous_program_input = program_input
            previous_preview_input = preview_input

    except Exception as e:
        print(f"Erreur lors de la mise à jour du Tally: {e}")
