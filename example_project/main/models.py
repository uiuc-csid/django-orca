from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from django_orca.auth.mixins import UserRoleMixin
from django_orca.models import RoleMixin


class User(UserRoleMixin, AbstractUser):
    pass


class School(RoleMixin, models.Model):
    name = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name


class Department(RoleMixin, models.Model):
    class RoleOptions:
        permission_parents = ["school"]

    name = models.CharField(max_length=256)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("department-detail", kwargs={"pk": self.pk})


class Course(RoleMixin, models.Model):
    class RoleOptions:
        permission_parents = ["department"]

    name = models.CharField(max_length=256)
    enrolled_students = models.ManyToManyField(settings.AUTH_USER_MODEL)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("course-detail", kwargs={"pk": self.pk})


class HonorsCourse(Course):
    class RoleOptions:
        permission_parents = ["department"]
