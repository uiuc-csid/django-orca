from abc import ABC
from typing import List, Optional, Type, Union

from django.apps import apps
from django.db.models import Model

from .exceptions import ImproperlyConfigured, NotAllowed

ALLOW_MODE = 0
DENY_MODE = 1

ALL_MODELS = -1


class Role(ABC):
    """
    Role

    This abstract class is the base for all other roles
    """

    verbose_name: str

    all_models: bool = False
    models: List[Union[Type[Model], str]]

    allow: Optional[List[str]]
    deny: Optional[List[str]]

    unique: bool = False
    ranking: int = 0

    inherit: bool = False
    inherit_allow: Optional[List[str]]
    inherit_deny: Optional[List[str]]

    MODE = ALLOW_MODE
    INHERIT_MODE = ALLOW_MODE

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        raise ImproperlyConfigured("Role classes must not be instantiated.")

    @classmethod
    def __protect(cls):
        if cls == Role:
            raise ImproperlyConfigured("The role class itself must not be used.")

    @classmethod
    def get_class_name(cls):
        cls.__protect()
        return str(cls.__name__.lower())

    @classmethod
    def get_verbose_name(cls):
        cls.__protect()
        return str(cls.verbose_name)

    @classmethod
    def get_mode(cls):
        cls.__protect()
        return cls.MODE

    @classmethod
    def get_inherit_mode(cls):
        cls.__protect()
        if cls.inherit is True:
            return cls.INHERIT_MODE
        raise NotAllowed(
            'The role "%s" is not marked as unique.' % cls.get_verbose_name()
        )

    @classmethod
    def get_models(cls):
        cls.__protect()
        if cls.all_models:
            return list(apps.get_models())  # All models known by Django.
        return list(cls.models)

    @classmethod
    def is_my_model(cls, model):
        cls.__protect()
        return model._meta.model in cls.get_models()  # pylint: disable=protected-access
