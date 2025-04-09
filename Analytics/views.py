from django.shortcuts import render
from rest_framework import viewsets,status, permissions
from rest_framework.permissions import IsAuthenticated
from .models import UserActivityLog, InstructorAnalytics
from .serializers import UserActivityLogSerializer, InstructorAnalyticsSerializer, StreakSerializer, AchievementSerializer
from courses.models import Course, Enrollment, LessonQuiz, Streak, Achievement
from quizzes.models import Quiz
from rest_framework.views import APIView
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.response import Response
from django.db.models import Avg, Count, F, Sum, Q
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import action
from django.db.models.functions import TruncDate
from courses.serializers import CourseSerializer

class StudentAnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'student':
            return Response(
                {"error": "Only students can access their analytics."},
                status=status.HTTP_403_FORBIDDEN
            )

        user = request.user
        activities = UserActivityLog.objects.filter(user=user)

        # Course Progress Analytics
        enrollments = Enrollment.objects.filter(student=user)
        active_courses = enrollments.filter(status='active')
        completed_courses = enrollments.filter(status='completed')
        
        avg_progress = active_courses.aggregate(
            avg_progress=Avg('progress')
        )['avg_progress'] or 0

        # Activity Counts
        lessons_watched = activities.filter(activity_type='lesson_watched').count()
        lesson_quizzes = activities.filter(activity_type='lesson_quiz_completed').count()
        big_quizzes = activities.filter(activity_type='big_quiz_completed').count()

        # Quiz Performance
        quiz_activities = activities.filter(
            Q(activity_type='lesson_quiz_completed') |
            Q(activity_type='big_quiz_completed')
        )
        avg_quiz_score = quiz_activities.aggregate(
            avg_score=Avg('score')
        )['avg_score'] or 0

        # Time Spent
        time_spent = activities.aggregate(
            total_time=Sum('time_spent')
        )['total_time'] or timedelta()

        # Streaks and Achievements
        streak = Streak.objects.filter(user=user).first()
        achievements = Achievement.objects.filter(user=user).count()

        analytics = {
            'course_progress': {
                'active_courses': active_courses.count(),
                'completed_courses': completed_courses.count(),
                'average_progress': avg_progress
            },
            'activity_summary': {
                'lessons_watched': lessons_watched,
                'lesson_quizzes_completed': lesson_quizzes,
                'big_quizzes_completed': big_quizzes,
                'total_time_spent': str(time_spent)
            },
            'performance_metrics': {
                'average_quiz_score': avg_quiz_score,
                'streak_days': streak.days if streak else 0,
                'achievements_earned': achievements
            }
        }

        return Response(analytics)

# Create your views here.
class UserActivityLogViewSet(viewsets.ModelViewSet):
    serializer_class = UserActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['activity_type', 'details']
    ordering_fields = ['timestamp']
    filterset_fields = ['activity_type', 'timestamp']

    def get_queryset(self):
        if self.request.user.role == 'instructor':
            return UserActivityLog.objects.filter(
                course__instructor=self.request.user
            )
        return UserActivityLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InstructorAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = InstructorAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'date']
    ordering_fields = ['date']
    ordering = ['-date']

    def get_queryset(self):
        return InstructorAnalytics.objects.filter(
            course__instructor=self.request.user
        )

    @action(detail=False, methods=['post'])
    def generate_analytics(self, request):
        course_id = request.data.get('course')
        if not course_id:
            return Response(
                {"error": "Course ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if course.instructor != request.user:
            return Response(
                {"error": "You are not authorized to view analytics for this course."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Calculate analytics
        total_students = Enrollment.objects.filter(
            course=course,
            status='active'
        ).count()

        avg_quiz_score = UserActivityLog.objects.filter(
            lesson_quiz__course=course,
            activity_type='quiz_completed'
        ).aggregate(avg_score=Avg('score'))['avg_score'] or 0

        completion_rate = Enrollment.objects.filter(
            course=course,
            status='completed'
        ).count() / total_students if total_students > 0 else 0

        drop_off_rate = Enrollment.objects.filter(
            course=course,
            status='dropped'
        ).count() / total_students if total_students > 0 else 0

        analytics = InstructorAnalytics.objects.create(
            course=course,
            total_students=total_students,
            avg_quiz_score=avg_quiz_score,
            completion_rate=completion_rate,
            drop_off_rate=drop_off_rate
        )

        return Response(
            InstructorAnalyticsSerializer(analytics).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def student_progress(self, request, pk=None):
        course = self.get_object().course
        if course.instructor != request.user:
            return Response(
                {"error": "You are not authorized to view student progress for this course."},
                status=status.HTTP_403_FORBIDDEN
            )

        enrollments = Enrollment.objects.filter(
            course=course,
            status__in=['active', 'completed']
        ).select_related('student')

        progress_data = []
        for enrollment in enrollments:
            activities = UserActivityLog.objects.filter(
                user=enrollment.student,
                lesson_quiz__course=course
            )
            
            progress_data.append({
                'student': enrollment.student.username,
                'progress': enrollment.progress,
                'last_accessed': enrollment.last_accessed,
                'activities_count': activities.count(),
                'avg_quiz_score': activities.filter(
                    activity_type='quiz_completed'
                ).aggregate(avg_score=Avg('score'))['avg_score'] or 0
            })

        return Response(progress_data)







    



