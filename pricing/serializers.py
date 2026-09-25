from rest_framework import serializers
from .models import (Docid, Docstatus, Goodsreceiptnote, GoodsreceiptnoteItems,
                     StockLedger, StockQoh, StockSummary, Itembatch, ItembatchLedger,
                     Purchasetemplate, PurchasetemplateItems, Purchaseorder, PurchaseorderItems,
                     Vendorinvoice, VendorInvoiceImage, VendorinvoiceItems, VendorLedger, Payment, Paymentalloc, Modeofpay)
from datetime import datetime
from geolocation.serializers import StateSerializer, CitySerializer
from project.serializers import ProjectSerializer
from vendor.serializers import VendorSerializer
from inventory.serializers import ItemSerializer, ItemuomSerializer, ItemtypeSerializer
from geolocation.models import State, City
from buildiq.super_serializer import DynamicFieldsModelSerializer


class DocIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docid
        fields = '__all__'


class DocStatusSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Docstatus
        fields = '__all__'


class GoodsReceiptNoteSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    vendor = VendorSerializer(source='vend_key',
                                     read_only=True, fields=('key', 'name'))

    project = ProjectSerializer(
        source='proj_key', read_only=True, fields=('key', 'id', 'name',))

    status = serializers.SerializerMethodField(read_only=True)
    grn_items = serializers.SerializerMethodField(read_only=True)

    def get_status(self, grn):
        if Docstatus.objects.filter(docstatus=grn.docstatus).exists():
            return DocStatusSerializer(Docstatus.objects.get(docstatus=grn.docstatus)).data
        return {}

    def get_grn_items(self, grn):
        if GoodsreceiptnoteItems.objects.filter(grn_key=grn.key).exists():
            return GoodsReceiptNoteItemsSerializer(GoodsreceiptnoteItems.objects.filter(grn_key=grn.key), many=True).data
        return []

    class Meta:
        model = Goodsreceiptnote
        fields = '__all__'


class GoodsReceiptNoteItemsSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    items = ItemSerializer(source='item_key',
                           read_only=True, fields=('key', 'id', 'descr',))
    items_uoms = ItemuomSerializer(source='itemuom_key',
                                   read_only=True, fields=('key', 'id', 'descr',))

    class Meta:
        model = GoodsreceiptnoteItems
        fields = '__all__'


class StockLedgerSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = StockLedger
        fields = '__all__'


class StockQohSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockQoh
        fields = '__all__'


class StockSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StockSummary
        fields = '__all__'


class ItemBatchSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Itembatch
        fields = '__all__'


class ItemBatchLedgerSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = ItembatchLedger
        fields = '__all__'


class PurchaseTemplateSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    purchs_template_items = serializers.SerializerMethodField(read_only=True)

    def get_purchs_template_items(self, purTmp):
        if PurchasetemplateItems.objects.filter(purtmpl_key=purTmp.key).exists():
            return PurchaseTemplateItemsSerializer(PurchasetemplateItems.objects.filter(purtmpl_key=purTmp.key), many=True).data
        return []

    class Meta:
        model = Purchasetemplate
        fields = '__all__'


class PurchaseTemplateItemsSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    itemtype = ItemtypeSerializer(source='itemtyp_key',
                                  read_only=True, fields=('key', 'id', 'descr'))
    class Meta:
        model = PurchasetemplateItems
        fields = '__all__'


class PurchaseOrderSerializer(DynamicFieldsModelSerializer):
    # date = serializers.DateField(
    #     format='%d-%m-%Y',
    #     input_formats=['%Y-%m-%d'],
    # )
    createddttm = serializers.DateTimeField( 
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    vendor = VendorSerializer(
        source='vend_key', read_only=True, fields=('key', 'id', 'name', 'type','apterm_key'))
    project = ProjectSerializer(
        source='proj_key', read_only=True, fields=('key', 'id', 'name','addr1'))
    purchs_odr_items = serializers.SerializerMethodField(read_only=True)
    item_type = serializers.CharField(source='item_type_key.descr', read_only=True)
    
    def get_purchs_odr_items(self, purchaseOrder):
        if PurchaseorderItems.objects.filter(po_key=purchaseOrder.key).exists():
            return PurchaseOrderItemsSerializer(PurchaseorderItems.objects.filter(po_key=purchaseOrder.key).order_by('key'), many=True).data
        return []

    class Meta:
        model = Purchaseorder
        fields = '__all__'


class PurchaseOrderItemsSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    items = ItemSerializer(source='item_key',
                           read_only=True, fields=('key', 'id', 'descr',))
    uom = serializers.CharField(source='item_uom_key.descr',read_only =True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = PurchaseorderItems
        fields = '__all__'


class VendorInvoiceSerializer(serializers.ModelSerializer):
    invoicedate = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    vendor = VendorSerializer(
        source='vend_key', read_only=True, fields=('key', 'name',))
    project = ProjectSerializer(
        source='proj_key', read_only=True, fields=('key', 'name',))
    purchase_order = PurchaseOrderSerializer(
        source='po_key', read_only=True)
    item_type_key = serializers.IntegerField(source='po_key.item_type_key.key', read_only=True)
    images = serializers.SerializerMethodField(read_only=True)

    def get_images(self, invoice):
        if VendorInvoiceImage.objects.filter(vendor_invoice=invoice.key).exists():
            objs = VendorInvoiceImage.objects.filter(vendor_invoice=invoice.key)
            serializer = VendorInvoiceImageSerializer(objs, many=True, fields=('image_url',))
            return serializer.data
        return []

    # Uncomment and adjust the following methods if needed
    # status = serializers.SerializerMethodField(read_only=True)
    # invoice_items = serializers.SerializerMethodField(read_only=True)

    # def get_status(self, invoice):
    #     if Docstatus.objects.filter(docstatus=invoice.docstatus).exists():
    #         return DocStatusSerializer(Docstatus.objects.get(docstatus=invoice.docstatus)).data
    #     return {}

    # def get_invoice_items(self, invoice):
    #     if VendorinvoiceItems.objects.filter(vendinv_key=invoice.key).exists():
    #         return VendorInvoiceItemsSerializer(VendorinvoiceItems.objects.filter(vendinv_key=invoice.key), many=True).data
    #     return []

    class Meta:
        model = Vendorinvoice
        fields = '__all__'


class VendorInvoiceImageSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = VendorInvoiceImage
        fields = "__all__"


class VendorInvoiceItemsSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    items = ItemSerializer(source='item_key',
                           read_only=True, fields=('key', 'id', 'descr',))
    items_uoms = ItemuomSerializer(source='itemuom_key',
                                   read_only=True, fields=('key', 'id', 'descr',))

    class Meta:
        model = VendorinvoiceItems
        fields = '__all__'


class VendorLedgerSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = VendorLedger
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    vendor = VendorSerializer(source='vend_key',
                                     read_only=True, fields=('key', 'name',))
    status = serializers.SerializerMethodField(read_only=True)
    payment_allocations = serializers.SerializerMethodField(read_only=True)

    def get_status(self, pymt):
        if Docstatus.objects.filter(docstatus=pymt.docstatus).exists():
            return DocStatusSerializer(Docstatus.objects.get(docstatus=pymt.docstatus)).data
        return {}

    def get_payment_allocations(self, pymt):
        if Paymentalloc.objects.filter(pay_key=pymt.key).exists():
            return PaymentAllocSerializer(Paymentalloc.objects.filter(pay_key=pymt.key), many=True).data
        return []

    class Meta:
        model = Payment
        fields = '__all__'


class PaymentAllocSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Paymentalloc
        fields = '__all__'


class ModeofpaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Modeofpay
        fields = '__all__'
