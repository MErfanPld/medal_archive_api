from django.urls import path

from .views import (
    DashboardSummaryView,
    CountryReportView,
    ValueReportView,
    PurchaseReportView,
    PdfReportView,
)

app_name = 'reports'

urlpatterns = [
    path('summary/', DashboardSummaryView.as_view(), name='summary'),
    path('dashboard/', DashboardSummaryView.as_view(), name='dashboard'),
    path('countries/', CountryReportView.as_view(), name='countries'),
    path('value/', ValueReportView.as_view(), name='value'),
    path('purchases/', PurchaseReportView.as_view(), name='purchases'),
    path('pdf/', PdfReportView.as_view(), name='pdf'),
]
