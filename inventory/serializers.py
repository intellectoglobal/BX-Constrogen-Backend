from rest_framework import serializers
from .models import (Purpose, Warehouse, Itemtype,
                     Itemuom, Item, ItemSpecification, ItemItemUOM, Uomtype, Itemgroup,
                     Itemgroupdetail, Itemsubtype, ItemSubtypeSpecification, ItemSubtypeItemUOM, ItemPurpose, Brand)
from pricing.models import PurchaseorderItems
from datetime import datetime
# from users.models import AppUser
# from geolocation.serializers import StateSerializer, CitySerializer
# from geolocation.models import State, City
from buildiq.super_serializer import DynamicFieldsModelSerializer


class WarehouseSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Warehouse
        fields = '__all__'


class ItemtypeSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Itemtype
        fields = '__all__'


class PurposeSerializer(serializers.ModelSerializer):

    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    itemtyp = ItemtypeSerializer(
        source='itemtyp_key', read_only=True, fields=('key', 'descr',))

    class Meta:
        model = Purpose
        fields = '__all__'


class ItemSubtypeSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    itemtyp = ItemtypeSerializer(
        source='itemtyp_key', read_only=True, fields=('key', 'descr',))

    specifications = serializers.SerializerMethodField(read_only=True)
    uoms = serializers.SerializerMethodField(read_only=True)

    def get_specifications(self, itemsubtype):
        try:
            if ItemSubtypeSpecification.objects.filter(item_subtype_key=itemsubtype.key).exists():
                spec_instances = ItemSubtypeSpecification.objects.filter(
                    item_subtype_key=itemsubtype.key)
                spec_data = ItemSubtypeSpecificationSerializer(
                    spec_instances, read_only=True, many=True).data
                return spec_data
            return []
        except:
            return []

    def get_uoms(self, itemsubtype):
        try:
            if ItemSubtypeItemUOM.objects.filter(item_subtype_key=itemsubtype.key).exists():
                uom_instances = ItemSubtypeItemUOM.objects.filter(
                    item_subtype_key=itemsubtype.key)
                uom_data = ItemSubtypeItemUOMSerializer(
                    uom_instances, read_only=True, many=True).data
                return uom_data
            return []
        except Exception as e:
            print(e)
            return []

    class Meta:
        model = Itemsubtype
        fields = '__all__'


class ItemSubtypeSpecificationSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = ItemSubtypeSpecification
        fields = '__all__'


class ItemSubtypeItemUOMSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = ItemSubtypeItemUOM
        fields = '__all__'


class ItemSpecificationSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = ItemSpecification
        fields = '__all__'


class ItemItemUOMSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = ItemItemUOM
        fields = '__all__'

class ItemPurposeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPurpose
        fields = '__all__'

class ItemSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    itemtyp = ItemtypeSerializer(
        source='itemtyp_key', read_only=True, fields=('key', 'descr',))
    item_subtype = ItemSubtypeSerializer(
        source='subtype', read_only=True, fields=('key', 'descr',))
    specifications = serializers.SerializerMethodField(read_only=True)
    uoms = serializers.SerializerMethodField(read_only=True)
    uoms_desc = serializers.SerializerMethodField(read_only=True)
    purpose = serializers.SerializerMethodField(read_only=True)

    def get_specifications(self, item):
        try:
            if ItemSpecification.objects.filter(item_key=item.key).exists():
                specIns = ItemSpecification.objects.filter(
                    item_key=item.key).select_related('item_subtype_spec_key')
                specInsRows = []
                for spec in specIns:
                    spec_data = ItemSpecificationSerializer(spec).data
                    spec_data['subtype_spec_descr'] = spec.item_subtype_spec_key.descr
                    specInsRows.append(spec_data)
                return specInsRows
            return []
        except:
            return []

    def get_uoms(self, item):
        try:
            if ItemItemUOM.objects.filter(item_key=item.key).exists():
                item_uoms = ItemItemUOM.objects.filter(item_key=item.key)
                item_uomsRows = ItemItemUOMSerializer(
                    item_uoms, read_only=True, many=True).data
                return item_uomsRows
            return []
        except:
            return []
        
    def get_uoms_desc(self, item):
        try:
            if ItemItemUOM.objects.filter(item_key=item.key).exists():
                item_uoms = ItemItemUOM.objects.filter(item_key=item.key)
                item_uoms_desc = []
                for uom in item_uoms:
                    item_uoms_desc.append(uom.item_uom_key.descr)
                # item_uomsRows = ItemItemUOMSerializer(
                #     item_uoms, read_only=True, many=True).data
                return item_uoms_desc
            return []
        except:
            return []
    
    def get_purpose(self, item):
        try:
            if ItemPurpose.objects.filter(item_key=item.key).exists():
                item_purpose = ItemPurpose.objects.filter(item_key=item.key)
                item_purpose = ItemPurposeSerializer(
                    item_purpose, read_only=True, many=True).data
                return item_purpose
            return []
        except:
            return []

    class Meta:
        model = Item
        fields = '__all__'


class ItemRateSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    vendor = serializers.CharField(source='po_key.vend_key.name')
    project = serializers.CharField(source='po_key.proj_key.name')
    brand = serializers.CharField(source='brand.name',allow_null=True,required=False)
    uom = serializers.CharField(source='item_uom_key.descr')

    without_gst = serializers.DecimalField(
        source='rate_without_gst',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    with_gst = serializers.DecimalField(
        source='rate_with_gst',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    def get_date(self, obj):
        invoice = obj.po_key.vendorinvoice_set.order_by("-invoicedate").first()
        return invoice.invoicedate.strftime("%d-%m-%Y") if invoice and invoice.invoicedate else None

    class Meta:
        model = PurchaseorderItems
        fields = [
            'date',
            'vendor',
            'project',
            'qty',
            'brand',
            'uom',
            'without_gst',
            'gst',
            'with_gst',
        ]



class UOMTypeSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Uomtype
        fields = '__all__'


class ItemuomSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    uom_type = UOMTypeSerializer(
        source='uomtyp_key', read_only=True, fields=('key', 'id', 'descr',))
    item_type = ItemtypeSerializer(
        source='itemtyp_key', read_only=True, fields=('key', 'id', 'descr',))

    class Meta:
        model = Itemuom
        fields = '__all__'


class ItemGroupSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    item_uoms = ItemuomSerializer(source='itemuom_key',
                                  read_only=True, fields=('key', 'id', 'descr',))
    item_group_details = serializers.SerializerMethodField(read_only=True)

    def get_item_group_details(self, itmGrp):
        if Itemgroupdetail.objects.filter(itemgrp_key=itmGrp).exists():
            itemGrpDetailIns = Itemgroupdetail.objects.filter(
                itemgrp_key=itmGrp)
            detailsRows = ItemGroupDetailSerializer(
                itemGrpDetailIns, read_only=True, many=True, fields=('key', 'item', 'mixratioval',)).data
            detailsRowsOutput = []
            for row in detailsRows:
                row['item_key'] = row['item']['key']
                row['item_id'] = row['item']['id']
                row['item_descr'] = row['item']['descr']
                row.pop('item')
                detailsRowsOutput.append(row)
            return detailsRowsOutput
        return []

    class Meta:
        model = Itemgroup
        fields = '__all__'


class ItemGroupDetailSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    item = ItemSerializer(source='item_key',
                          read_only=True, fields=('key', 'id', 'descr',))
    # itemgroup = ItemGroupSerializer(source='itemgrp_key',
    #                                 read_only=True, fields=('key', 'id', 'descr',))

    class Meta:
        model = Itemgroupdetail
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):

    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    itemtyp = ItemtypeSerializer(
        source='itemtyp_key', read_only=True, fields=('key', 'descr',))

    class Meta:
        model = Brand
        fields = '__all__'