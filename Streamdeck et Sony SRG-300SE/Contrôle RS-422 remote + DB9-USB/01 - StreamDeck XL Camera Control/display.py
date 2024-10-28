
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper

def create_button_image(deck, text, color):
    image = Image.new("RGB", (48, 48), color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_position = ((image.width - (text_bbox[2] - text_bbox[0])) // 2,
                     (image.height - (text_bbox[3] - text_bbox[1])) // 2)
    draw.text(text_position, text, fill="white", font=font)
    return PILHelper.to_native_format(deck, image)

# Fonction globale pour mettre à jour l'état du bouton SAVE
def update_save_button(deck, config_changed):
    color = "orange" if config_changed else "green"
    deck.set_key_image(16, create_button_image(deck, "Save", color))
