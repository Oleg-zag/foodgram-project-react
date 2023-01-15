from django.contrib import admin

from .models import User, Subscriptions

admin.site.register(User)
admin.site.register(Subscriptions)
