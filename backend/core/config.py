# backend/core/config.py
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # Utilisation d'une variable d'environnement
SESSION_MAX_AGE = 300  # Durée du token de session en secondes (5 minutes)
