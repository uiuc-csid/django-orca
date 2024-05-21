import inspect
import logging
from typing import Optional, Type

from django.core.cache.backends.base import BaseCache

from django_orca.roles import Role

from .exceptions import ImproperlyConfigured, NotAllowed, ParentNotFound, RoleNotFound

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "orca"


def is_role(role_class):
    """Check if the argument is a valid Role class.

    This method DOES NOT check if the class is registered
    """
    from .roles import Role

    return (
        inspect.isclass(role_class)
        and issubclass(role_class, Role)
        and role_class != Role
    )


def get_config(key, default):
    """Get the dictionary "ORCA_SETTINGS" from the settings module.

    Return "default" if "key" is not present in the dictionary.
    """
    from django.conf import settings

    config_dict = getattr(settings, "ORCA_SETTINGS", None)
    if config_dict:
        if key in config_dict:
            return config_dict[key]
    return default


def get_roleclass(role_class) -> Type[Role]:
    """Get the role class signature by string or by itself."""
    from .registry import registry

    if role_class in registry.roles_map:
        return registry.roles_map[role_class]
    else:
        raise RoleNotFound("'%s' is not a registered role class." % role_class)


def string_to_permission(perm):
    """Transforms a string representation into a Permission instance."""
    from django.contrib.auth.models import Permission

    # Checking if the Permission instance
    # exists in the cache system.
    prefix = get_config("CACHE_PREFIX_KEY", CACHE_KEY_PREFIX)
    key = "{}-permission-{}".format(prefix, perm)
    perm_obj: Optional[Permission] = orca_cache().get(key)

    # If not, creates the query to
    # get the Permission instance
    # and store into the cache.
    if perm_obj is None:
        app, codename = perm.split(".")
        perm_obj = (
            # TODO(joshuata): This is an eager fetch of a likely cached object
            Permission.objects.select_related("content_type")
            .filter(content_type__app_label=app, codename=codename)
            .get()
        )
        orca_cache().set(key, perm_obj)

    return perm_obj


def permission_to_string(perm):
    """Transforms a Permission instance into a string representation."""
    app_label = perm.content_type.app_label
    codename = perm.codename
    return "%s.%s" % (app_label, codename)


def get_permissions_list(models_list):
    """Given a list of Model instances or a Model classes, return all Permissions related to it."""
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    ct_list = ContentType.objects.get_for_models(*models_list)
    ct_ids = [ct.id for cls, ct in ct_list.items()]

    # TODO(joshuata): This performs multiple database queries
    return list(Permission.objects.filter(content_type_id__in=ct_ids))


def get_parents(model):
    """Return the list of instances refered as "parents" of a given model instance."""
    result = list()
    options = getattr(model, "RoleOptions", None)
    if options:
        parents_list = getattr(options, "permission_parents", None)
        if parents_list:
            for parent in parents_list:
                field = getattr(model, parent, False)
                if field is False:
                    # Field does not exist.
                    raise ParentNotFound(
                        'The field "%s" was not found in the '
                        'model "%s".' % (parent, str(model))
                    )
                elif field is not None:
                    # Only getting non-null parents.
                    result.append(field)
    return result


def is_unique_together(model):
    """Return True if the model does not accept multiple roles attached to it using the user instance."""
    options = getattr(model, "RoleOptions", None)
    if options:
        unique = getattr(options, "unique_together", None)
        if unique:
            if isinstance(unique, bool):
                return unique
            raise ImproperlyConfigured(
                'The field "unique_together" of "%s" must '
                "be a bool value." % (str(model))
            )
    return False


def inherit_check(role_s, permission):
    """Check if the role class has the following permission in inherit mode."""
    from .roles import ALLOW_MODE

    role = get_roleclass(role_s)
    if role.inherit is True:
        if role.get_inherit_mode() == ALLOW_MODE:
            return True if permission in role.inherit_allow else False
        return False if permission in role.inherit_deny else True
    return False


def cleanup_handler(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """This function is attached to the post_delete signal of all models of Django. Used to remove useless role instances and permissions."""
    from django.contrib.contenttypes.models import ContentType

    from .models import UserRole

    ct_obj = ContentType.objects.get_for_model(instance)
    ur_list = UserRole.objects.filter(content_type=ct_obj.id, object_id=instance.id)

    for ur_obj in ur_list:
        # Cleaning the cache system.
        delete_from_cache(ur_obj.user, instance)
        ur_obj.delete()


def register_cleanup():
    """Register the function "cleanup_handler" to all models in the project."""
    from django.apps import apps
    from django.db.models.signals import post_delete

    from .models import RolePermission, UserRole

    ignore = [UserRole, RolePermission]
    for model in apps.get_models():
        if model not in ignore and hasattr(model, "id"):
            post_delete.connect(cleanup_handler, sender=model, dispatch_uid=str(model))


def check_my_model(role, obj):
    """If both are provided, check if obj (instance or model class) belongs to the role class."""
    if role and obj and not role.is_my_model(obj):
        model_name = obj._meta.model  # pylint: disable=protected-access
        raise NotAllowed(
            'The model "%s" does not belong to the Role "%s"'
            "." % (model_name, role.get_verbose_name())
        )


##############################
###      CACHE UTILS       ###
##############################


def orca_cache() -> BaseCache:
    """Proxy method used to get the cache object belonging to orca."""
    from django.core.cache import caches

    return caches[
        get_config("CACHE", "default")
    ]  # TODO(joshuata): This will fully clear the cache. Might not be what we want. Can we scope this?


def generate_cache_key(user, obj, any_object):
    """Generate a md5 digest based on the string representation of the user and the object passed via arguments."""
    from hashlib import md5

    key = md5()
    str_key = str(user.__class__) + str(user) + str(user.id)
    if obj:
        str_key += str(obj.__class__) + str(obj) + str(obj.id)
    elif any_object:
        str_key += "any"

    key.update(str_key.encode("utf-8"))
    prefix = get_config("CACHE_PREFIX_KEY", CACHE_KEY_PREFIX)
    return "{}-userrole-{}".format(prefix, key.hexdigest())


def delete_from_cache(user, obj):
    """Delete all permissions data from the cache about the user and the object passed via arguments."""
    key = generate_cache_key(user, obj, any_object=False)
    orca_cache().delete(key)

    key = generate_cache_key(user, obj=None, any_object=True)
    orca_cache().delete(key)


def get_from_cache(user, obj, any_object):
    """Get all permissions data about the user and the object passed via arguments e store it in the Django cache system."""
    from django.contrib.contenttypes.models import ContentType

    from .models import UserRole

    # Key preparation.
    key = generate_cache_key(user, obj, any_object)

    # Check for the cached data.
    data = orca_cache().get(key)
    if data is None:
        query = UserRole.objects.prefetch_related("accesses").filter(user=user)

        # Filtering by object.
        if obj:
            ct_obj = ContentType.objects.get_for_model(obj)
            query = query.filter(content_type=ct_obj.id).filter(object_id=obj.id)
        elif not any_object:
            query = query.filter(content_type__isnull=True).filter(
                object_id__isnull=True
            )

        # Getting only the required values.
        query = query.values_list(
            "role_class", "accesses__permission", "accesses__access"
        )

        # Transform the query result into
        # a dictionary.
        data = dict()
        for item in query:
            perms_list = data.get(item[0], [])
            if item[0] and item[1]:
                perms_list.append((item[1], item[2]))
            data[item[0]] = perms_list

        # Ordering the tuple by their Role Ranking values.
        data = sorted(data.items(), key=lambda role: get_roleclass(role[0]).ranking)

        # Now, we get only the data from the
        # first role class found.
        data = data[0] if data else ()

        # Set the data to the cache.
        orca_cache().set(key, data)

    return data
