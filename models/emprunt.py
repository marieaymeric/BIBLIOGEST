"""
models/emprunt.py
------------------
Modèle représentant un emprunt : association entre un lecteur et un livre,
enregistrée par un utilisateur (bibliothécaire/administrateur).

Statuts possibles :
- "en_cours"  : le livre n'a pas encore été rendu, délai non dépassé
- "en_retard" : le livre n'a pas été rendu et la date limite est dépassée
- "retourne"  : le livre a été rendu
"""

from datetime import datetime
from models import db


class Emprunt(db.Model):
    __tablename__ = "emprunts"

    id = db.Column(db.Integer, primary_key=True)

    livre_id = db.Column(db.Integer, db.ForeignKey("livres.id"), nullable=False)
    lecteur_id = db.Column(db.Integer, db.ForeignKey("lecteurs.id"), nullable=False)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("utilisateurs.id"), nullable=False)

    date_emprunt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_limite = db.Column(db.DateTime, nullable=False)
    date_retour_effective = db.Column(db.DateTime, nullable=True)

    statut = db.Column(db.String(20), nullable=False, default="en_cours")

    # Relation : un emprunt peut entraîner une pénalité en cas de retard
    penalite = db.relationship(
        "Penalite", backref="emprunt", uselist=False, lazy=True
    )

    @property
    def est_en_retard(self):
        """Un emprunt est en retard s'il n'est pas rendu et que la date
        limite est dépassée."""
        if self.statut == "retourne":
            return False
        return datetime.utcnow() > self.date_limite

    @property
    def jours_de_retard(self):
        """Nombre de jours de retard, calculés sur la date de retour
        effective si le livre a été rendu, sinon sur la date du jour."""
        reference = self.date_retour_effective or datetime.utcnow()
        delta = (reference - self.date_limite).days
        return max(delta, 0)

    def __repr__(self):
        return f"<Emprunt livre={self.livre_id} lecteur={self.lecteur_id} statut={self.statut}>"
