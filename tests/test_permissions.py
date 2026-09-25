import pytest
from django.contrib.auth.models import AnonymousUser

from django_orca.auth.getters import get_perm_qs_for_user
from django_orca.shortcuts import has_permission, has_role
from tests.example_project.main.models import Course, User
from tests.example_project.main.roles import CourseOwner, CourseViewer


@pytest.mark.django_db
def test_anon_user(course):
    user = AnonymousUser()
    assert not has_role(user, role_class=CourseOwner)
    assert not has_role(user, role_class=CourseViewer, obj=course)

    assert not has_permission(user, "main.view_course")


@pytest.mark.django_db
def test_checker_error_handling(course, user):
    with pytest.raises(NotImplementedError):
        has_permission(user, "main.view_course", obj=course, any_object=True)


@pytest.mark.django_db
def test_assign_role(user: User, course: Course):
    assert not user.has_role(CourseOwner, obj=course)

    user.assign_role(CourseOwner, obj=course)
    assert user.has_role(CourseOwner, obj=course)

    user.remove_role(CourseOwner, obj=course)
    assert not user.has_role(CourseOwner, obj=course)


@pytest.mark.django_db
def test_basic_permission_granting(user: User, course: Course):
    assert not user.has_perm("main.view_course", course)

    user.assign_role(CourseOwner, course)
    assert user.has_perm("main.view_course", course)
    assert user.has_perms(["main.view_course", "main.change_course"], course)


@pytest.mark.django_db
def test_limited_permission_granting(user: User, course: Course):
    assert not user.has_perm("main.view_course", course)
    assert not user.has_perm("main.change_course", course)

    user.assign_role(CourseViewer, course)
    assert user.has_perm("main.view_course", course)
    assert not user.has_perm("main.change_course", course)


@pytest.mark.django_db
def test_permission_without_object(user: User, course: Course):
    user.assign_role(CourseOwner, obj=course)
    # Checks without an object are not supported, so they are always denied.
    assert not has_permission(user, "main.view_course")


@pytest.mark.django_db
def test_inactive_user_has_no_permissions(user: User, course: Course):
    user.assign_role(CourseOwner, obj=course)
    user.is_active = False
    user.save()

    assert not user.has_perm("main.view_course", course)
    assert not has_permission(user, "main.view_course", course)
    assert user.get_user_permissions(course) == set()
    assert user.get_user_permissions() == set()
    assert not get_perm_qs_for_user(user, Course, "main.view_course").exists()
    # Inactive users still hold their roles.
    assert has_role(user, CourseOwner, course)
