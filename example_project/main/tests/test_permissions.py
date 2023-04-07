import pytest
from django.test import Client
from django.urls import reverse

from ..models import Course, Department, User
from ..roles import CourseOwner, CourseViewer, DepartmentOwner


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


@pytest.mark.django_db
def test_role_view(client: Client, user: User, course: Course):
    client.force_login(user)
    url = reverse("course-owner-detail", kwargs={"pk": course.pk})

    response = client.get(url)
    assert response.status_code == 403

    user.assign_role(CourseOwner, course)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_role_view_404(client: Client, user: User, course: Course):
    client.force_login(user)
    url = reverse("course-owner-detail-404", kwargs={"pk": course.pk})

    response = client.get(url)
    assert response.status_code == 404

    user.assign_role(CourseOwner, course)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_perm_view(client: Client, user: User, course: Course):
    client.force_login(user)

    url = course.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 403

    user.assign_role(CourseOwner, course)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_perm_view_404(client: Client, user: User, course: Course):
    client.force_login(user)

    url = reverse("course-detail-404", kwargs={"pk": course.pk})
    response = client.get(url)
    assert response.status_code == 404

    user.assign_role(CourseOwner, course)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_perm_view_department(client: Client, user: User, department_factory):
    department: Department = department_factory()
    user = User.objects.create(username="testowner")
    client.force_login(user)

    url = department.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 403

    user.assign_role(DepartmentOwner, department)
    response = client.get(url)
    assert response.status_code == 200
