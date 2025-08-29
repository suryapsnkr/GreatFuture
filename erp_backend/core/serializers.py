
from rest_framework import serializers
from .models import Department, Employee, Project

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "budget", "created_at"]

class EmployeeListSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ["id", "username", "email", "first_name", "last_name", "role", "department", "salary", "title", "is_active"]

class EmployeeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "username", "password", "email", "first_name", "last_name", "role", "department", "salary", "title", "is_active"]
        extra_kwargs = { "password": {"write_only": True, "required": False} }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = Employee(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class ProjectSerializer(serializers.ModelSerializer):
    employees = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), many=True, required=False)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "department", "start_date", "end_date", "is_active", "employees"]
