from rest_framework import serializers
from buildiq.super_serializer import DynamicFieldsModelSerializer
from .models import DailyWorkProgressHdr, DailyWorkProgressDtl, DailyWorkProgressImage


class DailyWorkProgressImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyWorkProgressImage
        fields = [
            'key',
            'dtl_key',
            'image_url',
            'caption',
            'created_at',
            'created_by',
            'client_id'
        ]


class DailyWorkProgressDtlSerializer(serializers.ModelSerializer):
    images = DailyWorkProgressImageSerializer(many=True, read_only=True)

    class Meta:
        model = DailyWorkProgressDtl
        fields = [
            'key',
            'descr',
            'comments',
            'status',
            'hdr_key',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'client_id',
            'images'
        ]


class DailyWorkProgressHdrSerializer(DynamicFieldsModelSerializer):
    details = DailyWorkProgressDtlSerializer(many=True, read_only=True)


    project_name = serializers.CharField(
        source='project_key.name', read_only=True)
    blk_name = serializers.CharField(
        source='blk_key.descr', read_only=True)
    floor_name = serializers.CharField(
        source='floor_key.descr', read_only=True)
    unit_name = serializers.CharField(
        source='unit_key.descr', read_only=True)
    work_ctgry_name = serializers.CharField(
        source='workctgry_key.descr', read_only=True)
    schedule_name = serializers.CharField(
        source='schedule_key.name', read_only=True)
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = DailyWorkProgressHdr
        fields = [
            'key',
            'workctgry_key',
            'work_ctgry_name',
            'project_key',
            'project_name',
            'blk_key',
            'blk_name',
            'floor_key',
            'floor_name',
            'unit_key',
            'unit_name',
            'schedule_key',
            'schedule_name',
            'status',
            'status_label',
            'date',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'company_id',
            'client_id',
            'details'
        ]

    def get_status_label(self, obj):
        return dict(obj.STATUS_CHOICES).get(obj.status, obj.status)
