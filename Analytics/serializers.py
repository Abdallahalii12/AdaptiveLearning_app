from rest_framework import serializers
from .models import UserActivityLog,InstructorAnalytics
from django.db import models

class UserActivityLogSerializer(serializers.ModelSerializer):
    username=serializers.CharField(source="user.username",read_only=True)
    role=serializers.CharField(source="user.role",read_only=True)
    is_banned=serializers.BooleanField(source="user.is_banned",read_only=True)

    class Meta:
        model=UserActivityLog
        fields= '__all__'


class InstructorAnalyticsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = InstructorAnalytics
        fields = ['total_students', 'average_quiz_score', 'completion_rate', 'drop_off_rate', 'username']
