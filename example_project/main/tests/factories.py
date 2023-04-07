import factory
from django.conf import settings
from factory.django import DjangoModelFactory

from ..models import Course, Department


class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ["username"]

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    username = factory.Faker("user_name")


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department
        django_get_or_create = ["name"]

    name = factory.Faker("word")


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course
        django_get_or_create = ["name"]

    name = factory.Faker("word")
    department = factory.SubFactory(DepartmentFactory)
