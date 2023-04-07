import pytest

from django_orca.shortcuts import get_userroles, get_users

from ..models import Course, Department, User
from ..roles import CourseOwner, CourseViewer, DepartmentOwner


@pytest.mark.django_db
def test_get_users(user_factory, course_factory):
    course1: Course = course_factory()
    course2: Course = course_factory()
    course3: Course = course_factory()

    user1: User = user_factory()
    user1.assign_role(CourseViewer, course1)

    user2: User = user_factory()
    user2.assign_role(CourseViewer, course1)

    user3: User = user_factory()
    user3.assign_role(CourseViewer, course2)

    assert len(get_users(CourseViewer)) == 3
    assert len(get_users(CourseViewer, course1)) == 2
    assert len(get_users(CourseViewer, course2)) == 1
    assert len(get_users(CourseViewer, course3)) == 0


@pytest.mark.django_db
def test_get_objects(user: User, department: Department, course_factory):
    course1: Course = course_factory()
    course2: Course = course_factory()
    course3: Course = course_factory()
    assert len(user.get_objects()) == 0

    user.assign_role(CourseOwner, course1)
    user.assign_role(CourseOwner, course2)
    user.assign_role(CourseViewer, course3)
    assert len(user.get_objects()) == 3
    assert len(user.get_objects(role_class=CourseOwner)) == 2
    assert len(user.get_objects(role_class=CourseViewer)) == 1

    user.assign_role(CourseViewer, course1)
    assert len(user.get_objects(role_class=CourseViewer)) == 2

    user.assign_role(DepartmentOwner, department)
    assert len(user.get_objects(model=Course)) == 4
    assert len(user.get_objects(model=Department)) == 1


@pytest.mark.django_db
def test_get_obj_qs(user: User, course_factory):
    course1: Course = course_factory()
    course2: Course = course_factory()
    course3: Course = course_factory()
    assert user.get_objects_qs(model=Course).count() == 0

    user.assign_role(CourseOwner, course1)
    user.assign_role(CourseOwner, course2)
    user.assign_role(CourseViewer, course3)
    assert user.get_objects_qs(model=Course).count() == 3
    assert user.get_objects_qs(model=Course, role_class=CourseOwner).count() == 2
    assert user.get_objects_qs(model=Course, role_class=CourseViewer).count() == 1


@pytest.mark.django_db
def test_get_userroles(user: User, course_factory):
    course1: Course = course_factory()
    course2: Course = course_factory()
    assert get_userroles(user=user).count() == 0

    user.assign_role(CourseOwner, course1)
    user.assign_role(CourseViewer, course1)
    user.assign_role(CourseOwner, course2)
    assert get_userroles(user=user).count() == 3
    assert get_userroles(user=user, obj=course1).count() == 2
    assert get_userroles(user=user, obj=course2).count() == 1