from django.apps import AppConfig

class InfosettingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "infosetting"

    def ready(self):
        from . import signals
