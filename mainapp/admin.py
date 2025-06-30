from django.contrib import admin
from .models import Project, Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at', 'resume_file')


@admin.register(Project)  # Register Project model
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'github_link', 'created_at')  # Add your fields
    search_fields = ('title', 'description')  # Search bar
    list_filter = ('created_at',)  # Filter by date