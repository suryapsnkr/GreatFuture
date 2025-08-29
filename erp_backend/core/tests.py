
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Department, Employee

class SmokeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.dept = Department.objects.create(name="QA")
        self.admin = Employee.objects.create_user(username="admin", password="admin123", role="ADMIN")
        resp = self.client.post("/api/auth/token/", {"username":"admin","password":"admin123"}, format="json")
        self.token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_create_department(self):
        r = self.client.post("/api/departments/", {"name":"Eng","budget":"1000000.00"}, format="json")
        self.assertEqual(r.status_code, 201)
