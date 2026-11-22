-- schema.sql
-- ----------
-- Schéma de la base de données "bibliogest".
-- Ce fichier est fourni à titre de référence / sauvegarde : en pratique,
-- les tables sont créées automatiquement par Flask-SQLAlchemy via la
-- commande `flask init-db` (voir README.md). Il peut cependant être
-- exécuté manuellement avec un client MySQL si nécessaire.

CREATE DATABASE IF NOT EXISTS bibliogest
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE bibliogest;

-- Table des comptes utilisateurs (administrateurs et bibliothécaires)
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'bibliothecaire',
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Table des catégories d'ouvrages
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
) ENGINE=InnoDB;

-- Table des livres
CREATE TABLE IF NOT EXISTS livres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    auteur VARCHAR(150) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    editeur VARCHAR(150),
    annee_publication INT,
    nb_exemplaires INT NOT NULL DEFAULT 1,
    nb_disponibles INT NOT NULL DEFAULT 1,
    categorie_id INT,
    FOREIGN KEY (categorie_id) REFERENCES categories(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- Table des lecteurs (abonnés)
CREATE TABLE IF NOT EXISTS lecteurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    telephone VARCHAR(30),
    adresse VARCHAR(255),
    date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP,
    actif BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- Table des emprunts
CREATE TABLE IF NOT EXISTS emprunts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    livre_id INT NOT NULL,
    lecteur_id INT NOT NULL,
    utilisateur_id INT NOT NULL,
    date_emprunt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_limite DATETIME NOT NULL,
    date_retour_effective DATETIME,
    statut VARCHAR(20) NOT NULL DEFAULT 'en_cours',
    FOREIGN KEY (livre_id) REFERENCES livres(id),
    FOREIGN KEY (lecteur_id) REFERENCES lecteurs(id),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
) ENGINE=InnoDB;

-- Table des pénalités
CREATE TABLE IF NOT EXISTS penalites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emprunt_id INT NOT NULL UNIQUE,
    montant FLOAT NOT NULL DEFAULT 0,
    jours_de_retard INT NOT NULL DEFAULT 0,
    statut_paiement VARCHAR(20) NOT NULL DEFAULT 'impayee',
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_paiement DATETIME,
    FOREIGN KEY (emprunt_id) REFERENCES emprunts(id)
) ENGINE=InnoDB;
