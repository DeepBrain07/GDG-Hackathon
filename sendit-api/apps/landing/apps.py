# apps/landing/apps.py

from django.apps import AppConfig

class LandingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.landing'  # <--- This MUST match the folder path from root