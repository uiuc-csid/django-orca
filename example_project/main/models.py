from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from django_orca.auth.mixins import UserRoleMixin


class User(UserRoleMixin, AbstractUser):
    pass


class Department(models.Model):
    name = models.CharField(max_length=256)


class Course(models.Model):
    class RoleOptions:
        permission_parents = ["department"]

    name = models.CharField(max_length=256)
    enrolled_students = models.ManyToManyField(settings.AUTH_USER_MODEL)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
