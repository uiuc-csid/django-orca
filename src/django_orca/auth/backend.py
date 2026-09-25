from typing import Set

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django_orca.registry import registry
from django_orca.utils import get_roleclass, permission_to_string

from .checkers import has_permission
from .getters import get_userroles


class OrcaBackend(BaseBackend):
    def get_user_permissions(self, user_obj, obj=None) -> Set[str]:
        """
        Return the permissions, as "app_label.codename" strings, that the
        user's roles grant on "obj". These are exactly the permissions
        has_perm() allows for it, including inherited ones.

        Without "obj", return the permissions the user's roles grant on at
        least one object.
        """
        if user_obj.is_anonymous or not user_obj.is_active:
            return set()

        if obj is None:
            roles = {get_roleclass(ur.role_class) for ur in get_userroles(user_obj)}
            return {
                perm
                for role in roles
                # Roles for every model don't grant any permissions yet.
                if not role.all_models
                for perm in [*role.allow, *role.inherit_allow]
            }

        # Only the permissions some role grants, for the object's model or
        # the parents it inherits from, can be allowed.
        model = obj._meta.model
        content_types = ContentType.objects.get_for_models(
            model, *model._meta.get_parent_list()
        ).values()
        granted = {
            perm
            for role in registry.roles_map.values()
            for perm in [*role.allow, *role.inherit_allow]
        }
        candidates = {
            permission_to_string(perm)
            for perm in Permission.objects.filter(
                content_type__in=content_types
            ).select_related("content_type")
        } & granted
        return {perm for perm in candidates if has_permission(user_obj, perm, obj)}

    def get_all_permissions(self, user_obj, obj=None) -> Set[str]:
        return {
            *self.get_user_permissions(user_obj, obj=obj),
            *self.get_group_permissions(user_obj, obj=obj),
        }

    def has_perm(self, user_obj, perm, obj=None) -> bool:
        return has_permission(user_obj, perm, obj=obj)
