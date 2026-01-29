"""
Configuration du projet Billetterie
Auteurs : Ridwan & Sébastien
"""

import os

# Chemin vers le répertoire du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemin vers la base de données SQLite
DATABASE_PATH = os.path.join(BASE_DIR, "billetterie.db")

# Chemin vers le script SQL de création du schéma
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
