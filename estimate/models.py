from django.db import models
from client.models import Clientbase, Company


class WorkCategory(models.Model):
    key = models.AutoField(primary_key=True, db_column='WrkCtgry_Key')
    descr = models.CharField(max_length=255, db_column='WrkCtgry_Descr')
    created_by = models.CharField(
        max_length=255, db_column='WrkCtgry_CreatedBy')
    createddttm = models.DateTimeField(
        auto_now_add=True, db_column='WrkCtgry_CreatedDtTm')
    lastmodified_by = models.CharField(
        max_length=255, db_column='WrkCtgry_LastModifiedBy', blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        auto_now=True, db_column='WrkCtgry_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='WrkCtgry_Client_ID')

    class Meta:
        db_table = 'WorkCategory'


class WorkType(models.Model):
    key = models.AutoField(primary_key=True, db_column='WrkType_Key')
    category_key = models.ForeignKey(
        WorkCategory, on_delete=models.CASCADE, db_column='WrkType_Ctgry_Key')
    descr = models.CharField(max_length=255, db_column='WrkType_Descr')
    is_repetitive = models.BooleanField(db_column='WrkType_IsRepetitive')
    created_by = models.CharField(
        max_length=255, db_column='WrkType_CreatedBy')
    createddttm = models.DateTimeField(
        auto_now_add=True, db_column='WrkType_CreatedDtTm')
    lastmodifiedby = models.CharField(
        max_length=255, db_column='WrkType_LastModifiedBy', blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        auto_now=True, db_column='WrkType_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='WrkType_Client_ID')

    class Meta:
        db_table = 'WorkType'


class WorkActivity(models.Model):
    key = models.AutoField(primary_key=True, db_column='WrkActivity_Key')
    category_key = models.ForeignKey(
        WorkCategory, on_delete=models.CASCADE, db_column='WrkActivity_Ctgry_Key')
    type_key = models.ForeignKey(
        WorkType, on_delete=models.CASCADE, db_column='WrkActivity_Type_Key')
    descr = models.CharField(max_length=255, db_column='WrkActivity_Descr')
    created_by = models.CharField(
        max_length=255, db_column='WrkActivity_CreatedBy')
    createddttm = models.DateTimeField(
        auto_now_add=True, db_column='WrkActivity_CreatedDtTm')
    lastmodifiedby = models.CharField(
        max_length=255, db_column='WrkActivity_LastModifiedBy', blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        auto_now=True, db_column='WrkActivity_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='WrkActivity_Client_ID')

    class Meta:
        db_table = 'WorkActivity'


class JobList(models.Model):
    key = models.AutoField(primary_key=True, db_column='JobList_Key')
    activity_key = models.ForeignKey(
        WorkActivity, on_delete=models.CASCADE, db_column='JobList_Actvty_Key')
    descr = models.CharField(max_length=255, db_column='JobList_Descr')
    created_by = models.CharField(
        max_length=255, db_column='JobList_CreatedBy')
    createddttm = models.DateTimeField(
        auto_now_add=True, db_column='JobList_CreatedDtTm')
    lastmodifiedby = models.CharField(
        max_length=255, db_column='JobList_LastModifiedBy', blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        auto_now=True, db_column='JobList_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='JobList_Client_ID')

    class Meta:
        db_table = 'JobList'


class MaterialPack(models.Model):
    key = models.AutoField(primary_key=True, db_column='MaterialPack_Key')
    activity_key = models.ForeignKey(
        WorkActivity, on_delete=models.CASCADE, db_column='MaterialPack_Actvty_Key')
    descr = models.CharField(max_length=255, db_column='MaterialPack_Descr')
    created_by = models.CharField(
        max_length=255, db_column='MaterialPack_CreatedBy')
    createddttm = models.DateTimeField(
        auto_now_add=True, db_column='MaterialPack_CreatedDtTm')
    lastmodifiedby = models.CharField(
        max_length=255, db_column='MaterialPack_LastModifiedBy', blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        auto_now=True, db_column='MaterialPack_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='MaterialPack_Client_ID')

    class Meta:
        db_table = 'MaterialPack'
