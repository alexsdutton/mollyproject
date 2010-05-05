from django.contrib import admin
from models import Hit

class HitAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_id', 'requested', 'status_code', 'response_time', 'full_path')
    list_filter = ('location_method', 'view_name', 'status_code')

admin.site.register(Hit, HitAdmin)
