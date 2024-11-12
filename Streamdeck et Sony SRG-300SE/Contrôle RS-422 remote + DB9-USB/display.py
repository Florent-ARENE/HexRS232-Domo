## display.py
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper

# Fonction pour créer l'image du bouton avec détection de dimensions et texte en gras
def create_button_image(deck, text, color, text_color="white", bold=False):
    # Essayer d'obtenir les dimensions automatiquement
    try:
        width, height = deck.key_image_format()["size"]
    except KeyError:
        print("Avertissement : Dimensions des boutons non détectées. Utilisation des valeurs par défaut 72x72.")
        width, height = 72, 72

    # Création de l'image du bouton
    image = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(image)
    
    # Utiliser une taille de police plus grande pour la visibilité
    font_size = 18
    font_path = "arialbd.ttf" if bold else "arial.ttf"  # Utilise Arial Bold si bold=True
    font = ImageFont.truetype(font_path, font_size)

    # Centrage du texte
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_position = ((width - (text_bbox[2] - text_bbox[0])) // 2,
                     (height - (text_bbox[3] - text_bbox[1])) // 2)
    
    # Dessin du texte en couleur spécifiée
    draw.text(text_position, text, fill=text_color, font=font)
    return PILHelper.to_native_format(deck, image)

# Fonction pour mettre à jour le bouton Save avec texte en noir et en gras
def update_save_button(deck, config_changed):
    color = (255, 165, 0) if config_changed else (144, 238, 144)  # Orange si non sauvegardé, vert clair sinon
    deck.set_key_image(1, create_button_image(deck, "SAVE", color, text_color="black", bold=True))

# Fonction pour mettre à jour le bouton Toggle avec texte en blanc et en gras
def update_toggle_button(deck, mode):
    color = (0, 100, 0) if mode == "STORE" else (139, 0, 0)  # Vert foncé pour STORE, rouge foncé pour RECALL
    deck.set_key_image(0, create_button_image(deck, mode, color, text_color="white", bold=True))
