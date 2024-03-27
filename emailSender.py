import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
load_dotenv('.env')

def envoyer_email(destinataire, sujet, corps):
    
    msg = EmailMessage()
    msg['From'] = os.environ['EMAIL']  
    msg['To'] = destinataire
    msg['Subject'] = sujet
    msg.set_content(corps)

    # Connexion au serveur SMTP de Gmail
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        mail=os.environ['EMAIL']
        password=os.environ['EMAILPASS']
        server.login(mail, password)  
        server.send_message(msg)
