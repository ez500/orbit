from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

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

    tasks_list = Task.objects.filter(users__contains=[user.id]).order_by('-deadline')

    serializer = TaskViewSerializer(tasks_list, many=True)

    context = {
        'tasks': serializer.data
    }

    if not tasks_list:
        context['empty'] = True

    return render(request, 'calendar/tasks.html', context)


class TaskCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data.get('title')
            content = serializer.validated_data.get('content')
            deadline = serializer.validated_data.get('deadline')
            users = serializer.validated_data.get('users', [])

            task = Task.objects.create(
                title=title,
                content=content,
                deadline=deadline,
            )
            task.users = users
            task.save()

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
