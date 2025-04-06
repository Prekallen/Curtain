from django.contrib import admin
from .models import PlaceBoard
# Register your models here.
class BoardAdmin(admin.ModelAdmin):
    list_display = ('place', 'writer', 'created_at', 'updated_at')


admin.site.register(PlaceBoard, BoardAdmin)