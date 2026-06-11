# MAI26-BDE-AIRLINES

📌 Description

Ce projet contient des scripts Python permettant d’ingérer des données brutes (raw data) dans une base de données PostgreSQL.
Les données proviennent de fichiers JSON et sont insérées directement dans des tables SQL après un léger nettoyage.

⚙️ Prérequis
Python 3.10+
PostgreSQL
Les dépendances suivantes :
pip install pandas sqlalchemy psycopg2

🔐 Configuration
Dans src/config/config.py :
DATABASE_URL = "postgresql://user:password@localhost:5432/db_name"

🚀 Scripts d’ingestion
1️⃣ Airlines

📄 src/dataExtraction/extractAirlines.py

Ce script :

charge airlines.json
filtre et nettoie les données
insère les données dans la table airlines

2️⃣ Airports

📄 src/dataExtraction/extractAirports.py

Ce script :

charge airports.json
transforme les données
insère les données dans la table airports