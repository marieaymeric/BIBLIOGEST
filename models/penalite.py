"""
models/penalite.py
-------------------
Modèle représentant une pénalité appliquée à un emprunt rendu en retard.
"""

from datetime import datetime
from models import db


class Penalite(db.Model):
    __tablename__ = "penalites"

    id = db.Column(db.Integer, primary_key=True)
    emprunt_id = db.Column(db.Integer, db.ForeignKey("emprunts.id"), nullable=False, unique=True)

    montant = db.Column(db.Float, nullable=False, default=0.0)
    jours_de_retard = db.Column(db.Integer, nullable=False, default=0)
    # Statut de paiement : "impayee" ou "payee"
    statut_paiement = db.Column(db.String(20), nullable=False, default="impayee")
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_paiement = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Penalite emprunt={self.emprunt_id} montant={self.montant} statut={self.statut_paiement}>"
