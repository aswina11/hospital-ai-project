from django.contrib import admin
from .models import Appointment, Doctor

admin.site.register(Doctor)
admin.site.register(Appointment)