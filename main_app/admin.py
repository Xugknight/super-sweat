from django.contrib import admin
from .models import Profile, Guild, Membership, Event, EventTemplate, RSVP, ExternalAccount

# Register your models here.
admin.site.register(Profile)
admin.site.register(Guild)
admin.site.register(Membership)
admin.site.register(Event)
admin.site.register(EventTemplate)
admin.site.register(RSVP)
admin.site.register(ExternalAccount)