from django.urls import path
from buildiq.utils import ENDPOINT_METHODS_DICT
from .views import WorkCategoryViewset, WorkTypeViewset, WorkActivityViewset

app_name = 'estimate'

GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']


urlpatterns = [
    path('category/', WorkCategoryViewset.as_view(GET_POST), name='work_category'),
    path('category/<int:pk>',
         WorkCategoryViewset.as_view(RETRIVE_UPDATE_DELETE), name='work_category'),
    path('type/', WorkTypeViewset.as_view(GET_POST), name='work_type'),
    path('type/<int:pk>', WorkTypeViewset.as_view(RETRIVE_UPDATE_DELETE),
         name='work_type'),
    path('activity/', WorkActivityViewset.as_view(GET_POST), name='work_activity'),
    path('activity/<int:pk>',
         WorkActivityViewset.as_view(RETRIVE_UPDATE_DELETE), name='work_activity'),
]
