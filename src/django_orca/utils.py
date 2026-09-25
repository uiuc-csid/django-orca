import inspect
import logging
import time
from typing import Optional, Type, Union

from django.core.cache.backends.base import BaseCache
from django.db import models
from django.db.models.functions import Cast, Replace

from django_orca.roles import Role

from .exceptions import ImproperlyConfigured, NotAllowed, RoleNotFound

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "orca"
# Orca entries always expire, so keys retired by clear_cache() are freed
# even when the cache itself has no default timeout.
CACHE_TIMEOUT = 300


def is_role(role_class):
    """
    Check if the argument is a valid Role class.
    This method DOES NOT check if the class is registered
    """
    from .roles import Role

    return (
        inspect.isclass(role_class)
        and issubclass(role_class, Role)
        and role_class != Role
    )


def get_config(key, default):
    """
    Get the dictionary "ORCA_SETTINGS" from the settings module.
    Return "default" if "key" is not present in the dictionary.
    """
    from django.conf import settings

    config_dict = getattr(settings, "ORCA_SETTINGS", None)
    if config_dict:
        if key in config_dict:
            return config_dict[key]
    return default


def get_roleclass(role_class) -> Type[Role]:
    """
    Get the role class signature by string or by itself.
    """
    from .registry import registry

    if role_class in registry.roles_map:
        return registry.roles_map[role_class]
    else:
        raise RoleNotFound("'%s' is not a registered role class." % role_class)


def string_to_permission(perm):
    """
    Transforms a string representation into a Permission instance.
    """
    from django.contrib.auth.models import Permission

    # Checking if the Permission instance
    # exists in the cache system.
    key = "{}-permission-{}".format(cache_prefix(), perm)
    perm_obj: Optional[Permission] = orca_cache().get(key)

    # If not, creates the query to
    # get the Permission instance
    # and store into the cache.
    if perm_obj is None:
        app, codename = perm.split(".")
        perm_obj = (
            # TODO: This is an eager fetch of a likely cached object
            Permission.objects.select_related("content_type")
            .filter(content_type__app_label=app, codename=codename)
            .get()
        )
        orca_cache().set(key, perm_obj, timeout=cache_timeout())

    return perm_obj


def permission_to_string(perm):
    """
    Transforms a Permission instance into a string representation.
    """
    app_label = perm.content_type.app_label
    codename = perm.codename
    return "%s.%s" % (app_label, codename)


def is_unique_together(model):
    """
    Return True if the model does not accept multiple roles attached to it using the user instance.
    """
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


def cleanup_handler(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    Delete the roles attached to "instance". Connected to the post_delete
    signal of every model that roles can be attached to.
    """
    from django.contrib.contenttypes.models import ContentType

    from .models import UserRole

    ct_obj = ContentType.objects.get_for_model(instance)
    UserRole.objects.filter(content_type=ct_obj.id, object_id=instance.pk).delete()


def register_cleanup():
    """
    Connect "cleanup_handler" to the models listed in registered roles, and
    to their subclasses. Other models are left alone, because Django can't
    delete a model's rows in bulk while it has a post_delete receiver.
    """
    from django.apps import apps
    from django.db.models.signals import post_delete

    from .registry import registry

    role_models = {
        model
        for role in registry.roles_map.values()
        if not role.all_models
        for model in role.get_models()
    }
    for model in apps.get_models():
        if any(issubclass(model, role_model) for role_model in role_models):
            post_delete.connect(cleanup_handler, sender=model, dispatch_uid=str(model))


def pk_field(model) -> models.Field:
    """
    Return the field that holds the primary key value of "model". For a
    multi-table inheritance child, whose primary key links to its parent,
    this is the parent's primary key field.
    """
    field = model._meta.pk
    while field.is_relation:
        field = field.target_field
    return field


def object_ids(userroles, model) -> models.Subquery:
    """
    Return a subquery of the "object_id" values of "userroles", converted to
    the type of the primary key of "model" so they can be compared with it.
    """
    field = pk_field(model)
    object_id: Union[models.F, Replace] = models.F("object_id")
    if isinstance(field, models.UUIDField):
        # object_id holds str(uuid), which has hyphens, but databases without a
        # native UUID type store UUIDs as 32 hex characters.
        object_id = Replace(object_id, models.Value("-"), models.Value(""))
    return models.Subquery(
        userroles.annotate(orca_object_pk=Cast(object_id, output_field=field)).values(
            "orca_object_pk"
        )
    )


def check_my_model(role, obj):
    """
    if both are provided, check if obj (instance or model class) belongs to the role class.
    """
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
    """
    Proxy method used to get the cache object belonging to orca.
    """
    from django.core.cache import caches

    return caches[get_config("CACHE", "default")]


def cache_timeout() -> int:
    return get_config("CACHE_TIMEOUT", CACHE_TIMEOUT)


def _generation_key() -> str:
    return "{}-generation".format(get_config("CACHE_PREFIX_KEY", CACHE_KEY_PREFIX))


def cache_prefix() -> str:
    """
    Prefix for every orca cache key. It includes a generation number so
    that bumping the generation invalidates all orca keys at once.
    """
    prefix = get_config("CACHE_PREFIX_KEY", CACHE_KEY_PREFIX)
    # A missing generation starts from the current time rather than 1 so
    # that an evicted counter can't bring back keys from an old generation.
    generation = orca_cache().get_or_set(_generation_key(), time.time_ns, timeout=None)
    return "{}-{}".format(prefix, generation)


def clear_cache():
    """
    Invalidate every orca cache key without touching the rest of the cache.
    Stale keys are no longer read and expire through the cache's timeout.
    """
    # get + set rather than incr: some backends (database, file) rewrite the
    # key with the default timeout on incr, which would let the counter expire.
    # Concurrent clears may both write the same value, which still retires
    # the old generation.
    cache = orca_cache()
    generation = cache.get(_generation_key())
    if generation is None:
        generation = time.time_ns()
    cache.set(_generation_key(), generation + 1, timeout=None)
