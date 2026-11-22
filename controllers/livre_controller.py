"""
controllers/livre_controller.py
--------------------------------
Contrôleur gérant le catalogue des livres : ajout, consultation,
modification, suppression, recherche et classement par catégorie.
Gère également la liste des catégories.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from models import db
from models.livre import Livre
from models.categorie import Categorie

livre_bp = Blueprint("livre", __name__, url_prefix="/livres")


@livre_bp.route("/")
@login_required
def liste():
    """Liste des livres avec recherche (titre/auteur) et filtre par catégorie."""
    recherche = request.args.get("q", "").strip()
    categorie_id = request.args.get("categorie_id", type=int)

    requete = Livre.query

    if recherche:
        motif = f"%{recherche}%"
        requete = requete.filter(
            db.or_(Livre.titre.ilike(motif), Livre.auteur.ilike(motif))
        )

    if categorie_id:
        requete = requete.filter_by(categorie_id=categorie_id)

    livres = requete.order_by(Livre.titre).all()
    categories = Categorie.query.order_by(Categorie.nom).all()

    return render_template(
        "livres/liste.html",
        livres=livres,
        categories=categories,
        recherche=recherche,
        categorie_id=categorie_id,
    )


@livre_bp.route("/<int:livre_id>")
@login_required
def details(livre_id):
    livre = Livre.query.get_or_404(livre_id)
    return render_template("livres/details.html", livre=livre)


@livre_bp.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    categories = Categorie.query.order_by(Categorie.nom).all()

    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        auteur = request.form.get("auteur", "").strip()
        isbn = request.form.get("isbn", "").strip() or None
        editeur = request.form.get("editeur", "").strip() or None
        annee = request.form.get("annee_publication", type=int)
        categorie_id = request.form.get("categorie_id", type=int)
        nb_exemplaires = request.form.get("nb_exemplaires", type=int) or 1

        if not titre or not auteur:
            flash("Le titre et l'auteur sont obligatoires.", "danger")
            return redirect(url_for("livre.ajouter"))

        livre = Livre(
            titre=titre,
            auteur=auteur,
            isbn=isbn,
            editeur=editeur,
            annee_publication=annee,
            categorie_id=categorie_id,
            nb_exemplaires=nb_exemplaires,
            nb_disponibles=nb_exemplaires,
        )
        db.session.add(livre)
        db.session.commit()

        flash("Livre ajouté avec succès.", "success")
        return redirect(url_for("livre.liste"))

    return render_template("livres/formulaire.html", livre=None, categories=categories)


@livre_bp.route("/<int:livre_id>/modifier", methods=["GET", "POST"])
@login_required
def modifier(livre_id):
    livre = Livre.query.get_or_404(livre_id)
    categories = Categorie.query.order_by(Categorie.nom).all()

    if request.method == "POST":
        nouveau_total = request.form.get("nb_exemplaires", type=int) or livre.nb_exemplaires
        # Ajuste le nombre de disponibles proportionnellement au changement de stock total
        difference = nouveau_total - livre.nb_exemplaires
        livre.nb_disponibles = max(livre.nb_disponibles + difference, 0)
        livre.nb_exemplaires = nouveau_total

        livre.titre = request.form.get("titre", "").strip()
        livre.auteur = request.form.get("auteur", "").strip()
        livre.isbn = request.form.get("isbn", "").strip() or None
        livre.editeur = request.form.get("editeur", "").strip() or None
        livre.annee_publication = request.form.get("annee_publication", type=int)
        livre.categorie_id = request.form.get("categorie_id", type=int)

        db.session.commit()
        flash("Livre mis à jour avec succès.", "success")
        return redirect(url_for("livre.details", livre_id=livre.id))

    return render_template("livres/formulaire.html", livre=livre, categories=categories)


@livre_bp.route("/<int:livre_id>/supprimer", methods=["POST"])
@login_required
def supprimer(livre_id):
    livre = Livre.query.get_or_404(livre_id)

    if livre.emprunts:
        flash(
            "Impossible de supprimer ce livre : il possède un historique d'emprunts.",
            "danger",
        )
        return redirect(url_for("livre.details", livre_id=livre.id))

    db.session.delete(livre)
    db.session.commit()
    flash("Livre supprimé.", "success")
    return redirect(url_for("livre.liste"))


# ---------------------------------------------------------------------------
# Gestion des catégories
# ---------------------------------------------------------------------------

@livre_bp.route("/categories")
@login_required
def liste_categories():
    categories = Categorie.query.order_by(Categorie.nom).all()
    return render_template("livres/categories.html", categories=categories)


@livre_bp.route("/categories/ajouter", methods=["POST"])
@login_required
def ajouter_categorie():
    nom = request.form.get("nom", "").strip()
    description = request.form.get("description", "").strip() or None

    if not nom:
        flash("Le nom de la catégorie est obligatoire.", "danger")
    elif Categorie.query.filter_by(nom=nom).first():
        flash("Cette catégorie existe déjà.", "danger")
    else:
        db.session.add(Categorie(nom=nom, description=description))
        db.session.commit()
        flash("Catégorie ajoutée.", "success")

    return redirect(url_for("livre.liste_categories"))


@livre_bp.route("/categories/<int:categorie_id>/supprimer", methods=["POST"])
@login_required
def supprimer_categorie(categorie_id):
    categorie = Categorie.query.get_or_404(categorie_id)

    if categorie.livres:
        flash(
            "Impossible de supprimer cette catégorie : des livres y sont rattachés.",
            "danger",
        )
    else:
        db.session.delete(categorie)
        db.session.commit()
        flash("Catégorie supprimée.", "success")

    return redirect(url_for("livre.liste_categories"))
