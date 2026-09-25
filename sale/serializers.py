from rest_framework import serializers
from .models import Customer, CustomerPurchaseReceipt, SaleAgreement, SaleAgreementRateCard, SaleAgreementPaymentSchedule, SaleInvoice, SourceOfFund, SaleReceipt
from datetime import datetime


class CustomerSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Customer
        fields = '__all__'


class CustomerPurchaseReceiptSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField(read_only=True)
    customer_name = serializers.SerializerMethodField(read_only=True)

    def get_project_name(self, obj):
        return obj.project_key.name

    def get_customer_name(self, obj):
        return obj.customer_key.name
    
    class Meta:
        model = CustomerPurchaseReceipt
        fields = '__all__'


class SaleAgreementRateCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleAgreementRateCard
        fields = '__all__'


class SaleAgreementPaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleAgreementPaymentSchedule
        fields = '__all__'


class SaleAgreementSerializer(serializers.ModelSerializer):
    contractor = CustomerSerializer(source='customer_id', read_only=True)

    class Meta:
        model = SaleAgreement
        fields = '__all__'


class SaleAgreementGetSerializer(serializers.ModelSerializer):
    unit_descr = serializers.CharField(
        source='unit_id.descr', read_only=True)
    customer_name = serializers.CharField(
        source='customer_id.name', read_only=True)
    project_name = serializers.CharField(
        source='project_id.name', read_only=True)
    company_name = serializers.CharField(
        source='company_id.name', read_only=True)
    client_name = serializers.CharField(
        source='client_id.name', read_only=True)
    rate_cards = SaleAgreementRateCardSerializer(
        source='saleagreementratecard_set', many=True, read_only=True)
    payment_schedules = SaleAgreementPaymentScheduleSerializer(
        source='saleagreementpaymentschedule_set', many=True, read_only=True)

    class Meta:
        model = SaleAgreement
        fields = [
            'key', 'id', 'agreement_no', 'agreement_date', 'unit_id', 'unit_descr', 'customer_id', 'customer_name', 'project_id', 'project_name',
            'company_name', 'client_name', 'sale_amount', 'paid_amount', 'notes',
            'rate_cards', 'payment_schedules'
        ]


class SaleAgreementListSerializer(serializers.ModelSerializer):
    agreement_date =  serializers.DateField(format="%d-%m-%Y", read_only=True)
    customer_name = serializers.CharField(
        source='customer_id.name', read_only=True)
    unit_desc = serializers.CharField(
        source='unit_id.descr', read_only=True)
    project_name = serializers.CharField(
        source='project_id.name', read_only=True)
    company_name = serializers.CharField(
        source='company_id.name', read_only=True)
    client_name = serializers.CharField(
        source='client_id.name', read_only=True)
    balance_amount = serializers.SerializerMethodField()

    def get_balance_amount(self, obj):
        sale_amount = obj.sale_amount if obj.sale_amount is not None else 0.0
        paid_amount = obj.paid_amount if obj.paid_amount is not None else 0.0

        if paid_amount == 0:
            return sale_amount
        else:
            return float(sale_amount) - float(paid_amount)

    class Meta:
        model = SaleAgreement
        fields = [
            'key', 'id', 'agreement_no', 'agreement_date', 'customer_id', 'customer_name', 'unit_id', 'unit_desc', 'project_id', 'project_name',
            'company_name', 'client_name', 'sale_amount', 'paid_amount', 'balance_amount'
        ]

class SaleInvoiceSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    class Meta:
        model = SaleInvoice
        fields = '__all__'


class ReceiveSaleInvoiceSerializer(serializers.ModelSerializer):
    invoice_date =  serializers.DateField(format="%d-%m-%Y", read_only=True)
    pending_amount = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source="agreement_id.customer_id.name")
    project_name = serializers.CharField(source="project_id.name")
    unit_name = serializers.CharField(source="agreement_id.unit_id.descr")

    class Meta:
        model = SaleInvoice
        fields = '__all__'

    def get_pending_amount(self, obj):
        invoice_amount = obj.invoice_amount if obj.invoice_amount is not None else 0.0
        paid_amount = obj.paid_amount if obj.paid_amount is not None else 0.0
        
        if paid_amount == 0:
            return invoice_amount
        else:
            return float(invoice_amount) - float(paid_amount)


class SourceOfFundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceOfFund
        fields = '__all__'


class SaleReceiptSerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    customer_name = serializers.CharField(source="customer_id.name",read_only=True)
    payment_mode = serializers.CharField(source="payment_mode_id.descr",read_only=True)
    account_name = serializers.CharField(source="account_id.acc_name",read_only=True, allow_null=True)
    source_of_fund_name = serializers.CharField(source="source_of_fund_id.name",read_only=True)

    class Meta:
        model = SaleReceipt
        fields = '__all__'
