import pytest

from django_orca.exceptions import InvalidRoleAssignment
from django_orca.shortcuts import (
    assign_role,
    assign_roles,
    get_userroles,
    remove_role,
)
from tests.example_project.main.models import Course, User
from tests.example_project.main.roles import (
    CourseInstructor,
    CourseOwner,
    CourseViewer,
    Superuser,
)


@pytest.mark.django_db
def test_remove_roles(user: User, course_factory):
    course1: Course = course_factory.create()
    course2: Course = course_factory.create()
    course3: Course = course_factory.create()

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


@pytest.mark.django_db
def test_assign_role_twice_is_idempotent(user: User, course: Course):
    assign_role(user, CourseOwner, course)
    assign_role(user, CourseOwner, course)
    assert get_userroles(user).count() == 1


@pytest.mark.django_db
def test_unique_role_rejects_multiple_users(user_factory, course: Course):
    users = [user_factory.create(username="a"), user_factory.create(username="b")]
    with pytest.raises(InvalidRoleAssignment):
        assign_roles(users, CourseInstructor, course)
    assert get_userroles(users).count() == 0


@pytest.mark.django_db
def test_unique_role_rejects_second_user(user_factory, course_factory):
    course1: Course = course_factory.create()
    course2: Course = course_factory.create()
    first = user_factory.create(username="first")
    second = user_factory.create(username="second")

    assign_role(first, CourseInstructor, course1)
    with pytest.raises(InvalidRoleAssignment):
        assign_role(second, CourseInstructor, course1)

    # Uniqueness is per object.
    assign_role(second, CourseInstructor, course2)
    assert get_userroles(second).count() == 1


@pytest.mark.django_db
def test_unique_together_rejects_second_role(monkeypatch, user: User, course: Course):
    monkeypatch.setattr(Course.RoleOptions, "unique_together", True, raising=False)

    assign_role(user, CourseViewer, course)
    with pytest.raises(InvalidRoleAssignment):
        assign_role(user, CourseOwner, course)
    assert get_userroles(user).count() == 1


@pytest.mark.django_db
def test_assign_all_models_role(user: User):
    assign_role(user, Superuser)
    assert user.has_role(Superuser)
    assert get_userroles(user, role_class=Superuser).get().object_id is None
