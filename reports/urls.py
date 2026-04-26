from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_list, name="report_list"),
    path("my-reports/", views.my_reports, name="my_reports"),
    path("stats/", views.stats, name="stats"),

    # Create reports
    path("lost/new/", views.LostReportCreateView.as_view(), name="lost_create"),
    path("found/new/", views.FoundReportCreateView.as_view(), name="found_create"),
    
    # Detail/Edit/Delete
    path("<int:pk>/", views.ReportDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ReportUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ReportDeleteView.as_view(), name="delete"),
    
    # Mark as recovered
    path("<int:pk>/recover/", views.mark_recovered_view, name="recover"),
]
