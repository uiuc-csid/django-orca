import factory
from factory.django import DjangoModelFactory

from ..models import Course, Department


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
