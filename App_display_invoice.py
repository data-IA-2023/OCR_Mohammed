import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from ORM import Client, Facture, DetailFacture, connectBd

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

# Fonction pour afficher les informations de la facture
def display_invoice_info(session, qr_id):
    facture = session.query(Facture).filter_by(QRid=qr_id).first()
    if facture:
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
    else:
        st.write("Aucune facture trouvée avec ce QRid.")

# Fonction principale de l'application
def main():
    # st.title("Affichage des Factures et Détails")
    session = get_session()

    if session:
        # Récupérer les IDs de facture depuis la base de données
        facture_ids = get_facture_ids(session)

        # Demander à l'utilisateur d'entrer le QRid de la facture avec auto-complétion
        qr_id = st.sidebar.selectbox("Entrez l'ID de la facture :", options=facture_ids)

        if qr_id:
            display_invoice_info(session, qr_id)

        session.close()

# Exécuter l'application
if __name__ == "__main__":
    main()
