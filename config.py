"""
config.py
----------
Configuration centrale de l'application BiblioGest.

Les paramètres sensibles (identifiants de connexion à la base de données,
clé secrète Flask) sont lus depuis des variables d'environnement afin de
ne jamais être codés en dur dans le dépôt Git. Un fichier .env (non versionné,
voir .env.example) peut être utilisé en développement local grâce à
python-dotenv.
"""

import os
from dotenv import load_dotenv

# Charge le fichier .env s'il existe (développement local)
load_dotenv()


class Config:
    """Configuration de base commune à tous les environnements."""

    # Clé secrète utilisée par Flask pour signer les sessions et les cookies
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-moi-en-production")

    # --- Paramètres de connexion MySQL ---
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "bibliogest")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Règles métier ---
    # Nombre de jours accordés par défaut pour un emprunt
    DUREE_EMPRUNT_JOURS = int(os.environ.get("DUREE_EMPRUNT_JOURS", 14))

    # Montant de la pénalité appliqué par jour de retard (en unité monétaire locale)
    PENALITE_PAR_JOUR = float(os.environ.get("PENALITE_PAR_JOUR", 100))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
