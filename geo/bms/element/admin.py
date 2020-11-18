from django.contrib import admin

from .models import Factor
@admin.register(Factor)
class FactorAdmin(admin.ModelAdmin):
    #list_display = ['id', 'job', 'factor', 'parent', 'note']
    list_display = ['id', 'group', 'factor', 'note']

from .models import Element
@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    #list_display = ['id', 'factor', 'value', 'note']
    list_display = ['id', 'factor', 'value', 'parent', 'note']


