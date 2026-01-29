"""
Script d'insertion automatique de données de test
Projet : Gestion de billetterie locale
Auteurs : Ridwan & Sébastien

Ce script peuple la base de données avec des données réalistes pour les tests
"""

from dao import (
    init_database, 
    AcheteurDAO, EvenementDAO, TypeBilletDAO, VenteDAO,
    DatabaseConnection
)
from datetime import datetime, timedelta
import random


def inserer_donnees_test():
    """Insère des données de test dans la base"""
    
    print("=" * 60)
    print("🚀 INSERTION DES DONNÉES DE TEST")
    print("=" * 60)
    
    # Initialiser la base de données (crée les tables)
    print("\n📦 Initialisation de la base de données...")
    init_database()
    
    # Instancier les DAOs
    acheteur_dao = AcheteurDAO()
    evenement_dao = EvenementDAO()
    type_billet_dao = TypeBilletDAO()
    vente_dao = VenteDAO()
    
    # ============================================
    # 1. Insertion des acheteurs
    # ============================================
    print("\n👥 Insertion des acheteurs...")
    
    acheteurs_data = [
        ("Dupont", "Marie", "marie.dupont@email.com", "0612345678"),
        ("Martin", "Jean", "jean.martin@email.com", "0698765432"),
        ("Bernard", "Sophie", "sophie.bernard@email.com", "0645678901"),
        ("Petit", "Lucas", "lucas.petit@email.com", "0654321098"),
        ("Durand", "Emma", "emma.durand@email.com", "0623456789"),
        ("Leroy", "Thomas", "thomas.leroy@email.com", "0687654321"),
        ("Moreau", "Chloé", "chloe.moreau@email.com", "0634567890"),
        ("Simon", "Hugo", "hugo.simon@email.com", "0676543210"),
        ("Laurent", "Léa", "lea.laurent@email.com", "0656789012"),
        ("Roux", "Nathan", "nathan.roux@email.com", "0665432109"),
    ]
    
    acheteurs_ids = []
    for nom, prenom, email, tel in acheteurs_data:
        id_acheteur = acheteur_dao.create(nom, prenom, email, tel)
        acheteurs_ids.append(id_acheteur)
        print(f"   ✓ {prenom} {nom} (ID: {id_acheteur})")
    
    # ============================================
    # 2. Insertion des événements
    # ============================================
    print("\n🎭 Insertion des événements...")
    
    # Dates pour les événements (passés et futurs)
    today = datetime.now()
    
    evenements_data = [
        # Concerts
        ("Concert Rock Night", "Soirée rock avec plusieurs groupes locaux", 
         (today + timedelta(days=30)).strftime("%Y-%m-%d"), "20:00", "Salle des Fêtes", 500, "concert"),
        ("Jazz en Ville", "Festival de jazz acoustique", 
         (today + timedelta(days=45)).strftime("%Y-%m-%d"), "19:30", "Place du Marché", 300, "concert"),
        ("Électro Party", "Nuit électro avec DJs internationaux", 
         (today + timedelta(days=60)).strftime("%Y-%m-%d"), "22:00", "Hangar 42", 800, "concert"),
        
        # Conférences
        ("Tech Summit 2026", "Conférence sur l'IA et le futur du travail", 
         (today + timedelta(days=15)).strftime("%Y-%m-%d"), "09:00", "Centre des Congrès", 200, "conference"),
        ("Développement Durable", "Forum sur l'écologie et l'innovation", 
         (today + timedelta(days=25)).strftime("%Y-%m-%d"), "10:00", "Maison de l'Environnement", 150, "conference"),
        
        # Spectacles
        ("Cirque Moderne", "Spectacle de cirque contemporain", 
         (today + timedelta(days=20)).strftime("%Y-%m-%d"), "15:00", "Chapiteau Central", 400, "spectacle"),
        ("Comédie Musicale", "Les Misérables - Version locale", 
         (today + timedelta(days=35)).strftime("%Y-%m-%d"), "20:30", "Théâtre Municipal", 350, "spectacle"),
        ("One Man Show", "Humoriste local en représentation", 
         (today + timedelta(days=10)).strftime("%Y-%m-%d"), "21:00", "Café Théâtre", 100, "spectacle"),
    ]
    
    evenements_ids = []
    for nom, desc, date, heure, lieu, capacite, categorie in evenements_data:
        id_evenement = evenement_dao.create(nom, desc, date, heure, lieu, capacite, categorie)
        evenements_ids.append(id_evenement)
        print(f"   ✓ {nom} - {categorie} (ID: {id_evenement})")
    
    # ============================================
    # 3. Insertion des types de billets
    # ============================================
    print("\n🎫 Insertion des types de billets...")
    
    types_billets_ids = []
    
    # Pour chaque événement, créer des types de billets
    types_par_categorie = {
        "concert": [
            ("Standard", 25.00, 0.6),
            ("VIP", 50.00, 0.2),
            ("Early Bird", 20.00, 0.2),
        ],
        "conference": [
            ("Entrée Simple", 15.00, 0.5),
            ("Pass Journée", 35.00, 0.3),
            ("Pass VIP", 75.00, 0.2),
        ],
        "spectacle": [
            ("Placement Libre", 18.00, 0.5),
            ("Catégorie 1", 30.00, 0.3),
            ("Catégorie Premium", 45.00, 0.2),
        ],
    }
    
    for i, id_evenement in enumerate(evenements_ids):
        categorie = evenements_data[i][6]
        capacite = evenements_data[i][5]
        
        for nom_type, prix, ratio in types_par_categorie[categorie]:
            quantite = int(capacite * ratio)
            id_type = type_billet_dao.create(id_evenement, nom_type, prix, quantite)
            types_billets_ids.append((id_type, prix))
            print(f"   ✓ {evenements_data[i][0]} - {nom_type}: {prix}€ x {quantite}")
    
    # ============================================
    # 4. Insertion des ventes
    # ============================================
    print("\n💳 Insertion des ventes...")
    
    ventes_count = 0
    
    # Générer des ventes aléatoires mais réalistes
    for _ in range(50):  # 50 ventes
        id_acheteur = random.choice(acheteurs_ids)
        id_type_billet, prix = random.choice(types_billets_ids)
        quantite = random.randint(1, 4)
        montant_total = prix * quantite
        
        try:
            id_vente = vente_dao.create(id_acheteur, id_type_billet, quantite, montant_total)
            ventes_count += 1
            print(f"   ✓ Vente #{id_vente}: {quantite} billet(s) pour {montant_total:.2f}€")
        except Exception as e:
            print(f"   ✗ Erreur: {e}")
    
    # ============================================
    # Résumé
    # ============================================
    print("\n" + "=" * 60)
    print("✅ INSERTION TERMINÉE")
    print("=" * 60)
    print(f"   • {len(acheteurs_ids)} acheteurs créés")
    print(f"   • {len(evenements_ids)} événements créés")
    print(f"   • {len(types_billets_ids)} types de billets créés")
    print(f"   • {ventes_count} ventes enregistrées")
    print("=" * 60)
    
    # Fermer la connexion proprement
    db = DatabaseConnection()
    db.close()
    print("\n🔒 Connexion fermée proprement")


if __name__ == "__main__":
    inserer_donnees_test()
