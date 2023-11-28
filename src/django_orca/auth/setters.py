from typing import List, Optional, Type

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.contenttypes.models import ContentType

from django_orca.roles import Role

from ..exceptions import InvalidRoleAssignment
from ..models import UserRole
from ..utils import check_my_model, delete_from_cache, get_roleclass, is_unique_together
from .checkers import has_role
from .getters import get_user_roles_strings, get_userroles, get_users

RoleQ = Optional[Type[Role]]


def assign_role(user, role_class: Type[Role], obj=None):
    if not has_role(user, role_class=role_class, obj=obj):
        assign_roles([user], role_class, obj)


def assign_roles(users_list: List[AbstractBaseUser], role_class: Type[Role], obj=None):
    # TODO(joshuata): There should be a flag to ignore assigning a role twice
    users_set = set(users_list)
    role = get_roleclass(role_class)
    name = role.get_verbose_name()

    # Check if object belongs to the role class.
    check_my_model(role, obj)

    # If no object is provided but the role needs specific models.
    if not obj and not role.all_models:
        raise InvalidRoleAssignment(
            'The role "%s" must be assigned with a object.' % name
        )

    # If a object is provided but the role does not needs a object.
    if obj and role.all_models:
        raise InvalidRoleAssignment(
            'The role "%s" must not be assigned with a object.' % name
        )

    # Check if the model accepts multiple roles
    # attached using the same User instance.
    if obj and is_unique_together(obj):
        for user in users_set:
            has_user = get_user_roles_strings(user=user, obj=obj)
            if has_user:
                raise InvalidRoleAssignment(
                    'The user "%s" already has a role attached '
                    'to the object "%s".' % (user, obj)
                )

    if role.unique is True:
        # If the role is marked as unique but multiple users are provided.
        if len(users_list) > 1:
            raise InvalidRoleAssignment(
                'Multiple users were provided using "%s", '
                "but it is marked as unique." % name
            )

        # If the role is marked as unique but already has an user attached.
        has_user = get_users(role_class=role, obj=obj)
        if has_user:
            raise InvalidRoleAssignment(
                'The object "%s" already has a "%s" attached '
                "and it is marked as unique." % (obj, name)
            )

    for user in users_set:
        if obj:
            UserRole.objects.get_or_create(
                role_class=role.get_class_name(),
                user=user,
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
            )
        else:
            UserRole.objects.get_or_create(role_class=role.get_class_name(), user=user)

        # Cleaning the cache system.
        delete_from_cache(user, obj)


def remove_role(user, role_class=None, obj=None):
    """Proxy method to be used for one User instance."""
    remove_roles([user], role_class, obj)


def remove_roles(users_list, role_class=None, obj=None):
    """Delete all RolePermission objects in the database referencing the followling role_class to the user.

    If "obj" is provided, only the instances refencing this object will be deleted.
    """
    query = get_userroles(users_list, role_class=role_class, obj=obj)

    # Cleaning the cache system.
    for user in users_list:
        delete_from_cache(user, obj)

    # Cleaning the database.
    query.delete()
