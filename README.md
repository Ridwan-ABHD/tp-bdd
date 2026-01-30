# Billetterie Locale - TP Base de Données

**Auteurs :** Ridwan & Sébastien  
**Date :** Janvier 2026

---

## Description

Application de gestion de billetterie locale pour événements (concerts, conférences, spectacles).

**Technologies :**
- SQLite (base de données locale)
- Python 3 avec le module `sqlite3`
- Tkinter pour l'interface graphique

---

## Lancement

```bash
# 1. Initialiser les données de test (1ère fois)
python insert_data.py

# 2. Lancer l'application
python app.py
```

---

## Structure du Projet

```
billetterie/
├── config.py         # Chemins vers la base et le schéma
├── schema.sql        # Script SQL de création des tables
├── dao.py            # Requêtes SQL (Data Access Object)
├── services.py       # Logique métier et validations
├── app.py            # Interface graphique Tkinter
├── insert_data.py    # Insertion des données de test
├── billetterie.db    # Base SQLite (générée auto)
└── README.md
```

### Architecture 3 couches

```
Interface (app.py)      → Tkinter, affichage
        ↓
Services (services.py)  → Validations, calculs
        ↓
DAO (dao.py)            → Requêtes SQL
        ↓
SQLite (billetterie.db) → Base de données
```

---

## Base de Données

### Tables

| Table | Description |
|-------|-------------|
| `acheteurs` | Clients (nom, prénom, email, téléphone) |
| `evenements` | Événements (nom, date, lieu, catégorie, capacité) |
| `types_billets` | Tarifs par événement (Standard, VIP, etc.) |
| `ventes` | Transactions d'achat |

### Relations

```
acheteurs ──────┐
                │
                ▼
            ventes ◄─── types_billets ◄─── evenements
```

- `types_billets.id_evenement` → `evenements.id_evenement`
- `ventes.id_acheteur` → `acheteurs.id_acheteur`
- `ventes.id_type_billet` → `types_billets.id_type_billet`

---

## Fonctionnalités

**Gestion :**
- Ajouter / supprimer une vente
- Lister les ventes, événements, acheteurs

**Statistiques :**
- Chiffre d'affaires total (SUM)
- CA par événement (GROUP BY)
- Taux de remplissage
- Top billets vendus
- Top acheteurs

---

## Sécurité

Requêtes paramétrées pour éviter les injections SQL :

```python
# Correct
cursor.execute("SELECT * FROM acheteurs WHERE id = ?", (id,))

# A éviter
cursor.execute("SELECT * FROM acheteurs WHERE id = " + id)
```

---

## Données de Test

Le script `insert_data.py` crée :
- 10 acheteurs
- 8 événements
- 24 types de billets
- 50 ventes

---

## Points Techniques

- `import sqlite3` : module Python intégré
- Pattern Singleton pour la connexion
- Clés étrangères avec ON DELETE CASCADE
- `PRAGMA foreign_keys = ON` pour activer les FK
- Chemins absolus avec `os.path.abspath(__file__)`
