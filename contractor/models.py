import re
from django.db import models
from geolocation.models import State, City
from vendor.models import Vendor
from project.models import Project
from client.models import Company, Clientbase, BankAccount
from inventory.models import Item, Itemuom, Itemtype
from django.shortcuts import get_object_or_404
from django.core.validators import RegexValidator


class VendorContractManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().all()

    def saveVendorContract(self, params, serializer):

        serializerIns = serializer(data=params)
        if serializerIns.is_valid():
            try:
                serializerIns.save()
                return serializerIns.data, True, "Contract Added Successfully", {}
            except:
                return {}, False, "Error While Adding Contract", {}

        return {}, False, "Error in API request", serializerIns.errors

    def updateVendorContract(self, params, vendContrctKey, serializer, additionalParams={}):
        vendContrctIns = get_object_or_404(
            self.get_queryset(), pk=vendContrctKey)
        try:

            serializerIns = serializer(
                vendContrctIns, data=params, partial=True)
            if serializerIns.is_valid():
                try:
                    serializerIns.save()
                    return serializerIns.data, True, "Contract Updated Successfully", {}
                except:
                    return {}, False, "Error In Contract PUT Request", {}
            else:
                return {}, False, "Error In Contract PUT Request", serializerIns.errors
        except Exception as e:
            return {}, False, "Something went wrong. Please check input params", {}

    def cancelVendorContract(self, request, pk, serializer, currentDate, currentUser):
        otherTableUpdateReq = True
        VendContractIns = get_object_or_404(self.get_queryset(), pk=pk)

        if VendContractIns.docstatus == "S":
            otherTableUpdateReq = False
        elif VendContractIns.docstatus == "U":
            otherTableUpdateReq = True

        VendContractIns.docstatus = "C"
        VendContractIns.cancelledby = currentUser
        VendContractIns.cancelleddttm = currentDate

        VendContractIns.save()
        return serializer(VendContractIns).data, True, "Invoice Update Success", {}, otherTableUpdateReq

    def deleteAllVendorContractStageByVendorContractID(self, vendContrctKey):
        VendorcontractStages.objects.filter(
            vendctr_key=vendContrctKey).delete()

    def deleteAllVendorContractTasksByVendorContractID(self, vendContrctKey):
        VendorcontractTasks.objects.filter(vendctr_key=vendContrctKey).delete()

    def deleteVendorContractByVendorContractID(self, vendContrctKey):
        Vendorcontract.objects.get(key=vendContrctKey).delete()

    def insertVendorContractStage(self, params, ContractStgSerialiser):
        vendctr_key = params.get("vendctr_key", False)
        company = params.get("company", False)
        client_id = params.get("client_id", False)
        user = params.get("user")

        # Removing all items first
        self.deleteAllVendorContractStageByVendorContractID(vendctr_key)
        # GET UOM FOR 'EACH' row

        itemTypsIns, createdSuccess = Itemtype.objects.get_or_create(
            id="EACH_ID",
            descr='EACH',
            client_id=client_id,
            company=Company.objects.get(id=company)
        )

        uomInstance, created = Itemuom.objects.get_or_create(
            id='EACH',
            client_id=client_id,
            company=Company.objects.get(id=company),
            itemtyp_key=itemTypsIns
        )

        if created:
            uomInstance.createddttm = params.get('createddttm')
            uomInstance.createdby = params.get('createdby')
            uomInstance.save()

        if vendctr_key and company and client_id:
            insertedData = []
            stages = params.get('vend_contract_stages', [])
            for stg in stages:
                stg['vendctr_key'] = vendctr_key
                stg['company'] = company
                stg['client_id'] = client_id
                stg['createdby'] = user
                stg['itemuom_key'] = uomInstance.key
                stg['qty'] = 1
                stg['unitprice'] = stg['netamt']

                serializer = ContractStgSerialiser(data=stg)
                try:
                    if serializer.is_valid():
                        serializer.save()
                        insertedData.append(serializer.data)
                    else:
                        # if any one invoice items failed to load, delete all invoice items
                        self.deleteAllVendorContractStageByVendorContractID(
                            vendctr_key)
                        return {}, False, "Error in API request", serializer.errors
                except:
                    # if any one invoice items failed to load, delete all invoice items
                    self.deleteAllVendorContractStageByVendorContractID(
                        vendctr_key)
                    return {}, False, "Error While Adding Contract Stages", {}

            if len(insertedData) == len(stages):
                return insertedData, True, "Contract Stages Modified Successfully", {}
            else:
                # if any one invoice items failed to load, delete all invoice items
                self.deleteAllVendorContractStageByVendorContractID(
                    vendctr_key)
                return {}, False, "Error While Adding Invoice Items", {}
        else:
            return {}, False, "Contract Key (or) company (or) client_id is missing", {}

    def insertVendorContractTasks(self, params, ContractTskSerialiser):
        vendctr_key = params.get("vendctr_key", False)
        company = params.get("company", False)
        client_id = params.get("client_id", False)
        user = params.get("user")

        # Removing all items first
        self.deleteAllVendorContractTasksByVendorContractID(vendctr_key)

        if vendctr_key and company and client_id:
            insertedData = []
            tasks = params.get('vend_contract_tasks', [])
            for tsk in tasks:
                tsk['vendctr_key'] = vendctr_key
                tsk['company'] = company
                tsk['client_id'] = client_id
                tsk['createdby'] = user
                serializer = ContractTskSerialiser(data=tsk)
                try:
                    if serializer.is_valid():
                        serializer.save()
                        insertedData.append(serializer.data)
                    else:
                        # if any one invoice items failed to load, delete all invoice items
                        self.deleteAllVendorContractTasksByVendorContractID(
                            vendctr_key)
                        return {}, False, "Error in API request", serializer.errors
                except:
                    # if any one invoice items failed to load, delete all invoice items
                    self.deleteAllVendorContractTasksByVendorContractID(
                        vendctr_key)
                    return {}, False, "Error While Adding Contract Stages", {}

            if len(insertedData) == len(tasks):
                return insertedData, True, "Contract Task Modified Successfully", {}
            else:
                # if any one invoice items failed to load, delete all invoice items
                self.deleteAllVendorContractTasksByVendorContractID(
                    vendctr_key)
                return {}, False, "Error While Adding Invoice Items", {}
        else:
            return {}, False, "Contract Key (or) company (or) client_id is missing", {}

    def rollBack(self, conKey):
        # If Contract Stage and Tasks failed to load drollback everything
        self.deleteAllVendorContractTasksByVendorContractID(
            conKey)
        self.deleteAllVendorContractStageByVendorContractID(
            conKey)
        self.deleteVendorContractByVendorContractID(
            conKey)


class Vendorcontract(models.Model):
    key = models.AutoField(db_column='VendCtr_Key', primary_key=True)
    docid = models.CharField(db_column='VendCtr_DocID', max_length=3)
    vend_key = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, db_column='VendCtr_Vend_Key')
    contractno = models.CharField(
        db_column='VendCtr_ContractNo', max_length=25)
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='VendCtr_Proj_Key')
    contractdate = models.DateField(db_column='VendCtr_ContractDate')
    notes = models.CharField(db_column='VendCtr_Notes',
                             max_length=255, blank=True, null=True)
    docstatus = models.CharField(
        db_column='VendCtr_DocStatus', max_length=2, blank=True, null=True)
    submitteddttm = models.DateTimeField(
        db_column='VendCtr_SubmittedDtTm', blank=True, null=True)
    submittedby = models.CharField(
        db_column='VendCtr_SubmittedBy', max_length=100, blank=True, null=True)
    cancelleddttm = models.DateTimeField(
        db_column='VendCtr_CancelledDtTm', blank=True, null=True)
    cancelledby = models.CharField(
        db_column='VendCtr_CancelledBy', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='VendCtr_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='VendCtr_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='VendCtr_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='VendCtr_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='VendCtr_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='VendCtr_Client_ID')
    objects = VendorContractManager()

    class Meta:
        managed = True
        db_table = 'VendorContract'
        unique_together = (('company', 'docid', 'contractno'),)


class VendorcontractStages(models.Model):
    key = models.AutoField(db_column='VendCtrStg_Key', primary_key=True)
    vendctr_key = models.ForeignKey(
        Vendorcontract, on_delete=models.CASCADE, db_column='VendCtrStg_VendCtr_Key')
    item_descr = models.CharField(
        db_column='VendCtrStg_Item_Descr', max_length=100, blank=True, null=True)
    itemuom_key = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column='VendCtrStg_ItemUOM_Key')
    qty = models.DecimalField(db_column='VendCtrStg_Qty',
                              max_digits=15, decimal_places=5, blank=True, null=True)
    unitprice = models.DecimalField(
        db_column='VendCtrStg_UnitPrice', max_digits=15, decimal_places=2, blank=True, null=True)
    netamt = models.DecimalField(
        db_column='VendCtrStg_NetAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    invoiced = models.CharField(
        db_column='VendCtrStg_Invoiced', max_length=1, blank=True, null=True)
    itemnotes = models.CharField(
        db_column='VendCtrStg_ItemNotes', max_length=255, blank=True, null=True)
    createdby = models.CharField(
        db_column='VendCtrStg_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='VendCtrStg_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='VendCtrStg_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='VendCtrStg_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='VendCtrStg_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='VendCtrStg_Client_ID')

    class Meta:
        managed = True
        db_table = 'VendorContract_Stages'
        unique_together = (
            ('company', 'vendctr_key', 'item_descr', 'itemuom_key'),)


class VendorcontractTasks(models.Model):
    key = models.AutoField(db_column='VendCtrTsk_Key', primary_key=True)
    vendctr_key = models.ForeignKey(
        Vendorcontract, on_delete=models.CASCADE, db_column='VendCtrTsk_VendCtr_Key')
    item_descr = models.CharField(
        db_column='VendCtrTsk_Item_Descr', max_length=100, blank=True, null=True)
    itemuom_key = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column='VendCtrTsk_ItemUOM_Key')
    qty = models.DecimalField(db_column='VendCtrTsk_Qty',
                              max_digits=15, decimal_places=5, blank=True, null=True)
    unitprice = models.DecimalField(
        db_column='VendCtrTsk_UnitPrice', max_digits=15, decimal_places=2, blank=True, null=True)
    netamt = models.DecimalField(
        db_column='VendCtrTsk_NetAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    itemnotes = models.CharField(
        db_column='VendCtrTsk_ItemNotes', max_length=255, blank=True, null=True)
    createdby = models.CharField(
        db_column='VendCtrTsk_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='VendCtrTsk_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='VendCtrTsk_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='VendCtrTsk_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='VendCtrTsk_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='VendCtrTsk_Client_ID')

    class Meta:
        managed = True
        db_table = 'VendorContract_Tasks'
        unique_together = (
            ('company', 'vendctr_key', 'item_descr', 'itemuom_key'),)


class ContractorType(models.Model):
    key = models.AutoField(db_column='ContractorTyp_Key', primary_key=True)
    descr = models.CharField(
        db_column='ContractorTyp_Descr', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='ContractorTyp_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ContractorTyp_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ContractorTyp_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ContractorTyp_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ContractorTyp_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ContractorTyp_Client_ID')

    class Meta:
        managed = True
        db_table = 'ContractorType'


class Contractor(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Invalid Phonenumber")

    key = models.AutoField(db_column='Contractor_Key', primary_key=True)
    name = models.CharField(db_column='Contractor_Name', max_length=100)
    addr1 = models.CharField(
        db_column='Contractor_Addr1', max_length=100, blank=True, null=True)
    addr2 = models.CharField(
        db_column='Contractor_Addr2', max_length=100, blank=True, null=True)
    state_key = models.ForeignKey(
        State, on_delete=models.CASCADE, db_column='Contractor_State_Key', blank=True, null=True)
    city_key = models.ForeignKey(
        City, on_delete=models.CASCADE, db_column='Contractor_City_Key', blank=True, null=True)
    pincode = models.IntegerField(db_column="Contractor_PinCode", null=True)
    contractortyp_key = models.ForeignKey(
        ContractorType, on_delete=models.CASCADE, db_column='Contractor_ContractorTyp_Key')
    pan_no = models.CharField(db_column='Contractor_PanNo', max_length=10,  blank=True, null=True)
    gstnumber = models.CharField(
        db_column='Contractor_GSTNumber', max_length=20, blank=True, null=True)
    phoneno = models.CharField(
        db_column='Contractor_ContactPhoneNo', validators=[phone_regex], max_length=255, blank=True, null=True)
    landline_no = models.CharField(
        db_column='Contractor_ContactLandlineNo', max_length=255, blank=True, null=True)
    email_id = models.CharField(
        db_column='Contractor_ContactEmailID', max_length=255, blank=True, null=True)
    inactive = models.CharField(
        db_column='Contractor_InActive', max_length=1, blank=True, null=True, default='N')
    inhouse = models.CharField(
        db_column='Contractor_InHouse', max_length=1, blank=True, null=True, default='N')
    createdby = models.CharField(
        db_column='Contractor_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Contractor_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='Contractor_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Contractor_LastModifiedDtTm', blank=True, null=True)
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='Contractor_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='Contractor_Client_ID')

    class Meta:
        managed = True
        db_table = 'Contractor'


class ContractAgreement(models.Model):
    key = models.AutoField(db_column="ContractAgreementKey", primary_key=True)
    id = models.CharField(max_length=30, db_column="ContractAgreementID")
    agreement_no = models.CharField(
        max_length=100, unique=True, db_column="ContractAgreementNo")
    agreement_date = models.DateField(db_column="ContractAgreementDate")
    contractor_id = models.ForeignKey(
        Contractor, on_delete=models.CASCADE, db_column="ContractAgreementContractorID")
    project_id = models.ForeignKey(
        'project.Project', on_delete=models.CASCADE, db_column="ContractAgreementProjectID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ContractAgreementCompany_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ContractAgreementClient_ID')
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="ContractAgreementTotalAmount")
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="ContractAgreementPaidAmount")
    notes = models.TextField(blank=True, null=True,
                             db_column="ContractAgreementNotes")

    @staticmethod
    def nextID():
        currentModelObj = ContractAgreement
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
        db_table = 'ContractAgreement'


class ContractAgreementService(models.Model):
    key = models.AutoField(db_column="CAServiceKey", primary_key=True)
    id = models.CharField(max_length=30, db_column="CAServiceID")
    contract_agreement_id = models.ForeignKey(
        ContractAgreement, on_delete=models.CASCADE, db_column="CAServiceAgreementID")
    service_desc = models.CharField(max_length=500, db_column="CAServiceDesc")
    quantity = models.DecimalField(
        db_column="CAServiceQuantity", max_digits=10, decimal_places=2)
    uom = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column="CAServiceUOMID")
    rate_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="CAServiceRatePerUnit")
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="CAServiceCost")

    @staticmethod
    def nextID():
        currentModelObj = ContractAgreementService
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
        db_table = 'ContractAgreementService'


class ContractAgreementPaymentSchedule(models.Model):
    key = models.AutoField(db_column="CAPaymentScheduleKey", primary_key=True)
    id = models.CharField(max_length=255, db_column="CAPaymentScheduleID")
    contract_agreement_id = models.ForeignKey(
        ContractAgreement, on_delete=models.CASCADE, db_column="CAPaymentScheduleAgreementID")
    payment_stage_desc = models.CharField(
        max_length=500, db_column="CAPaymentScheduleDesc")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="CAPaymentScheduleAmnt")
    stage_status_choices = [('O', 'O'), ('I', 'I')]
    stage_status = models.CharField(
        max_length=1, choices=stage_status_choices, db_column="CAPaymentScheduleStatus", default="O")

    @staticmethod
    def nextID():
        currentModelObj = ContractAgreementPaymentSchedule
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
        db_table = 'ContractAgreementPaymentSchedule'


class ContractorInvoice(models.Model):
    key = models.AutoField(db_column="ContractorInvoiceKey", primary_key=True)
    invoice_id = models.CharField(
        max_length=100, unique=True, db_column="ContractorInvoice_InvoiceID")
    invoice_date = models.DateField(db_column="ContractorInvoice_InvoiceDate")
    payment_schedule_id = models.ForeignKey(
        ContractAgreementPaymentSchedule, null=True, on_delete=models.CASCADE, db_column="ContractorInvoice_PaymentScheldueID")
    invoice_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="ContractorInvoice_InvoiceAmount")
    payable_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, db_column="ContractorInvoice_PayableAmount")
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="ContractorInvoice_PaidAmount")
    tds_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="ContractorInvoice_TDSAmount")
    invoice_status_choices = [('O', 'O'), ('P', 'P'), ('A', 'A')]
    invoice_status = models.CharField(
        max_length=1, choices=invoice_status_choices, db_column="ContractorInvoice_InvoiceStatus", default="O")
    invoice_type_choices = [('C', 'C'), ('N', 'N')]
    invoice_type = models.CharField(
        max_length=1, choices=invoice_type_choices, db_column="ContractorInvoice_InvoiceType")
    invoice_desc = models.CharField(
        max_length=500, db_column="ContractorInvoice_InvoiceDesc", null=True, blank=True)
    contractor_id = models.ForeignKey(
        Contractor, on_delete=models.CASCADE, blank=True, db_column="ContractorInvoice_ContractorID")
    agreement_id = models.ForeignKey(
        ContractAgreement, on_delete=models.CASCADE, null=True, blank=True, db_column="ContractorInvoice_AgreementID")
    project_id = models.ForeignKey(
        'project.Project', on_delete=models.CASCADE, db_column="ContractorInvoice_ProjectID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ContractorInvoice_CompanyID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ContractorInvoice_ClientID')

    class Meta:
        managed = True
        db_table = 'ContractorInvoice'


class ContractInvAllocAmt(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='ContractInvAllocAmt_Key')
    invoice_id = models.ForeignKey(
        ContractorInvoice, on_delete=models.CASCADE, db_column='ContractInvAllocAmt_InvoiceID')
    allocated_amount = models.IntegerField(
        db_column='ContractInvAllocAmt_AllocatedAmount')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ContractInvAllocAmt_ClientID')

    class Meta:
        db_table = 'ContractInvAllocAmt'


class ContractVoucherHdr(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='ContractVoucherHdr_Key')
    voucher_number = models.IntegerField(
        db_column='ContractVoucherHdr_VoucherNumber')
    contract_voucher_dt = models.DateField(
        db_column='ContractVoucherHdr_ContractVoucherDate')
    contractor_id = models.ForeignKey(
        Contractor, on_delete=models.CASCADE, db_column='ContractVoucherHdr_ContractorID')
    account_id = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, db_column='ContractVoucherHdr_AccountID', blank=True, null=True)
    payment_mode_id = models.ForeignKey(
        'pricing.Modeofpay', on_delete=models.CASCADE, db_column='ContractVoucherHdr_PaymentModeID')
    transaction_detail = models.CharField(
        max_length=255, db_column='ContractVoucherHdr_TransactionDetail', blank=True, null=True)
    notes = models.CharField(
        max_length=255, db_column="ContractVoucherHdr_Notes", blank=True, null=True)
    total_amount = models.IntegerField(
        db_column='ContractVoucherHdr_TotalAmount')
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ContractVoucherHdr_CompanyID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ContractVoucherHdr_ClientID')

    class Meta:
        db_table = 'ContractVoucherHdr'


class ContractVoucherDtl(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='ContractVoucherDtl_Key')
    contract_voucher_hdr = models.ForeignKey(
        'ContractVoucherHdr', on_delete=models.CASCADE, db_column='ContractVoucherDtl_ContractVoucherHdrKey')
    invoice_id = models.ForeignKey(
        ContractorInvoice, on_delete=models.CASCADE, db_column='ContractVoucherDtl_InvoiceID')
    paid_amount = models.IntegerField(
        db_column='ContractVoucherDtl_PaidAmount')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ContractVoucherDtl_ClientID')

    class Meta:
        db_table = 'ContractVoucherDtl'

