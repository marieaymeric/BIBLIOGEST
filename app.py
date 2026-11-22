"""
app.py
------
Point d'entrée de l'application BiblioGest.

Ce fichier assemble l'application Flask selon le patron MVC :
- Configure l'application et la base de données (config.py, models/)
- Initialise Flask-Login pour l'authentification
- Enregistre les Blueprints (Contrôleurs) sur l'application
- Fournit la commande CLI "init-db" pour créer les tables et un compte
  administrateur initial.
"""

import os

from flask import Flask, render_template

from config import config_by_name
from models import db, login_manager
from models.utilisateur import Utilisateur

from controllers.auth_controller import auth_bp
from controllers.livre_controller import livre_bp
from controllers.lecteur_controller import lecteur_bp
from controllers.emprunt_controller import emprunt_bp


def create_app(nom_config=None):
    """Fabrique applicative (application factory) : permet de créer
    plusieurs instances de l'application avec des configurations
    différentes (développement, production, tests)."""

    nom_config = nom_config or os.environ.get("FLASK_ENV", "development")

    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="static",
    )
    app.config.from_object(config_by_name.get(nom_config, config_by_name["development"]))

    # --- Initialisation des extensions ---
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def charger_utilisateur(utilisateur_id):
        return Utilisateur.query.get(int(utilisateur_id))

    # --- Enregistrement des contrôleurs (Blueprints) ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(livre_bp)
    app.register_blueprint(lecteur_bp)
    app.register_blueprint(emprunt_bp)

    # --- Gestion des erreurs HTTP ---
    @app.errorhandler(403)
    def erreur_403(_erreur):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def erreur_404(_erreur):
        return render_template("errors/404.html"), 404

    # --- Commandes CLI utilitaires ---
    @app.cli.command("init-db")
    def init_db():
        """Crée toutes les tables de la base de données."""
        with app.app_context():
            db.create_all()
        print("Base de données initialisée (tables créées).")

    @app.cli.command("create-admin")
    def create_admin():
        """Crée un compte administrateur par défaut si aucun n'existe."""
        with app.app_context():
            if Utilisateur.query.filter_by(role="administrateur").first():
                print("Un administrateur existe déjà.")
                return

            admin = Utilisateur(
                nom="Administrateur",
                email="admin@bibliogest.local",
                role="administrateur",
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Administrateur créé : admin@bibliogest.local / admin123")
            print("Pensez à changer ce mot de passe dès la première connexion.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True))
