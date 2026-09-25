from rest_framework import serializers
from .models import WorkCategory, WorkType, WorkActivity, JobList, MaterialPack


class WorkCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCategory
        fields = '__all__'


class WorkTypeSerializer(serializers.ModelSerializer):
    work_category = WorkCategorySerializer(
        source='category_key', read_only=True)

    class Meta:
        model = WorkType
        fields = '__all__'


class WorkActivitySerializer(serializers.ModelSerializer):
    work_category = WorkCategorySerializer(
        source='category_key', read_only=True)
    work_type = WorkCategorySerializer(
        source='type_key', read_only=True)

    class Meta:
        model = WorkActivity
        fields = '__all__'
