import requests


def recup_name_image():

    # URL de l'API
    url = "https://invoiceocrp3.azurewebsites.net/invoices?start_date=2024-01-05"

    # Headers de la requête, spécifiant que nous acceptons une réponse en JSON
    headers = {
        "accept": "application/json",
    }

    # Envoyer la requête GET pour récupérer les métadonnées des images ou leurs URL
    response = requests.get(url, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Extraire les données JSON
        images_data = response.json()
        name_facture = []
        # Imprimer les données pour comprendre leur structure
        print(images_data)
        print(type(images_data))
        for item in images_data["invoices"]:
            print(item["no"])
            name_facture.append(item["no"])
        return name_facture
    # print(name_facture)
    # Continuer le traitement basé sur la structure correcte des données
    else:
        # La requête a échoué
        print(f"Échec de la requête : Code d'état {response.status_code}")


def recup(name_facture):
    return f"https://invoiceocrp3.azurewebsites.net/static/{name_facture}.png"


def test_recup():
    name_image = recup_name_image()

    for name in name_image:
        print(recup(name))




def load_facture(url, name_facture):
    response = requests.get(url)
    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Ouvrir un fichier en mode binaire pour écrire
        with open(f"{name_facture}.png", "wb") as file:
            file.write(response.content)
        print(f"L'image {name_facture}.png a été téléchargée avec succès.")
    else:
        print(
            f"Échec du téléchargement de l'image. Code d'état HTTP : {response.status_code}"
        )


if __name__ == '__main__':
    test = test_recup()
    print(test)