# C'est ici qu'on fait toutes les requêtes SQL vers la base de données

import sqlite3
from config import DATABASE_PATH, SCHEMA_PATH


# --- Connexion à la base de données ---

class DatabaseConnection:
    """
    On utilise un Singleton pour avoir une seule connexion à la base
    Ca évite d'ouvrir plein de connexions en même temps
    """
    _instance = None
    
    def __new__(cls):
        # Si on n'a pas encore créé d'instance, on en crée une
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        return cls._instance
    
    def get_connection(self):
        # On ouvre la connexion si elle n'existe pas encore
        if self.connection is None:
            self.connection = sqlite3.connect(DATABASE_PATH)
            # Ca permet d'accéder aux colonnes par leur nom (plus pratique)
            self.connection.row_factory = sqlite3.Row
            # On active les clés étrangères (sinon SQLite les ignore)
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection
    
    def close(self):
        # On ferme proprement la connexion
        if self.connection:
            self.connection.close()
            self.connection = None


def init_database():
    """Crée les tables en exécutant le fichier schema.sql"""
    db = DatabaseConnection()
    conn = db.get_connection()
    try:
        # On lit le fichier SQL et on l'exécute
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()
        return False


# --- DAO Acheteurs ---

class AcheteurDAO:
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, nom, prenom, email, telephone=None):
        # Ajoute un nouvel acheteur dans la base
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO acheteurs (nom, prenom, email, telephone) VALUES (?, ?, ?, ?)",
            (nom, prenom, email, telephone)
        )
        conn.commit()
        return cursor.lastrowid  # On retourne l'ID du nouvel acheteur
    
    def get_by_id(self, id_acheteur):
        # Cherche un acheteur par son ID
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM acheteurs WHERE id_acheteur = ?", (id_acheteur,))
        return cursor.fetchone()
    
    def get_by_email(self, email):
        # Cherche un acheteur par son email (pour vérifier s'il existe déjà)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM acheteurs WHERE email = ?", (email,))
        return cursor.fetchone()
    
    def get_all(self):
        # Récupère tous les acheteurs, triés par nom
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM acheteurs ORDER BY nom, prenom")
        return cursor.fetchall()


# --- DAO Evenements ---

class EvenementDAO:
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, nom, description, date_evenement, heure_debut, lieu, capacite_max, categorie):
        # Crée un nouvel événement
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO evenements 
               (nom, description, date_evenement, heure_debut, lieu, capacite_max, categorie)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (nom, description, date_evenement, heure_debut, lieu, capacite_max, categorie)
        )
        conn.commit()
        return cursor.lastrowid
    
    def get_by_id(self, id_evenement):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evenements WHERE id_evenement = ?", (id_evenement,))
        return cursor.fetchone()
    
    def get_all(self):
        # Liste tous les événements triés par date
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evenements ORDER BY date_evenement")
        return cursor.fetchall()
    
    def get_by_categorie(self, categorie):
        # Filtre les événements par catégorie (concert, spectacle, etc.)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM evenements WHERE categorie = ? ORDER BY date_evenement",
            (categorie,)
        )
        return cursor.fetchall()


# --- DAO Types de billets ---

class TypeBilletDAO:
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, id_evenement, nom_type, prix, quantite_disponible):
        # Crée un nouveau type de billet pour un événement
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO types_billets (id_evenement, nom_type, prix, quantite_disponible)
               VALUES (?, ?, ?, ?)""",
            (id_evenement, nom_type, prix, quantite_disponible)
        )
        conn.commit()
        return cursor.lastrowid
    
    def get_by_id(self, id_type_billet):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM types_billets WHERE id_type_billet = ?", (id_type_billet,))
        return cursor.fetchone()
    
    def get_by_evenement(self, id_evenement):
        # Récupère tous les types de billets pour un événement donné
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM types_billets WHERE id_evenement = ? ORDER BY prix",
            (id_evenement,)
        )
        return cursor.fetchall()
    
    def update_quantite(self, id_type_billet, nouvelle_quantite):
        # Met à jour le stock de billets après une vente
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE types_billets SET quantite_disponible = ? WHERE id_type_billet = ?",
            (nouvelle_quantite, id_type_billet)
        )
        conn.commit()


# --- DAO Ventes ---

class VenteDAO:
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, id_acheteur, id_type_billet, quantite, montant_total):
        # Enregistre une nouvelle vente
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO ventes (id_acheteur, id_type_billet, quantite, montant_total)
               VALUES (?, ?, ?, ?)""",
            (id_acheteur, id_type_billet, quantite, montant_total)
        )
        conn.commit()
        return cursor.lastrowid
    
    def get_all(self):
        # Récupère toutes les ventes avec les infos liées (jointures)
        # On fait des JOIN pour avoir le nom de l'acheteur, l'événement, etc.
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id_vente, v.date_vente, v.quantite, v.montant_total,
                   a.nom || ' ' || a.prenom AS acheteur, a.email,
                   tb.nom_type AS type_billet, tb.prix AS prix_unitaire,
                   e.nom AS evenement, e.date_evenement, e.categorie
            FROM ventes v
            JOIN acheteurs a ON v.id_acheteur = a.id_acheteur
            JOIN types_billets tb ON v.id_type_billet = tb.id_type_billet
            JOIN evenements e ON tb.id_evenement = e.id_evenement
            ORDER BY v.date_vente DESC
        """)
        return cursor.fetchall()
    
    def get_by_id(self, id_vente):
        # Récupère une vente par son ID (pour la suppression)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.*, tb.prix 
            FROM ventes v
            JOIN types_billets tb ON v.id_type_billet = tb.id_type_billet
            WHERE v.id_vente = ?
        """, (id_vente,))
        return cursor.fetchone()
    
    def delete(self, id_vente):
        # Supprime une vente de la base
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ventes WHERE id_vente = ?", (id_vente,))
        conn.commit()
        return cursor.rowcount > 0  # True si ça a supprimé quelque chose


# --- DAO Stats ---

class StatsDAO:
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def get_chiffre_affaires_total(self):
        # Calcule le CA total avec SUM()
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(montant_total), 0) as ca FROM ventes")
        return cursor.fetchone()['ca']
    
    def get_quantite_totale_vendue(self):
        # Compte le nombre total de billets vendus
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(quantite), 0) as total FROM ventes")
        return cursor.fetchone()['total']
    
    def get_chiffre_affaires_par_evenement(self):
        # CA par événement - on utilise GROUP BY pour regrouper
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id_evenement, e.nom AS evenement, e.date_evenement, e.categorie,
                   COALESCE(SUM(v.montant_total), 0) AS chiffre_affaires,
                   COALESCE(SUM(v.quantite), 0) AS billets_vendus
            FROM evenements e
            LEFT JOIN types_billets tb ON e.id_evenement = tb.id_evenement
            LEFT JOIN ventes v ON tb.id_type_billet = v.id_type_billet
            GROUP BY e.id_evenement
            ORDER BY chiffre_affaires DESC
        """)
        return cursor.fetchall()
    
    def get_taux_remplissage_par_evenement(self):
        # Calcule le % de places vendues pour chaque événement
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.nom AS evenement, e.capacite_max,
                   COALESCE(SUM(v.quantite), 0) AS billets_vendus,
                   ROUND(COALESCE(SUM(v.quantite), 0) * 100.0 / e.capacite_max, 2) AS taux_remplissage
            FROM evenements e
            LEFT JOIN types_billets tb ON e.id_evenement = tb.id_evenement
            LEFT JOIN ventes v ON tb.id_type_billet = v.id_type_billet
            GROUP BY e.id_evenement
            ORDER BY taux_remplissage DESC
        """)
        return cursor.fetchall()
    
    def get_top_billets(self):
        # Classement des types de billets les plus vendus
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tb.nom_type, e.nom AS evenement,
                   SUM(v.quantite) AS total_vendu,
                   SUM(v.montant_total) AS ca_type
            FROM types_billets tb
            JOIN ventes v ON tb.id_type_billet = v.id_type_billet
            JOIN evenements e ON tb.id_evenement = e.id_evenement
            GROUP BY tb.id_type_billet
            ORDER BY total_vendu DESC
        """)
        return cursor.fetchall()
    
    def get_top_acheteurs(self, limit=5):
        # Top des meilleurs clients
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.nom || ' ' || a.prenom AS acheteur,
                   COUNT(v.id_vente) AS nombre_achats,
                   SUM(v.quantite) AS total_billets,
                   SUM(v.montant_total) AS total_depense
            FROM acheteurs a
            JOIN ventes v ON a.id_acheteur = v.id_acheteur
            GROUP BY a.id_acheteur
            ORDER BY total_depense DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    
    def get_ventes_par_categorie(self):
        # Stats par catégorie (concert, spectacle, conférence)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.categorie,
                   COUNT(DISTINCT e.id_evenement) AS nombre_evenements,
                   COALESCE(SUM(v.quantite), 0) AS billets_vendus,
                   COALESCE(SUM(v.montant_total), 0) AS chiffre_affaires
            FROM evenements e
            LEFT JOIN types_billets tb ON e.id_evenement = tb.id_evenement
            LEFT JOIN ventes v ON tb.id_type_billet = v.id_type_billet
            GROUP BY e.categorie
            ORDER BY chiffre_affaires DESC
        """)
        return cursor.fetchall()
