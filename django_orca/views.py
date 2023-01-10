from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import Http404


class ObjectPermissionRequiredMixin(AccessMixin):
    """
    PermissionMixin
    This mixin helps the class-based views
    to secure them based in permissions.
    """

    login_url = settings.LOGIN_URL
    permission_required = None
    return_404 = False
    return_403 = True

    def get_permission_required(self):
        if self.permission_required != "":
            return self.permission_required

        raise ImproperlyConfigured("Provide a 'permission_required' attribute.")

    def get_permission_object(self):
        if hasattr(self, "permission_object"):
            return getattr(self, "permission_object")

        elif hasattr(self, "object"):
            if object := getattr(self, "object"):
                return object

        elif hasattr(self, "get_object"):
            return getattr(self, "get_object")()

        raise ImproperlyConfigured(
            "Provide a 'permission_object' attribute or implement "
            "a 'get_permission_object' method."
        )

    def has_permission(self):
        return self.request.user.has_perm(
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
