# src/utils/paths.py
from pathlib import Path

ROOT     = Path(__file__).resolve().parent.parent.parent
RAW_DATA = ROOT / "data" / "raw"
SILVER   = ROOT / "data" / "silver"
GOLD     = ROOT / "data" / "gold"
MODELS   = ROOT / "data" / "models"