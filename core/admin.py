from django.contrib import admin
from .models import SiteStat

@admin.register(SiteStat)
class SiteStatAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'order')
    list_editable = ('order',)
