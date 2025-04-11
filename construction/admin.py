from django.contrib import admin
from .models import Construction
# Register your models here.
class BoardAdmin(admin.ModelAdmin):
    list_display = ('address', 'housing_type', 'writer', 'latitude', 'longitude', 'created_at', 'updated_at')

admin.site.register(Construction, BoardAdmin)