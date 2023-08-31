from typing import Any, Dict

from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django_orca.views import ObjectPermissionRequiredMixin, ObjectRoleRequiredMixin

from .models import Course, Department
from .roles import CourseOwner


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["courses"] = Course.objects.all()
        context["departments"] = Department.objects.all()
        return context


class DepartmentDetailView(ObjectPermissionRequiredMixin, DetailView):
    model = Department
    permission_required = "main.view_department"


class CourseDetailView(ObjectPermissionRequiredMixin, DetailView):
    model = Course
    permission_required = ["main.view_course", "main.change_course"]


class CourseOwnerDetailView(ObjectRoleRequiredMixin, DetailView):
    model = Course
    role_required = CourseOwner


class CourseDetailView404(ObjectPermissionRequiredMixin, DetailView):
    model = Course
    return_404 = True
    permission_required = ["main.view_course", "main.change_course"]


class CourseOwnerDetailView404(ObjectRoleRequiredMixin, DetailView):
    model = Course
    return_404 = True
    role_required = CourseOwner
