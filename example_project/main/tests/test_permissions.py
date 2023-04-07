import pytest
from django.contrib.auth.models import AnonymousUser

from django_orca.exceptions import NotAllowed
from django_orca.shortcuts import has_permission, has_role

from ..models import Course, Department, User
from ..roles import CourseOwner, CourseViewer, DepartmentOwner


@pytest.mark.django_db
def test_anon_user(course):
    user = AnonymousUser()
    assert not has_role(user, role_class=CourseOwner)
    assert not has_role(user, role_class=CourseViewer, obj=course)

    assert not has_permission(user, "main.view_course")


@pytest.mark.django_db
def test_checker_error_handling(course, user):
    with pytest.raises(NotAllowed):
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
def test_inherited_permissions(user: User, department: Department, course_factory):
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
