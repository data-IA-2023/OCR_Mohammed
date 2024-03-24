from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import json
import os
import time
from qrcode import read_qr_code

def ocr_image(image_path_or_url):
    """
    Performs OCR on an image, whether it's a local image or a remote image, and returns the result as a dictionary.

    Parameters:
        - image_path_or_url (str): The path to the local image or the URL of the remote image.
        - subscription_key (str): The subscription key for the Azure Cognitive Services Computer Vision service.
        - endpoint (str): The endpoint URL for the Azure Cognitive Services Computer Vision service.

    Returns:
        - dict: A dictionary containing the OCR results.
    """
    subscription_key = os.environ["VISION_KEY"]
    endpoint = os.environ["VISION_ENDPOINT"]
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

    if os.path.exists(image_path_or_url):
        image = open(image_path_or_url, "rb")
        read_response = computervision_client.read_in_stream(image, raw=True, model_version="2022-04-30")
    else:
        read_response = computervision_client.read(image_path_or_url, raw=True, model_version="2022-04-30")

    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    ocr_results = []

    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                ocr_results.append({"text": line.text, "bounding_box": line.bounding_box})
    
    return ocr_results



def ocr_facture(image_path):
    # Local image example
    
    
    # Perform QR code reading and OCR
    qrcode_results = read_qr_code(image_path)
    ocr_results = ocr_image(image_path)
    
    # Combine QR code and OCR results
    combined_results = []
    combined_results.append(qrcode_results)
    combined_results.extend(ocr_results)
    return combined_results


import os
import json

def factures_To_Jsons(input_folder, output_folder):

    # Parcourir tous les fichiers dans le dossier d'entrée
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpeg") or filename.endswith(".jpg"):
            # Chemin complet de l'image
            image_path = os.path.join(input_folder, filename)
            

            
            # Chemin de sortie pour le fichier JSON
            json_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".json")
            
            if not os.path.exists(json_path):
                # Appeler la fonction ocr_facture pour obtenir les résultats OCR
                combined_results = ocr_facture(image_path)
                # Écrire les résultats dans le fichier JSON avec indentation pour la lisibilité
                with open(json_path, "w") as outfile:
                    json.dump(combined_results, outfile, indent=4)
                    print (f"l'ocr de la facture: {filename} est bien enregistré")
            else:
                print (f"l'ocr de la facture: {filename} existe déja")

# Exemple d'utilisation
if __name__ == "__main__":
    input_folder = "factures"  # Dossier contenant les images de facture
    output_folder = "json"      # Dossier où les résultats OCR seront sauvegardés
    
    factures_To_Jsons(input_folder, output_folder)
