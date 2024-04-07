import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, text
from JsonToBD import exportAll
from ORM import Client, Facture, DetailFacture, connectBd
import os
# import pygwalker as pyg
# from pygwalker.api.streamlit import init_streamlit_comm, get_streamlit_html
import streamlit.components.v1 as components
import matplotlib.pyplot as plt

from azureOCR import factures_To_Jsons
from invoiceListe import download_invoices_from_json, save_list_factures
from surveillance import inserer_donnees_surveillance, surveillanceAllInOne

import plotly.express as px
import plotly.graph_objects as go

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

# def display_financial_statement(session):
#     # Exécuter la requête SQL pour obtenir les données de la vue
#     result = session.execute(text("""
#     SELECT 
#         facture_QRid,
#         facture_QRdate,
#         facture_QRclientId,
#         client_QRclientCAT,
#         client_client,
#         client_adresse,
#         client_QRclientId,
#         detail_facture_label,
#         detail_facture_quantite,
#         detail_facture_prix,
#         facture_total_value,
#         facture_total_Calculated,
#         facture_delta
#     FROM vue_generale
#     """))
    
#     # Convertir les résultats en DataFrame Pandas
#     df = pd.DataFrame(result.fetchall(), columns=result.keys())

#     # Afficher le DataFrame complet si rien n'est sélectionné
#     if not st.sidebar.checkbox("Filtrer les données"):
#         components.html(get_pyg_html(df), width=1400, height=918, scrolling=False)#
#         with st.expander("Table detail"):
#             st.dataframe(df)
#     else:
#         # Filtrer les données par année si sélectionnée
#         st.sidebar.subheader("Filtrer par année")
#         selected_year = st.sidebar.selectbox("Sélectionnez une année :", options=pd.to_datetime(df['facture_QRdate']).dt.year.unique())
#         filtered_df = df[pd.to_datetime(df['facture_QRdate']).dt.year == selected_year]
        
#         # Filtrer les données par produit avec autocomplétion
#         st.sidebar.subheader("Filtrer par produit")
#         selected_product = st.sidebar.selectbox("Sélectionnez un produit :", options=df['detail_facture_label'].unique(), index=0)
#         filtered_df = filtered_df[filtered_df['detail_facture_label'] == selected_product]

#         # Afficher les données filtrées
#         st.dataframe(filtered_df)


def Bilan(session, annees=None, categories_client=None, clients=None, produits=None):
    # Définir la requête SQL de base
    sql_query = """
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
    """
    
    # Construire les clauses WHERE en fonction des filtres fournis
    where_clauses = []
    if annees is not None:
        year_conditions = " OR ".join([f"YEAR(facture_QRdate) = :year_{i}" for i, year in enumerate(annees)])
        where_clauses.append(f"({year_conditions})")
    if categories_client is not None:
        cat_conditions = " OR ".join([f"client_QRclientCAT = :cat_{i}" for i, cat in enumerate(categories_client)])
        where_clauses.append(f"({cat_conditions})")
    if clients is not None:
        client_conditions = " OR ".join([f"client_client = :client_{i}" for i, client in enumerate(clients)])
        where_clauses.append(f"({client_conditions})")
    if produits is not None:
        produit_conditions = " OR ".join([f"detail_facture_label = :produit_{i}" for i, produit in enumerate(produits)])
        where_clauses.append(f"({produit_conditions})")
    
    # Concaténer les clauses WHERE si nécessaire
    if where_clauses:
        sql_query += " WHERE " + " AND ".join(where_clauses)
    
    # Exécuter la requête SQL avec les filtres
    params = {}
    if annees:
        params.update({f"year_{i}": int(year) for i, year in enumerate(annees)})
    if categories_client:
        params.update({f"cat_{i}": cat for i, cat in enumerate(categories_client)})
    if clients:
        params.update({f"client_{i}": client for i, client in enumerate(clients)})
    if produits:
        params.update({f"produit_{i}": produit for i, produit in enumerate(produits)})
        
    result = session.execute(text(sql_query), params)
    
    # Convertir les résultats en DataFrame Pandas
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    
    # Afficher le DataFrame complet si rien n'est sélectionné
    return df

def show_bilan(session):
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
    
    # Sélectionnez les années uniques pour le sélecteur d'année
    years = pd.to_datetime(df['facture_QRdate']).dt.year.unique()
    year_options = [None] + list(years)
    
    # Sélectionnez les catégories de client uniques pour le sélecteur de catégorie de client
    categories_client = df['client_QRclientCAT'].unique()
    client_cat_options = [None] + list(categories_client)
    
    # Sélectionnez les produits uniques pour le sélecteur de produit
    products = df['detail_facture_label'].unique()
    product_options = [None] + list(products)
    
    # Sélectionnez les clients uniques pour le sélecteur de client
    clients = df['client_client'].unique()
    client_options = [None] + list(clients)
    
    st.sidebar.subheader("Filtres :")
    
    # Widgets de sélection pour l'année, la catégorie de client, le client et le produit
    selected_year = st.sidebar.multiselect("Sélectionnez une année :", options=year_options)
    selected_category = st.sidebar.multiselect("Sélectionnez une catégorie de client :", options=client_cat_options)
    selected_client = st.sidebar.multiselect("Sélectionnez un client :", options=client_options)
    selected_product = st.sidebar.multiselect("Sélectionnez un produit :", options=product_options)
    Afficher_erreur= st.sidebar.toggle('Filtres les factures erronées')
  
    # Appliquer les filtres en supprimant les valeurs None
    selected_year = [year for year in selected_year if year is not None]
    selected_category = [cat for cat in selected_category if cat is not None]
    selected_client = [client for client in selected_client if client is not None]
    selected_product = [product for product in selected_product if product is not None]
    # Remplacer les listes vides par None si nécessaire
    selected_year = selected_year if selected_year else None
    selected_category = selected_category if selected_category else None
    selected_client = selected_client if selected_client else None
    selected_product = selected_product if selected_product else None
  
    # Appliquer les filtres
    filtered_df = Bilan(session=session, annees=selected_year, categories_client=selected_category, clients=selected_client, produits=selected_product)
    
    if Afficher_erreur== True:
        filtered_df=filtered_df[abs(filtered_df['facture_delta']) < 0.5]
    
    
    # Afficher le DataFrame filtré
    st.dataframe(filtered_df)
    
    # Calculer le chiffre d'affaires total en regroupant par facture

    chiffre_affaires_facture = filtered_df.groupby('facture_QRid')['facture_total_value'].max().sum()
    
    chiffre_affaires_total=(filtered_df['detail_facture_prix']*filtered_df['detail_facture_quantite']).sum()
    
    # Afficher le chiffre d'affaires total
    st.write(f"Chiffre d'affaires total Calculé : \n{chiffre_affaires_total} Euros")
    # Afficher le chiffre d'affaires total
    st.write(f"Chiffre d'affaires des factures (Total Scanné): \n{chiffre_affaires_facture} Euros")
    # components.html(get_pyg_html(filtered_df), width=1400, height=918, scrolling=False)

    f_df=filtered_df[['facture_QRid', 'client_QRclientCAT', 'facture_total_value']].groupby('facture_QRid').first().reset_index()
    f_df=f_df[['client_QRclientCAT', 'facture_total_value']].groupby('client_QRclientCAT').sum().reset_index()
    
    fig = px.pie(f_df, names='client_QRclientCAT', values='facture_total_value', title='Total par catégorie')
    st.plotly_chart(fig, use_container_width=True)
    st.write(f_df)
    
    f_df_prod = filtered_df[['detail_facture_label', 'facture_total_value']].groupby('detail_facture_label').sum().reset_index()
    
    fig_prod = px.bar(f_df_prod, x='detail_facture_label', y='facture_total_value', title='Chiffre d\'affaires par produit')
    st.plotly_chart(fig_prod, use_container_width=True)
    st.write(f_df_prod)
    
    f_df_client = filtered_df[['facture_QRid','facture_QRclientId', 'client_client', 'facture_total_value']].groupby('facture_QRid').first().reset_index()
    f_df_client=f_df_client[['client_client', 'facture_total_value']].groupby('client_client').sum().reset_index()
    
    fig_client = px.bar(f_df_client, x='client_client', y='facture_total_value', title='Chiffre d\'affaires par client')
    st.plotly_chart(fig_client, use_container_width=True)
    st.write(f_df_client)


# You should cache your pygwalker renderer, if you don't want your memory to explode

def get_pyg_html(df: pd.DataFrame) -> str:
    # Lorsque vous devez publier votre application, vous devez définir `debug=False`, pour empêcher les autres utilisateurs d'écrire votre fichier de configuration.
    # Si vous souhaitez utiliser la fonctionnalité d'enregistrement de la configuration des graphiques, définissez `debug=True`
    html = get_streamlit_html(df, use_kernel_calc=True, spec="./gw0.json")#, debug=False
    return html

def Rapport_erreur(session):
    result = session.execute(text("""
    SELECT 
        *
    FROM erruernombre;
    """))
    
    # Convertir les résultats en DataFrame Pandas
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    st.subheader("Taux d'erreur :")
    st.dataframe(df)
    
    
    # Vos calculs pour obtenir les données nécessaires pour le graphique
    total_factures = df['total_factures'].iloc[0]
    erreur_nombre = df['erreur_nombre'].iloc[0]
    labels = ['Factures Sans Erreur', 'Factures erronées']
    sizes = [total_factures - erreur_nombre, erreur_nombre]
    colors = ['lightskyblue', 'red']
    # Création du graphique
    fig = px.pie(names=labels, values=sizes, title="Taux d'erreur :",  color_discrete_sequence=colors)
    st.write(fig)
        
    
    st.subheader("Erreur dans les prix des produits :")
    result = session.execute(text("""
    SELECT 
        *
    FROM erreurPrix;
    """))
    
    
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    st.dataframe(df)
    
    st.subheader("Nombre de Clients Par Categorie :")
    result = session.execute(text("""
    SELECT 
        *
    FROM NombreClientsParCategorie;
    """))
    
    
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    st.dataframe(df)
    
    

def monitoring(session):
    st.subheader("monitoring :")
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



@st.cache_data()
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
    
    
    # Vérifiez si la fonction de démarrage a déjà été exécutée
    if "fonction_demarrage_executed" not in st.session_state:
        newsession()
        st.session_state.fonction_demarrage_executed = True
        surveillanceAllInOne("Démarrage de l'application","OK", 200)
    
    
    if session:
        # Récupérer les IDs de facture depuis la base de données
        facture_ids = get_facture_ids(session)

        # Boutons de la barre latérale pour basculer entre l'affichage des factures et l'affichage du bilan comptable
        mode = st.sidebar.radio("MENU :", options=["Factures", "Bilan Comptable", "Rapport D'erreur", "Monitoring", "Mise à Jour"])
        try:
            if mode == "Factures":
                # Demander à l'utilisateur d'entrer le QRid de la facture avec auto-complétion
                qr_id = st.sidebar.selectbox("Entrez l'ID de la facture :", options=facture_ids)

                if qr_id:
                    display_invoice_info(session, qr_id)
            elif mode == "Bilan Comptable" :
                show_bilan(session)
            elif mode == "Rapport D'erreur" :
                Rapport_erreur(session)
            elif mode == "Monitoring" :
                monitoring(session)
            elif mode =="Mise à Jour":
                update()
        except Exception as e:
             print(f"Une erreur s'est produite dans la fonction {mode} :", type(e).__name__)
             surveillanceAllInOne(mode,str(type(e).__name__), 400)
        session.close()
        
# Exécuter l'application
if __name__ == "__main__":
    main()

