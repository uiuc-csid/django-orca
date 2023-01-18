import pytest
from django.test import Client

from ..models import User
from ..roles import CourseOwner, CourseViewer, DepartmentOwner


@pytest.mark.django_db
def test_assign_role(course_factory):
    course = course_factory()
    user = User.objects.create(username="owner")

    assert not user.has_role(CourseOwner, obj=course)

    user.assign_role(CourseOwner, obj=course)
    assert user.has_role(CourseOwner, obj=course)

    user.remove_role(CourseOwner, obj=course)
    assert not user.has_role(CourseOwner, obj=course)


@pytest.mark.django_db
def test_basic_permission_granting(course_factory):
    course = course_factory()
    user = User.objects.create(username="testowner")

    assert not user.has_perm("main.view_course", course)

    user.assign_role(CourseOwner, course)
    assert user.has_perm("main.view_course", course)
    assert user.has_perms(["main.view_course", "main.change_course"], course)


@pytest.mark.django_db
def test_views(client: Client, course_factory):
    course = course_factory()
    user = User.objects.create(username="testowner")
    client.force_login(user)

    response = client.get(course.get_absolute_url())
    assert response.status_code == 403

    user.assign_role(CourseOwner, course)
    response = client.get(course.get_absolute_url())
    assert response.status_code == 200


@pytest.mark.django_db
def test_limited_permission_granting(course_factory):
    course = course_factory()
    user = User.objects.create(username="viewer")

    assert not user.has_perm("main.view_course", course)
    assert not user.has_perm("main.change_course", course)

    user.assign_role(CourseViewer, course)
    assert user.has_perm("main.view_course", course)
    assert not user.has_perm("main.change_course", course)


@pytest.mark.django_db
def test_inherited_permissions(department_factory, course_factory):
    department = department_factory()
    user = User.objects.create(username="dept_owner")

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
