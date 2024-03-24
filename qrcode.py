from pyzbar.pyzbar import decode
from PIL import Image
import json

def read_qr_code(image_path):
    try:
        # Ouvrir l'image
        with open(image_path, 'rb') as img_file:
            # Charger l'image
            img = Image.open(img_file)
            # Décoder le QR code
            decoded_objects = decode(img)
            if decoded_objects:
                # Récupérer les données du premier QR code trouvé
                data = decoded_objects[0].data.decode('utf-8')
                # Organiser les données en un dictionnaire
                data_dict = {}
                for line in data.split('\n'):
                    parts = line.split(':')
                    if len(parts) == 2:
                        key, value = parts
                        data_dict[key.strip()] = value.strip()
                    else:
                        print(f"Ignorer la ligne mal formée dans le QR code : {line}")
                return data_dict
            else:
                print("Aucun QR code trouvé dans l'image.")
                return None
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du QR code : {e}")
        return None

if __name__ == '__main__':
    qr_code_data = read_qr_code(r'.\factures\FAC_2024_0266-1739322.jpeg')
    if qr_code_data:
        # Convertir les données en JSON
        qr_code_json = json.dumps(qr_code_data)
        print("Données du QR code en format JSON:", qr_code_json)


