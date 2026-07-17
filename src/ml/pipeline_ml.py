import os
from time import time

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

RAW_DATA_PATH = "data/raw/flights_sample_3m.csv"

SILVER_DATA_PATH = "data/silver/flights_silver.csv"
GOLD_DATA_PATH = "data/gold/flights_gold.csv"

MODEL_PATH = "data/models/delay_predictor.pkl"
CARRIER_ENCODER_PATH = "data/models/encoder_carrier.pkl"
ORIGIN_ENCODER_PATH = "data/models/encoder_origin.pkl"
DEST_ENCODER_PATH = "data/models/encoder_dest.pkl"


# ─────────────────────────────────────────────
# DÉMARRAGE DU PIPELINE
# ─────────────────────────────────────────────

time_0 = time()


# ─────────────────────────────────────────────
# CRÉATION DES DOSSIERS
# ─────────────────────────────────────────────

os.makedirs(
    "data/silver",
    exist_ok=True,
)

os.makedirs(
    "data/gold",
    exist_ok=True,
)

os.makedirs(
    "data/models",
    exist_ok=True,
)


# ─────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────

print(
    "Chargement des données..."
)

df = pd.read_csv(
    RAW_DATA_PATH,
    nrows=1_000_000,
)

print(
    f"Données chargées : {df.shape}"
)


# ─────────────────────────────────────────────
# BRONZE → SILVER
# ─────────────────────────────────────────────

print(
    "\nNettoyage des données..."
)


# On garde uniquement les vols non annulés
df = df[
    df["CANCELLED"] == 0
].copy()


# On supprime les lignes sans retard d'arrivée
df = df.dropna(
    subset=[
        "ARR_DELAY",
    ]
)


# Retard au départ manquant → 0
df["DEP_DELAY"] = (
    df["DEP_DELAY"]
    .fillna(0)
)


# Durée prévue manquante → médiane
elapsed_time_median = (
    df["CRS_ELAPSED_TIME"]
    .median()
)

df["CRS_ELAPSED_TIME"] = (
    df["CRS_ELAPSED_TIME"]
    .fillna(
        elapsed_time_median
    )
)


# On supprime les lignes où certaines
# variables essentielles sont manquantes
df = df.dropna(
    subset=[
        "AIRLINE_CODE",
        "ORIGIN",
        "DEST",
        "FL_DATE",
        "CRS_DEP_TIME",
        "DISTANCE",
    ]
)


print(
    f"Après nettoyage : {df.shape}"
)


# Sauvegarde Silver
df.to_csv(
    SILVER_DATA_PATH,
    index=False,
)

print(
    f"Silver sauvegardé : {SILVER_DATA_PATH}"
)


# ─────────────────────────────────────────────
# SILVER → GOLD
# ─────────────────────────────────────────────

print(
    "\nCréation des features..."
)


# Variable cible :
# 1 = retard supérieur à 10 minutes
# 0 = à l'heure
df["is_delayed"] = (
    df["ARR_DELAY"] > 10
).astype(int)


delay_rate = (
    df["is_delayed"]
    .mean()
    * 100
)

print(
    f"Vols en retard : {delay_rate:.1f}%"
)


# Conversion de la date
df["FL_DATE"] = pd.to_datetime(
    df["FL_DATE"]
)


# Jour de la semaine
# lundi = 0
# dimanche = 6
df["day_of_week"] = (
    df["FL_DATE"]
    .dt
    .dayofweek
)


# Mois
df["month"] = (
    df["FL_DATE"]
    .dt
    .month
)


# Heure de départ
# Exemple :
# 1430 → 14
df["dep_hour"] = (
    df["CRS_DEP_TIME"]
    // 100
).astype(int)


# Correction éventuelle du format 2400
df.loc[
    df["dep_hour"] == 24,
    "dep_hour",
] = 0


# ─────────────────────────────────────────────
# ENCODAGE DES VARIABLES CATÉGORIELLES
# ─────────────────────────────────────────────

print(
    "\nEncodage des catégories..."
)


encoder_carrier = OrdinalEncoder(
    handle_unknown="use_encoded_value",
    unknown_value=-1,
)


encoder_origin = OrdinalEncoder(
    handle_unknown="use_encoded_value",
    unknown_value=-1,
)


encoder_dest = OrdinalEncoder(
    handle_unknown="use_encoded_value",
    unknown_value=-1,
)


# Important :
# OrdinalEncoder attend une entrée 2D
df["AIRLINE_CODE_ENC"] = (
    encoder_carrier
    .fit_transform(
        df[
            [
                "AIRLINE_CODE",
            ]
        ].astype(str)
    )
    .ravel()
    .astype(int)
)


df["ORIGIN_ENC"] = (
    encoder_origin
    .fit_transform(
        df[
            [
                "ORIGIN",
            ]
        ].astype(str)
    )
    .ravel()
    .astype(int)
)


df["DEST_ENC"] = (
    encoder_dest
    .fit_transform(
        df[
            [
                "DEST",
            ]
        ].astype(str)
    )
    .ravel()
    .astype(int)
)


print(
    "Encodage terminé."
)


# ─────────────────────────────────────────────
# SAUVEGARDE GOLD
# ─────────────────────────────────────────────

df.to_csv(
    GOLD_DATA_PATH,
    index=False,
)

print(
    f"Gold sauvegardé : {GOLD_DATA_PATH}"
)


# ─────────────────────────────────────────────
# PRÉPARATION DES DONNÉES ML
# ─────────────────────────────────────────────

features = [
    "AIRLINE_CODE_ENC",
    "ORIGIN_ENC",
    "DEST_ENC",
    "day_of_week",
    "month",
    "dep_hour",
    "DEP_DELAY",
    "CRS_ELAPSED_TIME",
    "DISTANCE",
]


X = df[
    features
]

y = df[
    "is_delayed"
]


# ─────────────────────────────────────────────
# TRAIN / TEST SPLIT
# ─────────────────────────────────────────────

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
)


print(
    f"\nTrain : {len(X_train)} lignes"
)

print(
    f"Test : {len(X_test)} lignes"
)


# ─────────────────────────────────────────────
# ENTRAÎNEMENT
# ─────────────────────────────────────────────

print(
    "\nEntraînement du modèle..."
)


model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
)


model.fit(
    X_train,
    y_train,
)


print(
    "Entraînement terminé."
)


# ─────────────────────────────────────────────
# ÉVALUATION
# ─────────────────────────────────────────────

print(
    "\nÉvaluation du modèle..."
)


y_pred = model.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    y_pred,
)


print(
    f"\nAccuracy : {accuracy:.4f}"
)


print(
    "\nRapport de classification :"
)


print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "À l'heure",
            "En retard",
        ],
    )
)


# ─────────────────────────────────────────────
# SAUVEGARDE DU MODÈLE
# ─────────────────────────────────────────────

print(
    "\nSauvegarde du modèle et des encodeurs..."
)


joblib.dump(
    model,
    MODEL_PATH,
)


joblib.dump(
    encoder_carrier,
    CARRIER_ENCODER_PATH,
)


joblib.dump(
    encoder_origin,
    ORIGIN_ENCODER_PATH,
)


joblib.dump(
    encoder_dest,
    DEST_ENCODER_PATH,
)


print(
    "Modèle et encodeurs sauvegardés."
)


# ─────────────────────────────────────────────
# TEST D'UNE VALEUR INCONNUE
# ─────────────────────────────────────────────

test_unknown_airport = (
    encoder_origin
    .transform(
        [
            [
                "CDG",
            ]
        ]
    )[0][0]
)


print(
    "\nTest aéroport inconnu :"
)

print(
    f"CDG encodé en : {test_unknown_airport}"
)


# ─────────────────────────────────────────────
# FIN DU PIPELINE
# ─────────────────────────────────────────────

time_1 = time()


print(
    f"\nLe pipeline a mis "
    f"{time_1 - time_0:.2f} secondes."
)