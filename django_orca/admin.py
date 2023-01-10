from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import RolePermission, UserRole

admin.site.register(Permission)
admin.site.register(RolePermission)
admin.site.register(UserRole)
