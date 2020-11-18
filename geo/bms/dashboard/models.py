from django.db import models

from job.models import Job
from contact.models import Contact, Organisation
from element.models import Element

class TradingName(models.Model):
    """Trading name of the business."""
    name = models.TextField()
    date = models.DateField()
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-date',)
        get_latest_by = 'date'
    
    def __str__(self):
        return(self.name)


class Contact(models.Model):
    """A link between contact and jobs."""
    job = models.ForeignKey(Job, to_field='id', on_delete=models.CASCADE, related_name='dashboard_contact_job')
    contact = models.ForeignKey(Contact, to_field='id', on_delete=models.CASCADE, related_name='dashboard_contact')
    organisation = models.ForeignKey(Organisation, to_field='id', on_delete=models.CASCADE, related_name='dashboard_organisation')
    timestamp = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-job',)
        get_latest_by = 'timestamp'
    
    def __str__(self):
        return(self.contact)


class Element(models.Model):
    job = models.ForeignKey(Job, to_field='id', on_delete=models.CASCADE, related_name='dashboard_element_job')
    element = models.ForeignKey(Element, to_field='id', on_delete=models.CASCADE, related_name='dashboard_element')
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-job', '-element',)

    def __str__(self):
        return(self.element)



