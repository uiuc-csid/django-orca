import pytest
from rest_framework.test import APIRequestFactory

from django_orca.rest_framework.filters import ObjectRolePermissionsFilter
from tests.example_project.main.models import Course, User
from tests.example_project.main.roles import CourseInstructor, CourseViewer


def filter_courses(filter_backend, user):
    request = APIRequestFactory().get("/")
    request.user = user
    return filter_backend.filter_queryset(request, Course.objects.all(), view=None)


@pytest.mark.django_db
def test_filter_uses_view_permission_by_default(user: User, course_factory):
    visible: Course = course_factory()
    course_factory()
    user.assign_role(CourseViewer, visible)

    assert list(filter_courses(ObjectRolePermissionsFilter(), user)) == [visible]


@pytest.mark.django_db
def test_filter_uses_permission_name(user: User, course_factory):
    viewed: Course = course_factory()
    instructed: Course = course_factory()
    user.assign_role(CourseViewer, viewed)
    user.assign_role(CourseInstructor, instructed)

    class ChangeFilter(ObjectRolePermissionsFilter):
        permission_name = "main.change_course"

    assert list(filter_courses(ChangeFilter(), user)) == [instructed]


def test_permission_name_requires_queryset():
    with pytest.raises(Exception, match="Queryset must be passed in"):
        ObjectRolePermissionsFilter().get_permission_name(None)
