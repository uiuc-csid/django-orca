from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from .exceptions import RoleNotFound
from .utils import get_roleclass


class UserRoleManager(models.Manager):
    def get_by_natural_key(self, user_id, role_class, content_type_id, object_id):
        return self.get(
            user__pk=user_id,
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

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name="Users",
    )

    role_class = models.CharField(max_length=256)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    # Text, so any primary key type fits. Holds str(pk), like Django's
    # generic relations; queries cast it back to the primary key's type.
    # NULL, like content_type, for roles that aren't attached to an object.
    object_id = models.CharField(max_length=255, null=True)  # noqa: DJ001
    obj = GenericForeignKey()

    objects = UserRoleManager()

    class Meta:
        verbose_name = "Role Instance"
        verbose_name_plural = "Role Instances"
        unique_together = ("user", "role_class", "content_type", "object_id")
        indexes = [
            models.Index(fields=["role_class"]),
            models.Index(fields=["user"]),
            models.Index(fields=["content_type"]),
        ]

    def __str__(self):
        role = get_roleclass(self.role_class)
        output = "{user} is {role}".format(user=self.user, role=role.get_verbose_name())
        if self.obj:
            output += " of {obj}".format(obj=self.obj)
        return output

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def natural_key(self):
        # content_type is None for roles that aren't attached to an object.
        return (self.user.pk, self.role_class, self.content_type_id, self.object_id)

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


class RoleMixin:
    roles = GenericRelation(UserRole)
