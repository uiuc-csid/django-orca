import logging
from importlib import import_module
from inspect import getmembers
from typing import Any, Dict, List, Type, Union

from django.apps import apps
from django.contrib.auth.models import Permission
from django.db.models import Model
from django.utils.module_loading import autodiscover_modules, module_has_submodule

from .exceptions import AlreadyRegistered, ImproperlyConfigured
from .roles import Role
from .utils import is_role, orca_cache

logger = logging.getLogger(__name__)


ALLOW_MODE = 0
DENY_MODE = 1


# Get model of foreign key field with Model._meta.get_field("field_name").related_model
class OrcaRegistry:
    class RoleRegistry(Dict[str, Type[Role]]):
        def __contains__(self, item: Any) -> bool:
            if isinstance(item, str):
                return super().__contains__(item)
            elif issubclass(item, Role):
                return item in self.values()
            else:
                return False

        def __getitem__(self, key: Union[str, Type[Role]]) -> Type[Role]:
            if isinstance(key, str):
                return super().__getitem__(key)
            elif issubclass(key, Role):
                if key in self.values():
                    return key
                else:
                    raise KeyError()
            else:
                raise KeyError()

    def __init__(self, name="django_orca"):
        self._registry = OrcaRegistry.RoleRegistry()
        self.name = name
        orca_cache().clear()

    @property
    def roles_map(self):
        return self._registry

    def get_roles_for_perm(
        self, permission: Union[Permission, str]
    ) -> List[Type[Role]]:
        perm = (
            f"{permission.content_type.app_label}.{permission.codename}"
            if isinstance(permission, Permission)
            else permission
        )
        return [role for role in self.roles_map.values() if perm in role.allow] + [
            role for role in self.roles_map.values() if perm in role.inherit_allow
        ]

    def _get_perm_inherits_tree(
        self, curr: Type[Model], parents, attname
    ) -> Dict[str, Type[Model]]:
        parents[attname] = curr

        if hasattr(curr, "RoleOptions") and hasattr(
            curr.RoleOptions, "permission_parents"
        ):
            for parent in curr.RoleOptions.permission_parents:
                field = curr._meta.get_field(parent)
                new_attname = f"{attname}__{field.name}"
                if new_attname not in parents:
                    parents.update(
                        self._get_perm_inherits_tree(
                            field.related_model, parents, new_attname
                        )
                    )

        return parents

    def get_perm_inheritance_tree(self, model: Type[Model]) -> Dict[str, Type[Model]]:
        accessors: Dict[str, Type[Model]] = {}

        if hasattr(model, "RoleOptions") and hasattr(
            model.RoleOptions, "permission_parents"
        ):
            for parent in model.RoleOptions.permission_parents:
                field = model._meta.get_field(parent)
                attname = field.name
                accessors.update(
                    self._get_perm_inherits_tree(
                        field.related_model, accessors, attname
                    )
                )
        return accessors

    def register(self, kls):
        if not is_role(kls):
            raise ImproperlyConfigured(
                '"%s" does not inherit from Role."' % str(kls)
            )  # pragma: no cover

        kls_name = kls.get_class_name()
        current_kls = self._registry.get(kls_name, None)

        if current_kls == kls:
            raise AlreadyRegistered(  # pragma: no cover
                '"%s" was already registered as a Role class.' % kls_name
            )

        if current_kls is not None and current_kls != kls:
            raise ImproperlyConfigured(  # pragma: no cover
                '"Another role was already defined using "%s". Choose another name for this Role class.'
                % kls_name
            )

        self.__validate(kls)
        self._registry[kls.get_class_name()] = kls
        try:
            del self.get_roles_for_perm
            del self.get_inheritance_roles_for_perm
        except AttributeError:
            pass
        logger.debug("Registered role: %s", kls)

    @classmethod
    def __validate(cls, new_class):
        name = new_class.get_class_name()

        # Check for "verbose_name" definition.
        if not hasattr(new_class, "verbose_name"):
            raise ImproperlyConfigured(  # pragma: no cover
                'Provide a "verbose_name" definition to the Role class "%s".' % name
            )

        # Check if the atribute "models" is
        # defined correctly.
        cls.__validate_models(new_class)

        # Role classes with "models" = ALLMODELS
        # does not use allow/deny. In this case,
        # all permissions must be specified in
        # "inherit_allow" and "inherit_deny".
        new_class.MODE = cls.__validate_allow_deny(new_class, "allow", "deny")

        # Ensuring that "inherit" exists.
        # Default: False
        if not hasattr(new_class, "inherit") or not isinstance(new_class.inherit, bool):
            new_class.inherit = False

        if new_class.inherit is True:
            new_class.INHERIT_MODE = cls.__validate_allow_deny(
                new_class, "inherit_allow", "inherit_deny"
            )

        # Ensuring that "unique" exists.
        # Default: False
        if not hasattr(new_class, "unique") or not isinstance(new_class.unique, bool):
            new_class.unique = False

        # Ensuring that "ranking" exists.
        # Default: 0
        if not hasattr(new_class, "ranking") or not isinstance(new_class.ranking, int):
            new_class.ranking = 0

    @classmethod
    def __validate_models(cls, new_class):
        """Check if the attribute "models" is a valid list of Django models."""
        name = new_class.get_verbose_name()

        models_isvalid = True
        if hasattr(new_class, "models"):
            if isinstance(new_class.models, list):
                # Check for every item in the "models" list.
                valid_list = list()
                for model in new_class.models:
                    # Get the model class or "app_label.model".
                    model_class = apps.get_model(*model.split(".", 1))
                    if model_class:
                        valid_list.append(model_class)
                    else:
                        models_isvalid = False
                        break
                new_class.models = valid_list
            elif new_class.all_models:
                # Role classes with ALL_MODELS autoimplies inherit=True.
                new_class.inherit = True
                new_class.unique = False
                new_class.MODE = DENY_MODE
                new_class.allow = []
                new_class.deny = []
            else:
                models_isvalid = False
        elif new_class.all_models:
            new_class.inherit = True
            new_class.unique = False
        else:
            models_isvalid = False

        if not models_isvalid:
            raise ImproperlyConfigured(  # pragma: no cover
                'Provide a list of Models classes via definition of "models" to the Role class "%s".'
                % name
            )

    @classmethod
    def __validate_allow_deny(cls, new_class, allow_field, deny_field):
        """Validate the allow/deny attributes.

        This method validates the set attributes "allow/inherit_allow"
        and "deny/inherit_deny", checking if their values are a valid
        list of permissions in string representation.
        """
        name = new_class.get_verbose_name()

        # Checking for "allow" and "deny" fields
        c_allow = getattr(new_class, allow_field, None)
        c_deny = getattr(new_class, deny_field, None)

        # XOR operation.
        if c_allow and c_deny or not c_allow and not c_deny:
            raise ImproperlyConfigured(  # pragma: no cover
                'Provide either "%s" or "%s" when inherit=True for the Role "%s".'
                % (allow_field, deny_field, name)
            )

        if c_allow and isinstance(getattr(new_class, allow_field), list):
            result = ALLOW_MODE

        elif c_deny and isinstance(getattr(new_class, deny_field), list):
            result = DENY_MODE
        else:
            raise ImproperlyConfigured(  # pragma: no cover
                '"%s" or "%s" must to be a list in the Role "%s".'
                % (allow_field, deny_field, name)
            )

        # Return the mode.
        return result


registry = OrcaRegistry()


def autodiscover(module_name="roles"):
    autodiscover_modules(module_name, register_to=registry)

    for app in apps.get_app_configs():
        if not module_has_submodule(app.module, module_name):
            continue
        module = import_module(f"{app.name}.{module_name}")
        for _, member in getmembers(module):
            if is_role(member):
                try:
                    registry.register(member)
                except AlreadyRegistered:  # pragma: no cover
                    pass
