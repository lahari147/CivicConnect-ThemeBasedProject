from django.contrib import admin
from .models import Issue

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "location_name", "priority", "report_count", "created_at")
    list_filter = ("priority", "created_at")
    search_fields = ("description", "location_name")
    ordering = ("-priority_score", "-report_count")  # Orders by priority
