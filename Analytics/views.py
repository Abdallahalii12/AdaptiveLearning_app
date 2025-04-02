from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from .models import UserActivityLog
from .serializers import UserActivityLogSerializer,InstructorAnalyticsSerializer
from courses.models import Course
from rest_framework.views import APIView





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
    serializer_class=InstructorAnalyticsSerializer
    permission_class=[IsAuthenticated]
    def get(self,request,*args,**kwargs):
        instructor=request.user

        course=Course.objects.filter(instructor=instructor)


        total_students = 0
        total_quiz_score = 0
        total_completed_courses = 0
        total_dropped_off = 0

        for course in courses:
            students=course.enrolled_students.all()
            total_students+=len(students)

            for student in students:
                quizzes=Quiz.objects.filter(course=course)
                total_quiz_score += sum([quiz.get_score_for_student(student) for quiz in quiz])


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
        
        # Return the calculated data in the response
        return Response(analytics_data, status=status.HTTP_200_OK)









    



