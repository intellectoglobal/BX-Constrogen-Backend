import re
from django.db import models
from client.models import Company, Clientbase
from sale.models import Customer
from inventory.models import Itemuom

class ConstructionAgreement(models.Model):
    key = models.AutoField(db_column="ConstructionAgreementKey", primary_key=True)
    id = models.CharField(max_length=30, db_column="ConstructionAgreementID")
    agreement_no = models.CharField(
        max_length=100, unique=True, db_column="ConstructionAgreementNo")
    agreement_date = models.DateField(db_column="ConstructionAgreementDate")
    project_id = models.ForeignKey(
        'project.Project', on_delete=models.CASCADE, db_column="ConstructionAgreementProjectID")
    unit_id = models.ForeignKey(
        'project.Projectunit', on_delete=models.CASCADE, db_column="ConstructionAgreementUnitID")
    customer_id = models.ForeignKey(
        Customer,  on_delete=models.CASCADE, db_column="ConstructionAgreementCustomerID")
    contract_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="ConstructionAgreementContractAmount")
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="ConstructionAgreementPaidAmount")
    notes = models.TextField(blank=True, null=True,
                             db_column="ConstructionAgreementNotes")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ConstructionAgreementCompanyID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ConstructionAgreementClientID')

    @staticmethod
    def nextID():
        currentModelObj = ConstructionAgreement
        tableName = currentModelObj._meta.db_table
        if currentModelObj.objects.filter(id__icontains=tableName+"").count() > 0:
            lastRecordIDList = currentModelObj.objects.filter(
                id__icontains=tableName+"").values_list('id', flat=True)
            lastRecordIDInt = max(
                [int(re.search(r'-?\d+\.?\d*', x).group()) for x in lastRecordIDList])
            return tableName+"_"+str(int(lastRecordIDInt)+1)
        else:
            return str(tableName)+"_1"


    class Meta:
        managed = True
        db_table = 'ConstructionAgreement'


class ConstructionAgreementService(models.Model):
    key = models.AutoField(db_column="CAServiceKey", primary_key=True)
    id = models.CharField(max_length=30, db_column="CAServiceID")
    construction_agreement_id = models.ForeignKey(
        ConstructionAgreement, on_delete=models.CASCADE, db_column="CAServiceAgreementID")
    service_desc = models.CharField(max_length=500, db_column="CAServiceDesc")
    quantity = models.IntegerField(db_column="CAServiceQuantity")
    uom = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column="CAServiceUOMID")
    rate_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="CAServiceRatePerUnit")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="CAServiceAmount")

    @staticmethod
    def nextID():
        currentModelObj = ConstructionAgreementService
        tableName = currentModelObj._meta.db_table
        if currentModelObj.objects.filter(id__icontains=tableName+"").count() > 0:
            lastRecordIDList = currentModelObj.objects.filter(
                id__icontains=tableName+"").values_list('id', flat=True)
            lastRecordIDInt = max(
                [int(re.search(r'-?\d+\.?\d*', x).group()) for x in lastRecordIDList])
            return tableName+"_"+str(int(lastRecordIDInt)+1)
        else:
            return str(tableName)+"_1"

    class Meta:
        managed = True
        db_table = 'ConstructionAgreementService'


class ConstructionAgreementPaymentSchedule(models.Model):
    key = models.AutoField(db_column="CAPaymentScheduleKey", primary_key=True)
    id = models.CharField(max_length=255, db_column="CAPaymentScheduleID")
    construction_agreement_id = models.ForeignKey(
        ConstructionAgreement, on_delete=models.CASCADE, db_column="CAPaymentScheduleAgreementID")
    payment_stage_desc = models.CharField(
        max_length=500, db_column="CAPaymentScheduleDesc")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="CAPaymentScheduleAmount")

    @staticmethod
    def nextID():
        currentModelObj = ConstructionAgreementPaymentSchedule
        tableName = currentModelObj._meta.db_table
        if currentModelObj.objects.filter(id__icontains=tableName+"").count() > 0:
            lastRecordIDList = currentModelObj.objects.filter(
                id__icontains=tableName+"").values_list('id', flat=True)
            lastRecordIDInt = max(
                [int(re.search(r'-?\d+\.?\d*', x).group()) for x in lastRecordIDList])
            return tableName+"_"+str(int(lastRecordIDInt)+1)
        else:
            return str(tableName)+"_1"

    class Meta:
        managed = True
        db_table = 'ConstructionAgreementPaymentSchedule'
