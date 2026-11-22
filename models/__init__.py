"""
models/__init__.py
-------------------
Initialise l'instance partagée de SQLAlchemy (le "M" de MVC) ainsi que
celle de Flask-Login, utilisées par tous les modèles et par app.py.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
