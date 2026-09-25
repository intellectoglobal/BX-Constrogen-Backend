from django.db import models
import re


class Clientbase(models.Model):
    id = models.AutoField(
        db_column='Client_ID', primary_key=True)
    name = models.CharField(db_column='Client_Name', max_length=100)

    class Meta:
        managed = True
        db_table = 'ClientBase'


class Company(models.Model):
    id = models.AutoField(
        db_column='Company_ID', primary_key=True)
    name = models.CharField(db_column='Company_Name', max_length=255)
    client = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='Company_Client_ID')

    class Meta:
        managed = True
        db_table = 'Company'


class Costcategory(models.Model):
    key = models.AutoField(db_column='CostCtg_Key', primary_key=True)
    id = models.CharField(db_column='CostCtg_ID', max_length=30)
    descr = models.CharField(
        db_column='CostCtg_Descr', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='CostCtg_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='CostCtg_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='CostCtg_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='CostCtg_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='CostCtg_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='CostCtg_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Costcategory
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
        db_table = 'CostCategory'
        unique_together = (('company', 'id'),)


class Costcode(models.Model):
    key = models.AutoField(db_column='CostCd_Key', primary_key=True)
    id = models.CharField(db_column='CostCd_ID', max_length=30)
    descr = models.CharField(
        db_column='CostCd_Descr', max_length=100, blank=True, null=True)
    costctg_key = models.ForeignKey(
        Costcategory, on_delete=models.CASCADE, db_column='CostCd_CostCtg_Key')
    createdby = models.CharField(
        db_column='CostCd_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='CostCd_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='CostCd_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='CostCd_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='CostCd_Company_ID')
    client_id = models.ForeignKey(Clientbase, models.CASCADE,
                                  db_column='CostCd_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Costcode
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
        db_table = 'CostCode'
        unique_together = (('company', 'id'),)


class BankAccount(models.Model):
    key = models.AutoField(primary_key=True,db_column="BankAccount_Key")
    acc_no = models.CharField(max_length=50,db_column="BankAccount_AccNo")
    acc_name = models.CharField(max_length=255,db_column="BankAccount_AccName")
    bank_name = models.CharField(max_length=255,db_column="BankAccount_BankName")
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='BankAccount_CompanyID')  
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE, db_column='BankAccount_ClientID')

    
    class Meta:
        managed = True
        db_table = 'BankAccount'
