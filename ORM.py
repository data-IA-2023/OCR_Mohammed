from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, DateTime, ARRAY, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import pyodbc

def connectBd():
    # try:
        load_dotenv('.env')
        SERVER = os.environ['SERVER']
        DATABASE = os.environ['DATABASE']
        USERNAME = os.environ['USERNAME']
        PASSWORD = os.environ['PASSWORD']
        
        # connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
        # connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};' \
        #            f'SERVER={SERVER};DATABASE={DATABASE};' \
        #            f'UID={USERNAME};PWD={PASSWORD};' \
        #            f'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        
        connectionString = (
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'Server=tcp:ocrbd.database.windows.net,1433;'
        'Database=mohammed;'
        'Uid=mohammed;'
        'Pwd=password<à123;'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=30;'
        )
        
        conn = pyodbc.connect(connectionString)
    
    # except Exception  as e:
    #     print(f"Erreur lors de la connexion à la BD: {e}")
    #     return None
    # else:
        return conn
def createsession():
    # Création de la connexion à la base de données
    engine = connectBd()
    Session = sessionmaker(bind=engine)
    session = Session()
    session.autocommit = True
    return session

# Déclaration de la base de modèle SQLAlchemy
Base = declarative_base()

# Définition de la classe Client
class Client(Base):
    __tablename__ = 'client'
    __table_args__ = {'schema': 'dbo'}  # Ajout de cette ligne pour spécifier le schéma
    
    QRclientId = Column(String, primary_key=True)
    QRclientCAT = Column(String)
    client = Column(String)
    adresse = Column(String)
    factures = relationship("Facture", back_populates="client")

# Définition de la classe Facture
class Facture(Base):
    __tablename__ = 'facture'
    __table_args__ = {'schema': 'dbo'}  # Ajout de cette ligne pour spécifier le schéma
    
    QRid = Column(String, primary_key=True)
    QRdate = Column(DateTime)
    QRclientId = Column(String, ForeignKey('dbo.client.QRclientId'))  # Spécification du schéma
    total_value = Column(Float)
    total_Calculated = Column(Float)
    
    # Définir la relation avec le client
    client = relationship("Client", back_populates="factures")

# Définition de la classe DetailFacture
class DetailFacture(Base):
    __tablename__ = 'detail_facture'
    __table_args__ = {'schema': 'dbo'}  # Ajout de cette ligne pour spécifier le schéma
    
    id = Column(Integer, primary_key=True)
    facture_id = Column(String, ForeignKey('dbo.facture.QRid'))  # Spécification du schéma
    label = Column(String)
    quantite = Column(Integer)
    prix = Column(Float)

# Chargement des données JSON
def add_invoice(invoice, session):
    data = invoice
    # Création de l'objet Client
    client = Client(
        QRclientId=data['QRclientId'],
        QRclientCAT=data['QRclientCAT'],
        client=data['client'],
        adresse=data['adresse1'] + ', ' + data['adresse2']
    )

    # Ajout du client à la session
    session.add(client)

    # Création de l'objet Facture
    facture = Facture(
        QRid=data['QRid'],
        QRdate=datetime.strptime(data['QRdate'], '%Y-%m-%d %H:%M:%S'),
        QRclientId=data['QRclientId'],
        total_value=float(data['TotalValue']),
        total_Calculated=float(data['total_Calculated']),
        client=client
    )

    # Ajout de la facture à la session
    session.add(facture)

    # Création et ajout des détails de facture
    for label, qty, prix in zip(data['labels'], data['quantites'], data['prix']):
        detail_facture = DetailFacture(
            facture_id=data['QRid'],
            label=label,
            quantite=int(qty),
            prix=float(prix)
        )
        session.add(detail_facture)

    
    session.commit()

# # Fermeture de la session
# session.close()
