""" permissions shortcuts """

from .auth.checkers import has_permission, has_role
from .auth.getters import (
    get_objects,
    get_permissions_from_roles,
    get_qs_for_user,
    get_user,
    get_user_roles_strings,
    get_users,
)
from .auth.setters import (
    assign_permission,
    assign_role,
    assign_roles,
    remove_all,
    remove_role,
    remove_roles,
)

__all__ = [
    "get_user",
    "get_users",
    "get_objects",
    "get_qs_for_user",
    "get_user_roles_strings",
    "get_permissions_from_roles",
    "has_role",
    "has_permission",
    "assign_role",
    "assign_roles",
    "remove_role",
    "remove_roles",
    "remove_all",
    "assign_permission",
]
