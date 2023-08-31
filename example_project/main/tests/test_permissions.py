import pytest
from django.contrib.auth.models import AnonymousUser
from django_orca.shortcuts import has_permission, has_role

from ..models import Course, User
from ..roles import CourseOwner, CourseViewer


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
