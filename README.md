# MAI26-BDE-AIRLINES

## 📌 Description

Ce projet contient des scripts Python permettant d’ingérer des données brutes (raw data) sur des **vols de différentes compagnies aériennes** dans une base de données PostgreSQL.

Les données proviennent de fichiers JSON et sont insérées directement dans des tables SQL après un léger nettoyage.


## ⚙️ Prérequis

Il est nécessaire d'avoir accès à Python (version 3.10+) et PostgreSQL.

Pour éviter des conflits de versions, créer un environnement virtuel `.venv` après avoir cloner le projet. Installer ensuite les dépendances nécessaires. 

Celles-ci peuvent être importer du fichier `requirements.txt`:

- Sur **Linux**
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

- sur **Windows**
```
python3 -m venv .venv
. .venv\Scripts\activate
pip install -r requirements.txt
```


## 🔐 Configuration

Dans l'objectif de confirguer la base, on pourra trouver les informations nécessaires dans le fichier `src/config/config.py` :

```
DATABASE_URL = "postgresql://user:password@localhost:5432/db_name"
```

## 🚀 Scripts d’ingestion

### 1️⃣ Airlines

> 📄 src/dataExtraction/extractAirlines.py

Ce script permet de :
- charger airlines.json
- filtrer et nettoyer les données
- insérer les données dans la table `airlines`

### 2️⃣ Airports

> 📄 src/dataExtraction/extractAirports.py

Ce script permet de :
- charger airports.json
- transformer les données
- insérer les données dans la table `airports`