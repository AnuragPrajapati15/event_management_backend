from django.contrib import admin
from .models import User, Event, Ticket, Profile


admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Event)
admin.site.register(Ticket)


