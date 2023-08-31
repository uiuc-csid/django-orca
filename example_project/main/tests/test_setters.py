import pytest
from django_orca.exceptions import InvalidRoleAssignment
from django_orca.shortcuts import assign_role, get_userroles, remove_role

from ..models import Course, User
from ..roles import CourseOwner, CourseViewer, Superuser


@pytest.mark.django_db
def test_remove_roles(user: User, course_factory):
    course1: Course = course_factory()
    course2: Course = course_factory()
    course3: Course = course_factory()

    user.assign_role(CourseOwner, course1)
    user.assign_role(CourseViewer, course1)
    user.assign_role(CourseViewer, course2)
    user.assign_role(CourseViewer, course3)

    assert get_userroles(user).count() == 4
    # Remove a non-existent role
    remove_role(user, CourseOwner, course3)
    assert get_userroles(user).count() == 4

    # Remove a fully qualified role
    remove_role(user, CourseOwner, course1)
    assert get_userroles(user).count() == 3

    user.assign_role(CourseOwner, course1)
    assert get_userroles(user).count() == 4

    # Remove all roles on one object
    remove_role(user, obj=course1)
    assert get_userroles(user).count() == 2

    user.assign_role(CourseOwner, course1)
    user.assign_role(CourseViewer, course1)
    assert get_userroles(user).count() == 4

    # Remove all of one type of role
    remove_role(user, CourseViewer)
    assert get_userroles(user).count() == 1


@pytest.mark.django_db
def test_assign_roles(user, course):
    with pytest.raises(InvalidRoleAssignment):
        assign_role(user, CourseOwner)

    with pytest.raises(InvalidRoleAssignment):
        assign_role(user, Superuser, course)
