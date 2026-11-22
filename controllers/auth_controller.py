"""
controllers/auth_controller.py
-------------------------------
Contrôleur gérant l'authentification (connexion / déconnexion), la gestion
des comptes utilisateurs et le tableau de bord principal de l'application.
"""

from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from models import db
from models.utilisateur import Utilisateur
from models.livre import Livre
from models.lecteur import Lecteur
from models.emprunt import Emprunt
from models.penalite import Penalite
from controllers.decorateurs import administrateur_requis

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Affiche et traite le formulaire de connexion."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        mot_de_passe = request.form.get("mot_de_passe", "")

        utilisateur = Utilisateur.query.filter_by(email=email).first()

        if utilisateur is None or not utilisateur.verifier_mot_de_passe(mot_de_passe):
            flash("Adresse e-mail ou mot de passe incorrect.", "danger")
            return redirect(url_for("auth.login"))

        if not utilisateur.actif:
            flash("Ce compte a été désactivé. Contactez un administrateur.", "danger")
            return redirect(url_for("auth.login"))

        login_user(utilisateur)
        flash(f"Bienvenue, {utilisateur.nom} !", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté avec succès.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/")
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    """Tableau de bord : indicateurs clés de l'activité de la bibliothèque."""
    nb_livres = Livre.query.count()
    nb_lecteurs = Lecteur.query.filter_by(actif=True).count()
    nb_emprunts_en_cours = Emprunt.query.filter(
        Emprunt.statut.in_(["en_cours", "en_retard"])
    ).count()
    nb_livres_disponibles = db.session.query(
        db.func.coalesce(db.func.sum(Livre.nb_disponibles), 0)
    ).scalar()

    emprunts_en_cours = Emprunt.query.filter(
        Emprunt.statut.in_(["en_cours", "en_retard"])
    ).all()
    nb_retards = sum(1 for e in emprunts_en_cours if e.est_en_retard)

    derniers_emprunts = (
        Emprunt.query.order_by(Emprunt.date_emprunt.desc()).limit(8).all()
    )

    return render_template(
        "dashboard.html",
        nb_livres=nb_livres,
        nb_lecteurs=nb_lecteurs,
        nb_emprunts_en_cours=nb_emprunts_en_cours,
        nb_livres_disponibles=nb_livres_disponibles,
        nb_retards=nb_retards,
        derniers_emprunts=derniers_emprunts,
        maintenant=datetime.utcnow(),
    )


# ---------------------------------------------------------------------------
# Gestion des comptes utilisateurs (réservée aux administrateurs)
# ---------------------------------------------------------------------------

@auth_bp.route("/utilisateurs")
@login_required
@administrateur_requis
def liste_utilisateurs():
    utilisateurs = Utilisateur.query.order_by(Utilisateur.nom).all()
    return render_template("utilisateurs/liste.html", utilisateurs=utilisateurs)


@auth_bp.route("/utilisateurs/ajouter", methods=["GET", "POST"])
@login_required
@administrateur_requis
def ajouter_utilisateur():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "bibliothecaire")
        mot_de_passe = request.form.get("mot_de_passe", "")

        if not nom or not email or not mot_de_passe:
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect(url_for("auth.ajouter_utilisateur"))

        if Utilisateur.query.filter_by(email=email).first():
            flash("Un compte existe déjà avec cet e-mail.", "danger")
            return redirect(url_for("auth.ajouter_utilisateur"))

        utilisateur = Utilisateur(nom=nom, email=email, role=role)
        utilisateur.set_password(mot_de_passe)
        db.session.add(utilisateur)
        db.session.commit()

        flash("Utilisateur créé avec succès.", "success")
        return redirect(url_for("auth.liste_utilisateurs"))

    return render_template("utilisateurs/formulaire.html", utilisateur=None)


@auth_bp.route("/utilisateurs/<int:utilisateur_id>/modifier", methods=["GET", "POST"])
@login_required
@administrateur_requis
def modifier_utilisateur(utilisateur_id):
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)

    if request.method == "POST":
        utilisateur.nom = request.form.get("nom", "").strip()
        utilisateur.email = request.form.get("email", "").strip().lower()
        utilisateur.role = request.form.get("role", utilisateur.role)
        utilisateur.actif = bool(request.form.get("actif"))

        nouveau_mot_de_passe = request.form.get("mot_de_passe", "")
        if nouveau_mot_de_passe:
            utilisateur.set_password(nouveau_mot_de_passe)

        db.session.commit()
        flash("Utilisateur mis à jour.", "success")
        return redirect(url_for("auth.liste_utilisateurs"))

    return render_template("utilisateurs/formulaire.html", utilisateur=utilisateur)


@auth_bp.route("/utilisateurs/<int:utilisateur_id>/supprimer", methods=["POST"])
@login_required
@administrateur_requis
def supprimer_utilisateur(utilisateur_id):
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)

    if utilisateur.id == current_user.id:
        flash("Vous ne pouvez pas supprimer votre propre compte.", "danger")
        return redirect(url_for("auth.liste_utilisateurs"))

    db.session.delete(utilisateur)
    db.session.commit()
    flash("Utilisateur supprimé.", "success")
    return redirect(url_for("auth.liste_utilisateurs"))


# ---------------------------------------------------------------------------
# Rapports et statistiques
# ---------------------------------------------------------------------------

@auth_bp.route("/rapports")
@login_required
def rapports():
    """Historique des emprunts, livres les plus empruntés, lecteurs les
    plus actifs, retards et pénalités."""

    livres_plus_empruntes = (
        db.session.query(
            Livre, db.func.count(Emprunt.id).label("nb_emprunts")
        )
        .join(Emprunt, Emprunt.livre_id == Livre.id)
        .group_by(Livre.id)
        .order_by(db.text("nb_emprunts DESC"))
        .limit(5)
        .all()
    )

    lecteurs_plus_actifs = (
        db.session.query(
            Lecteur, db.func.count(Emprunt.id).label("nb_emprunts")
        )
        .join(Emprunt, Emprunt.lecteur_id == Lecteur.id)
        .group_by(Lecteur.id)
        .order_by(db.text("nb_emprunts DESC"))
        .limit(5)
        .all()
    )

    penalites = Penalite.query.order_by(Penalite.date_creation.desc()).all()
    total_penalites = sum(p.montant for p in penalites)
    total_impaye = sum(p.montant for p in penalites if p.statut_paiement == "impayee")

    historique_emprunts = (
        Emprunt.query.order_by(Emprunt.date_emprunt.desc()).limit(50).all()
    )

    return render_template(
        "rapports.html",
        livres_plus_empruntes=livres_plus_empruntes,
        lecteurs_plus_actifs=lecteurs_plus_actifs,
        penalites=penalites,
        total_penalites=total_penalites,
        total_impaye=total_impaye,
        historique_emprunts=historique_emprunts,
    )
