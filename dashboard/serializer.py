import datetime

from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import Profile
from .models import Task, Event


class OptionalDateField(serializers.DateField):
    def to_internal_value(self, value):
        if value in (None, '', 'null'):
            return None
        return super().to_internal_value(value)


class TaskViewSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['title', 'id', 'content', 'status', 'deadline', 'pub_date', 'team', 'project', 'users']
        depth = 1


class EventViewSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['title', 'id', 'content', 'start_datetime', 'end_datetime', 'pub_date', 'team', 'project', 'users']


class TaskCreateSerializer(serializers.ModelSerializer):
    deadline = OptionalDateField(required=False, allow_null=True)
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)


    class Meta:
        model = Task
        fields = ['title', 'content', 'status', 'deadline', 'team', 'project', 'users']
