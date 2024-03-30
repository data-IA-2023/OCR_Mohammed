import requests
import json
from dotenv import load_dotenv
import os

load_dotenv('.env')

def DiscordSend(message=''):
    url_webhook = os.environ['DISCORD']

    data = {
        "content": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url_webhook, data=json.dumps(data), headers=headers)
    if response.status_code == 204:
        print("Message envoyé avec succès au webhook.")
    else:
        print(f"Échec de l'envoi du message. Code d'état HTTP : {response.status_code}")


if __name__ == "__main__":
    DiscordSend('Bsahtek le msg')