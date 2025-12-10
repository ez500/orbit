from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.models import User

from dashboard.models import Task, Event
from dashboard.forms import TaskForm, EventForm
from .models import Team, TeamMembership,TeamDocument
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import JoinTeamForm
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse


class MyTeamsView(LoginRequiredMixin, ListView):
    model = Team
    template_name = "teams/my_teams.html"
    context_object_name = "teams"
    paginate_by = 12
    extra_context = {'title': 'My Teams'}

    def get_queryset(self):
        qs = Team.objects.filter(members=self.request.user).order_by("name").prefetch_related("members")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        return qs


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "teams/team_detail.html"
    context_object_name = "team"
    extra_context = {'title': 'My Teams'}
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.get_object()

        context["memberships"] = team.memberships.select_related("user")

        try:
            context["acting"] = TeamMembership.objects.get(user=self.request.user, team=team)
        except TeamMembership.DoesNotExist:
            context["acting"] = None

        context["user_is_member"] = self.request.user in team.members.all()

        return context


# TODO: EDIT TEAM
class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = "teams/create_team.html"
    fields = ["name", "description", "company"]
    success_url = reverse_lazy("teams:my_teams")
    extra_context = {'title': 'Create Team'}

    def form_valid(self, form):
        response = super().form_valid(form)
        TeamMembership.objects.create(
            user=self.request.user,
            team=self.object,
            role="Lead"
        )
        return response


@login_required
def join_team(request):
    if request.method == "POST":
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            team = form.cleaned_data["team_name"]
            already_member = TeamMembership.objects.filter(user=request.user, team=team).exists()
            if already_member:
                messages.warning(request, f"You’re already in {team.name}.")
                return redirect("teams:my_teams")

            TeamMembership.objects.create(user=request.user, team=team, role="Member")
            messages.success(request, f"You joined {team.name} successfully!")
            return redirect("teams:my_teams")
    else:
        form = JoinTeamForm()

    return render(request, "teams/join_team.html", {"form": form})


@login_required
def team_dashboard(request, pk):
    team = get_object_or_404(Team, pk=pk)

    if request.user not in team.members.all():
        messages.error(request, "You are not a member of this team.")
        return redirect("teams:my_teams")

    # Handle adding tasks
    if request.method == "POST":
        if "add_task" in request.POST:
            task_form = TaskForm(request.POST, user=request.user, team=team)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.team = team
                task.save()
                task_form.save_m2m()
                messages.success(request, f"Task '{task.title}' added.")
                return redirect("teams:team_dashboard", pk=pk)

        elif "add_event" in request.POST:
            event_form = EventForm(request.POST, user=request.user, team=team)
            if event_form.is_valid():
                event = event_form.save(commit=False)
                event.team = team
                event.save()
                event_form.save_m2m()
                messages.success(request, f"Event '{event.title}' created.")
                return redirect("teams:team_dashboard", pk=pk)

    task_form = TaskForm(team=team)
    event_form = EventForm(team=team)

    tasks = team.tasks.all().order_by("-pub_date")
    events = team.events.all().order_by("-start_datetime")

    context = {
        "team": team,
        "team_tasks": tasks,
        "team_events": events,
        "task_form": task_form,
        "event_form": event_form,
        "title": f"{team.name} Dashboard",
    }
    return render(request, "teams/team_dashboard.html", context)


@login_required
def delete_team_task(request, team_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk, team_id=team_pk)
    team = task.team

    if request.user not in team.members.all():
        messages.error(request, "You are not allowed to delete this task.")
        return redirect("teams:team_dashboard", pk=team_pk)

    task.delete()
    messages.success(request, f"Task '{task.title}' deleted.")
    return redirect("teams:team_dashboard", pk=team_pk)


@login_required
def delete_team_event(request, team_pk, event_pk):
    event = get_object_or_404(Event, pk=event_pk, team_id=team_pk)
    team = event.team

    if request.user not in team.members.all():
        messages.error(request, "You are not allowed to delete this event.")
        return redirect("teams:team_dashboard", pk=team_pk)

    event.delete()
    messages.success(request, f"Event '{event.title}' deleted.")
    return redirect("teams:team_dashboard", pk=team_pk)


@login_required
def leave_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.user in team.members.all():
        team.members.remove(request.user)
        messages.success(request, f"You have left the team '{team.name}'.")
    else:
        messages.warning(request, "You are not a member of this team.")
    return redirect("teams:my_teams")

@login_required
def remove_member(request, team_pk, user_pk):
    team = get_object_or_404(Team, pk=team_pk)
    target = get_object_or_404(User, pk=user_pk)

    acting = TeamMembership.objects.get(user=request.user, team=team)
    target_mem = TeamMembership.objects.get(user=target, team=team)

    if acting.role not in ["Lead", "Manager"]:
        messages.error(request, "You do not have permission to remove members.")
        return redirect("teams:detail", pk=team_pk)

    if acting.role == "Manager" and acting.user == target:
        messages.error(request, "Managers cannot remove themselves.")
        return redirect("teams:detail", pk=team_pk)

    if target_mem.role == "Lead":
        messages.error(request, "You cannot remove the Team Lead.")
        return redirect("teams:detail", pk=team_pk)

    target_mem.delete()
    messages.success(request, f"{target.username} has been removed from the team.")
    return redirect("teams:detail", pk=team_pk)


@login_required
def promote_member(request, team_pk, user_pk):
    team = get_object_or_404(Team, pk=team_pk)
    target = get_object_or_404(User, pk=user_pk)

    acting = TeamMembership.objects.get(user=request.user, team=team)
    target_mem = TeamMembership.objects.get(user=target, team=team)

    if acting.role != "Lead":
        messages.error(request, "Only the Team Lead can promote members.")
        return redirect("teams:detail", pk=team_pk)

    if target_mem.role != "Member":
        messages.error(request, "Only members can be promoted.")
        return redirect("teams:detail", pk=team_pk)

    target_mem.role = "Manager"
    target_mem.save()
    messages.success(request, f"{target.username} promoted to Manager.")
    return redirect("teams:detail", pk=team_pk)


@login_required
def demote_member(request, team_pk, user_pk):
    team = get_object_or_404(Team, pk=team_pk)
    target = get_object_or_404(User, pk=user_pk)

    acting = TeamMembership.objects.get(user=request.user, team=team)
    target_mem = TeamMembership.objects.get(user=target, team=team)

    if acting.role != "Lead":
        messages.error(request, "Only the Team Lead can demote managers.")
        return redirect("teams:detail", pk=team_pk)

    if target_mem.role != "Manager":
        messages.error(request, "Only managers can be demoted.")
        return redirect("teams:detail", pk=team_pk)

    target_mem.role = "Member"
    target_mem.save()
    messages.success(request, f"{target.username} demoted to Member.")
    return redirect("teams:detail", pk=team_pk)

@login_required
def team_add_document(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk)

    if request.method == "POST":
        form = TeamDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.team = team
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, "Document added successfully.")
            return redirect("teams:team_dashboard", team_pk)
    else:
        form = TeamDocumentForm()

    return render(request, "teams/team_add_document.html", {
        "team": team,
        "form": form
    })


@login_required
def team_view_document(request, team_pk, doc_pk):
    team = get_object_or_404(Team, pk=team_pk)
    document = get_object_or_404(TeamDocument, pk=doc_pk, team=team)
    return render(request, "teams/team_view_document.html", {
        "team": team,
        "document": document
    })


@login_required
def team_delete_document(request, team_pk, doc_pk):
    team = get_object_or_404(Team, pk=team_pk)
    document = get_object_or_404(TeamDocument, pk=doc_pk, team=team)

    if request.user not in team.members.all():
        return HttpResponseForbidden("Not allowed")

    document.delete()
    messages.success(request, "Document deleted.")
    return redirect("teams:team_dashboard", team_pk)


@login_required
def team_edit_internal_document(request, team_pk, doc_pk):
    team = get_object_or_404(Team, pk=team_pk)
    document = get_object_or_404(TeamDocument, pk=doc_pk, team=team)

    if document.doc_type != "internal":
        messages.error(request, "Only internal documents can be edited.")
        return redirect("teams:team_view_document", team_pk, doc_pk)

    if request.method == "POST":
        document.content = request.POST.get("content")
        document.save()
        messages.success(request, "Document updated.")
        return redirect("teams:team_view_document", team_pk, doc_pk)

    return render(request, "teams/team_edit_document.html", {
        "team": team,
        "document": document
    })

@login_required
def team_create_internal_document(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk)

    if request.method == "POST":
        name = request.POST.get("name")
        content = request.POST.get("content")

        doc = TeamDocument.objects.create(
            team=team,
            name=name,
            doc_type="internal",
            content=content,
            uploaded_by=request.user
        )
        return redirect("teams:team_view_document", team_pk=team.pk, doc_pk=doc.pk)

    return render(request, "teams/team_create_internal_document.html", {
        "team": team
    })
def my_teams_api(request):
    """API endpoint to get user's teams as JSON"""
    teams = Team.objects.filter(members=request.user).order_by("name")

    teams_data = [
        {
            'id': team.id,
            'name': team.name,
        }
        for team in teams
    ]

    return JsonResponse({'teams': teams_data})
