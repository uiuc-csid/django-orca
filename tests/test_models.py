import pytest

from django_orca.models import UserRole
from tests.example_project.main.models import Course, User
from tests.example_project.main.roles import CourseOwner, CourseViewer


@pytest.mark.django_db
def test_resaving_user_role_keeps_permissions(user: User, course: Course):
    user.assign_role(CourseOwner, course)
    user_role = UserRole.objects.get()
    permissions = set(user_role.accesses.values_list("permission", "access"))
    assert permissions

    user_role.save()

    assert set(user_role.accesses.values_list("permission", "access")) == permissions


@pytest.mark.django_db
def test_user_role_save_passes_arguments(user: User, course_factory):
    course: Course = course_factory()
    other: Course = course_factory()
    user.assign_role(CourseOwner, course)
    user_role = UserRole.objects.get()

    user_role.role_class = CourseViewer.get_class_name()
    user_role.object_id = other.id
    user_role.save(update_fields=["role_class"])

    user_role.refresh_from_db()
    assert user_role.role_class == CourseViewer.get_class_name()
    # object_id was not in update_fields, so it is unchanged.
    assert user_role.object_id == str(course.id)
