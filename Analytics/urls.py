from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserActivityViewSet, InstructorAnalyticsApiView, StudentAnalyticsAPIView

router = DefaultRouter()
router.register(r'user-activity', UserActivityViewSet)  # Only viewsets go here

urlpatterns = [
    path('', include(router.urls)),
    path('instructor-analytics/', InstructorAnalyticsApiView.as_view(), name='instructor-analytics'),
    path('student-analytics/', StudentAnalyticsAPIView.as_view(), name='student-analytics'),
]
