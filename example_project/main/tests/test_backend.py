import pytest
from django_orca.shortcuts import get_userroles

from ..models import Course, Department, User
from ..roles import CourseOwner, CourseViewer, DepartmentOwner


@pytest.mark.django_db
def test_user_permissions(user_factory, course: Course, department: Department):
    user1: User = user_factory()
    perms = user1.get_user_permissions()
    assert len(perms) == 0

    user1.assign_role(CourseViewer, course)
    perms = user1.get_user_permissions()
    assert len(perms) == 1
    assert user1.get_all_permissions() == user1.get_user_permissions()

    perms = user1.get_user_permissions(obj=course)
    assert len(perms) == 1
    assert user1.get_all_permissions(obj=course) == user1.get_user_permissions(
        obj=course
    )

    perms = user1.get_user_permissions(obj=department)
    assert len(perms) == 0
    assert user1.get_all_permissions(obj=department) == user1.get_user_permissions(
        obj=department
    )

    # Note: permissions are cached so they should be cleared between checks
    user2: User = user_factory()
    perms = user2.get_user_permissions()
    assert len(perms) == 0
    assert user2.get_all_permissions() == user2.get_user_permissions()

    user2.assign_role(CourseOwner, course)
    perms = user2.get_user_permissions()
    assert len(perms) == 3
    assert user2.get_all_permissions() == user2.get_user_permissions()


@pytest.mark.django_db
def test_post_delete_handler(user: User, course: Course, department: Department):
    assert get_userroles(user).count() == 0
    user.assign_role(DepartmentOwner, department)
    assert get_userroles(user).count() == 1
    department.delete()
    assert get_userroles(user).count() == 0

    assert get_userroles(user).count() == 0
    user.assign_role(CourseOwner, course)
    user.assign_role(CourseViewer, course)
    assert get_userroles(user).count() == 2
    course.delete()
    assert get_userroles(user).count() == 0
