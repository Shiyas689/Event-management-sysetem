from django.contrib import admin
from .models import Contractor, Event

# Customizing ContractorAdmin
class ContractorAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'phone', 'email', 'created_at', 'updated_at', 'profile_image')
    search_fields = ['user__username', 'user__email', 'phone']
    list_filter = ['created_at', 'updated_at']

    def get_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name  # Assuming user has first and last names
    get_name.short_description = 'Name'  # Label in admin

# Register the Contractor model with custom admin options
admin.site.register(Contractor, ContractorAdmin)

# Customizing EventAdmin
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'created_at', 'updated_at', 'poster_image')
    search_fields = ['title', 'location']
    list_filter = ['date', 'created_at']

# Register the Event model with custom admin options
admin.site.register(Event, EventAdmin)
