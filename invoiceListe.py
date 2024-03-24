import requests
import json
import os


def list_factures(start_date='2019-01-01'):
    url = f"https://invoiceocrp3.azurewebsites.net/invoices?start_date={start_date}"
    headers = {
        "Accept": "application/json"
    }
    invoices = []

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        data = response.json()
        invoices = data.get('invoices', [])

        if invoices:
            lastDate = invoices[-1]['dt']
            flag = False

            while not flag:
                urldata = f"https://invoiceocrp3.azurewebsites.net/invoices?start_date={lastDate}"
                responseData = requests.get(urldata, headers=headers)
                responseData.raise_for_status()

                adddata = responseData.json().get('invoices')
                if adddata:
                    invoices.extend(adddata)
                    lastDate = adddata[-1]['dt']
                    print(lastDate, adddata[-1])
                else:
                    flag = True
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")

    return invoices


def download_invoice(image_name):
    # Vérifier si l'image existe déjà dans le dossier "factures"
    if os.path.exists(f'factures/{image_name}.jpeg'):
        print(f"L'image {image_name}.jpeg existe déjà dans le dossier factures.")
        return

    url = f'https://invoiceocrp3.azurewebsites.net/invoices/{image_name}'
    headers = {'accept': 'image/jpeg'}  

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            
            with open(f'factures/{image_name}.jpeg', 'wb') as file:
                file.write(response.content)
            print(f"L'image {image_name}.jpeg a été téléchargée avec succès.")
        else:
            print(f"La requête a échoué avec le code d'état : {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite lors de la requête : {e}")


def download_invoices_from_json(file):
    with open(file, 'r') as file:
        data = json.load(file)
        for item in data:
            image_name = item['no']
            download_invoice(image_name)




def save_list_factures():
    # chemin_json = os.path.join('json', f"factoras.json")
    chemin_json = os.path("factoras.json")
    factures = list_factures()

    if factures:
        with open(chemin_json, 'w') as fichier:
            json.dump(factures, fichier, indent=2)
    else:
        print("Aucune donnée de facturation disponible.")


if __name__ == '__main__':
    download_invoices_from_json('json/factoras.json')
