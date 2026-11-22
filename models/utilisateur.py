"""
models/utilisateur.py
----------------------
Modèle représentant les comptes utilisateurs de l'application
(administrateurs et bibliothécaires). Implémente UserMixin pour
s'intégrer avec Flask-Login.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from models import db


class Utilisateur(db.Model, UserMixin):
    __tablename__ = "utilisateurs"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    mot_de_passe_hash = db.Column(db.String(255), nullable=False)
    # Rôle : "administrateur" ou "bibliothecaire"
    role = db.Column(db.String(20), nullable=False, default="bibliothecaire")
    actif = db.Column(db.Boolean, default=True, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation : un utilisateur peut avoir enregistré plusieurs emprunts
    emprunts = db.relationship("Emprunt", backref="utilisateur", lazy=True)

    def set_password(self, mot_de_passe):
        """Hache et stocke le mot de passe (jamais en clair)."""
        self.mot_de_passe_hash = generate_password_hash(mot_de_passe)

    def verifier_mot_de_passe(self, mot_de_passe):
        """Vérifie un mot de passe en clair contre le hachage stocké."""
        return check_password_hash(self.mot_de_passe_hash, mot_de_passe)

    @property
    def est_administrateur(self):
        return self.role == "administrateur"

    def get_id(self):
        # Requis par Flask-Login
        return str(self.id)

    def __repr__(self):
        return f"<Utilisateur {self.email} ({self.role})>"
