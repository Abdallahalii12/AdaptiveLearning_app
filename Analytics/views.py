from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from .models import UserActivityLog
from .serializers import UserActivityLogSerializer,InstructorAnalyticsSerializer
from courses.models import Course
from rest_framework.views import APIView
from quizzes.models import Quiz
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.response import Response

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
class UserActivityViewSet(viewsets.ModelViewSet):
    serializer_class=UserActivityLogSerializer
    permission_classes=[IsAuthenticated]
    queryset = UserActivityLog.objects.all() 

    def get_queryset(self):
        user=self.request.user
        if user.role=="student":
            return UserActivityLog.objects.filter(user=user)
        
        elif user.role=="instructor":
            instructor_courses=user.courses.all()
            return UserActivityLog.objects.filter(user__enrolled_courses__in=instructor_courses)
        
        else:
            return UserActivityLog.objects.all()


class InstructorAnalyticsViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        instructor = request.user
        courses = Course.objects.filter(instructor=instructor)

        total_students = 0
        total_quiz_score = 0
        total_completed_courses = 0
        total_dropped_off = 0

        for course in courses:
            students = course.enrolled_students.all()
            total_students += students.count()

            for student in students:
                quizzes = Quiz.objects.filter(course=course)
                total_quiz_score += sum([
                    quiz.get_score_for_student(student) for quiz in quizzes
                ])

                if student.completed_course(course):
                    total_completed_courses += 1
                else:
                    total_dropped_off += 1

        average_quiz_score = total_quiz_score / total_students if total_students else 0
        completion_rate = total_completed_courses / total_students * 100 if total_students else 0
        drop_off_rate = total_dropped_off / total_students * 100 if total_students else 0

        analytics_data = {
            'total_students': total_students,
            'average_quiz_score': average_quiz_score,
            'completion_rate': completion_rate,
            'drop_off_rate': drop_off_rate
        }

        return Response(analytics_data, status=status.HTTP_200_OK)







    



