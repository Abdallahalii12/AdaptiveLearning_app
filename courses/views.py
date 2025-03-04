from django.shortcuts import render
from rest_framework import viewsets
from .models import Course, Enrollment, Lesson
from .serializers import CourseSerializer, EnrollmentSerializer, LessonSerializer,LessonQuizSerializer,LessonQuiz
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


class LessonQuizViewSet(viewsets.ModelViewSet):
    queryset = LessonQuiz.objects.all() 
    serializer_class = LessonQuizSerializer
    permission_classes = [IsInstructorOrReadOnly] 
    
    def get_queryset(self):
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            return LessonQuiz.objects.filter(lesson_id=lesson_id)
        return LessonQuiz.objects.all()



