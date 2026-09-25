from rest_framework import serializers
from .models import State, City
from users.models import AppUser
from datetime import datetime
from buildiq.super_serializer import DynamicFieldsModelSerializer


class StateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)

    class Meta:
        model = State
        # fields = ('state_id', 'state_name')
        fields = '__all__'


class CitySerializer(DynamicFieldsModelSerializer):
    name = serializers.CharField(required=True)
    state = StateSerializer(source='state_key', read_only=True)
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        model = City
        fields = ('key', 'name','state', 'state_key',
                  'createdby', 'createddttm', 'lastmodifiedby', 'lastmodifieddttm', 'company', 'client_id')

    def create(self, validated_data):
        return City.objects.create(**validated_data)
