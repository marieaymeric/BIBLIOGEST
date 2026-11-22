"""
models/lecteur.py
------------------
Modèle représentant un lecteur (abonné) de la bibliothèque.
"""

from datetime import datetime
from models import db


class Lecteur(db.Model):
    __tablename__ = "lecteurs"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    telephone = db.Column(db.String(30), nullable=True)
    adresse = db.Column(db.String(255), nullable=True)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    # Permet de désactiver un lecteur sans supprimer son historique
    actif = db.Column(db.Boolean, default=True, nullable=False)

    # Relation : un lecteur peut effectuer plusieurs emprunts
    emprunts = db.relationship("Emprunt", backref="lecteur", lazy=True)

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def __repr__(self):
        return f"<Lecteur {self.nom_complet}>"
