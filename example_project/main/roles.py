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


class CourseViewerNoInherit(Role):
    verbose_name = "Course Viewer"
    models = ["main.Course"]
    allow = [
        "main.view_course",
    ]
    follow_inheritance = False


class SchoolOwner(Role):
    verbose_name = "School Owner"
    models = ["main.School"]
    allow = ["main.view_school", "main.change_school"]

    inherit_allow = [
        "main.view_course",
        "main.change_course",
    ]


class Superuser(Role):
    verbose_name = "Course Superuser"
    all_models = True
    allow = [
        "main.view_course",
        "main.change_course",
        "main.delete_course",
        "main.view_department" "main.change_department" "main.delete_department",
    ]

    inherit_allow = [
        "main.view_course",
        "main.change_course",
        "main.delete_course",
        "main.view_department" "main.change_department" "main.delete_department",
    ]
