"""
Services - Couche logique métier
Projet : Gestion de billetterie locale
Auteurs : Ridwan & Sébastien

IMPORTANT : Cette couche contient la logique métier
Elle est séparée de l'accès aux données (DAO) et de l'interface (UI)
"""

from dao import (
    AcheteurDAO, EvenementDAO, TypeBilletDAO, VenteDAO, StatsDAO,
    DatabaseConnection, init_database
)
from datetime import datetime


class BilletterieService:
    """Service principal pour la gestion de la billetterie"""
    
    def __init__(self):
        self.acheteur_dao = AcheteurDAO()
        self.evenement_dao = EvenementDAO()
        self.type_billet_dao = TypeBilletDAO()
        self.vente_dao = VenteDAO()
        self.stats_dao = StatsDAO()
    
    # ============================================
    # Gestion des acheteurs
    # ============================================
    
    def inscrire_acheteur(self, nom: str, prenom: str, email: str, telephone: str = None) -> dict:
        """Inscrit un nouvel acheteur avec validation"""
        # Validation des données
        if not nom or not prenom or not email:
            return {"success": False, "error": "Nom, prénom et email sont obligatoires"}
        
        if "@" not in email:
            return {"success": False, "error": "Email invalide"}
        
        # Vérifier si l'email existe déjà
        existing = self.acheteur_dao.get_by_email(email)
        if existing:
            return {"success": False, "error": "Cet email est déjà utilisé"}
        
        try:
            id_acheteur = self.acheteur_dao.create(nom, prenom, email, telephone)
            return {"success": True, "id_acheteur": id_acheteur, "message": f"Acheteur {prenom} {nom} inscrit avec succès"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def lister_acheteurs(self) -> list:
        """Retourne la liste de tous les acheteurs"""
        acheteurs = self.acheteur_dao.get_all()
        return [dict(a) for a in acheteurs]
    
    # ============================================
    # Gestion des événements
    # ============================================
    
    def creer_evenement(self, nom: str, description: str, date_evenement: str,
                        heure_debut: str, lieu: str, capacite_max: int, categorie: str) -> dict:
        """Crée un nouvel événement avec validation"""
        # Validation
        if not nom or not date_evenement or not lieu:
            return {"success": False, "error": "Nom, date et lieu sont obligatoires"}
        
        if categorie not in ['concert', 'conference', 'spectacle']:
            return {"success": False, "error": "Catégorie invalide (concert, conference, spectacle)"}
        
        if capacite_max <= 0:
            return {"success": False, "error": "La capacité doit être positive"}
        
        try:
            id_evenement = self.evenement_dao.create(
                nom, description, date_evenement, heure_debut, lieu, capacite_max, categorie
            )
            return {"success": True, "id_evenement": id_evenement, "message": f"Événement '{nom}' créé avec succès"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def lister_evenements(self) -> list:
        """Retourne la liste de tous les événements"""
        evenements = self.evenement_dao.get_all()
        return [dict(e) for e in evenements]
    
    def lister_evenements_par_categorie(self, categorie: str) -> list:
        """Filtre les événements par catégorie"""
        evenements = self.evenement_dao.get_by_categorie(categorie)
        return [dict(e) for e in evenements]
    
    # ============================================
    # Gestion des types de billets
    # ============================================
    
    def creer_type_billet(self, id_evenement: int, nom_type: str, prix: float, quantite: int) -> dict:
        """Crée un nouveau type de billet pour un événement"""
        if prix < 0:
            return {"success": False, "error": "Le prix ne peut pas être négatif"}
        
        if quantite <= 0:
            return {"success": False, "error": "La quantité doit être positive"}
        
        # Vérifier que l'événement existe
        evenement = self.evenement_dao.get_by_id(id_evenement)
        if not evenement:
            return {"success": False, "error": "Événement non trouvé"}
        
        try:
            id_type = self.type_billet_dao.create(id_evenement, nom_type, prix, quantite)
            return {"success": True, "id_type_billet": id_type, "message": f"Type de billet '{nom_type}' créé"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def lister_types_billets_evenement(self, id_evenement: int) -> list:
        """Liste les types de billets pour un événement"""
        types = self.type_billet_dao.get_by_evenement(id_evenement)
        return [dict(t) for t in types]
    
    # ============================================
    # Gestion des ventes (POST /vente)
    # ============================================
    
    def effectuer_vente(self, id_acheteur: int, id_type_billet: int, quantite: int) -> dict:
        """Effectue une vente de billets avec vérifications métier"""
        # Vérifier l'acheteur
        acheteur = self.acheteur_dao.get_by_id(id_acheteur)
        if not acheteur:
            return {"success": False, "error": "Acheteur non trouvé"}
        
        # Vérifier le type de billet
        type_billet = self.type_billet_dao.get_by_id(id_type_billet)
        if not type_billet:
            return {"success": False, "error": "Type de billet non trouvé"}
        
        # Vérifier la disponibilité
        if type_billet['quantite_disponible'] < quantite:
            return {
                "success": False, 
                "error": f"Stock insuffisant. Disponible: {type_billet['quantite_disponible']}"
            }
        
        # Calculer le montant total
        montant_total = type_billet['prix'] * quantite
        
        try:
            # Créer la vente
            id_vente = self.vente_dao.create(id_acheteur, id_type_billet, quantite, montant_total)
            
            # Mettre à jour le stock
            nouvelle_quantite = type_billet['quantite_disponible'] - quantite
            self.type_billet_dao.update_quantite(id_type_billet, nouvelle_quantite)
            
            return {
                "success": True,
                "id_vente": id_vente,
                "montant_total": montant_total,
                "message": f"Vente effectuée: {quantite} billet(s) pour {montant_total:.2f}€"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def lister_ventes(self) -> list:
        """Liste toutes les ventes (GET /ventes)"""
        ventes = self.vente_dao.get_all()
        return [dict(v) for v in ventes]
    
    # ============================================
    # Analyses et statistiques
    # ============================================
    
    def calculer_chiffre_affaires_total(self) -> dict:
        """Calcule le CA total (GET /stats/ca)"""
        ca = self.stats_dao.get_chiffre_affaires_total()
        quantite = self.stats_dao.get_quantite_totale_vendue()
        
        return {
            "chiffre_affaires_total": ca,
            "quantite_totale_vendue": quantite,
            "panier_moyen": round(ca / quantite, 2) if quantite > 0 else 0
        }
    
    def calculer_ca_par_evenement(self) -> list:
        """CA détaillé par événement"""
        resultats = self.stats_dao.get_chiffre_affaires_par_evenement()
        return [dict(r) for r in resultats]
    
    def calculer_taux_remplissage(self) -> list:
        """Taux de remplissage par événement"""
        resultats = self.stats_dao.get_taux_remplissage_par_evenement()
        return [dict(r) for r in resultats]
    
    def obtenir_top_billets(self) -> list:
        """Type de billet le plus vendu (GET /stats/top)"""
        resultats = self.stats_dao.get_type_billet_plus_vendu()
        return [dict(r) for r in resultats]
    
    def obtenir_evolution_ventes(self) -> list:
        """Évolution des ventes dans le temps"""
        resultats = self.stats_dao.get_evolution_ventes_par_jour()
        return [dict(r) for r in resultats]
    
    def obtenir_top_acheteurs(self, limit: int = 5) -> list:
        """Top des meilleurs acheteurs"""
        resultats = self.stats_dao.get_top_acheteurs(limit)
        return [dict(r) for r in resultats]
    
    def obtenir_stats_par_categorie(self) -> list:
        """Statistiques par catégorie d'événement"""
        resultats = self.stats_dao.get_ventes_par_categorie()
        return [dict(r) for r in resultats]
    
    # ============================================
    # Indicateur calculé côté Python (bonus)
    # ============================================
    
    def calculer_indicateurs_avances(self) -> dict:
        """Calcule des indicateurs avancés côté Python"""
        ca_total = self.stats_dao.get_chiffre_affaires_total()
        quantite_totale = self.stats_dao.get_quantite_totale_vendue()
        
        ca_par_evenement = self.calculer_ca_par_evenement()
        taux_remplissage = self.calculer_taux_remplissage()
        
        # Calculs Python
        if ca_par_evenement:
            # CA moyen par événement
            ca_moyen = sum(e['chiffre_affaires'] for e in ca_par_evenement) / len(ca_par_evenement)
            
            # Événement le plus rentable
            top_evenement = max(ca_par_evenement, key=lambda x: x['chiffre_affaires'])
            
            # Taux de remplissage moyen
            taux_moyen = sum(t['taux_remplissage'] for t in taux_remplissage) / len(taux_remplissage)
        else:
            ca_moyen = 0
            top_evenement = None
            taux_moyen = 0
        
        return {
            "chiffre_affaires_total": ca_total,
            "quantite_totale": quantite_totale,
            "prix_moyen_billet": round(ca_total / quantite_totale, 2) if quantite_totale > 0 else 0,
            "ca_moyen_par_evenement": round(ca_moyen, 2),
            "taux_remplissage_moyen": round(taux_moyen, 2),
            "evenement_top": top_evenement['evenement'] if top_evenement else "Aucun",
            "date_analyse": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def fermer_connexion(self):
        """Ferme proprement la connexion à la base"""
        db = DatabaseConnection()
        db.close()


# Point d'entrée pour tester les services
if __name__ == "__main__":
    print("Test des services métier")
    print("=" * 50)
    
    service = BilletterieService()
    
    # Test CA
    ca = service.calculer_chiffre_affaires_total()
    print(f"CA Total: {ca}")
    
    service.fermer_connexion()
