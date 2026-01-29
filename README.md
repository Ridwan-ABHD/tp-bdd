# 📋 Documentation Technique - Projet Billetterie Locale

## 👥 Auteurs
- **Ridwan**
- **Sébastien**

## 📅 Date
Janvier 2026

---

## 🎯 Objectif du Projet

Application locale de gestion de billetterie pour événements (concerts, conférences, spectacles) avec :
- Base de données SQLite
- Backend Python
- Interface graphique Tkinter

---

## 🏗️ Architecture du Projet

```
billetterie/
│
├── config.py           # Configuration (chemins, constantes)
├── schema.sql          # Script SQL de création des tables
├── dao.py              # Data Access Object (accès aux données)
├── services.py         # Logique métier
├── app.py              # Interface graphique Tkinter
├── insert_data.py      # Script d'insertion des données de test
├── billetterie.db      # Base de données SQLite (générée)
└── README.md           # Cette documentation
```

### Architecture en couches

```
┌─────────────────────────────────┐
│        Interface (app.py)       │  ← Tkinter, aucun SQL
├─────────────────────────────────┤
│   Logique Métier (services.py)  │  ← Validation, calculs Python
├─────────────────────────────────┤
│   Accès Données (dao.py)        │  ← Requêtes SQL paramétrées
├─────────────────────────────────┤
│        SQLite (billetterie.db)  │  ← Base de données
└─────────────────────────────────┘
```

---

## 📊 Modèle de Données

### Diagramme Entité-Relation

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│  acheteurs  │       │  types_billets   │       │ evenements  │
├─────────────┤       ├──────────────────┤       ├─────────────┤
│ id_acheteur │◄──┐   │ id_type_billet   │   ┌──►│id_evenement │
│ nom         │   │   │ id_evenement     │───┘   │ nom         │
│ prenom      │   │   │ nom_type         │       │ description │
│ email       │   │   │ prix             │       │ date_event  │
│ telephone   │   │   │ quantite_dispo   │       │ heure_debut │
│ date_inscr  │   │   └──────────────────┘       │ lieu        │
└─────────────┘   │            ▲                 │ capacite_max│
                  │            │                 │ categorie   │
                  │   ┌────────┴───────┐         └─────────────┘
                  │   │     ventes     │
                  │   ├────────────────┤
                  └───┤ id_acheteur    │
                      │ id_type_billet │
                      │ quantite       │
                      │ date_vente     │
                      │ montant_total  │
                      └────────────────┘
```

### Tables

| Table | Description | Clé Primaire | Clés Étrangères |
|-------|-------------|--------------|-----------------|
| `acheteurs` | Clients qui achètent des billets | `id_acheteur` | - |
| `evenements` | Concerts, conférences, spectacles | `id_evenement` | - |
| `types_billets` | Catégories de billets par événement | `id_type_billet` | `id_evenement` |
| `ventes` | Transactions d'achat | `id_vente` | `id_acheteur`, `id_type_billet` |

---

## 🔒 Sécurité Logique

### 1. Requêtes Paramétrées (OBLIGATOIRE)

**❌ INTERDIT - Concaténation de chaînes :**
```python
# DANGEREUX - Injection SQL possible!
query = "SELECT * FROM acheteurs WHERE email = '" + email + "'"
```

**✅ CORRECT - Requête paramétrée :**
```python
# SÉCURISÉ - Paramètres échappés automatiquement
query = "SELECT * FROM acheteurs WHERE email = ?"
cursor.execute(query, (email,))
```

### 2. Séparation Lecture / Écriture

- **DAO** : Contient TOUTES les requêtes SQL
- **Services** : Logique métier, aucun SQL
- **UI** : Interface utilisateur, aucun SQL

### 3. Gestion des Transactions

```python
# Toujours commit après une insertion
cursor.execute(query, params)
conn.commit()  # ← Ne pas oublier!

# En cas d'erreur
conn.rollback()
```

### 4. Connexion Unique (Singleton)

```python
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

---

## 📝 Requêtes SQL Implémentées

### Niveau 1 - Requêtes Simples

```sql
-- Insertion d'un acheteur
INSERT INTO acheteurs (nom, prenom, email, telephone)
VALUES (?, ?, ?, ?);

-- Sélection avec filtre WHERE
SELECT * FROM evenements WHERE categorie = ?;
```

### Niveau 2 - Requêtes Intermédiaires

```sql
-- Jointure entre tables
SELECT v.*, a.nom, a.prenom, tb.nom_type, e.nom AS evenement
FROM ventes v
JOIN acheteurs a ON v.id_acheteur = a.id_acheteur
JOIN types_billets tb ON v.id_type_billet = tb.id_type_billet
JOIN evenements e ON tb.id_evenement = e.id_evenement;

-- Agrégats (SUM, COUNT)
SELECT COALESCE(SUM(montant_total), 0) as ca_total FROM ventes;
```

### Niveau 3 - Requêtes Avancées

```sql
-- GROUP BY et indicateurs métier
SELECT 
    e.nom AS evenement,
    e.capacite_max,
    COALESCE(SUM(v.quantite), 0) AS billets_vendus,
    ROUND(COALESCE(SUM(v.quantite), 0) * 100.0 / e.capacite_max, 2) AS taux_remplissage
FROM evenements e
LEFT JOIN types_billets tb ON e.id_evenement = tb.id_evenement
LEFT JOIN ventes v ON tb.id_type_billet = v.id_type_billet
GROUP BY e.id_evenement, e.nom, e.capacite_max
ORDER BY taux_remplissage DESC;
```

---

## 📊 Analyses Métier Implémentées

| Indicateur | Description | Implémentation |
|------------|-------------|----------------|
| CA Total | Chiffre d'affaires global | SQL (SUM) |
| Quantité Vendue | Nombre total de billets | SQL (SUM) |
| Panier Moyen | CA / Nombre de ventes | Python |
| Taux de Remplissage | Vendus / Capacité × 100 | SQL (calcul) |
| Top Billets | Classement par quantité vendue | SQL (GROUP BY, ORDER BY) |
| CA par Événement | Revenus par événement | SQL (JOIN, GROUP BY) |
| Indicateurs Avancés | Moyennes, comparaisons | Python |

---

## 🖥️ Interface Tkinter - Équivalences API

| Bouton UI | Équivalent API | Fonction |
|-----------|---------------|----------|
| Ajouter Vente | `POST /vente` | `effectuer_vente()` |
| Lister Ventes | `GET /ventes` | `lister_ventes()` |
| Calcul CA | `GET /stats/ca` | `calculer_chiffre_affaires_total()` |
| Billets Top | `GET /stats/top` | `obtenir_top_billets()` |

---

## 🚀 Instructions d'Utilisation

### 1. Initialiser le projet

```bash
cd billetterie
python insert_data.py
```

### 2. Lancer l'application

```bash
python app.py
```

### 3. Utiliser l'interface

- Cliquer sur les boutons pour exécuter les actions
- Les résultats s'affichent dans le panneau de droite
- La barre de statut indique l'état de l'opération

---

## ⚠️ Pièges Évités

| Piège | Solution |
|-------|----------|
| Oublier `commit()` | Toujours appelé après insertion dans le DAO |
| SQL dans l'UI | L'UI n'utilise que les services |
| Mélanger logique et données | Architecture en 3 couches |
| Concaténer des chaînes SQL | Requêtes paramétrées uniquement |
| Connexions multiples | Pattern Singleton |

---

## 📁 Livrables

- ✅ `billetterie.db` - Fichier SQLite
- ✅ `schema.sql` - Script de création du schéma
- ✅ `dao.py`, `services.py`, `app.py` - Scripts Python
- ✅ `README.md` - Documentation technique

---

## 📈 Améliorations Possibles (Bonus)

1. Export des statistiques en CSV
2. Graphiques avec matplotlib
3. Gestion des remboursements
4. Système de réservation avec expiration
5. Notifications par email
