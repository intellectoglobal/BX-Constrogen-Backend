from django.db import models
from inventory.models import Itemuom, Item, Itemtype, Purpose

class ContractServiceTemplateHdr(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='ContractServiceTemplateHdr_Key')
    template_name = models.CharField(
        max_length=255, db_column='ContractServiceTemplateHdr_TemplateName')
    description = models.TextField(
        db_column='ContractServiceTemplateHdr_Description')
    contract_type_key = models.CharField(
        max_length=255, db_column='ContractServiceTemplateHdr_ContractTypeKey')
    client_id = models.IntegerField(
        db_column='ContractServiceTemplateHdr_ClientID')

    class Meta:
        db_table = 'ContractServiceTemplateHdr'


class ContractServiceTemplateDtl(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='ContractServiceTemplateDtl_Key')
    contractservice_template_hdr_key = models.ForeignKey(
        'ContractServiceTemplateHdr',
        on_delete=models.CASCADE,
        db_column='ContractServiceTemplateDtl_ContractServiceTemplateHdrKey',
        related_name='details'
    )
    service_desc = models.TextField(
        db_column='ContractServiceTemplateDtl_ServiceDesc')
    uom = models.ForeignKey(Itemuom, on_delete=models.CASCADE,
                            db_column='ContractServiceTemplateDtl_UOM')
    client_id = models.IntegerField(
        db_column='ContractServiceTemplateDtl_ClientID')

    class Meta:
        db_table = 'ContractServiceTemplateDtl'


class PaymentScheduleTemplateHdr(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='PaymentScheduleTemplateHdr_Key')
    template_name = models.CharField(
        max_length=255, db_column='PaymentScheduleTemplateHdr_TemplateName')
    description = models.TextField(
        db_column='PaymentScheduleTemplateHdr_Description')
    contract_type_key = models.CharField(
        max_length=255, db_column='PaymentScheduleTemplateHdr_ContractTypeKey')
    clientid = models.IntegerField(
        db_column='PaymentScheduleTemplateHdr_ClientID')

    class Meta:
        db_table = 'PaymentScheduleTemplateHdr'


class PaymentScheduleTemplateDtl(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='PaymentScheduleTemplateDtl_Key')
    payment_schedule_template_hdr_key = models.ForeignKey(
        'PaymentScheduleTemplateHdr',
        on_delete=models.CASCADE,
        db_column='PaymentScheduleTemplateDtl_PaymentScheduleTemplateHdrKey',
        related_name='details'
    )
    payment_stage_desc = models.TextField(
        db_column='PaymentScheduleTemplateDtl_ScheduleDesc')
    clientid = models.IntegerField(
        db_column='PaymentScheduleTemplateDtl_ClientID')

    class Meta:
        db_table = 'PaymentScheduleTemplateDtl'



class ItemKitTemplateHdr(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='ItemKitTemplateHdr_Key')
    kit_name = models.CharField(
        max_length=255, db_column='ItemKitTemplateHdr_Name')
    description = models.TextField(
        db_column='ItemKitTemplateHdr_Descr', blank=True, null=True)
    item_type_key = models.ForeignKey(Itemtype,
        on_delete=models.CASCADE, db_column='ItemKitTemplateHdr_ItemTypeKey')
    purpose_key = models.ForeignKey(Purpose, on_delete = models.CASCADE, db_column='ItemKitTemplateHdr_PurposeKey')
    client_id = models.IntegerField(
        db_column='ItemKitTemplateHdr_ClientID')

    class Meta:
        db_table = 'ItemKitTemplateHdr'


class ItemKitTemplateDtl(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='ItemKitTemplateDtl_Key')
    item_kit_template_hdr_key = models.ForeignKey(
        'ItemKitTemplateHdr',
        on_delete=models.CASCADE,
        db_column='ItemKitTemplateDtl_ItemKitTemplateHdrKey',
        related_name='item_kit_hdr'
    )
    item_key = models.ForeignKey(Item,on_delete = models.CASCADE,
        db_column='ItemKitTemplateDtl_ItemKey')
    brand = models.CharField(max_length=255, db_column='ItemKitTemplateDtl_Brand', null=True, blank= True)
    model_number = models.CharField(max_length=255, db_column='ItemKitTemplateDtl_Model', null=True, blank= True)
    qty = models.DecimalField(max_digits=15, decimal_places=2, db_column='ItemKitTemplateDtl_Quantity', null=True, blank= True)
    item_uom_key = models.ForeignKey(Itemuom, on_delete=models.CASCADE,
                            db_column='ItemKitTemplateDtl_UOM')
    client_id = models.IntegerField(
        db_column='ItemKitTemplateDtl_ClientID')

    class Meta:
        db_table = 'ItemKitTemplateDtl'



class CustomerPaymentScheduleTemplateHdr(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='Customer_PymntSchdleTemplateHdr_Key')
    template_name = models.CharField(
        max_length=255, db_column='Customer_PymntSchdleTemplateHdr_TemplateName')
    description = models.TextField(
        db_column='Customer_PymntSchdleTemplateHdr_Descr', null=True, blank=True)
    clientid = models.IntegerField(
        db_column='Customer_PymntSchdleTemplateHdr_ClientID')

    class Meta:
        db_table = 'Customer_PymntSchdleTemplateHdr'


class CustomerPaymentScheduleTemplateDtl(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='Customer_PymntSchdleTemplateDtl_Key')
    payment_schedule_template_hdr_key = models.ForeignKey(
        'CustomerPaymentScheduleTemplateHdr',
        on_delete=models.CASCADE,
        db_column='Customer_PymntSchdleTemplateDtl_TmplteHdrKey',
        related_name='details'
    )
    payment_stage_desc = models.TextField(
        db_column='Customer_PymntSchdleTemplateDtl_ScheduleDesc')
    clientid = models.IntegerField(
        db_column='Customer_PymntSchdleTemplateDtl_ClientID')

    class Meta:
        db_table = 'Customer_PymntSchdleTemplateDtl'

