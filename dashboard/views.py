import json
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.db.models import Q
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
    qs = Team.objects.filter(members=user)
    projects = Project.objects.filter(Q(lead=request.user) | Q(collaborators=request.user))

    q1 = Q(users=user.id)
    q2 = Q(team__in=qs)
    q3 = Q(project__in=projects)

    personal_tasks = Task.objects.filter(q1 | q2 | q3).order_by('-pub_date')[:5]

    project_tasks = Task.objects.filter(
        project__in=Project.objects.filter(collaborators=user) | Project.objects.filter(lead=user)
    ).order_by('-pub_date')[:5]

    context = {
        'title': 'Dashboard',
        'personal_tasks': personal_tasks,
        'project_tasks': project_tasks,
    }
    return render(request, 'dashboard/dashboard.html', context)

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
