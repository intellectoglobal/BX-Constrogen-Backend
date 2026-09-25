from rest_framework import serializers
from .models import SalaryAndAllowance
from buildiq.super_serializer import DynamicFieldsModelSerializer


class SalaryAndAllowanceSerializer(DynamicFieldsModelSerializer):
    date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    project = serializers.CharField(source='project_key.name',read_only=True)
    payee_name = serializers.CharField(
        source="employee.first_name", read_only=True)
    
    class Meta:
        model = SalaryAndAllowance
        fields = '__all__'
