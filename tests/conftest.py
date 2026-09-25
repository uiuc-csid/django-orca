import pytest  # noqa: F401
from pytest_factoryboy import register

from tests.factories import (
    CourseFactory,
    DepartmentFactory,
    HonorsCourseFactory,
    SchoolFactory,
    UserFactory,
)

register(SchoolFactory)
register(DepartmentFactory)
register(CourseFactory)
register(UserFactory)
register(HonorsCourseFactory)
