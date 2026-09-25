from rest_framework import serializers
from .models import Vendortype, Vendorgroup, Vendor, Apterms, VendorItemType, VendorInvAllocAmt, VendorPaymentVoucherHdr, VendorPaymentVoucherDtl
from datetime import datetime, date
from buildiq.super_serializer import DynamicFieldsModelSerializer
from inventory.serializers import ItemtypeSerializer
from inventory.models import Itemtype
from pricing.models import Vendorinvoice


class VendorTypeSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Vendortype
        fields = '__all__'


class VendorGroupSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Vendorgroup
        fields = '__all__'


class ApTermsSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Apterms
        fields = '__all__'


class VendorItemTypeSerializer(DynamicFieldsModelSerializer):
    itemType = ItemtypeSerializer(source='item_type_key',read_only=True)
    class Meta:
        model = VendorItemType
        fields = '__all__'
        
class VendorSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    group = VendorGroupSerializer(source='vendgrp_key',
                                  read_only=True, fields=('key', 'id', 'descr'))
    type = VendorTypeSerializer(source='vendtyp_key',
                                read_only=True, fields=('key', 'id', 'descr', 'contractor'))
    itemtypes = serializers.SerializerMethodField(read_only=True)

    invoice_list = serializers.SerializerMethodField(read_only=True)
    state = serializers.CharField(source="state_key.name",read_only=True)
    city = serializers.CharField(source="city_key.name",read_only=True)

    def get_itemtypes(self, vendor):
        vendorItemTypes=[]
        for itemType in VendorItemType.objects.filter(vend_key=vendor):
            vendorItemTypes.append(VendorItemTypeSerializer(itemType).data)
        return vendorItemTypes

    def get_invoice_list(self, vendor):
        invoices = []
        if Vendorinvoice.objects.filter(vend_key=vendor).exists():
            invoiceInst = Vendorinvoice.objects.filter(vend_key=vendor)
            for inv in invoiceInst:
                # ding loop to avoid circular import on Vendorinvoiceserialiser
                invoices.append({
                    "key": inv.key,
                    "docid": inv.invoiceno,
                    "vouchno": inv.invoiceno,
                    "invoiceno": inv.invoiceno,
                    "invnotes": inv.invnotes,
                    "invoicedate": inv.invoicedate,
                    # "duedate": inv.duedate,
                    # "proj_key": inv.proj_key,
                    "invamt": inv.invamt,
                    "balamt": inv.balamt,
                    # "docstatus": inv.status
                })
                
                
        return invoices

    class Meta:
        model = Vendor
        fields = '__all__'


class VendorPaymentSerializer(DynamicFieldsModelSerializer):
    type = VendorTypeSerializer(source='vendtyp_key',
                                    read_only=True, fields=('key', 'id', 'descr'))

    class Meta:
        model = Vendor
        fields = ['key','name','type']


class VendorInvAllocAmtSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorInvAllocAmt
        fields = '__all__'


class PayVendorSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="proj_key.name")
    pending_amount = serializers.SerializerMethodField()
    vendor_details = serializers.SerializerMethodField()
    allocated_amount = serializers.SerializerMethodField()
    allocated_amount_details = serializers.SerializerMethodField()

    class Meta:
        model = Vendorinvoice
        fields = ['key','invoiceno', 'invoicedate', 'project_name', 'invamt', 'pending_amount', 'allocated_amount','allocated_amount_details' ,'vendor_details', 'netamt']

    def get_pending_amount(self, obj):
        netamt = obj.netamt if obj.netamt is not None else 0.0
        paid_amount = obj.paid_amount if obj.paid_amount is not None else 0.0
        
        if paid_amount == 0:
            return netamt
        else:
            return float(netamt) - float(paid_amount)


    def get_vendor_details(self, obj):
        try:
            if obj.vend_key is not None:
                vendor_obj = Vendor.objects.get(key=obj.vend_key.key)
                serializer = VendorPaymentSerializer(vendor_obj)
                return serializer.data
            else:
                return None
        except (Vendor.DoesNotExist):
            return None
        
    def get_allocated_amount_details(self,obj):
        try:
            allocated_amount_obj = VendorInvAllocAmt.objects.get(invoice_id=obj.key)
            serializer = VendorInvAllocAmtSerializer(allocated_amount_obj)
            return serializer.data
        except VendorInvAllocAmt.DoesNotExist:
            return None
    
    def get_allocated_amount(self,obj):
        try:
            allocated_amount_obj = VendorInvAllocAmt.objects.get(invoice_id=obj.key)
            serializer = VendorInvAllocAmtSerializer(allocated_amount_obj)
            return serializer.data['allocated_amount']
        except VendorInvAllocAmt.DoesNotExist:
            return None



class PayVendorInvoiceSerializer(serializers.ModelSerializer):
    invoicedate =  serializers.DateField(format="%d-%m-%Y", read_only=True)
    project_name = serializers.CharField(source="proj_key.name")
    pending_amount = serializers.SerializerMethodField()
    vendor_details = serializers.SerializerMethodField()
    allocated_amount = serializers.SerializerMethodField()
    allocated_amount_details = serializers.SerializerMethodField()

    class Meta:
        model = Vendorinvoice
        fields = ['key', 'project_name', 'invoiceno', 'invoicedate','invamt', 'pending_amount', 'vendor_details','allocated_amount', 'allocated_amount_details', 'netamt']

    def get_pending_amount(self, obj):
        netamt = obj.netamt if obj.netamt is not None else 0.0
        paid_amount = obj.paid_amount if obj.paid_amount is not None else 0.0
        
        if paid_amount == 0:
            return netamt
        else:
            return float(netamt) - float(paid_amount)


    def get_vendor_details(self, obj):
        try:
            if obj.vend_key is not None:
                contractor_obj = Vendor.objects.get(key=obj.vend_key.key)
                serializer = VendorPaymentSerializer(contractor_obj)
                return serializer.data
            else:
                return None
        except (Vendor.DoesNotExist):
            return None
        
    def get_allocated_amount_details(self,obj):
        try:
            allocated_amount_obj = VendorInvAllocAmt.objects.get(invoice_id=obj.key)
            serializer = VendorInvAllocAmtSerializer(allocated_amount_obj)
            return serializer.data
        except VendorInvAllocAmt.DoesNotExist:
            return None
    
        
    def get_allocated_amount(self,obj):
        try:
            allocated_amount_obj = VendorInvAllocAmt.objects.get(invoice_id=obj.key)
            serializer = VendorInvAllocAmtSerializer(allocated_amount_obj)
            return serializer.data['allocated_amount']
        except VendorInvAllocAmt.DoesNotExist:
            return None
        

class VendorVoucherDtlSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPaymentVoucherDtl
        fields = '__all__'


class VendorVoucherDtlGetSerializer(serializers.ModelSerializer):
    invoice_no = serializers.CharField(source="invoice_id.invoiceno")
    invoice_date = serializers.DateField(source="invoice_id.invoicedate")
    netamt = serializers.DecimalField(source="invoice_id.netamt", max_digits=15, decimal_places=2)
    project_name = serializers.CharField(source="invoice_id.proj_key.name")
    pending_amount = serializers.SerializerMethodField()

    def get_pending_amount(self, obj):
        netamt = obj.invoice_id.netamt if obj.invoice_id.netamt is not None else 0.0
        paid_amount = obj.paid_amount if obj.paid_amount is not None else 0.0
        
        if paid_amount == 0:
            return netamt
        else:
            return float(netamt) - float(paid_amount)


    class Meta:
        model = VendorPaymentVoucherDtl
        fields = [
            'key', 'invoice_no', 'invoice_date', 'netamt', 'project_name', 'pending_amount',
            'paid_amount'
        ]


class VendorVoucherHdrSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VendorPaymentVoucherHdr
        fields = '__all__'


class VendorVoucherHdrListSerializer(serializers.ModelSerializer):
    vendor_voucher_dt =  serializers.DateField(format="%d-%m-%Y", read_only=True)
    payment_mode = serializers.CharField(source="payment_mode_id.descr")
    vendor_name = serializers.CharField(source="vendor_id.name")
    invoiceno = serializers.SerializerMethodField()

    class Meta:
        model = VendorPaymentVoucherHdr
        fields = ['key','vendor_voucher_dt','invoiceno','voucher_number','vendor_name','total_amount','payment_mode','notes']
    def get_invoiceno(self, obj):
        details = VendorPaymentVoucherDtl.objects.filter(vendor_voucher_hdr=obj)
        numbers = [d.invoice_id.invoiceno for d in details]
        return ", ".join(numbers)

class VendorVoucherHdrGetSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor_id.name")
    company_name = serializers.CharField(source="company_id.name")
    acc_name = serializers.CharField(source="account_id.acc_name",allow_null=True)
    payment_mode = serializers.CharField(source="payment_mode_id.descr")
    vendor_voucher_detail = serializers.SerializerMethodField()

    def get_vendor_voucher_detail(self, obj):
        vendor_voucher_dtl = VendorPaymentVoucherDtl.objects.filter(vendor_voucher_hdr=obj.key)
        if vendor_voucher_dtl is not None:
            serializer = VendorVoucherDtlGetSerializer(vendor_voucher_dtl, many=True)
            return serializer.data
        return None
    
    class Meta:
        model = VendorPaymentVoucherHdr
        fields = ['key', 'vendor_voucher_dt', 'voucher_number', 'vendor_name', 'company_name', 'acc_name', 'payment_mode', 'transaction_detail', 'total_amount', 'notes', 'vendor_voucher_detail']
