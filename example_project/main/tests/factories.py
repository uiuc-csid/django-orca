import factory
from django.conf import settings
from factory.django import DjangoModelFactory

from ..models import Course, Department, School


class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ["username"]

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    username = factory.Faker("user_name")


class SchoolFactory(DjangoModelFactory):
    class Meta:
        model = School
        django_get_or_create = ["name"]

    name = factory.Faker("word")


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department
        django_get_or_create = ["name"]

    name = factory.Faker("word")
    school = factory.SubFactory(SchoolFactory)


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course
        django_get_or_create = ["name"]

    name = factory.Faker("word")
    department = factory.SubFactory(DepartmentFactory)
