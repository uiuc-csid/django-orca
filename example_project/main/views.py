from django.views.generic.detail import DetailView

from django_orca.views import ObjectPermissionRequiredMixin, ObjectRoleRequiredMixin

from .models import Course
from .roles import CourseOwner


class CourseDetailView(ObjectPermissionRequiredMixin, DetailView):
    model = Course
    permission_required = ["main.view_course", "main.change_course"]


class CourseOwnerDetailView(ObjectRoleRequiredMixin, DetailView):
    model = Course
    role_required = CourseOwner
