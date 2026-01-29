# DAO (Data Access Object) - Accès aux données
# Auteurs : Ridwan & Sébastien
# Toutes les requêtes sont paramétrées pour éviter les injections SQL

import sqlite3
from config import DATABASE_PATH, SCHEMA_PATH


class DatabaseConnection:
    """Connexion unique à la base (Singleton)"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        return cls._instance
    
    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(DATABASE_PATH)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None


def init_database():
    """Initialise la base avec le schéma SQL"""
    db = DatabaseConnection()
    conn = db.get_connection()
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()
        return False


class AcheteurDAO:
    """CRUD pour les acheteurs"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, nom, prenom, email, telephone=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO acheteurs (nom, prenom, email, telephone) VALUES (?, ?, ?, ?)",
            (nom, prenom, email, telephone)
        )
        conn.commit()
        return cursor.lastrowid
    
    def get_by_id(self, id_acheteur):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM acheteurs WHERE id_acheteur = ?", (id_acheteur,))
        return cursor.fetchone()
    
    def get_by_email(self, email):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM acheteurs WHERE email = ?", (email,))
        return cursor.fetchone()
    
    def get_all(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM acheteurs ORDER BY nom, prenom")
        return cursor.fetchall()


class EvenementDAO:
    """CRUD pour les événements"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, nom, description, date_evenement, heure_debut, lieu, capacite_max, categorie):
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
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evenements ORDER BY date_evenement")
        return cursor.fetchall()
    
    def get_by_categorie(self, categorie):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM evenements WHERE categorie = ? ORDER BY date_evenement",
            (categorie,)
        )
        return cursor.fetchall()


class TypeBilletDAO:
    """CRUD pour les types de billets"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, id_evenement, nom_type, prix, quantite_disponible):
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
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM types_billets WHERE id_evenement = ? ORDER BY prix",
            (id_evenement,)
        )
        return cursor.fetchall()
    
    def update_quantite(self, id_type_billet, nouvelle_quantite):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE types_billets SET quantite_disponible = ? WHERE id_type_billet = ?",
            (nouvelle_quantite, id_type_billet)
        )
        conn.commit()


class VenteDAO:
    """CRUD pour les ventes"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, id_acheteur, id_type_billet, quantite, montant_total):
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
        """Récupère les ventes avec jointures"""
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


class StatsDAO:
    """Requêtes statistiques avec agrégats"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def get_chiffre_affaires_total(self):
        """SUM du chiffre d'affaires"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(montant_total), 0) as ca FROM ventes")
        return cursor.fetchone()['ca']
    
    def get_quantite_totale_vendue(self):
        """SUM des billets vendus"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(quantite), 0) as total FROM ventes")
        return cursor.fetchone()['total']
    
    def get_chiffre_affaires_par_evenement(self):
        """CA par événement avec GROUP BY"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id_evenement, e.nom AS evenement, e.categorie,
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
        """Taux de remplissage avec calcul"""
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
        """Types de billets les plus vendus"""
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
        """Top acheteurs par montant dépensé"""
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
        """Ventes par catégorie d'événement"""
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
