"""
DAO (Data Access Object) - Couche d'accès aux données
Projet : Gestion de billetterie locale
Auteurs : Ridwan & Sébastien

IMPORTANT : Toutes les requêtes sont paramétrées pour éviter les injections SQL
"""

import sqlite3
from config import DATABASE_PATH, SCHEMA_PATH


class DatabaseConnection:
    """Gestionnaire de connexion à la base de données (Singleton pattern)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        return cls._instance
    
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        if self.connection is None:
            self.connection = sqlite3.connect(DATABASE_PATH)
            self.connection.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
            self.connection.execute("PRAGMA foreign_keys = ON")  # Activer les clés étrangères
        return self.connection
    
    def close(self):
        """Ferme la connexion proprement"""
        if self.connection:
            self.connection.close()
            self.connection = None


def init_database():
    """Initialise la base de données en exécutant le script SQL"""
    db = DatabaseConnection()
    conn = db.get_connection()
    
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()
        print("✓ Base de données initialisée avec succès")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de l'initialisation : {e}")
        conn.rollback()
        return False


# ============================================
# DAO pour les Acheteurs (CRUD)
# ============================================
class AcheteurDAO:
    """Accès aux données pour la table acheteurs"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, nom: str, prenom: str, email: str, telephone: str = None) -> int:
        """Crée un nouvel acheteur - Retourne l'ID créé"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Requête paramétrée (jamais de concaténation de chaînes!)
        query = """
            INSERT INTO acheteurs (nom, prenom, email, telephone)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (nom, prenom, email, telephone))
        conn.commit()  # Ne pas oublier le commit!
        
        return cursor.lastrowid
    
    def get_by_id(self, id_acheteur: int):
        """Récupère un acheteur par son ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM acheteurs WHERE id_acheteur = ?"
        cursor.execute(query, (id_acheteur,))
        
        return cursor.fetchone()
    
    def get_all(self):
        """Récupère tous les acheteurs"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM acheteurs ORDER BY nom, prenom"
        cursor.execute(query)
        
        return cursor.fetchall()
    
    def get_by_email(self, email: str):
        """Récupère un acheteur par son email"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM acheteurs WHERE email = ?"
        cursor.execute(query, (email,))
        
        return cursor.fetchone()


# ============================================
# DAO pour les Événements
# ============================================
class EvenementDAO:
    """Accès aux données pour la table evenements"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, nom: str, description: str, date_evenement: str, 
               heure_debut: str, lieu: str, capacite_max: int, categorie: str) -> int:
        """Crée un nouvel événement"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO evenements (nom, description, date_evenement, heure_debut, lieu, capacite_max, categorie)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (nom, description, date_evenement, heure_debut, lieu, capacite_max, categorie))
        conn.commit()
        
        return cursor.lastrowid
    
    def get_by_id(self, id_evenement: int):
        """Récupère un événement par son ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM evenements WHERE id_evenement = ?"
        cursor.execute(query, (id_evenement,))
        
        return cursor.fetchone()
    
    def get_all(self):
        """Récupère tous les événements"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM evenements ORDER BY date_evenement"
        cursor.execute(query)
        
        return cursor.fetchall()
    
    def get_by_categorie(self, categorie: str):
        """Récupère les événements par catégorie (filtre WHERE)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM evenements WHERE categorie = ? ORDER BY date_evenement"
        cursor.execute(query, (categorie,))
        
        return cursor.fetchall()
    
    def get_upcoming(self):
        """Récupère les événements à venir"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM evenements WHERE date_evenement >= DATE('now') ORDER BY date_evenement"
        cursor.execute(query)
        
        return cursor.fetchall()


# ============================================
# DAO pour les Types de Billets
# ============================================
class TypeBilletDAO:
    """Accès aux données pour la table types_billets"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, id_evenement: int, nom_type: str, prix: float, quantite_disponible: int) -> int:
        """Crée un nouveau type de billet"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO types_billets (id_evenement, nom_type, prix, quantite_disponible)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (id_evenement, nom_type, prix, quantite_disponible))
        conn.commit()
        
        return cursor.lastrowid
    
    def get_by_evenement(self, id_evenement: int):
        """Récupère les types de billets pour un événement"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM types_billets WHERE id_evenement = ? ORDER BY prix"
        cursor.execute(query, (id_evenement,))
        
        return cursor.fetchall()
    
    def get_by_id(self, id_type_billet: int):
        """Récupère un type de billet par son ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM types_billets WHERE id_type_billet = ?"
        cursor.execute(query, (id_type_billet,))
        
        return cursor.fetchone()
    
    def update_quantite(self, id_type_billet: int, nouvelle_quantite: int):
        """Met à jour la quantité disponible"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "UPDATE types_billets SET quantite_disponible = ? WHERE id_type_billet = ?"
        cursor.execute(query, (nouvelle_quantite, id_type_billet))
        conn.commit()


# ============================================
# DAO pour les Ventes
# ============================================
class VenteDAO:
    """Accès aux données pour la table ventes"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, id_acheteur: int, id_type_billet: int, quantite: int, montant_total: float) -> int:
        """Crée une nouvelle vente"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO ventes (id_acheteur, id_type_billet, quantite, montant_total)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (id_acheteur, id_type_billet, quantite, montant_total))
        conn.commit()
        
        return cursor.lastrowid
    
    def get_all(self):
        """Récupère toutes les ventes avec jointures"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Jointure entre ventes, acheteurs, types_billets et evenements
        query = """
            SELECT 
                v.id_vente,
                v.date_vente,
                v.quantite,
                v.montant_total,
                a.nom || ' ' || a.prenom AS acheteur,
                a.email,
                tb.nom_type AS type_billet,
                tb.prix AS prix_unitaire,
                e.nom AS evenement,
                e.date_evenement,
                e.categorie
            FROM ventes v
            JOIN acheteurs a ON v.id_acheteur = a.id_acheteur
            JOIN types_billets tb ON v.id_type_billet = tb.id_type_billet
            JOIN evenements e ON tb.id_evenement = e.id_evenement
            ORDER BY v.date_vente DESC
        """
        cursor.execute(query)
        
        return cursor.fetchall()
    
    def get_by_acheteur(self, id_acheteur: int):
        """Récupère les ventes d'un acheteur"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT v.*, tb.nom_type, e.nom AS evenement
            FROM ventes v
            JOIN types_billets tb ON v.id_type_billet = tb.id_type_billet
            JOIN evenements e ON tb.id_evenement = e.id_evenement
            WHERE v.id_acheteur = ?
            ORDER BY v.date_vente DESC
        """
        cursor.execute(query, (id_acheteur,))
        
        return cursor.fetchall()
    
    def get_by_evenement(self, id_evenement: int):
        """Récupère les ventes pour un événement"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT v.*, a.nom, a.prenom, tb.nom_type
            FROM ventes v
            JOIN acheteurs a ON v.id_acheteur = a.id_acheteur
            JOIN types_billets tb ON v.id_type_billet = tb.id_type_billet
            WHERE tb.id_evenement = ?
            ORDER BY v.date_vente DESC
        """
        cursor.execute(query, (id_evenement,))
        
        return cursor.fetchall()


# ============================================
# DAO pour les Statistiques (requêtes complexes)
# ============================================
class StatsDAO:
    """Accès aux données pour les statistiques et agrégats"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def get_chiffre_affaires_total(self) -> float:
        """Calcule le chiffre d'affaires total (agrégat SUM)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COALESCE(SUM(montant_total), 0) as ca_total FROM ventes"
        cursor.execute(query)
        
        result = cursor.fetchone()
        return result['ca_total'] if result else 0
    
    def get_chiffre_affaires_par_evenement(self):
        """CA par événement avec jointure et GROUP BY"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                e.id_evenement,
                e.nom AS evenement,
                e.date_evenement,
                e.categorie,
                COALESCE(SUM(v.montant_total), 0) AS chiffre_affaires,
                COALESCE(SUM(v.quantite), 0) AS billets_vendus
            FROM evenements e
            LEFT JOIN types_billets tb ON e.id_evenement = tb.id_evenement
            LEFT JOIN ventes v ON tb.id_type_billet = v.id_type_billet
            GROUP BY e.id_evenement, e.nom, e.date_evenement, e.categorie
            ORDER BY chiffre_affaires DESC
        """
        cursor.execute(query)
        
        return cursor.fetchall()
    
    def get_quantite_totale_vendue(self) -> int:
        """Quantité totale de billets vendus"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COALESCE(SUM(quantite), 0) as total FROM ventes"
        cursor.execute(query)
        
        result = cursor.fetchone()
        return result['total'] if result else 0
    
    def get_taux_remplissage_par_evenement(self):
        """Taux de remplissage par événement (requête avancée)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                e.id_evenement,
                e.nom AS evenement,
                e.capacite_max,
                COALESCE(SUM(v.quantite), 0) AS billets_vendus,
                ROUND(COALESCE(SUM(v.quantite), 0) * 100.0 / e.capacite_max, 2) AS taux_remplissage
            FROM evenements e
            LEFT JOIN types_billets tb ON e.id_evenement = tb.id_evenement
            LEFT JOIN ventes v ON tb.id_type_billet = v.id_type_billet
            GROUP BY e.id_evenement, e.nom, e.capacite_max
            ORDER BY taux_remplissage DESC
        """
        cursor.execute(query)
        
        return cursor.fetchall()
    
    def get_type_billet_plus_vendu(self):
        """Type de billet le plus vendu (classement)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                tb.nom_type,
                e.nom AS evenement,
                SUM(v.quantite) AS total_vendu,
                SUM(v.montant_total) AS ca_type
            FROM types_billets tb
            JOIN ventes v ON tb.id_type_billet = v.id_type_billet
            JOIN evenements e ON tb.id_evenement = e.id_evenement
            GROUP BY tb.id_type_billet, tb.nom_type, e.nom
            ORDER BY total_vendu DESC
        """
        cursor.execute(query)
        
        return cursor.fetchall()
    
    def get_evolution_ventes_par_jour(self):
        """Évolution des ventes dans le temps"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                DATE(date_vente) AS jour,
                COUNT(*) AS nombre_ventes,
                SUM(quantite) AS billets_vendus,
                SUM(montant_total) AS ca_jour
            FROM ventes
            GROUP BY DATE(date_vente)
            ORDER BY jour
        """
        cursor.execute(query)
        
        return cursor.fetchall()
    
    def get_top_acheteurs(self, limit: int = 5):
        """Top des acheteurs par montant dépensé"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                a.id_acheteur,
                a.nom || ' ' || a.prenom AS acheteur,
                a.email,
                COUNT(v.id_vente) AS nombre_achats,
                SUM(v.quantite) AS total_billets,
                SUM(v.montant_total) AS total_depense
            FROM acheteurs a
            JOIN ventes v ON a.id_acheteur = v.id_acheteur
            GROUP BY a.id_acheteur, a.nom, a.prenom, a.email
            ORDER BY total_depense DESC
            LIMIT ?
        """
        cursor.execute(query, (limit,))
        
        return cursor.fetchall()
    
    def get_ventes_par_categorie(self):
        """Ventes groupées par catégorie d'événement"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                e.categorie,
                COUNT(DISTINCT e.id_evenement) AS nombre_evenements,
                COALESCE(SUM(v.quantite), 0) AS billets_vendus,
                COALESCE(SUM(v.montant_total), 0) AS chiffre_affaires
            FROM evenements e
            LEFT JOIN types_billets tb ON e.id_evenement = tb.id_evenement
            LEFT JOIN ventes v ON tb.id_type_billet = v.id_type_billet
            GROUP BY e.categorie
            ORDER BY chiffre_affaires DESC
        """
        cursor.execute(query)
        
        return cursor.fetchall()


# Point d'entrée pour tester le DAO
if __name__ == "__main__":
    print("Test du module DAO")
    print("=" * 50)
    
    # Initialiser la base de données
    if init_database():
        print("Base de données prête!")
    else:
        print("Erreur lors de l'initialisation")
