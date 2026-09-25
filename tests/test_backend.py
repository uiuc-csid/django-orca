import pytest

from django_orca.shortcuts import get_userroles
from tests.example_project.main.models import Course, Department, User
from tests.example_project.main.roles import CourseOwner, CourseViewer, DepartmentOwner


@pytest.mark.django_db
def test_user_permissions(user_factory, course: Course, department: Department):
    user1: User = user_factory.create()
    perms = user1.get_user_permissions()
    assert len(perms) == 0

    user1.assign_role(CourseViewer, course)
    perms = user1.get_user_permissions()
    assert len(perms) == 1
    assert user1.get_all_permissions() == user1.get_user_permissions()

    perms = user1.get_user_permissions(obj=course)
    assert len(perms) == 1
    assert user1.get_all_permissions(obj=course) == user1.get_user_permissions(
        obj=course
    )

    perms = user1.get_user_permissions(obj=department)
    assert len(perms) == 0
    assert user1.get_all_permissions(obj=department) == user1.get_user_permissions(
        obj=department
    )

    # Note: permissions are cached so they should be cleared between checks
    user2: User = user_factory.create()
    perms = user2.get_user_permissions()
    assert len(perms) == 0
    assert user2.get_all_permissions() == user2.get_user_permissions()

    user2.assign_role(CourseOwner, course)
    perms = user2.get_user_permissions()
    assert len(perms) == 3
    assert user2.get_all_permissions() == user2.get_user_permissions()


@pytest.mark.django_db
def test_post_delete_handler(user: User, course: Course, department: Department):
    assert get_userroles(user).count() == 0
    user.assign_role(DepartmentOwner, department)
    assert get_userroles(user).count() == 1
    department.delete()
    assert get_userroles(user).count() == 0

    assert get_userroles(user).count() == 0
    user.assign_role(CourseOwner, course)
    user.assign_role(CourseViewer, course)
    assert get_userroles(user).count() == 2
    course.delete()
    assert get_userroles(user).count() == 0


def test_cleanup_handler_only_on_role_models():
    from django.db.models.signals import post_delete

    from tests.example_project.main.models import HonorsCourse, School

    assert post_delete.has_listeners(Course)
    assert post_delete.has_listeners(School)
    # Subclasses of role models can have roles too.
    assert post_delete.has_listeners(HonorsCourse)
    # No role lists users, so their deletes stay fast.
    assert not post_delete.has_listeners(User)


@pytest.mark.django_db
def test_queryset_delete_removes_roles(user: User, course_factory):
    courses = [course_factory.create(), course_factory.create()]
    for course in courses:
        user.assign_role(CourseOwner, course)

    Course.objects.filter(pk__in=[course.pk for course in courses]).delete()

    assert get_userroles(user).count() == 0


@pytest.mark.django_db
def test_user_permissions_are_strings(user: User, course: Course):
    user.assign_role(CourseViewer, course)

    assert user.get_user_permissions(course) == {"main.view_course"}
    assert user.get_user_permissions() == {"main.view_course"}


@pytest.mark.django_db
def test_user_permissions_include_inherited(user: User, course: Course):
    user.assign_role(DepartmentOwner, course.department)

    assert user.get_user_permissions(course) == {
        "main.view_course",
        "main.change_course",
    }
    assert user.get_user_permissions(course.department) == {"main.view_department"}


@pytest.mark.django_db
def test_user_permissions_match_has_perm(user: User, course_factory):
    course: Course = course_factory.create()
    other: Course = course_factory.create()
    user.assign_role(CourseOwner, course)
    user.assign_role(DepartmentOwner, other.department)

    for obj in [course, other, course.department, other.department]:
        perms = user.get_user_permissions(obj)
        candidates = {
            "main.view_course",
            "main.change_course",
            "main.delete_course",
            "main.view_department",
        }
        assert perms == {perm for perm in candidates if user.has_perm(perm, obj)}
