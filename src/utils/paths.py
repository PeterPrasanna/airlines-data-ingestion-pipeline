from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # racine du projet

DATA_DIR = BASE_DIR / "data"
RAW_DATA = DATA_DIR / "raw"