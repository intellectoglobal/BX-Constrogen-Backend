from django.urls import path, include
# from .views import AuthenticationVIEW
app_name = 'API'

urlpatterns = [
    path('client/', include('client.urls'), name='client'),
    path('geo/', include('geolocation.urls'), name='geo'),
    path('project/', include('project.urls'), name='project'),
    path('vendor/', include('vendor.urls'), name='vendor'),
    path('inventory/', include('inventory.urls'), name='invntory'),
    path('sale/', include('sale.urls'), name='sale'),
    path('transaction/', include('pricing.urls'), name='pricing'),
    path('contract/', include('contractor.urls'), name='contract'),
    path('inquiry/', include('inquiry.urls'), name='inquiry'),
    path('tracker/', include('daily_tracker.urls'), name='tracker'),
    path('leads/', include('leads.urls'), name='leads'),
    path('templates/', include('templates.urls'), name='templates'),
    path('construction/', include('construction.urls'), name='construction'),
    path('tax/', include('tax.urls'), name='tax'),
    path('bill/', include('bill_extraction.urls'), name='bill'),
    path('reports/', include('audit_reports.urls'), name='reports'),
    path('expense/', include('expense_reports.urls'), name='expense_reports'),
    path('salary/', include('salary_and_allowance.urls'),  name='salary_and_allowance'),
    path('estimate/',include('estimate.urls'), name='estimate'),
    path('dashboard/', include('dashboard.urls'), name='dashboard')
]
