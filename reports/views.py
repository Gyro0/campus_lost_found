from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def report_list_placeholder(request):
    return HttpResponse("Reports list page coming soon.")

def lost_create_placeholder(request):
    return HttpResponse("Lost report form coming soon.")

def found_create_placeholder(request):
    return HttpResponse("Found report form coming soon.")

def my_reports_placeholder(request):
    return HttpResponse("My reports page coming soon.")
