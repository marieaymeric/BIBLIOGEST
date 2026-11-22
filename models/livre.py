"""
models/livre.py
----------------
Modèle représentant un livre du catalogue de la bibliothèque.

Un livre peut exister en plusieurs exemplaires physiques :
- nb_exemplaires   : nombre total d'exemplaires possédés par la bibliothèque
- nb_disponibles   : nombre d'exemplaires actuellement disponibles à l'emprunt

Ces deux compteurs permettent de contrôler la disponibilité et d'empêcher
un emprunt lorsque le stock disponible est insuffisant (voir
controllers/emprunt_controller.py).
"""

from models import db


class Livre(db.Model):
    __tablename__ = "livres"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    auteur = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=True)
    editeur = db.Column(db.String(150), nullable=True)
    annee_publication = db.Column(db.Integer, nullable=True)

    nb_exemplaires = db.Column(db.Integer, nullable=False, default=1)
    nb_disponibles = db.Column(db.Integer, nullable=False, default=1)

    categorie_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    # Relation : un livre peut être emprunté plusieurs fois au cours du temps
    emprunts = db.relationship("Emprunt", backref="livre", lazy=True)

    @property
    def disponible(self):
        """Un livre est disponible si au moins un exemplaire ne circule pas."""
        return self.nb_disponibles > 0

    def __repr__(self):
        return f"<Livre {self.titre} ({self.nb_disponibles}/{self.nb_exemplaires})>"
