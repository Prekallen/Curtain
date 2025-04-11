from django.contrib import admin
from .models import Contract
# Register your models here.
class BoardAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address', 'writer', 'price', 'created_at', 'updated_at', 'const_date', 'complete')

admin.site.register(Contract, BoardAdmin)