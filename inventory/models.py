from django.db import models
from client.models import Company, Clientbase
from geolocation.models import State, City
import re


class Warehouse(models.Model):
    key = models.AutoField(db_column='WH_Key', primary_key=True)
    id = models.CharField(db_column='WH_ID', max_length=30)
    name = models.CharField(db_column='WH_Name', max_length=100)
    addr1 = models.CharField(db_column='WH_Addr1',
                             max_length=100, blank=True, null=True)
    addr2 = models.CharField(db_column='WH_Addr2',
                             max_length=100, blank=True, null=True)
    state_key = models.ForeignKey(
        State, on_delete=models.CASCADE, db_column='WH_State_Key')
    city_key = models.ForeignKey(
        City, on_delete=models.CASCADE, db_column='WH_City_Key')
    briefdescr = models.CharField(
        db_column='WH_BriefDescr', max_length=255, blank=True, null=True)
    createdby = models.CharField(
        db_column='WH_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='WH_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='WH_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='WH_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='WH_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Warehouse
        tableName = currentModelObj._meta.db_table
        if currentModelObj.objects.filter(id__icontains=tableName+"_").count() > 0:
            lastRecordIDList = currentModelObj.objects.filter(
                id__icontains=tableName+"_").values_list('id', flat=True)
            lastRecordIDInt = max(
                [int(re.search(r'-?\d+\.?\d*', x).group()) for x in lastRecordIDList])
            return tableName+"_"+str(int(lastRecordIDInt)+1)
        else:
            return str(tableName)+"_1"

    class Meta:
        managed = True
        db_table = 'Warehouse'


class Itemtype(models.Model):
    key = models.AutoField(db_column='ItemTyp_Key', primary_key=True)
    descr = models.CharField(
        db_column='ItemTyp_Descr', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='ItemTyp_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItemTyp_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ItemTyp_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ItemTyp_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ItemTyp_Client_ID')

    class Meta:
        managed = True
        db_table = 'ItemType'


class Purpose(models.Model):
    key = models.AutoField(db_column='Purpose_Key', primary_key=True)
    name = models.CharField(
        db_column='Purpose_Name', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='Purpose_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Purpose_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='Purpose_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Purpose_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='Purpose_Client_ID')
    itemtyp_key = models.ForeignKey(
        Itemtype, on_delete=models.CASCADE, db_column='Purpose_ItemTyp_Key')

    class Meta:
        managed = True
        db_table = 'Purpose'


class Uomtype(models.Model):
    key = models.AutoField(db_column='UOMTyp_Key', primary_key=True)
    id = models.CharField(db_column='UOMTyp_ID', max_length=30)
    descr = models.CharField(db_column='UOMTyp_Descr',
                             max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='UOMTyp_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='UOMTyp_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='UOMTyp_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='UOMTyp_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='UOMTyp_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Uomtype
        tableName = currentModelObj._meta.db_table
        if currentModelObj.objects.filter(id__icontains=tableName+"_").count() > 0:
            lastRecordIDList = currentModelObj.objects.filter(
                id__icontains=tableName+"_").values_list('id', flat=True)
            lastRecordIDInt = max(
                [int(re.search(r'-?\d+\.?\d*', x).group()) for x in lastRecordIDList])
            return tableName+"_"+str(int(lastRecordIDInt)+1)
        else:
            return str(tableName)+"_1"

    class Meta:
        managed = True
        db_table = 'UOMType'


class Itemuom(models.Model):
    key = models.AutoField(db_column='ItemUOM_Key', primary_key=True)
    descr = models.CharField(
        db_column='ItemUOM_Descr', max_length=100, blank=True, null=True)
    stockuom_key = models.IntegerField(
        db_column='itemUOM_StockUOM_Key', blank=True, null=True)
    convunits = models.DecimalField(
        db_column='ItemUOK_ConvUnits', max_digits=15, decimal_places=5, blank=True, null=True)
    createdby = models.CharField(
        db_column='ItemUOM_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItemUOM_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ItemUOM_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ItemUOM_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(Clientbase, models.CASCADE,
                                  db_column='ItemUOM_Client_ID')
    uomtyp_key = models.ForeignKey(
        Uomtype, on_delete=models.CASCADE, db_column='ItemUOM_UOMTyp_Key', blank=True, null=True)
    itemtyp_key = models.ForeignKey(
        Itemtype, on_delete=models.CASCADE, db_column='ItemUOM_ItemTyp_Key')

    class Meta:
        managed = True
        db_table = 'ItemUOM'


class Itemgroup(models.Model):
    key = models.AutoField(db_column='ItemGrp_Key', primary_key=True)
    id = models.CharField(db_column='ItemGrp_ID', max_length=30)
    descr = models.CharField(db_column='ItemGrp_Descr',
                             max_length=100, blank=True, null=True)
    itemuom_key = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column='ItemGrp_ItemUOM_Key')
    grouptype = models.CharField(db_column='ItemGrp_GroupType', max_length=1)
    mixtype = models.CharField(db_column='ItemGrp_MixType', max_length=1)
    scope = models.CharField(db_column='ItemGrp_Scope', max_length=1)
    createdby = models.CharField(
        db_column='ItemGrp_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItemGrp_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ItemGrp_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ItemGrp_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, models.CASCADE, db_column='ItemGrp_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Itemgroup
        tableName = currentModelObj._meta.db_table
        if currentModelObj.objects.filter(id__icontains=tableName+"_").count() > 0:
            lastRecordIDList = currentModelObj.objects.filter(
                id__icontains=tableName+"_").values_list('id', flat=True)
            lastRecordIDInt = max(
                [int(re.search(r'-?\d+\.?\d*', x).group()) for x in lastRecordIDList])
            return tableName+"_"+str(int(lastRecordIDInt)+1)
        else:
            return str(tableName)+"_1"

    class Meta:
        managed = True
        db_table = 'ItemGroup'


class Itemsubtype(models.Model):
    key = models.AutoField(db_column='ItemSubTyp_Key', primary_key=True)
    descr = models.CharField(db_column='ItemSubTyp_Descr',
                             max_length=100, blank=True, null=True)

    itemtyp_key = models.ForeignKey(
        Itemtype, on_delete=models.CASCADE, db_column='ItemSubTyp_ItemTyp_Key')
    gst = models.IntegerField(
        db_column='ItemSubTyp_Gst')
    createdby = models.CharField(
        db_column='ItemSubTyp_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItemSubTyp_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ItemSubTyp_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ItemSubTyp_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ItemSubTyp_Client_ID', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ItemSubType'


class ItemSubtypeSpecification(models.Model):
    key = models.AutoField(
        db_column='ItemSubtypeSpec_Key', primary_key=True)
    descr = models.CharField(
        db_column='ItemSubtypeSpec_Descr', max_length=255, blank=True, null=True)
    item_subtype_key = models.ForeignKey(
        Itemsubtype, on_delete=models.CASCADE, db_column='ItemSubtypeSpec_ItemSubtype_Key'
    )
    createdby = models.CharField(
        db_column='ItemSubtypeSpec_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItemSubtypeSpec_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ItemSubtypeSpec_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ItemSubtypeSpec_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ItemSubtypeSpec_Client_ID'
    )

    class Meta:
        managed = True
        db_table = 'ItemSubtypeSpecification'


class ItemSubtypeItemUOM(models.Model):
    key = models.AutoField(
        db_column='ItemSubtypeUOM_Key', primary_key=True)
    item_subtype_key = models.ForeignKey(
        Itemsubtype, on_delete=models.CASCADE, db_column='ItemSubtypeUOM_ItemSubtype_Key'
    )
    item_uom_key = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column='ItemSubtypeUOM_ItemUOM_Key'
    )
    createdby = models.CharField(
        db_column='ItemSubtypeUOM_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItemSubtypeUOM_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ItemSubtypeUOM_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ItemSubtypeUOM_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ItemSubtypeUOM_Client_ID'
    )

    class Meta:
        managed = True
        db_table = 'ItemSubtype_ItemUOM'


class Item(models.Model):
    key = models.AutoField(db_column='Item_Key', primary_key=True)
    descr = models.CharField(
        db_column='Item_Descr', max_length=100, blank=True, null=True)
    model_number = models.CharField(
        db_column='Item_Model_Number', max_length=30, blank=True, null=True)
    itemtyp_key = models.ForeignKey(
        Itemtype, on_delete=models.CASCADE, db_column='Item_ItemTyp_Key')
    stocktype = models.CharField(db_column='Item_StockType', max_length=1)
    gst = models.IntegerField(
        db_column='Item_Gst')
    amount = models.DecimalField(
        db_column='Item_Amount', max_digits=15, decimal_places=2, blank=True, null=True)
    createdby = models.CharField(
        db_column='Item_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Item_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='Item_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Item_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='Item_Client_ID')
    subtype = models.ForeignKey(
        Itemsubtype, models.CASCADE, db_column='Item_SubType_Key', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Item'


class ItemPurpose(models.Model):

    key = models.AutoField(db_column="ItemPurpose_Key", primary_key=True)
    item_key = models.ForeignKey(
        Item, db_column="ItemPurpose_ItemKey", on_delete=models.CASCADE)
    purpose_key = models.ForeignKey(
        Purpose, db_column="ItemPurpose_PurposeKey", on_delete=models.CASCADE)
    client_id = models.ForeignKey(
        Clientbase, db_column="ItemPurpose_ClientID", on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = "ItemPurpose"


class ItemSpecification (models.Model):
    key = models.AutoField(db_column='ItemSpec_Key', primary_key=True)
    value = models.CharField(db_column='ItemSpec_Value',
                             max_length=100, blank=True, null=True)
    item_key = models.ForeignKey(
        Item, on_delete=models.CASCADE, db_column='ItemSpec_Item_key')
    item_subtype_spec_key = models.ForeignKey(
        ItemSubtypeSpecification, on_delete=models.CASCADE, db_column='ItemSpec_ItemSubtypeSpec_ID', blank=True, null=True
    )
    createdby = models.CharField(
        db_column='ItemSpec_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItemSpec_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ItemSpec_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ItemSpec_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ItemSpec_Client_ID')

    class Meta:
        managed = True
        db_table = 'ItemSpecification'


class ItemItemUOM(models.Model):
    key = models.AutoField(
        db_column='ItemItemUOM_Key', primary_key=True)
    item_key = models.ForeignKey(
        Item, on_delete=models.CASCADE, db_column='ItemItemUOM_Item_Key'
    )
    item_uom_key = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column='ItemItemUOM_ItemUOM_Key'
    )
    createdby = models.CharField(
        db_column='ItemItemUOM_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItemItemUOM_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ItemItemUOM_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ItemItemUOM_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ItemItemUOM_Client_ID'
    )

    class Meta:
        managed = True
        db_table = 'Item_ItemUOM'


class Itemgroupdetail(models.Model):
    key = models.AutoField(db_column='ItemGrpDet_Key', primary_key=True)
    itemgrp_key = models.ForeignKey(
        Itemgroup, models.CASCADE, db_column='ItemGrpDet_ItemGrp_Key')
    item_key = models.ForeignKey(
        Item, on_delete=models.CASCADE, db_column='ItemGrpDet_Item_Key')
    mixratioval = models.DecimalField(
        db_column='ItemGrpDet_MixRatioVal', max_digits=10, decimal_places=3, blank=True, null=True)
    createdby = models.CharField(
        db_column='ItemGrpDet_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItemGrpDet_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ItemGrpDet_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ItemGrpDet_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ItemGrpDet_Client_ID')

    class Meta:
        managed = True
        db_table = 'ItemGroupDetail'

class Brand(models.Model):
    key = models.AutoField(db_column='Brand_Key', primary_key=True)
    name = models.CharField(
        db_column='Brand_Name', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='Brand_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Brand_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='Brand_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Brand_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='Brand_Client_ID')
    itemtyp_key = models.ForeignKey(
        Itemtype, on_delete=models.CASCADE, db_column='Brand_ItemTyp_Key')

    class Meta:
        managed = True
        db_table = 'Brand'