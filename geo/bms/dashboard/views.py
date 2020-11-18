from django.shortcuts import render
from django.views import View

from .models import TradingName
from job.views import job_list, JobCreateView, JobUpdateView

def index(request):
    """Load the index page of the dashboard"""
    name = TradingName.objects.all().latest()
    context = {'name': name,}
    return(render(request, 'dashboard/index.html', context))
