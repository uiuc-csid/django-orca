from typing import Optional

from rest_framework.filters import BaseFilterBackend

from django_orca.auth.getters import get_perm_qs_for_user


class ObjectRolePermissionsFilter(BaseFilterBackend):
    permission_name: Optional[str] = None

    def get_permission_name(self, queryset) -> str:
        if self.permission_name is not None:
            return self.permission_name
        elif queryset is None:
            raise Exception(
                "Queryset must be passed in if self.permission_name is not set"
            )
        else:
            app_label = queryset.model._meta.app_label
            model_name = queryset.model._meta.model_name
            return f"{app_label}.view_{model_name}"

    def filter_queryset(self, request, queryset, view):
        user = request.user
        perm_name = self.get_permission_name(queryset)

        return get_perm_qs_for_user(user, queryset.model, perm_name)
