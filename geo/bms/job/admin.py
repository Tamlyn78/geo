from django.contrib import admin

from .models import Job
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'note']

from .models import Title
@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

from .models import Status
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id']

from .models import Location
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'location', 'timestamp', 'note']

from .models import Contact
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'contact', 'organisation', 'note']

from .models import Element
@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'element', 'note']


