from django.db import models

from django_orca import shortcuts


class UserRoleMixin(models.Model):
    """Mixin to allow accessing role methods from a User object."""

    class Meta:
        abstract = True

    def has_role(self, role_class=None, obj=None):
        return shortcuts.has_role(self, role_class, obj)

    def assign_role(self, role_class, obj=None):
        return shortcuts.assign_role(self, role_class, obj)

    def remove_role(self, role_class=None, obj=None):
        return shortcuts.remove_role(self, role_class, obj)

    def get_objects(self, role_class=None, model=None):
        return shortcuts.get_objects(self, role_class, model)

    def get_objects_qs(self, model, role_class=None):
        return shortcuts.get_qs_for_user(self, model, role_class)
