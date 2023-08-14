from heavy_water import BaseDataBuilder

from example_project.main.roles import DepartmentOwner
from example_project.main.tests.factories import (
    CourseFactory,
    DepartmentFactory,
    UserFactory,
)


class ExampleProjectDataBuilder(BaseDataBuilder):
    def handle(self):
        import factory.random

        factory.random.reseed_random("example_project")
        departments = DepartmentFactory.create_batch(size=3)
        for department in departments:
            CourseFactory.create_batch(department=department, size=3)

        dept_owner = UserFactory()
        dept_owner.assign_role(DepartmentOwner, departments[0])
        dept_owner.assign_role(DepartmentOwner, departments[1])
