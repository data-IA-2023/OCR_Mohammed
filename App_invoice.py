import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, text
from JsonToBD import exportAll
from ORM import Client, Facture, DetailFacture, connectBd
import os
import pygwalker as pyg
from pygwalker.api.streamlit import init_streamlit_comm, get_streamlit_html
import streamlit.components.v1 as components
import matplotlib.pyplot as plt

from azureOCR import factures_To_Jsons
from invoiceListe import download_invoices_from_json, save_list_factures
from surveillance import inserer_donnees_surveillance, surveillanceAllInOne

# Fonction pour se connecter à la base de données

def get_session():
    engine = connectBd()
    if engine is not None:
        Session = sessionmaker(bind=engine)
        session = Session()
        return {'session' : session, 'engine' : engine }
    else:
        st.error("Erreur lors de la connexion à la base de données.")

# Fonction pour récupérer les ID de facture depuis la base de données
def get_facture_ids(session):
    facture_ids = [facture.QRid for facture in session.query(Facture.QRid).all()]
    return facture_ids

# Fonction pour trouver le nom du fichier image correspondant au QRid
def find_facture_image(qr_id):
    facture_images = [f for f in os.listdir('factures') if f.startswith(qr_id)]
    if facture_images:
        return facture_images[0]
    else:
        return None

# Fonction pour afficher les informations de la facture
def display_invoice_info(session, qr_id):
    facture = session.query(Facture).filter_by(QRid=qr_id).first()
    if facture:
        col1, col2 = st.columns([1, 1] ) #, gap="small"

        with col1:
            st.subheader("Facture")
            st.write(f"INVOICE: {facture.QRid}")
            st.write(f"Issue date: {facture.QRdate.strftime('%Y-%m-%d')}")
            st.write(f"Bill to: {facture.client.client}")
            st.write(f"Adress: {facture.client.adresse}")

            # st.subheader("Détails de la Facture")
            details = session.query(DetailFacture).filter_by(facture_id=qr_id).all()
            df = pd.DataFrame([(detail.label, detail.quantite, detail.prix) for detail in details], 
                            columns=['Label', 'Quantité', 'Prix'])
            st.dataframe(df)

            st.subheader("TOTAL")
            st.write(f"Total : {facture.total_value}")
            st.write(f"Total Calculated: {facture.total_Calculated}")
            st.write(f"Delta: {facture.delta}")

        with col2:
            st.subheader("Image Source")
            facture_image = find_facture_image(qr_id)
            if facture_image:
                st.image(f"factures/{facture_image}", caption='Facture') #, width=1000
            else:
                st.write("Aucune image de facture trouvée.")

    else:
        st.write("Aucune facture trouvée avec ce QRid.")



# Fonction pour afficher le bilan comptable

def display_financial_statement(session):
    # Exécuter la requête SQL pour obtenir les données de la vue
    result = session.execute(text("""
    SELECT 
        facture_QRid,
        facture_QRdate,
        facture_QRclientId,
        client_QRclientCAT,
        client_client,
        client_adresse,
        client_QRclientId,
        detail_facture_label,
        detail_facture_quantite,
        detail_facture_prix,
        facture_total_value,
        facture_total_Calculated,
        facture_delta
    FROM vue_generale
    """))
    
    # Convertir les résultats en DataFrame Pandas
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

    # Afficher le DataFrame complet si rien n'est sélectionné
    if not st.sidebar.checkbox("Filtrer les données"):
        components.html(get_pyg_html(df), width=1400, height=918, scrolling=False)#
        with st.expander("Table detail"):
            st.dataframe(df)
    else:
        # Filtrer les données par année si sélectionnée
        st.sidebar.subheader("Filtrer par année")
        selected_year = st.sidebar.selectbox("Sélectionnez une année :", options=pd.to_datetime(df['facture_QRdate']).dt.year.unique())
        filtered_df = df[pd.to_datetime(df['facture_QRdate']).dt.year == selected_year]
        
        # Filtrer les données par produit avec autocomplétion
        st.sidebar.subheader("Filtrer par produit")
        selected_product = st.sidebar.selectbox("Sélectionnez un produit :", options=df['detail_facture_label'].unique(), index=0)
        filtered_df = filtered_df[filtered_df['detail_facture_label'] == selected_product]

        # Afficher les données filtrées
        st.dataframe(filtered_df)

# You should cache your pygwalker renderer, if you don't want your memory to explode
@st.cache_resource
def get_pyg_html(df: pd.DataFrame) -> str:
    # Lorsque vous devez publier votre application, vous devez définir `debug=False`, pour empêcher les autres utilisateurs d'écrire votre fichier de configuration.
    # Si vous souhaitez utiliser la fonctionnalité d'enregistrement de la configuration des graphiques, définissez `debug=True`
    html = get_streamlit_html(df, use_kernel_calc=True, spec="./gw0.json")#, debug=False
    return html

def Rapport_erreur(session):
    # Exécuter la requête SQL pour obtenir les données de la vue
    result = session.execute(text("""
    SELECT 
        *
    FROM erruernombre;
    """))
    
    # Convertir les résultats en DataFrame Pandas
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    st.subheader("Taux d'erreur :")
    st.dataframe(df)
    
    st.subheader("Monitoring :")
    # Exécuter la requête SQL pour obtenir les données de la vue
    result_monitoring = session.execute(text("""
    SELECT 
        *
    FROM table_surveillance;
    """))
    
    # Convertir les résultats en DataFrame Pandas
    df_monitoring = pd.DataFrame(result_monitoring.fetchall(), columns=result_monitoring.keys())
    st.dataframe(df_monitoring)

def update():
    if st.button('Update'):
        with st.spinner('Wait for it...'):
            save_list_factures()
            download_invoices_from_json('json/factoras.json')
            factures_To_Jsons(input_folder = "factures", output_folder = "json")
            exportAll()
        st.success('Done!')


# Fonction principale de l'application

def newsession():
    # Récupérer la valeur actuelle de la variable d'environnement OCRsession
    current_value = os.getenv("OCRsession")

    if current_value is not None and current_value.isdigit():
        incremented_value = str(int(current_value) + 1)
    else:
        incremented_value = "1"

    try:
        # Définir la variable d'environnement OCRsession avec la nouvelle valeur
        os.environ["OCRsession"] = incremented_value
    except Exception as e:
        print("Une erreur s'est produite lors de la modification de la variable d'environnement :", e)

    return incremented_value

def main():
    
    st.set_page_config(
    page_title="INVOICE OCR",
    layout="wide"
    )
    
    st.sidebar.image('logo.jpg')

        
    BDconnexion= get_session()    
    session = BDconnexion['session']
    # conn = BDconnexion['engine']
    
    newsession() # une nouvelle session pour le monitoring
    
    surveillanceAllInOne("Démarrage de l'application",'No problemo', 200)
    
    if session:
        # Récupérer les IDs de facture depuis la base de données
        facture_ids = get_facture_ids(session)

        # Boutons de la barre latérale pour basculer entre l'affichage des factures et l'affichage du bilan comptable
        mode = st.sidebar.radio("Mode d'affichage :", options=["Factures", "Bilan Comptable", "Rapport D'erreur", "Mise à Jour"])

        if mode == "Factures":
            # Demander à l'utilisateur d'entrer le QRid de la facture avec auto-complétion
            qr_id = st.sidebar.selectbox("Entrez l'ID de la facture :", options=facture_ids)

            if qr_id:
                display_invoice_info(session, qr_id)
        elif mode == "Bilan Comptable" :
            display_financial_statement(session)
        elif mode == "Rapport D'erreur" :
            Rapport_erreur(session)
        elif mode =="Mise à Jour":
            update()
            
        session.close()

# Exécuter l'application
if __name__ == "__main__":
    main()

