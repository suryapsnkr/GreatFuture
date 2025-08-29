
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core.views import DepartmentViewSet, EmployeeViewSet, ProjectViewSet, ReportsView, ExportView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/reports/", ReportsView.as_view(), name="reports"),
    path("api/export/", ExportView.as_view(), name="export"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
