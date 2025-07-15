from django.contrib import admin
from .models import (
    Profile, ExternalAccount,
    Guild, Membership,
    Event, EventTemplate,
    RSVP
)
class ExternalAccountInline(admin.TabularInline):
    model = ExternalAccount
    extra = 1            
    can_delete = True      
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'status', 'created_at')
    inlines = [ExternalAccountInline]
    
    fields = ('user', 'display_name', 'rank', 'main_game', 'preferred_roles', 'status')
    
# keep registering the rest as before:
admin.site.register(Guild)
admin.site.register(Membership)
admin.site.register(Event)
admin.site.register(EventTemplate)
admin.site.register(RSVP)