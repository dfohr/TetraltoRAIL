from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """
        Import signals when the app is ready.
        This ensures signals are registered when Django starts.
        """
        import core.signals 