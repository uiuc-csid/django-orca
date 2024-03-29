from itertools import groupby
from typing import Any, Iterable, List, Optional, Type, TypeVar, Union

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_orca.registry import registry
from django_orca.roles import Role

from ..models import UserRole
from ..utils import check_my_model, get_roleclass

RoleQ = Optional[Type[Role]]
ModelQ = Optional[Type[models.Model]]
T = TypeVar("T", bound=models.Model)
T2 = TypeVar("T2", bound=models.Model)


def get_users(
    role_class: RoleQ = None, obj: Any = None
) -> models.QuerySet[AbstractBaseUser]:
    """
    If "role_class" and "obj" is provided, returns a QuerySet of users who has this role class attached to the object.
    If only "role_class" is provided, returns a QuerySet of users who has this role class attached to any object.
    If neither "role_class" or "obj" are provided, returns all users of the project.
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


def get_objects(user, role_class: RoleQ = None, model=None) -> List[Any]:
    """
    Return the list of objects attached to a given user.
    If "role_class" is provided, only the objects which as registered in that role class will be returned.
    If "model" is provided, only the objects of that model will be returned.
    """
    if model:
        return list(get_qs_for_user(user, model=model, role_class=role_class))
    else:
        query = get_userroles(user, role_class=role_class, model_class=model).values(
            "content_type", "object_id"
        )

        objs: List[models.Model] = []
        for content_type_id, group in groupby(query, lambda obj: obj["content_type"]):
            content_type = ContentType.objects.get_for_id(content_type_id)
            ids = [obj["object_id"] for obj in group]
            objs.extend(content_type.model_class().objects.filter(id__in=ids))

        return objs


def get_qs_for_user(
    user, model: Type[T], role_class: RoleQ = None
) -> models.QuerySet[T]:
    # TODO: Include permission inheritance
    ct_obj = ContentType.objects.get_for_model(model)
    role_query = UserRole.objects.filter(user=user, content_type=ct_obj.id)

    if role_class:
        role_name = get_roleclass(role_class).get_class_name()
        role_query = role_query.filter(role_class=role_name)

    qs = model.objects.filter(id__in=models.Subquery(role_query.values("object_id")))
    return qs


def get_objects_for_role(
    model: Type[T],
    role_class: Type[Role],
    permission: str,
    userrole_qs,
    parent_model: Optional[T] = None,
) -> models.QuerySet[T]:
    qs = model.objects.none()
    named_role_qs = userrole_qs.filter(
        role_class=get_roleclass(role_class).get_class_name()
    )

    if (
        role_class.all_models
        or (not parent_model and model in role_class.models)
        or (parent_model and parent_model in role_class.models)
    ) and permission in role_class.allow:
        if parent_model:
            ct_objs = ContentType.objects.get_for_models(model, parent_model).values()
            local_role_qs = named_role_qs.filter(content_type__in=ct_objs)
            path_to_id = model._meta.get_ancestor_link(parent_model).attname
            filter_kwargs = {
                f"{path_to_id}__in": models.Subquery(local_role_qs.values("object_id"))
            }
        else:
            ct_obj = ContentType.objects.get_for_model(model)
            local_role_qs = named_role_qs.filter(content_type=ct_obj)
            filter_kwargs = {
                "id__in": models.Subquery(local_role_qs.values("object_id"))
            }
        qs |= model.objects.filter(**filter_kwargs)

    if permission in role_class.inherit_allow:
        parents = registry.get_perm_inheritance_tree(model)
        for attname, parent in parents.items():
            # Check whether there is a role with allow_inherit
            if role_class.all_models or parent in role_class.models:
                parent_ct = ContentType.objects.get_for_model(parent)
                local_role_qs = named_role_qs.filter(content_type=parent_ct)
                kwargs = {
                    f"{attname}__in": models.Subquery(local_role_qs.values("object_id"))
                }
                qs |= model.objects.filter(**kwargs)

    return qs


def get_perm_qs_for_user(user, model: Type[T], permission: str) -> models.QuerySet[T]:
    qs = model.objects.none()
    userroles = UserRole.objects.filter(user=user)

    for role in registry.get_roles_for_perm(permission):
        qs |= get_objects_for_role(model, role, permission, userroles)
        if role.follow_model_inheritance:
            for parent in model._meta.get_parent_list():
                qs |= get_objects_for_role(
                    model, role, permission, userroles, parent_model=parent
                )

    return qs


def get_userroles(
    user: Union[AbstractBaseUser, Iterable[AbstractBaseUser]],
    role_class: RoleQ = None,
    obj: Optional[models.Model] = None,
    model_class: ModelQ = None,
) -> models.QuerySet[UserRole]:
    """
    Return a QuerySet of UserRole objects associated to "user".
    If "obj" is provided, the QuerySet is filtered by "obj" as well.
    """
    query = UserRole.objects.all()
    if isinstance(user, AbstractBaseUser):
        query = query.filter(user=user)
    else:
        query = query.filter(user__in=user)

    if role_class:
        role = get_roleclass(role_class)
        query = query.filter(role_class=role.get_class_name())
        if model_class:
            check_my_model(role, model_class)
        else:
            check_my_model(role, obj)

    if model_class:
        ct_obj = ContentType.objects.get_for_model(model_class)
        query = query.filter(content_type=ct_obj.id)

    if obj:
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)

    return query


def get_user_roles_strings(user, obj: Optional[models.Model] = None):
    """
    Return a list of role classes associated to "user".
    If "obj" is provided, the list is filtered by "obj" as well.
    """
    # Transform the string representations into role classes and return as list
    return [get_roleclass(ur_obj.role_class) for ur_obj in get_userroles(user, obj=obj)]


def get_permissions_from_roles(roles: Iterable[UserRole], clean=False) -> List:
    """
    roles: list or QuerySet of UserRole objects
    For given role(s), return a list of all allowed permissions.
    If clean=True, return the permissions without the Django app prefix.
    """
    role_classes = [get_roleclass(ur.role_class) for ur in roles]
    permissions_lists = [r.allow for r in role_classes]

    # Flatten permissions list
    all_permissions = list(
        set([item for sublist in permissions_lists for item in sublist])
    )

    if clean:
        # Remove the app prefix from all permissions
        return [s.split(".")[1] for s in all_permissions]
    else:
        return all_permissions
