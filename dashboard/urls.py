from django.urls import path
from .views import DashboardSummary

urlpatterns = [
    path("", DashboardSummary.as_view(), name="dashboard"),
]