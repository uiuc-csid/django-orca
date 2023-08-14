from typing import List

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from .exceptions import RoleNotFound
from .roles import ALLOW_MODE
from .utils import get_permissions_list, get_roleclass, permission_to_string


class UserRoleManager(models.Manager):
    def get_by_natural_key(self, user_id, role_class, content_type_id, object_id):
        return self.get(
            user__id=user_id,
            role_class=role_class,
            content_type__id=content_type_id,
            object_id=object_id,
        )


class UserRole(models.Model):
    """
    UserRole
    This model represents the relationship between
    a user instance of the project with any other
    Django model, according to the rules defined
    in the Role class.
    """

    class Meta:
        verbose_name = "Role Instance"
        verbose_name_plural = "Role Instances"
        unique_together = ("user", "role_class", "content_type", "object_id")
        indexes = [
            models.Index(fields=["role_class"]),
            models.Index(fields=["user"]),
            models.Index(fields=["content_type"]),
        ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name="Users",
    )

    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        related_name="roles",
        verbose_name="Permissions",
    )

    role_class = models.CharField(max_length=256)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    obj = GenericForeignKey()

    objects = UserRoleManager()

    def natural_key(self):
        return (self.user.id, self.role_class, self.content_type.id, self.object_id)

    def __str__(self):
        role = get_roleclass(self.role_class)
        output = "{user} is {role}".format(user=self.user, role=role.get_verbose_name())
        if self.obj:
            output += " of {obj}".format(obj=self.obj)
        return output

    @property
    def role(self):
        return get_roleclass(self.role_class)

    def get_verbose_name(self):
        return self.role.get_verbose_name()

    def clean(self):
        try:
            get_roleclass(self.role_class)
        except RoleNotFound:
            raise ValidationError(
                {
                    "role_class": "This string representation does not exist as a Role class."
                }
            )

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ,unused-argument
        self.clean()
        super().save()

        # non-object roles does not have specific
        # permissions auto created.
        if self.role.all_models:
            return

        all_perms = get_permissions_list(self.role.get_models())

        role_instances: List[RolePermission] = list()

        for perm in all_perms:
            perm_s = permission_to_string(perm)
            if self.role.get_mode() == ALLOW_MODE:
                role_instances.append(
                    RolePermission(
                        role=self, permission=perm, access=perm_s in self.role.allow
                    )
                )
            else:
                role_instances.append(
                    RolePermission(
                        role=self, permission=perm, access=perm_s not in self.role.deny
                    )
                )

        RolePermission.objects.bulk_create(role_instances)


class RolePermissionManager(models.Manager):
    def get_by_natural_key(self, role_id, permission_id):
        return self.get(role__id=role_id, permission__id=permission_id)


class RolePermission(models.Model):
    """
    RolePermission
    This model has the function of performing
    the m2m relation between the Permission
    and the UserRole instances. It is possible
    that different instances of the same UserRole
    may have access to different permissions.
    """

    PERMISSION_CHOICES = ((True, "Allow"), (False, "Deny"))

    access = models.BooleanField(choices=PERMISSION_CHOICES, default=True)

    role = models.ForeignKey(
        UserRole, on_delete=models.CASCADE, related_name="accesses"
    )

    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="accesses"
    )

    objects = RolePermissionManager()

    def natural_key(self):
        return (self.role.id, self.permission.id)

    natural_key.dependencies = ["django_orca.userrole"]

    class Meta:
        unique_together = ("role", "permission")


class RoleMixin:
    roles = GenericRelation(UserRole)
