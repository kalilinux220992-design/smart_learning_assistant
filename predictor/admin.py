from django.contrib import admin

from predictor.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "company_name", "branch", "package_lpa", "status")
    list_filter = ("status", "branch", "year", "company_name")
    search_fields = ("name", "company_name", "branch")
