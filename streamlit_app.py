import streamlit as st
import pandas as pd
import joblib

# Infos projet
st.title("LIORA AIRLINES")
st.write("Prédiction des retards de vols")
st.write("Equipe : Julie Françoise, Prasanna Peter Alocias, Théo Voyer")

st.write("---")

# Chargement du modele et des encoders 
model = joblib.load("data/models/delay_predictor.pkl")
encoder_carrier = joblib.load("data/models/encoder_carrier.pkl")
encoder_origin = joblib.load("data/models/encoder_origin.pkl")
encoder_dest = joblib.load("data/models/encoder_dest.pkl")

# Formulaire
st.subheader("Informations du vol")

carrier = st.selectbox("Compagnie", list(encoder_carrier.classes_))
origin = st.selectbox("Aeroport de depart", list(encoder_origin.classes_))
dest = st.selectbox("Aeroport d'arrivée", list(encoder_dest.classes_))

fl_date = st.date_input("Date du vol")
dep_hour = st.slider("Heure de depart", 0, 23, 8)
dep_delay = st.number_input("Retard au depart (min)", value=0)
elapsed = st.number_input("Duree prevue du vol (min)", value=180)
distance = st.number_input("Distance (miles)", value=800)

# Bouton et prediction
if st.button("Run"):

    # On encode les colonnes texte
    carrier_enc = encoder_carrier.transform([carrier])[0]
    origin_enc = encoder_origin.transform([origin])[0]
    dest_enc = encoder_dest.transform([dest])[0]

    # On cree la ligne dans le meme ordre que l'entrainement
    donnees = pd.DataFrame([{
        "AIRLINE_CODE_ENC": carrier_enc,
        "ORIGIN_ENC": origin_enc,
        "DEST_ENC": dest_enc,
        "day_of_week": fl_date.weekday(),
        "month": fl_date.month,
        "dep_hour": dep_hour,
        "DEP_DELAY": dep_delay,
        "CRS_ELAPSED_TIME": elapsed,
        "DISTANCE": distance
    }])

    # Prediction
    prediction = model.predict(donnees)[0]
    proba = model.predict_proba(donnees)[0]

    st.write("---")
    st.subheader("Résultat")

    if prediction == 1:
        st.error("Le vol risque d'etre en retard")
    else:
        st.success("Le vol devrait etre à l'heure")

    st.write("Probabilite de retard :", round(proba[1] * 100, 1), "%")