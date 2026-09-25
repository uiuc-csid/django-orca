import pytest

from django_orca.auth.getters import get_perm_qs_for_user
from django_orca.models import UserRole
from django_orca.shortcuts import get_objects, get_qs_for_user, get_users
from tests.example_project.main.models import Course, Project, Task, User
from tests.example_project.main.roles import CourseOwner, ProjectOwner, TaskOwner


@pytest.mark.django_db
def test_uuid_primary_key(user: User):
    project = Project.objects.create(name="Mine")
    other = Project.objects.create(name="Other")
    user.assign_role(ProjectOwner, project)

    assert user.has_role(ProjectOwner, project)
    assert user.has_perm("main.change_project", project)
    assert not user.has_perm("main.change_project", other)
    assert list(get_perm_qs_for_user(user, Project, "main.view_project")) == [project]
    assert list(get_qs_for_user(user, Project)) == [project]
    assert get_objects(user) == [project]
    assert list(get_users(ProjectOwner, project)) == [user]
    assert user.get_user_permissions(project) == {
        "main.view_project",
        "main.change_project",
    }


@pytest.mark.django_db
def test_text_primary_key(user: User):
    project = Project.objects.create(name="Project")
    task = Task.objects.create(slug="write-docs", project=project)
    other = Task.objects.create(slug="other", project=project)
    user.assign_role(TaskOwner, task)

    assert user.has_perm("main.change_task", task)
    assert not user.has_perm("main.change_task", other)
    assert list(get_qs_for_user(user, Task)) == [task]
    assert get_objects(user) == [task]


@pytest.mark.django_db
def test_inherited_permission_through_uuid_parent(user: User):
    project = Project.objects.create(name="Mine")
    other = Project.objects.create(name="Other")
    task = Task.objects.create(slug="mine", project=project)
    other_task = Task.objects.create(slug="other", project=other)
    user.assign_role(ProjectOwner, project)

    assert user.has_perm("main.view_task", task)
    assert not user.has_perm("main.view_task", other_task)


@pytest.mark.django_db
def test_large_integer_primary_key(user: User, department):
    # Larger than a 32-bit integer column can hold.
    course = Course.objects.create(id=2**40, name="Big", department=department)
    user.assign_role(CourseOwner, course)

    assert user.has_perm("main.change_course", course)
    assert list(get_qs_for_user(user, Course)) == [course]


@pytest.mark.django_db
def test_deleting_object_removes_roles(user: User):
    project = Project.objects.create(name="Mine")
    task = Task.objects.create(slug="mine", project=project)
    user.assign_role(ProjectOwner, project)
    user.assign_role(TaskOwner, task)

    project.delete()

    assert not UserRole.objects.exists()
