from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from .models import UserActivityLog
from .serializers import UserActivityLogSerializer
from courses.models import Course





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



    



