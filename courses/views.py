from django.shortcuts import render
from rest_framework import viewsets
from .models import Course, Enrollment, Lesson, Quiz
from .serializers import CourseSerializer, EnrollmentSerializer, LessonSerializer, QuizSerializer
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .permissions import IsInstructorOrReadOnly, IsOwnerOrForbidden
from django.contrib.auth import get_user_model

User = get_user_model()

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly, IsOwnerOrForbidden]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)  # Automatically assign the instructor


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:  
            return [IsAuthenticated(), IsStudent()]  # Only students can enroll or modify their enrollments
        return [IsAuthenticated()]  # Instructors can view enrollments

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes=[IsAuthenticated, IsInstructorOrReadOnly, IsOwnerOrForbidden]
    def get_permissions(self):
        """ Apply different permissions based on the request method """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:  
            return [IsAuthenticated(), IsInstructor()]  
        return [IsAuthenticated()]  


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_permissions(self):
        """Set permissions for different actions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:  
            return [IsAuthenticated(), IsInstructor()]  # Only instructors can modify quizzes
        return [IsAuthenticated()]  # Any logged-in user can view or attempt quizzes

