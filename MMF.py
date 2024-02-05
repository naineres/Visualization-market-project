import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import time

# Fonction pour calculer le prix
def calculer_prix(prix_initial, prix_actuel, increment, decrement, temps_ecoule, seuil_temps_sans_achat, prix_minimum, prix_maximum):
    if temps_ecoule >= seuil_temps_sans_achat:
        nouveau_prix = max(prix_actuel - decrement, prix_minimum)
    else:
        nouveau_prix = prix_actuel + increment
    return min(nouveau_prix, prix_maximum)

# Fonction pour enregistrer un achat
def enregistrer_achat(prix_initial, increment_prix, prix_minimum, prix_maximum):
    st.session_state['nombre_achats'] += 1
    st.session_state['dernier_achat'] = time.time()
    st.session_state['historique_prix'].append(
        calculer_prix(prix_initial, st.session_state['historique_prix'][-1], increment_prix, 0, 0, float('inf'), prix_minimum, prix_maximum)
    )

# Fonction pour diminuer le prix après une période sans achat
def diminuer_prix(prix_initial, decrement_prix, seuil_temps_sans_achat, prix_minimum, prix_maximum):
    temps_actuel = time.time()
    temps_ecoule = temps_actuel - st.session_state['dernier_achat']
    if temps_ecoule >= seuil_temps_sans_achat:
        st.session_state['historique_prix'].append(
            calculer_prix(prix_initial, st.session_state['historique_prix'][-1], 0, decrement_prix, temps_ecoule, seuil_temps_sans_achat, prix_minimum, prix_maximum)
        )
        st.session_state['dernier_achat'] = temps_actuel

# Initialisation de l'état de session
if 'nombre_achats' not in st.session_state:
    st.session_state['nombre_achats'] = 0
    st.session_state['historique_prix'] = [5]  # Prix initial
    st.session_state['dernier_achat'] = time.time()

if 'changement_prix' not in st.session_state:
    st.session_state['changement_prix'] = pd.DataFrame(columns=['Timestamp', 'Prix'])

# Paramètres de l'application
st.sidebar.header("Paramètres")
prix_initial = st.sidebar.number_input("Prix initial", value=5, min_value=0)
prix_minimum = st.sidebar.number_input("Prix minimum", value=2, min_value=0)
prix_maximum = st.sidebar.number_input("Prix maximum", value=100, min_value=0)
increment_prix = st.sidebar.number_input("Increment du prix", value=0.2, min_value=0.0)
decrement_prix = st.sidebar.number_input("Decrement du prix", value=0.5, min_value=0.0)
seuil_temps_sans_achat = st.sidebar.number_input("Seuil temps sans achat (secondes)", value=10, min_value=0)

# Sélection de catégorie
categorie = st.sidebar.radio("Choisir une catégorie", ("Secret Santa", "Administrateur", "Visualisation des Prix", "Prix Actuel", "Changements de Prix"))

# Container pour le graphique
graphique_container = st.empty()

if categorie == "Administrateur":
    st.header("Interface Administrateur")
    achat_effectue = st.button("Enregistrer Achat")
    if achat_effectue:
        enregistrer_achat(prix_initial, increment_prix, prix_minimum, prix_maximum)

    st.write(f"Prix actuel : {st.session_state['historique_prix'][-1]}")

elif categorie == "Visualisation des Prix":
    st.header("Prix de la boisson !")

    while True:
        diminuer_prix(prix_initial, decrement_prix, seuil_temps_sans_achat, prix_minimum, prix_maximum)
        fig, ax = plt.subplots()
        ax.plot(st.session_state['historique_prix'], marker='o', color='blue')
        ax.set_title('Évolution du Prix de la Boisson', fontsize=14)
        ax.set_xlabel('Nombre de variation', fontsize=12)
        ax.set_ylabel('Prix', fontsize=12)
        ax.grid(True)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        graphique_container.pyplot(fig)
        time.sleep(1)


elif categorie == "Secret Santa":
    st.header("Secret Santa's present")
    st.write("From")
    st.image('RickertGodModeFin.png', caption='Rickert')
    st.write("To ")
    st.image('P.jpg', caption='To P')



elif categorie == "Prix Actuel":
    st.header("Prix de la Prochaine Boisson")
    st.write(f"Le prix de la prochaine boisson est : {st.session_state['historique_prix'][-1]}")

# Catégorie pour afficher les changements de prix et exporter en CSV
elif categorie == "Changements de Prix":
    st.header("Historique des Changements de Prix")
    st.dataframe(st.session_state['changement_prix'])

    # Bouton pour télécharger les données en CSV
    if st.button("Télécharger les Changements de Prix en CSV"):
        csv = st.session_state['changement_prix'].to_csv(index=False)
        st.download_button(label="Télécharger CSV", data=csv, file_name="changements_prix.csv", mime="text/csv")