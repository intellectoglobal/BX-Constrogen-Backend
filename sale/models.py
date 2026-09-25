import re
from decimal import Decimal
from django.db import models
from inventory.models import Purpose
from geolocation.models import State, City
from project.models import Project
from client.models import Company, Clientbase
from django.core.validators import RegexValidator, MinValueValidator


class Customer(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Invalid Phonenumber")

    key = models.AutoField(db_column='Cust_Key', primary_key=True)
    id = models.CharField(db_column='Cust_ID', max_length=30)
    name = models.CharField(db_column='Cust_Name', max_length=100)
    age = models.IntegerField(db_column='Cust_Age')
    sex = models.CharField(db_column='Cust_Sex', max_length=10)
    pan_no = models.CharField(db_column='Cust_PanNo', max_length=100)
    gst_no = models.CharField(
        db_column='Cust_GSTNo', max_length=20, blank=True, null=True)
    aadhaar_no = models.CharField(db_column='Cust_AadhaarNo', max_length=12)
    addr1 = models.CharField(db_column='Cust_Addr1',
                             max_length=100, blank=True, null=True)
    addr2 = models.CharField(db_column='Cust_Addr2',
                             max_length=100, blank=True, null=True)
    state_key = models.ForeignKey(
        State, on_delete=models.CASCADE, db_column='Cust_State_Key')
    city_key = models.ForeignKey(
        City, on_delete=models.CASCADE, db_column='Cust_City_Key')
    contact_no = models.CharField(
        db_column='Cust_ContactNo', validators=[phone_regex], max_length=255, blank=True, null=True)
    email_id = models.CharField(
        db_column='Cust_EmailID', max_length=255, blank=True, null=True)
    createdby = models.CharField(
        db_column='Cust_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Cust_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='Cust_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Cust_LastModifiedDtTm', blank=True, null=True)
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='Cust_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='Cust_Client_ID')
    inactive = models.CharField(
        db_column='Cust_InActive', max_length=1, blank=True, null=True)

    @staticmethod
    def nextID():
        currentModelObj = Customer
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
        db_table = 'Customer'


class CustomerPurchaseReceipt(models.Model):
	key = models.AutoField(primary_key= True, db_column = 'CustomerPurchRcpt_key')
	project_key = models.ForeignKey(Project, on_delete = models.CASCADE, db_column = 'CustomerPurchRcpt_ProjKey')
	customer_key = models.ForeignKey(Customer, on_delete = models.CASCADE, db_column ='CustomerPurchRcpt_CustomerKey')
	purpose_key = models.ForeignKey(Purpose, on_delete = models.CASCADE,db_column = 'CustomerPurchRcpt_PurposeKey', null =True)
	item_descr = models.CharField(max_length=100,db_column = 'CustomerPurchRcpt_ItemDesc')
	vendor = models.CharField(max_length=100,db_column ='CustomerPurchRcpt_Vendor', blank=True, null =True)
	amount = models.IntegerField(db_column ='CustomerPurchRcpt_Amount')
	builder_budget = models.IntegerField(db_column ='CustomerPurchRcpt_BuilderBudget', null =True)
	notes = models.CharField(max_length = 100, db_column = 'CustomerPurchRcpt_Notes', blank=True, null =True)
	company_id = models.ForeignKey(Company, on_delete = models.CASCADE, db_column ='CustomerPurchRcpt_CompanyID')
	client_id = models.ForeignKey(Clientbase, on_delete = models.CASCADE, db_column ='CustomerPurchRcpt_ClientID')

	class Meta:
		db_table = 'Customer_Purchase_Receipt'


class SaleAgreement(models.Model):
    key = models.AutoField(db_column="SaleAgreementKey", primary_key=True)
    id = models.CharField(max_length=30, db_column="SaleAgreementID")
    agreement_no = models.CharField(
        max_length=100, db_column="SaleAgreementNo")
    agreement_date = models.DateField(db_column="SaleAgreementDate")
    project_id = models.ForeignKey(
        'project.Project', on_delete=models.CASCADE, db_column="SaleAgreementProjectID")
    unit_id = models.ForeignKey(
        'project.Projectunit', on_delete=models.CASCADE, db_column="SaleAgreementUnitID")
    customer_id = models.ForeignKey(
        Customer,  on_delete=models.CASCADE, db_column="SaleAgreementCustomerID")
    sale_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="SaleAgreementSaleAmount")
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="SaleAgreementPaidAmount")
    notes = models.TextField(blank=True, null=True,
                             db_column="SaleAgreementNotes")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='SaleAgreementCompanyID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='SaleAgreementClientID')

    @staticmethod
    def nextID():
        currentModelObj = SaleAgreement
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
        db_table = 'SaleAgreement'


class SaleAgreementRateCard(models.Model):
    key = models.AutoField(db_column="SARateCardKey", primary_key=True)
    id = models.CharField(max_length=30, db_column="SARateCardID")
    sale_agreement_id = models.ForeignKey(
        SaleAgreement, on_delete=models.CASCADE, db_column="SARateCardAgreementID")
    item_desc = models.CharField(
        max_length=500, db_column="SARateCardItemDesc")
    rate = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="SARateCardRate")

    @staticmethod
    def nextID():
        currentModelObj = SaleAgreementRateCard
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
        db_table = 'SaleAgreementRateCard'


class SaleAgreementPaymentSchedule(models.Model):
    key = models.AutoField(db_column="SAPaymentScheduleKey", primary_key=True)
    id = models.CharField(max_length=255, db_column="SAPaymentScheduleID")
    sale_agreement_id = models.ForeignKey(
        SaleAgreement, on_delete=models.CASCADE, db_column="SAPaymentScheduleAgreementID")
    payment_stage_desc = models.CharField(
        max_length=500, db_column="SAPaymentScheduleDesc")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="SAPaymentScheduleAmount")
    stage_status_choices = [('O', 'O'), ('I', 'I')]
    stage_status = models.CharField(
        max_length=1, choices=stage_status_choices, db_column="SAPaymentScheduleStatus", default="O")


    @staticmethod
    def nextID():
        currentModelObj = SaleAgreementPaymentSchedule
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
        db_table = 'SaleAgreementPaymentSchedule'


class SaleInvoice(models.Model):
    key = models.AutoField(db_column="SaleInvoiceKey", primary_key=True)
    invoice_id = models.CharField(
        max_length=100, db_column="SaleInvoice_InvoiceID")
    invoice_date = models.DateField(db_column="SaleInvoice_InvoiceDate")
    payment_schedule_id = models.ForeignKey(
        SaleAgreementPaymentSchedule, null=True, on_delete=models.CASCADE, db_column="SaleInvoice_PaymentScheldueID")
    invoice_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="SaleInvoice_InvoiceAmount")
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="SaleInvoice_PaidAmount")
    is_tds_invoice = models.BooleanField(db_column="SaleInvoice_IsTDS")
    gst_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="SaleInvoice_GSTAmount")
    invoice_status_choices = [('O', 'O'), ('P', 'P'), ('A', 'A')]
    invoice_status = models.CharField(
        max_length=1, choices=invoice_status_choices, db_column="SaleInvoice_InvoiceStatus", default="O")
    notes = models.CharField(
        max_length=500, db_column="SaleInvoice_Notes", null=True, blank=True)
    agreement_id = models.ForeignKey(
        SaleAgreement, on_delete=models.CASCADE, null=True, blank=True, db_column="SaleInvoice_AgreementID")
    project_id = models.ForeignKey(
        'project.Project', on_delete=models.CASCADE, db_column="SaleInvoice_ProjectID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='SaleInvoice_CompanyID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='SaleInvoice_ClientID')

    class Meta:
        managed = True
        db_table = 'SaleInvoice'


class SourceOfFund(models.Model):
    key = models.AutoField(primary_key=True, db_column="SourceOfFund_Key")
    name = models.CharField(max_length=50, unique=True, db_column="SourceOfFund_Name")

    class Meta:
        managed = True
        db_table = "SourceOfFund"

class SaleReceipt(models.Model):
    key = models.AutoField(primary_key=True, db_column="Sale_Receipt_Key")
    receipt_number = models.IntegerField(db_column='Sale_Receipt_ReceiptNumber')
    date = models.DateField(db_column="Sale_Receipt_Date")
    invoice_id = models.ForeignKey(
        "sale.SaleInvoice",
        on_delete=models.CASCADE,
        db_column="Sale_Receipt_InvoiceID"
    )
    customer_id = models.ForeignKey(
        "sale.Customer",
        on_delete=models.CASCADE,
        db_column="Sale_Receipt_CustID",
        related_name='sale_receipts'
    )
    project_id = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE, 
        db_column="Sale_Receipt_ProjectID")
    unit_id = models.ForeignKey(
        "project.Projectunit",
        on_delete=models.CASCADE,
        db_column="Sale_Receipt_UnitID")
    source_of_fund_id = models.ForeignKey(
        'sale.SourceOfFund', on_delete=models.CASCADE, db_column='Sale_Receipt_SourceOfFundID')
    payment_mode_id = models.ForeignKey(
        'pricing.Modeofpay', on_delete=models.CASCADE, db_column='Sale_Receipt_PaymentModeID')
    account_id = models.ForeignKey(
    "client.BankAccount", on_delete=models.CASCADE, db_column='Sale_Receipt_AccountID', blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="Sale_Receipt_Amount",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    transaction_detail = models.CharField(
        max_length=255, db_column='Sale_Receipt_TransactionDetail', blank=True, null=True)
    notes = models.CharField(
        max_length=255, db_column="Sale_Receipt_Notes", blank=True, null=True)
    client = models.ForeignKey(
        'client.ClientBase',
        on_delete=models.CASCADE,
        db_column="Sale_Receipt_ClientID",
        related_name='sale_receipts'
    )
    company = models.ForeignKey(
        'client.Company',
        on_delete=models.CASCADE,
        db_column="Sale_Receipt_CompanyID",
        related_name='sale_receipts'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_column="Sale_Receipt_CreatedAt"
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_column="Sale_Receipt_UpdatedAt"
    )

    class Meta:
        managed = True
        db_table = "SaleReceipt"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['client']),
            models.Index(fields=['company']),
        ]

    def __str__(self):
        return f"Sale Receipt {self.key}- {self.date}"
    
