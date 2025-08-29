
from django.db.models import Sum, Count
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import Department, Employee, Project
from .serializers import DepartmentSerializer, EmployeeListSerializer, EmployeeWriteSerializer, ProjectSerializer
from .permissions import IsAdmin, IsManager, IsEmployee
import csv

class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name"]

    def get_queryset(self):
        user = self.request.user
        qs = Department.objects.all()
        # Managers and Employees can only see their department by default
        if getattr(user, "role", "") in ["MANAGER", "EMPLOYEE"] and user.department_id:
            return qs.filter(id=user.department_id)
        return qs

    def get_permissions(self):
        # Only Admins can create/update/delete departments
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields = ["username", "email", "first_name", "last_name", "title", "role"]
    ordering_fields = ["username", "salary", "role"]

    def get_queryset(self):
        user = self.request.user
        qs = Employee.objects.all()
        if getattr(user, "role", "") == "ADMIN":
            return qs
        if getattr(user, "role", "") == "MANAGER":
            return qs.filter(department=user.department)
        # employees can only see themselves
        return qs.filter(id=user.id)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return EmployeeListSerializer
        return EmployeeWriteSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "DELETE"]:
            # Only Admins can create new employees or delete
            return [IsAuthenticated(), IsAdmin()]
        if self.request.method in ["PUT", "PATCH"]:
            # Admin can edit anyone; manager can edit within department (not role=ADMIN); employee can edit self (limited)
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if getattr(user, "role", "") == "MANAGER":
            # Manager can modify only within department and cannot elevate to ADMIN
            if instance.department_id != user.department_id:
                return Response({ "detail": "Forbidden: different department." }, status=403)
            if request.data.get("role") == "ADMIN":
                return Response({ "detail": "Forbidden: cannot set ADMIN role." }, status=403)
        if getattr(user, "role", "") == "EMPLOYEE" and instance.id != user.id:
            return Response({ "detail": "Forbidden: employees can only update their own profile." }, status=403)
        return super().update(request, *args, **kwargs)

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "start_date", "end_date", "is_active"]

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.all()
        if getattr(user, "role", "") == "ADMIN":
            return qs
        if getattr(user, "role", "") == "MANAGER":
            return qs.filter(department=user.department)
        return qs.filter(employees=user)

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", "") == "MANAGER":
            # force project into manager's department
            serializer.save(department=user.department)
        else:
            serializer.save()

    def get_permissions(self):
        if self.request.method == "DELETE":
            # Only Admin can delete projects
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

class ReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        kind = request.query_params.get("type")
        user = request.user

        if kind == "employees_by_department":
            qs = Department.objects.all()
            if getattr(user, "role", "") in ["MANAGER", "EMPLOYEE"] and user.department_id:
                qs = qs.filter(id=user.department_id)
            data = []
            for dept in qs:
                employees = dept.employees.all().values("id", "username", "email", "role", "salary", "title")
                data.append({ "department": dept.name, "count": dept.employees.count(), "employees": list(employees) })
            return Response(data)

        if kind == "salary_cost_per_department":
            qs = Department.objects.all()
            if getattr(user, "role", "") in ["MANAGER", "EMPLOYEE"] and user.department_id:
                qs = qs.filter(id=user.department_id)
            agg = qs.annotate(total_salary=Sum("employees__salary")).values("id", "name", "total_salary").order_by("name")
            return Response(list(agg))

        if kind == "active_projects":
            qs = Project.objects.filter(is_active=True)
            if getattr(user, "role", "") == "MANAGER":
                qs = qs.filter(department=user.department)
            if getattr(user, "role", "") == "EMPLOYEE":
                qs = qs.filter(employees=user)
            data = list(qs.values("id", "name", "department__name", "start_date", "end_date"))
            return Response(data)

        return Response({ "detail": "Unknown or missing report 'type'." }, status=400)

class ExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        kind = request.query_params.get("type")
        if kind == "employees_csv":
            return self._export_employees_csv(request)
        if kind == "projects_csv":
            return self._export_projects_csv(request)
        if kind == "departments_csv":
            return self._export_departments_csv(request)
        return Response({ "detail": "Unknown export type." }, status=400)

    def _export_employees_csv(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="employees.csv"'
        writer = csv.writer(response)
        writer.writerow(["id","username","email","role","department","salary","title","is_active"])
        qs = Employee.objects.all()
        user = request.user
        if getattr(user, "role", "") == "MANAGER":
            qs = qs.filter(department=user.department)
        if getattr(user, "role", "") == "EMPLOYEE":
            qs = qs.filter(id=user.id)
        for e in qs.select_related("department"):
            writer.writerow([e.id, e.username, e.email, e.role, e.department.name if e.department else "", e.salary, e.title, e.is_active])
        return response

    def _export_projects_csv(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="projects.csv"'
        writer = csv.writer(response)
        writer.writerow(["id","name","department","is_active","start_date","end_date","employee_count"])
        qs = Project.objects.all()
        user = request.user
        if getattr(user, "role", "") == "MANAGER":
            qs = qs.filter(department=user.department)
        if getattr(user, "role", "") == "EMPLOYEE":
            qs = qs.filter(employees=user)
        for p in qs.select_related("department").annotate(emp_count=Count("employees")):
            writer.writerow([p.id, p.name, p.department.name if p.department else "", p.is_active, p.start_date, p.end_date, p.emp_count])
        return response

    def _export_departments_csv(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="departments.csv"'
        writer = csv.writer(response)
        writer.writerow(["id","name","budget","created_at","employee_count","project_count"])
        qs = Department.objects.all()
        user = request.user
        if getattr(user, "role", "") in ["MANAGER", "EMPLOYEE"] and user.department_id:
            qs = qs.filter(id=user.department_id)
        qs = qs.annotate(emp_count=Count("employees"), proj_count=Count("projects"))
        for d in qs:
            writer.writerow([d.id, d.name, d.budget, d.created_at, d.emp_count, d.proj_count])
        return response
