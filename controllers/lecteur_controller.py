"""
controllers/lecteur_controller.py
-----------------------------------
Contrôleur gérant les lecteurs (abonnés) de la bibliothèque : inscription,
consultation, modification, désactivation/suppression et historique
des emprunts d'un lecteur donné.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from models import db
from models.lecteur import Lecteur
from models.emprunt import Emprunt

lecteur_bp = Blueprint("lecteur", __name__, url_prefix="/lecteurs")


@lecteur_bp.route("/")
@login_required
def liste():
    recherche = request.args.get("q", "").strip()

    requete = Lecteur.query
    if recherche:
        motif = f"%{recherche}%"
        requete = requete.filter(
            db.or_(Lecteur.nom.ilike(motif), Lecteur.prenom.ilike(motif), Lecteur.email.ilike(motif))
        )

    lecteurs = requete.order_by(Lecteur.nom).all()
    return render_template("lecteurs/liste.html", lecteurs=lecteurs, recherche=recherche)


@lecteur_bp.route("/<int:lecteur_id>")
@login_required
def details(lecteur_id):
    """Fiche d'un lecteur avec son historique d'emprunts."""
    lecteur = Lecteur.query.get_or_404(lecteur_id)
    emprunts = (
        Emprunt.query.filter_by(lecteur_id=lecteur.id)
        .order_by(Emprunt.date_emprunt.desc())
        .all()
    )
    return render_template("lecteurs/details.html", lecteur=lecteur, emprunts=emprunts)


@lecteur_bp.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        prenom = request.form.get("prenom", "").strip()
        email = request.form.get("email", "").strip().lower() or None
        telephone = request.form.get("telephone", "").strip() or None
        adresse = request.form.get("adresse", "").strip() or None

        if not nom or not prenom:
            flash("Le nom et le prénom sont obligatoires.", "danger")
            return redirect(url_for("lecteur.ajouter"))

        lecteur = Lecteur(
            nom=nom, prenom=prenom, email=email, telephone=telephone, adresse=adresse
        )
        db.session.add(lecteur)
        db.session.commit()

        flash("Lecteur inscrit avec succès.", "success")
        return redirect(url_for("lecteur.liste"))

    return render_template("lecteurs/formulaire.html", lecteur=None)


@lecteur_bp.route("/<int:lecteur_id>/modifier", methods=["GET", "POST"])
@login_required
def modifier(lecteur_id):
    lecteur = Lecteur.query.get_or_404(lecteur_id)

    if request.method == "POST":
        lecteur.nom = request.form.get("nom", "").strip()
        lecteur.prenom = request.form.get("prenom", "").strip()
        lecteur.email = request.form.get("email", "").strip().lower() or None
        lecteur.telephone = request.form.get("telephone", "").strip() or None
        lecteur.adresse = request.form.get("adresse", "").strip() or None
        lecteur.actif = bool(request.form.get("actif"))

        db.session.commit()
        flash("Informations du lecteur mises à jour.", "success")
        return redirect(url_for("lecteur.details", lecteur_id=lecteur.id))

    return render_template("lecteurs/formulaire.html", lecteur=lecteur)


@lecteur_bp.route("/<int:lecteur_id>/desactiver", methods=["POST"])
@login_required
def desactiver(lecteur_id):
    """Désactive un lecteur plutôt que de le supprimer, afin de conserver
    son historique d'emprunts."""
    lecteur = Lecteur.query.get_or_404(lecteur_id)
    lecteur.actif = False
    db.session.commit()
    flash("Lecteur désactivé.", "success")
    return redirect(url_for("lecteur.details", lecteur_id=lecteur.id))


@lecteur_bp.route("/<int:lecteur_id>/supprimer", methods=["POST"])
@login_required
def supprimer(lecteur_id):
    lecteur = Lecteur.query.get_or_404(lecteur_id)

    if lecteur.emprunts:
        flash(
            "Impossible de supprimer ce lecteur : il possède un historique d'emprunts. "
            "Vous pouvez le désactiver à la place.",
            "danger",
        )
        return redirect(url_for("lecteur.details", lecteur_id=lecteur.id))

    db.session.delete(lecteur)
    db.session.commit()
    flash("Lecteur supprimé.", "success")
    return redirect(url_for("lecteur.liste"))
