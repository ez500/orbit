import json
import traceback
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.models import Company, Announcement
from message.models import Message
from projects.models import Project
from teams.models import Team
from .forms import TaskForm, EventForm
from .models import Task, InsightSuggestion, Event, Notification
from .orbit import generate_orbit_insights
from .serializer import TaskViewSerializer, TaskCreateSerializer


@login_required
def dashboard(request):
    """Dashboard view"""
    user = request.user

    personal_tasks = Task.objects.filter(users=user).order_by('-pub_date')[:5]

    project_tasks = Task.objects.filter(
        project__in=Project.objects.filter(collaborators=user) | Project.objects.filter(lead=user)
    ).order_by('-pub_date')[:5]

    # Check if user has completed the tour
    has_completed_tour = user.profile.has_completed_tour if hasattr(user, 'profile') else False

    context = {
        'title': 'Dashboard',
        'personal_tasks': personal_tasks,
        'project_tasks': project_tasks,
        'has_completed_tour': has_completed_tour,
    }
    return render(request, 'dashboard/dashboard.html', context)


# TODO ADD CONFIRMATION PAGE BEFORE EXECUTING ANY SUGGESTION
@login_required
def orbit_insights(request):
    """Orbit Insights view"""

    return render(request, 'dashboard/orbit_insights.html', {"title": "Orbit Insights"})


class OrbitInsightsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = generate_orbit_insights(request.user, persist=True)
        batch_id = data["batch_id"]

        suggestions = InsightSuggestion.objects.filter(
            user=request.user,
            batch_id=batch_id
        ).order_by('-created_at')

        html = render_to_string(
            "dashboard/_orbit_suggestion_cards.html",
            {
                "suggestions": suggestions,
                "fallback": data["fallback"],
            },
            request=request
        )
        return Response({"html": html}, status=status.HTTP_200_OK)


@login_required
def execute_suggestion(request, suggestion_id):
    suggestion = get_object_or_404(
        InsightSuggestion, id=suggestion_id, user=request.user
    )
    if suggestion.executed:
        messages.info(request, "Suggestion already executed.")
        return redirect("dashboard:orbit_insights")

    payload = suggestion.raw_data or {}
    suggestion_type = payload.get("type") or suggestion.suggestion_type

    try:
        if suggestion_type == "create_task":
            title = request.POST.get("title") or payload.get("title") or "Orbit Task"
            content = request.POST.get("content") or payload.get("content") or ""
            deadline = request.POST.get("deadline") or payload.get("deadline")
            project_or_team_id = payload.get("project_or_team_id")
            user_ids = payload.get("users", [])

            task = Task.objects.create(
                title=title,
                content=content,
                deadline=deadline or None
            )

            if project_or_team_id:
                project = Project.objects.filter(id=project_or_team_id).first()
                if project:
                    task.project = project
                    task.save()
                else:
                    team = Team.objects.filter(id=project_or_team_id).first()
                    if team:
                        task.team = team
                        task.save()

            if user_ids:
                task.users.set(User.objects.filter(id__in=user_ids))

            suggestion.mark_executed()
            messages.success(request, "Task created from insight.")
            return redirect("dashboard:tasks")

        elif suggestion_type == "create_event":
            title = request.POST.get("title") or payload.get("title") or "Orbit Event"
            content = (
                    request.POST.get("content")
                    or payload.get("content")
                    or ""
            )
            start_datetime = request.POST.get("start_datetime") or payload.get("start_datetime")
            end_datetime = request.POST.get("end_datetime") or payload.get("end_datetime")
            project_or_team_id = payload.get("project_or_team_id")
            user_ids = payload.get("users", [])

            event = Event.objects.create(
                title=title,
                content=content,
                start_datetime=start_datetime or None,
                end_datetime=end_datetime or None
            )

            if project_or_team_id:
                project = Project.objects.filter(id=project_or_team_id).first()
                if project:
                    event.project = project
                    event.save()
                else:
                    team = Team.objects.filter(id=project_or_team_id).first()
                    if team:
                        event.team = team
                        event.save()

            if user_ids:
                event.users.set(User.objects.filter(id__in=user_ids))

            suggestion.mark_executed()
            messages.success(request, "Event created from insight.")
            return redirect("dashboard:dashboard")

        elif suggestion_type == "create_announcement":
            company_id = payload.get("company_id")
            company = get_object_or_404(Company, id=company_id)

            title = (
                    request.POST.get("title")
                    or payload.get("title")
                    or "Orbit Announcement"
            )

            content = (
                    request.POST.get("content")
                    or payload.get("content")
                    or ""
            )

            announcement = Announcement.objects.create(
                company=company,
                title=title,
                content=content
            )

            task_ids = payload.get("tasks") or []
            if task_ids:
                announcement.tasks = Task.objects.filter(id__in=task_ids)
                announcement.save()

            suggestion.mark_executed()
            messages.success(request, "Announcement created from insight.")
            return redirect("company:company", name=company.name)

        elif suggestion_type == "send_message":
            conversation_id = payload.get("conversation_id")
            content = payload.get("content") or ""

            message = Message.objects.create(
                conversation_id=conversation_id,
                sender=request.user,
                content=content
            )

            team_id = payload.get("team_id")
            if team_id:
                message.team_id = team_id
                message.save()

            suggestion.mark_executed()
            messages.success(request, "Message sent from insight.")
            return redirect(
                "message:conversation_thread",
                username=request.user.username,
                conversation_id=conversation_id
            )

        # TODO IMPLEMENT EMAIL HELPER
        elif suggestion_type == "send_email":
            payload["subject"] = (
                    request.POST.get("subject")
                    or payload.get("subject")
            )
            payload["body"] = (
                    request.POST.get("body")
                    or payload.get("body")
            )
            request.session["orbit_email_draft"] = payload
            suggestion.mark_executed()
            return redirect(reverse("email:compose") + "?from_orbit=1")

        elif suggestion_type == "general_insight":
            suggestion.mark_executed()
            messages.info(request, "Marked insight as read.")
            return redirect("dashboard:orbit_insights")

        else:
            messages.error(request, "Unknown suggestion type.")
            return redirect("dashboard:orbit_insights")

    except Exception:
        messages.error(request, "Failed to execute insight suggestion.")
        traceback.print_exc()
        return redirect("dashboard:orbit_insights")


@login_required
def tasks(request):
    """Tasks view"""
    user = request.user
    qs = Team.objects.filter(members=user)
    projects = Project.objects.filter(Q(lead=request.user) | Q(collaborators=request.user))

    q1 = Q(users=user.id)
    q2 = Q(team__in=qs)
    q3 = Q(project__in=projects)

    tasks_list = Task.objects.filter(q1 | q2 | q3).order_by('-deadline')

    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    team_filter = request.GET.get('team', '')
    project_filter = request.GET.get('project', '')
    deadline_filter = request.GET.get('deadline', '')
    sort_by = request.GET.get('sort', '')

    if search:
        tasks_list = tasks_list.filter(title__icontains=search) | tasks_list.filter(content__icontains=search)
    if status_filter:
        tasks_list = tasks_list.filter(status=status_filter)
    if team_filter:
        tasks_list = tasks_list.filter(team__id=team_filter)
    if project_filter:
        tasks_list = tasks_list.filter(project__id=project_filter)
    if deadline_filter:
        today = date.today()
        if deadline_filter == 'overdue':
            tasks_list = tasks_list.filter(deadline__lt=today)
        elif deadline_filter == 'today':
            tasks_list = tasks_list.filter(deadline=today)
        elif deadline_filter == 'upcoming':
            tasks_list = tasks_list.filter(deadline__gt=today)

    order_map = {
        "deadline_asc": "deadline",
        "deadline_desc": "-deadline",
        "created_asc": "pub_date",
        "created_desc": "-pub_date",
        "title_asc": "title",
        "title_desc": "-title",
        "status": "status",
    }

    if sort_by in order_map:
        tasks_list = tasks_list.order_by(order_map[sort_by])
    else:
        tasks_list = tasks_list.order_by('deadline')

    teams = Team.objects.filter(members=user.id)
    projects = Project.objects.filter(collaborators=user.id) | Project.objects.filter(lead=user.id)

    serializer = TaskViewSerializer(tasks_list, many=True)

    if request.method == "POST":
        if "add_task" in request.POST:
            task_form = TaskForm(request.POST, user=request.user)
            if task_form.is_valid():
                new_task = task_form.save()
                new_task.save()
                messages.success(request, "Task created successfully.")
                return redirect("dashboard:tasks")
            else:
                messages.error(request, "Error creating task.")
        elif "add_event" in request.POST:
            event_form = EventForm(request.POST, user=request.user)
            if event_form.is_valid():
                new_event = event_form.save()
                new_event.save()
                messages.success(request, "Task created successfully.")
                return redirect("dashboard:tasks")
            else:
                messages.error(request, "Error creating event.")

    task_form = TaskForm(user=request.user)
    event_form = EventForm(user=request.user)

    context = {
        'title': 'Tasks',
        'tasks_qs': tasks_list,
        'tasks': serializer.data,
        'teams': teams,
        'projects': projects,
        'search': search,
        'status_filter': status_filter,
        'team_filter': team_filter,
        'project_filter': project_filter,
        'deadline_filter': deadline_filter,
        'sort_by': sort_by,
        'empty': not tasks_list.exists(),
        'task_form': task_form,
        'event_form': event_form,
    }

    return render(request, 'dashboard/calendar/tasks.html', context)


@login_required
def get_project_or_team_members(request):
    data = json.loads(request.body or '{}')

    if data.get('team'):
        team = get_object_or_404(Team, id=data.get('team'))
        serialized_members = json.loads(serialize('json', team.members.all(), use_natural_foreign_keys=True))
    elif data.get('project'):
        project = get_object_or_404(Project, id=data.get('project'))
        serialized_members = json.loads(serialize('json',
                                                  User.objects.filter(Q(led_projects=project)
                                                                      | Q(collaborative_projects=project)).distinct(),
                                                  use_natural_foreign_keys=True))
    else:
        serialized_members = (json.loads(serialize('json',
                                                   User.objects.filter(pk=request.user.pk),
                                                   use_natural_foreign_keys=True)))

    formatted_members = {}
    for member in serialized_members:
        fields = member['fields']
        fields['id'] = member['pk']
        formatted_members[fields['id']] = fields

    return JsonResponse(formatted_members)


class TaskDetailModalView(DetailView):
    model = Task
    template_name = 'dashboard/calendar/_view_task_modal.html'


class TaskCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            print(e)

        if serializer.is_valid():
            task = serializer.save()

            return Response({'message': 'Task created successfully', 'task_id': task.id},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@require_POST
@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if not request.user.is_superuser and request.user not in task.users.all():
        messages.error(request, "Not authorized.")
        return redirect("dashboard:tasks")
    task.delete()
    messages.success(request, "Task deleted successfully.")
    return redirect("dashboard:tasks")


@login_required
def notifications(request):
    notifications_list = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(
        request,
        "dashboard/notifications.html",
        {"title": "Notifications", "notifications": notifications_list},
    )
