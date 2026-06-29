from django.contrib import admin
from .models import Task, TaskDetail, Employee, Project


class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']


class TaskDetailAdmin(admin.ModelAdmin):
    list_display = ['task', 'priority', 'asset_image', 'asset_caption']
    list_filter = ['priority']
    search_fields = ['task__title', 'notes', 'asset_caption']
    fields = ['task', 'priority', 'notes', 'asset_image', 'asset_caption']


# Register your models here.
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskDetail, TaskDetailAdmin)
admin.site.register(Employee)
admin.site.register(Project)