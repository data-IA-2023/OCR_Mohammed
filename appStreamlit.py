import streamlit as st
import os
from PIL import Image
import pyodbc
from dotenv import load_dotenv
import os
# Fonction pour se connecter à la base de données SQL Server
def connect_to_database():
    load_dotenv('.env')
    SERVER = os.environ['SERVER']
    DATABASE = os.environ['DATABASE']
    USERNAME = os.environ['USERNAME']
    PASSWORD = os.environ['PASSWORD']
    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}')
    cursor = conn.cursor()
    return conn, cursor

# Fonction pour rechercher et afficher l'image de la facture à partir du dossier
def display_image(folder_path, image_name):
    image_path = os.path.join(folder_path, image_name)
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, caption='Facture', use_column_width=True)
    else:
        st.write("L'image de la facture n'a pas été trouvée.")

# Fonction pour récupérer les informations de la facture à partir de la base de données
def get_facture_info(facture_id, cursor):
    query = f"SELECT * FROM Facture WHERE FactureID = {facture_id}"
    cursor.execute(query)
    facture_info = cursor.fetchone()
    return facture_info

# Fonction pour afficher le contenu de l'onglet "Recherche par image"
def image_search():
    st.subheader("Recherche par image")

    # Sélectionner une image depuis le dossier
    uploaded_file = st.file_uploader("Téléchargez une image de facture :", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        st.image(uploaded_file, caption='Image de la facture téléchargée', use_column_width=True)

# Fonction pour afficher le contenu de l'onglet "Recherche par ID de facture"
def id_search():
    st.subheader("Recherche par ID de facture")

    # Entrée pour saisir l'ID de la facture
    facture_id = st.number_input("Entrez l'ID de la facture :")

    # Connexion à la base de données
    conn, cursor = connect_to_database()

    if st.button("Afficher la facture"):
        # Récupérer les informations de la facture depuis la base de données
        facture_info = get_facture_info(facture_id, cursor)
        if facture_info:
            st.write(f"ID de la facture : {facture_info[0]}")
            st.write(f"Montant : {facture_info[1]}")
            st.write(f"Date : {facture_info[2]}")
            st.write(f"ID du client : {facture_info[3]}")
        else:
            st.write("Aucune facture trouvée pour cet ID.")

# Fonction principale de l'application
def main():
    st.title("Application de gestion de factures")

    # Création des onglets dans le menu latéral
    menu_selection = st.sidebar.selectbox("Sélectionnez une option :", ["Recherche par image", "Recherche par ID de facture"])

    # Afficher le contenu de l'onglet sélectionné
    if menu_selection == "Recherche par image":
        image_search()
    elif menu_selection == "Recherche par ID de facture":
        id_search()

    st.write("Merci d'utiliser notre application.")

if __name__ == "__main__":
    main()

