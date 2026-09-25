from typing import Optional, Type

from django.contrib.auth.models import AnonymousUser

from django_orca.auth.getters import get_perm_qs_for_user, get_userroles
from django_orca.registry import registry
from django_orca.roles import Role

RoleQ = Optional[Type[Role]]


def has_role(user, role_class: RoleQ = None, obj=None) -> bool:
    """
    Check if the "user" has any role attached to them.

    If "role_class" is provided, only instances of the role class will be counted.
    If "obj" is provided, the search is refined to look only at that object.
    """
    if isinstance(user, AnonymousUser):
        return False
    else:
        return get_userroles(user, role_class=role_class, obj=obj).exists()


def has_global_permission(user, permission) -> bool:
    """
    Return True if one of the user's roles for every model (all_models = True)
    grants "permission". Those roles are assigned without an object.
    """
    role_names = [
        role.get_class_name()
        for role in registry.get_roles_for_perm(permission)
        if role.all_models and permission in role.allow
    ]
    return (
        get_userroles(user)
        .filter(role_class__in=role_names, content_type__isnull=True)
        .exists()
    )


def has_permission(user, permission, obj=None, any_object=False) -> bool:
    """
    Return True if the "user" has the "permission".
    Inactive users have no permissions, as with Django's own backend.
    """
    if isinstance(user, AnonymousUser) or not user.is_active:
        return False

    # We do not support any_object yet
    if any_object:
        raise NotImplementedError("We do not support any_object yet")

    if obj is None:
        return has_global_permission(user, permission)

    return (
        get_perm_qs_for_user(user, obj._meta.model, permission)
        .filter(pk=obj.pk)
        .exists()
    )
