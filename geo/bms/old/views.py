from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Job

def job_list(request):
    jobs = Job.objects.all()
    return render(request, 'old/job/list.html', {'jobs': jobs})
        
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'old/job/detail.html', {'job': job})