
from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Employee(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        EMPLOYEE = "EMPLOYEE", "Employee"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.EMPLOYEE)
    department = models.ForeignKey(Department, related_name="employees", on_delete=models.SET_NULL, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    title = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, related_name="projects", on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    employees = models.ManyToManyField(Employee, related_name="projects", blank=True)

    def __str__(self):
        return self.name
