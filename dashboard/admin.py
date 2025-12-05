from django.contrib import admin

from dashboard.models import Task, InsightSuggestion, Event

# Register your models here.

admin.site.register(Task)
admin.site.register(Event)
admin.site.register(InsightSuggestion)
