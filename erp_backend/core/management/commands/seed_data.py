
from django.core.management.base import BaseCommand
from core.models import Department, Employee, Project
from django.utils import timezone

class Command(BaseCommand):
    help = "Seed demo data: departments, users with roles, and projects"

    def handle(self, *args, **options):
        eng, _ = Department.objects.get_or_create(name="Engineering", defaults={"budget":"1000000.00"})
        hr, _ = Department.objects.get_or_create(name="HR", defaults={"budget":"200000.00"})
        sales, _ = Department.objects.get_or_create(name="Sales", defaults={"budget":"500000.00"})

        if not Employee.objects.filter(username="admin").exists():
            admin = Employee.objects.create_superuser(username="admin", email="admin@example.com", password="admin123", role="ADMIN")
            self.stdout.write(self.style.SUCCESS("Created admin: admin/admin123"))
        else:
            admin = Employee.objects.get(username="admin")

        if not Employee.objects.filter(username="manager").exists():
            manager = Employee.objects.create_user(username="manager", email="manager@example.com", password="manager123", role="MANAGER", department=eng, salary=1500000, first_name="Manny", last_name="Ger")
            self.stdout.write(self.style.SUCCESS("Created manager: manager/manager123"))
        else:
            manager = Employee.objects.get(username="manager")

        if not Employee.objects.filter(username="employee").exists():
            employee = Employee.objects.create_user(username="employee", email="employee@example.com", password="employee123", role="EMPLOYEE", department=eng, salary=800000, first_name="Emp", last_name="Loyee")
            self.stdout.write(self.style.SUCCESS("Created employee: employee/employee123"))
        else:
            employee = Employee.objects.get(username="employee")

        p1, _ = Project.objects.get_or_create(name="ERP Core", department=eng, defaults={"description":"Core services", "is_active":True})
        p2, _ = Project.objects.get_or_create(name="Mobile App", department=eng, defaults={"description":"iOS/Android App", "is_active":True})
        p3, _ = Project.objects.get_or_create(name="Recruitment Drive", department=hr, defaults={"description":"Campus hiring", "is_active":False})

        p1.employees.set([manager, employee])
        p2.employees.set([employee])
        p3.employees.set([])

        self.stdout.write(self.style.SUCCESS("Seed data ready."))
