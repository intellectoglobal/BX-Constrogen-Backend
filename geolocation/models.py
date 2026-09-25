from django.db import models
from users.models import AppUser
from client.models import Company, Clientbase
import re


class State(models.Model):
    key = models.AutoField(db_column='State_Key', primary_key=True)
    id = models.CharField(
        db_column='State_ID', unique=True, max_length=30)
    name = models.CharField(db_column='State_Name', max_length=100)

    class Meta:
        managed = True
        db_table = 'State'


class City(models.Model):
    key = models.AutoField(db_column='City_Key', primary_key=True)
    name = models.CharField(db_column='City_Name', max_length=100)
    state_key = models.ForeignKey(
        State, on_delete=models.CASCADE, db_column='City_State_Key')
    createdby = models.CharField(
        db_column='City_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='City_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='City_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='City_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='City_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE,
        db_column='City_Client_ID')

    class Meta:
        managed = True
        db_table = 'City'
        unique_together = (('company', 'state_key', 'name'),)
