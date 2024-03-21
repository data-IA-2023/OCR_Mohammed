import pytesseract
from PIL import Image

# Chemin vers l'image à traiter
image_path = 'C:\partage\code\OCR_Mohammed\exemple.png'

# Charger l'image
image = Image.open(image_path)

# Reconnaissance de caractères
texte = pytesseract.image_to_string(image)

# Afficher le texte extrait
print(texte)
