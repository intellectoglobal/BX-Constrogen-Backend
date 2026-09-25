from rest_framework import serializers
from .models import (Amenity, Projecttype, Projectstatus,
                     Project, Projcostcode, Projectamenity,
                     Projectblock, Projectfloor, ProjectUnitStatus, Projectunit, Projectstage,
                     Projpayterms, Projpricehistory, Projstatushistory,
                     Projecttask, ProjectWork, ProjectElevationDiagrams, Project3DFloorPlanHdr, Project3DFloorPlanDtl, PaidExpenses, ExpenseType, ExpenseVendor, ProjectSchedule)
from users.models import AppUser
from datetime import datetime
from geolocation.serializers import StateSerializer, CitySerializer
from geolocation.models import State, City
from buildiq.super_serializer import DynamicFieldsModelSerializer


class ProjectStatusSerializer(DynamicFieldsModelSerializer):
    descr = serializers.CharField(required=True)

    class Meta:
        model = Projectstatus
        fields = '__all__'


class ProjectTypeSerializer(DynamicFieldsModelSerializer):
    descr = serializers.CharField(required=True)
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Projecttype
        fields = '__all__'


class ProjectSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    state = StateSerializer(source='state_key', read_only=True)
    city = CitySerializer(source='city_key',
                          read_only=True, fields=('key', 'name'))
    status = ProjectStatusSerializer(source='projstatus_key',
                                     read_only=True, fields=('key', 'descr'))
    pro_type = ProjectTypeSerializer(source='projtyp_key',
                                     read_only=True, fields=('key', 'id', 'descr'))
    
    latest_proj_status = serializers.SerializerMethodField(read_only=True)
    latest_proj_price = serializers.SerializerMethodField(read_only=True)
    no_of_blocks = serializers.SerializerMethodField(read_only=True)
    no_of_units = serializers.SerializerMethodField(read_only=True)
    no_of_floors = serializers.SerializerMethodField(read_only=True)

    def get_latest_proj_status(self, project):
        if Projstatushistory.objects.filter(proj_key=project).exists():
            proStsHis = Projstatushistory.objects.filter(
                proj_key=project).latest("createddttm")
            return ProjStatusHistorySerializer(proStsHis).data['proj_status']
        return {}

    def get_latest_proj_price(self, project):
        if Projpricehistory.objects.filter(proj_key=project).exists():
            proStsHis = Projpricehistory.objects.filter(
                proj_key=project).latest("createddttm")
            return {"effprice": ProjPriceHistorySerializer(proStsHis).data["effprice"]}
        return {}
    
    def get_no_of_blocks(self, project):
        """Count blocks from Projectblock table"""
        return Projectblock.objects.filter(proj_key=project).count()
    
    def get_no_of_units(self, project):
        """Sum of units from Projectfloor table through blocks"""
        blocks = Projectblock.objects.filter(proj_key=project)
        total_units = 0
        for block in blocks:
            floors = Projectfloor.objects.filter(projblk_key=block.key)
            total_units += sum(int(f.no_of_units or 0) for f in floors)
        return total_units
    
    def get_no_of_floors(self, project):
        """Sum of floors from Projectblock table"""
        blocks = Projectblock.objects.filter(proj_key=project)
        total_floors = 0
        for block in blocks:
            abv = block.floor_count_abv_ground or 0
            blw = block.floor_count_blw_ground or 0
            total_floors += abv + blw
        return total_floors

    class Meta:
        model = Project
        fields = '__all__'


class AmenitySerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Amenity
        fields = '__all__'


class ProjectAmenitySerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Projectamenity
        fields = '__all__'


class ProjCostCodeSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Projcostcode
        fields = '__all__'


class ProjectBlockSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    floor_count = serializers.SerializerMethodField(read_only=True)
    unit_count = serializers.SerializerMethodField(read_only=True)

    def get_floor_count(self, obj):
        floor_count_abv_ground = obj.floor_count_abv_ground if obj.floor_count_abv_ground else 0
        floor_count_blw_ground = obj.floor_count_blw_ground if obj.floor_count_blw_ground else 0
        return floor_count_abv_ground + floor_count_blw_ground
    
    def get_unit_count(self, obj):
        """Get unit count from Projectfloor table"""
        floors = Projectfloor.objects.filter(projblk_key=obj.key)
        return sum(int(f.no_of_units or 0) for f in floors)
    
    class Meta:
        model = Projectblock
        fields = '__all__'


class ProjectFloorSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    block = ProjectBlockSerializer(source='projblk_key',
                                   read_only=True, fields=('key', 'id', 'descr', 'proj_key'))

    class Meta:
        model = Projectfloor
        fields = '__all__'

class ProjectUnitStatusSerializer(DynamicFieldsModelSerializer):
    descr = serializers.CharField(required=True)

    class Meta:
        model = ProjectUnitStatus
        fields = '__all__'


class ProjectUnitSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    block = ProjectBlockSerializer(source='projblk_key',
                                   read_only=True, fields=('key', 'id', 'descr', 'proj_key'))
    floor = ProjectFloorSerializer(source='projflr_key',
                                   read_only=True, fields=('key', 'id', 'descr', 'projblk_key'))
    status = ProjectUnitStatusSerializer(source='projunit_status_key',
                                         read_only=True, fields=('key', 'id', 'descr'))

    class Meta:
        model = Projectunit
        fields = '__all__'


class ProjectWorkSerializer(DynamicFieldsModelSerializer):
    project = ProjectSerializer(
        source='proj_key', read_only=True, fields=('key', 'id', 'name',))

    class Meta:
        model = ProjectWork
        fields = '__all__'


class ProjectStageSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    work = ProjectWorkSerializer(
        source="projwrk_key",
        read_only=True,
        fields=('key', 'id', 'descr', 'project',)
    )

    class Meta:
        model = Projectstage
        fields = '__all__'


class ProjPayTermsSerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = Projpayterms
        fields = '__all__'


class ProjPriceHistorySerializer(serializers.ModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    project = ProjectSerializer(
        source='proj_key', read_only=True, fields=('sqftprice',))

    class Meta:
        model = Projpricehistory
        fields = '__all__'


class ProjStatusHistorySerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    proj_status = ProjectStatusSerializer(source='projstatus_key',
                                          read_only=True, fields=('key', 'descr'))
    project = ProjectSerializer(
        source='proj_key', read_only=True, fields=('sqftprice',))

    class Meta:
        model = Projstatushistory
        fields = '__all__'


class ProjectTaskSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    project = ProjectSerializer(
        source='proj_key',
        read_only=True,
        fields=('sqftprice',)
    )
    stage = ProjectStageSerializer(
        source='projstg_key',
        read_only=True,
        fields=('key', 'id', 'descr', 'projwrk_key', 'work',)
    )

    class Meta:
        model = Projecttask
        fields = '__all__'


class ProjectElevationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ProjectElevationDiagrams
        fields = '__all__'


class Project3DFloorPlanHdrSerializer(DynamicFieldsModelSerializer):
    floors = serializers.SerializerMethodField()

    def get_floors(self, obj):
        floor_ids = list(
            Project3DFloorPlanDtl.objects.filter(hdr_key = obj.key).values_list('floor_id', flat=True)
        )
        floors = []
        for floor_id in floor_ids:
            floor_objs = Projectfloor.objects.filter(key=floor_id)
            serializer = ProjectFloorSerializer(floor_objs, many=True, fields=['key','descr'])
            floors.append(serializer.data)

        return floors 
    class Meta:
        model = Project3DFloorPlanHdr
        fields = '__all__'


class Project3DFloorPlanDtlSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = Project3DFloorPlanDtl
        fields = '__all__'


class ExpenseTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpenseType
        fields = '__all__'


class ExpenseVendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpenseVendor
        fields = '__all__'


class PaidExpensesSerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        format='%d-%m-%Y',
        input_formats=['%Y-%m-%d'],
    )
    payment_mode_descr = serializers.SerializerMethodField(read_only=True)
    expense_type_descr = serializers.SerializerMethodField(read_only=True)
    project_name = serializers.CharField(read_only=True, source="project_key.name")
    # expense_vendor_descr = serializers.CharField(read_only=True, source="exp_vendor_id.name")

    def get_payment_mode_descr(self, obj):
        return obj.payment_mode.descr

    def get_expense_type_descr(self, obj):
        return obj.expense_type.descr

    class Meta:
        model = PaidExpenses
        fields = '__all__'


class ProjectScheduleSerializer(serializers.ModelSerializer):

    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    projtyp = ProjectTypeSerializer(
        source='projtyp_key', read_only=True, fields=('key', 'descr',))

    class Meta:
        model = ProjectSchedule
        fields = '__all__'