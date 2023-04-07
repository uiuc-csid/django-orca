import pytest
from django.test import Client
from django.urls import reverse

from ..models import Course, Department, User
from ..roles import CourseOwner, DepartmentOwner


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
