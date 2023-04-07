import pytest

from ..models import Course, User
from ..roles import CourseOwner, CourseViewer


@pytest.mark.django_db
def test_user_permissions(user_factory, course: Course):
    user1: User = user_factory()
    perms = user1.get_user_permissions()
    assert len(perms) == 0

    user1.assign_role(CourseViewer, course)
    perms = user1.get_user_permissions()
    assert len(perms) == 1

    # Note: permissions are cached so they should be cleared between checks
    user2: User = user_factory()
    perms = user2.get_user_permissions()
    assert len(perms) == 0

    user2.assign_role(CourseOwner, course)
    perms = user2.get_user_permissions()
    assert len(perms) == 3
