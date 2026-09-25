from django.db import models
from geolocation.models import State, City
from client.models import Company, Clientbase, BankAccount
from inventory.models import Itemtype
import re
from django.core.validators import RegexValidator


class Apterms(models.Model):
    key = models.AutoField(db_column='APTerm_Key', primary_key=True)
    id = models.CharField(db_column='APTerm_ID', max_length=30)
    descr = models.CharField(
        db_column='APTerm_Descr', max_length=100, blank=True, null=True)
    days = models.DecimalField(
        db_column='APTerm_Days', max_digits=5, decimal_places=0, blank=True, null=True)
    createdby = models.CharField(
        db_column='APTerm_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='APTerm_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='APTerm_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='APTerm_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='APTerm_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='APTerm_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Apterms
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
        db_table = 'APTerms'
        unique_together = (('company', 'id'),)


class Vendorgroup(models.Model):
    key = models.AutoField(db_column='VendGrp_Key', primary_key=True)
    id = models.CharField(db_column='VendGrp_ID', max_length=30)
    descr = models.CharField(
        db_column='VendGrp_Descr', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='VendGrp_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='VendGrp_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='VendGrp_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='VendGrp_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='VendGrp_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='VendGrp_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Vendorgroup
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
        db_table = 'VendorGroup'
        unique_together = (('company', 'id'),)


class Vendortype(models.Model):
    key = models.AutoField(db_column='VendTyp_Key', primary_key=True)
    descr = models.CharField(
        db_column='VendTyp_Descr', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='VendTyp_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='VendTyp_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='VendTyp_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='VendTyp_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='VendTyp_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='VendTyp_Client_ID')


    class Meta:
        managed = True
        db_table = 'VendorType'


class Vendor(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Invalid Phonenumber")

    key = models.AutoField(db_column='Vend_Key', primary_key=True)
    name = models.CharField(db_column='Vend_Name', max_length=100)
    addr1 = models.CharField(
        db_column='Vend_Addr1', max_length=100, blank=True, null=True)
    addr2 = models.CharField(
        db_column='Vend_Addr2', max_length=100, blank=True, null=True)
    state_key = models.ForeignKey(
        State, on_delete=models.CASCADE, db_column='Vend_State_Key', blank=True, null=True)
    city_key = models.ForeignKey(
        City, on_delete=models.CASCADE, db_column='Vend_City_Key', blank=True, null=True)
    pincode = models.IntegerField(db_column="Vend_PinCode", null=True)
    vendtyp_key = models.ForeignKey(
        Vendortype, on_delete=models.CASCADE, db_column='Vend_VendTyp_Key', blank=True, null=True)
    # vendgrp_key = models.ForeignKey(
    #     Vendorgroup, on_delete=models.CASCADE, db_column='Vend_VendGrp_Key',)
    briefdescr = models.CharField(
        db_column='Vend_BriefDescr', max_length=255, blank=True, null=True)
    apterm_key = models.ForeignKey(
        Apterms, on_delete=models.CASCADE, db_column='Vend_APTerm_Key', blank=True, null=True)
    modeofpay = models.CharField(
        db_column='Vend_ModeOfPay', max_length=10, blank=True, null=True)
    pan_no = models.CharField(db_column='Vend_PanNo', max_length=10,  blank=True, null=True)
    gstnumber = models.CharField(
        db_column='Vend_GSTNumber', max_length=20, blank=True, null=True)
    createdby = models.CharField(
        db_column='Vend_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Vend_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='Vend_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Vend_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='Vend_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='Vend_Client_ID')
    inactive = models.CharField(
        db_column='Vend_InActive', max_length=1, blank=True, null=True, default='N')
    # itemtyp_key = models.ForeignKey(
    #     Itemtype, on_delete=models.CASCADE, db_column='Vend_ItemTyp_Key')
    # itemtype_keys = models.CharField(
    #     db_column='Vend_ItemTyp_Keys', max_length=255)
    contactname = models.CharField(
        db_column='Vend_ContactName', max_length=255, blank=True, null=True)
    contactphoneno = models.CharField(
        db_column='Vend_ContactPhoneNo', validators=[phone_regex], max_length=255, blank=True, null=True)
    landline_no = models.CharField(
        db_column='Vend_ContactLandlineNo', max_length=255, blank=True, null=True)


    class Meta:
        managed = True
        db_table = 'Vendor'

class VendorItemType(models.Model):
    key = models.AutoField(db_column='VendItemType_Key', primary_key=True)
    vend_key = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, db_column='VendItemType_Vend_Key', blank=True, null=True)
    item_type_key = models.ForeignKey(
        Itemtype, on_delete=models.CASCADE, db_column='VendItemType_Item_Type_Key', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='VendItemType_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='VendItemType_Client_ID')
    
    class Meta:
        managed = True
        db_table = 'VendorItemType'


class VendorInvAllocAmt(models.Model):
    key = models.AutoField(primary_key=True, db_column='VendorInvAllocAmt_Key') 
    invoice_id = models.ForeignKey('pricing.Vendorinvoice', on_delete=models.CASCADE, db_column='VendorInvAllocAmt_InvoiceID') 
    allocated_amount = models.IntegerField(db_column='VendorInvAllocAmt_AllocatedAmount')  
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE, db_column='VendorInvAllocAmt_ClientID')  
    class Meta:
        db_table = 'VendorInvAllocAmt'



class VendorPaymentVoucherHdr(models.Model):
    key = models.AutoField(primary_key=True, db_column='VendorPaymentVoucherHdr_Key')
    voucher_number = models.IntegerField(db_column='VendorPaymentVoucherHdr_VoucherNumber')
    vendor_voucher_dt = models.DateField(db_column='VendorPaymentVoucherHdr_VendorVoucherDate') 
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE, db_column='VendorPaymentVoucherHdr_VendorID')
    account_id = models.ForeignKey(BankAccount, on_delete=models.CASCADE, db_column='VendorPaymentVoucherHdr_AccountID', blank=True, null=True)
    payment_mode_id = models.ForeignKey('pricing.Modeofpay', on_delete=models.CASCADE, db_column='VendorPaymentVoucherHdr_PaymentModeID')
    transaction_detail = models.CharField(max_length=255, db_column='VendorPaymentVoucherHdr_TransactionDetail', blank=True, null=True)
    notes = models.CharField(max_length=255,db_column="VendorPaymentVoucherHdr_Notes", blank=True, null=True)
    total_amount = models.DecimalField(db_column='VendorPaymentVoucherHdr_TotalAmount', max_digits=10, decimal_places=2)  
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='VendorPaymentVoucherHdr_CompanyID')  
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE, db_column='VendorPaymentVoucherHdr_ClientID')  

    class Meta:
        db_table = 'VendorPaymentVoucherHdr'


class VendorPaymentVoucherDtl(models.Model):
    key = models.AutoField(primary_key=True, db_column='VendorPaymentVoucherDtl_Key')
    vendor_voucher_hdr = models.ForeignKey(VendorPaymentVoucherHdr, on_delete=models.CASCADE, db_column='VendorPaymentVoucherDtl_VendorPaymentVoucherHdrKey')  
    invoice_id = models.ForeignKey('pricing.Vendorinvoice', on_delete=models.CASCADE, db_column='VendorPaymentVoucherDtl_InvoiceID')  
    paid_amount = models.DecimalField(db_column='VendorPaymentVoucherDtl_PaidAmount', max_digits=10, decimal_places=2)  
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE, db_column='VendorPaymentVoucherDtl_ClientID')  

    class Meta:
        db_table = 'VendorPaymentVoucherDtl'  

        