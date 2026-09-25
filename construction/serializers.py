from rest_framework import serializers
from .models import ConstructionAgreement, ConstructionAgreementService, ConstructionAgreementPaymentSchedule
from sale.serializers import CustomerSerializer


class ConstructionAgreementServiceSerializer(serializers.ModelSerializer):
    uom_descr = serializers.CharField(source='uom.descr', read_only=True)

    class Meta:
        model = ConstructionAgreementService
        fields = ['key', 'id', 'service_desc', 'quantity', 'uom',
                  'uom_descr', 'rate_per_unit', 'amount', 'construction_agreement_id']


class ConstructionAgreementPaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionAgreementPaymentSchedule
        fields = ['key', 'id', 'payment_stage_desc',
                  'amount', 'construction_agreement_id']


class ConstructionAgreementSerializer(serializers.ModelSerializer):
    # customer = CustomerSerializer(source='customer_id', read_only=True)

    class Meta:
        model = ConstructionAgreement
        fields = '__all__'


class ConstructionAgreementGetSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source='customer_id.name', read_only=True)
    project_name = serializers.CharField(
        source='project_id.name', read_only=True)
    company_name = serializers.CharField(
        source='company_id.name', read_only=True)
    client_name = serializers.CharField(
        source='client_id.name', read_only=True)
    service_descriptions = ConstructionAgreementServiceSerializer(
        source='constructionagreementservice_set', many=True, read_only=True)
    payment_schedules = ConstructionAgreementPaymentScheduleSerializer(
        source='constructionagreementpaymentschedule_set', many=True, read_only=True)

    class Meta:
        model = ConstructionAgreement
        fields = [
            'key', 'id', 'agreement_no', 'agreement_date', 'customer_id', 'customer_name', 'project_id', 'unit_id', 'project_name',
            'company_name', 'client_name', 'contract_amount', 'paid_amount', 'notes',
            'service_descriptions', 'payment_schedules'
        ]


class ConstructionAgreementListSerializer(serializers.ModelSerializer):
    agreement_date =  serializers.DateField(format="%d-%m-%Y", read_only=True)
    customer_name = serializers.CharField(
        source='customer_id.name', read_only=True)
    project_name = serializers.CharField(
        source='project_id.name', read_only=True)
    company_name = serializers.CharField(
        source='company_id.name', read_only=True)
    client_name = serializers.CharField(
        source='client_id.name', read_only=True)
    balance_amount = serializers.SerializerMethodField()
    
    def get_balance_amount(self, obj):
        contract_amount = obj.contract_amount if obj.contract_amount is not None else 0.0
        paid_amount = obj.paid_amount if obj.paid_amount is not None else 0.0
        return float(contract_amount) - float(paid_amount)


    class Meta:
        model = ConstructionAgreement
        fields = [
            'key', 'id', 'agreement_no', 'agreement_date', 'customer_id', 'customer_name', 'project_id', 'project_name',
            'company_name', 'client_name', 'contract_amount', 'paid_amount', 'balance_amount'
        ]
