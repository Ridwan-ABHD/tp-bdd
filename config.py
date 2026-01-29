# config.py - Ridwan & Sébastien
# Ici on met les chemins vers nos fichiers importants

import os

# On récupère le dossier où se trouve ce fichier config.py
# Comme ça peu importe d'où on lance le script, ça marchera toujours
DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))

# Chemin vers la base de données SQLite
DATABASE_PATH = os.path.join(DOSSIER_PROJET, "billetterie.db")

# Chemin vers le fichier SQL qui crée les tables
SCHEMA_PATH = os.path.join(DOSSIER_PROJET, "schema.sql")
