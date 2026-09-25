from rest_framework import serializers


class MaterialExpenseSerializer(serializers.Serializer):
    item_type = serializers.CharField()
    netamt = serializers.FloatField()
    paid_amount = serializers.FloatField()
    discount_amount = serializers.FloatField()

class ContractExpenseSerializer(serializers.Serializer):
    contractor_type = serializers.CharField()
    invoice_amount = serializers.FloatField()
    paid_amount = serializers.FloatField()


class SalaryExpenseSerializer(serializers.Serializer):
    employee = serializers.CharField()
    salary = serializers.FloatField()
    allowance = serializers.FloatField()


class ExtraExpenseSerializer(serializers.Serializer):
    expense_type = serializers.CharField()
    paid_amount = serializers.FloatField()


class InvoiceDetailSerializer(serializers.Serializer):
    invoice_key = serializers.IntegerField()
    date = serializers.DateField()
    invoice_no = serializers.CharField()
    quantity = serializers.FloatField()
    uom = serializers.CharField(allow_null=True)

class StockItemSerializer(serializers.Serializer):
    item_key = serializers.IntegerField()
    item_name = serializers.CharField()
    item_type = serializers.CharField()
    quantity = serializers.FloatField()
    UOM = serializers.CharField(allow_null=True)
    model = serializers.CharField(allow_null=True)
    brand = serializers.CharField(allow_null=True)
    invoices = InvoiceDetailSerializer(many=True)