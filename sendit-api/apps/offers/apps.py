from django.apps import AppConfig

class OffersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.offers' # This must match the folder path

    def ready(self):
        # This tells Django to start listening for Proposal/Bid signals
        import apps.offers.signals