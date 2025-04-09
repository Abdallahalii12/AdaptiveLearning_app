from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from .models import UserActivityLog, InstructorAnalytics
from .serializers import UserActivityLogSerializer, InstructorAnalyticsSerializer
from courses.models import Course, Enrollment, LessonQuiz
from quizzes.models import Quiz
from rest_framework.views import APIView
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.response import Response
from django.db.models import Avg, Count, F
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action

class StudentAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "student":
            return Response({"detail": "Not a student"}, status=403)

        logs = UserActivityLog.objects.filter(user=user)

        lessons_watched = logs.filter(lessons_watched__isnull=False).count()
        lesson_quizzes = logs.filter(lesson_quiz__isnull=False).count()
        big_quizzes = logs.filter(big_quiz__isnull=False).count()

        total_quizzes = lesson_quizzes + big_quizzes

        # Optional: Streaks or time tracking if available
        time_spent_minutes = 0  # Placeholder: you can track and compute this later

        analytics = {
            "lessons_watched": lessons_watched,
            "quizzes_attempted": total_quizzes,
            "lesson_quizzes": lesson_quizzes,
            "big_quizzes": big_quizzes,
            "time_spent_minutes": time_spent_minutes,  # If tracked
        }

        return Response(analytics)





# Create your views here.
class UserActivityLogViewSet(viewsets.ModelViewSet):
    serializer_class = UserActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'lesson_quiz', 'big_quiz', 'lessons_watched']
    ordering_fields = ['time_stamp']
    ordering = ['-time_stamp']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return UserActivityLog.objects.filter(user=user)
        elif user.role == 'instructor':
            return UserActivityLog.objects.filter(
                user__enrollments__course__in=user.courses_taught.all()
            )
        return UserActivityLog.objects.none()

class InstructorAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = InstructorAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['instructor', 'course']
    ordering_fields = ['updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'instructor':
            return InstructorAnalytics.objects.filter(instructor=user)
        return InstructorAnalytics.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def generate_analytics(self, request):
        if request.user.role != 'instructor':
            return Response(
                {"error": "Only instructors can generate analytics."},
                status=status.HTTP_403_FORBIDDEN
            )

        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {"error": "Course ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id, instructor=request.user)
        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Calculate analytics
        total_students = course.enrollments.filter(status='active').count()
        
        # Calculate average quiz score
        quiz_scores = []
        for quiz in course.lessons.filter(quizzes__isnull=False):
            quiz_scores.extend(quiz.quizzes.values_list('completed_by__id', flat=True))
        
        average_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else None

        # Calculate completion rate
        total_enrollments = course.enrollments.count()
        completed_enrollments = course.enrollments.filter(status='completed').count()
        completion_rate = (completed_enrollments / total_enrollments) * 100 if total_enrollments else 0

        # Calculate drop-off rate
        dropped_enrollments = course.enrollments.filter(status='dropped').count()
        drop_off_rate = (dropped_enrollments / total_enrollments) * 100 if total_enrollments else 0

        # Create or update analytics
        analytics, created = InstructorAnalytics.objects.update_or_create(
            instructor=request.user,
            course=course,
            defaults={
                'total_students': total_students,
                'average_quiz_score': average_quiz_score,
                'completion_rate': completion_rate,
                'drop_off_rate': drop_off_rate
            }
        )

        serializer = self.get_serializer(analytics)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def student_progress(self, request, pk=None):
        analytics = self.get_object()
        if request.user != analytics.instructor:
            return Response(
                {"error": "You don't have permission to view these analytics."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get student progress data
        enrollments = analytics.course.enrollments.filter(status='active')
        progress_data = []
        
        for enrollment in enrollments:
            student_data = {
                'student_id': enrollment.student.id,
                'student_name': enrollment.student.username,
                'progress': enrollment.progress,
                'last_accessed': enrollment.last_accessed,
                'completed_lessons': analytics.course.lessons.filter(
                    completed_by=enrollment.student
                ).count(),
                'total_lessons': analytics.course.lessons.count()
            }
            progress_data.append(student_data)

        return Response(progress_data)







    



