from django.urls import path
from .views import (PurposeViewset, WarehouseViewset,
                    ItemTypeViewset, ItemUomViewset, ItemViewset,
                    UomTypeViewset, ItemGroupViewset,
                    ItemGroupDetailViewset, ItemSubTypeViewset, BrandViewset, ItemRateViewSet,
                    ItemModelViewSet)
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'invntory'

GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']

urlpatterns = [
    path('purpose/',
         PurposeViewset.as_view(GET_POST), name="purpose"),
    path('purpose/<int:pk>',
         PurposeViewset.as_view(RETRIVE_UPDATE_DELETE), name="purpose"),


    path('warehouse/',
         WarehouseViewset.as_view(GET_POST), name="warehouses"),
    path('warehouse/<int:pk>',
         WarehouseViewset.as_view(RETRIVE_UPDATE_DELETE), name="warehouse"),


    path('item_type/',
         ItemTypeViewset.as_view(GET_POST), name="item_types"),
    path('item_type/<int:pk>',
         ItemTypeViewset.as_view(RETRIVE_UPDATE_DELETE), name="item_type"),

    path('item_subtype/',
         ItemSubTypeViewset.as_view(GET_POST), name="item_subtypes"),
    path('item_subtype/<int:pk>',
         ItemSubTypeViewset.as_view(RETRIVE_UPDATE_DELETE), name="item_subtype"),

    path('item_uom/',
         ItemUomViewset.as_view(GET_POST), name="item_uoms"),
    path('item_uom/<int:pk>',
         ItemUomViewset.as_view(RETRIVE_UPDATE_DELETE), name="item_uom"),

    path('item/',
         ItemViewset.as_view(GET_POST), name="items"),
    path('item/<int:pk>',
         ItemViewset.as_view(RETRIVE_UPDATE_DELETE), name="item"),

    path('item/rate/',
         ItemRateViewSet.as_view(), name="itemrate"),

    path('uom/type/',
         UomTypeViewset.as_view(GET_POST), name="uomtypes"),
    path('uom/type/<int:pk>',
         UomTypeViewset.as_view(RETRIVE_UPDATE_DELETE), name="uomtype"),

    path('item/group/',
         ItemGroupViewset.as_view(GET_POST), name="itemgrp"),
    path('item/group/<int:pk>',
         ItemGroupViewset.as_view(RETRIVE_UPDATE_DELETE), name="itemgrps"),

    path('item/group/detail',
         ItemGroupDetailViewset.as_view(GET_POST), name="itemgrpdetails"),
    path('item/group/detail/<int:pk>',
         ItemGroupDetailViewset.as_view(RETRIVE_UPDATE_DELETE), name="itemgrpdetail"),

    path('brand/',
         BrandViewset.as_view(GET_POST), name="brand"),
    path('brand/<int:pk>',
         BrandViewset.as_view(RETRIVE_UPDATE_DELETE), name="brand"),

    path('item/models/',
         ItemModelViewSet.as_view(), name="item_models"),
]
