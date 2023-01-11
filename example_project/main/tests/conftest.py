import pytest  # noqa: F401
from pytest_factoryboy import register

from .factories import CourseFactory, DepartmentFactory

register(DepartmentFactory)
register(CourseFactory)
