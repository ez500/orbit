from django.contrib import admin
from .models import Team, TeamMembership

class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0
    autocomplete_fields = ["user"]

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "member_count")
    search_fields = ("name", "description")
    inlines = [TeamMembershipInline]

    def member_count(self, obj):
        return obj.members.count()

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("team", "user", "role", "joined_at")
    list_filter = ("role", "joined_at")
    search_fields = ("team__name", "user__username", "user__email")
