from typing import Set

from django.contrib.auth.backends import BaseBackend
from django.contrib.contenttypes.models import ContentType

from django_orca.models import RolePermission

from .checkers import has_permission


class OrcaBackend(BaseBackend):
    def get_user_permissions(self, user_obj, obj=None) -> Set:
        query = RolePermission.objects.filter(role__user=user_obj)
        if obj:
            ct_obj = ContentType.objects.get_for_model(obj)
            query = query.filter(role__content_type=ct_obj.id, role__object_id=obj.id)

        allows = set([rp.permission for rp in query if rp.access])
        return allows.difference([rp.permission for rp in query if not rp.access])

    def get_all_permissions(self, user_obj, obj=None):
        return {
            *self.get_user_permissions(user_obj, obj=obj),
            *self.get_group_permissions(user_obj, obj=obj),
        }

    def has_perm(self, user_obj, perm, obj=None):
        return has_permission(user_obj, perm, obj=obj)
