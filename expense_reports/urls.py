from django.urls import path
from .views import MaterialExpenseApiViewSet, ContractExpenseApiViewSet, ExtraExpenseApiViewSet, SalaryExpenseApiViewSet, OverallExpenseApiViewSet, StockListApiViewSet

app_name = "expense_reports"

urlpatterns = [
    path('material-expenses/', MaterialExpenseApiViewSet.as_view(),
         name='material-expense-list'),
    path('contract-expenses/', ContractExpenseApiViewSet.as_view(),
         name='contract-expense-list'),
    path('extra-expenses/', ExtraExpenseApiViewSet.as_view(),
         name='extra-expense-list'),
    path('salary-expenses/', SalaryExpenseApiViewSet.as_view(),
         name='salary-expense-list'),
    path('overall-expenses/', OverallExpenseApiViewSet.as_view(),
         name='overall-expense-list'),
    path('stock-report/', StockListApiViewSet.as_view(), name='stock-report-list'),
]
