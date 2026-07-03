from django.apps import AppConfig


class InventarioAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inventario_app"

    def ready(self):
        import inventario_app.signals
