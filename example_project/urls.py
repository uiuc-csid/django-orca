from django.contrib import admin
from django.urls import path

from example_project.main.views import CourseDetailView, CourseOwnerDetailView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("course/<int:pk>", CourseDetailView.as_view(), name="course-detail"),
    path(
        "course-owner/<int:pk>",
        CourseOwnerDetailView.as_view(),
        name="course-owner-detail",
    ),
]
