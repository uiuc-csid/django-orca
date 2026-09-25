import pytest

from django_orca.auth.getters import get_perm_qs_for_user
from django_orca.registry import registry
from django_orca.roles import Role
from django_orca.shortcuts import get_objects
from tests.example_project.main.models import Course, Department, User
from tests.example_project.main.roles import CourseOwner, Superuser


@pytest.mark.django_db
def test_all_models_role_grants_on_every_object(
    user: User, course_factory, honors_course
):
    course: Course = course_factory.create()
    other: Course = course_factory.create()
    assert not user.has_perm("main.change_course", course)

    user.assign_role(Superuser)

    assert user.has_perm("main.change_course", course)
    assert user.has_perm("main.change_course", other)
    assert user.has_perm("main.delete_department", course.department)
    # Subclasses get the permissions of their parent model.
    assert user.has_perm("main.view_course", honors_course)
    assert set(get_perm_qs_for_user(user, Course, "main.view_course")) == {
        course,
        other,
        honors_course.course_ptr,
    }


@pytest.mark.django_db
def test_all_models_role_only_grants_allowed_permissions(
    user: User, course: Course, school
):
    user.assign_role(Superuser)

    # Not in Superuser.allow.
    assert not user.has_perm("main.view_school", school)
    # A permission of a different model than the object's.
    assert not user.has_perm("main.view_department", course)


@pytest.mark.django_db
def test_all_models_role_grants_global_permissions(user: User):
    assert not user.has_perm("main.view_course")

    user.assign_role(Superuser)

    assert user.has_perm("main.view_course")
    assert not user.has_perm("main.view_school")


@pytest.mark.django_db
def test_all_models_role_other_users_unaffected(user_factory, course: Course):
    admin: User = user_factory.create(username="admin")
    other: User = user_factory.create(username="other")
    admin.assign_role(Superuser)

    assert not other.has_perm("main.view_course", course)
    assert not other.has_perm("main.view_course")


@pytest.mark.django_db
def test_all_models_role_permissions(user: User, course: Course):
    user.assign_role(Superuser)

    assert user.get_user_permissions(course) == {
        "main.view_course",
        "main.change_course",
        "main.delete_course",
    }
    assert user.get_user_permissions() == set(Superuser.allow)


@pytest.mark.django_db
def test_get_objects_skips_all_models_roles(user: User, course: Course):
    user.assign_role(Superuser)
    user.assign_role(CourseOwner, course)

    assert get_objects(user) == [course]


def test_all_models_role_without_inherit_allow():
    class Auditor(Role):
        verbose_name = "Auditor"
        all_models = True
        allow = ["main.view_department"]

    registry.register(Auditor)
    try:
        assert registry.roles_map["auditor"] is Auditor
        assert Auditor.unique is False
    finally:
        del registry.roles_map["auditor"]


@pytest.mark.django_db
def test_department_permission_through_all_models_role(user: User, department):
    user.assign_role(Superuser)
    assert list(get_perm_qs_for_user(user, Department, "main.change_department")) == [
        department
    ]
