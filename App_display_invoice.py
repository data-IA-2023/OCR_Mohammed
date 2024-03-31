import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from ORM import Client, Facture, DetailFacture, connectBd
import os

# Fonction pour se connecter à la base de données
def get_session():
    engine = connectBd()
    if engine is not None:
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
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

# Fonction principale de l'application
def main():
    # Supprimer les marges à gauche et à droite
    # st.markdown(
    #     """
    #     <style>
    #     .reportview-container .main .block-container {
    #         padding-top: 0rem !important;
    #         padding-right: 0rem !important;
    #         padding-left: 0rem !important;
    #         padding-bottom: 0rem !important;
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True
    # )
    st.set_page_config(layout="wide")
    session = get_session()

    if session:
        # Récupérer les IDs de facture depuis la base de données
        facture_ids = get_facture_ids(session)
        st.sidebar.image('logo.jpg')
        # Demander à l'utilisateur d'entrer le QRid de la facture avec auto-complétion
        qr_id = st.sidebar.selectbox("Entrez l'ID de la facture :", options=facture_ids)

        if qr_id:
            display_invoice_info(session, qr_id)

        session.close()

# Exécuter l'application
if __name__ == "__main__":
    main()
