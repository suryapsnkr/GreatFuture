
from django.contrib import admin
from .models import Department, Employee, Project
from django.contrib.auth.admin import UserAdmin

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "budget", "created_at")
    search_fields = ("name",)

@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("ERP Fields", {"fields": ("role", "department", "salary", "title")}),
    )
    list_display = ("id", "username", "email", "role", "department", "salary", "is_active")
    list_filter = ("role", "department")
    search_fields = ("username", "email", "first_name", "last_name")

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "department", "is_active", "start_date", "end_date")
    list_filter = ("is_active", "department")
    search_fields = ("name", "description")
