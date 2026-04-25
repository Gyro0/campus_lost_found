from django.contrib import admin
from .models import Category, Report


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "report_type",
        "status",
        "category",
        "location",
        "user",
        "event_date",
        "created_at"
    )
    list_filter = ("report_type", "status", "category", "created_at")
    search_fields = ("title", "description", "location", "user__username")
    readonly_fields = ("created_at", "updated_at", "recovered_at")
    
    fieldsets = (
        ("Item Information", {
            "fields": ("title", "description", "category", "image")
        }),
        ("Report Details", {
            "fields": ("report_type", "status", "location", "event_date")
        }),
        ("Contact", {
            "fields": ("contact_info",)
        }),
        ("User & Timestamps", {
            "fields": ("user", "created_at", "updated_at", "recovered_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return self.readonly_fields + ("user", "report_type")
        return self.readonly_fields

