from typing import Type, TypeVar

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models

from ..exceptions import NotAllowed
from ..models import UserRole
from ..utils import check_my_model, get_roleclass


def get_user(role_class=None, obj=None):
    """
    Get the User instance attached to the object.
    Only one UserRole must exists and this relation
    must be unique=True.
    Returns None if there is no user attached
    to the object.
    """
    query = UserRole.objects.select_related("user").all()
    role = None

    if role_class:
        # All users who have "role_class" attached to any object.
        role = get_roleclass(role_class)
        query = query.filter(role_class=role.get_class_name())

    if obj:
        # All users who have any role attached to the object.
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)

    # Check if object belongs
    # to the role class.
    check_my_model(role, obj)

    # Looking for a role class using unique=True
    selected = list()
    for ur_obj in query:
        role = get_roleclass(ur_obj.role_class)
        if role.unique is True:
            selected.append(ur_obj.user)

    users_set = set(selected)
    if len(users_set) > 1:
        raise NotAllowed(
            "Multiple unique roles was found using "
            "the function get_user.  Use get_users "
            "instead."
        )
    if len(users_set) == 1:
        return selected[0]
    return None


def get_users(role_class=None, obj=None):
    """
    If "role_class" and "obj" is provided,
    returns a QuerySet of users who has
    this role class attached to the
    object.
    If only "role_class" is provided, returns
    a QuerySet of users who has this role
    class attached to any object.
    If neither "role_class" or "obj" are provided,
    returns all users of the project.
    """
    role = None
    kwargs = {}

    if role_class:
        # All users who have "role_class" attached to any object.
        role = get_roleclass(role_class)
        kwargs["roles__role_class"] = role.get_class_name()

    if obj:
        # All users who have any role attached to the object.
        ct_obj = ContentType.objects.get_for_model(obj)
        kwargs["roles__content_type"] = ct_obj.id
        kwargs["roles__object_id"] = obj.id

    # Check if object belongs
    # to the role class.
    check_my_model(role, obj)

    # Return as a distinct QuerySet.
    return get_user_model().objects.filter(**kwargs).distinct()


def get_objects(user, role_class=None, model=None):
    """
    Return the list of objects attached
    to a given user.
    If "role_class" is provided, only the objects
    which as registered in that role class will
    be returned.
    If "model" is provided, only the objects
    of that model will be returned.
    TODO: This seems to be an n+1 query
    """
    query = UserRole.objects.filter(user=user)
    role = None

    if role_class:
        # Filtering by role class.
        role = get_roleclass(role_class)
        query = query.filter(role_class=role.get_class_name())

    if model:
        # Filtering by model.
        ct_obj = ContentType.objects.get_for_model(model)
        query = query.filter(content_type=ct_obj.id)

    # Check if object belongs
    # to the role class.
    check_my_model(role, model)

    return [ur_obj.obj for ur_obj in query]


T = TypeVar("T", bound=models.Model)


def get_qs_for_user(user, model: Type[T], role_class=None) -> models.QuerySet[T]:
    # TODO: Include permission inheritance
    ct_obj = ContentType.objects.get_for_model(model)
    role_query = UserRole.objects.filter(user=user, content_type=ct_obj.id)

    if role_class:
        role_name = get_roleclass(role_class).get_class_name()
        role_query = role_query.filter(role_class=role_name)

    qs = model.objects.filter(id__in=models.Subquery(role_query.values("object_id")))
    return qs


def get_userroles(user, obj=None):
    """
    Return a QuerySet of UserRole objects associated to "user".
    If "obj" is provided, the QuerySet is filtered by "obj" as well.
    """
    query = UserRole.objects.filter(user=user)
    if obj:
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)

    return query


def get_user_role_string(user, obj=None):
    """
    Proxy method to be used when you sure that
    will have only one role class attached.
    """
    try:
        return get_user_roles_strings(user, obj)[0]
    except IndexError:
        return None


def get_user_roles_strings(user, obj=None):
    """
    Return a list of role classes associated to "user".
    If "obj" is provided, the list is filtered by "obj" as well.
    """
    query = UserRole.objects.filter(user=user)
    if obj:
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)

    # Transform the string representations into role classes and return as list
    return [get_roleclass(ur_obj.role_class) for ur_obj in query]


def get_permissions_from_roles(roles, clean=False):
    """
    roles: list or QuerySet of UserRole objects
    For given role(s), return a list of all allowed permissions. If clean=True,
    return the permissions without the Django app prefix.
    """
    role_classes = [get_roleclass(ur.role_class) for ur in roles]
    permissions_lists = [r.allow for r in role_classes]

    # Flatten permissions list
    all_permissions = list(
        set([item for sublist in permissions_lists for item in sublist])
    )

    if clean:
        # Remove the app prefix from all permissions
        all_permissions_clean = [s.split(".")[1] for s in all_permissions]
        return all_permissions_clean
    else:
        return all_permissions
