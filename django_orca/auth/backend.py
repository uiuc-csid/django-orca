from django.contrib.auth.backends import BaseBackend

from .checkers import has_permission


class OrcaBackend(BaseBackend):
    # def get_user_permissions(self, user_obj, obj=None):
    #     return set()

    # def get_group_permissions(self, user_obj, obj=None):
    #     return set()

    def get_all_permissions(self, user_obj, obj=None):
        return {
            *self.get_user_permissions(user_obj, obj=obj),
            *self.get_group_permissions(user_obj, obj=obj),
        }

    def has_perm(self, user_obj, perm, obj=None):
        return has_permission(user_obj, perm, obj=obj)
