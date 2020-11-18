from django.contrib import admin

from .models import Organisation
@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'abbr', 'timestamp', 'note')
 

from .models import Contact
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'note')
 
from .models import Name
@admin.register(Name)
class NameAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact', 'first', 'middle', 'last', 'timestamp', 'note')
 
#from .models import ContactOrg
#@admin.register(ContactOrg)
#class ContactOrgAdmin(admin.ModelAdmin):
#    list_display = ('id', 'contact', 'organisation', 'timestamp', 'note')
# 
