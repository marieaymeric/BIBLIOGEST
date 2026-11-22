"""
models/categorie.py
--------------------
Modèle représentant les catégories d'ouvrages (ex : Roman, Informatique,
Histoire...). Une catégorie peut contenir plusieurs livres.
"""

from models import db


class Categorie(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relation : une catégorie peut contenir plusieurs livres
    livres = db.relationship("Livre", backref="categorie", lazy=True)

    def __repr__(self):
        return f"<Categorie {self.nom}>"
