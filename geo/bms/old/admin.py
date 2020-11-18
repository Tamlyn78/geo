from os.path import join
from bms.settings import BASE_DIR
from django.contrib import admin
from django.utils.html import format_html

#import admin_thumbnails

# Register your models here.
from .models import Job
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'folder', 'description', 'location', 'open', 'client', 'notes')
    search_fields = ['id', 'description', 'client__organisation__name', 'location__description', 'client__firstname', 'client__lastname', 'open', 'notes']

    def folder(self, obj):
        """Create a link to the project folder; currently """
        s = 'file:////' + BASE_DIR + '/_' + str(obj.id)
        return(format_html('<a href="{{ %s }}">Open</a>' % s))
    folder.allow_tags = True

from .models import JobStatus
@admin.register(JobStatus)
class JobStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'date', 'status', 'notes')
    search_fields = ['id', 'job__id', 'job__description', 'date', 'status', 'notes']

#from .models import Manager
#@admin.register(Manager)
#class ManagerAdmin(admin.ModelAdmin):
#    list_display = ('id', 'job', 'person', 'notes')
#    search_fields = ['id', 'job__id', 'user__username', 'user__first_name', 'user__last_name', 'notes']

from .models import Closure
@admin.register(Closure)
class ClosureAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'date', 'notes')
    #search_fields = ['id', 'description', 'client__organisation__name', 'location__description', 'client__firstname', 'client__lastname', 'open', 'notes']

from .models import Location
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'notes')
    search_fields = ['id', 'description', 'notes']
    
from .models import Organisation
@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'abbreviation', 'address', 'notes')
    #search_fields = ('name', 'firstname', 'lastname', 'notes')
    
from .models import Client
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'lastname', 'organisation', 'status', 'notes')
    list_filter = ['status']
    search_fields = ('organisation', 'firstname', 'lastname', 'notes')
    
from .models import Invoice
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    #list_display = ('id', 'job', 'date', 'value', 'payment_date', 'notes')
    list_display = ('id', 'job', 'value', 'payment_date', 'notes')
    search_fields = ['job__id', 'job__description']

from .models import Quote
@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'date', 'description', 'status', 'notes')
    search_fields = ['job__id', 'job__description', 'date', 'description', 'status', 'notes']
    
from .models import Factor
@admin.register(Factor)
class FactorAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'label', 'notes')

from .models import Element
@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'factor', 'value', 'notes')
    
    #def get_name(self, obj):
    #    return obj.factor.job
    #get_name.admin_order_field  = 'id'
    #get_name.short_description = 'Job'
    
from .models import Rank
@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent', 'child')
    
from .models import ASC
@admin.register(ASC)
class ASCAdmin(admin.ModelAdmin):
    list_display = ('id', 'element', 'label')
    
from .models import Sample
@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'element', 'field_label')
    
from .models import PSA
@admin.register(PSA)
class PSAAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_id', 'sample_id', 'date')
    
from .models import Receipt
@admin.register(Receipt)
#@admin_thumbnails.thumbnail('image')
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'upload', 'date', 'value', 'currency', 'category', 'description', 'note')
    list_filter = ('date', 'category')
    search_fields = ['date', 'value', 'currency', 'note']

