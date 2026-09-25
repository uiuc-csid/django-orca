import factory
from factory.django import DjangoModelFactory

from tests.example_project.main.models import (
    Course,
    Department,
    HonorsCourse,
    School,
    User,
)


class UserFactory(DjangoModelFactory[User]):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    # Unique names, so every call creates a separate object.
    username = factory.Sequence(lambda n: f"user-{n}")


class SchoolFactory(DjangoModelFactory[School]):
    class Meta:
        model = School

    name = factory.Sequence(lambda n: f"school-{n}")


class DepartmentFactory(DjangoModelFactory[Department]):
    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"department-{n}")
    school = factory.SubFactory(SchoolFactory)


class CourseFactory(DjangoModelFactory[Course]):
    class Meta:
        model = Course

    name = factory.Sequence(lambda n: f"course-{n}")
    department = factory.SubFactory(DepartmentFactory)


class HonorsCourseFactory(CourseFactory):
    class Meta:
        model = HonorsCourse
