import requests
from bs4 import BeautifulSoup
import os

def telecharger_image(url, dossier_destination):
    # Télécharge une image à partir de l'URL donnée et la sauvegarde dans le dossier spécifié
    try:
        response = requests.get(url)
        if response.status_code == 200:
            if url.lower().endswith('.png'):  # Vérifie si l'URL pointe vers un fichier PNG
                filename = os.path.basename(url)
                if not filename.lower().endswith('.png'):  # Si le nom de fichier ne se termine pas déjà par .png
                    filename += '.png'
            else:
                filename = os.path.basename(url)

            with open(os.path.join(dossier_destination, filename), 'wb') as f:
                f.write(response.content)
                print(f"Image téléchargée avec succès : {url}")
        else:
            print(f"Échec du téléchargement de l'image : {url}")
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement de l'image : {url}")
        print(f"Erreur : {e}")

def telecharger_images_depuis_page(url, dossier_destination):
    # Télécharge toutes les images à partir de la page web donnée
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('img')
            for img in images:
                img_url = img.get('src')
                if img_url.startswith(('http://', 'https://')):
                    telecharger_image(img_url, dossier_destination)
                else:
                    telecharger_image(url + img_url, dossier_destination)
        else:
            print(f"Impossible d'accéder à la page : {url}")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'accès à la page : {url}")
        print(f"Erreur : {e}")

# Exemple d'utilisation :
url_page_web = "https://invoiceocrp3.azurewebsites.net/invoices"  # Mettez l'URL de la page web contenant les images ici
dossier_destination = "images"  # Dossier où vous souhaitez enregistrer les images téléchargées
if not os.path.exists(dossier_destination):
    os.makedirs(dossier_destination)

telecharger_images_depuis_page(url_page_web, dossier_destination)