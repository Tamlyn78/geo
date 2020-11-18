from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from .models import Job, Title, Status
from .forms import JobForm, TitleForm, StatusForm

def job_list(request):
    jobs = Job.objects.all().prefetch_related('job_title', 'job_status')
    context = {'jobs': jobs,}
    return(render(request, 'job/job_list.html', context))

class JobCreateView(View):
    """Create a new job."""
    def get(self, request):
        context = {
            'job_form': JobForm(),
            'title_form': TitleForm(),
            'status_form': StatusForm(),
            'manager_form': ManagerForm(),
        }
        return(render(request, 'job/job_detail.html', context))

    def post(self, request):
        j = JobForm(request.POST)
        t = TitleForm(request.POST)
        s = StatusForm(request.POST)
        if j.is_valid() and t.is_valid() and s.is_valid():
            fk = self._save_job_form(j)
            self._save_title_form(t, fk)
            self._save_status_form(s, fk)
        return(redirect('/job/'))

    def _save_job_form(self, form):
        cd = form.cleaned_data
        j = Job(note=cd['note'])
        j.save()
        return(j.id)

    def _save_title_form(self, form, fk):
        cd = form.cleaned_data
        t = Title(job_id=fk, title=cd['title'], note=cd['note'])
        t.save()

    def _save_status_form(self, form, fk):
        cd = form.cleaned_data
        s = Status(job_id=fk, status=cd['status'], note=cd['note'])
        s.save()

    def _save_manager_form(self, form, fk):
        cd = form.cleaned_data
        m = Manager(job_id=fk, manager=cd['status'], note=cd['note'])
        m.save()
 

class JobUpdateView(View):
    """Update an existing job. Only update the tables called."""
    def get(self, request, uid):
        context = {
            'job_form': self._fill_job_form(uid),
            'title_form': self._fill_title_form(uid),
            'status_form': self._fill_status_form(uid),
        }
        return(render(request, 'job/job_detail.html', context))

    def post(self, request, uid):
        """Only update if changes are made"""
        j = JobForm(request.POST)
        t = TitleForm(request.POST)
        s = StatusForm(request.POST)
        if j.is_valid() and t.is_valid() and s.is_valid():
            self._update_job_form(j, uid)
            self._update_title_form(t, uid)
            self._update_status_form(s, uid)
        return(redirect('/job/'))

    def _fill_job_form(self, uid):
        job = get_object_or_404(Job, id=uid)
        d = {
            'id': job.id,
            'note': job.note,
        }
        form = JobForm(d)
        return(form)

    def _fill_title_form(self, uid):
        title = Title.objects.filter(job=uid).latest()
        d = {
            'title': title.title,
            'note': title.note,
        }
        form = TitleForm(d)
        return(form)

    def _fill_status_form(self, uid):
        status = Status.objects.filter(job=uid).latest()
        d = {
            'status': status.status,
            'note': status.note,
        }
        form = StatusForm(d)
        return(form)
 
    def _update_job_form(self, form, uid):
        cd = form.cleaned_data
        j = Job(id=uid, note=cd['note'])
        j.save()

    def _update_title_form(self, form, uid):
        cd = form.cleaned_data
        t = Title.objects.filter(job=uid).latest()
        if t.title != cd['title'] or t.note != cd['note']:
            title = Title(job_id=uid, title=cd['title'], note=cd['note'])
            title.save()

    def _update_status_form(self, form, uid):
        cd = form.cleaned_data
        s = Status.objects.filter(job=uid).latest()
        if s.status != cd['status'] or s.note != cd['note']:
            status = Status(job_id=uid, status=cd['status'], note=cd['note'])
            status.save()


