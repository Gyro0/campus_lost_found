from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_list_placeholder, name="report_list"),
    path("lost/new/", views.lost_create_placeholder, name="lost_create"),
    path("found/new/", views.found_create_placeholder, name="found_create"),
    path("mine/", views.my_reports_placeholder, name="my_reports"),
]