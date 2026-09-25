import pytest

from django_orca.exceptions import ImproperlyConfigured, NotAllowed
from django_orca.roles import Role
from tests.example_project.main.roles import CourseOwner, DepartmentOwner


def test_roles_cannot_be_instantiated():
    with pytest.raises(ImproperlyConfigured):
        CourseOwner()


def test_base_role_cannot_be_used():
    with pytest.raises(ImproperlyConfigured):
        Role.get_class_name()


def test_inherit_mode_requires_inherit():
    assert DepartmentOwner.get_inherit_mode() is not None
    with pytest.raises(NotAllowed):
        CourseOwner.get_inherit_mode()
