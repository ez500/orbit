import json
from urllib.parse import uses_netloc

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
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

    context = {'title': 'Dashboard'}

    return render(request, 'dashboard/dashboard.html', context)


@login_required
def tasks(request):
    """Tasks view"""
    user = request.user

    tasks_list = Task.objects.filter(users=user.id).order_by('-deadline')
    teams = Team.objects.filter(members=user.id)
    projects = Project.objects.filter(collaborators=user.id) | Project.objects.filter(lead=user.id)

    serializer = TaskViewSerializer(tasks_list, many=True)

    context = {
        'title': 'Tasks',
        'tasks_qs': tasks_list,
        'tasks': serializer.data,
        'teams': teams,
        'projects': projects
    }

    if not tasks_list:
        context['empty'] = True

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


class TaskDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
            task.delete()
            return Response({'message': 'Task deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
