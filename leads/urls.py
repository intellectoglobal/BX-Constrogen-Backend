from django.urls import path
from .views import (LeadDashboardViewset, LeadProjectAllViewset, LeadStatusViewset, LeadSourceCategoryViewset, LeadViewset, VisitStatusViewset,LeadSourceViewset,BudgetRangesViewset,ProjectInterestsViewset,FloorsViewset,FacingViewset,FollowUpStagesViewset,OccupanciesViewset,OccupancySubTypesViewset,LocationPreferenceViewset,
                    VisitViewset, FollowUpStatusViewset, FollowUpViewset, LeadRelatedDataViewSet, CommentsViewSet, PropertiesViewset, ExportReportViewset, FeedBackViewset, FeedBackDetailsViewset, JunkLeadsViewset, Contact1AvailabilityViewSet)
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'leads'

GET = ENDPOINT_METHODS_DICT['GET']
GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']
comments_view = CommentsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
})

urlpatterns = [
    
    path('dashboard/',
         LeadDashboardViewset.as_view(GET), name="dashboard"),

    path('status/',
         LeadStatusViewset.as_view(GET_POST), name="statuses"),
    path('status/<int:pk>',
         LeadStatusViewset.as_view(RETRIVE_UPDATE_DELETE), name="status"),
    path('leads/',
         LeadViewset.as_view(GET_POST), name="leads"),
    path('leads/<int:pk>',
         LeadViewset.as_view(RETRIVE_UPDATE_DELETE), name="lead"),

    path('contact1-exists/',
         Contact1AvailabilityViewSet.as_view(GET), name="contact1-exists"),
  
     path('project/all/active',
         LeadProjectAllViewset.as_view(GET), name="projectsall-active"),

    path('leadsourcecategory/',
         LeadSourceCategoryViewset.as_view(GET_POST), name="leadsourcecategory"),
    path('leadsourcecategory/<int:pk>',
         LeadSourceCategoryViewset.as_view(RETRIVE_UPDATE_DELETE), name="leadsourcecategory"),

    path('leadsource/',
         LeadSourceViewset.as_view(GET_POST), name="leadsource"),
    path('leadsource/<int:pk>',
         LeadSourceViewset.as_view(RETRIVE_UPDATE_DELETE), name="leadsource"),

    path('budgetsrange/',
         BudgetRangesViewset.as_view(GET_POST), name="budgetsrange"),
    path('budgetsrange/<int:pk>',
         BudgetRangesViewset.as_view(RETRIVE_UPDATE_DELETE), name="budgetsrange"),

    path('propertyinterests/',
         ProjectInterestsViewset.as_view(GET_POST), name="propertyinterests"),
    path('propertyinterests/<int:pk>',
         ProjectInterestsViewset.as_view(RETRIVE_UPDATE_DELETE), name="propertyinterests"),

    path('floors/',
         FloorsViewset.as_view(GET_POST), name="floors"),
    path('floors/<int:pk>',
         FloorsViewset.as_view(RETRIVE_UPDATE_DELETE), name="floors"),

    path('facings/',
         FacingViewset.as_view(GET_POST), name="facings"),
    path('facings/<int:pk>',
         FacingViewset.as_view(RETRIVE_UPDATE_DELETE), name="facings"),

    path('followupstages/',
         FollowUpStagesViewset.as_view(GET_POST), name="followupstages"),
    path('followupstages/<int:pk>',
         FollowUpStagesViewset.as_view(RETRIVE_UPDATE_DELETE), name="followupstages"),

    path('occupancies/',
         OccupanciesViewset.as_view(GET_POST), name="occupancies"),
    path('occupancies/<int:pk>',
         OccupanciesViewset.as_view(RETRIVE_UPDATE_DELETE), name="occupancies"),

    path('occupancysubtypes/',
         OccupancySubTypesViewset.as_view(GET_POST), name="occupancysubtypes"),
    path('occupancysubtypes/<int:pk>',
         OccupancySubTypesViewset.as_view(RETRIVE_UPDATE_DELETE), name="occupancysubtypes"),

    path('locations/',
         LocationPreferenceViewset.as_view(GET_POST), name="locations"),
    path('locations/<int:pk>',
         LocationPreferenceViewset.as_view(RETRIVE_UPDATE_DELETE), name="locations"), 
 
    path('visit/status/',
         VisitStatusViewset.as_view(GET_POST), name="visit-statuses"),
    path('visit/status/<int:pk>',
         VisitStatusViewset.as_view(RETRIVE_UPDATE_DELETE), name="visit-status"),
    path('visit/',
         VisitViewset.as_view(GET_POST), name="visits"),
    path('visit/<int:pk>',
         VisitViewset.as_view(RETRIVE_UPDATE_DELETE), name="visit"),

    path('follow-up/status/',
         FollowUpStatusViewset.as_view(GET_POST), name="follow-up-statuses"),
    path('follow-up/status/<int:pk>',
         FollowUpStatusViewset.as_view(RETRIVE_UPDATE_DELETE), name="follow-up-status"),
    path('follow-up/',
         FollowUpViewset.as_view(GET_POST), name="follow-up"),
    path('follow-up/<int:pk>',
         FollowUpViewset.as_view(RETRIVE_UPDATE_DELETE), name="follow-up"),

    path('leads-related/',
         LeadRelatedDataViewSet.as_view(GET_POST), name="leads-related"),
    path('leads-related/<int:pk>',
         LeadRelatedDataViewSet.as_view(RETRIVE_UPDATE_DELETE), name="leads-related"),

    path('lead/comments/<int:pk>', comments_view),
    path('follow-up/comments/<int:pk>', comments_view),
    path('visit/comments/<int:pk>', comments_view),

    path('properties/',PropertiesViewset.as_view(GET), name="properties"),

    path('export_report/',ExportReportViewset.as_view(GET), name="export-report"),

    path('feedback/',
         FeedBackViewset.as_view(GET_POST), name="feedback"),
    path('feedback/<int:pk>',
         FeedBackViewset.as_view(RETRIVE_UPDATE_DELETE), name="feedback"),

    path('feedback-details/',
         FeedBackDetailsViewset.as_view(GET_POST), name="feedback-details"),
    path('feedback-details/<int:pk>',
         FeedBackDetailsViewset.as_view(RETRIVE_UPDATE_DELETE), name="feedback-details"),

    path('junk-leads/',
         JunkLeadsViewset.as_view(GET), name="junk-leads"),
    path('junk-leads/<int:pk>',
         JunkLeadsViewset.as_view(RETRIVE_UPDATE), name="junk-lead"),
]
