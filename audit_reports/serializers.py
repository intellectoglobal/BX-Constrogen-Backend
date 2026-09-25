from rest_framework import serializers
from sale.models import SaleReceipt
from salary_and_allowance.models import SalaryAndAllowance 
from pricing.models import Vendorinvoice, PurchaseorderItems
from contractor.models import ContractVoucherDtl
from vendor.models import VendorItemType, VendorPaymentVoucherDtl, VendorPaymentVoucherHdr
from buildiq.super_serializer import DynamicFieldsModelSerializer
from project.models import PaidExpenses

class VendorInvoiceReportSerializer(DynamicFieldsModelSerializer):
    invoice_date = serializers.DateField(source='invoicedate', read_only=True, format="%d-%m-%Y")
    vendor_name = serializers.CharField(source="vend_key.name", read_only=True)
    vendor_gst = serializers.CharField(
        source="vend_key.gstnumber", read_only=True)
    material_type = serializers.CharField(source='po_key.item_type_key.descr', read_only=True)
    taxable_invoice_amount = serializers.DecimalField(
        source="invamt", max_digits=12, decimal_places=2, read_only=True)
    gst_rate = serializers.SerializerMethodField()
    gst_amount = serializers.DecimalField(
        source="gstamt", max_digits=12, decimal_places=2, read_only=True)
    rounded_off_direction = serializers.SerializerMethodField()
    rounded_off_value = serializers.DecimalField(
        source="roundedamt", max_digits=12, decimal_places=2, read_only=True)
    total_bill_amount = serializers.DecimalField(
        source="netamt", max_digits=12, decimal_places=2, read_only=True)
    vendor_invoice_no = serializers.CharField(read_only=True)
    project_name = serializers.CharField(
        source="proj_key.name", read_only=True)

    def get_gst_rate(self, obj):
        try:
            taxable_invoice_amount = obj.invamt - \
                obj.gstamt if obj.invamt and obj.gstamt else 0
            if taxable_invoice_amount != 0:
                return round((obj.gstamt / taxable_invoice_amount) * 100, 2)
        except (TypeError, ZeroDivisionError):
            return None
        return None

    def get_rounded_off_direction(self, obj):
        return {
            'A': 'Increment',
            'S': 'Decrement'
        }.get(obj.rounded_action, obj.rounded_action)

    class Meta:
        model = Vendorinvoice
        fields = '__all__'

class PaidExpenseReportSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(source='date', format='%d-%m-%Y', read_only=True)
    vendor_name = serializers.CharField(source='exp_vendor_id.name', read_only=True)
    material_type = serializers.SerializerMethodField()
    total_bill_amount = serializers.DecimalField(source='amount', max_digits=12, decimal_places=2, read_only=True)
    project_name = serializers.CharField(source="project_key.name", read_only=True)

    def get_material_type(self, obj):
        return obj.expense_type.descr if obj.expense_type else "Miscellaneous"

    class Meta:
        model = PaidExpenses
        fields = ['invoice_date', 'vendor_name', 'material_type', 'total_bill_amount', 'project_name']


class CustomerPaymentReceiptSerializer(DynamicFieldsModelSerializer):
    date_of_receipt = serializers.DateField(
        source="date", read_only=True, format="%d-%m-%Y")
    customer_name = serializers.CharField(
        source="customer_id.name", read_only=True)
    receipt_amount = serializers.DecimalField(
        source="amount", max_digits=12, decimal_places=2, read_only=True)
    project_name = serializers.CharField(
        source="project_id.name", read_only=True)
    flat_name = serializers.CharField(
        source="unit_id.descr", read_only=True)
    sale_area = serializers.CharField(
        source="unit_id.saleablearea", read_only=True)
    carpet_area = serializers.CharField(
        source="unit_id.carpetarea", read_only=True)
    gross_value = serializers.CharField(
        source="invoice_id.agreement_id.sale_amount", read_only=True)
    mode_of_payment = serializers.CharField(
        source="payment_mode_id.descr", read_only=True)
    project_location = serializers.CharField(
        source="unit_id.proj_key.addr1", read_only=True)

    class Meta:
        model = SaleReceipt
        fields = '__all__'


class ContractorPaymentVoucherSerializer(DynamicFieldsModelSerializer):
    date_of_payment = serializers.DateField(
        source="contract_voucher_hdr.contract_voucher_dt", read_only=True, format="%d-%m-%Y")
    payee_name = serializers.CharField(
        source="contract_voucher_hdr.contractor_id.name", read_only=True)
    amount = serializers.IntegerField(
        source="paid_amount", read_only=True)
    mode_of_payment = serializers.CharField(
        source="contract_voucher_hdr.payment_mode_id.descr", read_only=True)
    bank_name = serializers.CharField(
        source="contract_voucher_hdr.account_id.bank_name", read_only=True)
    transaction_no = serializers.CharField(
        source="contract_voucher_hdr.transaction_detail", read_only=True)
    contractor_type = serializers.CharField(
        source="contract_voucher_hdr.contractor_id.contractortyp_key.descr", read_only=True)

    class Meta:
        model = ContractVoucherDtl
        fields = '__all__'


class SupplierPaymentVoucherSerializer(DynamicFieldsModelSerializer):
    date_of_payment = serializers.DateField(
        source="vendor_voucher_hdr.vendor_voucher_dt", read_only=True, format="%d-%m-%Y")
    payee_name = serializers.CharField(
        source="vendor_voucher_hdr.vendor_id.name", read_only=True)
    amount = serializers.IntegerField(
        source="paid_amount", read_only=True)
    mode_of_payment = serializers.CharField(
        source="vendor_voucher_hdr.payment_mode_id.descr", read_only=True)
    bank_name = serializers.CharField(
        source="vendor_voucher_hdr.account_id.bank_name", read_only=True)
    transaction_no = serializers.CharField(
        source="vendor_voucher_hdr.transaction_detail", read_only=True)
    vendor_type = serializers.SerializerMethodField()

    def get_vendor_type(self, obj):
        invoice_key = obj.invoice_id
        po_key = invoice_key.po_key
        item = PurchaseorderItems.objects.filter(
            po_key=po_key).first()
        if item:
            item_type = item.item_key.itemtyp_key.descr
            return item_type
        return None

    class Meta:
        model = VendorPaymentVoucherDtl
        fields = '__all__'

class SupplierPaymentVoucherHdrSerializer(DynamicFieldsModelSerializer):
    date_of_payment = serializers.DateField(
        source="vendor_voucher_dt", read_only=True, format="%d-%m-%Y")
    payee_name = serializers.CharField(
        source="vendor_id.name", read_only=True)
    amount = serializers.IntegerField(
        source="total_amount", read_only=True)
    mode_of_payment = serializers.CharField(
        source="payment_mode_id.descr", read_only=True)
    bank_name = serializers.CharField(
        source="account_id.bank_name", read_only=True)
    transaction_no = serializers.CharField(
        source="transaction_detail", read_only=True)
    vendor_type = serializers.SerializerMethodField()

    def get_vendor_type(self, obj):
        vendor_key = obj.vendor_id
        item_type = VendorItemType.objects.filter(
            vend_key=vendor_key).first()
        if item_type:
            item_type = item_type.item_type_key.descr
            return item_type
        return None

    class Meta:
        model = VendorPaymentVoucherHdr
        fields = '__all__'


class ContractorTDSReportSerializer(serializers.Serializer):
    contractor_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    pan_no = serializers.CharField()


class PayrollReportSerializer(DynamicFieldsModelSerializer):
    date_of_payment = serializers.DateField(
        source="date", read_only=True, format="%d-%m-%Y")
    project = serializers.CharField(
        source="project_key.name", read_only=True)
    payee_name = serializers.CharField(
        source="employee.first_name", read_only=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    mode_of_payment = serializers.CharField(
        source="payment_mode_key.descr", read_only=True)
    bank_name = serializers.CharField(
        source="account_key.bank_name", read_only=True)
    transaction_no = serializers.CharField(
        source="transaction_detail", read_only=True)
    type = serializers.SerializerMethodField()
    
    def get_type(self, obj):
        return {
            'A': 'Allowance',
            'S': 'Salary'
        }.get(obj.type, obj.type)


    class Meta:
        model = SalaryAndAllowance
        fields = '__all__'
