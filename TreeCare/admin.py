from django.contrib import admin
from .models import *
# Register your models here.
@admin.action(description='Xóa toàn bộ dữ liệu trong bảng')
def delete_all_data(modeladmin, request, queryset):
    modeladmin.model.objects.all().delete()

class TreeAdmin(admin.ModelAdmin):
    actions = [delete_all_data]

admin.site.register(Tree, TreeAdmin)