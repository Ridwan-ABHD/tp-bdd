# Script d'insertion de données de test
# Auteurs : Ridwan & Sébastien

from dao import init_database, AcheteurDAO, EvenementDAO, TypeBilletDAO, VenteDAO, DatabaseConnection
from datetime import datetime, timedelta
import random


def inserer_donnees():
    """Insère des données de test dans la base"""
    
    print("Initialisation de la base...")
    init_database()
    
    acheteur_dao = AcheteurDAO()
    evenement_dao = EvenementDAO()
    type_billet_dao = TypeBilletDAO()
    vente_dao = VenteDAO()
    
    # Acheteurs
    print("Insertion des acheteurs...")
    acheteurs = [
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
    
    ids_acheteurs = []
    for nom, prenom, email, tel in acheteurs:
        id_a = acheteur_dao.create(nom, prenom, email, tel)
        ids_acheteurs.append(id_a)
    print(f"  {len(ids_acheteurs)} acheteurs créés")
    
    # Événements
    print("Insertion des événements...")
    today = datetime.now()
    
    evenements = [
        ("Concert Rock Night", "Soirée rock", (today + timedelta(days=30)).strftime("%Y-%m-%d"), 
         "20:00", "Salle des Fêtes", 500, "concert"),
        ("Jazz en Ville", "Festival jazz", (today + timedelta(days=45)).strftime("%Y-%m-%d"), 
         "19:30", "Place du Marché", 300, "concert"),
        ("Électro Party", "Nuit électro", (today + timedelta(days=60)).strftime("%Y-%m-%d"), 
         "22:00", "Hangar 42", 800, "concert"),
        ("Tech Summit", "Conférence IA", (today + timedelta(days=15)).strftime("%Y-%m-%d"), 
         "09:00", "Centre des Congrès", 200, "conference"),
        ("Forum Écologie", "Développement durable", (today + timedelta(days=25)).strftime("%Y-%m-%d"), 
         "10:00", "Maison Environnement", 150, "conference"),
        ("Cirque Moderne", "Spectacle contemporain", (today + timedelta(days=20)).strftime("%Y-%m-%d"), 
         "15:00", "Chapiteau", 400, "spectacle"),
        ("Comédie Musicale", "Les Misérables", (today + timedelta(days=35)).strftime("%Y-%m-%d"), 
         "20:30", "Théâtre Municipal", 350, "spectacle"),
        ("One Man Show", "Humour", (today + timedelta(days=10)).strftime("%Y-%m-%d"), 
         "21:00", "Café Théâtre", 100, "spectacle"),
    ]
    
    ids_evenements = []
    for nom, desc, date, heure, lieu, cap, cat in evenements:
        id_e = evenement_dao.create(nom, desc, date, heure, lieu, cap, cat)
        ids_evenements.append((id_e, cap, cat))
    print(f"  {len(ids_evenements)} événements créés")
    
    # Types de billets
    print("Insertion des types de billets...")
    types_par_cat = {
        "concert": [("Standard", 25.00, 0.6), ("VIP", 50.00, 0.2), ("Early Bird", 20.00, 0.2)],
        "conference": [("Simple", 15.00, 0.5), ("Journée", 35.00, 0.3), ("VIP", 75.00, 0.2)],
        "spectacle": [("Libre", 18.00, 0.5), ("Cat.1", 30.00, 0.3), ("Premium", 45.00, 0.2)],
    }
    
    ids_types = []
    for id_evt, capacite, categorie in ids_evenements:
        for nom_type, prix, ratio in types_par_cat[categorie]:
            quantite = int(capacite * ratio)
            id_t = type_billet_dao.create(id_evt, nom_type, prix, quantite)
            ids_types.append((id_t, prix))
    print(f"  {len(ids_types)} types de billets créés")
    
    # Ventes
    print("Insertion des ventes...")
    nb_ventes = 0
    for _ in range(50):
        id_acheteur = random.choice(ids_acheteurs)
        id_type, prix = random.choice(ids_types)
        quantite = random.randint(1, 4)
        montant = prix * quantite
        vente_dao.create(id_acheteur, id_type, quantite, montant)
        nb_ventes += 1
    print(f"  {nb_ventes} ventes créées")
    
    # Fermeture
    DatabaseConnection().close()
    print("\nTerminé !")


if __name__ == "__main__":
    inserer_donnees()
