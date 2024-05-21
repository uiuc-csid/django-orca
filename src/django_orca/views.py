"""Useful views and mixins for using django_orca."""
from __future__ import annotations

from collections.abc import Iterable
from typing import List, Type

from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import Http404

from django_orca.roles import Role
from django_orca.shortcuts import has_role


class ObjectPermissionRequiredMixin(AccessMixin):
    """Checks whether the accessor has the specified permission(s) on the referenced object.

    Attributes:
        login_url:  The page.
        return_404: If true, will return a 404. Otherwise this will return a 403. False by default
        permission_required: The permission or list of permissions to be checked
    """

    login_url: str = settings.LOGIN_URL
    permission_required: str | Iterable[str]
    return_404: bool = False

    def get_permission_required(self) -> List[str]:
        """Retrieves the list of required permissions from the `permission_required` attribute.

        Returns:
            List[str]: A list of all required permissions
        """
        if self.permission_required:
            if isinstance(self.permission_required, str):
                return [self.permission_required]
            else:
                return self.permission_required

        raise ImproperlyConfigured(
            "Provide a 'permission_required' attribute."
        )  # pragma: no cover

    def get_permission_object(self):
        if hasattr(self, "permission_object"):
            return getattr(self, "permission_object")

        elif hasattr(self, "object"):
            if object := getattr(self, "object"):
                return object

        elif hasattr(self, "get_object"):
            return getattr(self, "get_object")()

        raise ImproperlyConfigured(  # pragma: no cover
            "Provide a 'permission_object' attribute or implement "
            "a 'get_permission_object' method."
        )

    def has_permission(self):
        return self.request.user.has_perms(
            self.get_permission_required(), self.get_permission_object()
        )

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            if self.return_404:
                raise Http404
            else:
                raise PermissionDenied
        else:
            return super().dispatch(request, *args, **kwargs)


class ObjectRoleRequiredMixin(AccessMixin):
    """Checks whether the accessor has the specified role(s) on the referenced object.

    Attributes:
        login_url:  The page.
        return_404: If true, will return a 404. Otherwise this will return a 403. False by default
        permission_required: The role that will be validated
    """

    login_url: str = settings.LOGIN_URL
    permission_required: Type[Role]
    return_404: bool = False

    def get_role_required(self) -> Type[Role]:
        """Retrieves the role that will be required for the page."""
        if self.role_required:
            return self.role_required

        raise ImproperlyConfigured(
            "Provide a 'role_required' attribute."
        )  # pragma: no cover

    def get_permission_object(self):
        if hasattr(self, "permission_object"):
            return getattr(self, "permission_object")

        elif hasattr(self, "object"):
            if object := getattr(self, "object"):
                return object

        elif hasattr(self, "get_object"):
            return getattr(self, "get_object")()

        raise ImproperlyConfigured(  # pragma: no cover
            "Provide a 'permission_object' attribute or implement "
            "a 'get_permission_object' method."
        )

    def has_permission(self):
        return has_role(
            self.request.user, self.get_role_required(), self.get_permission_object()
        )

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            if self.return_404:
                raise Http404
            else:
                raise PermissionDenied
        else:
            return super().dispatch(request, *args, **kwargs)
