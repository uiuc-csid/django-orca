import pytest

from ..models import Course, Department, User
from ..roles import CourseViewer, DepartmentOwner, SchoolOwner


@pytest.mark.django_db
def test_single_hop_inherited_permissions(
    user: User, department: Department, course_factory
):
    course1 = course_factory(department=department)
    course2 = course_factory(department=department)
    course3 = course_factory()

    # No permissions initially
    assert not user.has_perm("main.view_course", course1)
    assert not user.has_perm("main.change_course", course1)
    assert not user.has_perm("main.view_course", course2)
    assert not user.has_perm("main.change_course", course2)
    assert not user.has_perm("main.view_course", course3)
    assert not user.has_perm("main.change_course", course3)

    user.assign_role(DepartmentOwner, department)

    # Permissions have been granted, but not all perms
    assert user.has_perm("main.view_course", course1)
    assert not user.has_perm("main.delete_course", course1)
    assert user.has_perm("main.view_course", course2)
    assert not user.has_perm("main.delete_course", course2)

    # We haven't set permissions globally
    assert not user.has_perm("main.view_course", course3)
    assert not user.has_perm("main.change_course", course3)


@pytest.mark.django_db
def test_multiple_hop_inheritance(user_factory, course_factory):
    user1: User = user_factory()

    course1: Course = course_factory()
    course2: Course = course_factory(department=course1.department)
    course3: Course = course_factory()

    user1.assign_role(SchoolOwner, course1.department.school)

    assert user1.has_perm("main.view_course", course1)
    assert user1.has_perm("main.view_course", course2)
    assert not user1.has_perm("main.view_course", course3)
    assert not user1.has_perm("main.delete_course", course1)


@pytest.mark.django_db
def test_model_inheritance(user, honors_course):
    assert not user.has_perm("main.view_course", honors_course)
    user.assign_role(CourseViewer, honors_course)
    assert user.has_perm("main.view_course", honors_course)
