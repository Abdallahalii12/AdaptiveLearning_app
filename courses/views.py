from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Enrollment, Lesson, LessonQuiz, Streak
from .serializers import (
    CourseSerializer, EnrollmentSerializer, LessonSerializer, LessonQuizSerializer, 
    StreakSerializer
)
from .permissions import IsInstructorOrReadOnly, IsOwnerOrForbidden, IsStudent

# 📌 Course ViewSet (Handles Course CRUD)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly, IsOwnerOrForbidden]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)  # Automatically assign the instructor


# 📌 Enrollment ViewSet (Handles Enrollment)
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsStudent()]  # Only students can enroll
        return [IsAuthenticated()]  # Instructors can view enrollments

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsStudent])
    def enroll(self, request):
        """ Allow students to enroll in a course """
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)

        if created:
            return Response({"message": "Enrolled successfully!"})
        return Response({"message": "Already enrolled!"}, status=400)


# 📌 Lesson ViewSet (Handles Lessons & Completion)
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly, IsOwnerOrForbidden]

    def get_queryset(self):
        """ Students should only see published lessons """
        if self.request.user.is_authenticated and not self.request.user.is_instructor:
            return Lesson.objects.filter(is_published=True)
        return Lesson.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsStudent])
    def complete_lesson(self, request, pk=None):
        """ Mark a lesson as completed and update streak """
        lesson = self.get_object()

        if request.user in lesson.completed_by.all():
            return Response({"message": "Lesson already completed!"}, status=400)

        lesson.completed_by.add(request.user)  # Mark lesson as completed

        # Update streak
        streak, _ = Streak.objects.get_or_create(user=request.user)
        streak.current_streak += 1
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
        streak.save()

        return Response({"message": "Lesson completed! Streak updated."})

class LessonQuizViewSet(viewsets.ModelViewSet):
    queryset = LessonQuiz.objects.all()
    serializer_class = LessonQuizSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]

    def get_queryset(self):
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            return LessonQuiz.objects.filter(lesson_id=lesson_id)
        return LessonQuiz.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsStudent])
    def complete_quiz(self, request, pk=None):
        """ Mark a quiz as completed """
        quiz = self.get_object()
        quiz.completed_by.add(request.user)  # Mark quiz as completed

        return Response({"message": "Quiz completed!"})
