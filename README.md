# 🎫 Billetterie Locale - TP Base de Données

## 👥 Auteurs
- **Ridwan**
- **Sébastien**

## 📅 Date
Janvier 2026

---

## 🎯 Description du Projet

Application de gestion de billetterie locale pour événements (concerts, conférences, spectacles).

**Technologies utilisées :**
- **SQLite** : Base de données locale (fichier .db)
- **Python 3** : Backend avec le module `sqlite3` intégré
- **Tkinter** : Interface graphique (aucun package externe)

---

## 🚀 Lancement du Projet

```bash
# 1. Aller dans le dossier
cd billetterie

# 2. Initialiser les données de test (1ère fois seulement)
python insert_data.py

# 3. Lancer l'application
python app.py
```

---

## 📁 Structure du Projet

```
billetterie/
├── config.py         # Chemins vers la base et le schéma
├── schema.sql        # Script SQL de création des tables
├── dao.py            # Requêtes SQL (Data Access Object)
├── services.py       # Logique métier et validations
├── app.py            # Interface graphique Tkinter
├── insert_data.py    # Insertion des données de test
├── billetterie.db    # Base SQLite (générée automatiquement)
└── README.md         # Ce fichier
```

### Architecture 3 couches

```
┌─────────────────────────────────┐
│    Interface (app.py)           │  ← Tkinter, affichage
├─────────────────────────────────┤
│    Services (services.py)       │  ← Validations, calculs Python
├─────────────────────────────────┤
│    DAO (dao.py)                 │  ← Requêtes SQL paramétrées
├─────────────────────────────────┤
│    SQLite (billetterie.db)      │  ← Base de données
└─────────────────────────────────┘
```

---

## 🗄️ Base de Données

### Tables (4)

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

- `types_billets.id_evenement` → `evenements.id_evenement` (FK)
- `ventes.id_acheteur` → `acheteurs.id_acheteur` (FK)
- `ventes.id_type_billet` → `types_billets.id_type_billet` (FK)

---

## 🔧 Fonctionnalités

### Gestion (CRUD)
- ➕ Ajouter une vente
- 🗑️ Supprimer une vente
- 📜 Lister les ventes
- 🎭 Lister les événements
- 👥 Lister les acheteurs

### Statistiques (Agrégats SQL)
- 💰 Chiffre d'affaires total (`SUM`)
- 🎯 CA par événement (`GROUP BY`)
- 📈 Taux de remplissage (%)
- 🏆 Top billets vendus
- 👑 Top acheteurs

---

## 🔒 Sécurité

### Requêtes paramétrées (anti-injection SQL)

```python
# ✅ CORRECT - avec des ?
cursor.execute("SELECT * FROM acheteurs WHERE id = ?", (id,))

# ❌ INTERDIT - concaténation
cursor.execute("SELECT * FROM acheteurs WHERE id = " + id)
```

---

## 📊 Données de Test

Le script `insert_data.py` crée :
- 10 acheteurs
- 8 événements (3 concerts, 2 conférences, 3 spectacles)
- 24 types de billets
- 50 ventes

---

## 🎨 Interface

- Design dark mode moderne
- Interface responsive (s'adapte à l'écran)
- Sidebar avec boutons d'action
- Cartes de statistiques animées

---

## 📝 Points Techniques Importants

1. **`import sqlite3`** : Module Python intégré (pas MySQL)
2. **Pattern Singleton** : Une seule connexion à la base
3. **Clés étrangères** : `FOREIGN KEY ... ON DELETE CASCADE`
4. **Index** : Sur les colonnes fréquemment recherchées
5. **`PRAGMA foreign_keys = ON`** : Active les FK dans SQLite
6. **Chemins absolus** : `os.path.abspath(__file__)` pour éviter les erreurs
