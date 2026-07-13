import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
from time import time

# ─────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────

time_0 = time()

df = pd.read_csv("data/raw/flights_sample_3m.csv", nrows=1000000)

print(f"Données chargées : {df.shape}")

# ─────────────────────────────────────────────
# BRONZE → SILVER
# ─────────────────────────────────────────────

# On enlève les vols annulés
df = df[df["CANCELLED"] == 0]

# On enlève les lignes où on n'a pas le retard d'arrivée
df = df.dropna(subset=["ARR_DELAY"])

# Quelques colonnes ont des valeurs manquantes, on les remplace par 0
df["DEP_DELAY"] = df["DEP_DELAY"].fillna(0)
df["CRS_ELAPSED_TIME"] = df["CRS_ELAPSED_TIME"].fillna(df["CRS_ELAPSED_TIME"].median())

print(f"Après nettoyage : {df.shape}")

# ─────────────────────────────────────────────
# SILVER → GOLD
# ─────────────────────────────────────────────

# Variable cible : 1 si le vol a plus de 10 min de retard, 0 sinon
df["is_delayed"] = (df["ARR_DELAY"] > 10).astype(int)
print(f"Vols en retard : {df['is_delayed'].mean() * 100:.1f}%")

# On extrait des infos depuis la date
df["FL_DATE"] = pd.to_datetime(df["FL_DATE"])
df["day_of_week"] = df["FL_DATE"].dt.dayofweek
df["month"] = df["FL_DATE"].dt.month

# Heure de départ (le format est HHMM, ex: 1430 = 14h30)
df["dep_hour"] = df["CRS_DEP_TIME"] // 100

# Encoding des colonnes texte (compagnie, aéroport départ, aéroport arrivée)
le_carrier = LabelEncoder()
le_origin  = LabelEncoder()
le_dest    = LabelEncoder()

df["AIRLINE_CODE_ENC"] = le_carrier.fit_transform(df["AIRLINE_CODE"].astype(str))
df["ORIGIN_ENC"]       = le_origin.fit_transform(df["ORIGIN"].astype(str))
df["DEST_ENC"]         = le_dest.fit_transform(df["DEST"].astype(str))

# ─────────────────────────────────────────────
# PRÉPARATION DES DONNÉES POUR LE ML
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
    "DISTANCE"
]

X = df[features]
y = df["is_delayed"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Train : {len(X_train)} lignes | Test : {len(X_test)} lignes")

# ─────────────────────────────────────────────
# ENTRAÎNEMENT
# ─────────────────────────────────────────────

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ─────────────────────────────────────────────
# ÉVALUATION
# ─────────────────────────────────────────────

y_pred = model.predict(X_test)

print(f"\nAccuracy : {accuracy_score(y_test, y_pred):.2f}")
print(classification_report(y_test, y_pred, target_names=["À l'heure", "En retard"]))

# ─────────────────────────────────────────────
# SAUVEGARDE DU MODÈLE
# ─────────────────────────────────────────────

joblib.dump(model,      "data/models/delay_predictor.pkl")
joblib.dump(le_carrier, "data/models/encoder_carrier.pkl")
joblib.dump(le_origin,  "data/models/encoder_origin.pkl")
joblib.dump(le_dest,    "data/models/encoder_dest.pkl")

print("Modèle et encoders sauvegardés !")

time_1 = time()

print(f"\nLe pipeline a mis {time_1 - time_0:.2f} secondes à process")


time_1 = time()

print(f"\nLe pipeline a mis {time_1 - time_0:.2f} secondes à process")
