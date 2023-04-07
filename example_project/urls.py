from django.contrib import admin
from django.urls import path

from example_project.main.views import (
    CourseDetailView,
    CourseOwnerDetailView,
    DepartmentDetailView,
    IndexView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("course/<int:pk>", CourseDetailView.as_view(), name="course-detail"),
    path(
        "department/<int:pk>", DepartmentDetailView.as_view(), name="department-detail"
    ),
    path(
        "course-owner/<int:pk>",
        CourseOwnerDetailView.as_view(),
        name="course-owner-detail",
    ),
    path("", IndexView.as_view(), name="index"),
]
