import json
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project
from teams.models import Team
from .models import Task
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

@login_required
def tasks(request):
    """Tasks view"""
    user = request.user

    tasks_list = Task.objects.filter(users=user.id).order_by('-deadline')

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
    }

    return render(request, 'calendar/tasks.html', context)


@login_required
def get_project_or_team_members(request):
    data = json.loads(request.body or '{}')

    if data.get('team'):
        team = get_object_or_404(Team, id=data.get('team'))
        serialized_members = json.loads(serialize('json', team.members.all(), use_natural_foreign_keys=True))
    elif data.get('project'):
        project = get_object_or_404(Project, id=data.get('project'))
        serialized_members = json.loads(serialize('json',
                                                  project.collaborators.all() | User.objects.filter(pk=project.lead.pk),
                                                  use_natural_foreign_keys=True))
    else:
        serialized_members =(json.loads(serialize('json',
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
    template_name = 'calendar/task_modal.html'


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


class TaskUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)

        # Check if user has permission to edit this task
        if not request.user.is_superuser and request.user not in task.users.all():
            return Response({'error': 'You do not have permission to edit this task'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = TaskCreateSerializer(task, data=request.data, partial=True)

        if serializer.is_valid():
            # Update task
            task = serializer.save()
            # Return success message
            return Response({'message': 'Task updated successfully', 'task_id': task.id},
                            status=status.HTTP_200_OK)

        # Return error if invalid
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
def get_dashboard_widgets(request):
    """API endpoint to get user's dashboard widget configuration"""
    from .models import DashboardWidget

    if request.method == 'GET':
        config, created = DashboardWidget.objects.get_or_create(user=request.user)
        return JsonResponse({
            'widgets': config.widgets,
            'layout': config.layout
        })

    elif request.method == 'POST':
        data = json.loads(request.body)
        config, created = DashboardWidget.objects.get_or_create(user=request.user)
        config.widgets = data.get('widgets', [])
        config.layout = data.get('layout', {})
        config.save()
        return JsonResponse({'status': 'success'})


@login_required
def get_widget_data(request, widget_type):
    """API endpoint to get data for a specific widget type"""
    user = request.user

    if widget_type == 'tasks':
        tasks = Task.objects.filter(users=user).order_by('-deadline')[:10]
        return JsonResponse({
            'tasks': [{
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'project': task.project.name if task.project else None,
                'team': task.team.name if task.team else None,
            } for task in tasks]
        })

    elif widget_type == 'stats':
        from datetime import datetime, timedelta

        total_tasks = Task.objects.filter(users=user).count()
        completed_tasks = Task.objects.filter(users=user, status='completed').count()
        active_projects = Project.objects.filter(
            models.Q(collaborators=user) | models.Q(lead=user)
        ).count()
        team_members = Team.objects.filter(members=user).values('members').distinct().count()

        # Calculate completion rate
        completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)

        return JsonResponse({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'active_projects': active_projects,
            'team_members': team_members,
            'completion_rate': completion_rate,
        })

    elif widget_type == 'team':
        # Get recent team activities
        activities = []

        # Recent task creations
        recent_tasks = Task.objects.filter(
            models.Q(team__members=user) | models.Q(project__collaborators=user)
        ).order_by('-pub_date')[:5]

        for task in recent_tasks:
            activities.append({
                'title': f'New task: {task.title}',
                'timestamp': task.pub_date.isoformat(),
                'icon': 'tasks'
            })

        return JsonResponse({'activities': activities})

    elif widget_type == 'calendar':
        # Get upcoming tasks and events as calendar events
        tasks = Task.objects.filter(users=user, deadline__isnull=False).order_by('deadline')[:20]
        events = [{
            'title': task.title,
            'start': task.deadline.isoformat() if task.deadline else None,
            'className': f'status-{task.status}'
        } for task in tasks if task.deadline]

        return JsonResponse({'events': events})

    elif widget_type == 'projectTimeline':
        projects = Project.objects.filter(
            models.Q(collaborators=user) | models.Q(lead=user)
        )[:5]

        project_data = []
        for project in projects:
            total_tasks = Task.objects.filter(project=project).count()
            completed_tasks = Task.objects.filter(project=project, status='completed').count()
            progress = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)

            project_data.append({
                'id': project.id,
                'name': project.name,
                'progress': progress,
                'deadline': project.deadline.isoformat() if hasattr(project, 'deadline') and project.deadline else None,
            })

        return JsonResponse({'projects': project_data})

    elif widget_type == 'teamBoard':
        todo = Task.objects.filter(users=user, status='todo')[:5]
        in_progress = Task.objects.filter(users=user, status='in_progress')[:5]
        completed = Task.objects.filter(users=user, status='completed')[:5]

        return JsonResponse({
            'todo': [{'id': t.id, 'title': t.title} for t in todo],
            'in_progress': [{'id': t.id, 'title': t.title} for t in in_progress],
            'completed': [{'id': t.id, 'title': t.title} for t in completed],
        })

    elif widget_type == 'analytics':
        # Placeholder for analytics data
        return JsonResponse({
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'data': [12, 19, 3, 5, 2, 3, 7]
        })

    else:
        return JsonResponse({'error': 'Unknown widget type'}, status=400)
