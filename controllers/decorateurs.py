"""
controllers/decorateurs.py
---------------------------
Décorateurs utilitaires partagés par les contrôleurs, notamment pour la
protection des routes selon le rôle de l'utilisateur connecté
(administrateur / bibliothécaire).
"""

from functools import wraps
from flask import abort
from flask_login import current_user


def administrateur_requis(fonction):
    """Restreint l'accès à une route aux seuls administrateurs."""

    @wraps(fonction)
    def decoree(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.est_administrateur:
            abort(403)
        return fonction(*args, **kwargs)

    return decoree
