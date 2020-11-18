"""Jobs should also include details such as contacts (including organisation, where relevant), location and manager"""


from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from contact.models import Contact as JobContact, Organisation as JobOrg
from element.models import Element as JobElement

class Job(models.Model):
    """Unique identifier for a job. All other job attributes should point here."""
    timestamp = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return(str(self.id))

    def get_absolute_url(self):
        return(reverse('job:job_detail', args=[self.id]))

class Title(models.Model):
    """A descriptive title for the job. This should be changeable but keeping a record of previous titles for traceability, hence a timestamp is used to determine the latest title. Preferably this should be the same as the output report/presentation or other."""
    job = models.ForeignKey(Job, to_field='id', on_delete=models.CASCADE, related_name='job_title')
    title = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-job', '-timestamp',)
        get_latest_by = 'timestamp'

    def __str__(self):
        return(self.title)

class Status(models.Model):
    """A record of the current status of a job (e.g. open or closed)."""
    job = models.ForeignKey(Job, to_field='id', on_delete=models.CASCADE, related_name='job_status')
    status = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-job', '-timestamp',)
        get_latest_by = 'timestamp'

    def __str__(self):
        b = 'Active' if self.status else 'Closed'
        return(b)

   
class Location(models.Model):
    """A string describing the location of a job. This should become a foreign key cross-table to an app with actual GIS data."""
    job = models.ForeignKey(Job, to_field='id', on_delete=models.CASCADE, related_name='job_location')
    location = models.TextField(default=True, )
    timestamp = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-job', '-timestamp',)
        get_latest_by = 'timestamp'

    def __str__(self):
        return(self.location)


class Contact(models.Model):
    """A link between contact and jobs."""
    job = models.ForeignKey(Job, to_field='id', on_delete=models.CASCADE, related_name='job_contact')
    contact = models.ForeignKey(JobContact, to_field='id', on_delete=models.CASCADE, related_name='Job_contact_id')
    organisation = models.ForeignKey(JobOrg, to_field='id', on_delete=models.CASCADE, related_name='contact_organisation')
    timestamp = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-job',)
        get_latest_by = 'timestamp'
    
    def __str__(self):
        return(self.contact)


class Element(models.Model):
    job = models.ForeignKey(Job, to_field='id', on_delete=models.CASCADE, related_name='job_element_job')
    element = models.ForeignKey(JobElement, to_field='id', on_delete=models.CASCADE, related_name='job_element_id')
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-job', '-element',)

    def __str__(self):
        return(self.element)


