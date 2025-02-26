# 在 feedback/admin.py 中
from django.contrib import admin
from .models import Registration

class CheckAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'check_in_time', 'check_out_time', 'is_checked_out')
    list_filter = ('event', 'is_checked_out')
    search_fields = ('user__username', 'event__name')

admin.site.register(Registration, CheckAdmin)
