from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    # Create reports
    path("lost/new/", views.LostReportCreateView.as_view(), name="lost_create"),
    path("found/new/", views.FoundReportCreateView.as_view(), name="found_create"),
    
    # Detail/Edit/Delete (these will be handled by Person 3 later, but we need the URL)
    path("<int:pk>/", views.ReportDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ReportUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ReportDeleteView.as_view(), name="delete"),
    
    # Mark as recovered
    path("<int:pk>/recover/", views.mark_recovered_view, name="recover"),
]
