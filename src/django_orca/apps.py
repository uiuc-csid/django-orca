from types import ModuleType

from django.apps import AppConfig


class OrcaConfig(AppConfig):
    name = "django_orca"
    default_auto_field = "django.db.models.AutoField"
    verbose_name = "Object-based Role Control and Authorization"
    default = True
    module: ModuleType

    def ready(self):
        from django_orca.registry import autodiscover
        from django_orca.utils import register_cleanup

        autodiscover()
        register_cleanup()
