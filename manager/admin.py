from django.contrib import admin
from .models import Manager

# Register your models here.
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'username','address', 'phone', 'email', 'password', 'created_at', 'updated_at')

admin.site.register(Manager, ManagerAdmin)