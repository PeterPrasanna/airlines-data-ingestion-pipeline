# ✈️ Airlines Data Ingestion Pipeline

**Python | PostgreSQL | ETL | Data Engineering**

## 📌 Présentation

Ce projet a été réalisé en équipe dans le cadre de ma formation **Data Engineer**.

L'objectif est de développer un pipeline d'ingestion permettant d'extraire, de nettoyer et de charger des données aériennes dans une base de données PostgreSQL.

Les données concernent les compagnies aériennes, les aéroports et les vols.

Le projet repose sur des scripts Python qui traitent des fichiers JSON et CSV avant leur insertion dans une base relationnelle.

## 🛠️ Technologies utilisées

- **Python 3.10+** : extraction et transformation des données
- **PostgreSQL** : stockage des données
- **SQL** : manipulation des données relationnelles
- **JSON / CSV** : formats des données sources
- **Git / GitHub** : versionnement et collaboration

## 🏗️ Architecture du pipeline

```text
Sources de données
    |
    |-- airlines.json
    |-- airports.json
    |-- flights_sample_3M.csv
    |
    v
Scripts Python d'extraction
    |
    v
Nettoyage et transformation
    |
    v
PostgreSQL
    |
    |-- airlines
    |-- airports
    |-- flights
```

## 📂 Organisation du projet

```text
MAI26-BDE-AIRLINES/
│
├── src/
│   ├── config/
│   │   └── config.py
│   │
│   └── dataExtraction/
│       ├── extractAirlines.py
│       ├── extractAirports.py
│       └── extractFlights.py
│
├── requirements.txt
└── README.md
```


## 🚀 Fonctionnalités

### 1. Ingestion des compagnies aériennes

**Script :** `src/dataExtraction/extractAirlines.py`

- Lecture du fichier `airlines.json`
- Filtrage et nettoyage des données
- Insertion dans la table PostgreSQL `airlines`

### 2. Ingestion des aéroports

**Script :** `src/dataExtraction/extractAirports.py`

- Lecture du fichier `airports.json`
- Transformation des données
- Insertion dans la table PostgreSQL `airports`

### 3. Ingestion des vols

**Script :** `src/dataExtraction/extractFlights.py`

- Lecture du fichier `flights_sample_3M.csv`
- Nettoyage et transformation des données
- Chargement dans la table PostgreSQL `flights`

## ⚙️ Installation

### Prérequis

- Python 3.10 ou supérieur
- PostgreSQL
- Git

### Cloner le projet

```bash
git clone https://github.com/PeterPrasanna/airlines-data-ingestion-pipeline.git
cd airlines-data-ingestion-pipeline
```

### Créer un environnement virtuel

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🔐 Configuration PostgreSQL

Le projet utilise une connexion PostgreSQL définie dans :

`src/config/config.py`

Exemple de configuration :

```python
DATABASE_URL = "postgresql://user:password@localhost:5432/db_name"
```

**Sécurité :** ne jamais publier de véritables identifiants de connexion sur GitHub. Il est recommandé de passer par des variables d'environnement.

## 🎯 Compétences mises en pratique

- Développement de scripts d'ingestion Python
- Traitement de fichiers JSON et CSV
- Nettoyage et transformation de données
- Chargement de données dans PostgreSQL
- Manipulation de bases de données relationnelles
- Organisation d'un projet Data Engineering
- Collaboration et versionnement avec Git

## 👥 Contexte du projet

Projet collectif réalisé dans le cadre de la formation Data Engineer.

Ce dépôt présente le travail réalisé en équipe et les compétences techniques mobilisées au cours du projet.