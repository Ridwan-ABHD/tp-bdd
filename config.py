# Configuration du projet Billetterie
# Auteurs : Ridwan & Sébastien

import os

# Chemins du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "billetterie.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
