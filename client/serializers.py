from rest_framework import serializers
from .models import Company, Clientbase, Costcategory, Costcode, BankAccount
from users.models import AppUser
from datetime import datetime
from buildiq.super_serializer import DynamicFieldsModelSerializer
from project.models import Projectstatus
from project.serializers import ProjectStatusSerializer

class ClientBaseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = Clientbase
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    project_status = serializers.SerializerMethodField(read_only=True)
    client_data = ClientBaseSerializer('client',read_only=True)
    def get_project_status(self, company):
        projectstatusList = []
        if Projectstatus.objects.filter(company=company.id,client_id=company.client.id).exists():
            projectstatusInstance = Projectstatus.objects.filter(company=company.id,client_id=company.client.id)
            return ProjectStatusSerializer(projectstatusInstance,many=True,fields=('key','descr','is_active')).data
        return []
    class Meta:
        model = Company
        fields = '__all__'


class CostcategorySerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Costcategory
        fields = '__all__'


class CostcodeSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    cost_category = CostcategorySerializer(source='costctg_key',
                                           read_only=True, fields=('key', 'id', 'descr',))

    class Meta:
        model = Costcode
        fields = '__all__'


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'
