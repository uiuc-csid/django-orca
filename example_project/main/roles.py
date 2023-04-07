from django_orca.roles import Role


class DepartmentOwner(Role):
    verbose_name = "Department Owner"
    models = ["main.Department"]

    allow = ["main.view_department"]

    inherit = True
    inherit_allow = [
        "main.view_course",
        "main.change_course",
    ]


class CourseOwner(Role):
    verbose_name = "Course Owner"
    models = ["main.Course"]
    allow = [
        "main.view_course",
        "main.change_course",
        "main.delete_course",
    ]


class CourseViewer(Role):
    verbose_name = "Course Viewer"
    models = ["main.Course"]
    allow = [
        "main.view_course",
    ]
