from rest_framework import serializers
from .models import (Vendorcontract, VendorcontractStages, VendorcontractTasks, Contractor, ContractorType,
                     ContractAgreement, ContractAgreementService, ContractAgreementPaymentSchedule, ContractorInvoice, ContractInvAllocAmt, ContractVoucherHdr, ContractVoucherDtl)
from datetime import datetime, date
from pricing.models import Docstatus
from pricing.serializers import DocStatusSerializer
from project.serializers import ProjectSerializer
from vendor.serializers import VendorSerializer
from inventory.serializers import ItemtypeSerializer
from inventory.models import Itemtype
from inventory.serializers import ItemuomSerializer  # ItemSerializer
# from geolocation.models import State, City
from buildiq.super_serializer import DynamicFieldsModelSerializer
from django.db.models import Sum

class VendorContractSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    vendor = VendorSerializer(
        source='vend_key', read_only=True, fields=('key', 'id', 'name',))
    project = ProjectSerializer(
        source='proj_key', read_only=True, fields=('key', 'id', 'name',))
    vend_contract_stages = serializers.SerializerMethodField(read_only=True)
    vend_contract_tasks = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    def get_vend_contract_stages(self, contractKey):
        if VendorcontractStages.objects.filter(vendctr_key=contractKey).exists():
            conStagIns = VendorcontractStages.objects.filter(
                vendctr_key=contractKey)
            return VendorContractStagesSerializer(conStagIns, many=True).data
        return []

    def get_vend_contract_tasks(self, contractKey):
        if VendorcontractTasks.objects.filter(vendctr_key=contractKey).exists():
            conTaskIns = VendorcontractTasks.objects.filter(
                vendctr_key=contractKey)
            return VendorContractTasksSerializer(conTaskIns, many=True).data
        return []

    def get_status(self, venCon):
        if Docstatus.objects.filter(docstatus=venCon.docstatus).exists():
            return DocStatusSerializer(Docstatus.objects.get(docstatus=venCon.docstatus)).data
        return {}

    class Meta:
        model = Vendorcontract
        fields = '__all__'


class VendorContractStagesSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    itemuoms = ItemuomSerializer(
        source='itemuom_key', read_only=True, fields=('key', 'id', 'descr',))

    class Meta:
        model = VendorcontractStages
        fields = '__all__'


class VendorContractTasksSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    itemuoms = ItemuomSerializer(
        source='itemuom_key', read_only=True, fields=('key', 'id', 'descr',))

    class Meta:
        model = VendorcontractTasks
        fields = '__all__'


class ContractorTypeSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = ContractorType
        fields = '__all__'


class ContractorSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    type = ContractorTypeSerializer(source='Contractor_ContractorTyp_Key',
                                    read_only=True, fields=('key', 'id', 'descr'))

    class Meta:
        model = Contractor
        fields = '__all__'


class ContractorGetSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    type = ContractorTypeSerializer(source='Contractor_ContractorTyp_Key',
                                    read_only=True, fields=('key', 'id', 'descr'))
    contractor_type = serializers.CharField(source="contractortyp_key.descr")
    state = serializers.CharField(source="state_key.name", allow_null=True)
    city = serializers.CharField(source="city_key.name", allow_null=True)

    class Meta:
        model = Contractor
        fields = '__all__'

class ContractorPaymentSerializer(DynamicFieldsModelSerializer):
    type = ContractorTypeSerializer(source='contractortyp_key',
                                    read_only=True, fields=('key', 'id', 'descr'))

    class Meta:
        model = Contractor
        fields = ['key','name','type']


class ContractAgreementServiceSerializer(serializers.ModelSerializer):
    uom_descr = serializers.CharField(source='uom.descr', read_only=True)

    class Meta:
        model = ContractAgreementService
        fields = ['key', 'id', 'service_desc', 'quantity', 'uom',
                  'uom_descr', 'rate_per_unit', 'cost', 'contract_agreement_id']


class ContractAgreementPaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractAgreementPaymentSchedule
        fields = ['key', 'id', 'payment_stage_desc',
                  'amount', 'contract_agreement_id']


class ContractAgreementSerializer(serializers.ModelSerializer):
    contractor = ContractorSerializer(source='contractor_id', read_only=True)
    class Meta:
        model = ContractAgreement
        fields = '__all__'

class ContractAgreementGetSerializer(serializers.ModelSerializer):
    contractor = ContractorSerializer(source='contractor_id', read_only=True)
    contractor_name = serializers.CharField(
        source='contractor_id.name', read_only=True)
    contractor_type = serializers.CharField(
        source='contractor_id.vendtyp_key.descr', read_only=True)
    project_name = serializers.CharField(
        source='project_id.name', read_only=True)
    company_name = serializers.CharField(
        source='company_id.name', read_only=True)
    client_name = serializers.CharField(
        source='client_id.name', read_only=True)
    service_descriptions = ContractAgreementServiceSerializer(
        source='contractagreementservice_set', many=True, read_only=True)
    payment_schedules = ContractAgreementPaymentScheduleSerializer(
        source='contractagreementpaymentschedule_set', many=True, read_only=True)

    class Meta:
        model = ContractAgreement
        fields = [
            'key', 'id', 'agreement_no', 'agreement_date','contractor', 'contractor_id', 'contractor_type', 'contractor_name', 'project_id', 'project_name',
            'company_name', 'client_name', 'total_amount', 'paid_amount', 'notes',
            'service_descriptions', 'payment_schedules'
        ]


class ContractAgreementListSerializer(serializers.ModelSerializer):
    agreement_date =  serializers.DateField(format="%d-%m-%Y", read_only=True)
    contractor_name = serializers.CharField(
        source='contractor_id.name', read_only=True)
    contractor_type = serializers.CharField(
        source='contractor_id.contractortyp_key.descr', read_only=True)
    project_name = serializers.CharField(
        source='project_id.name', read_only=True)
    company_name = serializers.CharField(
        source='company_id.name', read_only=True)
    client_name = serializers.CharField(
        source='client_id.name', read_only=True)

    class Meta:
        model = ContractAgreement
        fields = [
            'key', 'id', 'agreement_no', 'agreement_date', 'contractor_id', 'contractor_type', 'contractor_name', 'project_id', 'project_name',
            'company_name', 'client_name', 'total_amount', 'paid_amount'
        ]


class ContractorInvoiceSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    class Meta:
        model = ContractorInvoice
        fields = '__all__'


class ContractInvAllocAmtSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractInvAllocAmt
        fields = '__all__'


class ContractInvAllocAmtGetSerializer(serializers.ModelSerializer):
    invoice_no = serializers.CharField(source="invoice_id.invoice_id")
    invoice_date = serializers.DateField(source="invoice_id.invoice_date")
    project_name = serializers.CharField(source="invoice_id.project_id.name")

    class Meta:
        model = ContractInvAllocAmt
        fields ='__all__'

class ContractVoucherDtlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractVoucherDtl
        fields = '__all__'

class ContractVoucherDtlGetSerializer(serializers.ModelSerializer):
    invoice_no = serializers.CharField(source="invoice_id.invoice_id")
    invoice_date = serializers.DateField(source="invoice_id.invoice_date")
    invoice_amount = serializers.DecimalField(source="invoice_id.invoice_amount", max_digits=15, decimal_places=2)
    project_name = serializers.CharField(source="invoice_id.project_id.name")
    pending_amount = serializers.SerializerMethodField()

    def get_pending_amount(self, obj):
        invoice_amount = obj.invoice_id.invoice_amount if obj.invoice_id.invoice_amount is not None else 0.0
        paid_amount = obj.paid_amount if obj.paid_amount is not None else 0.0
        return float(invoice_amount) - float(paid_amount)


    class Meta:
        model = ContractVoucherDtl
        fields = [
            'key', 'invoice_no', 'invoice_date', 'invoice_amount', 'project_name', 'pending_amount',
            'paid_amount'
        ]


class ContractVoucherHdrSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = ContractVoucherHdr
        fields = '__all__'


class ContractVoucherHdrListSerializer(serializers.ModelSerializer):
    contract_voucher_dt =  serializers.DateField(format="%d-%m-%Y", read_only=True)
    payment_mode = serializers.CharField(source="payment_mode_id.descr")
    contractor_name = serializers.CharField(source="contractor_id.name")
    invoice_id = serializers.SerializerMethodField()

    class Meta:
        model = ContractVoucherHdr
        fields = ['key','contract_voucher_dt','voucher_number','invoice_id','contractor_name','total_amount','payment_mode','notes']
    
    def get_invoice_id(self, obj):
        details = ContractVoucherDtl.objects.filter(contract_voucher_hdr=obj) 
        return [d.invoice_id.invoice_id for d in details]


class ContractVoucherHdrGetSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company_id.name")
    acc_name = serializers.CharField(source="account_id.acc_name",allow_null=True)
    payment_mode = serializers.CharField(source="payment_mode_id.descr")
    contract_voucher_detail = serializers.SerializerMethodField()

    def get_contract_voucher_detail(self, obj):
        contract_voucher_dtl = ContractVoucherDtl.objects.filter(contract_voucher_hdr=obj.key)
        if contract_voucher_dtl is not None:
            serializer = ContractVoucherDtlGetSerializer(contract_voucher_dtl, many=True)
            return serializer.data
        return None
    
    class Meta:
        model = ContractVoucherHdr
        fields = ['key','contract_voucher_dt','voucher_number','company_name', 'acc_name', 'payment_mode', 'transaction_detail', 'total_amount','notes','contract_voucher_detail']


class PayContractorSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project_id.name")
    pending_amount = serializers.SerializerMethodField()
    contractor_details = serializers.SerializerMethodField()
    allocated_amount = serializers.SerializerMethodField()
    allocated_amount_details = serializers.SerializerMethodField()

    class Meta:
        model = ContractorInvoice
        fields = [
            'key', 'invoice_id', 'invoice_date', 'project_name',
            'invoice_amount', 'pending_amount',
            'allocated_amount', 'allocated_amount_details',
            'contractor_details'
        ]

    def get_pending_amount(self, obj):
        invoice_amount = obj.invoice_amount or 0.0
        paid_amount = obj.paid_amount or 0.0
        return float(invoice_amount) - float(paid_amount)

    def get_contractor_details(self, obj):
        if obj.contractor_id is None:
            return None
        try:
            contractor_obj = Contractor.objects.get(key=obj.contractor_id.key)
            return ContractorPaymentSerializer(contractor_obj).data
        except Contractor.DoesNotExist:
            return None

    def get_allocated_amount(self, obj):
        total_allocated = (
            ContractInvAllocAmt.objects.filter(invoice_id=obj.key)
            .aggregate(Sum('allocated_amount'))['allocated_amount__sum']
        )
        return total_allocated or 0.0

    def get_allocated_amount_details(self, obj):
        qs = ContractInvAllocAmt.objects.filter(invoice_id=obj.key)
        if qs.exists():
            return ContractInvAllocAmtSerializer(qs, many=True).data
        return []

class PayInvoiceSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", read_only=True)
    project_name = serializers.CharField(source="project_id.name")
    pending_amount = serializers.SerializerMethodField()
    contractor_details = serializers.SerializerMethodField()
    allocated_amount = serializers.SerializerMethodField()
    allocated_amount_details = serializers.SerializerMethodField()

    class Meta:
        model = ContractorInvoice
        fields = ['key', 'project_name', 'invoice_id', 'invoice_date','invoice_amount', 'pending_amount', 'contractor_details', 'allocated_amount', 'allocated_amount_details']

    def get_pending_amount(self, obj):
        if obj.paid_amount is None or obj.paid_amount == 0:
            return obj.invoice_amount
        else:
            return float(obj.invoice_amount) - float(obj.paid_amount)

    def get_contractor_details(self, obj):
        try:
            if obj.contractor_id is not None:
                contractor_obj = Contractor.objects.get(key=obj.contractor_id.key)
                serializer = ContractorPaymentSerializer(contractor_obj)
                return serializer.data
            else:
                return None
        except (Contractor.DoesNotExist):
            return None
        
    def get_allocated_amount(self, obj):
        total = ContractInvAllocAmt.objects.filter(invoice_id=obj.key).aggregate(Sum('allocated_amount'))['allocated_amount__sum']
        return total or 0.00

    def get_allocated_amount_details(self, obj):
        qs = ContractInvAllocAmt.objects.filter(invoice_id=obj.key)
        return ContractInvAllocAmtSerializer(qs, many=True).data if qs.exists() else []
