from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Enrollment, Lesson, LessonQuiz, Streak, Achievement, UserActivityLog
from .serializers import (
    CourseSerializer, EnrollmentSerializer, LessonSerializer, LessonQuizSerializer, 
    StreakSerializer, AchievementSerializer
)
from .permissions import IsInstructorOrReadOnly, IsOwnerOrForbidden, IsStudent
from datetime import timedelta
from django.utils.timezone import now

from .serializers import CourseSearchSerializer 
from rest_framework import permissions

# 📌 Course ViewSet (Handles Course CRUD)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly, IsOwnerOrForbidden]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status', 'instructor']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == 'student':
            return queryset.filter(status='published')
        elif user.role == 'instructor':
            return queryset.filter(instructor=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        if course.status != 'published':
            return Response(
                {"error": "Course is not published yet."},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'status': 'active'}
        )

        if not created:
            return Response(
                {"error": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def analytics(self, request, pk=None):
        course = self.get_object()
        if request.user != course.instructor:
            return Response(
                {"error": "You don't have permission to view these analytics."},
                status=status.HTTP_403_FORBIDDEN
            )

        analytics = course.analytics.first()
        if not analytics:
            return Response(
                {"error": "No analytics available for this course."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = InstructorAnalyticsSerializer(analytics)
        return Response(serializer.data)

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'course']
    ordering_fields = ['enrolled_at', 'last_accessed', 'progress']
    ordering = ['-enrolled_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Enrollment.objects.filter(student=user)
        elif user.role == 'instructor':
            return Enrollment.objects.filter(course__instructor=user)
        return Enrollment.objects.none()

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_progress(self, request, pk=None):
        enrollment = self.get_object()
        if request.user != enrollment.student:
            return Response(
                {"error": "You can only update your own progress."},
                status=status.HTTP_403_FORBIDDEN
            )

        progress = request.data.get('progress')
        if progress is None:
            return Response(
                {"error": "Progress value is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            progress = float(progress)
            if not 0 <= progress <= 100:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "Progress must be a number between 0 and 100."},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollment.progress = progress
        if progress >= 100:
            enrollment.status = 'completed'
            enrollment.completion_date = now()
        enrollment.save()

        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        enrollment = self.get_object()
        if request.user != enrollment.student:
            return Response(
                {"error": "You can only update your own enrollment status."},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        if new_status not in dict(Enrollment.STATUS_CHOICES):
            return Response(
                {"error": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollment.status = new_status
        enrollment.save()

        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)

def grant_achievement(user, title, description, badge_image=None):
    """ Grant an achievement if the user doesn't already have it """
    if not Achievement.objects.filter(user=user, title=title).exists():
        Achievement.objects.create(
            user=user, title=title, description=description, badge_image=badge_image
        )

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'is_published']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Lesson.objects.filter(
                course__enrollments__student=user,
                is_published=True
            )
        elif user.role == 'instructor':
            return Lesson.objects.filter(course__instructor=user)
        return Lesson.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_complete(self, request, pk=None):
        lesson = self.get_object()
        if request.user.role != 'student':
            return Response(
                {"error": "Only students can mark lessons as complete."},
                status=status.HTTP_403_FORBIDDEN
            )

        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=lesson.course,
            status='active'
        ).first()

        if not enrollment:
            return Response(
                {"error": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN
            )

        lesson.completed_by.add(request.user)
        
        # Update enrollment progress
        total_lessons = lesson.course.lessons.count()
        completed_lessons = lesson.course.lessons.filter(completed_by=request.user).count()
        enrollment.progress = (completed_lessons / total_lessons) * 100
        enrollment.save()

        return Response({"message": "Lesson marked as complete."})

class LessonQuizViewSet(viewsets.ModelViewSet):
    serializer_class = LessonQuizSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['lesson', 'difficulty']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return LessonQuiz.objects.filter(
                lesson__course__enrollments__student=user,
                lesson__is_published=True
            )
        elif user.role == 'instructor':
            return LessonQuiz.objects.filter(lesson__course__instructor=user)
        return LessonQuiz.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_answers(self, request, pk=None):
        quiz = self.get_object()
        if request.user.role != 'student':
            return Response(
                {"error": "Only students can submit quiz answers."},
                status=status.HTTP_403_FORBIDDEN
            )

        answers = request.data.get('answers', [])
        if not answers:
            return Response(
                {"error": "No answers provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_score = 0
        max_score = quiz.questions.count()

        for answer_data in answers:
            question_id = answer_data.get('question_id')
            answer_text = answer_data.get('answer')

            try:
                question = quiz.questions.get(id=question_id)
                if question.question_type == 'mcq':
                    selected_answer = question.answers.get(text=answer_text, is_correct=True)
                    total_score += question.points
                else:
                    if answer_text.lower() == question.correct_answer.lower():
                        total_score += question.points
            except:
                continue

        score_percentage = (total_score / max_score) * 100
        quiz.completed_by.add(request.user)

        # Log the quiz attempt
        UserActivityLog.objects.create(
            user=request.user,
            lesson_quiz=quiz,
            time_stamp=now()
        )

        return Response({
            "score": total_score,
            "max_score": max_score,
            "percentage": score_percentage,
            "message": "Quiz submitted successfully."
        })

# Courses search 
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSearchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Course.objects.all()

        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset

#URL for Search courses http://127.0.0.1:8000/courses/?search= course_name 
