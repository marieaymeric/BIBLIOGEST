# BiblioGest

Application web de gestion de bibliothèque développée en **Python** avec le
framework **Flask**, une base de données **MySQL**, et une architecture
**MVC (Modèle – Vue – Contrôleur)**.

Projet académique réalisé dans le cadre d'un cahier des charges (voir
`Cahier_des_charges_BiblioGest.pdf`).

## Fonctionnalités

- Authentification (connexion / déconnexion) avec gestion des rôles
  **administrateur** et **bibliothécaire**, mots de passe hachés.
- Tableau de bord avec indicateurs clés (livres, lecteurs, emprunts en
  cours, retards).
- Gestion du catalogue de livres : ajout, consultation, modification,
  suppression, recherche, catégories, suivi du stock disponible.
- Gestion des lecteurs : inscription, modification, désactivation,
  historique des emprunts.
- Gestion des emprunts : enregistrement avec vérification automatique de
  la disponibilité, enregistrement des retours, mise à jour du stock.
- Gestion des pénalités : calcul automatique en cas de retard, suivi du
  paiement.
- Rapports et statistiques : livres les plus empruntés, lecteurs les plus
  actifs, historique, pénalités.

## Stack technique

| Composant       | Technologie           |
|-----------------|------------------------|
| Langage         | Python 3.10+           |
| Framework web   | Flask                  |
| Base de données | MySQL                  |
| ORM             | Flask-SQLAlchemy       |
| Pilote MySQL    | PyMySQL                |
| Authentification| Flask-Login            |
| Frontend        | HTML5, CSS3, Bootstrap 5, Jinja2 |

## Arborescence du projet

```text
BIBLIOGEST/
├── app.py                  # Point d'entrée Flask (application factory)
├── config.py                # Configuration (lit les variables d'environnement)
├── requirements.txt          # Dépendances Python
├── .env.example               # Modèle de fichier d'environnement
├── models/                     # Modèle (M) : définitions SQLAlchemy
│   ├── __init__.py
│   ├── utilisateur.py
│   ├── categorie.py
│   ├── livre.py
│   ├── lecteur.py
│   ├── emprunt.py
│   └── penalite.py
├── controllers/                # Contrôleur (C) : Blueprints Flask
│   ├── __init__.py
│   ├── decorateurs.py
│   ├── auth_controller.py
│   ├── livre_controller.py
│   ├── lecteur_controller.py
│   └── emprunt_controller.py
├── views/
│   └── templates/              # Vue (V) : templates Jinja2
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── database/
    └── schema.sql              # Schéma SQL de référence
```

## Prérequis

- Python 3.10 ou supérieur
- MySQL Server (ou MariaDB) installé et démarré
- pip / venv

## Installation

### 1. Récupérer le projet

```bash
git clone <url-de-votre-depot> bibliogest
cd bibliogest
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Copiez le fichier d'exemple puis adaptez les valeurs à votre installation
MySQL :

```bash
cp .env.example .env
```

Éditez `.env` et renseignez au minimum `DB_USER`, `DB_PASSWORD`, `DB_HOST`
et `SECRET_KEY`.

### 5. Créer la base de données

Deux options :

**Option A — via le script SQL fourni :**

```bash
mysql -u root -p < database/schema.sql
```

**Option B — laisser Flask-SQLAlchemy créer les tables :**

Créez simplement une base vide nommée `bibliogest` dans MySQL, puis
exécutez (voir étape suivante) la commande `flask init-db`, qui génère
toutes les tables à partir des modèles Python.

```sql
CREATE DATABASE bibliogest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Initialiser les tables et créer un compte administrateur

```bash
export FLASK_APP=app.py          # Windows (PowerShell) : $env:FLASK_APP="app.py"

flask init-db
flask create-admin
```

La commande `create-admin` crée un compte administrateur par défaut :

- **E-mail :** `admin@bibliogest.local`
- **Mot de passe :** `admin123`

> ⚠️ Pensez à changer ce mot de passe dès la première connexion
> (menu Utilisateurs, réservé aux administrateurs).

### 7. Lancer l'application

```bash
python app.py
```

L'application est accessible à l'adresse : http://127.0.0.1:5000

## Utilisation de Git

Le fichier `.gitignore` exclut déjà l'environnement virtuel, le fichier
`.env` et les fichiers temporaires Python. Pour initialiser le dépôt :

```bash
git init
git add .
git commit -m "Initial commit — BiblioGest"
git branch -M main
git remote add origin <url-de-votre-depot>
git push -u origin main
```

## Notes pédagogiques

- L'application suit strictement l'architecture **MVC** : les modèles
  (`models/`) ne contiennent aucune logique de présentation, les vues
  (`views/templates/`) ne contiennent aucune logique métier, et les
  contrôleurs (`controllers/`) orchestrent les échanges entre les deux.
- La règle métier centrale (empêcher un emprunt lorsque le stock
  disponible est insuffisant, actualiser le stock après chaque retour,
  calculer automatiquement les pénalités de retard) est implémentée dans
  `controllers/emprunt_controller.py`.
- Les durées d'emprunt et le montant des pénalités par jour de retard
  sont configurables dans `.env` (`DUREE_EMPRUNT_JOURS`,
  `PENALITE_PAR_JOUR`) sans toucher au code.
