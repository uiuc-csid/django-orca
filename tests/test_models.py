import pytest

from django_orca.models import UserRole
from tests.example_project.main.models import Course, User
from tests.example_project.main.roles import CourseOwner, CourseViewer, Superuser


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
    course: Course = course_factory.create()
    other: Course = course_factory.create()
    user.assign_role(CourseOwner, course)
    user_role = UserRole.objects.get()

    user_role.role_class = CourseViewer.get_class_name()
    user_role.object_id = other.id
    user_role.save(update_fields=["role_class"])

    user_role.refresh_from_db()
    assert user_role.role_class == CourseViewer.get_class_name()
    # object_id was not in update_fields, so it is unchanged.
    assert user_role.object_id == str(course.id)


@pytest.mark.django_db
def test_natural_key_without_object(user: User):
    user.assign_role(Superuser)
    user_role = UserRole.objects.get()

    assert UserRole.objects.get_by_natural_key(*user_role.natural_key()) == user_role
