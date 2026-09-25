from django.urls import path
from .views import (ProjectStatusViewset, ProjectTypeViewset,
                    ProjectViewset, AmenityViewset, ProjectAmenityViewset, ProjCostCodeViewset,
                    ProjectBlockViewset, ProjectFloorGenerationView, ProjectFloorViewset, ProjectUnitGenerationView, ProjectUnitViewset, ProjectStageViewset,
                    ProjectAvailabilityViewset, ProjectAvailabilityCategoryViewset,
                    ProjectPayTermViewset, ProjectPriceHistoryViewset, ProjStatusHistoryViewset,
                    ProjectAllViewset, ProjectWorkViewset, ProjectBulkTaskViewset, ProjectBulkEditTaskViewset, ProjectTaskViewset,
                    ProjectTaskReverseViewset, NonTaskProjectViewset, ProjectAvailableUnitViewset, ProjectElevationViewSet, Project3DFloorPlansViewSet, PaidExpensesViewset, ExpenseTypeViewset, ProjectUnitStatusViewset, ExpenseVendorViewset,
                    ProjectScheduleViewset)
from buildiq.utils import ENDPOINT_METHODS_DICT
app_name = 'project'


GET = ENDPOINT_METHODS_DICT['GET']
GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
POST = ENDPOINT_METHODS_DICT['POST']
RETRIVE = ENDPOINT_METHODS_DICT['RETRIVE']
DELETE = ENDPOINT_METHODS_DICT['DELETE']
RETRIVE_UPDATE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']

urlpatterns = [
    path('status/',
         ProjectStatusViewset.as_view(GET_POST), name="statuses"),
    path('status/<int:pk>',
         ProjectStatusViewset.as_view(RETRIVE_UPDATE_DELETE), name="status"),

    path('type/',
         ProjectTypeViewset.as_view(GET_POST), name="types"),
    path('type/<int:pk>',
         ProjectTypeViewset.as_view(RETRIVE_UPDATE_DELETE), name="types"),

    path('project/all/active',
         ProjectAllViewset.as_view(GET), name="projectsall"),
    path('project/',
         ProjectViewset.as_view(GET_POST), name="projects"),
    path('project/<int:pk>',
         ProjectViewset.as_view(RETRIVE_UPDATE_DELETE), name="project"),

    path('elevation/',
         ProjectElevationViewSet.as_view(GET_POST), name="elevation"),
    path('elevation/<int:pk>',
         ProjectElevationViewSet.as_view(RETRIVE), name="elevation"),
    path('elevation/<int:pk>',
         ProjectElevationViewSet.as_view(DELETE), name="elevation"),
    
    path('3d_floor/',
         Project3DFloorPlansViewSet.as_view(GET_POST), name="3d_floor"),
    path('3d_floor/<int:pk>',
         Project3DFloorPlansViewSet.as_view(RETRIVE_UPDATE_DELETE), name="3d_floor"),

    path('amenity/',
         AmenityViewset.as_view(GET_POST), name="amenities"),
    path('amenity/<int:pk>',
         AmenityViewset.as_view(RETRIVE_UPDATE), name="amenity"),

    path('project_amenity/',
         ProjectAmenityViewset.as_view(GET_POST), name="projectamenities"),
    path('project_amenity/<int:pk>',
         ProjectAmenityViewset.as_view(RETRIVE_UPDATE), name="projectamenity"),

    path('project_cost_code/',
         ProjCostCodeViewset.as_view(GET_POST), name="projectcostcodes"),
    path('project_cost_code/<int:pk>',
         ProjCostCodeViewset.as_view(RETRIVE_UPDATE), name="projectcostcode"),

    path('project_cost_code/',
         ProjCostCodeViewset.as_view(GET_POST), name="projectcostcodes"),
    path('project_cost_code/<int:pk>',
         ProjCostCodeViewset.as_view(RETRIVE_UPDATE), name="projectcostcode"),

    path('block/',
         ProjectBlockViewset.as_view(GET_POST), name="projectblocks"),
    path('block/<int:pk>',
         ProjectBlockViewset.as_view(RETRIVE_UPDATE_DELETE), name="projectblock"),

    path('floor/generate/', ProjectFloorGenerationView.as_view(), name='generate_projectfloors'),
    
    path('floor/',
         ProjectFloorViewset.as_view(GET_POST), name="projectfloors"),
    path('floor/<int:pk>',
         ProjectFloorViewset.as_view(RETRIVE_UPDATE_DELETE), name="projectfloor"),

    path('unit/generate/', ProjectUnitGenerationView.as_view(), name='generate_projectunits'),

    path('unit/status/',
         ProjectUnitStatusViewset.as_view(GET_POST), name="projectunits_status"),
    path('unit/status/<int:pk>',
         ProjectUnitStatusViewset.as_view(RETRIVE_UPDATE_DELETE), name="projectunit_status"),

    path('unit/',
         ProjectUnitViewset.as_view(GET_POST), name="projectunits"),
    path('unit/<int:pk>',
         ProjectUnitViewset.as_view(RETRIVE_UPDATE_DELETE), name="projectunit"),

    path('stage/',
         ProjectStageViewset.as_view(GET_POST), name="projectstages"),
    path('stage/<int:pk>',
         ProjectStageViewset.as_view(RETRIVE_UPDATE_DELETE), name="projectstage"),

    path('status_available/',
         ProjectAvailabilityCategoryViewset.as_view(GET), name="status_available"),
    path('availability/<int:pk>',
         ProjectAvailabilityViewset.as_view(RETRIVE), name="availability"),

    path('payterm/',
         ProjectPayTermViewset.as_view(GET_POST), name="payterms"),
    path('payterm/<int:pk>',
         ProjectPayTermViewset.as_view(RETRIVE_UPDATE_DELETE), name="payterm"),

    path('history/price/',
         ProjectPriceHistoryViewset.as_view(GET_POST), name="pricehistorys"),
    path('history/price/<int:pk>',
         ProjectPriceHistoryViewset.as_view(RETRIVE_UPDATE_DELETE), name="pricehistory"),

    path('history/status/',
         ProjStatusHistoryViewset.as_view(GET_POST), name="pricehistorys"),
    path('history/status/<int:pk>',
         ProjStatusHistoryViewset.as_view(RETRIVE_UPDATE_DELETE), name="pricehistory"),

    path('task/bulk/',
         ProjectBulkTaskViewset.as_view(GET_POST), name="tasks"),
    path('task/bulk/<int:pk>',
         ProjectBulkTaskViewset.as_view(RETRIVE_UPDATE_DELETE), name="task"),


    path('task/bulk/edit/',
         ProjectBulkEditTaskViewset.as_view(POST), name="tasks"),

    path('task/',
         ProjectTaskViewset.as_view(GET_POST), name="tasks"),
    path('task/<int:pk>',
         ProjectTaskViewset.as_view(RETRIVE_UPDATE_DELETE), name="task"),

    path('task/reverse/',
         ProjectTaskReverseViewset.as_view(GET), name="tasks_reverse"),
    #     path('task/reverse/<int:pk>',
    #          ProjectTaskViewset.as_view(RETRIVE), name="task"),

    path('non/task/projects',
         NonTaskProjectViewset.as_view(GET), name="projectsnontasks"),

    path('work/',
         ProjectWorkViewset.as_view(GET_POST), name="works"),
    path('work/<int:pk>',
         ProjectWorkViewset.as_view(RETRIVE_UPDATE_DELETE), name="work"),


    path('units/available/',
         ProjectAvailableUnitViewset.as_view(GET), name="availableunits"),

    path('expense/type/',
         ExpenseTypeViewset.as_view(GET_POST), name="expense_type"),
    path('expense/type/<str:pk>',
         ExpenseTypeViewset.as_view(RETRIVE_UPDATE_DELETE), name="expense_type"),

    path('expense_vendor/',
         ExpenseVendorViewset.as_view(GET_POST), name="expense_vendor"),
    path('expense_vendor/<str:pk>',
         ExpenseVendorViewset.as_view(RETRIVE_UPDATE_DELETE), name="expense_vendor"),

    path('expense/',
         PaidExpensesViewset.as_view(GET_POST), name="paid_expense"),
    path('expense/<str:pk>',
         PaidExpensesViewset.as_view(RETRIVE_UPDATE_DELETE), name="paid_expense"),

    path('schedule/',
         ProjectScheduleViewset.as_view(GET_POST), name="schedule"),
    path('schedule/<int:pk>',
         ProjectScheduleViewset.as_view(RETRIVE_UPDATE_DELETE), name="schedule"),

]
