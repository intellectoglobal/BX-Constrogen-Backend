from rest_framework import serializers
from .models import ContractServiceTemplateDtl, ContractServiceTemplateHdr, PaymentScheduleTemplateHdr, PaymentScheduleTemplateDtl, ItemKitTemplateHdr, ItemKitTemplateDtl, CustomerPaymentScheduleTemplateHdr, CustomerPaymentScheduleTemplateDtl
from contractor.models import ContractorType
from contractor.serializers import ContractorTypeSerializer
from inventory.models import Itemuom, Item, Itemtype, Purpose
from inventory.serializers import ItemuomSerializer, ItemSerializer, ItemtypeSerializer, PurposeSerializer


class ContractServiceTemplateDtlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractServiceTemplateDtl
        fields = '__all__'


class ContractServiceTemplateDtlGetSerializer(serializers.ModelSerializer):
    uom = serializers.SerializerMethodField()

    def get_uom(self, obj):
        uom_obj = Itemuom.objects.get(
            key=obj.uom.key)
        if uom_obj:
            serializer = ItemuomSerializer(uom_obj)
            return serializer.data['key']

    class Meta:
        model = ContractServiceTemplateDtl
        fields = '__all__'


class ContractServiceTemplateHdrSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContractServiceTemplateHdr
        fields = '__all__'


class ContractServiceTemplateHdrListSerializer(serializers.ModelSerializer):
    contract_type = serializers.SerializerMethodField()

    def get_contract_type(self, obj):
        contract_type_obj = ContractorType.objects.get(
            key=obj.contract_type_key)
        if contract_type_obj:
            serializer = ContractorTypeSerializer(contract_type_obj)
            return serializer.data['descr']

    class Meta:
        model = ContractServiceTemplateHdr
        fields = ['key', 'template_name', 'description',
                  'contract_type', 'client_id']


class ContractServiceTemplateHdrGetSerializer(serializers.ModelSerializer):
    service_template_detail = serializers.SerializerMethodField()
    contract_type_key = serializers.SerializerMethodField()

    def get_contract_type_key(self, obj):
        contract_type_obj = ContractorType.objects.get(
            key=obj.contract_type_key)
        if contract_type_obj:
            serializer = ContractorTypeSerializer(contract_type_obj)
            return serializer.data['key']

    def get_service_template_detail(self, obj):
        template_dtl = ContractServiceTemplateDtl.objects.filter(
            contractservice_template_hdr_key=obj.key)
        if template_dtl is not None:
            serializer = ContractServiceTemplateDtlGetSerializer(
                template_dtl, many=True)
            return serializer.data
        return None

    class Meta:
        model = ContractServiceTemplateHdr
        fields = ['key', 'template_name', 'description',
                  'contract_type_key', 'client_id', 'service_template_detail']


class PaymentScheduleTemplateDtlSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentScheduleTemplateDtl
        fields = '__all__'


class PaymentScheduleTemplateHdrSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentScheduleTemplateHdr
        fields = '__all__'


class PaymentScheduleTemplateHdrListSerializer(serializers.ModelSerializer):
    contract_type = serializers.SerializerMethodField()

    def get_contract_type(self, obj):
        contract_type_obj = ContractorType.objects.get(
            key=obj.contract_type_key)
        if contract_type_obj:
            serializer = ContractorTypeSerializer(contract_type_obj)
            return serializer.data['descr']

    class Meta:
        model = PaymentScheduleTemplateHdr
        fields = ['key', 'template_name',
                  'description', 'contract_type', 'clientid']


class PaymentScheduleTemplateHdrGetSerializer(serializers.ModelSerializer):
    payment_schedule_template_detail = serializers.SerializerMethodField()
    contract_type_key = serializers.SerializerMethodField()

    def get_contract_type_key(self, obj):
        contract_type_obj = ContractorType.objects.get(
            key=obj.contract_type_key)
        if contract_type_obj:
            serializer = ContractorTypeSerializer(contract_type_obj)
            return serializer.data['key']

    def get_payment_schedule_template_detail(self, obj):
        template_dtl = PaymentScheduleTemplateDtl.objects.filter(
            payment_schedule_template_hdr_key=obj.key)
        if template_dtl is not None:
            serializer = PaymentScheduleTemplateDtlSerializer(
                template_dtl, many=True)
            return serializer.data
        return None

    class Meta:
        model = PaymentScheduleTemplateHdr
        fields = ['key', 'template_name', 'description', 'contract_type_key',
                  'clientid', 'payment_schedule_template_detail']


class ItemKitTemplateDtlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemKitTemplateDtl
        fields = '__all__'


class ItemKitTemplateHdrSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemKitTemplateHdr
        fields = '__all__'


class ItemKitTemplateHdrListSerializer(serializers.ModelSerializer):
    item_type = serializers.SerializerMethodField()
    purpose = serializers.SerializerMethodField()

    def get_item_type(self, obj):
        item_type_obj = Itemtype.objects.get(
            key=obj.item_type_key.key)
        if item_type_obj:
            serializer = ItemtypeSerializer(item_type_obj)
            return serializer.data['descr']

    def get_purpose(self, obj):
        item_type_obj = Purpose.objects.get(
            key=obj.purpose_key.key)
        if item_type_obj:
            serializer = PurposeSerializer(item_type_obj)
            return serializer.data['name']

    class Meta:
        model = ItemKitTemplateHdr
        fields = ['key', 'kit_name',
                  'description', 'item_type', 'purpose', 'client_id']


class ItemKitTemplateHdrGetSerializer(serializers.ModelSerializer):
    item_kit_template_detail = serializers.SerializerMethodField()

    def get_item_kit_template_detail(self, obj):
        item_kit_dtl = ItemKitTemplateDtl.objects.filter(
            item_kit_template_hdr_key=obj.key).order_by('key')
        if item_kit_dtl is not None:
            serializer = ItemKitTemplateDtlSerializer(
                item_kit_dtl, many=True)
            return serializer.data
        return None

    class Meta:
        model = ItemKitTemplateHdr
        fields = ['key', 'kit_name', 'description', 'item_type_key',
                  'purpose_key', 'client_id', 'item_kit_template_detail']


class CustomerPaymentScheduleTemplateDtlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPaymentScheduleTemplateDtl
        fields = '__all__'


class CustomerPaymentScheduleTemplateHdrSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPaymentScheduleTemplateHdr
        fields = '__all__'


class CustomerPaymentScheduleTemplateHdrListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentScheduleTemplateHdr
        fields = ['key', 'template_name',
                  'description', 'clientid']


class CustomerPaymentScheduleTemplateHdrGetSerializer(serializers.ModelSerializer):
    payment_schedule_template_detail = serializers.SerializerMethodField()

    def get_payment_schedule_template_detail(self, obj):
        template_dtl = CustomerPaymentScheduleTemplateDtl.objects.filter(
            payment_schedule_template_hdr_key=obj.key)
        if template_dtl is not None:
            serializer = CustomerPaymentScheduleTemplateDtlSerializer(
                template_dtl, many=True)
            return serializer.data
        return None

    class Meta:
        model = CustomerPaymentScheduleTemplateHdr
        fields = ['key', 'template_name', 'description',
                  'clientid', 'payment_schedule_template_detail']
