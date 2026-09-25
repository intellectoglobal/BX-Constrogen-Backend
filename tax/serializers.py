from rest_framework import serializers
from .models import TdsEntry, TdsReport, SalesTds, PurchaseGstEntry, PurchaseGstReport, SalesGstEntry, SalesGstReport


class TdsEntrySerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    invoice_no = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()
    invoice_amount = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = TdsEntry

    def get_invoice_no(self, obj):
        if obj.invoice_type == 'C' and obj.contractor_invoice:
            return obj.contractor_invoice.invoice_id
        elif obj.invoice_type == 'V' and obj.vendor_invoice:
            return obj.vendor_invoice.invoiceno
        return None

    def get_vendor_name(self,obj):
        if obj.invoice_type == 'C' and obj.contractor_invoice:
            return obj.contractor_invoice.contractor_id.name
        elif obj.invoice_type == 'V' and obj.vendor_invoice:
            return obj.vendor_invoice.vend_key.name
        return None
    
    def get_invoice_amount(self,obj):
        if obj.contractor_invoice:
            invoice_amount = obj.contractor_invoice.invoice_amount
        else:
            invoice_amount = obj.vendor_invoice.invamt
        return invoice_amount


class TdsReportSerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    vendor_name = serializers.SerializerMethodField()
    vendor_pan = serializers.SerializerMethodField()

    def get_vendor_name(self, obj):
        if obj.entity_type == 'C' and obj.contractor:
            return obj.contractor.name
        elif obj.entity_type == 'V' and obj.vendor:
            return obj.vendor.name
        return None
    
    def get_vendor_pan(self, obj):
        if obj.entity_type == 'C' and obj.contractor:
            return obj.contractor.pan_no
        elif obj.entity_type == 'V' and obj.vendor:
            return obj.vendor.pan_no
        return None

    class Meta:
        fields = '__all__'
        model = TdsReport

class SalesTdsSerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    project_name = serializers.CharField(source="project.name",read_only= True)
    unit_name = serializers.CharField(source="unit.descr",read_only= True)
    customer_name = serializers.CharField(source="customer.name",read_only= True)
    agreement_amount = serializers.DecimalField(max_digits=15, decimal_places=2, source="invoice.agreement_id.sale_amount",read_only= True)

    class Meta:
        fields = '__all__'
        model = SalesTds


class PurchaseGstEntrySerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    vendor_name = serializers.CharField(source="vendor.name",read_only= True)
    invoice_no = serializers.CharField(source="invoice.invoiceno",read_only= True)
    invoice_amount = serializers.DecimalField(max_digits=15, decimal_places=2, source="invoice.invamt",read_only= True)
    gst_number = serializers.CharField(source="vendor.gstnumber",read_only= True, allow_null= True)

    class Meta:
        fields = '__all__'
        model = PurchaseGstEntry


class PurchaseGstReportSerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    vendor_name = serializers.CharField(source="vendor.name",read_only= True)
    invoice_no = serializers.CharField(source="invoice.invoiceno",read_only= True)

    class Meta:
        fields = '__all__'
        model = PurchaseGstReport


class SalesGstEntrySerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    project_name = serializers.CharField(source="project.name",read_only= True)
    customer_name = serializers.CharField(source="customer.name",read_only= True)
    unit_name = serializers.CharField(source="unit.descr",read_only= True)
    sale_area = serializers.CharField(source="unit.saleablearea",read_only= True)
    carpet_area = serializers.CharField(source="unit.carpetarea",read_only= True)
    agreement_amount = serializers.DecimalField(max_digits=15, decimal_places=2, source="invoice.agreement_id.sale_amount",read_only= True)
    received_amount = serializers.DecimalField(max_digits=15, decimal_places=2, source="invoice.agreement_id.paid_amount",read_only= True)
    invoice_no = serializers.CharField(source="invoice.invoice_id",read_only= True)
    invoice_amount = serializers.DecimalField(max_digits=15, decimal_places=2, source="invoice.invoice_amount",read_only= True)

    class Meta:
        fields = '__all__'
        model = SalesGstEntry


class SalesGstReportSerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    project_name = serializers.CharField(source="project.name",read_only= True)
    unit_name = serializers.CharField(source="unit.descr",read_only= True)
    customer_name = serializers.CharField(source="customer.name",read_only= True)
    agreement_amount = serializers.DecimalField(max_digits=15, decimal_places=2, source="agreement.sale_amount",read_only= True)
    received_amount = serializers.DecimalField(max_digits=15, decimal_places=2, source="agreement.paid_amount",read_only= True)
    gst_number = serializers.CharField(source="customer.gstnumber",read_only= True)

    class Meta:
        fields = '__all__'
        model = SalesGstReport

