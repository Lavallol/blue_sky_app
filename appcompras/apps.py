from django.apps import AppConfig


class AppcomprasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appcompras'

    def ready(self):
        """
        Cargamos el admin de desarrollo de factura sin afectar al admin real.
        Si el archivo no existe o tiene errores, Django seguirá arrancando
        porque lo envolvemos en un try/except silencioso.
        """
        try:
            from . import admin_factura_dev  # noqa
        except Exception:
            # No hacemos nada: el admin real sigue funcionando
            pass

