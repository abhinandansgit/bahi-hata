from django.contrib import admin
from .models import Vendor

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'user', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('shop_name', 'user__username')
    prepopulated_fields = {'slug': ('shop_name',)}
