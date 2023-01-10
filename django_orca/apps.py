from types import ModuleType

from django.apps import AppConfig

from .utils import register_cleanup


class OrcaConfig(AppConfig):
    name = "django_orca"
    default_auto_field = "django.db.models.AutoField"
    verbose_name = "Object-based Role Control and Authorization"
    default = True
    module: ModuleType

    def ready(self):
        self.module.autodiscover()
        register_cleanup()
