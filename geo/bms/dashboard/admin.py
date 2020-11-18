from django.contrib import admin

from .models import TradingName
@admin.register(TradingName)
class TradingNameAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'note']

from .models import Contact
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'contact', 'organisation', 'timestamp', 'note']

from .models import Element
@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'element', 'note']


