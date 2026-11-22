"""
controllers/emprunt_controller.py
-----------------------------------
Contrôleur gérant le cœur métier de l'application :
- Enregistrement d'un emprunt (avec vérification de la disponibilité du stock)
- Enregistrement d'un retour (avec mise à jour du stock et calcul du retard)
- Détection des retards et calcul automatique des pénalités

Règles appliquées (voir config.py) :
- DUREE_EMPRUNT_JOURS : délai accordé par défaut pour un emprunt
- PENALITE_PAR_JOUR   : montant de la pénalité appliqué par jour de retard
"""

from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from models import db
from models.emprunt import Emprunt
from models.livre import Livre
from models.lecteur import Lecteur
from models.penalite import Penalite

emprunt_bp = Blueprint("emprunt", __name__, url_prefix="/emprunts")


def _actualiser_statuts_retard():
    """Met à jour le statut des emprunts en cours dont la date limite est
    dépassée, afin que les retards soient toujours reflétés avant tout
    affichage de la liste des emprunts."""
    emprunts_en_cours = Emprunt.query.filter_by(statut="en_cours").all()
    for emprunt in emprunts_en_cours:
        if emprunt.est_en_retard:
            emprunt.statut = "en_retard"
    db.session.commit()


@emprunt_bp.route("/")
@login_required
def liste():
    _actualiser_statuts_retard()

    statut = request.args.get("statut", "").strip()
    requete = Emprunt.query

    if statut:
        requete = requete.filter_by(statut=statut)

    emprunts = requete.order_by(Emprunt.date_emprunt.desc()).all()
    return render_template("emprunts/liste.html", emprunts=emprunts, statut=statut)


@emprunt_bp.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    livres_disponibles = Livre.query.filter(Livre.nb_disponibles > 0).order_by(Livre.titre).all()
    lecteurs_actifs = Lecteur.query.filter_by(actif=True).order_by(Lecteur.nom).all()

    if request.method == "POST":
        livre_id = request.form.get("livre_id", type=int)
        lecteur_id = request.form.get("lecteur_id", type=int)
        duree_jours = request.form.get(
            "duree_jours", type=int
        ) or current_app.config["DUREE_EMPRUNT_JOURS"]

        livre = Livre.query.get_or_404(livre_id)
        lecteur = Lecteur.query.get_or_404(lecteur_id)

        # Règle métier essentielle : empêcher un emprunt si le stock
        # disponible est insuffisant.
        if livre.nb_disponibles <= 0:
            flash(
                f"Emprunt impossible : aucun exemplaire disponible pour « {livre.titre} ».",
                "danger",
            )
            return redirect(url_for("emprunt.ajouter"))

        if not lecteur.actif:
            flash("Ce lecteur est désactivé et ne peut pas emprunter de livre.", "danger")
            return redirect(url_for("emprunt.ajouter"))

        maintenant = datetime.utcnow()
        emprunt = Emprunt(
            livre_id=livre.id,
            lecteur_id=lecteur.id,
            utilisateur_id=current_user.id,
            date_emprunt=maintenant,
            date_limite=maintenant + timedelta(days=duree_jours),
            statut="en_cours",
        )

        # Mise à jour immédiate du stock disponible
        livre.nb_disponibles -= 1

        db.session.add(emprunt)
        db.session.commit()

        flash(
            f"Emprunt enregistré : « {livre.titre} » pour {lecteur.nom_complet}.",
            "success",
        )
        return redirect(url_for("emprunt.liste"))

    return render_template(
        "emprunts/formulaire.html",
        livres=livres_disponibles,
        lecteurs=lecteurs_actifs,
        duree_defaut=current_app.config["DUREE_EMPRUNT_JOURS"],
    )


@emprunt_bp.route("/<int:emprunt_id>")
@login_required
def details(emprunt_id):
    emprunt = Emprunt.query.get_or_404(emprunt_id)
    return render_template("emprunts/details.html", emprunt=emprunt)


@emprunt_bp.route("/<int:emprunt_id>/retour", methods=["POST"])
@login_required
def retour(emprunt_id):
    """Enregistre le retour d'un livre : actualise le stock disponible,
    vérifie le retard et calcule automatiquement la pénalité éventuelle."""
    emprunt = Emprunt.query.get_or_404(emprunt_id)

    if emprunt.statut == "retourne":
        flash("Ce livre a déjà été rendu.", "info")
        return redirect(url_for("emprunt.details", emprunt_id=emprunt.id))

    maintenant = datetime.utcnow()
    emprunt.date_retour_effective = maintenant
    emprunt.statut = "retourne"

    # Actualisation automatique du stock disponible
    livre = emprunt.livre
    livre.nb_disponibles = min(livre.nb_disponibles + 1, livre.nb_exemplaires)

    # Vérification du retard et calcul de la pénalité
    jours_retard = max((maintenant - emprunt.date_limite).days, 0)

    if jours_retard > 0:
        montant = jours_retard * current_app.config["PENALITE_PAR_JOUR"]
        penalite = Penalite(
            emprunt_id=emprunt.id,
            montant=montant,
            jours_de_retard=jours_retard,
            statut_paiement="impayee",
        )
        db.session.add(penalite)
        flash(
            f"Retour enregistré avec {jours_retard} jour(s) de retard. "
            f"Pénalité calculée : {montant:.2f}.",
            "warning",
        )
    else:
        flash("Retour enregistré dans les délais. Aucune pénalité.", "success")

    db.session.commit()
    return redirect(url_for("emprunt.details", emprunt_id=emprunt.id))


# ---------------------------------------------------------------------------
# Gestion des pénalités
# ---------------------------------------------------------------------------

@emprunt_bp.route("/penalites")
@login_required
def liste_penalites():
    penalites = Penalite.query.order_by(Penalite.date_creation.desc()).all()
    return render_template("emprunts/penalites.html", penalites=penalites)


@emprunt_bp.route("/penalites/<int:penalite_id>/payer", methods=["POST"])
@login_required
def payer_penalite(penalite_id):
    penalite = Penalite.query.get_or_404(penalite_id)
    penalite.statut_paiement = "payee"
    penalite.date_paiement = datetime.utcnow()
    db.session.commit()
    flash("Pénalité marquée comme payée.", "success")
    return redirect(url_for("emprunt.liste_penalites"))
