from django.contrib import admin
from .models import Appointment, Doctor
from .models import ContactMessage

admin.site.register(Doctor)
admin.site.register(Appointment)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_resolved')
    list_filter = ('is_resolved',)