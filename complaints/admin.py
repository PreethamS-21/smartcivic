from django.contrib import admin
from .models import Category, Department, Complaint, StatusLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display  = ['complaint_id', 'title', 'user', 'category', 'status', 'created_at']
    list_filter   = ['status', 'category', 'department']
    search_fields = ['complaint_id', 'title', 'user__username']
    readonly_fields = ['complaint_id', 'qr_code', 'created_at', 'updated_at']


@admin.register(StatusLog)
class StatusLogAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'old_status', 'new_status', 'changed_by', 'changed_at']
    readonly_fields = ['changed_at']
