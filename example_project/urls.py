from django.contrib import admin
from django.urls import path

from example_project.main.views import (
    CourseDetailView,
    CourseDetailView404,
    CourseOwnerDetailView,
    CourseOwnerDetailView404,
    DepartmentDetailView,
    IndexView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("course/<int:pk>", CourseDetailView.as_view(), name="course-detail"),
    path("course404/<int:pk>", CourseDetailView404.as_view(), name="course-detail-404"),
    path(
        "department/<int:pk>", DepartmentDetailView.as_view(), name="department-detail"
    ),
    path(
        "course-owner/<int:pk>",
        CourseOwnerDetailView.as_view(),
        name="course-owner-detail",
    ),
    path(
        "course-owner404/<int:pk>",
        CourseOwnerDetailView404.as_view(),
        name="course-owner-detail-404",
    ),
    path("", IndexView.as_view(), name="index"),
]
