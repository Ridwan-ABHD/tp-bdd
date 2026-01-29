# Services - Logique métier
# Auteurs : Ridwan & Sébastien

from dao import (AcheteurDAO, EvenementDAO, TypeBilletDAO, VenteDAO, 
                 StatsDAO, DatabaseConnection, init_database)
from datetime import datetime


class BilletterieService:
    """Service principal de gestion de la billetterie"""
    
    def __init__(self):
        self.acheteur_dao = AcheteurDAO()
        self.evenement_dao = EvenementDAO()
        self.type_billet_dao = TypeBilletDAO()
        self.vente_dao = VenteDAO()
        self.stats_dao = StatsDAO()
    
    # --- Acheteurs ---
    
    def inscrire_acheteur(self, nom, prenom, email, telephone=None):
        """Inscrit un acheteur avec validation"""
        if not nom or not prenom or not email:
            return {"success": False, "error": "Nom, prénom et email obligatoires"}
        if "@" not in email:
            return {"success": False, "error": "Email invalide"}
        if self.acheteur_dao.get_by_email(email):
            return {"success": False, "error": "Email déjà utilisé"}
        
        try:
            id_acheteur = self.acheteur_dao.create(nom, prenom, email, telephone)
            return {"success": True, "id_acheteur": id_acheteur}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def lister_acheteurs(self):
        return [dict(a) for a in self.acheteur_dao.get_all()]
    
    # --- Événements ---
    
    def creer_evenement(self, nom, description, date_evenement, heure_debut, 
                        lieu, capacite_max, categorie):
        """Crée un événement avec validation"""
        if not nom or not date_evenement or not lieu:
            return {"success": False, "error": "Nom, date et lieu obligatoires"}
        if categorie not in ['concert', 'conference', 'spectacle']:
            return {"success": False, "error": "Catégorie invalide"}
        if capacite_max <= 0:
            return {"success": False, "error": "Capacité doit être positive"}
        
        try:
            id_evt = self.evenement_dao.create(
                nom, description, date_evenement, heure_debut, lieu, capacite_max, categorie
            )
            return {"success": True, "id_evenement": id_evt}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def lister_evenements(self):
        return [dict(e) for e in self.evenement_dao.get_all()]
    
    def lister_evenements_par_categorie(self, categorie):
        return [dict(e) for e in self.evenement_dao.get_by_categorie(categorie)]
    
    # --- Types de billets ---
    
    def creer_type_billet(self, id_evenement, nom_type, prix, quantite):
        """Crée un type de billet"""
        if prix < 0:
            return {"success": False, "error": "Prix négatif interdit"}
        if quantite <= 0:
            return {"success": False, "error": "Quantité doit être positive"}
        if not self.evenement_dao.get_by_id(id_evenement):
            return {"success": False, "error": "Événement introuvable"}
        
        try:
            id_type = self.type_billet_dao.create(id_evenement, nom_type, prix, quantite)
            return {"success": True, "id_type_billet": id_type}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def lister_types_billets_evenement(self, id_evenement):
        return [dict(t) for t in self.type_billet_dao.get_by_evenement(id_evenement)]
    
    # --- Ventes ---
    
    def effectuer_vente(self, id_acheteur, id_type_billet, quantite):
        """Effectue une vente avec vérifications"""
        acheteur = self.acheteur_dao.get_by_id(id_acheteur)
        if not acheteur:
            return {"success": False, "error": "Acheteur introuvable"}
        
        type_billet = self.type_billet_dao.get_by_id(id_type_billet)
        if not type_billet:
            return {"success": False, "error": "Type de billet introuvable"}
        
        if type_billet['quantite_disponible'] < quantite:
            return {"success": False, "error": f"Stock insuffisant ({type_billet['quantite_disponible']} dispo)"}
        
        montant_total = type_billet['prix'] * quantite
        
        try:
            id_vente = self.vente_dao.create(id_acheteur, id_type_billet, quantite, montant_total)
            nouvelle_qte = type_billet['quantite_disponible'] - quantite
            self.type_billet_dao.update_quantite(id_type_billet, nouvelle_qte)
            return {"success": True, "id_vente": id_vente, "montant_total": montant_total}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def lister_ventes(self):
        return [dict(v) for v in self.vente_dao.get_all()]
    
    # --- Statistiques ---
    
    def calculer_chiffre_affaires_total(self):
        ca = self.stats_dao.get_chiffre_affaires_total()
        qte = self.stats_dao.get_quantite_totale_vendue()
        return {
            "chiffre_affaires_total": ca,
            "quantite_totale_vendue": qte,
            "panier_moyen": round(ca / qte, 2) if qte > 0 else 0
        }
    
    def calculer_ca_par_evenement(self):
        return [dict(r) for r in self.stats_dao.get_chiffre_affaires_par_evenement()]
    
    def calculer_taux_remplissage(self):
        return [dict(r) for r in self.stats_dao.get_taux_remplissage_par_evenement()]
    
    def obtenir_top_billets(self):
        return [dict(r) for r in self.stats_dao.get_top_billets()]
    
    def obtenir_top_acheteurs(self, limit=5):
        return [dict(r) for r in self.stats_dao.get_top_acheteurs(limit)]
    
    def obtenir_stats_par_categorie(self):
        return [dict(r) for r in self.stats_dao.get_ventes_par_categorie()]
    
    def calculer_indicateurs_avances(self):
        """Calculs avancés côté Python"""
        ca = self.stats_dao.get_chiffre_affaires_total()
        qte = self.stats_dao.get_quantite_totale_vendue()
        ca_evt = self.calculer_ca_par_evenement()
        taux = self.calculer_taux_remplissage()
        
        if ca_evt:
            ca_moyen = sum(e['chiffre_affaires'] for e in ca_evt) / len(ca_evt)
            top_evt = max(ca_evt, key=lambda x: x['chiffre_affaires'])
            taux_moyen = sum(t['taux_remplissage'] for t in taux) / len(taux)
        else:
            ca_moyen, top_evt, taux_moyen = 0, None, 0
        
        return {
            "chiffre_affaires_total": ca,
            "quantite_totale": qte,
            "prix_moyen_billet": round(ca / qte, 2) if qte > 0 else 0,
            "ca_moyen_par_evenement": round(ca_moyen, 2),
            "taux_remplissage_moyen": round(taux_moyen, 2),
            "evenement_top": top_evt['evenement'] if top_evt else "Aucun",
            "date_analyse": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    
    def fermer_connexion(self):
        DatabaseConnection().close()
