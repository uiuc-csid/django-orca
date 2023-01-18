from django.views.generic.detail import DetailView

from django_orca.views import ObjectPermissionRequiredMixin

from .models import Course


class CourseDetailView(ObjectPermissionRequiredMixin, DetailView):
    model = Course
    permission_required = ["main.view_course", "main.change_course"]
