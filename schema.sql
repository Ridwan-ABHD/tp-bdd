-- Schéma de la base de données - Billetterie locale

-- Suppression des tables (ordre inverse des dépendances)
DROP TABLE IF EXISTS ventes;
DROP TABLE IF EXISTS types_billets;
DROP TABLE IF EXISTS evenements;
DROP TABLE IF EXISTS acheteurs;

-- Table des acheteurs
CREATE TABLE acheteurs (
    id_acheteur INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    telephone TEXT,
    date_inscription DATE DEFAULT CURRENT_DATE
);

-- Table des événements
CREATE TABLE evenements (
    id_evenement INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    description TEXT,
    date_evenement DATE NOT NULL,
    heure_debut TEXT NOT NULL,
    lieu TEXT NOT NULL,
    capacite_max INTEGER NOT NULL,
    categorie TEXT CHECK(categorie IN ('concert', 'conference', 'spectacle')) NOT NULL
);

-- Table des types de billets
CREATE TABLE types_billets (
    id_type_billet INTEGER PRIMARY KEY AUTOINCREMENT,
    id_evenement INTEGER NOT NULL,
    nom_type TEXT NOT NULL,
    prix REAL NOT NULL CHECK(prix >= 0),
    quantite_disponible INTEGER NOT NULL CHECK(quantite_disponible >= 0),
    FOREIGN KEY (id_evenement) REFERENCES evenements(id_evenement) ON DELETE CASCADE
);

-- Table des ventes
CREATE TABLE ventes (
    id_vente INTEGER PRIMARY KEY AUTOINCREMENT,
    id_acheteur INTEGER NOT NULL,
    id_type_billet INTEGER NOT NULL,
    quantite INTEGER NOT NULL CHECK(quantite > 0),
    date_vente DATETIME DEFAULT CURRENT_TIMESTAMP,
    montant_total REAL NOT NULL CHECK(montant_total >= 0),
    FOREIGN KEY (id_acheteur) REFERENCES acheteurs(id_acheteur),
    FOREIGN KEY (id_type_billet) REFERENCES types_billets(id_type_billet)
);

-- Index pour les performances
CREATE INDEX idx_ventes_date ON ventes(date_vente);
CREATE INDEX idx_ventes_acheteur ON ventes(id_acheteur);
CREATE INDEX idx_evenements_date ON evenements(date_evenement);
CREATE INDEX idx_types_billets_evenement ON types_billets(id_evenement);
