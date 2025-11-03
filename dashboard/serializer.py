from rest_framework import serializers
from .models import Task


class TaskViewSerializer(serializers.ModelSerializer):
    users = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Task
        fields = ['id', 'title', 'content', 'team', 'deadline', 'pub_date', 'status', 'project', 'users']
        depth = 1


class TaskCreateSerializer(serializers.ModelSerializer):
    users = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Task
        fields = ['title', 'content', 'deadline', 'users']

    def create(self, validated_data):
        users = validated_data.pop('users', [])
        task = Task.objects.create(**validated_data)
        task.users = users  # Assuming your model supports assigning list directly
        task.save()
        return task