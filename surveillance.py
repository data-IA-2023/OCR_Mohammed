from datetime import datetime
import pyodbc
from emailSender import envoyer_email
from dotenv import load_dotenv
import os


def connectBd():
    try:
        load_dotenv('.env')
        SERVER = os.environ['SERVER']
        DATABASE = os.environ['DATABASE']
        USERNAME = os.environ['USERNAME']
        PASSWORD = os.environ['PASSWORD']
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
        conn = pyodbc.connect(connectionString)
    
    except Exception  as e:
        print(f"Erreur lors de la connexion à la BD: {e}")
        return None
    else:
        return conn


def inserer_donnees_surveillance(conn, fonction, resultat, erreur):
    try:
        
        if (erreur==400):
            envoyer_email(os.environ['TOEMAIL'], f'⚠️ Erreur in {fonction} ⚠️', f"{datetime.now()} une erreur dans la l'API : {fonction} code erreur : {erreur} .")
        
        cursor = conn.cursor()
        query = "INSERT INTO vocal_weather.dbo.table_surveillance (date_evenement, fonction, resultat, erreur) VALUES (?, ?, ?, ?)"
        data = (datetime.now(), fonction, resultat, erreur)
        cursor.execute(query, data)
        conn.commit()
        print("Données de surveillance insérées avec succès.")
        

    
    except Exception  as e:
        print(f"Erreur lors de l'insertion des données de surveillance: {e}")
        


def surveillanceAllInOne(fonction, resultat, erreur):
    
    try:
    
        load_dotenv('.env')

        SERVER = os.environ['SERVER']
        DATABASE = os.environ['DATABASE']
        USERNAME = os.environ['USERNAME']
        PASSWORD = os.environ['PASSWORD']
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
        conn = pyodbc.connect(connectionString) 

        cursor = conn.cursor()
        query = "INSERT INTO mohammed.dbo.table_surveillance (date_evenement, fonction, resultat, erreur) VALUES (?, ?, ?, ?)"
        data = (datetime.now(), fonction, resultat, erreur)
        cursor.execute(query, data)
        conn.commit()
        print("Données de surveillance insérées avec succès.")

        cursor.close()
        conn.close()
        
    except Exception  as e:
        print(f"Erreur lors de l'insertion des données de surveillance: {e}")