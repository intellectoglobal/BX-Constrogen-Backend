from django.db import models
from users.models import AppUser
from geolocation.models import State, City
from client.models import Company, Clientbase, Costcode, Costcategory, BankAccount
from geolocation.models import State, City
from vendor.models import Vendortype
from estimate.models import WorkCategory, WorkType
import re


class Amenity(models.Model):
    key = models.AutoField(db_column='Amnty_Key', primary_key=True)
    id = models.CharField(db_column='Amnty_ID', max_length=30)
    descr = models.CharField(
        db_column='Amnty_Descr', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='Amnty_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Amnty_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='Amnty_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Amnty_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='Amnty_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='Amnty_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Amenity
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
        db_table = 'Amenity'
        unique_together = (('company', 'id'),)


class Projecttype(models.Model):
    key = models.AutoField(db_column='ProjTyp_Key', primary_key=True)
    descr = models.CharField(
        db_column='ProjTyp_Descr', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='ProjTyp_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjTyp_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjTyp_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjTyp_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjTyp_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ProjTyp_Client_ID')

    class Meta:
        managed = True
        db_table = 'ProjectType'


class Projectstatus(models.Model):
    key = models.AutoField(
        db_column='ProjStatus_Key', primary_key=True)
    descr = models.CharField(
        db_column='ProjStatus_Descr', max_length=100)
    is_active = models.BooleanField(
        db_column='ProjStatus_Is_Active_State', default=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjStatus_Company_ID', max_length=20)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ProjStatus_Client_ID')

    class Meta:
        managed = True
        db_table = 'ProjectStatus'
        unique_together = (('company', 'descr'),)


class Project(models.Model):
    key = models.AutoField(db_column='Proj_Key', primary_key=True)
    name = models.CharField(db_column='Proj_Name', max_length=100)
    door_no = models.IntegerField(
        db_column="Proj_DoorNo", blank=True, null=True)
    plot_no = models.IntegerField(
        db_column="Proj_PlotNo", blank=True, null=True)
    survey_no = models.IntegerField(
        db_column="Proj_SurveyNo", blank=True, null=True)
    addr1 = models.CharField(
        db_column='Proj_Addr1', max_length=255, blank=True, null=True)
    addr2 = models.CharField(
        db_column='Proj_Addr2', max_length=100, blank=True, null=True)
    streetname = models.CharField(
        db_column='Proj_Street', max_length=100, blank=True, null=True)
    area = models.CharField(
        db_column='Proj_Area', max_length=100, blank=True, null=True)
    state_key = models.ForeignKey(
        State, on_delete=models.CASCADE, db_column='Proj_State_Key', blank=True, null=True)
    city_key = models.ForeignKey(
        City, on_delete=models.CASCADE, db_column='Proj_City_Key', blank=True, null=True)
    projtyp_key = models.ForeignKey(
        Projecttype, on_delete=models.CASCADE, db_column='Proj_ProjTyp_Key', blank=True, null=True)
    briefdescr = models.TextField(
        db_column='Proj_BriefDescr', blank=True, null=True)
    possessionby = models.CharField(
        db_column='Proj_PossessionBy', max_length=20, blank=True, null=True)
    projstatus_key = models.ForeignKey(
        Projectstatus, on_delete=models.CASCADE, db_column='Proj_ProjStatus_Key')
    elevationimage = models.TextField(
        db_column='Proj_ElevationImage', blank=True, null=True)
    no_of_blocks = models.CharField(
        db_column='Proj_No_Of_Blocks', max_length=100, blank=True, null=True)
    no_of_units = models.CharField(
        db_column='Proj_No_Of_Units', max_length=100, blank=True, null=True)
    totallandarea = models.DecimalField(
        db_column='Proj_TotalLandArea', max_digits=12, decimal_places=2, blank=True, null=True)
    builtuparea = models.DecimalField(
        db_column='Proj_BuiltUpArea', max_digits=12, decimal_places=2, blank=True, null=True)
    car_parking_cost = models.DecimalField(
        db_column='Proj_CarParkingCost', max_digits=12, decimal_places=2, blank=True, null=True)
    eb_cost = models.DecimalField(
        db_column='Proj_EBCost', max_digits=12, decimal_places=2, blank=True, null=True)
    water_and_drainage_cost = models.DecimalField(
        db_column='Proj_WaterAndDrainageCost', max_digits=12, decimal_places=2, blank=True, null=True)
    eb_service_no = models.CharField(
        db_column='Proj_EBServiceNo', max_length=20, blank=True, null=True)
    arn = models.CharField(db_column='Proj_ARN',
                           max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='Proj_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Proj_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='Proj_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Proj_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='Proj_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='Proj_Client_ID')

    class Meta:
        managed = True
        db_table = 'Project'


class Projcostcode(models.Model):
    key = models.AutoField(
        db_column='ProjCstCd_Key', primary_key=True)
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='ProjCstCd_Proj_Key')
    costcd_key = models.ForeignKey(
        Costcode, on_delete=models.CASCADE, db_column='ProjCstCd_CostCd_Key')
    amount = models.DecimalField(
        db_column='ProjCstCd_Amount', max_digits=15, decimal_places=2, blank=True, null=True)
    createdby = models.CharField(
        db_column='ProjCstCd_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjCstCd_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjCstCd_LastModifiedBy', max_length=100, blank=True, null=True)
    plastmodifieddttm = models.DateTimeField(
        db_column='ProjCstCd_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjCstCd_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ProjCstCd_Client_ID')

    class Meta:
        managed = True
        db_table = 'ProjCostCode'
        unique_together = (
            ('company', 'key'),)


class Projectamenity(models.Model):
    key = models.AutoField(
        db_column='ProjAmnty_Key', primary_key=True)
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='ProjAmnty_Proj_Key')
    amnty_key = models.ForeignKey(
        Amenity, on_delete=models.CASCADE, db_column='ProjAmnty_Amnty_Key')
    createdby = models.CharField(
        db_column='ProjAmnty_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjAmnty_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjAmnty_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjAmnty_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjAmnty_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ProjAmnty_Client_ID')

    class Meta:
        managed = True
        db_table = 'ProjectAmenity'
        unique_together = (
            ('company', 'proj_key', 'amnty_key'),)


class Projectblock(models.Model):
    key = models.AutoField(db_column='ProjBlk_Key', primary_key=True)
    id = models.CharField(db_column='ProjBlk_ID', max_length=30)
    descr = models.CharField(db_column='ProjBlk_Descr',
                             max_length=100, blank=True, null=True)
    floor_count_abv_ground = models.IntegerField(
        db_column='ProjBlk_FlrCount_AbvGrnd', blank=True, null=True)
    floor_count_blw_ground = models.IntegerField(
        db_column='ProjBlk_FlrCount_BlwGrnd', blank=True, null=True)
    unit_count = models.IntegerField(
        db_column='ProjBlk_UnitCount', blank=True, null=True)
    column_count = models.IntegerField(
        db_column='ProjBlk_ColmnCount', blank=True, null=True)
    lift_count = models.IntegerField(
        db_column='ProjBlk_LiftCount', blank=True, null=True, default=1)
    staircase_count = models.IntegerField(
        db_column='ProjBlk_StrCaseCount', blank=True, null=True, default=1)
    sump_count = models.IntegerField(
        db_column='ProjBlk_SumpCount', blank=True, null=True, default=1)
    overhead_tank_count = models.IntegerField(
        db_column='ProjBlk_OvrHdTnkCount', blank=True, null=True, default=1)
    ots_count = models.IntegerField(
        db_column='ProjBlk_OtsCount', blank=True, null=True, default=1)
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='ProjBlk_Proj_Key')
    createdby = models.CharField(
        db_column='ProjBlk_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjBlk_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjBlk_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjBlk_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjBlk_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ProjBlk_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Projectblock
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
        db_table = 'ProjectBlock'
        unique_together = (('company', 'proj_key', 'id'),)


class Projectfloor(models.Model):
    key = models.AutoField(db_column='ProjFlr_Key', primary_key=True)
    projblk_key = models.ForeignKey(
        Projectblock, on_delete=models.CASCADE, db_column='ProjFlr_ProjBlk_Key')
    id = models.CharField(db_column='ProjFlr_ID', max_length=30)
    descr = models.CharField(db_column='ProjFlr_Descr',
                             max_length=100, blank=True, null=True)
    no_of_units = models.CharField(db_column='ProjFlr_NoOfUnits',
                             max_length=100, blank=True, null=True)
    pricediff = models.DecimalField(
        db_column='ProjFlr_PriceDiff', max_digits=12, decimal_places=2, blank=True, null=True)
    createdby = models.CharField(
        db_column='ProjFlr_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjFlr_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjFlr_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjFlr_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjFlr_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ProjFlr_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Projectfloor
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
        db_table = 'ProjectFloor'
        unique_together = (('company', 'projblk_key', 'id'),)


class ProjectUnitStatus(models.Model):
    key = models.AutoField(
        db_column='ProjUnitStatus_Key', primary_key=True)
    descr = models.CharField(
        db_column='ProjUnitStatus_Descr', max_length=100)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjUnitStatus_Company_ID', max_length=20)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ProjUnitStatus_Client_ID')

    class Meta:
        managed = True
        db_table = 'ProjectUnitStatus'


class Projectunit(models.Model):
    key = models.AutoField(db_column='ProjUnit_Key', primary_key=True)
    id = models.CharField(db_column='ProjUnit_ID', max_length=30)
    descr = models.CharField(db_column='ProjUnit_Descr',
                             max_length=100, blank=True, null=True)
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='ProjUnit_Proj_Key')
    projflr_key = models.ForeignKey(
        Projectfloor, on_delete=models.CASCADE, db_column='ProjUnit_ProjFlr_Key')
    projblk_key = models.ForeignKey(
        Projectblock, on_delete=models.CASCADE, db_column='ProjUnit_ProjBlk_Key')
    projunit_status_key = models.ForeignKey(
        ProjectUnitStatus, on_delete=models.CASCADE, db_column='ProjUnit_Status_Key', blank=True, null=True)
    bedrooms = models.IntegerField(
        db_column='ProjUnit_Bedrooms', blank=True, null=True)
    bathrooms = models.IntegerField(
        db_column='ProjUnit_Bathrooms', blank=True, null=True)
    attachedbaths = models.IntegerField(
        db_column='ProjUnit_AttachedBaths', blank=True, null=True)
    balconies = models.IntegerField(
        db_column='ProjUnit_Balconies', blank=True, null=True)
    servicearea = models.CharField(
        db_column='ProjUnit_ServiceArea', max_length=1, blank=True, null=True)
    poojaroom = models.CharField(
        db_column='ProjUnit_PoojaRoom', max_length=1, blank=True, null=True)
    carparking = models.CharField(
        db_column='ProjUnit_Carparking', max_length=1, blank=True, null=True)
    allotedparkingspot = models.CharField(
        db_column='ProjUnit_AllotedParkingSpot', max_length=10, blank=True, null=True)
    carpetarea = models.DecimalField(
        db_column='ProjUnit_CarpetArea', max_digits=10, decimal_places=3, blank=True, null=True)
    saleablearea = models.DecimalField(
        db_column='ProjUnit_SaleableArea', max_digits=10, decimal_places=3, blank=True, null=True)
    udsarea = models.DecimalField(
        db_column='ProjUnit_UDSArea', max_digits=10, decimal_places=3, blank=True, null=True)
    bsp = models.DecimalField(
        db_column='ProjUnit_BSP', max_digits=12, decimal_places=2, blank=True, null=True)
    plc = models.DecimalField(
        db_column='ProjUnit_PLC', max_digits=12, decimal_places=2, blank=True, null=True)
    fms = models.DecimalField(
        db_column='ProjUnit_FMS', max_digits=12, decimal_places=2, blank=True, null=True)
    edc = models.DecimalField(
        db_column='ProjUnit_EDC', max_digits=12, decimal_places=2, blank=True, null=True)
    unitstatus = models.CharField(
        db_column='ProjUnit_UnitStatus', max_length=1, blank=True, null=True)
    salbk_key = models.IntegerField(
        db_column='ProjUnit_SalBk_Key', blank=True, null=True)
    base_price = models.DecimalField(
        db_column="ProjUnit_BasePrice", max_digits=12, decimal_places=2, blank=True, null=True)
    FACING_CHOICES = [
        ('North', 'North'),
        ('South', 'South'),
        ('East', 'East'),
        ('West', 'West')
    ]
    facing = models.CharField(db_column='ProjUnit_Facing',
                              max_length=5, choices=FACING_CHOICES, null=True, blank=True)
    gst_percentage = models.IntegerField(
        db_column='ProjUnit_GSTPercentage', blank=True, null=True)
    createdby = models.CharField(
        db_column='ProjUnit_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjUnit_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjUnit_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjUnit_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjUnit_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ProjUnit_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Projectunit
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
        db_table = 'ProjectUnit'
        unique_together = (('company', 'projblk_key', 'id'),)


class ProjectWork(models.Model):
    key = models.AutoField(primary_key=True, db_column='ProjectWork_Key')
    project_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='ProjectWork_ProjKey')
    block_key = models.ForeignKey(
        Projectblock, on_delete=models.CASCADE, db_column='ProjectWork_BlkKey')
    category_key = models.ForeignKey(
        WorkCategory, on_delete=models.CASCADE, db_column='ProjectWork_CtgryKey')
    type_key = models.ForeignKey(
        WorkType, on_delete=models.CASCADE, db_column='ProjectWork_TypeKey')
    name = models.CharField(max_length=255, db_column='ProjectWork_Name')
    segment = models.CharField(max_length=255, db_column='ProjectWork_Sgmnt')
    created_by = models.CharField(
        max_length=255, db_column='ProjectWork_CreatedBy')
    createddttm = models.DateTimeField(
        auto_now_add=True, db_column='ProjectWork_CreatedDtTm')
    lastmodifiedby = models.CharField(
        max_length=255, db_column='ProjectWork_LastModifiedBy', blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        auto_now=True, db_column='ProjectWork_LastModifiedDtTm', blank=True, null=True)
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjectWork_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ProjectWork_Client_ID')

    class Meta:
        db_table = 'ProjectWork'


class Projectstage(models.Model):
    key = models.AutoField(db_column='ProjStg_Key', primary_key=True)
    id = models.CharField(db_column='ProjStg_ID', max_length=30)
    descr = models.CharField(db_column='ProjStg_Descr',
                             max_length=100, blank=True, null=True)
    projwrk_key = models.ForeignKey(
        ProjectWork, on_delete=models.CASCADE, db_column='ProjStg_ProjWrk_Key', blank=True, null=True)
    complperc = models.DecimalField(
        db_column='ProjStg_ComplPerc', max_digits=6, decimal_places=2, blank=True, null=True)
    createdby = models.CharField(
        db_column='ProjStg_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjStg_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjStg_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjStg_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjStg_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ProjStg_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Projectstage
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
        db_table = 'ProjectStage'
        unique_together = (('company', 'projwrk_key', 'id'),)


class Projpayterms(models.Model):
    key = models.AutoField(db_column='ProjPay_Key', primary_key=True)
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='ProjPay_Proj_Key')
    term = models.CharField(db_column='ProjPay_Term', max_length=100)
    termcharges = models.CharField(
        db_column='ProjPay_TermCharges', max_length=255)
    createdby = models.CharField(
        db_column='ProjPay_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjPay_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjPay_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjPay_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjPay_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ProjPay_Client_ID')

    class Meta:
        managed = True
        db_table = 'ProjPayTerms'
        unique_together = (('company', 'proj_key', 'term'),)


class Projpricehistory(models.Model):
    key = models.AutoField(db_column='ProjPrcHist_Key', primary_key=True)
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='ProjPrcHist_Proj_Key')
    effdate = models.DateField(db_column='ProjPrcHist_EffDate')
    effprice = models.DecimalField(
        db_column='ProjPrcHist_EffPrice', max_digits=12, decimal_places=2)
    notes = models.CharField(
        db_column='ProjPrcHist_Notes', max_length=255, blank=True, null=True)
    createdby = models.CharField(
        db_column='ProjPrcHist_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjPrcHist_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjPrcHist_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjPrcHist_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjPrcHist_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ProjPrcHist_Client_ID')

    class Meta:
        managed = True
        db_table = 'ProjPriceHistory'
        unique_together = (('company', 'proj_key', 'effdate'),)


class Projstatushistory(models.Model):
    key = models.AutoField(db_column='ProjStsHist_Key', primary_key=True)
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='ProjStsHist_Proj_Key')
    effdate = models.DateField(db_column='ProjStsHist_EffDate')
    projstatus_key = models.ForeignKey(
        Projectstatus, on_delete=models.CASCADE, db_column='ProjStsHist_ProjStatus_Key')
    createdby = models.CharField(
        db_column='ProjStsHist_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjStsHist_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjStsHist_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjStsHist_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjStsHist_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ProjStsHist_Client_ID')

    class Meta:
        managed = True
        db_table = 'ProjStatusHistory'
        unique_together = (('company', 'proj_key', 'effdate'),)


class Projecttask(models.Model):
    key = models.AutoField(db_column='ProjTsk_Key', primary_key=True)
    id = models.CharField(db_column='ProjTsk_ID', max_length=30)
    descr = models.CharField(db_column='ProjTsk_Descr',
                             max_length=100, blank=True, null=True)
    projstg_key = models.ForeignKey(
        Projectstage, on_delete=models.CASCADE, db_column='ProjTsk_ProjStg_Key')
    tskcomplperc = models.DecimalField(
        db_column='ProjTsk_TskComplPerc', max_digits=6, decimal_places=2, blank=True, null=True)
    startdate = models.DateField(
        db_column='ProjTsk_StartDate', blank=True, null=True)
    enddate = models.DateField(
        db_column='ProjTsk_EndDate', blank=True, null=True)
    status = models.CharField(
        db_column='ProjTsk_Status', max_length=1, blank=True, null=True)
    createdby = models.CharField(
        db_column='ProjTsk_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjTsk_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjTsk_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjTsk_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='ProjTsk_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ProjTsk_Client_ID')

    @staticmethod
    def nextID():
        currentModelObj = Projecttask
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
        db_table = 'ProjectTask'
        unique_together = (('company', 'projstg_key', 'id'),)


class ProjectElevationDiagrams(models.Model):
    key = models.AutoField(primary_key=True, db_column="ProjElev_Key")
    image_url = models.TextField(db_column="ProjElev_ImgURL")
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="ProjElev_Client_ID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column="ProjElev_Company_ID")
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE,
                                   related_name='elevation_diagrams', db_column="ProjElev_Proj_Key")
    block_id = models.ForeignKey(Projectblock, on_delete=models.CASCADE,
                                 related_name='elevation_diagrams', db_column="ProjElev_Blk_Key")

    class Meta:
        managed = True
        db_table = 'ProjElevationDiagrams'


class Project3DFloorPlanHdr(models.Model):
    key = models.AutoField(primary_key=True, db_column="Proj3DFloorHdr_Key")
    IMAGE_TYPE_CHOICES = [('3D', '3D'), ('FloorPlan', 'FloorPlan')]
    image_type = models.CharField(db_column="Proj3DFloorHdr_ImageType",
                                  max_length=10, choices=IMAGE_TYPE_CHOICES)
    image_name = models.CharField(
        db_column="Proj3DFloorHdr_ImgName", max_length=255, blank=True, null=True)
    image_url = models.TextField(db_column="Proj3DFloorHdr_ImgURL")
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="Proj3DFloorHdr_Client_ID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column="Proj3DFloorHdr_Company_ID")
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE,
                                   related_name='floor_plan_headers', db_column="Proj3DFloorHdr_Proj_Key")
    block_id = models.ForeignKey(Projectblock, on_delete=models.CASCADE,
                                 related_name='floor_plan_headers', db_column="Proj3DFloorHdr_Blk_Key")

    class Meta:
        managed = True
        db_table = 'Project3DFloorPlanHdr'


class Project3DFloorPlanDtl(models.Model):
    key = models.AutoField(primary_key=True, db_column="Proj3DFloorDtl_Key")
    hdr_key = models.ForeignKey(Project3DFloorPlanHdr, on_delete=models.CASCADE,
                                related_name='details', db_column="Proj3DFloorDtl_Hdr_Key")
    floor_id = models.ForeignKey(Projectfloor, on_delete=models.CASCADE,
                                 related_name='floor_plan_details', db_column="Proj3DFloorDtl_Flr_Key")

    class Meta:
        managed = True
        db_table = 'Project3DFloorPlanDtl'
        unique_together = ('hdr_key', 'floor_id')


class ExpenseType(models.Model):
    key = models.AutoField(
        db_column='ExpenseType_Key', primary_key=True)
    descr = models.CharField(
        db_column='ExpenseType_Descr', max_length=100)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ExpenseType_Client_ID')

    class Meta:
        managed = True
        db_table = 'ExpenseType'


class ExpenseVendor(models.Model):
    key = models.AutoField(
        db_column='ExpenseVendor_Key', primary_key=True)
    name = models.CharField(
        db_column='ExpenseVendor_Name', max_length=100)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ExpenseVendor_Client_ID')

    class Meta:
        managed = True
        db_table = 'ExpenseVendor'


class PaidExpenses(models.Model):
    key = models.AutoField(primary_key=True, db_column='PaidExpenses_Key')
    project_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='PaidExpenses_ProjectKey', null=True, blank=True)
    date = models.DateField(db_column='PaidExpenses_Date')
    amount = models.DecimalField(
        db_column='PaidExpenses_Amount', max_digits=10, decimal_places=2)
    expense_type = models.ForeignKey(
        ExpenseType, on_delete=models.CASCADE, db_column='PaidExpenses_ExpenseType')
    account_id = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, db_column='PaidExpenses_AccountID', null=True, blank=True)
    exp_vendor_id = models.ForeignKey(
        ExpenseVendor, on_delete=models.CASCADE, db_column='PaidExpenses_ExpenseVendorID', null=True, blank=True)
    notes = models.CharField(
        max_length=255, db_column='PaidExpenses_Notes', null=True, blank=True)
    payment_mode = models.ForeignKey(
        'pricing.Modeofpay', on_delete=models.CASCADE, db_column='PaidExpenses_PaymentModeKey')
    payment_desc = models.CharField(
        max_length=255, db_column='PaidExpenses_Payment_Desc', null=True, blank=True)
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='PaidExpenses_CompanyID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='PaidExpenses_ClientID')

    class Meta:
        db_table = 'PaidExpenses'


class ProjectSchedule(models.Model):
    key = models.AutoField(db_column='ProjectSchedule_Key', primary_key=True)
    name = models.CharField(
        db_column='ProjectSchedule_Name', max_length=100, blank=True, null=True)
    DURATION_TYPE_CHOICES = [('D', 'Days'), ('W', 'Weeks'), ('M', 'Months')]
    duration_type = models.CharField(
        max_length=1, db_column='ProjectSchedule_DurationTyp', choices=DURATION_TYPE_CHOICES)
    duration = models.IntegerField(db_column='ProjectSchedule_Duration')
    createdby = models.CharField(
        db_column='ProjectSchedule_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ProjectSchedule_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='ProjectSchedule_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='ProjectSchedule_LastModifiedDtTm', blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ProjectSchedule_Client_ID')
    projtyp_key = models.ForeignKey(
        Projecttype, on_delete=models.CASCADE, db_column='ProjectSchedule_ProjTyp_Key')

    class Meta:
        managed = True
        db_table = 'ProjectSchedule'
