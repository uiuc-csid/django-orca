from typing import Optional, Type

from django.contrib.auth.models import AnonymousUser

from django_orca.auth.getters import get_perm_qs_for_user, get_userroles
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


def has_permission(user, permission, obj=None, any_object=False) -> bool:
    """
    Return True if the "user" has the "permission".
    """
    if isinstance(user, AnonymousUser):
        return False

    # We do not support any_object yet
    if any_object:
        raise NotImplementedError("We do not support any_object yet")

    if obj is None:
        return False

    return (
        get_perm_qs_for_user(user, obj._meta.model, permission)
        .filter(id=obj.id)
        .exists()
    )
